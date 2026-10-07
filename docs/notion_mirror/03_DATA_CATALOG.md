# 03 · Catálogo de datos

> Campos oficiales: fuente, URL, fecha de extracción, cobertura, campos, licencia/condiciones, transformaciones, hash del snapshot.
> Estado: **v1 congelado y verificado, C-01** (2026-10-07). 187 noticias (50 TVN), 540 WB,
> 82 sismos oficiales 2024 y 87 de extensión. Candidatos ciegos exportados, sin ranking real.
> Evidencia y hash: `docs/worklog/worker-b-c01-verification.json`; auditoría `data/raw/v1/assembly-c01.json`.
> Las tablas de extracción de 2025 debajo son históricas; quedan fuera del corpus C-01.

## Snapshot C-01 · 2026-10-07

- Corte: 2026-10-01T00:00:00Z. Ventana oficial [2025-10-02, 2026-10-01).
- Últimos 30 días: 67 noticias, 2 TVN; se amplió a 90 días: 159 noticias, 22 TVN.
- Corpus total: 187 URL únicas, 50 TVN; RSS admitido en toda C-01 según DL-017.
- DOC parcial: 28 registros; respuestas y fallos 429 en `doc-c01-partial.json`.
- Respaldo GKG: 109 URL únicas, muestreo diario a las 18:00 UTC de 2026-07-03 a 2026-10-01;
  no es cobertura exhaustiva ni implica representatividad. Recibos y reportes GKG conservados.
- RSS: fecha de publicación original, detección nula, extracción separada; sin descripciones en noticias.csv.
- Fuentes, condiciones y limitaciones: `data/raw/v1/fuentes.json`. WB sigue como contexto histórico.
- USGS: oficial 2024 intacto; `eventos_ext.geojson` separado para C-01, misma caja y M≥3 (AP-004).
- Raw antiguo intacto: excluido con `fuera_de_ventana_C-01` en la auditoría. ZIP/RSS solo locales;
  hashes en inventario original y adendas inmutables. Manifest portable verificado sin esos auxiliares.
- `data/labels/editor_candidates.csv`: 187 candidatos sin puntajes, barajados una sola vez; no regenerar.

| Fuente | Archivo | URL | Extracción | Cobertura | Campos | Licencia / condiciones | Transformaciones | SHA-256 |
|---|---|---|---|---|---|---|---|---|
| TVN RSS | noticias.csv (origen=tvn_rss) | https://www.tvn-2.com (feed RSS) | _pendiente_ | Meta: ≥20 registros dentro de [2024-01-01, 2025-10-01) | id_noticia, titulo, url, medio, idioma, fecha_publicacion, fecha_deteccion, fecha_extraccion, tema, origen, alcance_texto, licencia | Titulares y enlaces del patrocinador; el RSS **no** implica licencia abierta sobre artículos, videos o imágenes. Descripciones solo en uso local. | _pendiente_ | _pendiente_ |
| GDELT DOC 2.0 | noticias.csv (origen=gdelt), fuentes.json | https://api.gdeltproject.org/api/v2/doc/doc | _pendiente_ | Meta: 200 únicos (mín. 100); ≤250 por consulta; deduplicado por URL | ídem; `fecha_deteccion` = seendate | La API no transfiere derechos de los medios enlazados. Solo metadatos. | _pendiente_ | _pendiente_ |
| World Bank Indicators v2 | indicadores.csv | https://api.worldbank.org/v2 | _pendiente_ | 6 países (PAN, CRI, COL, DOM, MEX, GTM) × 6 indicadores × 2010–2024 = cuadrícula de 1.350 (con nulos) | pais_iso3, indicador_id, anio, valor (nullable), unidad, fuente_url, fecha_extraccion, licencia | CC BY 4.0 salvo excepciones por indicador (atribución) | _pendiente_ | _pendiente_ |
| USGS FDSN | eventos.geojson | https://earthquake.usgs.gov/fdsnws/event/1/ | _pendiente_ | 2024-01-01..2024-12-31; lat 5–12, lon −86..−76; M≥3; todos los eventos | id, magnitude, time, updated, longitude, latitude, depth, place, status, url | Dominio público (USGS); confirmar elementos de terceros. Solo hechos sísmicos. | _pendiente_ | _pendiente_ |
| Casos sintéticos | data/synthetic/cases.jsonl | — (creados por el equipo) | _pendiente_ | T01, T02, T03, T05, T07 | contrato NewsItem, `sintetico=true` | Propios; marcados `[SINTÉTICO]` | — | _pendiente_ |

