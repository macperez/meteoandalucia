"""CSV de registros completos, conservando sus valores originales."""

import csv
from pathlib import Path


def export_daily_csv(path: str | Path, rows: list[dict]) -> Path:
    """Incluye todos los campos, incluso los presentes solo en algunas estaciones."""
    if not rows:
        raise ValueError("No hay registros; no se ha creado ni sobrescrito el CSV")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path
