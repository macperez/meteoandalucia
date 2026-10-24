"""Inventario y medidas diarias de RIAweb."""

from meteoandalucia.api.http import APIError, JSONClient, records
from meteoandalucia.parsing import date_range

BASE_URL = "https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaws"


class RiawebClient:
    def __init__(self, http=None, base_url: str = BASE_URL):
        self.http = http or JSONClient()
        self.base_url = base_url.rstrip("/")

    def stations(self) -> list[dict]:
        return records(self.http.get(f"{self.base_url}/estaciones"))

    def measurement(self, province: int, station: int, day: str, et0: bool = True) -> dict:
        date_range(day, day)
        value = self.http.get(
            f"{self.base_url}/datosdiarios/{int(province)}/{int(station)}/{day}/{str(et0).lower()}"
        )
        if not isinstance(value, dict):
            raise APIError("Se esperaba una medida JSON")
        return value

    def measurements(
        self, province: int, station: int, start: str, end: str, et0: bool = True
    ) -> list[dict]:
        date_range(start, end)
        return records(
            self.http.get(
                f"{self.base_url}/datosdiarios/{int(province)}/{int(station)}/"
                f"{start}/{end}/{str(et0).lower()}"
            )
        )
