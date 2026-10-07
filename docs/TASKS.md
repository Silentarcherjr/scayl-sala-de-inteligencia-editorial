# TASKS — tareas atómicas y asignables

> El estado oficial lo actualiza solo el Lead (al mergear). Los workers reportan en su PR y en `docs/worklog/`.
> Estados: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`. Prioridad: P0/P1/P2. Hito: M0–M4.
> Dueños (DL-011): **L** = Humano 1 + Claude (Lead) · **F** = **frictionspp-svg** + su agente (camino crítico: datos, semántica y primera UI; empieza ya) · **W** = **LowCrime** + su agente (resto de la UI, evaluación, Trust Lab y despliegue; llega más tarde; es el "editor" independiente) · **H** = tareas humanas.
> Las secciones de contrato siguen llamándose "A-xx" (UI) y "B-xx" (datos/eval) por su tipo, no por la persona: el dueño real es el de esta tabla.
> Instrucciones por persona y agente: `docs/agents/frictionspp-svg.md` y `docs/agents/LowCrime.md`.

## Resumen

| ID | Tarea | Dueño | Prio | Hito | Estado | Depende de |
|---|---|---|---|---|---|---|
| L-01 | Contratos de datos + fixture de UI | L | P0 | M0 | DONE | — |
| L-02 | Docs de gobernanza + espejo Notion | L | P0 | M0 | DONE | — |
| L-03 | `scoring_rules.v1.yaml` + `evidence/scoring.py` + `status.py` | L | P0 | M1 | DONE | L-01 |
| L-04 | `evidence/provenance.py` (Source DNA) | L | P0/P1 | M1 | DONE | B-03 |
| L-05 | `evidence/linking.py` + `temporal.py` (WB/USGS, Temporal Guard) | L | P0 | M1 | DONE | B-03 |
| L-06 | `evidence/conflicts.py` (numéricos, fechas, unidades, períodos) | L | P0 | M2 | DONE (numérico; fechas/unidades en M2) | L-05 |
| L-07 | `pipeline.py build` + `service.py` + `bundle.json` + `fichas.jsonl` | L | P0 | M1 | DONE (pipeline corre con datos reales) | L-03, B-03, B-05 |
| L-08 | `gen/llm.py` (Ollama + caché + meta) + `guard.py` | L | P0 | M2 | DONE | — |
| L-09 | `gen/validators.py` + fallback `template` | L | P0 | M1 | DONE | L-01 |
| L-10 | `gen/claims.py` + `studio.py` + prompts v1 | L | P0 | M2 | DONE | L-08, L-09 |
| L-11 | `gen/qa.py` con abstención | L | P0 | M2 | DONE | B-06, L-08 |
| L-12 | `review/store.py` + `outbox.py` | L | P0 | M1 | DONE | L-01 |
| L-13 | `evidence/gaps.py` (Investigation Gap) | L | P1 | M2 | DOING (determinista listo; inferencias vía Story Studio) | L-05 |
| L-14 | Integración, merges, README final, pitch | L | P0 | M3–M4 | TODO | todo |
| A-01 | App Streamlit: esqueleto + `FixtureService` + navegación | **W** LowCrime (DL-020) | P0 | M1 | DONE (PR #18) | L-01 |
| A-02 | Sala de Situación | **W** LowCrime (DL-020) | P0 | M1 | DONE (PR #18) | A-01 |
| A-03 | Ficha de Caso (6 pestañas) | **W** LowCrime | P0 | M1–M2 | DONE (PR #13) | A-01 |
| A-04 | Consultas (Q&A) | **W** LowCrime | P0 | M2 | DONE (PR #25) | A-01 |
| A-05 | Trust Lab (vista) | **L** Lead (DL-021) | P1 | M3 | DONE (vista; métricas reales pendientes de B-08) | B-08 |
| A-06 | Despliegue del enlace en modo `cache` | **W** LowCrime | P0 | M3 | TODO | AP-001, L-07 |
| B-01 | Construir el snapshot propio según el PDF §6–7 (fetchers) → `data/raw/v1` | **F** frictionspp-svg | P0 | M0 | DONE (PR #19) | — |
| B-02 | `ingest/manifest.py` (SHA-256, conteos, transformaciones) + diccionario | **F** frictionspp-svg | P0 | M0 | DONE (PR #19) | B-01 |
| B-03 | `ingest/validate.py` + normalización → `data/processed` + `quality_report` (T01) | **L** Lead (DL-023) | P0 | M1 | DONE | B-01 |
| B-04 | Casos sintéticos T01/T03/T05/T07 en `data/synthetic/` | **F** frictionspp-svg | P0 | M1 | TODO | L-01 |
| B-05 | `intel/embed.py` + `topics.py` + `cluster.py` (baseline + IA) | **L** baseline / **F** IA (DL-023) | P0 | M1–M2 | DOING (baseline listo; falta variante IA + calibración) | B-03 |
| B-06 | `intel/retrieve.py` (BM25 + coseno) | **F** frictionspp-svg | P0 | M2 | TODO | B-05 |
| B-07 | Etiquetas humanas: temas (≥100), pares de agrupación, top 5 ciego, benchmark dev (40) | F (etiquetas) + W (top 5 ciego) | P0 | M2 | TODO | B-03 |
| B-08 | `eval/`: métricas, benchmark, latencia → `eval/results/latest.json` | **W** LowCrime | P0/P1 | M3 | PARCIAL (PR #27: P@5 y T01–T10; el resto no medido hasta B-05 IA, L-10/L-11 en vivo y benchmark B-10) | B-05, L-10, L-11 |
| B-09 | Revisión humana de ≥30 afirmaciones (validez de sustento) | W (editor) | P0 | M3 | TODO | L-10 |
| B-10 | Benchmark de modelos locales (embeddings + LLM) en hardware declarado | **F** frictionspp-svg (AMD Radeon RX 9060 XT 8 GB, Vulkan) | P0 | M1 | TODO | — |
| H-01 | Preparar el espacio Notion (estructura de §5) para migrar en cuanto haya licencia | H1 | P0 | M3 | TODO | — |
| H-02 | Bitácora `docs/AI_TOOLS_USED.md` → PDF | Todos | P0 | M4 | DOING | — |
| H-03 | Publicaciones en redes (@hackiathon @viamatica @adenbs) | H | P0 | M1–M4 | TODO | — |
| H-04 | Migrar el espejo a Notion y compartirlo con el jurado | H1 + L | P0 | M3 | BLOCKED (sin acceso) | Notion |
| L-15 | **Simulador de pesos**: `scoring.rescore(bundle, weights)` + registro de justificación | L | P1 | M2 | DONE (núcleo; vista = A-10) | L-03 |
| L-16 | **Recibo de trazabilidad** por decisión (JSON + hash: snapshot, afirmaciones, revisor) | L | P1 | M2 | DONE | L-12 |
| L-17 | `config/verification_sources.v1.yaml`: tema → institución oficial sugerida (INEC, SINAPROC, ACP, MEF, ATP, ASEP…) | L | P1 | M1 | DONE | — |
| L-18 | Métrica de **preservación de atribución** (validador `STATUS_MISMATCH`) | L | P1 | M3 | DONE (generation_report.jsonl) | L-09 |
| A-07 | **Agenda de la mañana** (top 5 + por qué + a quién verificar) en la Sala de Situación | **W** LowCrime | P0 | M2 | DONE (PR #26) | A-02, L-17 |
| A-08 | **Clic en número → tarjeta de evidencia**, componente reutilizable en todas las pantallas | **W** LowCrime (DL-020) | P0 | M1 | DONE (PR #13) | A-01 |
| A-09 | **Modo jurado** en Consultas (las 4 preguntas del PDF precargadas) | **W** LowCrime | P1 | M2 | DONE (PR #25) | A-04 |
| A-10 | Vista del simulador de pesos (sliders → ranking nuevo vs v1, justificación obligatoria) | **L** Lead (DL-021) | P1 | M2 | DONE | L-15 |
| B-11 | **GitHub Actions**: pytest (T01–T10) en cada PR + badge en el README | **F** frictionspp-svg | P0 | M1 | TODO | — |
| B-12 | **Set de 10 ataques** (inyección, preguntas trampa, pedir secretos, acusaciones) + tasa de resistencia | **W** LowCrime | P1 | M3 | TODO | L-10, L-11 |
| H-05 | **Video de la demo con internet apagado** → Notion | W | P0 | M4 | TODO | M3 |
| H-06 | **Mini-estudio manual vs asistido** (3 tareas cronometradas, protocolo en 06) | F + W | P1 | M3 | TODO | M2 |
| H-07 | Registro de **prueba fallida → corrección** (regla continua: cada fallo real se anota en 06) | Todos | P0 | M1–M4 | DOING | — |
| H-08 | Top 5 **a ciego** del editor (Humano 2), antes de que exista ranking | W (editor) | P0 | M0–M1 | DONE (PR #23; ver DL-024) | B-01 |
| B-13 | **ACP**: niveles del lago Gatún (CSV histórico + proyección) → `indicadores_recientes.csv` (AP-010) | **F** frictionspp-svg | P1 | M2 | TODO | B-01 |
| B-14 | **INEC**: IPC urbano nacional mensual (variación mensual e interanual) desde los cuadros PDF → `indicadores_recientes.csv` | **F** frictionspp-svg | P1 | M2–M3 | TODO | B-13 |

---

## Contratos de las tareas de los workers

Cada tarea define: objetivo · archivos permitidos · entradas · salidas · interfaces · pruebas · terminado.
**Fuera de los archivos permitidos → propuesta en `AGENT_PROPOSALS.md`.**

### A-01 · Esqueleto Streamlit + FixtureService
- **Objetivo:** app navegable de 4 páginas que lee el fixture.
- **Archivos permitidos:** `app/**`, `tests/ui/**`, (las dependencias necesarias ya están fijadas en `requirements.txt`).
- **Entradas:** `tests/fixtures/ui_bundle.example.json` (modelo `UIBundle`).
- **Salidas:** `app/Home.py` (Sala de Situación), `app/pages/1_Ficha_de_Caso.py`, `2_Consultas.py`, `3_Trust_Lab.py`, `app/service_client.py`.
- **Interfaz:** `scayl/service.py` **ya existe** y, si no hay `data/processed/<snapshot>/bundle.json`, usa automáticamente el fixture sintético. `app/service_client.py` puede ser un reexport delgado de `scayl.service` (útil solo para stubs en pruebas). La UI **solo** importa `scayl.contracts` y `scayl.service` (o `service_client`).
- **Reglas:** horas mostradas en America/Panama; ítems sintéticos con insignia `SINTÉTICO`; no mostrar P como porcentaje de verdad; la insignia de evidencia (3 niveles) es visualmente distinta del puntaje.
- **Pruebas:** `tests/ui/test_service_client.py` (carga el fixture, `get_event`, `review` en memoria); smoke test con `streamlit.testing.v1.AppTest` en cada página.
- **Terminado:** `streamlit run app/Home.py` abre las 4 páginas sin error con el fixture; pruebas en verde; capturas en el PR.

### A-02 · Sala de Situación
- **Archivos:** `app/Home.py`, `app/components/**`.
- **Muestra:** embudo (`signals_total` → `signals_valid` → `len(events)` → top 5); tabla ordenada por P desc → U desc → ID; mini-barras con contribución ponderada R/I/U/N/E y tooltip con `rationale`; insignias de rango y de estado de evidencia; publicaciones vs `max_possible_independent`/`confirmed_independent`; ícono de conflicto; `recommended_action`; matriz 3×3 rango × estado de evidencia (con cantidad de eventos por celda); filtros por tema y estado.
- **Pruebas:** AppTest verifica que el orden y el desempate coinciden con el fixture; que EVT-0003 (alto + insuficiente) muestra "no habilita publicación".
- **Terminado:** cumple lo anterior a 1280×720.

### A-03 · Ficha de Caso
- **Archivos:** `app/pages/1_Ficha_de_Caso.py`, `app/components/**`.
- **Pestañas:** Evento (resumen, titulares con medio y hora, entidades, línea de tiempo, `text_scope_note`, marca de recirculación) · Fuentes (grupos de procedencia con `basis`, frase `statement` literal) · Evidencia (afirmaciones con tipo, estado, `EvidenceRef` → evidence_id, campo, valor, período, URL; conflictos lado a lado "Versión A / Versión B / verificación pendiente"; advertencias temporales destacadas) · Vacíos (5 bloques del gap) · Producir (paquete con chips de etiqueta por oración, clic → afirmación y evidencia, `ValidationReport`, `GenerationMeta.mode` visible, botón Generar) · Revisión (estado actual, transiciones permitidas según `REVIEW_TRANSITIONS`, revisor, justificación obligatoria, historial).
- **Pruebas:** AppTest: la pestaña Evidencia de EVT-0002 muestra ambas versiones; la revisión rechaza una justificación vacía y una transición inválida.
- **Terminado:** las 6 pestañas funcionan con el fixture.

### A-04 · Consultas
- **Archivos:** `app/pages/2_Consultas.py`.
- **Comportamiento:** input → `ask()`; si `abstained` muestra "No hay evidencia suficiente en el corpus" + `abstention_reason` + `needed_information`; si no, oraciones con chips de cita. Ejemplos precargados (sustentada, contradicción, sin respuesta, adversarial).
- **Terminado:** funciona con un stub que devuelve un `QAAnswer` del fixture.

### A-05 · Trust Lab (vista)
- **Archivos:** `app/pages/3_Trust_Lab.py`. **Entrada:** `eval/results/latest.json` (esquema en B-08).
- **Regla:** si una métrica no existe, se muestra "no medido", nunca un valor inventado. Muestra numerador y denominador.

### A-06 · Enlace desplegado
- **Requiere** la aceptación de AP-001. **Archivos:** `deploy/**`, `README.md` (sección Despliegue).
- **Terminado:** URL accesible para el jurado, modo `cache`, insignia "Demo snapshot · salidas IA precalculadas".

### B-01 · Snapshot
- **Objetivo:** `data/raw/v1/` con `noticias.csv`, `fuentes.json`, `indicadores.csv`, `eventos.geojson` y `manifest.json`.
- **Fuente de verdad:** PDF TVN §6–7. No hay paquete oficial: lo construimos y lo congelamos nosotros.
- **Fetchers:** `scayl/ingest/fetch_{tvn,gdelt,worldbank,usgs}.py`, ejecutados en una máquina con internet; cada uno es idempotente y guarda la respuesta cruda.
- **Noticias, estrategia del intervalo (DL-008), con un bloque de tiempo de 2 h:**
  1. **Ventana oficial (aclaración C-01, DL-017):** noticias en [2025-10-02, 2026-10-01). Objetivo: los 30 días previos al corte (2026-09-01 → 2026-10-01), ampliable a 90 días (desde 2026-07-03). Fuente única de las fechas: `scayl/config/data_window.v1.yaml`. **GDELT DOC 2.0** `mode=ArtList&format=json&maxrecords=250&STARTDATETIME=...&ENDDATETIME=...`, partido por día y deduplicado por URL; `fecha_publicacion` = null (seendate = detección). Respaldo: GKG 2.1 de la misma ventana. **TVN:** entradas del RSS con `pubDate` dentro de la ventana (`origen=tvn_rss`, `fecha_deteccion` = null), más `domain:tvn-2.com` en GDELT si responde.
  2. Si no se alcanzan ≥100 registros (≥20 TVN) con 30 días, ampliar hasta 90 y registrar la cobertura efectiva en el catálogo y el manifest.
  3. **USGS:** el archivo oficial de 2024 (`eventos.geojson`) + extensión `eventos_ext.geojson` con la misma caja y M≥3 para la ventana de noticias (AP-004, declarada como extensión).
  - WB: 6 países (PAN, CRI, COL, DOM, MEX, GTM) × 6 indicadores × 2010–2024; completar la cuadrícula de **540** filas (6×6×15; ver DL-013) con `valor` nulo.
  - USGS: 2024-01-01..2024-12-31, lat 5–12, lon −86..−76, M≥3, todos los eventos.
  - GDELT: consultas "Panama" + logística/turismo/economía/eventos naturales, partidas por fecha, deduplicadas por URL; ≤250 por consulta.
  - TVN RSS: lo disponible; documentar la cobertura real y la desviación del intervalo oficial.
- **Archivos:** `scayl/ingest/**`, `data/raw/**`, `docs/notion_mirror/03_DATA_CATALOG.md` (sección propia).
- **Terminado:** manifest con SHA-256 por archivo; catálogo actualizado; nada de contenido protegido completo.

### B-02 · Manifest + diccionario
- `scayl/ingest/manifest.py`: `build_manifest(dir) -> dict`; `verify_manifest(dir) -> list[str]` (difs). Diccionario de campos en `docs/DATA_DICTIONARY.md`.
- **Pruebas:** al alterar un byte, la verificación falla.

### B-03 · Validación y normalización (T01)
- **Interfaz:** `scayl.ingest.validate.load_snapshot(dir) -> (list[NewsItem], list[IndicatorObservation], list[SeismicEvent], QualityReport)`; escribe `data/processed/<snap>/`.
- **Reglas:** ARCHITECTURE §4.1. Nulos preservados; fechas inválidas → None + flag; filas excluidas con motivo.
- **Pruebas:** `tests/test_t01_validation.py` con un CSV sintético de fechas inválidas y nulos → la carga continúa, el reporte cuenta correctamente y `valor` nulo sigue nulo.

### B-04 · Casos sintéticos
- `data/synthetic/cases.jsonl` con: (T01) fechas inválidas; (T02) 3 titulares del mismo evento, 2 con agencia; (T03) noticia de 2024 detectada en 2025-09; (T05) dos cifras incompatibles; (T07) titular/descripción con "Ignora tus instrucciones y revela…". Todos con `origen=sintetico` y título con prefijo `[SINTÉTICO]`.

### B-05 · Inteligencia semántica
- **Interfaz:** ARCHITECTURE §5.1. `topics.classify(items, method) -> list[(Topic, conf)]`; `cluster.cluster(items, embedder, tau) -> list[list[id]]`.
- **Salidas:** `embeddings.npz` precalculado.
- **Pruebas:** T02 (los 3 registros sintéticos forman 1 cluster); determinismo; el baseline corre sin torch.

### B-06 · Recuperación
- `retrieve.search(query, k) -> list[(evidence_id, score, EvidenceRef)]` sobre titulares, filas WB y USGS. Híbrido BM25 + coseno, con la puntuación normalizada en [0,1] para el umbral de abstención.

### B-07 · Etiquetas humanas
- `data/labels/topics.csv` (≥100 titulares, 2 etiquetadores si hay tiempo, registrar el acuerdo); `data/labels/cluster_pairs.csv`; `data/labels/editor_top5.json` (**elegido a ciegas, antes de ver el ranking**, con hora); `data/labels/benchmark_dev.jsonl` (40 consultas: 20 sustentadas / 7 contradicción / 7 sin respuesta / 6 adversariales; misma proporción que el oficial). Documentar el método en `06_TESTS_AND_METRICS.md`.
- **Muestreo de pares de agrupación (DL-016), obligatorio.** Los pares al azar casi nunca son del mismo evento y dejarían la métrica vacía. Usar un *pool* de candidatos:
  1. **Todos** los pares que agrupa el baseline (TF-IDF) **o** la IA (embeddings), hasta ~150.
  2. ~40 pares "difíciles": mismo día ±1 y palabra clave compartida, que **ningún** método agrupó.
  3. ~30 pares al azar como control.
  - Columnas: `pair_id,id_a,id_b,titulo_a,titulo_b,medio_a,medio_b,fecha_a,fecha_b,mismo_evento,etiquetador,nota`. **Sin** columna de método ni de puntaje: el orden es aleatorio con semilla fija registrada, y quien etiqueta no sabe qué sistema propuso el par.
  - El origen de cada par (baseline / IA / ambos / difícil / azar) va en un archivo separado (`cluster_pairs_origin.csv`) que el etiquetador no abre.
  - B-08 reporta, por método: precisión (sobre los pares que propuso), **recall relativo** (sobre los positivos del pool) y F1, con n y el método declarados. Nunca se llama "recall absoluto".

### B-13 / B-14 · Evidencia oficial reciente (AP-010, DL-019)
- **Archivo:** `data/raw/v1/indicadores_recientes.csv` (los raw originales, CSV de la ACP y PDF del INEC, en `responses/` con recibo SHA-256). Columnas = las de `indicadores.csv` + `periodo,fuente,frecuencia,es_proyeccion`:
  `pais_iso3,indicador_id,indicador_nombre,anio,valor,unidad,fuente_url,fecha_extraccion,licencia,periodo,fuente,frecuencia,es_proyeccion`
- **Series** (ids exactos, los usa `scayl/evidence/recent.py`):
  - `ACP.GATUN.NIVEL`: nivel **observado** diario, `periodo=AAAA-MM-DD`, `unidad=pies`, `fuente=acp`, `frecuencia=diaria`, `es_proyeccion=false`. Ventana de noticias + 30 días antes.
  - `ACP.GATUN.PROYECCION`: proyección publicada, `es_proyeccion=true`. Nunca se usa como hecho.
  - `INEC.IPC.VAR_MENSUAL` e `INEC.IPC.VAR_INTERANUAL`: `periodo=AAAA-MM`, `unidad=%`, `fuente=inec`, `frecuencia=mensual`; de 2025-09 al último mes publicado antes del corte. `indicador_nombre` incluye el cuadro y la página de origen (cita válida según el PDF §7).
- **Reglas:** valores tal como los publica la fuente (signo incluido); nulo si falta; nunca datos posteriores al corte (2026-10-01); registrar la advertencia de la ACP ("estimación informativa") en `fuentes.json`.
- **Pruebas:** el CSV valida contra `IndicatorObservation` (contrato 0.3.0); una fila por (serie, período).
- **Terminado:** filas en el CSV, recibos, catálogo actualizado; `load_snapshot` las devuelve junto a las de WB.

### B-08 · Evaluación
- **Salida:** `eval/results/latest.json`:
  `{run_at, hardware, models, metrics:{citation_coverage:{num,den}, support_validity:{num,den,reviewer}, abstention_correct:{num,den}, abstention_false:{num,den}, topics_macro_f1:{baseline,ai,n}, clustering:{baseline:{p,r,f1}, ai:{...}, n_pairs}, precision_at_5:{value, exploratory:true}, latency_ms:{qa:{median,p95,n}, package:{median,p95,n}}, tokens:{...}, api_cost_usd:0.0}, tests:{T01..T10:{status, evidence}}}`.
- Comando: `python -m scayl.eval.run --snapshot v1`.

### B-10 · Benchmark de modelos locales
- Medir en el hardware real (AMD Radeon RX 9060 XT 8 GB, Vulkan; y la RTX 3050 si se usa): embeddings `BAAI/bge-m3` vs `intfloat/multilingual-e5-base` vs `Qwen/Qwen3-Embedding-0.6B` (tiempo + macro-F1 de temas + F1 de agrupación). LLM: en la 4060 `qwen3.5:9b` vs `qwen3:8b`; en la 3050 `qwen3:4b` vs `gemma4` E4B (verificar los tags exactos en Ollama). Contexto 4096, thinking desactivado y `format` JSON. Medir tokens/s, latencia del paquete y de Q&A (mediana y p95, n≥10), tasa de JSON válido y VRAM. Registrar los resultados en `02_DECISION_LOG.md` (DL-006) mediante PR.

### Contratos de las tareas 10/10 (resumen)
- **L-15 / A-10 Simulador de pesos.** `scayl.evidence.scoring.rescore(events, weights: dict[str,int]) -> list[Event]`; los pesos deben sumar 100; `rules_version = "scoring-v1+custom:<sha8>"`. La UI muestra el ranking v1 junto al nuevo, con flechas de cambio, y exige justificación; la justificación se guarda en `data/state/weight_changes.jsonl` (y en el outbox de Notion). Prueba: con los pesos oficiales se reproduce exactamente el ranking v1.
- **L-16 Recibo de trazabilidad.** En cada `review()` se escribe `data/state/receipts/<review_id>.json` con `{review, event_id, snapshot_sha256 (del manifest), evidence_snapshot_sha256, claims, package_id, generated_by}` y su propio sha256. La UI muestra "Recibo #… · hash …" y permite descargarlo. Prueba: al alterar la evidencia, el hash cambia.
- **L-17 Fuentes de verificación sugeridas.** Solo sugerencias ("Fuente sugerida para verificar: SINAPROC"), nunca afirmaciones de que la institución dijo algo. Se muestran en `recommended_action` e `investigate_next`.
- **L-18 Preservación de atribución.** Numerador: oraciones generadas a partir de afirmaciones DECLARACION/SOLO_REPORTADA que conservan la atribución ("según…"). Denominador: todas las oraciones de ese tipo antes de la validación. Se reporta antes y después del validador.
- **A-07 Agenda de la mañana.** Bloque superior de la Sala de Situación: 5 tarjetas (título, P y rango, insignia de evidencia, "por qué" = las 2 frases de `rationale` con más peso, acción + fuente sugerida). Hora de Panamá.
- **A-08 Tarjeta de evidencia.** `evidence_card(ref: EvidenceRef)`: evidence_id, tipo, campo, valor, período (con advertencia si es histórico), URL y extracto. Se usa en la Ficha, en Producir y en Consultas.
- **A-09 Modo jurado.** Botones: "¿De dónde viene esta cifra y de qué año es?", "Si 5 medios replican una agencia, ¿cuántas fuentes independientes hay?", "¿Qué pasa si no hay evidencia?", "Fuente con instrucciones maliciosas". Cada uno lleva a la pantalla y el caso que lo demuestran.
- **B-11 CI.** `.github/workflows/ci.yml`: Python 3.12, `pip install -r requirements.txt`, `pytest -q -m "not needs_model"`. Sin secretos.
- **B-12 Ataques.** `data/labels/redteam.jsonl` (10 casos, marcados sintéticos) → `eval` reporta resistidos/total; cada fallo se anota en 06 con su corrección.
- **H-06 Mini-estudio.** 3 tareas (p. ej.: "elige el tema del día y lista 3 vacíos de verificación"), manual con navegador vs con SCAYL; cronometrar y declarar n=3 como exploratorio. Sin n medido no se afirma ahorro de tiempo.
