-- PostgreSQL: estructura del inventario exportado en bin/estaciones.csv.
-- Crea las tablas en una base nueva o en un esquema sin estas tablas.
-- No modifica ni migra la tabla aemet.station del antiguo meteobackup.sql.
-- Ejecutar después de comunidades_ddl.sql.
-- El CSV no contiene la CCAA: se relaciona mediante el catálogo de provincias.

BEGIN;

CREATE SCHEMA IF NOT EXISTS aemet;

CREATE TABLE aemet.provincia (
    -- Código oficial de provincia; se asigna explícitamente, no es autonumérico.
    id smallint PRIMARY KEY,
    slug text NOT NULL UNIQUE,
    provincia text NOT NULL UNIQUE,
    comunidad_id integer NOT NULL,
    CONSTRAINT provincia_comunidad_fk FOREIGN KEY (comunidad_id)
        REFERENCES aemet.comunidades (id),
    CONSTRAINT provincia_id_check CHECK (id BETWEEN 1 AND 52),
    CONSTRAINT provincia_slug_check CHECK (btrim(slug) <> ''),
    CONSTRAINT provincia_nombre_check CHECK (btrim(provincia) <> '')
);

CREATE INDEX provincia_comunidad_id_idx ON aemet.provincia (comunidad_id);

CREATE TABLE aemet.station (
    indicativo text PRIMARY KEY,
    nombre text NOT NULL,
    provincia_id smallint NOT NULL,
    altitud integer NOT NULL,
    latitud varchar(7) NOT NULL,
    longitud varchar(7) NOT NULL,
    -- Es opcional en el inventario y puede tener ceros iniciales.
    indsinop text,
    CONSTRAINT station_provincia_fk FOREIGN KEY (provincia_id)
        REFERENCES aemet.provincia (id),
    CONSTRAINT station_indicativo_check CHECK (btrim(indicativo) <> ''),
    CONSTRAINT station_nombre_check CHECK (btrim(nombre) <> ''),
    -- Se conserva el dato original: MARBELLA (6083X) incluye 362860N.
    -- Se valida el formato, sin rechazar los segundos 60 del inventario.
    CONSTRAINT station_latitud_check CHECK (latitud ~ '^[0-9]{6}[NS]$'),
    CONSTRAINT station_longitud_check CHECK (
        longitud ~ '^[0-9]{6}[EW]$'
    ),
    CONSTRAINT station_indsinop_check CHECK (indsinop ~ '^[0-9]{5}$')
);

CREATE INDEX station_provincia_id_idx ON aemet.station (provincia_id);

COMMENT ON COLUMN aemet.station.altitud IS 'Altitud en metros sobre el nivel del mar.';
COMMENT ON COLUMN aemet.station.latitud IS 'Formato AEMET: DDMMSS seguido de N o S.';
COMMENT ON COLUMN aemet.station.longitud IS 'Formato AEMET del CSV: DDMMSS seguido de E o W.';
COMMENT ON COLUMN aemet.station.indsinop IS 'Indicativo sinóptico; NULL si el CSV lo deja vacío.';

-- Mapeo de importación: CSV.provincia -> provincia.provincia -> station.provincia_id.
-- El resto de campos conserva los nombres de las cabeceras del CSV.
-- Consulta equivalente al CSV original:
-- SELECT s.indicativo, s.nombre, p.provincia, s.altitud,
--        s.latitud, s.longitud, s.indsinop
-- FROM aemet.station AS s
-- JOIN aemet.provincia AS p ON p.id = s.provincia_id;

COMMIT;
