"""Carga un fichero CSV de medidas AEMET en raw.aemet_measurement."""

import argparse
import csv
import sys
from pathlib import Path

import psycopg

from meteoandalucia.config import load_environment
from meteoandalucia.db.aemet import AemetRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--csv", required=True, type=Path, help="Ruta al fichero CSV que se cargará"
    )
    args = parser.parse_args(argv)
    try:
        load_environment()
        count = AemetRepository().load_raw_csv_measurement(args.csv)
    except (OSError, ValueError, csv.Error, psycopg.Error) as exc:
        print(f"Error al cargar CSV: {exc}", file=sys.stderr)
        return 1
    print(f"Carga completada: {count} filas en raw.aemet_measurement desde {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
