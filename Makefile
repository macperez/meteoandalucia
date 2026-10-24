.DEFAULT_GOAL := check

.PHONY: sync check test inventory

sync:
	cd python && uv sync --locked

check:
	cd python && uv run --locked ruff check .
	cd python && uv run --locked ruff format --check .

test:
	cd python && uv run --locked pytest

inventory:
	cd python && uv run --locked python src/scripts/aemet_inventory.py
