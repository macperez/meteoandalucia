import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import psycopg
import pytest

from meteoandalucia.db.aemet import AemetRepository


def database():
    factory = MagicMock()
    connection = factory.return_value.__enter__.return_value
    cursor = connection.cursor.return_value.__enter__.return_value
    copy = cursor.copy.return_value.__enter__.return_value
    return factory, cursor, copy


def test_raw_copy_preserves_text_and_header_order(tmp_path):
    path = tmp_path / "raw.csv"
    path.write_text(
        "\ufeffindicativo,fecha,prec,nombre,horaracha,hrMedia\n"
        '0010,2015-01-01,"12,3","MÁLAGA, AEROPUERTO",Varias,\n'
        '0010,2015-01-01,Ip,"  espacios  ",84:00,75\n',
        encoding="utf-8",
    )
    factory, cursor, copy = database()
    assert AemetRepository(factory).load_raw_csv_measurement(path) == 2
    assert cursor.copy.call_args.args[0].as_string() == (
        'COPY raw.aemet_measurement ("indicativo", "fecha", "prec", "nombre", "horaracha", "hrMedia") '
        "FROM STDIN"
    )
    assert copy.write_row.call_args_list[0].args[0] == [
        "0010",
        "2015-01-01",
        "12,3",
        "MÁLAGA, AEROPUERTO",
        "Varias",
        "",
    ]
    assert copy.write_row.call_args_list[1].args[0] == [
        "0010",
        "2015-01-01",
        "Ip",
        "  espacios  ",
        "84:00",
        "75",
    ]
    assert factory.return_value.__exit__.call_args.args[0] is None


@pytest.mark.parametrize(
    "header", ["", "fecha,fecha,indicativo\n", "fecha,indicativo,extra\n", "fecha,nombre\n"]
)
def test_invalid_header_does_not_connect(tmp_path, header):
    path = tmp_path / "bad.csv"
    path.write_text(header, encoding="utf-8")
    factory, _, _ = database()
    with pytest.raises(ValueError):
        AemetRepository(factory).load_raw_csv_measurement(path)
    factory.assert_not_called()


def test_bad_row_rolls_back_whole_file(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("fecha,indicativo\n2015-01-01,0010\n2015-01-02\n", encoding="utf-8")
    factory, _, copy = database()
    with pytest.raises(ValueError, match="Línea 3"):
        AemetRepository(factory).load_raw_csv_measurement(path)
    copy.write_row.assert_called_once_with(["2015-01-01", "0010"])
    assert factory.return_value.__exit__.call_args.args[0] is ValueError


def test_database_failure_rolls_back(tmp_path):
    path = tmp_path / "raw.csv"
    path.write_text("fecha,indicativo\n2015-01-01,0010\n", encoding="utf-8")
    factory, _, copy = database()
    copy.write_row.side_effect = psycopg.DataError("fallo de carga")
    with pytest.raises(psycopg.DataError):
        AemetRepository(factory).load_raw_csv_measurement(path)
    assert factory.return_value.__exit__.call_args.args[0] is psycopg.DataError


@pytest.fixture
def script():
    path = Path(__file__).parents[1] / "src/scripts/load_raw_csv_measurement.py"
    spec = importlib.util.spec_from_file_location("raw_loader_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_argument_and_success(script, monkeypatch, capsys):
    repository = MagicMock()
    repository.load_raw_csv_measurement.return_value = 2
    monkeypatch.setattr(script, "load_environment", lambda: None)
    monkeypatch.setattr(script, "AemetRepository", lambda: repository)
    assert script.main(["--csv", "path with spaces/file.csv"]) == 0
    repository.load_raw_csv_measurement.assert_called_once_with(Path("path with spaces/file.csv"))
    assert "2 filas en raw.aemet_measurement" in capsys.readouterr().out


def test_script_missing_argument(script):
    with pytest.raises(SystemExit) as exc:
        script.main([])
    assert exc.value.code == 2


def test_script_error_returns_failure(script, monkeypatch, capsys):
    repository = MagicMock()
    repository.load_raw_csv_measurement.side_effect = FileNotFoundError("CSV inexistente")
    monkeypatch.setattr(script, "load_environment", lambda: None)
    monkeypatch.setattr(script, "AemetRepository", lambda: repository)
    assert script.main(["--csv", "missing.csv"]) == 1
    assert "CSV inexistente" in capsys.readouterr().err
