-- Los catálogos public.provincia y public.comunidades deben existir.
-- Migra las estaciones existentes sin eliminar los nombres originales.
BEGIN;

ALTER TABLE aemet.station ADD COLUMN IF NOT EXISTS provincia_id smallint;

WITH nombres AS (
    SELECT indicativo,
           trim(both '-' from regexp_replace(
               translate(lower(coalesce(nullif(btrim(provincia_str), ''), provincia)),
                         'áéíóúüñ', 'aeiouun'),
               '[^a-z0-9]+', '-', 'g')) AS slug
    FROM aemet.station
), normalizados AS (
    SELECT indicativo, CASE slug
        WHEN 'araba-alava' THEN 'alava'
        WHEN 'bizkaia' THEN 'vizcaya'
        WHEN 'gipuzkoa' THEN 'guipuzcoa'
        WHEN 'baleares' THEN 'illes-balears'
        WHEN 'sta-cruz-de-tenerife' THEN 'santa-cruz-de-tenerife'
        ELSE slug END AS slug
    FROM nombres
)
UPDATE aemet.station AS s
SET provincia_id = p.id
FROM normalizados AS n JOIN public.provincia AS p ON p.slug = n.slug
WHERE s.indicativo = n.indicativo AND s.provincia_id IS NULL;

-- Si algún nombre no tiene correspondencia, falla y revierte toda la migración.
ALTER TABLE aemet.station ALTER COLUMN provincia_id SET NOT NULL;
ALTER TABLE aemet.station ADD CONSTRAINT station_provincia_fk
    FOREIGN KEY (provincia_id) REFERENCES public.provincia (id);
CREATE INDEX IF NOT EXISTS station_provincia_id_idx ON aemet.station (provincia_id);

-- RIAweb ya utiliza provincia_id como parte de su clave primaria.
ALTER TABLE riamet.station ADD CONSTRAINT station_provincia_fk
    FOREIGN KEY (provincia_id) REFERENCES public.provincia (id);

COMMIT;
