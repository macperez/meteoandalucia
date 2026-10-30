"""Correspondencia de campos y conversi?n de medidas RIAweb."""

from meteoandalucia.common.parsing import parse_measurement

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


def parse_riaweb_measurement(row: dict, province: int, station: int) -> dict:
    return {"prov_id": province, "station_id": station, **parse_measurement(row, RIAWEB_FIELDS)}
