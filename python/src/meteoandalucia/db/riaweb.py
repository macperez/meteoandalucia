"""Persistencia de estaciones y medidas diarias RIAweb."""

from psycopg import sql
from psycopg.rows import dict_row

from meteoandalucia.db.connection import connect
from meteoandalucia.riaweb.measurements import parse_riaweb_measurement

STATION_FIELDS = {
    "station_code": "codigoEstacion",
    "station_name": "nombre",
    "under_plastic": "bajoplastico",
    "active": "activa",
    "visible": "visible",
    "longitude": "longitud",
    "latitude": "latitud",
    "altitude": "altitud",
    "xutm": "xutm",
    "yutm": "yutm",
    "huso": "huso",
}


class RiawebRepository:
    def __init__(self, connection_factory=connect):
        self.connection_factory = connection_factory

    def stations(self, active_only: bool = False) -> list[dict]:
        query = """SELECT s.prov AS prov_code, p.name AS province,
            s.station_code, s.station_name, s.active
            FROM meteo.station s JOIN meteo.provincias p ON p.postal_code = s.prov"""
        if active_only:
            query += " WHERE s.active = true"
        query += " ORDER BY p.name, s.station_code"
        with self.connection_factory() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def _insert(self, table: str, rows: list[dict]) -> int:
        if not rows:
            return 0
        columns = list(rows[0])
        query = sql.SQL("INSERT INTO meteo.{} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder(column) for column in columns),
        )
        with self.connection_factory() as connection:
            with connection.cursor() as cursor:
                cursor.executemany(query, rows)
        return len(rows)

    def insert_stations(self, rows: list[dict]) -> int:
        parsed = []
        for row in rows:
            station = {column: row.get(key) for column, key in STATION_FIELDS.items()}
            station["prov"] = int(row["provincia"]["id"])
            station["station_code"] = int(row["codigoEstacion"])
            parsed.append(station)
        return self._insert("station", parsed)

    def insert_measurements(self, rows: list[dict], province: int, station: int) -> int:
        return self._insert(
            "daily_measurement", [parse_riaweb_measurement(row, province, station) for row in rows]
        )

    def insert_measurement(self, row: dict, province: int, station: int) -> int:
        return self.insert_measurements([row], province, station)
