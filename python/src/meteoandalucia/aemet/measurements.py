"""Correspondencia de campos y conversi?n de medidas AEMET."""

from meteoandalucia.common.parsing import nullable_float, parse_measurement

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


def parse_aemet_measurement(row: dict) -> dict:
    if not str(row.get("indicativo", "")).strip():
        raise ValueError("Falta indicativo")
    nullable_float(row.get("altitud"))
    return {"station_id": row["indicativo"], **parse_measurement(row, AEMET_FIELDS)}
