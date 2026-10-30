import csv
import re

import pytest

from meteoandalucia.aemet.provinces import province_slug
from meteoandalucia.aemet.stations_csv import read_stations_csv
from meteoandalucia.common.config import DATA_DIR, ROOT, api_key, load_environment


def test_environment_priority(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text("API_KEY=from-file\n", encoding="utf-8")
    monkeypatch.setenv("API_KEY", "from-environment")
    load_environment(path)
    assert api_key() == "from-environment"
    monkeypatch.setenv("API_KEY", "  ")
    with pytest.raises(ValueError):
        api_key()


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("MÁLAGA", "malaga"),
        ("ARABA/ALAVA", "alava"),
        ("BIZKAIA", "vizcaya"),
        ("GIPUZKOA", "guipuzcoa"),
        ("BALEARES", "illes-balears"),
        ("STA. CRUZ DE TENERIFE", "santa-cruz-de-tenerife"),
    ],
)
def test_province_aliases(name, slug):
    assert province_slug(name) == slug


def test_alternative_csv_header(tmp_path):
    path = tmp_path / "stations.csv"
    path.write_text(
        "indicativo,nombre,provincia_str,altitud,latitud,longitud,indsinop\n"
        "0010,X,MALAGA,1,364000N,042900W,\n",
        encoding="utf-8",
    )
    assert read_stations_csv(path)[0]["provincia"] == "MALAGA"


def test_local_inventory_provinces_match_catalog():
    path = DATA_DIR / "estaciones.csv"
    if not path.exists():
        pytest.skip("Inventario local no disponible")
    sql = (ROOT / "sql/provincias_inserts.sql").read_text(encoding="utf-8-sig")
    slugs = set(re.findall(r"\(\d+, '([^']+)'", sql))
    with path.open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    names = {row.get("provincia", row.get("provincia_str")) for row in rows}
    assert {province_slug(name) for name in names} <= slugs
