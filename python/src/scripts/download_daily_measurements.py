"""Editar los parámetros antes de ejecutar. Sin argumentos ni CLI instalada."""

import json

from meteoandalucia.api.aemet import AemetClient
from meteoandalucia.api.riaweb import RiawebClient
from meteoandalucia.application.measurements import (
    aemet_measurements,
    measurements_all,
    riaweb_measurements,
)
from meteoandalucia.common.config import api_key, load_environment
from meteoandalucia.db.aemet import AemetRepository
from meteoandalucia.db.riaweb import RiawebRepository

PROVIDER = "aemet"  # aemet o riaweb
START = ""  # YYYY-MM-DD
END = ""  # Vacío: un día; en modo ALL_STATIONS es obligatorio.
STATION = ""  # Indicativo AEMET o código numérico RIAweb
PROVINCE = 4  # Solo RIAweb
ALL_STATIONS = False
ET0 = True  # Solo RIAweb
PERSIST = False


def main():
    if not START or (ALL_STATIONS and not END) or (not ALL_STATIONS and not STATION):
        raise ValueError("Configura START, STATION y, para todas las estaciones, END")
    if PROVIDER not in {"aemet", "riaweb"}:
        raise ValueError("PROVIDER debe ser aemet o riaweb")
    load_environment()
    if PROVIDER == "aemet":
        client, repository = AemetClient(api_key()), AemetRepository()
    else:
        client, repository = RiawebClient(), RiawebRepository()
    if ALL_STATIONS:
        result = measurements_all(
            client, repository, START, END, provider=PROVIDER, persist=PERSIST
        )
        print(
            json.dumps(
                {
                    "measurements": result.measurements,
                    "inserted": result.inserted,
                    "errors": result.errors,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        if result.errors:
            raise RuntimeError(f"Han fallado {len(result.errors)} estaciones; revisa errors")
    else:
        if PROVIDER == "aemet":
            rows = aemet_measurements(client, repository, STATION, START, END or START, PERSIST)
        else:
            rows = riaweb_measurements(
                client, repository, PROVINCE, int(STATION), START, END or None, ET0, PERSIST
            )
        print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
