# Instrucciones para el agente de frictionspp-svg (Codex/Astra)

Eres el agente de código de **frictionspp-svg** en el proyecto SCAYL (reto TVN Media "De la señal a la decisión",
hackIAthon Panamá). El Lead es Claude (otro agente) junto con el Humano 1; él revisa y mergea tus PR.
Tu dueño humano está contigo: pídele confirmación antes de cualquier acción irreversible o que use credenciales.

## Tu rol
Camino crítico del proyecto: **datos → inteligencia semántica → primera UI visible**. Otros dependen de ti
(el snapshot desbloquea todo), así que prioriza entregar pronto y en PRs pequeños.

## 📌 Notas del Lead pendientes (actualizado 2026-10-07, tras mergear tu PR #19)
**Tu snapshot C-01 está en `main` y verificado** (187 noticias, 50 TVN, manifest con 0 diferencias). Gracias.
Como te quedaste sin sesión y B-03 bloqueaba el hito M1, el Lead hizo (DL-023):
- **B-03** `scayl/ingest/validate.py::load_snapshot` (nulos preservados, fechas inválidas marcadas, exclusiones con motivo, ventana C-01, URL duplicadas, idioma normalizado a ISO 639-1; lee también `indicadores_recientes.csv` y `eventos_ext.geojson`).
- **B-05 baseline:** `scayl/intel/embed.py` (TF-IDF de caracteres), `topics.py` (reglas por palabras clave) y `cluster.py` (aglomerativo con restricción de 7 días). **El pipeline ya corre con datos reales.**
- Se quitó `tmp/` del repo (ahora está en `.gitignore`; tus archivos siguen en tu disco). `data/processed/*/` no se sube hasta que exista el top 5 ciego.

**Tu orden ahora:**
1. **B-13 ACP** y **B-14 INEC** → `data/raw/v1/indicadores_recientes.csv` (formato exacto en TASKS B-13/B-14). Snapshot v1 ya congelado: agrega estos archivos como **adición declarada** (nuevo inventario + manifest recongelado como v1.1 o con su recibo; no alteres bytes existentes).
2. **B-05 variante IA** (tu GPU): crea `scayl/intel/embed_st.py` con `class SentenceTransformerEmbedder` (atributo `name`, `encode(texts) -> np.ndarray` L2-normalizado) y `scayl/intel/topics_ai.py` con `classify(items) -> list[(Topic, conf)]`. El pipeline los usa solo (`SCAYL_INTEL=ai`). Agrega `DEFAULT_TAU[<name>]` en `cluster.py` (eso es local a tu tarea).
3. **Calibra** τ y las reglas con el **conjunto de desarrollo de 2025** (DL-018), nunca con la ventana C-01.
4. **B-07** etiquetas (≥100 temas + pares por pool DL-016) y **B-10** benchmark de modelos (`make ping`, latencia real en tu AMD).
5. **Cuando LowCrime haya entregado `data/labels/editor_top5.json`**: `make precompute` en tu máquina (LLM real sobre el top 15) y guarda `data/processed/v1/generation_report.jsonl` para el Trust Lab.
Cuando cumplas los pasos, borra esta sección en tu PR.

## ⚠️ Relevo de sesión (lee esto primero)
- **Al empezar:** sincroniza tu rama con `main` (`git fetch origin && git merge origin/main`, sin rebase) y lee las "Notas del Lead pendientes". Luego, si existe `docs/handoff/frictionspp-svg.md`, léelo antes que cualquier otra cosa y continúa desde su "Siguiente paso concreto".
- **Al acercarte al límite (~15% restante)**, o si tu humano escribe **"RELEVO"**: detente, haz commit (`WIP:` si está a medias), escribe `docs/handoff/frictionspp-svg.md` con la plantilla `docs/handoff/TEMPLATE.md`, haz push y avísale a tu humano. Si no puedes ver tu límite, díselo a tu humano al empezar y haz un relevo preventivo al terminar cada tarea. Detalle en `AGENTS.md` §2b.

## Lee antes de escribir código (en este orden)
1. `AGENTS.md` (reglas obligatorias).
2. `docs/ARCHITECTURE.md` §3 (contratos), §4.1 (validación), §4.2 (agrupación), §5.1 (interfaz semántica), §6 (interfaces).
3. `scayl/contracts.py` y `tests/fixtures/ui_bundle.example.json`.
4. `docs/notion_mirror/02_DECISION_LOG.md` (DL-006, DL-008, DL-010, DL-011) y `03_DATA_CATALOG.md`.
5. En `docs/TASKS.md`: la tabla (tus filas dicen **F**) y las secciones B-01..B-07, B-10, B-11, A-01, A-02, A-08.

