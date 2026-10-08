# Auditoría final de QA, métricas y seguridad

- **Fecha:** 2026-10-08 (≈18:30 UTC-5) · **Base:** `main` @ `b4d03f0`
- **Alcance:** verificación independiente (Subagente E). Solo lectura del código de producto (`scayl/`, `web/`, `app/`); se corrigieron únicamente textos de documentación cuando la evidencia era inequívoca (§5).
- **Entorno:** macOS (Darwin 24.6), Python del `.venv` del proyecto, Node v25.4.0. Sin GPU ni Ollama: nada de lo aquí ejecutado usa un modelo vivo.
- **Fuente de la definición T01–T10:** el PDF oficial no está en el repositorio. Se usaron la matriz `docs/notion_mirror/06_TESTS_AND_METRICS.md` (§ "Matriz T01–T10") y `web/public/data/trust_lab.json` → `test_definitions`, que coinciden entre sí.

## 1. Pruebas de aceptación T01–T10

Comando: `python -m pytest -q -rs` → **287 passed in 9.86 s, exit 0** (JUnit local, no versionado). Los IDs de cada T salen de `eval/results/latest.json → tests` (evidencia guardada: `eval/results/runs/20261007T222511745754Z.pytest.xml`, SHA-256 verificado).

| T | Caso | Pruebas (evidencia) | Guardado en `latest.json` | Re-ejecución hoy | Observación |
|---|---|---|---|---|---|
| T01 | Fechas inválidas y nulos | `tests/test_t01_validation.py` (2) | passed 2/2 | PASA | — |
| T02 | Tres registros del mismo evento | `tests/test_assemble.py::test_t02_…` (1) | passed 1/1 | PASA | Solo sintético |
| T03 | Noticia recirculada | `tests/test_assemble.py::test_t03_…` (1) | passed 1/1 | PASA | Solo sintético |
| T04 | Cifra anual del Banco Mundial | `tests/test_assemble.py::test_t04_…` (1) | passed 1/1 | PASA | Solo sintético |
| T05 | Afirmaciones incompatibles | `tests/test_assemble.py::test_t05_…` (1) | passed 1/1 | PASA | Solo sintético |
| T06 | Consulta sin respuesta | `tests/test_t06_qa_abstention.py` (13) | passed 13/13 | PASA | LLM simulado |
| T07 | Inyección en la fuente | `tests/test_t07_injection.py` (4) | passed 4/4 | PASA | LLM simulado; sin prueba con modelo vivo |
| T08 | Prioridad alta | `tests/test_t08_scoring.py` + `test_assemble::test_t08_…` (16) | passed 16/16 | PASA | — |
| T09 | Brief editorial | `tests/test_t09_studio.py`, `tests/test_t09_validators.py` (19) | passed 19/19 | PASA | LLM simulado |
| T10 | Sin internet | `tests/test_service_pipeline.py::test_pipeline_builds_bundle_and_fichas_offline` (1, fixture autouse bloquea `socket`) | passed 1/1 | PASA (automatizada) + arranque de la demo offline verificado | Ver detalle abajo |

**Detalle T10.**
- `python scripts/demo_offline.py` (equivale a `make demo-offline`) se lanzó en segundo plano con límite de 30 s. Copió `deploy/artifacts/v1/bundle.public.json` a `data/processed/v1/bundle.json` y Streamlit respondió `GET /_stcore/health → 200 ok` y `GET / → 200` en ≈1 s. Después se detuvo el proceso.
- Nota: el puerto 8501 estaba ocupado por otro proceso local, así que Streamlit se movió solo al 8502. Durante el ensayo, avisar que la URL puede cambiar.
- El SHA-256 del bundle copiado (`cf87681c…13bb8`) coincide con `latest.json → inputs[0]`.
- **Límite:** el wifi estaba encendido. El ensayo real sin red (H-05, `docs/TASKS.md:57`, estado DOING) **no se verificó** aquí. El propio `latest.json` declara para cada T: "no equivale a validación con LLM real ni ensayo sin wifi".
- **Inconsistencia:** `docs/notion_mirror/06_TESTS_AND_METRICS.md:19` dice que T10 está "**Parcial**", mientras `latest.json`, la web y las páginas Notion dicen "aprobada". Las dos lecturas son compatibles (la prueba automatizada pasa y falta el ensayo real), pero conviene que el Lead unifique el texto.

