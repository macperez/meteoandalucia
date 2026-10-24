"""Importa el CSV local; ejecutar explícitamente tras preparar los catálogos SQL."""

from meteoandalucia.config import DATA_DIR, load_environment
from meteoandalucia.db.aemet import AemetRepository


def main():
    load_environment()
    count = AemetRepository().import_stations_csv(DATA_DIR / "estaciones.csv")
    print(f"Estaciones importadas: {count}")


if __name__ == "__main__":
    main()
