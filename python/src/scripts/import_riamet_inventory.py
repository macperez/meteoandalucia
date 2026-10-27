"""Importa data/riamet/estaciones.csv tras ejecutar sql/riamet_ddl.sql."""

from meteoandalucia.config import DATA_DIR, load_environment
from meteoandalucia.db.riamet import RiametRepository


def main():
    load_environment()
    count = RiametRepository().import_stations_csv(DATA_DIR / "riamet" / "estaciones.csv")
    print(f"Estaciones importadas: {count}")


if __name__ == "__main__":
    main()
