# Fuentes de registros meteorológicos

Catálogo inicial para MeteoAndalucía. Revisión: **30 de octubre de 2026**.
El ámbito principal es Andalucía; los archivos nacionales e internacionales se
incluyen como posibles accesos complementarios a observaciones de la región.
Es un catálogo ampliable, no una relación exhaustiva de todas las estaciones.

«Integrada» significa que existe código en este repositorio. «Documentado» indica
que el publicador describe el acceso; no implica haber probado una descarga.
«Pendiente» significa que falta comprobar el acceso, formato o cobertura.

## Redes y portales públicos

| Fuente | Registros de interés | Acceso conocido | Estado en el proyecto |
| --- | --- | --- | --- |
| [AEMET OpenData](https://opendata.aemet.es/dist/) | Inventario y observaciones climatológicas diarias; otras variables según producto y estación. | API REST, con API key. [Información oficial](https://www.aemet.es/es/datos_abiertos/AEMET_OpenData). | Integrada: estaciones, medidas y descarga a CSV. |
| [RIA / RIAweb — IFAPA](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/inicio_estaciones) | Estaciones agroclimáticas: temperatura, humedad, viento, radiación, precipitación y ET0 según disponibilidad. | Web y servicio JSON usado por los clientes actuales. [Presentación oficial de las redes](https://www.juntadeandalucia.es/organismos/agriculturapescaaguaydesarrollorural/servicios/sia/red-estaciones-agrometeorologicas.html). | Integrada. Revisar disponibilidad por estación y variable; ET0 da errores en algunos históricos. |
| [SiAR — MAPA](https://servicio.mapa.gob.es/siarweb/) | Observaciones agroclimáticas de la red SiAR. | Consulta web, CSV y API documentados. [Manual web](https://servicio.mapa.gob.es/siarweb/documentos/manuales/ManualUsoWebSiAR.pdf), [manual de API](https://servicio.mapa.gob.es/siarweb/documentos/manuales/ManualTecnico_WEB_API_SIAR.pdf). | Pendiente de integrar; comprobar requisitos de acceso de la API y solapamiento con RIA. |
| [RAIF — datos climáticos](https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif-clima) | Datos de estaciones agroclimáticas para información fitosanitaria. El catálogo anuncia datos desde 2002. | Conjunto de datos abiertos con recursos descargables y fichero de identificación de estaciones. | Pendiente de inspeccionar recursos, formatos y solapamiento con otras redes agrarias. |
| [CLIMA / REDIAM](https://www.juntadeandalucia.es/medioambiente/portal/acceso-rediam/teledeteccion-y-caracterizacion-territorio/redes-de-medicion-en-tiempo-real/subsistema-clima) | Integración de registros de estaciones de diferentes organismos en Andalucía. | Portal y consultas del subsistema. [Catálogo de estaciones](https://www.juntadeandalucia.es/datosabiertos/portal/dataset/estaciones-meteorologicas-integradas-en-el-subsistema-de-informacion-de-climatologia-ambiental-clim). | Pendiente de verificar descarga de series. El inventario geográfico de estaciones no equivale a sus medidas históricas. |
| [SAIH Guadalquivir — CHG](https://www.chguadalquivir.es/saih/DatosHistoricos.aspx) | Precipitación y temperatura, además de variables hidrológicas. | El formulario documenta salida Excel e informes por bloques: horario 7 días, diario 170 días y mensual 14 años. | Pendiente. No se ha localizado una API pública documentada ni el repositorio CSV recordado por el usuario. Mantener abierta esa investigación. |
| [SAIH Hidrosur](https://www.redhidrosurmedioambiente.es/saih/) | Red hidrometeorológica de las cuencas andaluzas; consultar variables y estaciones concretas. | Visor público. [Directorio REDIAM de redes](https://www.juntadeandalucia.es/medioambiente/portal/acceso-rediam/redes-de-medicion-en-tiempo-real). | Pendiente de verificar catálogo, históricos y exportación; no dar por confirmada una API o salida CSV. |
| [SAIH Guadiana — datos meteorológicos](https://www.chguadiana.es/cuenca-hidrografica/hidrologia/aguas-superficiales/meteorologia) | Datos meteorológicos de su demarcación, de interés para estudiar cobertura del ámbito onubense. | La Confederación enlaza redes para consulta y descarga. | Pendiente de confirmar estaciones concretas en Andalucía, históricos y formatos. |
| [ICTS Doñana / EBD-CSIC — datos automáticos](https://datos-automaticos.icts-donana.es/es/raw/) | Series hidrometeorológicas de Doñana. El portal anuncia series desde 2020. | Descarga del filtro activo por estación, variable y fechas; datos brutos sin control automático de calidad. | Pendiente de probar descarga y formato. La consulta directa agotó el tiempo de espera durante esta revisión. |
| [ICTS Doñana — estación manual Palacio](https://meteorologia-palacio.icts-donana.es/es/meteopalacio_info/) | Registros de la estación meteorológica manual del Palacio de Doñana. | Portal público específico. | Pendiente de verificar variables, periodo, descarga e identidad respecto de otros catálogos. |

## Redes colaborativas y archivos de observaciones

| Fuente | Qué aporta | Acceso y pendientes |
| --- | --- | --- |
| [Meteoclimatic](https://www.meteoclimatic.net/) | Observaciones de una red colaborativa de estaciones. | Web pública. Localizar estaciones andaluzas y comprobar histórico, descarga y condiciones de reutilización. |
| [Ogimet](https://www.ogimet.com/getsynop_help.phtml) | Archivo de mensajes SYNOP; posible complemento para estaciones sinópticas. | Consulta parametrizada documentada. Verificar cobertura, límites y decodificación antes de integrar. |
| [NOAA NCEI — Global Hourly / ISD](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database) | Archivo internacional de observaciones horarias y sinópticas de múltiples fuentes. | [Buscador y acceso](https://www.ncei.noaa.gov/access/search/datasets/global-hourly/). Verificar estaciones españolas, identificadores y cobertura temporal. |
| [Meteostat](https://dev.meteostat.net/data.html) | Archivo agregado de observaciones históricas. | Documenta series por estación en CSV y descargas masivas en Parquet. [Series](https://dev.meteostat.net/data/timeseries). Comprobar procedencia y tratamientos de cada producto antes de usarlo como observación original. |

## Criterios para ampliar el catálogo

- Registrar organismo, URL, red original e identificadores de estación.
- Comprobar provincia, coordenadas, altitud, variables, unidades y periodo disponible.
- Registrar frecuencia, zona horaria, significado de acumulados y marcas de ausencia.
- Distinguir observaciones brutas, validadas, agregadas y valores estimados.
- Anotar API o formato, autenticación, límites, licencia y fecha de comprobación.
- Conservar la procedencia: dos portales pueden publicar la misma estación.
- Comprobar una descarga pequeña antes de marcar una fuente como integrable.

Los reanálisis, predicciones y productos de rejilla pueden catalogarse aparte:
no equivalen a registros originales de estaciones.

## Próximos pasos

1. Inspeccionar SiAR y RAIF, especialmente sus recursos descargables y estaciones compartidas con RIA.
2. Investigar los históricos de Hidrosur y el acceso CSV pendiente del Guadalquivir.
3. Probar las descargas de Doñana y las consultas de CLIMA.
4. Ampliar con redes universitarias, municipales y asociaciones locales, verificando cada acceso.

Para futuras integraciones se mantiene la convención `download_<fuente>_stations.py`,
`download_<fuente>_daily_csv.py` e `import_<fuente>_stations.py`, según la operación.
