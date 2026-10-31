-- Requiere ejecutar common_ddl.sql previamente.
-- XML locales de data/siarweb/. Ejecutar antes de los importadores.
-- No ejecuta cargas ni transforma raw. Requiere el catalogo public.provincia.
BEGIN;

CREATE SCHEMA IF NOT EXISTS siarweb;
-- El esquema raw se crea en common_ddl.sql.

CREATE TABLE siarweb.station (
    id_est text PRIMARY KEY,
    nombre text NOT NULL,
    provincia_id smallint NOT NULL,
    municipio integer,
    latitud numeric,
    longitud numeric,
    altitud integer,
    CONSTRAINT station_provincia_fk FOREIGN KEY (provincia_id)
        REFERENCES public.provincia (id)
);

CREATE INDEX station_provincia_id_idx ON siarweb.station (provincia_id);

COMMENT ON TABLE siarweb.station IS 'Inventario Identificacion_EstacionesClima.xml; coordenadas conservadas sin correcciones.';
COMMENT ON COLUMN siarweb.station.id_est IS 'Identificador original ID_EST; se conserva como texto (por ejemplo AL001).';
COMMENT ON COLUMN siarweb.station.nombre IS 'Nombre original NOMBRE de la estacion.';
COMMENT ON COLUMN siarweb.station.provincia_id IS 'Codigo PROVINCIA del XML; referencia al catalogo public.provincia.';
COMMENT ON COLUMN siarweb.station.municipio IS 'Codigo MUNICIPIO del XML dentro de su provincia; no es un nombre.';
COMMENT ON COLUMN siarweb.station.latitud IS 'LATITUD original, sin corregir valores ni asumir un sistema de referencia no documentado.';
COMMENT ON COLUMN siarweb.station.longitud IS 'LONGITUD original: conservar el signo del XML; no asumir que los positivos son este.';
COMMENT ON COLUMN siarweb.station.altitud IS 'ALTITUD original de la estacion; unidad y datum no definidos en el XML de identificacion.';

-- Todas las etiquetas originales como texto, incluidas variantes entre anios.
-- Elemento ausente: NULL. Elemento presente vacio: cadena vacia.
-- No hay unicidad ni FK en raw; repetir una importacion agrega duplicados.
CREATE TABLE raw.siarweb_measurement (
    source_file text,
    "COD_EST" text,
    "cod_est" text,
    "FECHA" text,
    "T_MAX" text,
    "T_MED" text,
    "T_MIN" text,
    "T_Max" text,
    "T_Med" text,
    "T_Min" text,
    "H_R_MAX" text,
    "H_R_MED" text,
    "H_R_MIN" text,
    "H_R_Max" text,
    "H_R_Med" text,
    "H_R_Min" text,
    "RADIACION" text,
    "Radiacion" text,
    "PromedioDeRadiacion" text,
    "Radicion_Med" text,
    "LLUVIA" text,
    "Lluvia" text,
    "SumaDeLluvia" text,
    "Lluvia_acum" text,
    "LLUVIA_MIN" text,
    "T_S_MAX" text,
    "T_S_MED" text,
    "T_S_MIN" text,
    "V_MAX" text,
    "V_MED" text,
    "V_MIN" text,
    "V_Max" text,
    "V_Med" text,
    "V_Min" text,
    "CV1" text,
    "CV2" text,
    "CV3" text,
    "CV4" text,
    "SumaDeCV1" text,
    "SumaDeCV2" text,
    "SumaDeCV3" text,
    "SumaDeCV4" text,
    "DIRECCION" text,
    "Direccion" text,
    "PromedioDeDireccion" text,
    "HORAS" text,
    "H_T" text,
    "H_HR" text,
    "H_R" text,
    "H_LL" text,
    "H_TS" text,
    "H_V" text,
    "H_D" text,
    "CALCULOS" text,
    "MTMEN0" text,
    "MTMEN7" text,
    "MTMA30" text,
    "MVMA50" text
);
COMMENT ON TABLE raw.siarweb_measurement IS 'Medidas XML sin conversion de valores. Etiquetas originales, entidades XML decodificadas y procedencia del archivo.';
COMMENT ON COLUMN raw.siarweb_measurement.source_file IS 'Nombre del XML de origen; permite identificar el anio y la variante del formato.';

