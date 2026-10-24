"""Lectura y exportación del inventario AEMET con códigos tratados como texto."""

import csv
import re
from pathlib import Path

HEADER = ["indicativo", "nombre", "provincia", "altitud", "latitud", "longitud", "indsinop"]


def export_stations_csv(path: str | Path, stations: list[dict]) -> Path:
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=HEADER, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(stations)
    return path


def read_stations_csv(path: str | Path) -> list[dict]:
    result, seen = [], set()
    with Path(path).open(encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source, strict=True)
        header = next(reader, None)
        alternate = ["provincia_str" if field == "provincia" else field for field in HEADER]
        if header not in (HEADER, alternate):
            raise ValueError("Cabecera CSV incorrecta")
        for line, values in enumerate(reader, 2):
            if not values:
                continue
            if len(values) != len(HEADER):
                raise ValueError(f"Registro {line}: número de columnas incorrecto")
            row = dict(zip(HEADER, (value.strip() for value in values), strict=True))
            if any(not row[key] for key in HEADER[:3]):
                raise ValueError(f"Registro {line}: indicativo, nombre y provincia obligatorios")
            if row["indicativo"] in seen:
                raise ValueError(f"Registro {line}: indicativo duplicado")
            seen.add(row["indicativo"])
            row["altitud"] = int(row["altitud"])
            if not -(2**31) <= row["altitud"] < 2**31:
                raise ValueError(f"Registro {line}: altitud fuera de rango")
            for key, pattern in [("latitud", r"[0-9]{6}[NS]"), ("longitud", r"[0-9]{6}[EW]")]:
                if not re.fullmatch(pattern, row[key]):
                    raise ValueError(f"Registro {line}: {key} inválida")
            if row["indsinop"] and not re.fullmatch(r"[0-9]{5}", row["indsinop"]):
                raise ValueError(f"Registro {line}: indsinop inválido")
            row["indsinop"] = row["indsinop"] or None
            result.append(row)
    return result
