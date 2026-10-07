# Diccionario del snapshot · B-01 / B-02

Estado: `data/raw/v1` congelado para C-01, corte 2026-10-01T00:00:00Z, con manifest verificado.
AP-008 aceptada (540 filas, DL-013); AP-009 superada por la ventana C-01 (DL-017).
Ejecución guardada: `docs/worklog/worker-b-c01-verification.json`.

## Convenciones

- UTF-8; CSV con encabezado, coma y comillas según CSV estándar.
- El literal CSV `null` representa un valor ausente. El lector debe convertirlo a `None`,
  nunca a `0` ni a una cadena vacía. JSON usa `null`. Un cero observado se conserva como cero.
- Las fechas normalizadas son ISO 8601 UTC con `Z`. Los formatos originales permanecen en respuestas crudas.
- `fecha_publicacion` es la fecha declarada por el medio; `fecha_deteccion` es la observación del agregador
  (nula para RSS); `fecha_extraccion` es la descarga por el equipo. No son intercambiables.
- No se descargan artículos ni archivos de imagen. El RSS contiene descripciones breves y URLs de imágenes
  como parte de su respuesta original; no se incorporan a `noticias.csv` ni a candidatos del editor.
- Los archivos se escriben una sola vez. Repetir una descarga usa sus bytes y recibo existentes,
  comprobando URL y SHA-256. Un contenido distinto exige una versión nueva, nunca sobrescribir raw.
- `data/raw/.gitattributes` desactiva conversiones de fin de línea para conservar SHA-256 al clonar
  desde Windows o Linux.

## noticias.csv

| Campo | Tipo / nulo | Significado y procedencia |
|---|---|---|
| id_noticia | texto, no nulo | `gdt-` + primeros 20 caracteres SHA-256 de URL normalizada en GDELT. Estable entre extracciones. |
| titulo | texto, no nulo | Titular original de DOC o `PAGE_TITLE` de GKG, decodificando entidades HTML. No generado. |
| url | URL HTTP(S), no nulo en fetchers | Esquema y host en minúsculas, fragmento eliminado; se conserva query y ruta. Clave de deduplicación. |
| medio | texto, nullable | Dominio informado; `TVN` para tvn-2.com y sus subdominios. |
| idioma | texto, nullable | DOC: etiqueta original de idioma; GKG: `srclc`, si existe. No inferido. |
| fecha_publicacion | datetime UTC, nullable | Nula para GDELT: seendate no informa publicación. |
| fecha_deteccion | datetime UTC, nullable | DOC `seendate`; GKG campo DATE, instante de procesamiento. |
| fecha_extraccion | datetime UTC, no nulo | Fecha de descarga del recibo de la respuesta, no fecha de ejecución de un reintento desde caché. |
| tema | texto, nullable | Nulo antes del clasificador. La consulta de adquisición no es una etiqueta humana. |
| origen | enum del contrato | `gdelt` para DOC y GKG, incluido TVN si procede de GDELT; `tvn_rss` solo si procede del RSS. |
| alcance_texto | enum | `titular_metadatos`. |
| licencia | texto, nullable | Condiciones de reutilización; GDELT no concede derechos sobre los artículos de terceros. |

El extractor DOC usa los días definidos por `data_window.v1.yaml`: TVN, Canal/logística, turismo, economía y
eventos naturales, con máximo 250 por consulta. No se declara exhaustividad. El respaldo GKG de DL-008
muestrea lotes de quince minutos en horas declaradas, conserva `PAGE_TITLE` y selecciona TVN o titulares
que mencionan Panamá con localización GKG de país `PM`. Ese muestreo no representa el universo de noticias.
Filas GKG con codificación inválida o columnas insuficientes se excluyen con archivo, línea y motivo.

## indicadores.csv

| Campo | Tipo / nulo | Significado |
|---|---|---|
| pais_iso3 | texto | PAN, CRI, COL, DOM, MEX, GTM. |
| indicador_id | texto | Código WDI de la tabla inferior. |
| indicador_nombre | texto, nullable | Nombre devuelto por la API. |
| anio | entero | 2010 a 2024, ambos inclusive. |
| valor | número, nullable | Valor original, sin imputación ni redondeo. Una observación no devuelta también se conserva como nula. |
| unidad | texto | Unidad propia del indicador, sin conversión de escala. |
| fuente_url | URL | Endpoint del indicador y países; parámetros exactos y páginas en el recibo. |
| fecha_extraccion | datetime UTC | Descarga de la respuesta. |
| licencia | texto | WDI: atribución World Bank, CC BY 4.0, sujeto a excepciones declaradas por fuente. |