## 2. Auditoría de métricas

Todas las métricas de `eval/results/latest.json` (run_at 2026-10-07T22:25:11Z, snapshot v1) se cotejaron con su evidencia. `web/public/data/trust_lab.json → lab.metrics` y `lab.tests` son **idénticos** a `latest.json` (comparación JSON exacta), así que la web muestra exactamente lo medido.

### 2.1 Tabla de trazabilidad

| Métrica | Valor (num/den) | Fecha | Dataset | Modelo / modo | Método | Independencia | Evidencia · SHA-256 |
|---|---|---|---|---|---|---|---|
| Cobertura de citas | 45/45 | 2026-10-07 21:01Z | Top 15 eventos, frases conservadas de brief y guion (incluye avisos no factuales; excluye copy social) | qwen3:8b, **live** 15/15 (Q4_K_M, RX 9060 XT, Vulkan) | Automático | No aplica; 100 % en parte por construcción: el validador elimina las frases sin cita (67 generadas → 59 conservadas) | `eval/results/dl029-precompute.json` · **coincide** |
| Validez de sustento | 25/30 (2 parcial, 3 no) | 2026-10-07 | 30 afirmaciones, muestra determinista | **Paquetes `template`**, no salidas de Qwen | Humano (LowCrime, integrante del equipo) | No aleatoria; un solo revisor | `data/labels/support_review.csv` · **coincide**; archivo `runs/…support.csv` · coincide |
| Abstención correcta (red-team) | 16/16 | 2026-10-07 17:42Z | Set sintético escrito por IA | template/extractivo, sin modelo vivo | Automático | **Desarrollo**: corregido sobre el mismo set (6/16 → 16/16, DL-027) | `runs/…redteam.json` · coincide |
| Abstención falsa (red-team) | 0/4 | ídem | ídem | ídem | Automático | Desarrollo | ídem |
| Resistencia red-team / controles / sondas | 16/16 · 4/4 · 9/9 | ídem | ídem | ídem | Automático | Desarrollo | ídem |
| Holdout v2 (no está en `latest.json`) | Trampas 6/6; **abstención falsa 4/4**; controles respondidos 0/4; expectativas 6/10 | 2026-10-07 20:28Z | 10 preguntas escritas por un humano (frictionspp-svg, integrante del equipo) | template/extractivo | Automático contra expectativas humanas | Reservado: "no existing cases shown" (procedencia). No consta que no viera el código | `eval/results/holdout-v2-summary.json`, `eval/redteam/holdout_v2.provenance.json` |
| Temas macro-F1 | Reglas 0,757 · E5 0,246 (n=100) | 2026-10-07 19:58Z | 100 titulares C-01 | Reglas frente a E5 | Humano asistido (vio antes la propuesta IA) | No ciego | `eval/results/b07-human-metrics.json` · **coincide** |
| Agrupación F1 | E5 0,988 (P 42/42, R 42/43) · TF-IDF 0,436 (P 12/12, R 12/43), 488 pares | ídem | Pares de desarrollo 2025 | E5 frente a TF-IDF | Humano asistido | **Calibración** (los mismos pares fijaron τ): optimista | ídem · **coincide** |
| Precision@5 | 1/5 (exploratoria) | 2026-10-07 22:25Z | `data/labels/editor_top5.json` | ranking scoring-v1 | Humano (editor) | El editor vio antes una propuesta IA (coincidencia 1/5) | `editor_top5.json` · coincide |
| Latencia de paquete | mediana 13 131 ms, p95 16 997,5 ms, n=15 | 2026-10-07 21:01Z | Top 15 | qwen3:8b live; excluye caché y fallback | Automático (reloj de pared) | Hardware del equipo de demo, no el del evaluador | `dl029-precompute.json` · coincide |
| Latencia de consultas | no medido | — | — | — | — | — | — |
| Tokens, preservación de atribución | no medido | — | — | — | — | — | — |
| Costo de API | US$ 0,00 | — | — | local | Declarado | `cost_scope`: "no mide hardware/electricidad" | `latest.json` |
| Ahorro de tiempo | **no medido** (n=0 de 3 previstos) | 2026-10-07 18:04Z | — | — | — | — | `eval/results/time-study.json` |

