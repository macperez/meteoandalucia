"""Descarga reanudable del histórico RIAweb por estación y año."""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from zoneinfo import ZoneInfo

from meteoandalucia.api.http import APIError
from meteoandalucia.api.riaweb import RiawebClient
from meteoandalucia.common.config import DATA_DIR
from meteoandalucia.common.csv import export_daily_csv
from meteoandalucia.riaweb.stations_csv import read_stations_csv

START = "2015-01-01"
END = datetime.now(ZoneInfo("Europe/Madrid")).date().isoformat()
PROVINCES = {4, 11, 14, 18, 21, 23, 29, 41}


def download_block(province, code, first, last, path):
    client = RiawebClient()
    for attempt in range(4):
        try:
            rows = client.measurements(province, code, first, last, et0=False)
            break
        except APIError as exc:
            if str(exc) == "HTTP 404":
                return {"status": "http404", "rows": 0, "et0": False}
            if attempt == 3:
                raise
            time.sleep(2**attempt)
    if any(not first <= row.get("fecha", "") <= last for row in rows):
        raise ValueError("Fecha fuera del periodo solicitado")
    if rows:
        temporary = path.with_suffix(".csv.tmp")
        try:
            export_daily_csv(temporary, rows)
            for attempt in range(4):
                try:
                    temporary.replace(path)
                    break
                except PermissionError:
                    if attempt == 3:
                        raise
                    time.sleep(0.2)
        finally:
            temporary.unlink(missing_ok=True)
    return {"status": "ok", "rows": len(rows), "et0": False}


def main():
    stations = read_stations_csv(DATA_DIR / "riamet" / "estaciones.csv")
    directory = DATA_DIR / "riamet" / f"diarios_{START}_{END}"
    directory.mkdir(parents=True, exist_ok=True)
    manifest_path = directory / "resumen.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    )
    errors = {}
    jobs = []
    for station in stations:
        province, code = station["provincia_id"], station["codigoEstacion"]
        if province not in PROVINCES:
            continue
        for year in range(date.fromisoformat(START).year, date.fromisoformat(END).year + 1):
            first, last = max(START, f"{year}-01-01"), min(END, f"{year}-12-31")
            key = f"{province}_{code}_{first}_{last}"
            path = directory / f"{key}.csv"
            previous = manifest.get(key, {})
            if (
                previous.get("status") in {"ok", "http404"}
                and previous.get("et0") is False
                and (previous["rows"] == 0 or (path.exists() and path.stat().st_size))
            ):
                continue
            jobs.append((province, code, first, last, key, path))
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending = {pool.submit(download_block, *job[:4], job[5]): job[4] for job in jobs}
        for future in as_completed(pending):
            key = pending[future]
            try:
                manifest[key] = future.result()
                print(f"{key}: {manifest[key]}", flush=True)
            except Exception as exc:
                errors[key] = str(exc)
                manifest[key] = {"status": "error", "error": str(exc)}
                print(f"ERROR {key}: {exc}", flush=True)
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    print(
        f"Completado: {sum(x.get('rows', 0) for x in manifest.values())} registros; "
        f"{len(errors)} errores. Carpeta: {directory}",
        flush=True,
    )
    if errors:
        raise RuntimeError(f"{len(errors)} bloques pendientes; vuelve a ejecutar para reintentar")


if __name__ == "__main__":
    main()
