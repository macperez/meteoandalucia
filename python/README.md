# MeteoAndalucía · Python

Implementación Python de AEMET, RIAweb y PostgreSQL. Requiere uv y Python 3.12.
Desde `python/` ejecuta `uv sync --locked`. El paquete se instala en modo editable;
no se registra ninguna herramienta CLI.

## Estructura

```text
src/
  meteoandalucia/
    api/                  # HTTP, inventario y medidas AEMET/RIAweb
    db/                   # Conexión y repositorios PostgreSQL
    config.py             # Carga explícita de .env y variables
    parsing.py            # Fechas, números y correspondencias de columnas
    provinces.py          # Alias de provincias AEMET a slugs del catálogo
    services.py           # Consultas e importación por estación o por lotes
    stations_csv.py        # Lectura y exportación del inventario
  scripts/                # Ejecuciones concretas; sin parser de argumentos
 tests/                   # Pruebas sin llamadas a servicios externos
```

## Configuración

Copia `.env.example` de la raíz a `.env` y configura `API_KEY` y las variables
`DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD`,
`DATABASE_NAME` y `DATABASE_SSLMODE`. Las variables del entorno tienen prioridad.
Los scripts cargan el `.env` de la raíz del repositorio, independientemente del
CWD. Los módulos no consultan APIs ni abren conexiones al importarse.
El inventario AEMET necesita API_KEY pero no PostgreSQL. RIAweb no necesita API_KEY.

## Scripts

Para descargar directamente los datos climatológicos diarios de **todas las estaciones**,
configura `START` y `END` en `src/scripts/aemet_daily_csv.py` y ejecuta desde `python/`:

```sh
uv run python src/scripts/aemet_daily_csv.py
```

Consulta el endpoint `diarios/datos/fechaini/.../fechafin/.../todasestaciones`,
descarga el enlace `datos` y guarda CSV separados en
`data/aemet_diarios_FECHAINICIAL_FECHAFINAL/`. Incluye el día final completo (UTC).
Conserva todos los campos de la
respuesta, textos, comas decimales e indicadores como `Ip`. Si no recibe registros,
no crea ni sobrescribe el archivo. Este script no utiliza PostgreSQL ni crea tablas.
Para históricos largos divide el periodo en bloques de 15 días, guarda los CSV
en esa carpeta, con nombres `INICIOBLOQUE_FINBLOQUE.csv`. No combina los archivos.
Si se interrumpe, vuelve a ejecutar el mismo script para reutilizar los bloques ya
descargados; cada bloque se guarda de forma atómica al completar su descarga.

Ejecutar desde `python/`:

```sh
uv run python src/scripts/aemet_inventory.py
uv run python src/scripts/riaweb_stations.py
```

El inventario AEMET se imprime ordenado y exporta a `data/estaciones.csv` de la raíz.
Sobrescribe ese archivo únicamente al ejecutar el script. Conserva UTF-8, códigos
como texto y coordenadas originales. La consulta RIAweb imprime JSON; permite
persistir las estaciones cambiando `PERSIST` a `True` en el script.

Para importar el CSV local en una transacción:

```sh
uv run python src/scripts/import_aemet_inventory.py
```

Acepta `provincia` o `provincia_str` en la cabecera. Valida columnas, duplicados,
altitud y formatos de coordenadas e indicativo sinóptico; conserva ceros iniciales.
Busca la provincia por slug, normalizando tildes y alias explícitos (ARABA/ALAVA,
BIZKAIA, GIPUZKOA, BALEARES y STA. CRUZ DE TENERIFE). Si falta una provincia, falla
toda la importación. Actualiza estaciones existentes y convierte indsinop vacío a NULL.

Para consultar medidas, edita las constantes de `src/scripts/daily_measurements.py`
y ejecútalo:

```sh
uv run python src/scripts/daily_measurements.py
```

Configura `PROVIDER`, `START`, `END`, `STATION`, `PROVINCE`, `ALL_STATIONS`, `ET0`
y `PERSIST`. Las fechas usan YYYY-MM-DD. END vacío consulta un día. Por defecto no
se escribe en PostgreSQL. ALL_STATIONS requiere END y consulta estaciones de la
base de datos: las ocho provincias andaluzas para AEMET, las activas para RIAweb.
Los lotes continúan tras un fallo, devuelven errores por estación y el script
termina con error si alguna falla. Cada estación se confirma en su propia transacción.

