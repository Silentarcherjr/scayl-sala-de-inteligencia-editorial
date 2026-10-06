# TASKS — tareas atómicas y asignables

> El estado oficial lo actualiza solo el Lead (al mergear). Los workers reportan en su PR y en `docs/worklog/`.
> Estados: `TODO` · `DOING` · `REVIEW` · `DONE` · `BLOCKED`. Prioridad: P0/P1/P2. Hito: M0–M4.
> Dueños: **L** = Humano 1 + Claude (Lead) · **A** = Humano 2 + Codex/Astra (UI) · **B** = Humano 3 + Codex/Astra (datos/eval) · **H** = tareas humanas.

## Resumen

| ID | Tarea | Dueño | Prio | Hito | Estado | Depende de |
|---|---|---|---|---|---|---|
| L-01 | Contratos de datos + fixture de UI | L | P0 | M0 | DONE | — |
| L-02 | Docs de gobernanza + espejo Notion | L | P0 | M0 | DONE | — |
| L-03 | `scoring_rules.v1.yaml` + `evidence/scoring.py` + `status.py` | L | P0 | M1 | TODO | L-01 |
| L-04 | `evidence/provenance.py` (Source DNA) | L | P0/P1 | M1 | TODO | B-03 |
| L-05 | `evidence/linking.py` + `temporal.py` (WB/USGS, Temporal Guard) | L | P0 | M1 | TODO | B-03 |
| L-06 | `evidence/conflicts.py` (numéricos, fechas, unidades, períodos) | L | P0 | M2 | TODO | L-05 |
| L-07 | `pipeline.py build` + `service.py` + `bundle.json` + `fichas.jsonl` | L | P0 | M1 | TODO | L-03, B-03, B-05 |
| L-08 | `gen/llm.py` (Ollama + caché + meta) + `guard.py` | L | P0 | M2 | TODO | — |
| L-09 | `gen/validators.py` + fallback `template` | L | P0 | M1 | TODO | L-01 |
| L-10 | `gen/claims.py` + `studio.py` + prompts v1 | L | P0 | M2 | TODO | L-08, L-09 |
| L-11 | `gen/qa.py` con abstención | L | P0 | M2 | TODO | B-06, L-08 |
| L-12 | `review/store.py` + `outbox.py` | L | P0 | M1 | TODO | L-01 |
| L-13 | `evidence/gaps.py` (Investigation Gap) | L | P1 | M2 | TODO | L-05 |
| L-14 | Integración, merges, README final, pitch | L | P0 | M3–M4 | TODO | todo |
| A-01 | App Streamlit: esqueleto + `FixtureService` + navegación | A | P0 | M1 | TODO | L-01 |
| A-02 | Sala de Situación | A | P0 | M1 | TODO | A-01 |
| A-03 | Ficha de Caso (6 pestañas) | A | P0 | M1–M2 | TODO | A-01 |
| A-04 | Consultas (Q&A) | A | P0 | M2 | TODO | A-01 |
| A-05 | Trust Lab (vista) | A | P1 | M3 | TODO | B-08 |
| A-06 | Despliegue del enlace en modo `cache` | A | P0 | M3 | TODO | AP-001, L-07 |
| B-01 | Obtener snapshot oficial **o** Plan B (fetchers) → `data/raw/v1` | B | P0 | M0 | TODO | — |
| B-02 | `ingest/manifest.py` (SHA-256, conteos, transformaciones) + diccionario | B | P0 | M0 | TODO | B-01 |
| B-03 | `ingest/validate.py` + normalización → `data/processed` + `quality_report` (T01) | B | P0 | M1 | TODO | B-01 |
| B-04 | Casos sintéticos T01/T03/T05/T07 en `data/synthetic/` | B | P0 | M1 | TODO | L-01 |
| B-05 | `intel/embed.py` + `topics.py` + `cluster.py` (baseline + IA) | B | P0 | M1–M2 | TODO | B-03 |
| B-06 | `intel/retrieve.py` (BM25 + coseno) | B | P0 | M2 | TODO | B-05 |
| B-07 | Etiquetas humanas: temas (≥100), pares de agrupación, top 5 ciego, benchmark dev (40) | B + H | P0 | M2 | TODO | B-03 |
| B-08 | `eval/`: métricas, benchmark, latencia → `eval/results/latest.json` | B | P0/P1 | M3 | TODO | B-05, L-10, L-11 |
| B-09 | Revisión humana de ≥30 afirmaciones (validez de sustento) | H | P0 | M3 | TODO | L-10 |
| B-10 | Benchmark de modelos locales (embeddings + LLM) en hardware declarado | B | P0 | M1 | TODO | — |
| H-01 | Pedir a la organización: snapshot, benchmark, fecha exacta, acceso a Notion | H1 | P0 | M0 | TODO | — |
| H-02 | Bitácora `docs/AI_TOOLS_USED.md` → PDF | Todos | P0 | M4 | DOING | — |
| H-03 | Publicaciones en redes (@hackiathon @viamatica @adenbs) | H | P0 | M1–M4 | TODO | — |
| H-04 | Migrar el espejo a Notion y compartirlo con el jurado | H1 + L | P0 | M3 | BLOCKED (sin acceso) | Notion |

