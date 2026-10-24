# MeteoAndalucía · Python

Entorno para scripts Python del proyecto, gestionado con uv y separado del código Go.
Utiliza Python 3.12 (ver `.python-version`). No instala un paquete ni una CLI.

Desde esta carpeta:

```sh
uv sync
```

`uv sync` crea `.venv` e instala las dependencias y herramientas de desarrollo.
Versiona `uv.lock` para reproducir las dependencias. En CI utiliza `uv sync --locked`.

## Estructura

- `src/scripts/`: scripts Python del proyecto.
- `tests/`: pruebas de los scripts cuando se añada funcionalidad.
- `pyproject.toml`: dependencias y configuración de pytest y Ruff.
- `.python-version`: versión de Python utilizada por uv.

Para ejecutar un script que añadas a `src/scripts/`:

```sh
uv run python src/scripts/nombre_del_script.py
```

## Desarrollo

```sh
uv run ruff check .
uv run ruff format --check .
uv run ruff format .
```

Cuando existan pruebas, ejecútalas con `uv run pytest`.

Añade dependencias con `uv add nombre` y herramientas de desarrollo con
`uv add --dev nombre`. Para eliminar una dependencia, usa `uv remove nombre`.