Verificación de entradas (`latest.json → inputs`): las 8 rutas coinciden en SHA-256. `data/processed/v1/bundle.json` no está versionado. Coincide tras ejecutar `demo_offline.py`, porque es una copia de `deploy/artifacts/v1/bundle.public.json`.

### 2.2 Discrepancias encontradas

Ningún número publicado difiere de su evidencia. Los problemas son de **alcance o redacción**:

| # | Archivo:línea (antes de corregir) | Problema | Corrección sugerida | Estado |
|---|---|---|---|---|
| D1 | `README.md:40`; `docs/notion/SCAYL/Documentacion tecnica.md:52`; `Presentacion Pitch Day.md:63`, `:117` | "$0" sin la salvedad de hardware y electricidad (`cost_scope` la declara) | "…; no incluye hardware ni electricidad (no medidos)" | **Corregido** |
| D2 | `README.md:33`; `Documentacion tecnica.md:73`; `Presentacion Pitch Day.md:73` | La validez de sustento 25/30 se midió sobre paquetes **template** (`generation_modes: ["template"]`), pero aparece junto a la cobertura 45/45 de qwen3:8b, como si validara los borradores del LLM | Agregar "muestra de paquetes en modo plantilla (no de borradores de qwen3:8b)" | **Corregido** |
| D3 | `README.md:32`; `Documentacion tecnica.md:72`; `Presentacion Pitch Day.md:65` | La cobertura de citas puede leerse como sustento ("lo que no tiene respaldo se elimina") | "Mide presencia de cita, no validez del sustento" | **Corregido** |
| D4 | `Documentacion tecnica.md:50`; `Presentacion Pitch Day.md:60` | F1 0,99 de agrupación sin aclarar que viene de pares de **calibración** (el README sí lo aclara) | "(pares de desarrollo usados para calibrar τ: resultado optimista)" | **Corregido** |
| D5 | `Documentacion tecnica.md:74` ("set humano **independiente** … sin ver el código"); `Presentacion Pitch Day.md:72` | El autor es integrante del equipo. La procedencia solo dice "no existing cases shown". Se omite que también se abstuvo en 4/4 controles (abstención falsa 4/4; 6/10 frente a las expectativas, DL-030) | "Escrito por un integrante del equipo sin ver los casos existentes; también se abstuvo en 4/4 controles (6/10 frente a sus expectativas)" | **Corregido** (también en `README.md:35`) |
| D6 | `Documentacion tecnica.md:70`, `:85`; `Presentacion Pitch Day.md:71` | "10/10 aprobadas" y "Funciona con el wifi apagado (T10)": la evidencia es una prueba automatizada con el socket bloqueado; el ensayo sin wifi no consta | "10/10 pruebas automatizadas; T10 con red bloqueada en pytest, no equivale a ensayo real sin wifi" | **Corregido** |
| D7 | `Documentacion tecnica.md:93` | "`.env.example` vacío": el archivo tiene valores no secretos (host de Ollama, modelo, etc.) | "`.env.example` sin valores secretos" | **Corregido** |
| D8 | `Documentacion funcional.md:25` | "recibo verificable": el recibo es un SHA-256 calculado por el mismo servidor, sin firma; además `from_state` lo aporta el navegador | "recibo con hash SHA-256 (integridad del contenido; no es una firma)" | **Corregido** |
| D9 | `docs/DEMO_SCRIPT.md:32` | "costo de API $0" sin salvedad | Agregar "sin contar hardware ni electricidad" | Pendiente (fuera del alcance de edición) |
| D10 | `docs/notion_mirror/02_DECISION_LOG.md:212`, `08_JURY_PITCH.md:12` | "sin ver el código": la procedencia solo respalda "sin ver los casos existentes" | Cambiar a "sin ver los casos existentes" | Pendiente (lo edita el Lead) |
| D11 | `docs/notion_mirror/06_TESTS_AND_METRICS.md:19` frente a `latest.json` | T10 "Parcial" frente a "passed" | Unificar: "Automatizada: PASA; ensayo real sin wifi: pendiente o hecho (con fecha)" | Pendiente (Lead) |
| D12 | `docs/notion_mirror/06_TESTS_AND_METRICS.md:26` | "Holdout v2 humano: 6/6" sin mencionar la abstención falsa 4/4 | Agregar "abstención falsa 4/4 (controles fuera del corpus)" | Pendiente (Lead) |
| D13 | `web/app/trust-lab/page.tsx:43` (tarjeta "Generación medida") con `trust_lab.json → generation: {packages: 0, status: "no medido"}` | La tarjeta dice "no medido" mientras la misma página muestra cobertura y latencia medidas de la corrida DL-029. Se debe a que el bundle público no trae `generation_report`; puede confundir al jurado | Texto: "El bundle público no incluye el reporte de generación; la cobertura y la latencia provienen de la corrida DL-029 (ver arriba)" | Pendiente (código web) |
| D14 | `.env.example:6` | `SCAYL_EMBED_MODEL=BAAI/bge-m3`, mientras la agrupación documentada usa `intfloat/multilingual-e5-base` | Cambiar el ejemplo a `intfloat/multilingual-e5-base` | Pendiente (configuración) |

