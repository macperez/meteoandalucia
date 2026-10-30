"""Carga XML diarios en raw según la fuente seleccionada."""

import argparse
import sys
from pathlib import Path
from xml.etree.ElementTree import ParseError

import psycopg

from meteoandalucia.common.config import load_environment
from meteoandalucia.db.siarweb import SiarwebRepository


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=("siarweb",), help="Fuente de datos")
    parser.add_argument(
        "--xml",
        required=True,
        type=Path,
        help="XML diario o carpeta; selecciona Clim_Diario_*.xml sin subcarpetas",
    )
    args = parser.parse_args(argv)
    try:
        load_environment()
        paths = sorted(args.xml.glob("Clim_Diario_*.xml")) if args.xml.is_dir() else [args.xml]
        if not paths:
            raise ValueError(f"No hay XML diarios en {args.xml}")
        count = SiarwebRepository().load_raw_xml_measurements(paths)
    except (OSError, ValueError, ParseError, psycopg.Error) as exc:
        print(f"Error al cargar XML: {exc}", file=sys.stderr)
        return 1
    print(f"Carga completada: {count} filas en raw.siarweb_measurement desde {len(paths)} XML")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
