-- PROVISIONAL: paso de raw.siarweb_measurement a siarweb.daily_measurement.
-- PostgreSQL 16+ (pg_input_is_valid). Ejecutar tras cargar el inventario station.
-- No modifica raw ni aplica control de calidad, limites o conversiones de unidades.
-- Las variantes se unifican por nombre, pero su equivalencia fisica sigue pendiente:
-- especialmente radiacion, lluvia y direccion NO deben compararse entre formatos
-- como una serie homogenea hasta revisar escalas y agregaciones historicas.
-- Vacio/ausente -> NULL; comas decimales -> puntos; otros numeros invalidos abortan.
-- Fechas admitidas: ISO YYYY-MM-DD o YYYY-MM-DDT00:00:00 (fecha civil, sin zona).
-- No se omiten estaciones desconocidas ni claves invalidas: abortan todo el lote.
-- Duplicados identicos se agrupan; versiones contradictorias abortan sin elegir una.
-- Reejecutar conserva los registros ya existentes (ON CONFLICT DO NOTHING).
-- No actualiza observaciones previas ni registra sospechas en control_medida.
BEGIN;

CREATE TEMP TABLE siarweb_transform_normalizados ON COMMIT DROP AS
SELECT
    coalesce(NULLIF(btrim(r."COD_EST"), ''), NULLIF(btrim(r."cod_est"), '')) AS cod_est,
    NULLIF(btrim(r."FECHA"), '') AS fecha_texto,
    replace(coalesce(NULLIF(btrim(r."T_MAX"), ''), NULLIF(btrim(r."T_Max"), '')), ',', '.') AS t_max,
    replace(coalesce(NULLIF(btrim(r."T_MED"), ''), NULLIF(btrim(r."T_Med"), '')), ',', '.') AS t_med,
    replace(coalesce(NULLIF(btrim(r."T_MIN"), ''), NULLIF(btrim(r."T_Min"), '')), ',', '.') AS t_min,
    replace(coalesce(NULLIF(btrim(r."H_R_MAX"), ''), NULLIF(btrim(r."H_R_Max"), '')), ',', '.') AS h_r_max,
    replace(coalesce(NULLIF(btrim(r."H_R_MED"), ''), NULLIF(btrim(r."H_R_Med"), '')), ',', '.') AS h_r_med,
    replace(coalesce(NULLIF(btrim(r."H_R_MIN"), ''), NULLIF(btrim(r."H_R_Min"), '')), ',', '.') AS h_r_min,
    replace(coalesce(NULLIF(btrim(r."RADIACION"), ''), NULLIF(btrim(r."Radiacion"), ''), NULLIF(btrim(r."PromedioDeRadiacion"), ''), NULLIF(btrim(r."Radicion_Med"), '')), ',', '.') AS radiacion,
    replace(coalesce(NULLIF(btrim(r."LLUVIA"), ''), NULLIF(btrim(r."Lluvia"), ''), NULLIF(btrim(r."SumaDeLluvia"), ''), NULLIF(btrim(r."Lluvia_acum"), '')), ',', '.') AS lluvia,
    replace(coalesce(NULLIF(btrim(r."V_MAX"), ''), NULLIF(btrim(r."V_Max"), '')), ',', '.') AS v_max,
    replace(coalesce(NULLIF(btrim(r."V_MED"), ''), NULLIF(btrim(r."V_Med"), '')), ',', '.') AS v_med,
    replace(coalesce(NULLIF(btrim(r."V_MIN"), ''), NULLIF(btrim(r."V_Min"), '')), ',', '.') AS v_min,
    replace(coalesce(NULLIF(btrim(r."CV1"), ''), NULLIF(btrim(r."SumaDeCV1"), '')), ',', '.') AS cv1,
    replace(coalesce(NULLIF(btrim(r."CV2"), ''), NULLIF(btrim(r."SumaDeCV2"), '')), ',', '.') AS cv2,
    replace(coalesce(NULLIF(btrim(r."CV3"), ''), NULLIF(btrim(r."SumaDeCV3"), '')), ',', '.') AS cv3,
    replace(coalesce(NULLIF(btrim(r."CV4"), ''), NULLIF(btrim(r."SumaDeCV4"), '')), ',', '.') AS cv4,
    replace(coalesce(NULLIF(btrim(r."DIRECCION"), ''), NULLIF(btrim(r."Direccion"), ''), NULLIF(btrim(r."PromedioDeDireccion"), '')), ',', '.') AS direccion,
    replace(NULLIF(btrim(r."LLUVIA_MIN"), ''), ',', '.') AS lluvia_min,
    replace(NULLIF(btrim(r."T_S_MAX"), ''), ',', '.') AS t_s_max,
    replace(NULLIF(btrim(r."T_S_MED"), ''), ',', '.') AS t_s_med,
    replace(NULLIF(btrim(r."T_S_MIN"), ''), ',', '.') AS t_s_min,
    replace(NULLIF(btrim(r."HORAS"), ''), ',', '.') AS horas,
    replace(NULLIF(btrim(r."H_T"), ''), ',', '.') AS h_t,
    replace(NULLIF(btrim(r."H_HR"), ''), ',', '.') AS h_hr,
    replace(NULLIF(btrim(r."H_R"), ''), ',', '.') AS h_r,
    replace(NULLIF(btrim(r."H_LL"), ''), ',', '.') AS h_ll,
    replace(NULLIF(btrim(r."H_TS"), ''), ',', '.') AS h_ts,
    replace(NULLIF(btrim(r."H_V"), ''), ',', '.') AS h_v,
    replace(NULLIF(btrim(r."H_D"), ''), ',', '.') AS h_d,
    replace(NULLIF(btrim(r."CALCULOS"), ''), ',', '.') AS calculos,
    replace(NULLIF(btrim(r."MTMEN0"), ''), ',', '.') AS mtmen0,
    replace(NULLIF(btrim(r."MTMEN7"), ''), ',', '.') AS mtmen7,
    replace(NULLIF(btrim(r."MTMA30"), ''), ',', '.') AS mtma30,
    replace(NULLIF(btrim(r."MVMA50"), ''), ',', '.') AS mvma50,
    ((SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."COD_EST"), ''), NULLIF(btrim(r."cod_est"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."T_MAX"), ''), NULLIF(btrim(r."T_Max"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."T_MED"), ''), NULLIF(btrim(r."T_Med"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."T_MIN"), ''), NULLIF(btrim(r."T_Min"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."H_R_MAX"), ''), NULLIF(btrim(r."H_R_Max"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."H_R_MED"), ''), NULLIF(btrim(r."H_R_Med"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."H_R_MIN"), ''), NULLIF(btrim(r."H_R_Min"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."RADIACION"), ''), NULLIF(btrim(r."Radiacion"), ''), NULLIF(btrim(r."PromedioDeRadiacion"), ''), NULLIF(btrim(r."Radicion_Med"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."LLUVIA"), ''), NULLIF(btrim(r."Lluvia"), ''), NULLIF(btrim(r."SumaDeLluvia"), ''), NULLIF(btrim(r."Lluvia_acum"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."V_MAX"), ''), NULLIF(btrim(r."V_Max"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."V_MED"), ''), NULLIF(btrim(r."V_Med"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."V_MIN"), ''), NULLIF(btrim(r."V_Min"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."CV1"), ''), NULLIF(btrim(r."SumaDeCV1"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."CV2"), ''), NULLIF(btrim(r."SumaDeCV2"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."CV3"), ''), NULLIF(btrim(r."SumaDeCV3"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."CV4"), ''), NULLIF(btrim(r."SumaDeCV4"), '')]) AS variants(v))
     OR (SELECT count(DISTINCT v) > 1 FROM unnest(ARRAY[NULLIF(btrim(r."DIRECCION"), ''), NULLIF(btrim(r."Direccion"), ''), NULLIF(btrim(r."PromedioDeDireccion"), '')]) AS variants(v))) AS variantes_en_conflicto
