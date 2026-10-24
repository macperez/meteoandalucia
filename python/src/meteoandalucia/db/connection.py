"""Conexiones configuradas mediante DATABASE_*; sin conexiones al importar."""

import os

import psycopg
from psycopg import sql


def connect():
    names = {
        "host": "HOST",
        "port": "PORT",
        "user": "USER",
        "password": "PASSWORD",
        "dbname": "NAME",
    }
    options = {
        key: os.environ[f"DATABASE_{value}"]
        for key, value in names.items()
        if os.environ.get(f"DATABASE_{value}")
    }
    return psycopg.connect(
        **options, sslmode=os.getenv("DATABASE_SSLMODE", "prefer"), connect_timeout=10
    )


def ping(connection_factory=connect) -> bool:
    with connection_factory() as connection:
        connection.execute("SELECT 1")
    return True


def truncate(schema: str, table: str, connection_factory=connect) -> None:
    with connection_factory() as connection:
        connection.execute(
            sql.SQL("TRUNCATE TABLE {}.{}").format(sql.Identifier(schema), sql.Identifier(table))
        )
