-- Carga de raw.riamet_measurement en riamet.daily_measurement.
-- id se genera automaticamente. Requiere PostgreSQL 16+ (pg_input_is_valid).
-- Vacio y marcas conocidas quedan NULL; otros valores invalidos producen error.
-- Excluye fechas vacias, estaciones no inventariadas y horas invalidas filtradas.
-- Conserva duplicados: repetir la carga vuelve a insertar las mismas filas.
WITH normalizados AS (
    SELECT
        NULLIF(btrim(r.provincia_id), '') AS provincia_id,
        NULLIF(btrim(r.codigo_estacion), '') AS codigo_estacion,
        NULLIF(btrim(r.fecha), '') AS fecha,
        NULLIF(btrim(r.dia), '') AS dia,
        replace(NULLIF(btrim(r."tempMedia"), ''), ',', '.') AS "tempMedia",
        replace(NULLIF(btrim(r."tempMax"), ''), ',', '.') AS "tempMax",
        NULLIF(btrim(r."horMinTempMax"), '') AS "horMinTempMax",
        replace(NULLIF(btrim(r."tempMin"), ''), ',', '.') AS "tempMin",
        NULLIF(btrim(r."horMinTempMin"), '') AS "horMinTempMin",
        replace(NULLIF(btrim(r."humedadMedia"), ''), ',', '.') AS "humedadMedia",
        replace(NULLIF(btrim(r."humedadMax"), ''), ',', '.') AS "humedadMax",
        NULLIF(btrim(r."horMinHumMax"), '') AS "horMinHumMax",
        replace(NULLIF(btrim(r."humedadMin"), ''), ',', '.') AS "humedadMin",
        NULLIF(btrim(r."horMinHumMin"), '') AS "horMinHumMin",
        replace(NULLIF(btrim(r."velViento"), ''), ',', '.') AS "velViento",
        replace(NULLIF(btrim(r."dirViento"), ''), ',', '.') AS "dirViento",
        replace(NULLIF(btrim(r."velVientoMax"), ''), ',', '.') AS "velVientoMax",
        NULLIF(btrim(r."horMinVelMax"), '') AS "horMinVelMax",
        replace(NULLIF(btrim(r."dirVientoVelMax"), ''), ',', '.') AS "dirVientoVelMax",
        replace(NULLIF(btrim(r.radiacion), ''), ',', '.') AS radiacion,
        replace(NULLIF(btrim(r.precipitacion), ''), ',', '.') AS precipitacion,
        replace(NULLIF(btrim(r.bateria), ''), ',', '.') AS bateria,
        NULLIF(btrim(r."fechaUtlMod"), '') AS "fechaUtlMod",
        replace(NULLIF(btrim(r.et0), ''), ',', '.') AS et0
    FROM raw.riamet_measurement AS r
), filtrados AS (
    SELECT *
    FROM normalizados
    -- Excluye horas anomalas (por ejemplo 12:80); --:-- es ausencia.
    WHERE NOT EXISTS (
        SELECT 1
        FROM unnest(ARRAY[
            "horMinTempMax", "horMinTempMin", "horMinHumMax",
            "horMinHumMin", "horMinVelMax"
        ]) AS horas(valor)
        WHERE NOT pg_input_is_valid(NULLIF(valor, '--:--'), 'time')
    )
), tipados AS (
    SELECT
        provincia_id::smallint AS provincia_id,
        codigo_estacion::integer AS codigo_estacion,
        fecha::date AS fecha,
        dia::smallint AS dia,
        "tempMedia"::numeric AS "tempMedia",
        "tempMax"::numeric AS "tempMax",
        NULLIF("horMinTempMax", '--:--')::time without time zone AS "horMinTempMax",
        "tempMin"::numeric AS "tempMin",
        NULLIF("horMinTempMin", '--:--')::time without time zone AS "horMinTempMin",
        "humedadMedia"::numeric AS "humedadMedia",
        "humedadMax"::numeric AS "humedadMax",
        NULLIF("horMinHumMax", '--:--')::time without time zone AS "horMinHumMax",
        "humedadMin"::numeric AS "humedadMin",
        NULLIF("horMinHumMin", '--:--')::time without time zone AS "horMinHumMin",
        "velViento"::numeric AS "velViento",
        "dirViento"::numeric AS "dirViento",
        "velVientoMax"::numeric AS "velVientoMax",
        NULLIF("horMinVelMax", '--:--')::time without time zone AS "horMinVelMax",
        "dirVientoVelMax"::numeric AS "dirVientoVelMax",
        radiacion::numeric AS radiacion,
        precipitacion::numeric AS precipitacion,
        bateria::numeric AS bateria,
        "fechaUtlMod"::timestamp with time zone AS "fechaUtlMod",
        et0::numeric AS et0
    FROM filtrados
)
INSERT INTO riamet.daily_measurement (
    provincia_id,
    codigo_estacion,
    fecha,
    dia,
    "tempMedia",
    "tempMax",
    "horMinTempMax",
    "tempMin",
    "horMinTempMin",
    "humedadMedia",
    "humedadMax",
    "horMinHumMax",
    "humedadMin",
    "horMinHumMin",
    "velViento",
    "dirViento",
    "velVientoMax",
    "horMinVelMax",
    "dirVientoVelMax",
    radiacion,
    precipitacion,
    bateria,
    "fechaUtlMod",
    et0
)
SELECT
    s.provincia_id,
    s.codigo_estacion,
    t.fecha,
    t.dia,
    t."tempMedia",
    t."tempMax",
    t."horMinTempMax",
    t."tempMin",
    t."horMinTempMin",
    t."humedadMedia",
    t."humedadMax",
    t."horMinHumMax",
    t."humedadMin",
    t."horMinHumMin",
    t."velViento",
    t."dirViento",
    t."velVientoMax",
    t."horMinVelMax",
    t."dirVientoVelMax",
    t.radiacion,
    t.precipitacion,
    t.bateria,
    t."fechaUtlMod",
    t.et0
FROM tipados AS t
JOIN riamet.station AS s
    ON s.provincia_id = t.provincia_id
   AND s.codigo_estacion = t.codigo_estacion
WHERE t.fecha IS NOT NULL;

-- Auditorias de raw frente al destino cargado: measurement_audit.sql
