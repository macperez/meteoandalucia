from decimal import Decimal
from unittest.mock import MagicMock
from xml.etree.ElementTree import ParseError

import pytest

from meteoandalucia.common.xml import XMLRecords
from meteoandalucia.db.siarweb import SiarwebRepository
from meteoandalucia.siarweb.xml import MEASUREMENT_FIELDS, MeasurementsXML, StationsXML
from scripts import import_raw_xml_measurement


def xml_file(tmp_path, body, name="daily.xml"):
    path = tmp_path / name
    path.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><dataroot>{body}</dataroot>', encoding="utf-8"
    )
    return path


def database():
    factory = MagicMock()
    cursor = factory.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    return factory, cursor, cursor.copy.return_value.__enter__.return_value


def test_xml_preserves_text_empty_missing_and_entities(tmp_path):
    path = xml_file(tmp_path, "<row><name>  A &amp; B  </name><empty /></row>")
    records = XMLRecords(path, {"row"})
    assert list(records) == [{"name": "  A & B  ", "empty": ""}]
    assert list(records) == [{"name": "  A & B  ", "empty": ""}]


@pytest.mark.parametrize(
    "body",
    [
        "<other><x>1</x></other>",
        "<row><x>1</x><x>2</x></row>",
        "<row><x><nested>1</nested></x></row>",
        '<row><x unit="m">1</x></row>',
    ],
)
def test_xml_rejects_unexpected_structures(tmp_path, body):
    with pytest.raises(ValueError):
        list(XMLRecords(xml_file(tmp_path, body), {"row"}))


STATION = """<Identificacion_Estaciones_OpenDATA>
<ID_EST>AL001</ID_EST><NOMBRE>Níjar</NOMBRE><PROVINCIA>4</PROVINCIA>
<MUNICIPIO>66</MUNICIPIO><LATITUD>36.9119</LATITUD><LONGITUD>2.1719</LONGITUD>
<ALTITUD>120</ALTITUD></Identificacion_Estaciones_OpenDATA>"""


def test_station_types_upsert_and_coordinates_are_not_corrected(tmp_path):
    path = xml_file(tmp_path, STATION)
    row = StationsXML(path).read()[0]
    assert row["nombre"] == "Níjar"
    assert row["id_est"] == "AL001"
    assert row["provincia_id"] == 4 and row["municipio"] == 66
    assert row["longitud"] == Decimal("2.1719")
    factory, cursor, _ = database()
    assert SiarwebRepository(factory).import_stations_xml(path) == 1
    query, rows = cursor.executemany.call_args.args
    assert "ON CONFLICT (id_est) DO UPDATE" in query
    assert "provincia_id=EXCLUDED.provincia_id" in query
    assert rows == [row]


@pytest.mark.parametrize("body", [STATION + STATION, STATION.replace("120", "invalid"), ""])
def test_invalid_station_does_not_connect(tmp_path, body):
    factory, _, _ = database()
    with pytest.raises(ValueError):
        SiarwebRepository(factory).import_stations_xml(xml_file(tmp_path, body))
    factory.assert_not_called()


def test_station_optional_metadata_can_be_absent(tmp_path):
    body = STATION.replace("<MUNICIPIO>66</MUNICIPIO>", "")
    body = body.replace("<LATITUD>36.9119</LATITUD><LONGITUD>2.1719</LONGITUD>", "")
    row = StationsXML(xml_file(tmp_path, body)).read()[0]
    assert row["municipio"] is None
    assert row["latitud"] is None and row["longitud"] is None


