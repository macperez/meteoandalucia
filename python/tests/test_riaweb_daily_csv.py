import csv

import pytest

from meteoandalucia.api.http import APIError
from scripts import download_riaweb_daily_csv


def test_block_preserves_fields_and_dates(monkeypatch, tmp_path):
    rows = [{"fecha": "2015-01-01", "tempMedia": 12.5, "extra": "original"}]
    monkeypatch.setattr(
        download_riaweb_daily_csv.RiawebClient, "measurements", lambda *a, **k: rows
    )
    path = tmp_path / "block.csv"
    result = download_riaweb_daily_csv.download_block(4, 10, "2015-01-01", "2015-12-31", path)
    assert result == {"status": "ok", "rows": 1, "et0": False}
    with path.open(encoding="utf-8", newline="") as source:
        assert list(csv.DictReader(source)) == [
            {"fecha": "2015-01-01", "tempMedia": "12.5", "extra": "original"}
        ]


def test_404_recorded_without_empty_csv(monkeypatch, tmp_path):
    def missing(*args, **kwargs):
        raise APIError("HTTP 404")

    monkeypatch.setattr(download_riaweb_daily_csv.RiawebClient, "measurements", missing)
    path = tmp_path / "block.csv"
    result = download_riaweb_daily_csv.download_block(4, 10, "2015-01-01", "2015-12-31", path)
    assert result["status"] == "http404"
    assert not path.exists()


def test_out_of_range_response_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(
        download_riaweb_daily_csv.RiawebClient,
        "measurements",
        lambda *a, **k: [{"fecha": "2016-01-01"}],
    )
    path = tmp_path / "block.csv"
    with pytest.raises(ValueError, match="Fecha fuera"):
        download_riaweb_daily_csv.download_block(4, 10, "2015-01-01", "2015-12-31", path)
    assert not path.exists()
