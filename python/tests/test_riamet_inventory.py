import csv
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from meteoandalucia.db.riamet import FIELDS, RiametRepository, read_stations_csv


def write_inventory(path, **changes):
    row = dict(
        zip(
            FIELDS,
            (
                "14",
                "Córdoba",
                "2",
                "Adamuz",
                "False",
                "True",
                "True",
                "042643000W",
                "375951000N",
                "145",
                "373099,0",
                "4206530,0",
                "30",
            ),
            strict=True,
        )
    )
    row.update(changes)
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerow(row)


def test_import_converts_csv_and_rolls_back_on_database_failure(tmp_path):
    path = tmp_path / "estaciones.csv"
    write_inventory(path)
    factory = MagicMock()
    cursor = factory.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value
    repository = RiametRepository(factory)
    assert repository.import_stations_csv(path) == 1
    row = cursor.executemany.call_args.args[1][0]
    assert row["xutm"] == Decimal("373099.0")
    assert row["activa"] is True
    assert row["bajoplastico"] is False
    assert row["longitud"] == "042643000W"
    cursor.executemany.side_effect = RuntimeError("database failure")
    with pytest.raises(RuntimeError):
        repository.import_stations_csv(path)
    assert factory.return_value.__exit__.call_args.args[0] is RuntimeError


@pytest.mark.parametrize(
    "changes",
    [
        {"activa": "yes"},
        {"xutm": "NaN"},
        {"provincia_id": "99"},
        {"longitud": "invalid"},
        {"nombre": ""},
    ],
)
def test_invalid_inventory_never_opens_database(tmp_path, changes):
    path = tmp_path / "estaciones.csv"
    write_inventory(path, **changes)
    factory = MagicMock()
    with pytest.raises(ValueError, match="Línea 2"):
        RiametRepository(factory).import_stations_csv(path)
    factory.assert_not_called()


def test_duplicate_station_rejected(tmp_path):
    path = tmp_path / "estaciones.csv"
    write_inventory(path)
    with path.open("a", encoding="utf-8") as output:
        output.write(path.read_text(encoding="utf-8-sig").splitlines()[1] + "\n")
    with pytest.raises(ValueError, match="duplicada"):
        read_stations_csv(path)
