"""Lectura del inventario CSV RIAweb, independiente de PostgreSQL."""

import csv
import re
from decimal import Decimal
from pathlib import Path

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
