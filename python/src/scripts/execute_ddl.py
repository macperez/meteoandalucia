"""Ejecuta los archivos DDL indicados, en orden, usando DATABASE_* y .env."""

import argparse
import sys
from pathlib import Path

import psycopg
from meteoandalucia.common.config import load_environment
from meteoandalucia.common.ddl import DdlExecutor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="DDL relativos al directorio actual")
    args = parser.parse_args(argv)
    path = args.files[0]
    try:
        load_environment()
        executor = DdlExecutor()
        for path in args.files:
            executor.execute(path)
            print(f"DDL ejecutado: {path}")
    except (OSError, ValueError, psycopg.Error) as exc:
        print(f"Error al ejecutar DDL {path}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
