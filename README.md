# MeteoAndalucía

Proyecto Python modular para consultar datos meteorológicos de AEMET y RIAweb,
exportar e importar el inventario CSV y almacenar estaciones y medidas en PostgreSQL.
Gestionado con uv; el código y las pruebas están en `python/`. La implementación
Go se ha sustituido por Python.

```sh
cd python
uv sync --locked
uv run python src/scripts/aemet_inventory.py
```

Configura primero el `.env` de la raíz usando `.env.example`. Consulta la
[documentación Python](python/README.md) para preparar la base de datos, consultar
medidas individuales o por lotes y ejecutar pruebas. No se instala ninguna CLI;
las ejecuciones concretas están en `python/src/scripts/`.

- `python/src/meteoandalucia/api/`: clientes AEMET y RIAweb.
- `python/src/meteoandalucia/db/`: repositorios y conexiones PostgreSQL.
- `python/tests/`: pruebas de regresión.
- `sql/`: estructura, catálogos y backup histórico.
- `data/`: inventario y CSV diarios locales, excluidos del seguimiento de Git.

Desde la raíz, Make ofrece `sync`, `check`, `test` e `inventory` como atajos a uv.
