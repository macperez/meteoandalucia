"""Conversión de fechas y valores meteorológicos sin pérdida silenciosa de datos."""

import math
from datetime import date


def validate_date_range(start: str, end: str) -> tuple[date, date]:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first.isoformat() != start or last.isoformat() != end:
        raise ValueError("Las fechas deben tener formato YYYY-MM-DD")
    if first > last:
        raise ValueError("La fecha inicial no puede ser posterior a la final")
    return first, last


def nullable_float(value) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    # Ip (precipitación inapreciable) y otras marcas no son valores numéricos.
    # Se conservan en el JSON de origen; en columnas numéricas quedan como NULL.
    if str(value).strip().lower() in {"ip", "acum", "var"}:
        return None
    number = float(str(value).strip().replace(",", "."))
    if not math.isfinite(number):
        raise ValueError(f"Valor numérico no finito: {value}")
    return number


def parse_measurement(row: dict, fields: dict) -> dict:
    result = {"measurement_date": validate_date_range(row["fecha"], row["fecha"])[0]}
    for column, key in fields.items():
        value = row.get(key)
        if column.startswith("time_") or column == "dateutlmod":
            result[column] = value or None
        else:
            result[column] = nullable_float(value)
    return result