## Orden de trabajo (un PR por bloque; rama `worker-b/<bloque>` para datos, `worker-a/<bloque>` para UI)
1. **B-01 + B-02 · Snapshot** (meta: miércoles 7 a las 10:00, hora de Panamá).
   - GDELT DOC 2.0 `mode=ArtList&format=json&maxrecords=250` con `STARTDATETIME`/`ENDDATETIME` de la ventana de `scayl/config/data_window.v1.yaml` (objetivo 2026-09-01 → 2026-10-01), **un día por consulta**; consultas: Panama/Panamá y logística/Canal, turismo, economía y eventos naturales. Deduplica por URL.
   - TVN: la misma API con `domain:tvn-2.com` (≥20 registros). Guarda también el RSS actual de TVN aparte (no entra al intervalo).
   - World Bank: PAN, CRI, COL, DOM, MEX y GTM × los 6 indicadores × 2010–2024; completa la cuadrícula de 540 filas (6×6×15, DL-013) con `valor` nulo.
   - USGS: 2024-01-01..2024-12-31, lat 5..12, lon −86..−76, M≥3, todos los eventos.
   - Guarda las respuestas crudas en `data/raw/v1/`, el `manifest.json` con SHA-256 y `docs/DATA_DICTIONARY.md`; actualiza tus filas de `03_DATA_CATALOG.md`.
   - Bloque de tiempo: si en 2 h no hay ≥100 noticias (≥20 TVN) en el intervalo, aplica el respaldo de DL-008 y documenta la desviación.
   - Interfaz que el pipeline del Lead ya consume (`scayl/pipeline.py::_load_worker_b`): `scayl.ingest.validate.load_snapshot(dir) -> (news, indicators, quakes, report)` con `report.total` o `report["total"]`; `scayl.intel.topics.classify(items, method="baseline"|"ai") -> list[(Topic, conf)]`; `scayl.intel.cluster.cluster(items, embedder) -> list[list[id_noticia]]`; `scayl.intel.embed.get_embedder("tfidf"|"st", model)`. Si necesitas cambiar una firma, propuesta en AGENT_PROPOSALS.
   - **En cuanto el snapshot exista:** genera `data/labels/editor_candidates.csv` (id + titular + medio + fecha, en orden aleatorio, **sin ningún puntaje**) para que LowCrime haga su top 5 a ciegas (H-08).
2. **A-01 + A-08 + A-02 · Primera UI sobre el fixture**: esqueleto Streamlit que usa `scayl/service.py` (ya existe; sin bundle real usa el fixture automáticamente), tarjeta de evidencia y Sala de Situación. Tus archivos: `app/Home.py`, `app/service_client.py`, `app/components/**`, `tests/ui/**`. Las páginas `app/pages/1_Ficha_de_Caso.py`, `2_Consultas.py` y `3_Trust_Lab.py` créalas solo como esqueleto: son de LowCrime.
3. **B-03 + B-04 · Validación (T01) y casos sintéticos.**
4. **B-11 · GitHub Actions** (pytest sin modelos en cada PR).
5. **B-05 · Embeddings, temas y agrupación** (baseline TF-IDF + IA; embeddings precalculados en `embeddings.npz`) y **B-07 · etiquetas** (≥100 titulares por tema + pares de agrupación; pídeselas a tu humano y documenta el método).
6. **B-06 · Recuperación** (BM25 + coseno, puntuación en [0,1]).
7. **Máquina de demo (comandos listos del Lead):** `make ping` (calienta el modelo y mide latencia), `make precompute` (LLM sobre el top 15: llena `data/cache/llm/` y genera `data/processed/v1/generation_report.jsonl`). Variables en `.env`: `SCAYL_LLM_MODEL`, `OLLAMA_HOST`. Si `ping` falla, revisa que Ollama esté corriendo y que el tag del modelo exista.
8. **B-10 · Benchmark de modelos locales.** Tu máquina (AMD RX 9060 XT 8 GB, Vulkan) es la **máquina de demo y de precálculo**. Empieza las descargas en paralelo desde el inicio (`ollama pull` de los candidatos de DL-006 y los modelos de embeddings), mientras corren los fetchers. Mide con `num_ctx=4096`, thinking desactivado y salida JSON: tokens/s, latencia (mediana y p95, n≥10), tasa de JSON válido y VRAM. Registra los resultados en tu PR para que el Lead cierre DL-006. Más adelante, el Lead te pedirá correr en esta máquina el precálculo de la caché LLM (`data/cache/llm/`).

## Reglas clave (el detalle está en AGENTS.md)
- Solo tocas tus archivos permitidos. Para cambiar contratos, `scayl/config/`, dependencias o archivos de otros: primero propuesta en `docs/AGENT_PROPOSALS.md`.
- UTF-8, ISO 8601 en UTC; nunca conviertas un nulo en 0; la fecha de publicación es distinta de la de detección; conserva las unidades originales; `data/raw` es inmutable.
- Solo titulares + URL + metadatos: nunca cuerpos de artículos. Casos alterados = sintéticos, con el prefijo `[SINTÉTICO]`.
- Métricas solo desde ejecuciones guardadas, con numerador y denominador. Nada inventado.
- `python -m pytest -q` en verde antes de cada PR; las pruebas con modelo llevan `@pytest.mark.needs_model`.
- No edites `docs/TASKS.md`, el tablero ni el decision log. Escribe tu avance en `docs/worklog/worker-b.md` (hora UTC; solo agregar).
- Agrega una fila en `docs/AI_TOOLS_USED.md` por cada uso relevante de IA (entregable oficial).
- Si una prueba falla de verdad y la corriges, anótalo en `docs/notion_mirror/06_TESTS_AND_METRICS.md` → "Registro de pruebas fallidas".
- Descripción del PR: tarea(s) cerradas, pruebas, desviaciones y capturas (para UI, a 1280×720).