FROM raw.siarweb_measurement AS r;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM siarweb_transform_normalizados
        WHERE variantes_en_conflicto
    ) THEN
        RAISE EXCEPTION 'SIARweb: variantes con valores distintos en una misma fila raw';
    END IF;
    IF EXISTS (
        SELECT 1 FROM siarweb_transform_normalizados
        WHERE cod_est IS NULL OR fecha_texto IS NULL
           OR fecha_texto !~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}(T00:00:00)?$'
           OR NOT pg_input_is_valid(left(fecha_texto, 10), 'date')
    ) THEN
        RAISE EXCEPTION 'SIARweb: estacion vacia o fecha ausente/invalida; revisar raw';
    END IF;
END;
$$;

CREATE TEMP TABLE siarweb_transform_tipados ON COMMIT DROP AS
SELECT DISTINCT
    cod_est,
    left(fecha_texto, 10)::date AS fecha,
    t_max::numeric AS t_max,
    t_med::numeric AS t_med,
    t_min::numeric AS t_min,
    h_r_max::numeric AS h_r_max,
    h_r_med::numeric AS h_r_med,
    h_r_min::numeric AS h_r_min,
    radiacion::numeric AS radiacion,
    lluvia::numeric AS lluvia,
    v_max::numeric AS v_max,
    v_med::numeric AS v_med,
    v_min::numeric AS v_min,
    cv1::integer AS cv1,
    cv2::integer AS cv2,
    cv3::integer AS cv3,
    cv4::integer AS cv4,
    direccion::numeric AS direccion,
    lluvia_min::numeric AS lluvia_min,
    t_s_max::numeric AS t_s_max,
    t_s_med::numeric AS t_s_med,
    t_s_min::numeric AS t_s_min,
    horas::numeric AS horas,
    h_t::numeric AS h_t,
    h_hr::numeric AS h_hr,
    h_r::numeric AS h_r,
    h_ll::numeric AS h_ll,
    h_ts::numeric AS h_ts,
    h_v::numeric AS h_v,
    h_d::numeric AS h_d,
    calculos::numeric AS calculos,
    mtmen0::numeric AS mtmen0,
    mtmen7::numeric AS mtmen7,
    mtma30::numeric AS mtma30,
    mvma50::numeric AS mvma50
