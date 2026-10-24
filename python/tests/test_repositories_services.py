from unittest.mock import MagicMock, Mock

import pytest

from meteoandalucia.db.aemet import AemetRepository
from meteoandalucia.db.riaweb import RiawebRepository
from meteoandalucia.services import measurements_all, riaweb_measurements
from meteoandalucia.stations_csv import HEADER


def database():
    factory = MagicMock()
    connection = factory.return_value.__enter__.return_value
    cursor = connection.cursor.return_value.__enter__.return_value
    return factory, connection, cursor


def test_csv_import_requires_exactly_one_province_and_rolls_back(tmp_path):
    path = tmp_path / "stations.csv"
    path.write_text(",".join(HEADER) + "\nx,n,p,1,364000N,042900W,\n", encoding="utf-8")
    factory, _, cursor = database()
    cursor.rowcount = 0
    with pytest.raises(ValueError, match="provincia"):
        AemetRepository(factory).import_stations_csv(path)
    assert factory.return_value.__exit__.call_args.args[0] is ValueError
    cursor.rowcount = 1
    assert AemetRepository(factory).import_stations_csv(path) == 1
    assert cursor.execute.call_args.args[1]["indsinop"] is None


def test_measurement_batches_and_station_conversion():
    factory, _, cursor = database()
    aemet = AemetRepository(factory)
    assert aemet.insert_measurements([]) == 0
    assert aemet.insert_measurements([{"fecha": "2023-01-01", "indicativo": "0010"}]) == 1
    assert cursor.executemany.call_args.args[1][0]["avg_temp"] is None
    cursor.executemany.side_effect = RuntimeError("database failure")
    with pytest.raises(RuntimeError):
        aemet.insert_measurements([{"fecha": "2023-01-01", "indicativo": "0010"}])
    assert factory.return_value.__exit__.call_args.args[0] is RuntimeError
    cursor.executemany.side_effect = None
    riaweb = RiawebRepository(factory)
    riaweb.insert_stations([{"provincia": {"id": 4}, "codigoEstacion": "041", "nombre": "X"}])
    assert cursor.executemany.call_args.args[1][0]["station_code"] == 41
    assert riaweb.insert_measurement({"fecha": "2023-01-01", "et0": 2}, 4, 41) == 1


def test_station_filters():
    factory, _, cursor = database()
    AemetRepository(factory).stations()
    assert cursor.execute.call_args.args[1] == ([4, 11, 14, 18, 21, 23, 29, 41],)
    AemetRepository(factory).stations(None)
    assert "WHERE" not in cursor.execute.call_args.args[0]
    RiawebRepository(factory).stations(True)
    assert "active = true" in cursor.execute.call_args.args[0]


@pytest.mark.parametrize("provider", ["aemet", "riaweb"])
def test_batch_continues_after_failure(provider):
    client, repository = Mock(), Mock()
    repository.stations.return_value = [
        {"prov_code": 4, "station_code": "001"},
        {"prov_code": 4, "station_code": "002"},
    ]
    client.measurements.side_effect = [RuntimeError("unavailable"), [{"fecha": "2023-01-01"}]]
    repository.insert_measurements.return_value = 1
    result = measurements_all(
        client, repository, "2023-01-01", "2023-01-02", provider=provider, persist=True
    )
    assert len(result.errors) == 1
    assert result.inserted == 1
    assert len(result.measurements) == 1


def test_single_service_no_persistence_by_default():
    client, repository = Mock(), Mock()
    client.measurement.return_value = {"fecha": "2023-01-01"}
    assert riaweb_measurements(client, repository, 4, 41, "2023-01-01") == [{"fecha": "2023-01-01"}]
    repository.insert_measurements.assert_not_called()
