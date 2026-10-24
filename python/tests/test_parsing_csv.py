from datetime import date

import pytest

from meteoandalucia.parsing import (
    AEMET_FIELDS,
    RIAWEB_FIELDS,
    nullable_float,
    parse_aemet_measurement,
    parse_riaweb_measurement,
)
from meteoandalucia.stations_csv import HEADER, export_stations_csv, read_stations_csv


@pytest.mark.parametrize(
    ("value", "expected"),
    [("", None), (None, None), ("Ip", None), ("Acum", None), ("12,3", 12.3), ("-2", -2), (0, 0)],
)
def test_nullable_float(value, expected):
    assert nullable_float(value) == expected


@pytest.mark.parametrize("value", ["invalid", "NaN", "inf"])
def test_invalid_numbers(value):
    with pytest.raises(ValueError):
        nullable_float(value)


def test_measurement_fields():
    row = {
        key: ("12:00" if column.startswith("time_") else "1,5")
        for column, key in AEMET_FIELDS.items()
    }
    parsed = parse_aemet_measurement({**row, "fecha": "2023-01-15", "indicativo": "0010"})
    assert parsed["measurement_date"] == date(2023, 1, 15)
    for column in AEMET_FIELDS:
        assert parsed[column] == ("12:00" if column.startswith("time_") else 1.5)
    row = {
        key: ("12:00" if column.startswith("time_") else "2,5")
        for column, key in RIAWEB_FIELDS.items()
    }
    row["fechaUtlMod"] = "2023-01-16T12:00:00"
    parsed = parse_riaweb_measurement({**row, "fecha": "2023-01-15"}, 4, 41)
    assert parsed["prov_id"] == 4 and parsed["station_id"] == 41
    assert parsed["et0"] == 2.5
    assert parsed["dateutlmod"] == row["fechaUtlMod"]


def test_csv_roundtrip(tmp_path):
    row = dict(
        zip(
            HEADER,
            ["0010", 'MÁLAGA, "AEROPUERTO"', "MALAGA", "-2", "362860N", "042900W", "08482"],
            strict=True,
        )
    )
    path = export_stations_csv(
        tmp_path / "stations.csv", [row, {**row, "indicativo": "0011", "indsinop": ""}]
    )
    rows = read_stations_csv(path)
    assert rows[0] == {**row, "altitud": -2}
    assert rows[1]["indsinop"] is None
    path.write_text("\ufeff" + path.read_text(encoding="utf-8"), encoding="utf-8")
    assert read_stations_csv(path) == rows


@pytest.mark.parametrize(
    "body",
    [
        "",
        "nombre,indicativo\n",
        "x,n,p,no,364000N,042900W,\n",
        "x,n,p,1\n",
        ",n,p,1,364000N,042900W,\n",
        "x,n,p,1,364000N,042900W,\nx,n,p,1,364000N,042900W,\n",
    ],
)
def test_csv_errors(tmp_path, body):
    path = tmp_path / "bad.csv"
    prefix = ",".join(HEADER) + "\n" if body.startswith(("x,", ",n")) else ""
    path.write_text(prefix + body, encoding="utf-8")
    with pytest.raises(ValueError):
        read_stations_csv(path)