## Uso desde Python

```python
from meteoandalucia.api.aemet import AemetClient
from meteoandalucia.config import api_key, load_environment
from meteoandalucia.db.aemet import AemetRepository
from meteoandalucia.services import aemet_measurements

load_environment()
client = AemetClient(api_key())
repository = AemetRepository()
rows = aemet_measurements(client, repository, "5783", "2023-01-01", "2023-01-02")
# persist=True inserta las medidas; por defecto solo devuelve el JSON.
```

`RiawebClient` ofrece `stations()`, `measurement(province, station, day, et0=True)`
y `measurements(province, station, start, end, et0=True)`.
`RiawebRepository` ofrece `stations(active_only=False)`, `insert_stations(rows)`,
`insert_measurement(row, province, station)` e `insert_measurements(rows, province, station)`.
`AemetRepository` ofrece `stations(provinces=ANDALUSIA)` (`None` para todo el país),
`import_stations_csv(path)` e `insert_measurements(rows)`.
`services.measurements_all(...)` coordina ambos proveedores.
`db.connection` ofrece `connect()`, `ping()` y `truncate(schema, table)`; esta última
solo debe invocarse cuando se quiera vaciar expresamente una tabla.

Las conexiones son context managers: confirman al terminar y revierten ante errores.
Las medidas mantienen la semántica INSERT histórica: una medida AEMET duplicada
produce error por la restricción estación/fecha; no se sobrescribe automáticamente.
Los números vacíos y marcas Ip/Acum/Var se guardan como NULL; números desconocidos
inválidos producen error en vez de convertirse silenciosamente a cero. Las respuestas
originales siguen disponibles en los clientes y servicios; no se archivan automáticamente.

## Base de datos

### Inventario RIAweb en riamet

Ejecuta `sql/riamet_ddl.sql` una vez para crear `riamet.station`. Este esquema
es independiente de las tablas históricas `meteo` usadas por `RiawebRepository`.
Después, desde `python/`, importa el inventario descargado:

```sh
uv run python src/scripts/import_riamet_inventory.py
```

`RiametRepository` (`meteoandalucia.db.riamet`) lee
`data/riamet/estaciones.csv`, incluidas las estaciones inactivas. Valida todo el
CSV antes de conectar y utiliza las variables `DATABASE_*` del `.env` raíz.
Convierte booleanos y coordenadas UTM con coma decimal; conserva las coordenadas
geográficas originales. La clave es `(provincia_id, codigo_estacion)` y las
estaciones existentes se actualizan en una única transacción. Un fallo revierte
toda la importación. El script no ejecuta el DDL automáticamente.

Para una base **nueva**, ejecutar los scripts SQL de la raíz en este orden:

1. `sql/aemet_ddl.sql` (incluye comunidades, provincias, estaciones y `raw.aemet_measurement`).
2. `sql/comunidades_inserts.sql`.
3. `sql/provincias_inserts.sql`.

`comunidades_ddl.sql` permite crear comunidades por separado; no lo ejecutes además
de `aemet_ddl.sql` en la misma base nueva. Los DDL no son migraciones de una base
existente y no se ejecutan automáticamente. `meteobackup.sql` se conserva como
backup histórico; no se necesita cargarlo para preparar la base nueva.

`raw.aemet_measurement` es la tabla de entrada para los 27 campos de los CSV diarios:
todas las columnas son `text`, admiten vacíos y no tienen restricciones de unicidad
ni claves foráneas. Conserva los nombres originales del CSV (los que tienen
mayúsculas se entrecomillan en SQL). No convierte fechas, números con coma, `Ip`,
`Acum`, `Varias` ni horas anómalas. El tipado y la deduplicación se harán después
mediante scripts SQL. La tabla tipada de medidas queda pendiente.

Para cargar con COPY será necesario indicar las columnas explícitamente, siguiendo
el orden de la cabecera de cada fichero: `HEADER` no mapea los nombres y los CSV
pueden tener diferentes columnas u orden. `FORCE_NOT_NULL` con la lista de columnas
cargadas permite conservar los campos vacíos como texto vacío.

La herramienta de carga de un CSV se ejecuta desde `python/`:

```sh
uv run python src/scripts/load_raw_csv_measurement.py aemet --csv ../data/aemet_diarios_2015-01-01_2026-10-01/2015-01-16_2015-01-30.csv
```

