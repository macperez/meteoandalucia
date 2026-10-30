import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import psycopg
import pytest

from meteoandalucia.db.aemet import AemetRepository
from meteoandalucia.db.riamet import RiametRepository


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
        'COPY raw.aemet_measurement ("indicativo", "fecha", "prec", "nombre", '
        '"horaracha", "hrMedia") '
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
    path = Path(__file__).parents[1] / "src/scripts/import_raw_csv_measurement.py"
    spec = importlib.util.spec_from_file_location("raw_loader_script", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_argument_and_success(script, monkeypatch, capsys):
    repository = MagicMock()
    repository.load_raw_csv_measurement.return_value = 2
    monkeypatch.setattr(script, "load_environment", lambda: None)
    monkeypatch.setattr(script, "AemetRepository", lambda: repository)
    assert script.main(["aemet", "--csv", "path with spaces/file.csv"]) == 0
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
    assert script.main(["aemet", "--csv", "missing.csv"]) == 1
    assert "CSV inexistente" in capsys.readouterr().err


def test_riaweb_batch_preserves_identity_and_values(tmp_path):
    paths = [tmp_path / f"{province}_002_2015-01-01_2015-12-31.csv" for province in (4, 14)]
    for path in paths:
        path.write_text('tempMedia,fecha,et0\n"12,3",anómala,\n', encoding="utf-8")
    factory, cursor, copy = database()
    assert RiametRepository(factory).load_raw_csv_measurements(paths) == 2
    factory.assert_called_once()
    assert cursor.copy.call_args.args[0].as_string() == (
        'COPY raw.riamet_measurement ("provincia_id", "codigo_estacion", '
        '"tempMedia", "fecha", "et0") FROM STDIN'
    )
    assert [call.args[0] for call in copy.write_row.call_args_list] == [
        ["4", "002", "12,3", "anómala", ""],
        ["14", "002", "12,3", "anómala", ""],
    ]


@pytest.mark.parametrize(
    "header",
    ["fecha,fecha\n", "tempMedia\n", "fecha,unknown\n", "fecha,provincia_id\n"],
)
def test_riaweb_rejects_invalid_headers(tmp_path, header):
    path = tmp_path / "4_2_2015-01-01_2015-12-31.csv"
    path.write_text(header, encoding="utf-8")
    factory, _, _ = database()
    with pytest.raises(ValueError):
        RiametRepository(factory).load_raw_csv_measurement(path)
    assert factory.return_value.__exit__.call_args.args[0] is ValueError


def test_riaweb_batch_rolls_back_on_second_file_failure(tmp_path):
    first = tmp_path / "4_2_2015-01-01_2015-12-31.csv"
    second = tmp_path / "4_2_2016-01-01_2016-12-31.csv"
    first.write_text("fecha\n2015-01-01\n", encoding="utf-8")
    second.write_text("fecha\n2016-01-01,extra\n", encoding="utf-8")
    factory, _, copy = database()
    with pytest.raises(ValueError):
        RiametRepository(factory).load_raw_csv_measurements([first, second])
    copy.write_row.assert_called_once_with(["4", "2", "2015-01-01"])
    assert factory.return_value.__exit__.call_args.args[0] is ValueError


def test_riaweb_script_directory(script, monkeypatch, tmp_path, capsys):
    paths = [tmp_path / f"4_{station}_2015-01-01_2015-12-31.csv" for station in (1, 2)]
    for path in paths:
        path.touch()
    repository = MagicMock()
    repository.load_raw_csv_measurements.return_value = 10
    monkeypatch.setattr(script, "load_environment", lambda: None)
    monkeypatch.setattr(script, "RiametRepository", lambda: repository)
    assert script.main(["riaweb", "--csv", str(tmp_path)]) == 0
    repository.load_raw_csv_measurements.assert_called_once_with(paths)
    assert "10 filas en raw.riamet_measurement" in capsys.readouterr().out


def test_source_choices_listed(script, capsys):
    with pytest.raises(SystemExit):
        script.main(["unknown", "--csv", "file.csv"])
    assert "{aemet,riaweb}" in capsys.readouterr().err
