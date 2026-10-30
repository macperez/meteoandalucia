"""Correspondencia explícita de nombres AEMET con los slugs del catálogo."""

import re
import unicodedata

ALIASES = {
    "araba-alava": "alava",
    "bizkaia": "vizcaya",
    "gipuzkoa": "guipuzcoa",
    "baleares": "illes-balears",
    "illes-balears": "illes-balears",
    "sta-cruz-de-tenerife": "santa-cruz-de-tenerife",
}


def province_slug(name: str) -> str:
    normalized = unicodedata.normalize("NFKD", name.strip().lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return ALIASES.get(slug, slug)
