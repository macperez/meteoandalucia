# meteoandalucia

## Python

El proyecto Python está en [`python/`](python/README.md) y se gestiona con uv.

```sh
cd python
uv sync
```

Los scripts Python se guardan en `python/src/scripts/`.

## AEMET: inventario de estaciones

Añade tu token de AEMET al archivo `.env` de la raíz del proyecto:

```dotenv
API_KEY=tu_token_de_aemet
```

El archivo `.env` está excluido de Git. `.env.example` sirve como plantilla.
También puedes definir `API_KEY` como variable de entorno; tiene prioridad sobre `.env`.

Ejecuta desde la raíz del proyecto:

```sh
go run ./cmd/aemet --list
```

Usa la ruta del paquete (`./cmd/aemet`), no solo `cmd/aemet/main.go`:
Go necesita compilar también `stations.go`, que pertenece al mismo paquete.

Consulta directamente la API de AEMET e imprime todas las estaciones del inventario
nacional, con código, provincia, nombre, altitud, latitud, longitud e indicativo sinóptico.
No requiere base de datos. Las coordenadas conservan el formato original de AEMET.

La API devuelve primero un enlace `datos`, que el CLI descarga para obtener las
estaciones. Documentación: https://opendata.aemet.es/dist/

`go run` compila y ejecuta una copia temporal en la caché de Go. Para obtener
un ejecutable persistente en Windows, compila desde la raíz del proyecto:

```sh
go build -o bin/aemet.exe ./cmd/aemet
.\bin\aemet.exe --list
```

El ejecutable queda en `bin/aemet.exe`. Puedes copiarlo a otra carpeta;
necesita `API_KEY` en el entorno o un `.env` en el directorio desde el que lo ejecutes.
No necesita Go instalado para ejecutarse.

Con Make, `make build` (o `make compile-aemet`) genera el mismo ejecutable.
`make client-run ARGS=--list` lo compila y ejecuta.

Para exportar el inventario a CSV:

```sh
make build
.\bin\aemet.exe --csv
```

Guarda `estaciones.csv` junto al ejecutable (`bin/estaciones.csv` en este ejemplo)
y muestra la ruta completa y el número de estaciones exportadas. Si ya existe,
lo sobrescribe. El CSV utiliza UTF-8, comas como separador y los nombres de campos
de AEMET: `indicativo,nombre,provincia,altitud,latitud,longitud,indsinop`.
Puedes combinar `--list --csv` para imprimir y exportar con una sola consulta.
Para conservar el CSV, usa el ejecutable compilado: con `go run` se escribiría
junto al ejecutable temporal de Go.

La función Go `posg.ImportAemetStationsCSV(ctx, "bin/estaciones.csv")` permite
importar el inventario en las tablas de `sql/aemet_ddl.sql`. Devuelve el número
de estaciones procesadas y un error. Utiliza las variables `DATABASE_HOST`,
`DATABASE_PORT`, `DATABASE_USER`, `DATABASE_PASSWORD` y `DATABASE_NAME`.
Antes de invocarla, carga `aemet.provincia` con los códigos oficiales, los nombres
de provincia del CSV, sus slugs y su `comunidad_id`. Para crear y cargar los catálogos,
ejecuta en orden `sql/comunidades_ddl.sql`, `sql/comunidades_inserts.sql`,
`sql/aemet_ddl.sql` y `sql/provincias_inserts.sql`.
La búsqueda ignora mayúsculas y espacios exteriores,
pero no cambia tildes ni nombres. Actualiza estaciones existentes por `indicativo`,
convierte el indicativo sinóptico vacío en `NULL` y revierte toda la importación
si falla algún registro. Esta función todavía no está conectada a una opción del CLI.

## RIAweb

La CLI de RIAweb continúa disponible en `cmd/riaweb`.
Recoge datos de https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/datosabiertos
