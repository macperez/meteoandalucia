"""Importa estaciones XML locales tras ejecutar sql/siarweb_ddl.sql."""

from meteoandalucia.common.config import DATA_DIR, load_environment
from meteoandalucia.db.siarweb import SiarwebRepository


def main():
    load_environment()
    path = DATA_DIR / "siarweb" / "Identificacion_EstacionesClima.xml"
    count = SiarwebRepository().import_stations_xml(path)
    print(f"Estaciones importadas: {count}")


if __name__ == "__main__":
    main()
