"""Consulta RIAweb; PERSIST=True permite importar las estaciones a PostgreSQL."""

import json

from meteoandalucia.api.riaweb import RiawebClient
from meteoandalucia.common.config import load_environment
from meteoandalucia.db.riaweb import RiawebRepository

PERSIST = False


def main():
    load_environment()
    rows = RiawebClient().stations()
    if PERSIST:
        print(f"Estaciones insertadas: {RiawebRepository().insert_stations(rows)}")
    else:
        print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