@pytest.mark.parametrize(
    ("tag", "field"),
    [
        ("Diario", "RADIACION"),
        ("Diario_OpenData", "Radiacion"),
        ("Cns_OpenData", "PromedioDeRadiacion"),
        ("Cns_OpenData_ActualizarFcha", "Radicion_Med"),
    ],
)
def test_raw_retains_each_years_original_fields(tmp_path, tag, field):
    path = xml_file(
        tmp_path,
        f"<{tag}><cod_est>AL001</cod_est><FECHA>not a date</FECHA>"
        f"<{field}>  0.26028255 </{field}><Direccion>1.08333333333333</Direccion>"
        f"<T_Max /></{tag}>",
    )
    factory, cursor, copy = database()
    assert SiarwebRepository(factory).load_raw_xml_measurement(path) == 1
    values = copy.write_row.call_args.args[0]
    row = dict(zip(("source_file", *MEASUREMENT_FIELDS), values, strict=True))
    assert row["source_file"] == "daily.xml"
    assert row[field] == "  0.26028255 "
    assert row["FECHA"] == "not a date"
    assert row["Direccion"] == "1.08333333333333"
    assert row["T_Max"] == "" and row["T_MIN"] is None
    assert "COPY raw.siarweb_measurement" in cursor.copy.call_args.args[0].as_string()


@pytest.mark.parametrize(
    "body",
    [
        "<Diario><COD_EST>A</COD_EST></Diario>",
        "<Diario><COD_EST>A</COD_EST><FECHA>x</FECHA><unknown>1</unknown></Diario>",
        "<Identificacion_Estaciones_OpenDATA><ID_EST>A</ID_EST></Identificacion_Estaciones_OpenDATA>",
    ],
)
def test_invalid_measurement_fields(tmp_path, body):
    with pytest.raises(ValueError):
        list(MeasurementsXML(xml_file(tmp_path, body)))


def test_broken_second_file_rolls_back_batch(tmp_path):
    first = xml_file(tmp_path, "<Diario><COD_EST>A</COD_EST><FECHA>x</FECHA></Diario>")
    second = tmp_path / "broken.xml"
    second.write_text("<dataroot><Diario>", encoding="utf-8")
    factory, _, copy = database()
    with pytest.raises(ParseError):
        SiarwebRepository(factory).load_raw_xml_measurements([first, second])
    copy.write_row.assert_called_once()
    assert factory.return_value.__exit__.call_args.args[0] is ParseError


def test_empty_file_rolls_back(tmp_path):
    factory, _, _ = database()
    with pytest.raises(ValueError, match="no contiene medidas"):
        SiarwebRepository(factory).load_raw_xml_measurement(xml_file(tmp_path, ""))
    assert factory.return_value.__exit__.call_args.args[0] is ValueError


def test_cli_selects_only_daily_files(tmp_path, monkeypatch):
    for name in (
        "Clim_Diario_2026.xml",
        "Clim_Diario_2006.xml",
        "Identificacion_EstacionesClima.xml",
        "Descripcion_Campos.xml",
    ):
        (tmp_path / name).touch()
    repository = MagicMock()
    repository.load_raw_xml_measurements.return_value = 2
    monkeypatch.setattr(import_raw_xml_measurement, "load_environment", lambda: None)
    monkeypatch.setattr(import_raw_xml_measurement, "SiarwebRepository", lambda: repository)
    assert import_raw_xml_measurement.main(["siarweb", "--xml", str(tmp_path)]) == 0
    repository.load_raw_xml_measurements.assert_called_once_with(
        [tmp_path / "Clim_Diario_2006.xml", tmp_path / "Clim_Diario_2026.xml"]
    )


def test_cli_reports_xml_error(tmp_path, monkeypatch, capsys):
    path = tmp_path / "bad.xml"
    path.write_text("<dataroot>", encoding="utf-8")
    monkeypatch.setattr(import_raw_xml_measurement, "load_environment", lambda: None)
    factory, _, _ = database()
    monkeypatch.setattr(
        import_raw_xml_measurement, "SiarwebRepository", lambda: SiarwebRepository(factory)
    )
    assert import_raw_xml_measurement.main(["siarweb", "--xml", str(path)]) == 1
    assert "Error al cargar XML" in capsys.readouterr().err
