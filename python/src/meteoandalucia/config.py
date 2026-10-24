"""Configuración explícita; las variables del entorno tienen prioridad sobre .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data"


def load_environment(path: Path | None = None) -> None:
    load_dotenv(path or ROOT / ".env", override=False)


def api_key() -> str:
    key = os.getenv("API_KEY", "").strip()
    if not key:
        raise ValueError("Falta API_KEY en el entorno o en .env")
    return key
