-- Ejecutar después de comunidades_ddl.sql.
-- Conserva los IDs originales y omite capital_id.
BEGIN;

INSERT INTO aemet.comunidades (id, slug, comunidad) VALUES
(1, 'andalucia', 'Andalucía'),
(2, 'aragon', 'Aragón'),
(3, 'principado-de-asturias', 'Principado de Asturias'),
(4, 'illes-balears', 'Illes Balears'),
(5, 'canarias', 'Canarias'),
(6, 'cantabria', 'Cantabria'),
(7, 'castilla-y-leon', 'Castilla y León'),
(8, 'castilla-la-mancha', 'Castilla - La Mancha'),
(9, 'cataluna', 'Cataluña'),
(10, 'comunitat-valenciana', 'Comunitat Valenciana'),
(11, 'extremadura', 'Extremadura'),
(12, 'galicia', 'Galicia'),
(13, 'comunidad-de-madrid', 'Comunidad de Madrid'),
(14, 'region-de-murcia', 'Región de Murcia'),
(15, 'comunidad-foral-de-navarra', 'Comunidad Foral de Navarra'),
(16, 'pais-vasco', 'País Vasco'),
(17, 'la-rioja', 'La Rioja'),
(18, 'ceuta', 'Ceuta'),
(19, 'melilla', 'Melilla');

-- Los IDs explícitos no avanzan la secuencia de la columna identity.
SELECT setval(
    pg_get_serial_sequence('aemet.comunidades', 'id'),
    (SELECT max(id) FROM aemet.comunidades)
);

COMMIT;
