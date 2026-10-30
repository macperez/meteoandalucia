"""Descarga y exporta el inventario sin utilizar PostgreSQL."""

from meteoandalucia.aemet.stations_csv import export_stations_csv
from meteoandalucia.api.aemet import AemetClient
from meteoandalucia.common.config import DATA_DIR, api_key, load_environment


def main():
    load_environment()
    rows = AemetClient(api_key()).stations()
    destination = DATA_DIR / "estaciones.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    export_stations_csv(destination, rows)
    for row in rows:
        print(
            "\t".join(
                str(row.get(key, ""))
                for key in (
                    "indicativo",
                    "provincia",
                    "nombre",
                    "altitud",
                    "latitud",
                    "longitud",
                    "indsinop",
                )
            )
        )
    print(f"CSV exportado ({len(rows)} estaciones): {destination}")


if __name__ == "__main__":
    main()
