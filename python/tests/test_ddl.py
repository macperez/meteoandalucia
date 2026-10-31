from unittest.mock import MagicMock

import psycopg
import pytest
from meteoandalucia.common.ddl import DdlExecutor
from scripts import execute_ddl


def test_preserves_sql_blocks_and_utf8_bom(tmp_path):
    path = tmp_path / "schema.sql"
    statement = "BEGIN; DO $$ BEGIN PERFORM 1; END $$; COMMIT;"
    path.write_text(statement, encoding="utf-8-sig")
    factory = MagicMock()
    connection = factory.return_value.__enter__.return_value
    DdlExecutor(factory).execute(path)
    connection.execute.assert_called_once_with(statement)
    assert factory.return_value.__exit__.call_args.args[0] is None


def test_sql_error_reaches_connection_context_for_rollback(tmp_path):
    path = tmp_path / "schema.sql"
    path.write_text("BEGIN; CREATE TABLE broken; COMMIT;", encoding="utf-8")
    factory = MagicMock()
    factory.return_value.__enter__.return_value.execute.side_effect = psycopg.ProgrammingError
    with pytest.raises(psycopg.ProgrammingError):
        DdlExecutor(factory).execute(path)
    assert factory.return_value.__exit__.call_args.args[0] is psycopg.ProgrammingError


def test_missing_or_empty_file_does_not_connect(tmp_path):
    path = tmp_path / "schema.sql"
    factory = MagicMock()
    executor = DdlExecutor(factory)
    with pytest.raises(FileNotFoundError):
        executor.execute(path)
    path.write_text(" \n", encoding="utf-8")
    with pytest.raises(ValueError, match="vacio"):
        executor.execute(path)
    factory.assert_not_called()


def test_script_stops_at_first_error(monkeypatch, capsys):
    monkeypatch.setattr(execute_ddl, "load_environment", MagicMock())
    executor = MagicMock()
    executor.execute.side_effect = [None, psycopg.ProgrammingError("DDL invalido")]
    monkeypatch.setattr(execute_ddl, "DdlExecutor", lambda: executor)
    assert execute_ddl.main(["first.sql", "broken.sql", "last.sql"]) == 1
    assert executor.execute.call_count == 2
    output = capsys.readouterr()
    assert "first.sql" in output.out
    assert "broken.sql" in output.err
