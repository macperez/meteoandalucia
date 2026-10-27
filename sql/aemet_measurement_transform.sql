-- Carga de raw.aemet_measurement en aemet.daily_measurement.
-- id se genera automaticamente. Requiere PostgreSQL 16+ (pg_input_is_valid).
-- Vacio y marcas conocidas quedan NULL; otros valores invalidos producen error.
-- Excluye fechas vacias, estaciones no inventariadas y horas invalidas filtradas.
-- Conserva duplicados: repetir la carga vuelve a insertar las mismas filas.
WITH normalizados AS (
    SELECT
        NULLIF(btrim(r.indicativo), '') AS indicativo,
        NULLIF(btrim(r.fecha), '') AS fecha,
        NULLIF(btrim(r.nombre), '') AS nombre,
        NULLIF(btrim(r.provincia), '') AS provincia,
        NULLIF(btrim(r.altitud), '') AS altitud,
        replace(NULLIF(btrim(r.tmed), ''), ',', '.') AS tmed,
        replace(NULLIF(btrim(r.prec), ''), ',', '.') AS prec,
        replace(NULLIF(btrim(r.tmin), ''), ',', '.') AS tmin,
        NULLIF(btrim(r.horatmin), '') AS horatmin,
        replace(NULLIF(btrim(r.tmax), ''), ',', '.') AS tmax,
        NULLIF(btrim(r.horatmax), '') AS horatmax,
        NULLIF(btrim(r."hrMedia"), '') AS "hrMedia",
        NULLIF(btrim(r."hrMax"), '') AS "hrMax",
        NULLIF(btrim(r."horaHrMax"), '') AS "horaHrMax",
        NULLIF(btrim(r."hrMin"), '') AS "hrMin",
        NULLIF(btrim(r."horaHrMin"), '') AS "horaHrMin",
        replace(NULLIF(btrim(r."pintMax"), ''), ',', '.') AS "pintMax",
        NULLIF(btrim(r."horaPIntMax"), '') AS "horaPIntMax",
        NULLIF(btrim(r.dir), '') AS dir,
        replace(NULLIF(btrim(r.velmedia), ''), ',', '.') AS velmedia,
        replace(NULLIF(btrim(r.racha), ''), ',', '.') AS racha,
        NULLIF(btrim(r.horaracha), '') AS horaracha,
        replace(NULLIF(btrim(r."presMax"), ''), ',', '.') AS "presMax",
        NULLIF(btrim(r."horaPresMax"), '') AS "horaPresMax",
        replace(NULLIF(btrim(r."presMin"), ''), ',', '.') AS "presMin",
        NULLIF(btrim(r."horaPresMin"), '') AS "horaPresMin",
        replace(NULLIF(btrim(r.sol), ''), ',', '.') AS sol
    FROM raw.aemet_measurement AS r
), filtrados AS (
    SELECT *
    FROM normalizados
    -- Anomalias observadas en raw: 65:00, 01:61, etc.
    WHERE coalesce(pg_input_is_valid(NULLIF(horatmin, 'Varias'), 'time'), true)
      AND coalesce(pg_input_is_valid(NULLIF(horatmax, 'Varias'), 'time'), true)
      AND coalesce(pg_input_is_valid(NULLIF(horaracha, 'Varias'), 'time'), true)
), tipados AS (
    SELECT
        indicativo,
        fecha::date AS fecha,
        nombre,
        provincia,
        altitud::integer AS altitud,
        tmed::numeric AS tmed,
        NULLIF(NULLIF(prec, 'Ip'), 'Acum')::numeric AS prec,
        tmin::numeric AS tmin,
        NULLIF(horatmin, 'Varias')::time without time zone AS horatmin,
        tmax::numeric AS tmax,
        NULLIF(horatmax, 'Varias')::time without time zone AS horatmax,
        "hrMedia"::smallint AS "hrMedia",
        "hrMax"::smallint AS "hrMax",
        NULLIF("horaHrMax", 'Varias')::time without time zone AS "horaHrMax",
        "hrMin"::smallint AS "hrMin",
        NULLIF("horaHrMin", 'Varias')::time without time zone AS "horaHrMin",
        "pintMax"::numeric AS "pintMax",
        NULLIF("horaPIntMax", 'Varias')::time without time zone AS "horaPIntMax",
        dir::smallint AS dir,
        velmedia::numeric AS velmedia,
        racha::numeric AS racha,
        NULLIF(horaracha, 'Varias')::time without time zone AS horaracha,
        "presMax"::numeric AS "presMax",
        NULLIF("horaPresMax", 'Varias')::smallint AS "horaPresMax",
        "presMin"::numeric AS "presMin",
        NULLIF("horaPresMin", 'Varias')::smallint AS "horaPresMin",
        sol::numeric AS sol
    FROM filtrados
)
INSERT INTO aemet.daily_measurement (
    indicativo,
    fecha,
    nombre,
    provincia,
    altitud,
    tmed,
    prec,
    tmin,
    horatmin,
    tmax,
    horatmax,
    "hrMedia",
    "hrMax",
    "horaHrMax",
    "hrMin",
    "horaHrMin",
    "pintMax",
    "horaPIntMax",
    dir,
    velmedia,
    racha,
    horaracha,
    "presMax",
    "horaPresMax",
    "presMin",
    "horaPresMin",
    sol
)
SELECT
    s.indicativo,
    t.fecha,
    t.nombre,
    t.provincia,
    t.altitud,
    t.tmed,
    t.prec,
    t.tmin,
    t.horatmin,
    t.tmax,
    t.horatmax,
    t."hrMedia",
    t."hrMax",
    t."horaHrMax",
    t."hrMin",
    t."horaHrMin",
    t."pintMax",
    t."horaPIntMax",
    t.dir,
    t.velmedia,
    t.racha,
    t.horaracha,
    t."presMax",
    t."horaPresMax",
    t."presMin",
    t."horaPresMin",
    t.sol
FROM tipados AS t
JOIN aemet.station AS s
    ON s.indicativo = t.indicativo
WHERE t.fecha IS NOT NULL;

-- Auditorias de raw frente al destino cargado: measurement_audit.sql
