"""Conversión de fechas y valores meteorológicos sin pérdida silenciosa de datos."""

import math
from datetime import date


def date_range(start: str, end: str) -> tuple[date, date]:
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


AEMET_FIELDS = {
    "avg_temp": "tmed",
    "precipitation": "prec",
    "min_temp": "tmin",
    "time_mintemp": "horatmin",
    "max_temp": "tmax",
    "time_maxtemp": "horatmax",
    "wind_direction": "dir",
    "avg_wind": "velmedia",
    "max_wind_speed": "racha",
    "time_maxwind": "horaracha",
    "max_press": "presMax",
    "time_maxpress": "horaPresMax",
    "min_press": "presMin",
    "time_minpress": "horaPresMin",
}

RIAWEB_FIELDS = {
    "max_temp": "tempMax",
    "min_temp": "tempMin",
    "avg_temp": "tempMedia",
    "time_maxtemp": "horMinTempMax",
    "time_mintemp": "horMinTempMin",
    "max_humid": "humedadMax",
    "min_humid": "humedadMin",
    "avg_humid": "humedadMedia",
    "time_maxhumid": "horMinHumMax",
    "time_minhumid": "horMinHumMin",
    "wind_speed": "velViento",
    "wind_direction": "dirViento",
    "max_wind_speed": "velVientoMax",
    "direction_max_wind": "dirVientoVelMax",
    "time_maxwind": "horMinVelMax",
    "radiation": "radiacion",
    "precipitation": "precipitacion",
    "batery": "bateria",
    "dateutlmod": "fechaUtlMod",
    "et0": "et0",
}


def parse_measurement(row: dict, fields: dict) -> dict:
    result = {"measurement_date": date_range(row["fecha"], row["fecha"])[0]}
    for column, key in fields.items():
        value = row.get(key)
        if column.startswith("time_") or column == "dateutlmod":
            result[column] = value or None
        else:
            result[column] = nullable_float(value)
    return result


def parse_aemet_measurement(row: dict) -> dict:
    if not str(row.get("indicativo", "")).strip():
        raise ValueError("Falta indicativo")
    nullable_float(row.get("altitud"))
    return {"station_id": row["indicativo"], **parse_measurement(row, AEMET_FIELDS)}


def parse_riaweb_measurement(row: dict, province: int, station: int) -> dict:
    return {"prov_id": province, "station_id": station, **parse_measurement(row, RIAWEB_FIELDS)}
