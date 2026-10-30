"""Carga del inventario y de los XML diarios locales en PostgreSQL."""

from collections.abc import Iterable
from pathlib import Path

from psycopg import sql

from meteoandalucia.db.connection import connect
from meteoandalucia.siarweb.xml import MEASUREMENT_FIELDS, MeasurementsXML, StationsXML


class SiarwebRepository:
    def __init__(self, connection_factory=connect):
        self.connection_factory = connection_factory

    def import_stations_xml(self, path: str | Path) -> int:
        rows = StationsXML(path).read()
        query = """INSERT INTO siarweb.station
            (id_est, nombre, provincia_id, municipio, latitud, longitud, altitud)
            VALUES (%(id_est)s, %(nombre)s, %(provincia_id)s, %(municipio)s,
                    %(latitud)s, %(longitud)s, %(altitud)s)
            ON CONFLICT (id_est) DO UPDATE SET
                nombre=EXCLUDED.nombre, provincia_id=EXCLUDED.provincia_id,
                municipio=EXCLUDED.municipio, latitud=EXCLUDED.latitud,
                longitud=EXCLUDED.longitud, altitud=EXCLUDED.altitud"""
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, rows)
        return len(rows)

    def load_raw_xml_measurement(self, path: str | Path) -> int:
        return self.load_raw_xml_measurements([path])

    def load_raw_xml_measurements(self, paths: Iterable[str | Path]) -> int:
        """COPY incremental; un fallo de cualquier XML revierte todo el lote.

        No transforma textos ni fechas: un elemento vacío es '', uno ausente
        es NULL. El XML se interpreta, por lo que las entidades se decodifican.
        """
        columns = ("source_file", *MEASUREMENT_FIELDS)
        query = sql.SQL("COPY raw.siarweb_measurement ({}) FROM STDIN").format(
            sql.SQL(", ").join(map(sql.Identifier, columns))
        )
        count = 0
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                with cursor.copy(query) as copy:
                    for path in paths:
                        path = Path(path)
                        file_count = 0
                        for row in MeasurementsXML(path):
                            copy.write_row(
                                [path.name, *(row.get(key) for key in MEASUREMENT_FIELDS)]
                            )
                            count += 1
                            file_count += 1
                        if not file_count:
                            raise ValueError(f"{path}: no contiene medidas")
        return count