Con el entorno activado también puede ejecutarse con `python` directamente.
La ruta se interpreta respecto al directorio de ejecución; admite rutas absolutas.
El script carga el `.env` de la raíz y utiliza las variables `DATABASE_*`.
La tabla `raw.aemet_measurement` debe existir previamente; el comando no ejecuta DDL.

`AemetRepository.load_raw_csv_measurement(path)` implementa la carga en `db/aemet.py`,
mediante la conexión de `db/connection.py`. Utiliza COPY FROM STDIN en una transacción,
sin cargar el fichero completo en memoria. Rechaza columnas desconocidas o duplicadas
y filas con un número incorrecto de campos. Admite columnas opcionales ausentes o
en distinto orden; requiere `fecha` e `indicativo` en la cabecera. No transforma
los valores, ni siquiera fechas o números inválidos. Los vacíos presentes quedan
como texto vacío; las columnas no incluidas quedan en NULL. Si ocurre un error,
se revierte todo el archivo y el comando termina con código distinto de cero.
Cada ejecución añade filas: cargar el mismo archivo de nuevo genera duplicados.

Los métodos históricos de medidas siguen apuntando a `daily_measurement` y no
quedan preparados con estos DDL. La estructura de RIAweb se abordará más adelante.

Las rutas de datos se centralizan en `meteoandalucia.config.DATA_DIR`, que apunta
a `data/` en la raíz. La carpeta está excluida del seguimiento de Git.

## Desarrollo

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

Las pruebas usan HTTP y conexiones simuladas: no consumen cuota AEMET ni escriben
en la base configurada. La prueba del catálogo local verifica los nombres de las
provincias del CSV cuando existe. Para una prueba real de extremo a extremo se
necesitan credenciales de API y una base de pruebas preparada con los DDL.
Las dependencias se añaden con `uv add` o `uv add --dev`. Versiona `uv.lock`.


### CSV hist?ricos RIAweb

Desde `python/`, ejecuta `uv run python src/scripts/riaweb_daily_csv.py`.
Lee todas las estaciones (tambi?n inactivas) de `data/riamet/estaciones.csv`
y consulta las ocho provincias andaluzas desde 2015-01-01 hasta la fecha actual
en Europe/Madrid. Guarda un CSV por provincia, estaci?n y a?o en
`data/riamet/diarios_INICIO_FIN/`, conservando los campos originales.
Se desactiva el c?lculo ET0 porque provoca HTTP 500 en algunos hist?ricos.
Realiza hasta cuatro consultas simult?neas y reintenta los fallos transitorios.
`resumen.json` registra los bloques descargados, las respuestas HTTP 404
y los errores. No se crea CSV para respuestas sin registros. La misma ejecuci?n
se puede reanudar: omite bloques completados y reintenta errores; un HTTP 404
queda registrado como respuesta del proveedor, sin inferir cobertura hist?rica.
No escribe en PostgreSQL.


### Carga raw por fuente

`load_raw_csv_measurement.py --help` lista las fuentes admitidas (`aemet`,
`riaweb`). Desde `python/`:

```sh
uv run python src/scripts/load_raw_csv_measurement.py aemet --csv ../data/archivo.csv
uv run python src/scripts/load_raw_csv_measurement.py riaweb --csv ../data/riamet/diarios_2015-01-01_2026-10-26/14_2_2015-01-01_2015-12-31.csv
uv run python src/scripts/load_raw_csv_measurement.py riaweb --csv ../data/riamet/diarios_2015-01-01_2026-10-26
```

`--csv` admite un archivo o una carpeta, sin buscar en subcarpetas. RIAweb carga
todos los archivos del lote en una ?nica transacci?n en `raw.riamet_measurement`;
un fallo revierte el lote completo. AEMET conserva una transacci?n por archivo.
Las tablas deben existir previamente: el cargador no ejecuta DDL.
RIAweb obtiene `provincia_id` y `codigo_estacion` del nombre
`provincia_estacion_INICIO_FIN.csv`; las dem?s columnas se mapean por cabecera.
Todos los valores se conservan como texto, incluidos vac?os, espacios y anomal?as.
Se rechazan cabeceras desconocidas o duplicadas y filas de longitud incorrecta.
Cada ejecuci?n a?ade filas: repetir una carga genera duplicados.
