"""Descarga reanudable a CSV; no utiliza modelos ni conexiones de base de datos."""

import time
from datetime import timedelta
from pathlib import Path

from meteoandalucia.api.http import APIError
from meteoandalucia.common.csv import export_daily_csv
from meteoandalucia.common.parsing import validate_date_range


def date_blocks(start: str, end: str, days: int = 15):
    current, last = validate_date_range(start, end)
    if days < 1:
        raise ValueError("El tamaño de bloque debe ser positivo")
    while current <= last:
        finish = min(current + timedelta(days=days - 1), last)
        yield current.isoformat(), finish.isoformat()
        current = finish + timedelta(days=1)


def download_daily_range(client, start: str, end: str, directory: Path, *, days=15, pause=3.2):
    blocks = list(date_blocks(start, end, days))
    directory = Path(directory)
    chunks = directory / f"aemet_diarios_{start}_{end}"
    chunks.mkdir(parents=True, exist_ok=True)
    for index, (first, last) in enumerate(blocks, 1):
        path = chunks / f"{first}_{last}.csv"
        if path.exists() and path.stat().st_size:
            print(f"[{index}/{len(blocks)}] Ya descargado: {first} / {last}", flush=True)
            continue
        for attempt in range(4):
            try:
                rows = client.daily_all_stations(first, last)
                break
            except APIError as exc:
                retryable = any(
                    code in str(exc)
                    for code in ("429", "500", "502", "503", "504", "petición HTTP")
                )
                if not retryable or attempt == 3:
                    raise
                delay = 5 * 2**attempt
                print(f"Reintento en {delay}s: {exc}", flush=True)
                time.sleep(delay)
        for row in rows:
            if not first <= row.get("fecha", "") <= last:
                raise ValueError(f"AEMET devolvió una fecha fuera del bloque {first} / {last}")
        temporary = path.with_suffix(".csv.tmp")
        try:
            export_daily_csv(temporary, rows)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"[{index}/{len(blocks)}] {first} / {last}: {len(rows)} registros", flush=True)
        if index < len(blocks):
            time.sleep(pause)
    print(f"Descarga completa: {len(blocks)} CSV en {chunks}", flush=True)
    return chunks
