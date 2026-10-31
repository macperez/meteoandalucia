-- Requiere ejecutar common_ddl.sql previamente.
-- Inventario RIAweb y entrada raw de los CSV diarios de data/riamet/.
-- Ejecutar una vez antes de importar. Requiere el cat?logo public.provincia.
BEGIN;

CREATE SCHEMA IF NOT EXISTS riamet;

CREATE TABLE riamet.station (
    provincia_id smallint NOT NULL CHECK (provincia_id BETWEEN 1 AND 52),
    provincia_nombre text NOT NULL CHECK (btrim(provincia_nombre) <> ''),
    codigo_estacion integer NOT NULL CHECK (codigo_estacion > 0),
    nombre text NOT NULL CHECK (btrim(nombre) <> ''),
    bajoplastico boolean NOT NULL,
    activa boolean NOT NULL,
    visible boolean NOT NULL,
    longitud text NOT NULL CHECK (longitud ~ '^[0-9]{9}[EW]$'),
    latitud text NOT NULL CHECK (latitud ~ '^[0-9]{9}[NS]$'),
    altitud integer NOT NULL,
    xutm numeric NOT NULL,
    yutm numeric NOT NULL,
    huso smallint NOT NULL CHECK (huso BETWEEN 1 AND 60),
    PRIMARY KEY (provincia_id, codigo_estacion),
    CONSTRAINT station_provincia_fk FOREIGN KEY (provincia_id)
        REFERENCES public.provincia (id)
);

COMMENT ON TABLE riamet.station IS
    'Inventario RIAweb, incluidas las estaciones inactivas. Clave por provincia y estación.';
COMMENT ON COLUMN riamet.station.longitud IS 'Coordenada original del proveedor, sin conversión.';
COMMENT ON COLUMN riamet.station.latitud IS 'Coordenada original del proveedor, sin conversión.';

-- Entrada de ficheros CSV RIAweb antes de cualquier transformación SQL.
-- El esquema raw se crea en common_ddl.sql.

-- Campos originales como text, sin restricciones de calidad o unicidad.
-- La provincia y la estación no vienen en el CSV: se obtienen del nombre
-- provincia_estacion_INICIO_FIN.csv y se incorporan durante la carga.
CREATE TABLE raw.riamet_measurement (
    provincia_id text,
    codigo_estacion text,
    fecha text,
    dia text,
    "tempMedia" text,
    "tempMax" text,
    "horMinTempMax" text,
    "tempMin" text,
    "horMinTempMin" text,
    "humedadMedia" text,
    "humedadMax" text,
    "horMinHumMax" text,
    "humedadMin" text,
    "horMinHumMin" text,
    "velViento" text,
    "dirViento" text,
    "velVientoMax" text,
    "horMinVelMax" text,
    "dirVientoVelMax" text,
    radiacion text,
    precipitacion text,
    bateria text,
    "fechaUtlMod" text,
    et0 text
);

COMMENT ON TABLE raw.riamet_measurement IS
    'Carga textual de los CSV diarios RIAweb. El tipado, limpieza y deduplicación se realizarán después mediante SQL.';
COMMENT ON COLUMN raw.riamet_measurement.provincia_id IS
    'Provincia de la consulta, extraída del nombre del archivo; no incluida en la cabecera CSV.';
COMMENT ON COLUMN raw.riamet_measurement.codigo_estacion IS
    'Estación de la consulta, extraída del nombre del archivo; no incluida en la cabecera CSV.';

-- Para COPY: indicar explícitamente las columnas en el orden de la cabecera.
-- HEADER descarta la primera línea, pero no relaciona nombres con columnas.
-- Incorporar provincia_id y codigo_estacion durante la carga, sin perder
-- la asociación de cada fila con su estación de origen.
-- Usar FORMAT csv, HEADER true, ENCODING 'UTF8' y FORCE_NOT_NULL con la lista
-- de columnas cargadas para preservar vacíos como texto vacío.
-- No convertir fechas, números, horas ni ET0 durante la carga.
-- Destino tipado de las medidas diarias.
-- numeric sin escala fija conserva los decimales originales sin redondeo.
-- Las marcas no convertibles quedan NULL; el original se conserva en raw.
CREATE TABLE riamet.daily_measurement (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    provincia_id smallint NOT NULL,
    codigo_estacion integer NOT NULL,
    fecha date NOT NULL,
    dia smallint,
    "tempMedia" numeric,
    "tempMax" numeric,
    "horMinTempMax" time without time zone,
    "tempMin" numeric,
    "horMinTempMin" time without time zone,
    "humedadMedia" numeric,
    "humedadMax" numeric,
    "horMinHumMax" time without time zone,
    "humedadMin" numeric,
    "horMinHumMin" time without time zone,
    "velViento" numeric,
    "dirViento" numeric,
    "velVientoMax" numeric,
    "horMinVelMax" time without time zone,
    "dirVientoVelMax" numeric,
    radiacion numeric,
    precipitacion numeric,
    bateria numeric,
    "fechaUtlMod" timestamp with time zone,
    et0 numeric,
    CONSTRAINT daily_measurement_station_fk FOREIGN KEY (provincia_id, codigo_estacion)
        REFERENCES riamet.station (provincia_id, codigo_estacion)
);

CREATE INDEX daily_measurement_fecha_idx ON riamet.daily_measurement (fecha);
COMMENT ON TABLE riamet.daily_measurement IS
    'Medidas diarias RIAweb tipadas; una fila por provincia, estaci?n y fecha, despu?s de deduplicar raw.';
COMMENT ON COLUMN riamet.daily_measurement."fechaUtlMod" IS
    'Instante de modificaci?n del proveedor; respeta el desplazamiento horario del CSV.';
COMMENT ON COLUMN riamet.daily_measurement.dia IS
    'Valor entero original del campo dia del proveedor.';

COMMIT;