| Código | Unidad |
|---|---|
| NY.GDP.MKTP.KD.ZG | Crecimiento PIB, % anual |
| FP.CPI.TOTL.ZG | Inflación de precios al consumidor, % anual |
| SL.UEM.TOTL.ZS | Desempleo, % de la población activa total, estimación modelada OIT |
| SP.POP.TOTL | Población total, personas |
| IT.NET.USER.ZS | Uso de internet, % de la población |
| NE.EXP.GNFS.ZS | Exportaciones de bienes y servicios, % del PIB |

La cuadrícula explícita tiene 6 × 6 × 15 = **540 claves únicas**. El objetivo escrito de 1.350 es
incompatible con esas dimensiones: AP-008 solicita corregirlo, sin inventar filas adicionales.

## eventos.geojson

FeatureCollection USGS sin inferencias. Intervalo `[2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z)`,
latitud 5–12, longitud −86 a −76, magnitud ≥3. La caja no equivale al territorio de Panamá.

| Campo de la respuesta | Campo normalizado (B-03) | Unidad / significado |
|---|---|---|
| feature.id | id | Identificador USGS original. |
| properties.mag | magnitude | Magnitud en escala `magType`; puede ser nula. |
| properties.magType | mag_type | Escala original, sin conversión. |
| properties.time | time | Milisegundos Unix UTC → datetime UTC. |
| properties.updated | updated | Milisegundos Unix UTC, actualización del registro. |
| geometry.coordinates[0] | longitude | Grados. |
| geometry.coordinates[1] | latitude | Grados. |
| geometry.coordinates[2] | depth | Kilómetros; conservar incluso valores negativos. |
| properties.place | place | Descripción geográfica original. |
| properties.status | status | Estado USGS original. |
| properties.url | url | Ficha pública USGS. |

La API tiene límite final inclusivo; el adaptador excluye exactamente el instante 2025-01-01.
Si hay más de 20.000 eventos, itera `offset` y detecta IDs duplicados entre páginas.

## Respuestas, fuentes y manifest

- `responses/**`: bytes recibidos. Cada `*.request.json` registra URL completa, instante UTC,
  estado HTTP, tipo de contenido y SHA-256 de la respuesta. No usa autenticación de cuentas.
- `fuentes.json`: origen, URL, licencia/condiciones, cobertura real, limitaciones y desviaciones.
- `manifest.json`: versión, corte, congelación, consultas, fuentes, transformaciones y mapa `archivos`
  con SHA-256, bytes y cantidad (cuando se puede contar). El manifest no se incluye en su propio hash.
- `verify_manifest(dir)` detecta cambios, archivos ausentes y archivos inesperados del paquete portable. No requiere red.
- `responses/gkg/*.zip` y `responses/tvn-current/rss.xml` son auxiliares **solo locales**:
  no se suben a Git ni aparecen en `manifest.archivos`. Sus SHA-256 y tamaños permanecen en
  `acquisition_inventory.json`, con `disponibilidad: "solo local"`. El inventario sí está cubierto
  por el manifest; una copia sin los auxiliares verifica igual que la máquina de adquisición.
  Antes de congelar se comprueban los hashes locales contra el inventario existente; nunca se
  reescribe automáticamente un inventario o manifest previo. Nuevas adquisiciones añaden
  `acquisition_inventory.c01-<UTC>.json`; los hashes repetidos deben coincidir. El corte se lee de `data_window.v1.yaml`.
- `tvn_rss_actual.json`: proyección de metadatos del feed obtenido en 2026; separado del corpus.
- `data/labels/editor_candidates.csv`: orden aleatorio sin puntajes ni temas predichos; conserva columnas
  separadas para publicación y detección. No sustituir la selección humana del top 5.

## Comandos reproducibles

```powershell
python -m scayl.ingest.fetch_worldbank --output data/raw/v1
python -m scayl.ingest.fetch_usgs --output data/raw/v1
python -m scayl.ingest.fetch_tvn --url https://www.tvn-2.com/rss/ --output data/raw/v1
python -m scayl.ingest.acquire_c01 --output data/raw/v1
# Solo como respaldo documentado de DL-008:
python -m scayl.ingest.acquire_gkg_c01 --output data/raw/v1 --extended
python -m scayl.ingest.fetch_usgs --output data/raw/v1 --extension
python -m scayl.ingest.assemble_c01 data/raw/v1
# Tras resolver cobertura, registrar fuentes y congelar:
python -m scayl.ingest.manifest data/raw/v1
python -m scayl.ingest.manifest data/raw/v1 --verify
python -m scayl.ingest.editor_candidates --snapshot data/raw/v1
```

`python -m pytest -q` verifica transformaciones y manipulación de bytes sin consultar fuentes en vivo.
La carga normalizada y su reporte T01 corresponden a B-03; no se declaran implementados en B-01/B-02.