-- Destino tipado para un proceso posterior de limpieza y deduplicacion.
-- Los importadores de esta entrega SOLO cargan station y raw.
-- Correspondencias: COD_EST/cod_est -> cod_est; nombres de temperatura,
-- humedad y viento se unifican en minusculas.
-- RADIACION/Radiacion/PromedioDeRadiacion/Radicion_Med -> radiacion.
-- LLUVIA/Lluvia/SumaDeLluvia/Lluvia_acum -> lluvia.
-- CVn/SumaDeCVn -> cvn; DIRECCION/Direccion/PromedioDeDireccion -> direccion.
-- Las correspondencias de etiquetas NO autorizan conversiones de unidades:
-- comprobar cambios de escala/agregacion entre anios antes de poblar esta tabla.
CREATE TABLE siarweb.daily_measurement (
    cod_est text NOT NULL,
    fecha date NOT NULL,
    t_max numeric,
    t_med numeric,
    t_min numeric,
    h_r_max numeric,
    h_r_med numeric,
    h_r_min numeric,
    radiacion numeric,
    lluvia numeric,
    v_max numeric,
    v_med numeric,
    v_min numeric,
    cv1 integer,
    cv2 integer,
    cv3 integer,
    cv4 integer,
    direccion numeric,
    lluvia_min numeric,
    t_s_max numeric,
    t_s_med numeric,
    t_s_min numeric,
    horas numeric,
    h_t numeric,
    h_hr numeric,
    h_r numeric,
    h_ll numeric,
    h_ts numeric,
    h_v numeric,
    h_d numeric,
    calculos numeric,
    mtmen0 numeric,
    mtmen7 numeric,
    mtma30 numeric,
    mvma50 numeric,
    PRIMARY KEY (cod_est, fecha),
    CONSTRAINT daily_measurement_station_fk FOREIGN KEY (cod_est)
        REFERENCES siarweb.station (id_est)
);
CREATE INDEX siarweb_daily_measurement_fecha_idx ON siarweb.daily_measurement (fecha);
COMMENT ON TABLE siarweb.daily_measurement IS 'Destino diario tipado; una fila por estacion y fecha tras revisar y deduplicar raw. No se carga automaticamente.';
COMMENT ON COLUMN siarweb.daily_measurement.cod_est IS 'Código de la estación de meteorológica';
COMMENT ON COLUMN siarweb.daily_measurement.fecha IS 'Fecha de los datos de este registro; fecha civil diaria, sin zona horaria.';
COMMENT ON COLUMN siarweb.daily_measurement.t_max IS 'Temperatura máxima (ºC)';
COMMENT ON COLUMN siarweb.daily_measurement.t_med IS 'Temperatura media (ºC)';
COMMENT ON COLUMN siarweb.daily_measurement.t_min IS 'Temperatura mínima (ºC)';
COMMENT ON COLUMN siarweb.daily_measurement.h_r_max IS 'Humedad relativa máxima (%)';
COMMENT ON COLUMN siarweb.daily_measurement.h_r_med IS 'Humedad relativa media (%)';
COMMENT ON COLUMN siarweb.daily_measurement.h_r_min IS 'Humedad relativa mínima (%)';
COMMENT ON COLUMN siarweb.daily_measurement.radiacion IS 'Radicación media (w*h/m2) Unidad transcrita del descriptor; no se asume equivalente entre formatos historicos.';
COMMENT ON COLUMN siarweb.daily_measurement.lluvia IS 'Lluvia total (mm)';
COMMENT ON COLUMN siarweb.daily_measurement.v_max IS 'Velocidad de viento máxima (Km/h)';
COMMENT ON COLUMN siarweb.daily_measurement.v_med IS 'Velocidad de viento media (Km/h)';
COMMENT ON COLUMN siarweb.daily_measurement.v_min IS 'Velocidad de viento mínima (Km/h)';
COMMENT ON COLUMN siarweb.daily_measurement.cv1 IS 'Minutos con dirección de viento en el primer cuadrante';
COMMENT ON COLUMN siarweb.daily_measurement.cv2 IS 'Minutos con dirección de viento en el segundo cuadrante';
COMMENT ON COLUMN siarweb.daily_measurement.cv3 IS 'Minutos con dirección de viento en el tercer cuadrante';
COMMENT ON COLUMN siarweb.daily_measurement.cv4 IS 'Minutos con dirección de viento en el cuarto cuadrante';
COMMENT ON COLUMN siarweb.daily_measurement.direccion IS 'Dirección dominante del viento; se usa numeric porque los XML contienen fracciones, sin asumir grados.';
COMMENT ON COLUMN siarweb.daily_measurement.lluvia_min IS 'Campo historico LLUVIA_MIN; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.t_s_max IS 'Campo historico T_S_MAX; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.t_s_med IS 'Campo historico T_S_MED; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.t_s_min IS 'Campo historico T_S_MIN; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.horas IS 'Campo historico HORAS; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_t IS 'Campo historico H_T; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_hr IS 'Campo historico H_HR; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_r IS 'Campo historico H_R; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_ll IS 'Campo historico H_LL; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_ts IS 'Campo historico H_TS; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_v IS 'Campo historico H_V; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.h_d IS 'Campo historico H_D; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.calculos IS 'Campo historico CALCULOS; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.mtmen0 IS 'Campo historico MTMEN0; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.mtmen7 IS 'Campo historico MTMEN7; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.mtma30 IS 'Campo historico MTMA30; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';
COMMENT ON COLUMN siarweb.daily_measurement.mvma50 IS 'Campo historico MVMA50; significado y unidad no definidos en Descripcion_Campos.xml. No se infiere su semantica.';

COMMIT;
