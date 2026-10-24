"""Inventario y datos climatológicos diarios de AEMET."""

from urllib.parse import quote

from meteoandalucia.api.http import APIError, JSONClient, records
from meteoandalucia.parsing import date_range

BASE_URL = "https://opendata.aemet.es/opendata/api"


class AemetClient:
    def __init__(self, key: str, http=None, base_url: str = BASE_URL):
        if not key.strip():
            raise ValueError("Falta API_KEY")
        self.key = key.strip()
        self.http = http or JSONClient()
        self.base_url = base_url.rstrip("/")

    def _download(self, path: str) -> list[dict]:
        envelope = self.http.get(
            f"{self.base_url}/{path}", {"api_key": self.key, "cache-control": "no-cache"}
        )
        if not isinstance(envelope, dict):
            raise APIError("Respuesta AEMET inválida")
        if envelope.get("estado") != 200:
            raise APIError(
                f"AEMET estado {envelope.get('estado')}: {envelope.get('descripcion', '')}"
            )
        link = envelope.get("datos")
        if not isinstance(link, str) or not link:
            raise APIError("Falta un enlace de datos válido")
        # El token nunca se envía al enlace de descarga.
        return records(self.http.get(link))

    def stations(self) -> list[dict]:
        rows = self._download("valores/climatologicos/inventarioestaciones/todasestaciones")
        return sorted(rows, key=lambda row: (row.get("provincia", ""), row.get("indicativo", "")))

    def measurements(self, station: str, start: str, end: str) -> list[dict]:
        date_range(start, end)
        if not station.strip():
            raise ValueError("El indicativo es obligatorio")
        return self._download(
            "valores/climatologicos/diarios/datos/"
            f"fechaini/{start}T00%3A00%3A00UTC/"
            f"fechafin/{end}T00%3A00%3A00UTC/estacion/{quote(station, safe='')}"
        )

    def daily_all_stations(self, start: str, end: str) -> list[dict]:
        """Consulta directa de datos diarios de todas las estaciones, sin PostgreSQL."""
        date_range(start, end)
        return self._download(
            "valores/climatologicos/diarios/datos/"
            f"fechaini/{start}T00%3A00%3A00UTC/"
            f"fechafin/{end}T23%3A59%3A59UTC/todasestaciones"
        )
