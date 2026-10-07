# Instrucciones para el agente de frictionspp-svg (Codex/Astra)

Eres el agente de código de **frictionspp-svg** en el proyecto SCAYL (reto TVN Media "De la señal a la decisión",
hackIAthon Panamá). El Lead es Claude (otro agente) junto con el Humano 1; él revisa y mergea tus PR.
Tu dueño humano está contigo: pídele confirmación antes de cualquier acción irreversible o que use credenciales.

## Tu rol
Camino crítico del proyecto: **datos → inteligencia semántica → primera UI visible**. Otros dependen de ti
(el snapshot desbloquea todo), así que prioriza entregar pronto y en PRs pequeños.

## 📌 Notas del Lead pendientes — backlog final (actualizado 2026-10-07, tras PR #31)
Integrado en main: B-05 IA (DL-025), B-13/B-14 (DL-026, AP-012 aceptada), red-team y nuevas guardias de Consultas (DL-027). Entrega: **jueves 8, 23:59 hora de Panamá**. Trabaja en este orden:

1. **Repetir `make precompute`** (GPU, E5 activo). Cambiaron afirmaciones de contexto y el caché LLM viejo no coincide. Guarda en `eval/results/` la latencia mediana y el p95, la cobertura de citas, los modos (live/fallback) y el hardware.
2. **Caché pública para A-06:** `make public-bundle` + la caché LLM necesaria (solo entradas revisadas, sin descripciones RSS), por PR. Avisa a LowCrime en el PR (`@LowCrime`).
3. **B-11 CI:** `.github/workflows/ci.yml` con Python 3.12, `pip install -r requirements.txt`, `python -m pytest -q` y `ruff check .`; badge en el README. Corrige los avisos de ruff en `tests/` (no toques la lógica de `scayl/` del Lead; si ruff marca algo ahí, solo reporta).
4. **Set reservado de red-team v2 (humano):** tu humano escribe a mano 10 preguntas trampa nuevas, **sin mirar** `scayl/gen/qa.py` ni `eval/redteam/cases.jsonl`. Guárdalas en `eval/redteam/holdout_v2.jsonl` (mismo formato) y córrelas con el runner sin cambiar código. Reporta num/den tal como salgan, aunque sean malos.
5. **B-07 etiquetas humanas:** el agente propone y el humano confirma o corrige. ≥100 temas (de C-01, `data/labels/topics_human.csv`) y revisión humana de los pares de desarrollo de agrupación. Con eso, calcula macro-F1 de temas (baseline vs IA) y P/R/F1 de agrupación en `eval/results/b07-*.json`.
6. **B-10 benchmark:** compara qwen3:8b con al menos un modelo más pequeño (p. ej. qwen3:4b o llama3.2:3b) en el top 15: latencia mediana y p95, cobertura de citas y oraciones eliminadas por el validador. Recomienda el modelo para la demo, con datos.
7. **B-04 casos sintéticos** T01/T03/T05/T07 en `data/synthetic/`, marcados `sintetico=true`, para la demo de casos que el corpus real no tiene (incluye **un caso "suficiente para borrador"** con cifra coincidente de ACP o INEC, claramente SINTÉTICO).
8. **H-06 mini-estudio (con LowCrime):** 3 tareas cronometradas, manual vs con SCAYL (protocolo en TASKS §H-06). n=3, exploratorio.
9. **B-06** (opcional, solo si sobra tiempo): `scayl/intel/retrieve.py` híbrido BM25 + coseno E5 detrás de un flag. No reemplaces el recuperador de `qa.py` sin propuesta.

### Reglas de autonomía (trabaja hasta terminar sin esperar al Lead)
- **No esperes merges.** Al terminar una tarea, abre su PR y pasa a la siguiente. Antes de cada tarea: `git fetch origin && git checkout -b <rama-nueva> origin/main` (una rama y un PR por tarea; sin rebase ni force-push sobre ramas compartidas).
- **Si una tarea está bloqueada** (depende de otra persona o de un merge), sáltala, anótalo en el PR o en el worklog y sigue con la próxima; vuelve a ella al final.
- **Tareas con humano:** pídele a tu humano lo mínimo y concreto (p. ej., "elige sí/no en estas 30 filas"). Mientras responde, avanza con otra tarea.
- **Nunca:** publicar nada externo sin confirmación del Lead; subir `data/processed/`, ZIP de GKG, RSS con descripciones, secretos o `.env`; editar `01_EXECUTION_BOARD.md`, `02_DECISION_LOG.md` ni el estado de `TASKS.md` (eso es del Lead). Si una decisión cambia contratos, alcance o el módulo de otro, abre una propuesta en `docs/AGENT_PROPOSALS.md` (con el siguiente número libre) y sigue con lo demás.
- **Cada PR:** `python -m pytest -q` en verde; métricas con num/den y "no medido" en lo que no midas; fallos reales en el registro de `06`; tu fila en `docs/AI_TOOLS_USED.md` (en conflictos de bitácoras, conserva ambos lados).
- **Relevo:** cerca del 15% de sesión o si tu humano escribe "RELEVO", aplica AGENTS §2b. Quien te releve continúa desde esta lista.
- **Al terminar todo:** escribe en `docs/handoff/frictionspp-svg.md` la lista de PRs abiertos y lo que quedó pendiente, y avísale a tu humano con "TERMINADO".

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
