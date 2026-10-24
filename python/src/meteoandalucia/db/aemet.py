"""Persistencia AEMET, compatible con los nombres de columnas existentes."""

from psycopg import sql
from psycopg.rows import dict_row

from meteoandalucia.db.connection import connect
from meteoandalucia.parsing import parse_aemet_measurement
from meteoandalucia.provinces import province_slug
from meteoandalucia.stations_csv import read_stations_csv

ANDALUSIA = (4, 11, 14, 18, 21, 23, 29, 41)


class AemetRepository:
    def __init__(self, connection_factory=connect):
        self.connection_factory = connection_factory

    def stations(self, provinces: tuple[int, ...] | None = ANDALUSIA) -> list[dict]:
        query = """SELECT provincia_id AS prov_code, p.provincia AS province,
            indicativo AS station_code, nombre AS station_name
            FROM aemet.station s JOIN aemet.provincia p ON p.id = s.provincia_id"""
        params = ()
        if provinces is not None:
            query += " WHERE provincia_id = ANY(%s)"
            params = (list(provinces),)
        query += " ORDER BY province, station_name"
        with self.connection_factory() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def import_stations_csv(self, path) -> int:
        rows = read_stations_csv(path)
        query = """INSERT INTO aemet.station
            (indicativo, nombre, provincia_id, altitud, latitud, longitud, indsinop)
            SELECT %(indicativo)s, %(nombre)s, id, %(altitud)s,
                %(latitud)s, %(longitud)s, %(indsinop)s FROM aemet.provincia
            WHERE slug = %(slug)s
            ON CONFLICT (indicativo) DO UPDATE SET
                nombre=EXCLUDED.nombre, provincia_id=EXCLUDED.provincia_id,
                altitud=EXCLUDED.altitud, latitud=EXCLUDED.latitud,
                longitud=EXCLUDED.longitud, indsinop=EXCLUDED.indsinop"""
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                for line, row in enumerate(rows, 2):
                    row["slug"] = province_slug(row["provincia"])
                    cursor.execute(query, row)
                    if cursor.rowcount != 1:
                        raise ValueError(
                            f"Registro {line}: provincia ausente o ambigua: {row['provincia']}"
                        )
        return len(rows)

    def insert_measurements(self, rows: list[dict]) -> int:
        parsed = [parse_aemet_measurement(row) for row in rows]
        if not parsed:
            return 0
        columns = list(parsed[0])
        query = sql.SQL("INSERT INTO aemet.daily_measurement ({}) VALUES ({})").format(
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder(column) for column in columns),
        )
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, parsed)
        return len(parsed)