No se encontraron afirmaciones de ahorro de tiempo: todas las superficies dicen "no medido". Tampoco se encontraron números que difieran de la evidencia (45/45, 25/30, 16/16, 6/6, 0,76/0,25, 0,99/0,44, 1/5, 13,1 s / 17,0 s y 287 coinciden).

## 3. Seguridad

| Severidad | Hallazgo | Evidencia |
|---|---|---|
| Ninguna | **Sin secretos versionados.** `git ls-files` (911 archivos) solo contiene `.env.example`, sin valores secretos (`NOTION_TOKEN=` vacío). `git grep` sin coincidencias para claves AWS, OpenAI/Anthropic `sk-…`, GitHub `ghp_`/`github_pat_`, Slack `xox*`, Google `AIza…`, HuggingFace `hf_…`, JWT ni bloques `PRIVATE KEY`, ni asignaciones literales a `api_key/secret/token/password`. | §6 |
| Ninguna | `.gitignore` raíz ignora `.env`, `data/cache/`, `data/state/` y `models/`; `web/.gitignore` ignora `.env*`, `.vercel/`, `node_modules/` y `.python-runtime/`. `web/vercel.json` no declara variables; la web no usa `process.env` ni `NEXT_PUBLIC_*`. | — |
| Baja | El `.gitignore` raíz ignora `.env` pero no `.env.local` ni `.env.*`. Hoy no hay ninguno; sugerencia: añadir `.env.*` y `!.env.example`. | `.gitignore:1` |
| Baja | **API de revisión web** (`web/python_api/actions.py`, `http.py`). Bien: pydantic `extra="forbid"`, `StrictStr` con longitudes máximas (300, 80, 100 y 500), cuerpo de 8 KiB como máximo, `Content-Type` obligatorio, errores 503 saneados, sin logs de contenido, solo modo caché y sin rutas del llamador. Límites declarados: sin autenticación ni límite de tasa; `from_state` lo aporta el cliente; el recibo es un hash propio sin firma, así que cualquiera puede generar uno válido. Aceptable para una demo sin estado; no presentarlo como auditoría a prueba de manipulación (corregido en D8). | — |
| Baja | La persistencia local (`scayl/review/store.py`) usa SQL **parametrizado** (`?` y `:name`): sin inyección SQL. A diferencia de la API web, no aplica longitudes máximas a `reviewer` ni a `justification`. | `store.py:61`, `:105` |
| Baja | No hay sumideros de HTML: ni `dangerouslySetInnerHTML`/`innerHTML` en `web/`, ni `unsafe_allow_html` en `app/`. | grep |
| Baja | `scripts/demo_offline.py:38-39` arranca Streamlit sin `--server.address`, así que escucha en todas las interfaces (el log mostró la URL de red local y la externa). En una red de evento, otros equipos de la LAN podrían abrir la demo. Sugerencia: añadir `"--server.address", "localhost"`. | log del ensayo T10 |
| Informativa | **Texto de fuente no confiable.** `scayl/gen/guard.py` detecta patrones de inyección en español e inglés, quita los delimitadores `<<<`, `>>>` y ```` ``` ````, serializa en JSON dentro de `<<<DATOS_NO_CONFIABLES>>>` y añade `SYSTEM_DATA_RULE`. `claims.py`, `studio.py`, `qa.py` y `bulletin.py` pasan siempre por `data_block`. El modelo no tiene herramientas, red ni secretos; la salida se valida con esquema y con `output_obeys_injection`. Límite: la detección es por expresiones regulares y no cubre ataques desconocidos ni otros idiomas (ya declarado en `latest.json → limitations`). | — |
| Resultado | Pruebas de red-team y de inyección: `pytest tests/test_redteam.py tests/test_t07_injection.py tests/test_t06_qa_abstention.py` → **22 passed**. Corrida guardada `redteam-latest.json`: 16/16, sin fallos. | — |

## 4. Calidad de código y build

| Comando | Resultado |
|---|---|
| `python -m pytest -q -rs` | **287 passed**, 0 omitidas, 9,86 s |
| `python -m ruff check .` (ruff 0.16.10, configurado en `pyproject.toml`) | **All checks passed** |
| `cd web && npm run lint` (`eslint . --max-warnings=0`) | **exit 0**, sin advertencias |
| `cd web && npm ci && npm run build` (Next.js 16.4.0, Turbopack) | **exit 0**: 173 páginas estáticas (165 fichas `/caso/*`, `/`, `/boletin`, `/consultas`, `/recorrido`, `/simulador`, `/trust-lab`). Primero se intentó con un enlace simbólico a `node_modules`, que Turbopack rechaza; se repitió con `npm ci` local (4 s) y luego se borraron `node_modules`, `.next` y `out`. |

## 5. Correcciones de documentación hechas en esta auditoría

1. `README.md`: tabla de resultados → cobertura de citas ≠ sustento (D3), validez de sustento sobre paquetes plantilla (D2), holdout con 4/4 controles y 6/10 (D5), costo $0 sin hardware ni electricidad (D1).
2. `docs/notion/SCAYL/Documentacion tecnica.md`: D1, D2, D3, D4, D5, D6 (filas T01–T10 y despliegue offline) y D7.
3. `docs/notion/SCAYL/Presentacion Pitch Day.md`: D1 (dos lugares), D3, D4, D5, D6 y D2.
4. `docs/notion/SCAYL/Documentacion funcional.md`: D8.

Ninguna corrección cambia un número: solo añaden el alcance que ya consta en la evidencia (`latest.json`, `b07-human-metrics.json`, `holdout-v2-summary.json`, `holdout_v2.provenance.json`, `.env.example` y `web/python_api/actions.py`). **Las páginas de Notion publicadas deben reimportarse** para reflejar estos cambios.

## 6. Comandos ejecutados

```bash
python -m pytest -q -rs --junitxml=<scratch>/pytest-qa.xml        # 287 passed
python -m ruff check .                                             # All checks passed
python -m pytest -q tests/test_redteam.py tests/test_t07_injection.py tests/test_t06_qa_abstention.py   # 22 passed
python scripts/demo_offline.py &  ; curl localhost:8502/_stcore/health ; curl localhost:8502/   # 200 / 200, luego kill
shasum -a 256 data/processed/v1/bundle.json deploy/artifacts/v1/bundle.public.json
python <scratch>/q1.py   # SHA-256 de cada evidence/sha256 de latest.json
python <scratch>/q2.py   # SHA-256 de latest.json → inputs; lectura de time-study, holdout, b07, b10
python <scratch>/q3.py   # trust_lab.json frente a latest.json (igualdad exacta)
git ls-files | grep -iE '(^|/)\.env|\.pem$|\.key$|id_rsa|credentials|secrets?\.'
git grep -nIE 'AKIA…|sk-…|ghp_…|github_pat_…|xox…|AIza…|hf_…|BEGIN … PRIVATE KEY|eyJ…'
git grep -nIiE '(api_key|secret|token|password)\s*[:=]\s*"…"'
git grep -nE 'process\.env|NEXT_PUBLIC_|os\.environ|getenv|st\.secrets' -- web deploy app scayl scripts
cd web && npm run lint && npm ci --prefer-offline && npm run build
```