## Extracción B-01/B-02 · frictionspp-svg · 2026-10-06

Los objetivos de la tabla anterior no se declaran cumplidos. Evidencia de esta ejecución:
`data/raw/v1/acquisition-20261006T2140.json` (hora interna: 21:38:14 UTC; el nombre del archivo no es el corte).

| Fuente | Resultado medido | Extracción / cobertura | Transformación / SHA-256 |
|---|---|---|---|
| World Bank WDI | 540 filas; 0/540 valores nulos en esta respuesta | Primera serie: 2026-10-06T21:19:24.551363Z. Seis países × seis indicadores × 2010–2024 | Producto cartesiano con nulos explícitos si faltan valores; sin cambiar unidades. `indicadores.csv`: `ddf9c81e78e46828697442193cfc75947f5d8f371e44402f04d18e3b80aa1e8a` |
| USGS | 82 eventos | 2026-10-06T21:19:27.277126Z; año 2024, lat 5..12, lon −86..−76, M≥3 | Límite superior exclusivo; datos GeoJSON originales. `eventos.geojson`: `8cef9ddb521a01e50e08ac8b85dfe400c52a267d3abbdee31d99cfb9be5b6d52` |
| GDELT DOC + respaldo GKG | 300 URL únicas combinadas; 0 TVN en respuestas obtenidas | Septiembre de 2025; DOC parcial por errores 429, GKG muestreado, no exhaustivo | URL normalizada; titulares GKG con entidades HTML decodificadas. Fechas de publicación nulas; detección conservada. Recibos con SHA-256 por respuesta. |
| TVN RSS actual | 152 entradas; 48 dentro del intervalo oficial completo (no incorporadas) | 2026-10-06T21:21:58.100143Z; feed mezcla publicaciones de 2024 a 2026 | [RSS público](https://www.tvn-2.com/rss/). Proyección de titulares y metadatos separada. `tvn_rss_actual.json`: `872c7ee7aa794e1c454c63f26d6a7f64a579931d314036e73e4141e9325ca3b6` |

**Decisiones pendientes:** AP-008 solicita confirmar 540 filas (las dimensiones declaradas no dan 1.350).
AP-009 solicita incorporar las 48 entradas RSS históricas sin alterar publicación, detección ni extracción.
Las entradas actuales fuera del corte quedan excluidas. El adaptador está preparado, pero no aplicado.

**Respaldo GKG:** 76 filas de los archivos descargados no pudieron decodificarse o tenían menos de 27
columnas; se registran por archivo/línea/motivo en el reporte. Los ZIP originales permanecen intactos.
La adquisición GKG descargó unos 910 MB de archivos auxiliares locales; no son cuerpos de artículos.
El cierre del snapshot y su política de empaquetado quedan pendientes de revisión; no se presenta el
directorio parcial como un snapshot distribuible ni como cobertura exhaustiva.

**Indicadores WB:** NY.GDP.MKTP.KD.ZG (crecimiento del PIB, %), FP.CPI.TOTL.ZG (inflación, %), SL.UEM.TOTL.ZS (desempleo, %), SP.POP.TOTL (población), IT.NET.USER.ZS (uso de internet, %), NE.EXP.GNFS.ZS (exportaciones, % PIB).

**Limitaciones conocidas:** solo titular/metadatos; RSS sin histórico; posible desfase temporal USGS 2024 frente a noticias de 2025; la caja USGS ≠ territorio de Panamá; WB = datos anuales históricos (nunca "actuales").
