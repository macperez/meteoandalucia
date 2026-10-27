"""Importación del inventario CSV de RIAweb en el esquema riamet."""

import csv
import re
from decimal import Decimal
from pathlib import Path

from psycopg import sql

from meteoandalucia.db.connection import connect

RAW_MEASUREMENT_COLUMNS = frozenset(
    "fecha dia tempMedia tempMax horMinTempMax tempMin horMinTempMin "
    "humedadMedia humedadMax horMinHumMax humedadMin horMinHumMin "
    "velViento dirViento velVientoMax horMinVelMax dirVientoVelMax "
    "radiacion precipitacion bateria fechaUtlMod et0".split()
)

FIELDS = (
    "provincia_id",
    "provincia_nombre",
    "codigoEstacion",
    "nombre",
    "bajoplastico",
    "activa",
    "visible",
    "longitud",
    "latitud",
    "altitud",
    "xutm",
    "yutm",
    "huso",
)


def read_stations_csv(path: str | Path) -> list[dict]:
    rows, seen = [], set()
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        header = next(reader, [])
        if len(header) != len(FIELDS) or set(header) != set(FIELDS):
            raise ValueError("Cabecera CSV RIAweb incorrecta")
        for values in reader:
            if not values:
                continue
            try:
                if len(values) != len(header):
                    raise ValueError("Número de columnas incorrecto")
                row = dict(zip(header, (value.strip() for value in values), strict=True))
                for field in ("provincia_id", "codigoEstacion", "altitud", "huso"):
                    row[field] = int(row[field])
                if not 1 <= row["provincia_id"] <= 52 or row["codigoEstacion"] <= 0:
                    raise ValueError("Provincia o código de estación inválido")
                if not 1 <= row["huso"] <= 60:
                    raise ValueError("Huso inválido")
                if not row["nombre"] or not row["provincia_nombre"]:
                    raise ValueError("Nombre o provincia vacío")
                for field in ("bajoplastico", "activa", "visible"):
                    value = row[field].lower()
                    if value not in ("true", "false"):
                        raise ValueError(f"Booleano inválido: {field}")
                    row[field] = value == "true"
                for field in ("xutm", "yutm"):
                    row[field] = Decimal(row[field].replace(",", "."))
                    if not row[field].is_finite():
                        raise ValueError(f"Coordenada no finita: {field}")
                for field, suffix in (("latitud", "NS"), ("longitud", "EW")):
                    if not re.fullmatch(rf"[0-9]{{9}}[{suffix}]", row[field]):
                        raise ValueError(f"Formato inválido: {field}")
                key = row["provincia_id"], row["codigoEstacion"]
                if key in seen:
                    raise ValueError("Estación duplicada en la misma provincia")
                seen.add(key)
                rows.append(row)
            except (ValueError, ArithmeticError) as exc:
                raise ValueError(f"Línea {reader.line_num}: {exc}") from exc
    return rows


class RiametRepository:
    def __init__(self, connection_factory=connect):
        self.connection_factory = connection_factory

    def load_raw_csv_measurement(self, path: str | Path) -> int:
        """Carga un CSV conservando sus valores y la identidad del nombre de archivo."""
        return self.load_raw_csv_measurements([path])

    def load_raw_csv_measurements(self, paths) -> int:
        """Carga todos los archivos en una transacción; un fallo revierte el lote."""
        count = 0
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                for path in paths:
                    path = Path(path)
                    match = re.fullmatch(
                        r"([0-9]+)_([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})_"
                        r"([0-9]{4}-[0-9]{2}-[0-9]{2})\.csv",
                        path.name,
                    )
                    if not match:
                        raise ValueError(
                            f"{path}: nombre esperado provincia_estacion_INICIO_FIN.csv"
                        )
                    province, station = match.group(1, 2)
                    if not 1 <= int(province) <= 52 or int(station) <= 0:
                        raise ValueError(f"{path}: provincia o estación inválida")
                    with path.open(encoding="utf-8-sig", newline="") as source:
                        reader = csv.reader(source, strict=True)
                        header = next(reader, None)
                        if not header or len(header) != len(set(header)):
                            raise ValueError(f"{path}: cabecera vacía o duplicada")
                        unknown = set(header) - RAW_MEASUREMENT_COLUMNS
                        if unknown:
                            raise ValueError(
                                f"{path}: columnas desconocidas: {', '.join(sorted(unknown))}"
                            )
                        if "fecha" not in header:
                            raise ValueError(f"{path}: falta la columna fecha")
                        columns = ["provincia_id", "codigo_estacion", *header]
                        query = sql.SQL("COPY raw.riamet_measurement ({}) FROM STDIN").format(
                            sql.SQL(", ").join(map(sql.Identifier, columns))
                        )
                        with cursor.copy(query) as copy:
                            for row in reader:
                                if not row:
                                    continue
                                if len(row) != len(header):
                                    raise ValueError(
                                        f"{path}, línea {reader.line_num}: "
                                        "número de columnas incorrecto"
                                    )
                                copy.write_row([province, station, *row])
                                count += 1
        return count

    def import_stations_csv(self, path: str | Path) -> int:
        """Valida el CSV y actualiza el inventario en una única transacción."""
        rows = read_stations_csv(path)
        if not rows:
            return 0
        query = """INSERT INTO riamet.station
            (provincia_id, provincia_nombre, codigo_estacion, nombre, bajoplastico,
             activa, visible, longitud, latitud, altitud, xutm, yutm, huso)
            VALUES (%(provincia_id)s, %(provincia_nombre)s, %(codigoEstacion)s, %(nombre)s,
                %(bajoplastico)s, %(activa)s, %(visible)s, %(longitud)s, %(latitud)s,
                %(altitud)s, %(xutm)s, %(yutm)s, %(huso)s)
            ON CONFLICT (provincia_id, codigo_estacion) DO UPDATE SET
                provincia_nombre=EXCLUDED.provincia_nombre, nombre=EXCLUDED.nombre,
                bajoplastico=EXCLUDED.bajoplastico, activa=EXCLUDED.activa,
                visible=EXCLUDED.visible, longitud=EXCLUDED.longitud,
                latitud=EXCLUDED.latitud, altitud=EXCLUDED.altitud,
                xutm=EXCLUDED.xutm, yutm=EXCLUDED.yutm, huso=EXCLUDED.huso"""
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, rows)
        return len(rows)
