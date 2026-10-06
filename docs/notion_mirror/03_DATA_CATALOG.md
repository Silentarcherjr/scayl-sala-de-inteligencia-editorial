# 03 · Catálogo de datos

> Campos oficiales: fuente, URL, fecha de extracción, cobertura, campos, licencia/condiciones, transformaciones, hash del snapshot.
> Estado: **snapshot aún no disponible** (B-01). Los valores marcados _pendiente_ se completan desde `manifest.json`.

| Fuente | Archivo | URL | Extracción | Cobertura | Campos | Licencia / condiciones | Transformaciones | SHA-256 |
|---|---|---|---|---|---|---|---|---|
| TVN RSS | noticias.csv (origen=tvn_rss) | https://www.tvn-2.com (feed RSS) | _pendiente_ | Meta: ≥20 registros dentro de [2024-01-01, 2025-10-01) | id_noticia, titulo, url, medio, idioma, fecha_publicacion, fecha_deteccion, fecha_extraccion, tema, origen, alcance_texto, licencia | Titulares y enlaces del patrocinador; el RSS **no** implica licencia abierta sobre artículos, videos o imágenes. Descripciones solo en uso local. | _pendiente_ | _pendiente_ |
| GDELT DOC 2.0 | noticias.csv (origen=gdelt), fuentes.json | https://api.gdeltproject.org/api/v2/doc/doc | _pendiente_ | Meta: 200 únicos (mín. 100); ≤250 por consulta; deduplicado por URL | ídem; `fecha_deteccion` = seendate | La API no transfiere derechos de los medios enlazados. Solo metadatos. | _pendiente_ | _pendiente_ |
| World Bank Indicators v2 | indicadores.csv | https://api.worldbank.org/v2 | _pendiente_ | 6 países (PAN, CRI, COL, DOM, MEX, GTM) × 6 indicadores × 2010–2024 = cuadrícula de 1.350 (con nulos) | pais_iso3, indicador_id, anio, valor (nullable), unidad, fuente_url, fecha_extraccion, licencia | CC BY 4.0 salvo excepciones por indicador (atribución) | _pendiente_ | _pendiente_ |
| USGS FDSN | eventos.geojson | https://earthquake.usgs.gov/fdsnws/event/1/ | _pendiente_ | 2024-01-01..2024-12-31; lat 5–12, lon −86..−76; M≥3; todos los eventos | id, magnitude, time, updated, longitude, latitude, depth, place, status, url | Dominio público (USGS); confirmar elementos de terceros. Solo hechos sísmicos. | _pendiente_ | _pendiente_ |
| Casos sintéticos | data/synthetic/cases.jsonl | — (creados por el equipo) | _pendiente_ | T01, T02, T03, T05, T07 | contrato NewsItem, `sintetico=true` | Propios; marcados `[SINTÉTICO]` | — | _pendiente_ |

**Indicadores WB:** NY.GDP.MKTP.KD.ZG (crecimiento del PIB, %), FP.CPI.TOTL.ZG (inflación, %), SL.UEM.TOTL.ZS (desempleo, %), SP.POP.TOTL (población), IT.NET.USER.ZS (uso de internet, %), NE.EXP.GNFS.ZS (exportaciones, % PIB).

**Limitaciones conocidas:** solo titular/metadatos; RSS sin histórico; posible desfase temporal USGS 2024 frente a noticias de 2025; la caja USGS ≠ territorio de Panamá; WB = datos anuales históricos (nunca "actuales").
