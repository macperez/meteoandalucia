import csv
from unittest.mock import Mock

import pytest

from meteoandalucia.api.http import APIError
from meteoandalucia.application.aemet_download import date_blocks, download_daily_range


def test_blocks_have_no_gaps_or_overlap():
    assert list(date_blocks("2020-02-28", "2020-03-02", 2)) == [
        ("2020-02-28", "2020-02-29"),
        ("2020-03-01", "2020-03-02"),
    ]
    assert list(date_blocks("2020-01-01", "2020-01-01")) == [("2020-01-01", "2020-01-01")]


def test_download_resume_keeps_csv_separate(tmp_path):
    client = Mock()
    client.daily_all_stations.side_effect = [
        [{"fecha": "2020-01-01", "indicativo": "0010", "prec": "Ip"}],
        APIError("HTTP 401"),
    ]
    with pytest.raises(APIError):
        download_daily_range(client, "2020-01-01", "2020-01-02", tmp_path, days=1, pause=0)
    assert not (tmp_path / "aemet_diarios_2020-01-01_2020-01-02.csv").exists()
    client.daily_all_stations.side_effect = None
    client.daily_all_stations.return_value = [
        {"fecha": "2020-01-02", "indicativo": "0011", "hrMedia": "80"}
    ]
    path = download_daily_range(client, "2020-01-01", "2020-01-02", tmp_path, days=1, pause=0)
    assert client.daily_all_stations.call_args.args == ("2020-01-02", "2020-01-02")
    files = sorted(path.glob("*.csv"))
    assert len(files) == 2
    with files[0].open(encoding="utf-8", newline="") as source:
        assert list(csv.DictReader(source)) == [
            {"fecha": "2020-01-01", "indicativo": "0010", "prec": "Ip"}
        ]
    with files[1].open(encoding="utf-8", newline="") as source:
        assert list(csv.DictReader(source)) == [
            {"fecha": "2020-01-02", "indicativo": "0011", "hrMedia": "80"}
        ]
    assert not (tmp_path / "aemet_diarios_2020-01-01_2020-01-02.csv").exists()
