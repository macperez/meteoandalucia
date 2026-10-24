"""Transporte JSON con tiempo límite y compatibilidad UTF-8/ISO-8859-1."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class APIError(RuntimeError):
    """Error de comunicación o respuesta inválida del proveedor."""


class JSONClient:
    def __init__(self, timeout: float = 30):
        self.timeout = timeout

    def get(self, url: str, headers: dict | None = None):
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise APIError("Enlace de datos inválido")
        try:
            with urlopen(Request(url, headers=headers or {}), timeout=self.timeout) as response:
                body = response.read()
        except HTTPError as exc:
            raise APIError(f"HTTP {exc.code}") from None
        except (URLError, TimeoutError) as exc:
            raise APIError("No se pudo completar la petición HTTP") from exc
        try:
            try:
                text = body.decode("utf-8-sig")
            except UnicodeDecodeError:
                text = body.decode("iso-8859-1")
            return json.loads(text)
        except ValueError as exc:
            raise APIError("Respuesta JSON inválida") from exc


def records(value) -> list[dict]:
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise APIError("Se esperaba una lista de registros JSON")
    return value
