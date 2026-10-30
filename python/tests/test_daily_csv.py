import csv
from unittest.mock import Mock

import pytest

from meteoandalucia.api.aemet import AemetClient
from meteoandalucia.common.csv import export_daily_csv


def test_all_stations_direct_endpoint():
    http = Mock()
    rows = [{"fecha": "2023-01-01", "indicativo": "0010", "tmed": "12,3"}]
    http.get.side_effect = [{"estado": 200, "datos": "https://example.com/data"}, rows]
    assert AemetClient("token", http=http).daily_all_stations("2023-01-01", "2023-01-02") == rows
    url, headers = http.get.call_args_list[0].args
    assert url.endswith(
        "/fechaini/2023-01-01T00%3A00%3A00UTC/fechafin/2023-01-02T23%3A59%3A59UTC/todasestaciones"
    )
    assert headers["api_key"] == "token"
    assert http.get.call_args_list[1].args == ("https://example.com/data",)


def test_invalid_dates_do_not_make_request():
    http = Mock()
    with pytest.raises(ValueError):
        AemetClient("token", http=http).daily_all_stations("2023-01-02", "2023-01-01")
    http.get.assert_not_called()


def test_csv_keeps_all_fields_and_original_values(tmp_path):
    rows = [
        {
            "fecha": "2023-01-01",
            "indicativo": "0010",
            "nombre": 'MÁLAGA, "AEROPUERTO"',
            "prec": "Ip",
            "tmed": "12,3",
        },
        {"fecha": "2023-01-01", "indicativo": "0011", "hrMedia": "75"},
    ]
    path = export_daily_csv(tmp_path / "data" / "daily.csv", rows)
    with path.open(encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        exported = list(reader)
        assert reader.fieldnames == ["fecha", "indicativo", "nombre", "prec", "tmed", "hrMedia"]
    assert exported[0]["indicativo"] == "0010"
    assert exported[0]["nombre"] == rows[0]["nombre"]
    assert exported[0]["prec"] == "Ip"
    assert exported[0]["tmed"] == "12,3"
    assert exported[0]["hrMedia"] == ""
    assert exported[1]["hrMedia"] == "75"


def test_empty_response_does_not_overwrite(tmp_path):
    path = tmp_path / "daily.csv"
    path.write_text("existing data", encoding="utf-8")
    with pytest.raises(ValueError, match="No hay registros"):
        export_daily_csv(path, [])
    assert path.read_text(encoding="utf-8") == "existing data"
