"""Descarga los datos diarios de todas las estaciones a data/, sin base de datos."""

from meteoandalucia.api.aemet import AemetClient
from meteoandalucia.config import DATA_DIR, api_key, load_environment
from meteoandalucia.daily_download import download_daily_range
from meteoandalucia.parsing import validate_date_range

START = "2015-01-01"  # Fecha inicial: YYYY-MM-DD
END = "2026-10-01"  # Fecha final incluida: YYYY-MM-DD


def download(start: str, end: str):
    validate_date_range(start, end)
    load_environment()
    return download_daily_range(AemetClient(api_key()), start, end, DATA_DIR)


def main():
    if not START or not END:
        raise ValueError("Configura START y END con las fechas que quieras descargar")
    download(START, END)


if __name__ == "__main__":
    main()
