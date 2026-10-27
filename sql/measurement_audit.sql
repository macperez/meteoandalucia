-- Auditoria de medidas AEMET y RIAweb. Solo SELECT; no modifica datos.
-- Ejecutar cada consulta por separado con raw y destino estables.

-- 1. DIFERENCIAS DE CONTEO
-- Diferencia positiva: hay mas filas en raw. Negativa: hay mas en destino.
-- El conteo no comprueba que coincidan los valores de las medidas.
WITH conteos AS (
    SELECT 'AEMET' AS fuente,
           (SELECT count(*) FROM raw.aemet_measurement) AS filas_raw,
           (SELECT count(*) FROM aemet.daily_measurement) AS filas_destino
    UNION ALL
    SELECT 'RIAweb',
           (SELECT count(*) FROM raw.riamet_measurement),
           (SELECT count(*) FROM riamet.daily_measurement)
)
SELECT fuente, filas_raw, filas_destino, filas_raw - filas_destino AS diferencia
FROM conteos;

-- 2. DUPLICADOS
-- Clave natural: estacion y fecha. id distingue registros, no evita duplicados.
-- Se revisan tanto raw como destino para localizar donde aparecen.

-- Duplicados en raw.aemet_measurement.
SELECT indicativo, fecha, count(*) AS filas
FROM raw.aemet_measurement
GROUP BY indicativo, fecha
HAVING count(*) > 1
ORDER BY filas DESC;

-- Duplicados en aemet.daily_measurement.
SELECT indicativo, fecha, count(*) AS filas
FROM aemet.daily_measurement
GROUP BY indicativo, fecha
HAVING count(*) > 1
ORDER BY filas DESC;

-- Duplicados en raw.riamet_measurement.
SELECT provincia_id, codigo_estacion, fecha, count(*) AS filas
FROM raw.riamet_measurement
GROUP BY provincia_id, codigo_estacion, fecha
HAVING count(*) > 1
ORDER BY filas DESC;

-- Duplicados en riamet.daily_measurement.
SELECT provincia_id, codigo_estacion, fecha, count(*) AS filas
FROM riamet.daily_measurement
GROUP BY provincia_id, codigo_estacion, fecha
HAVING count(*) > 1
ORDER BY filas DESC;
