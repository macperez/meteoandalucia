"""Ejecucion de archivos DDL mediante la conexion del proyecto."""

from pathlib import Path

from meteoandalucia.db.connection import connect


class DdlExecutor:
    def __init__(self, connection_factory=connect):
        self.connection_factory = connection_factory

    def execute(self, path: str | Path) -> None:
        """Ejecuta el archivo completo sin dividir funciones ni bloques SQL.

        Los DDL del proyecto contienen BEGIN/COMMIT. Si no los incluyen,
        el contexto de conexion confirma o revierte la transaccion.
        """
        statement = Path(path).read_text(encoding="utf-8-sig")
        if not statement.strip():
            raise ValueError(f"El archivo DDL esta vacio: {path}")
        with self.connection_factory() as connection:
            connection.execute(statement)
