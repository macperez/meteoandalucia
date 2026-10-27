"""Carga CSV de medidas en raw según la fuente seleccionada: aemet o riaweb."""

import argparse
import csv
import sys
from pathlib import Path

import psycopg

from meteoandalucia.config import load_environment
from meteoandalucia.db.aemet import AemetRepository
from meteoandalucia.db.riamet import RiametRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=("aemet", "riaweb"), help="Fuente de datos")
    parser.add_argument(
        "--csv", required=True, type=Path, help="Ruta al CSV o carpeta de CSV (sin subcarpetas)"
    )
    args = parser.parse_args(argv)
    try:
        load_environment()
        paths = sorted(args.csv.glob("*.csv")) if args.csv.is_dir() else [args.csv]
        if not paths:
            raise ValueError(f"No hay CSV en {args.csv}")
        if args.source == "riaweb":
            count = RiametRepository().load_raw_csv_measurements(paths)
            table = "raw.riamet_measurement"
        else:
            repository = AemetRepository()
            count = sum(repository.load_raw_csv_measurement(path) for path in paths)
            table = "raw.aemet_measurement"
    except (OSError, ValueError, csv.Error, psycopg.Error) as exc:
        print(f"Error al cargar CSV: {exc}", file=sys.stderr)
        return 1
    print(f"Carga completada: {count} filas en {table} desde {len(paths)} CSV: {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
