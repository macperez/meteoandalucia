"""Persistencia AEMET, compatible con los nombres de columnas existentes."""

import csv
from pathlib import Path

from psycopg import sql
from psycopg.rows import dict_row

from meteoandalucia.db.connection import connect
from meteoandalucia.parsing import parse_aemet_measurement
from meteoandalucia.provinces import province_slug
from meteoandalucia.stations_csv import read_stations_csv

ANDALUSIA = (4, 11, 14, 18, 21, 23, 29, 41)

RAW_MEASUREMENT_COLUMNS = frozenset(
    (
        "fecha",
        "indicativo",
        "nombre",
        "provincia",
        "altitud",
        "tmed",
        "prec",
        "tmin",
        "horatmin",
        "tmax",
        "horatmax",
        "hrMedia",
        "hrMax",
        "horaHrMax",
        "hrMin",
        "horaHrMin",
        "pintMax",
        "horaPIntMax",
        "dir",
        "velmedia",
        "racha",
        "horaracha",
        "presMax",
        "horaPresMax",
        "presMin",
        "horaPresMin",
        "sol",
    )
)


class AemetRepository:
    def __init__(self, connection_factory=connect):
        self.connection_factory = connection_factory

    def load_raw_csv_measurement(self, path: str | Path) -> int:
        """Carga un CSV en raw.aemet_measurement en una transacción, sin transformar valores.

        COPY FROM STDIN evita necesitar acceso al fichero desde el servidor PostgreSQL.
        Las columnas se identifican por la cabecera; el resto queda en NULL.
        Los campos vacíos presentes se conservan como cadenas vacías.
        """
        with Path(path).open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source, strict=True)
            header = next(reader, None)
            if not header or len(header) != len(set(header)):
                raise ValueError("Cabecera CSV vacía o con columnas duplicadas")
            unknown = set(header) - RAW_MEASUREMENT_COLUMNS
            if unknown:
                raise ValueError(f"Columnas CSV desconocidas: {', '.join(sorted(unknown))}")
            if not {"fecha", "indicativo"} <= set(header):
                raise ValueError("La cabecera CSV debe incluir fecha e indicativo")
            query = sql.SQL("COPY raw.aemet_measurement ({}) FROM STDIN").format(
                sql.SQL(", ").join(map(sql.Identifier, header))
            )
            count = 0
            with self.connection_factory() as connection:
                with connection.cursor() as cursor:
                    with cursor.copy(query) as copy:
                        for row in reader:
                            if not row:
                                continue
                            if len(row) != len(header):
                                raise ValueError(
                                    f"Línea {reader.line_num}: se esperaban {len(header)} "
                                    f"columnas y se encontraron {len(row)}"
                                )
                            copy.write_row(row)
                            count += 1
        return count

    def stations(self, provinces: tuple[int, ...] | None = ANDALUSIA) -> list[dict]:
        query = """SELECT provincia_id AS prov_code, p.provincia AS province,
            indicativo AS station_code, nombre AS station_name
            FROM aemet.station s JOIN aemet.provincia p ON p.id = s.provincia_id"""
        params = ()
        if provinces is not None:
            query += " WHERE provincia_id = ANY(%s)"
            params = (list(provinces),)
        query += " ORDER BY province, station_name"
        with self.connection_factory() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def import_stations_csv(self, path) -> int:
        rows = read_stations_csv(path)
        query = """INSERT INTO aemet.station
            (indicativo, nombre, provincia_id, altitud, latitud, longitud, indsinop)
            SELECT %(indicativo)s, %(nombre)s, id, %(altitud)s,
                %(latitud)s, %(longitud)s, %(indsinop)s FROM aemet.provincia
            WHERE slug = %(slug)s
            ON CONFLICT (indicativo) DO UPDATE SET
                nombre=EXCLUDED.nombre, provincia_id=EXCLUDED.provincia_id,
                altitud=EXCLUDED.altitud, latitud=EXCLUDED.latitud,
                longitud=EXCLUDED.longitud, indsinop=EXCLUDED.indsinop"""
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                for line, row in enumerate(rows, 2):
                    row["slug"] = province_slug(row["provincia"])
                    cursor.execute(query, row)
                    if cursor.rowcount != 1:
                        raise ValueError(
                            f"Registro {line}: provincia ausente o ambigua: {row['provincia']}"
                        )
        return len(rows)

    def insert_measurements(self, rows: list[dict]) -> int:
        parsed = [parse_aemet_measurement(row) for row in rows]
        if not parsed:
            return 0
        columns = list(parsed[0])
        query = sql.SQL("INSERT INTO aemet.daily_measurement ({}) VALUES ({})").format(
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder(column) for column in columns),
        )
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, parsed)
        return len(parsed)