---

## Contratos de las tareas de los workers

Cada tarea define: objetivo · archivos permitidos · entradas · salidas · interfaces · pruebas · terminado.
**Fuera de los archivos permitidos → propuesta en `AGENT_PROPOSALS.md`.**

### A-01 · Esqueleto Streamlit + FixtureService
- **Objetivo:** app navegable de 4 páginas que lee el fixture.
- **Archivos permitidos:** `app/**`, `tests/ui/**`, `requirements.txt` (solo agregar `streamlit` y `pandas` fijados; avisar en el PR).
- **Entradas:** `tests/fixtures/ui_bundle.example.json` (modelo `UIBundle`).
- **Salidas:** `app/Home.py` (Sala de Situación), `app/pages/1_Ficha_de_Caso.py`, `2_Consultas.py`, `3_Trust_Lab.py`, `app/service_client.py`.
- **Interfaz:** `app/service_client.py` expone las mismas funciones que `scayl/service.py` (ARCHITECTURE §6). Selección por `SCAYL_UI_SOURCE=fixture|service`. La UI **solo** importa `scayl.contracts` y `service_client`.
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
- **Ruta 1:** paquete oficial de la organización (preferido) → copiar sin modificar.
- **Ruta 2 (Plan B):** `scayl/ingest/fetch_{tvn_rss,gdelt,worldbank,usgs}.py` ejecutados en máquina con internet.
  - WB: 6 países (PAN, CRI, COL, DOM, MEX, GTM) × 6 indicadores × 2010–2024; completar la cuadrícula de 1.350 filas con `valor` nulo.
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

### B-08 · Evaluación
- **Salida:** `eval/results/latest.json`:
  `{run_at, hardware, models, metrics:{citation_coverage:{num,den}, support_validity:{num,den,reviewer}, abstention_correct:{num,den}, abstention_false:{num,den}, topics_macro_f1:{baseline,ai,n}, clustering:{baseline:{p,r,f1}, ai:{...}, n_pairs}, precision_at_5:{value, exploratory:true}, latency_ms:{qa:{median,p95,n}, package:{median,p95,n}}, tokens:{...}, api_cost_usd:0.0}, tests:{T01..T10:{status, evidence}}}`.
- Comando: `python -m scayl.eval.run --snapshot v1`.

### B-10 · Benchmark de modelos locales
- Medir en el hardware real: tiempo de embeddings (bge-m3 frente a multilingual-e5-base), tokens/s y latencia JSON de `qwen3:8b` frente a `qwen3:4b` (u otra alternativa local) con thinking desactivado. Registrar los resultados en `02_DECISION_LOG.md` (DL-006) mediante PR.