FROM siarweb_transform_normalizados;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM siarweb_transform_tipados
        GROUP BY cod_est, fecha HAVING count(*) > 1
    ) THEN
        RAISE EXCEPTION 'SIARweb: medidas distintas para la misma estacion y fecha; revisar raw';
    END IF;
    IF EXISTS (
        SELECT 1 FROM siarweb_transform_tipados AS t
        WHERE NOT EXISTS (SELECT 1 FROM siarweb.station AS s WHERE s.id_est = t.cod_est)
    ) THEN
        RAISE EXCEPTION 'SIARweb: estaciones no inventariadas; cargar/revisar siarweb.station';
    END IF;
END;
$$;

INSERT INTO siarweb.daily_measurement (
    cod_est,
    fecha,
    t_max,
    t_med,
    t_min,
    h_r_max,
    h_r_med,
    h_r_min,
    radiacion,
    lluvia,
    v_max,
    v_med,
    v_min,
    cv1,
    cv2,
    cv3,
    cv4,
    direccion,
    lluvia_min,
    t_s_max,
    t_s_med,
    t_s_min,
    horas,
    h_t,
    h_hr,
    h_r,
    h_ll,
    h_ts,
    h_v,
    h_d,
    calculos,
    mtmen0,
    mtmen7,
    mtma30,
    mvma50
)
SELECT
    cod_est,
    fecha,
    t_max,
    t_med,
    t_min,
    h_r_max,
    h_r_med,
    h_r_min,
    radiacion,
    lluvia,
    v_max,
    v_med,
    v_min,
    cv1,
    cv2,
    cv3,
    cv4,
    direccion,
    lluvia_min,
    t_s_max,
    t_s_med,
    t_s_min,
    horas,
    h_t,
    h_hr,
    h_r,
    h_ll,
    h_ts,
    h_v,
    h_d,
    calculos,
    mtmen0,
    mtmen7,
    mtma30,
    mvma50
FROM siarweb_transform_tipados
ON CONFLICT (cod_est, fecha) DO NOTHING;

COMMIT;
