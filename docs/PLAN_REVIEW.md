# PLAN_REVIEW — Revisión crítica del brief SCAYL

> Autor: Lead (Claude) · Fecha: 2026-10-06 · Estado: v1, pendiente de validación humana
> Fuentes oficiales leídas: `hackIAthon - reto TVN Media.pdf` (12 pp, **fuente de verdad**, el más reciente) y
> `hackIAthon Panamá - Bases y Entregables.pdf` (4 pp).
>
> Leyenda de procedencia de cada afirmación:
> **[OFICIAL]** está en los documentos del reto · **[MEDIDO]** lo comprobé en este entorno ·
> **[EXTERNO]** conocimiento externo no verificado aquí · **[SUPUESTO]** hipótesis nuestra.

---

## 1. Estado actual del repositorio [MEDIDO]

| Elemento | Estado al iniciar |
|---|---|
| Código | Ninguno. Solo `README.md` de 2 líneas (commit inicial). |
| Dependencias | Ninguna. |
| Datos | Ninguno. |
| Deuda técnica | Ninguna (repositorio vacío). |
| Componentes reutilizables | Ninguno. |

Lo que se creó en esta sesión: contratos de datos (`scayl/contracts.py`), un fixture sintético para la UI,
pruebas de contrato, el esqueleto de directorios y toda la documentación de plan/gobernanza.

### Restricciones del entorno de ejecución del Lead [MEDIDO]
- El contenedor cloud de Claude **no tiene acceso** a `tvn-2.com`, `api.gdeltproject.org`,
  `api.worldbank.org`, `earthquake.usgs.gov`, `huggingface.co` ni `ollama.com` (403 de la política de red).
  Sí tiene acceso a PyPI y npm.
- Sin GPU; 4 vCPU y 15 GB de RAM.
- **Consecuencia:** la descarga de datos y modelos y las pruebas con LLM o embeddings reales se hacen en
  la máquina de un integrante humano. El código del Lead debe poder probarse sin modelos, con fallbacks
  deterministas y artefactos precalculados.

---

## 2. Discrepancias entre el brief y los requisitos oficiales

| # | Tema | Brief SCAYL | Requisito oficial | Resolución |
|---|---|---|---|---|
| D1 | Enlace del agente | No mencionado | **[OFICIAL Bases]** Entregar el "enlace del agente desarrollado y en ejecución" | Desplegar la app en **modo snapshot** con salidas LLM precalculadas y etiquetadas; el LLM en vivo queda local. Ver AP-001. |
| D2 | PDF de herramientas IA | No mencionado | **[OFICIAL Bases]** Un PDF con propósito, aplicación y resultado de cada herramienta IA usada en el desarrollo; afecta la calificación | Bitácora continua en `docs/AI_TOOLS_USED.md` → PDF al cierre. |
| D3 | Duración del pitch | Demo de 4 min | **[OFICIAL TVN §11]** Pitch de 10 min desde Notion: 1 problema / 1 solución / **4 demo** / 2 arquitectura+IA / 1 valor / 1 riesgos, más 5 min de preguntas | La demo de 4 min se mantiene como bloque; el pitch completo está en `08_JURY_PITCH.md`. |
| D4 | Notion | Opcional hasta que esté disponible | **[OFICIAL §5]** Condición de **admisión**: URL accesible al jurado, ≥8 tareas, ≥3 decisiones, catálogo, ≥5 fichas (≥1 con evidencia insuficiente), matriz T01–T10 y pitch desde Notion. Debe mostrar "registro durante la ejecución, no solo un resumen final" | Espejo Markdown con marcas de tiempo + historial git como prueba. La migración manual basta ("no es obligatorio automatizar la carga"). La sincronización por MCP es P2. |
| D5 | Consultas en español | Q&A en "Inteligencia generativa", sin prioridad | **[OFICIAL §2 MVP]** "Bandeja priorizada, ficha de evidencia, **consultas en español**" | Q&A con abstención pasa a **P0**. |
| D6 | Paquete TVN | Brief, título, ángulo, preguntas, guion, copy | **[OFICIAL §3]** Además: "**fuentes y verificaciones pendientes**" | Añadido a `StoryPackage.pending_verifications` + `sources`. |
| D7 | Frase obligatoria | "indicar la limitación" | **[OFICIAL §3]** Debe decir textualmente "**basado únicamente en titular/metadatos**" | Constante en código; prueba T09 la verifica. |
| D8 | Rangos y desempate | Fórmula P | **[OFICIAL §4]** bajo [0,40), medio [40,70), alto [70,100]; empate → mayor U, luego ID; mostrar versión de reglas; permitir justificar cambios de pesos | `rules_version` en contrato y desempate en el ranking. |
| D9 | Taxonomía | "topic" libre | **[OFICIAL §3]** economía, logística/Canal, turismo, servicios públicos, eventos naturales, regulación | Enum `Topic` fijo + `otro`. |
| D10 | Casos sintéticos | No mencionado | **[OFICIAL §7]** "Identificar los casos alterados como sintéticos" | Campo `sintetico`, prefijo `[SINTÉTICO]` visible y directorio `data/synthetic/` separado. |
| D11 | Benchmark | Etiquetas humanas genéricas | **[OFICIAL §7]** `benchmark.jsonl` de 60 consultas (30 sustentadas / 10 contradicción / 10 sin respuesta / 10 adversariales); 40 dev + 20 reservadas para el jurado | Lo construimos nosotros: 60 con la proporción oficial, 40 de desarrollo + 20 "reservadas" que no se usan para ajustar nada. **Nunca** mezclamos el set reservado con el corpus. |
| D12 | Archivos | 5 archivos | **[OFICIAL §6–7]** También `fuentes.json`, diccionario de datos y separación raw/processed | Añadidos al catálogo. |
| D13 | Hora | ISO 8601 | **[OFICIAL §7]** Almacenar en UTC y **mostrar hora de Panamá** en la interfaz | Regla de UI en AGENTS.md. |
| D14 | Intervalo de datos | No mencionado | **[OFICIAL §7]** Excluir registros fuera de [2024-01-01, 2025-10-01) | Filtro con registro de excluidos (T01). Ver R2. |
| D15 | Validez de sustento | "Evidence support validity" | **[OFICIAL §9.1]** Revisión humana de ≥30 afirmaciones; reportar numerador, denominador y fallos | Tarea humana explícita (B-09). |
| D16 | Ahorro de tiempo | Implícito en el pitch | **[OFICIAL §9.1]** Solo con una tarea equivalente manual vs asistida y N declarado | Mini-estudio opcional (P1); si no se hace, **no se afirma** ahorro. |
| D17 | Publicación en redes | — | **[OFICIAL Bases]** Repostear y etiquetar @hackiathon @viamatica @adenbs | Tarea no técnica H-03. |

| D18 | Cuadrícula World Bank | 1.350 filas | **[OFICIAL §6]** "6 países × 6 indicadores × 2010–2024 = 1.350 combinaciones", pero 6×6×15 = **540** (inconsistencia interna del PDF) | Se respetan las enumeraciones explícitas (países, indicadores y años): 540 filas con nulos explícitos (DL-013). |

**Sobre las fechas:** el documento TVN es el más reciente y manda. Fija el intervalo de datos y deja la
fecha del evento "por confirmar". Las Bases indican recepción el 6 de octubre, entrega el 8 de octubre a
las 23:59 y Pitch Day el 16 de octubre. Planificamos en bloques D1/D2/D3, como sugiere el doc TVN, y usamos
el **jueves 8 de octubre a las 23:59** como fecha límite. **No hay canal para consultar a la organización:** todo se resuelve con lo que dice el PDF y se documenta.

---

## 3. Ataque crítico al plan

### 3.1 Supuestos sin respaldo
1. **"Tendremos cuerpos de artículos".** Falso. [OFICIAL] Solo titulares, URL y metadatos; descripción RSS
   en TVN. La extracción de afirmaciones a partir de titulares produce afirmaciones *delgadas*: suele haber
   una por titular y casi siempre de tipo DECLARACIÓN/SOLO_REPORTADA. → La fortaleza real del producto es
   **Investigation Gap + abstención**, no la cantidad de hechos sustentados.
2. **"Podremos descargar los datos ahora".** [OFICIAL] Intervalo [2024-01-01, 2025-10-01) y "no asumir que
   el RSS conserva el histórico". Hoy es octubre de 2026: **el RSS de TVN de septiembre de 2025 ya no es
   recuperable**. [EXTERNO, corregido tras la búsqueda] La API DOC 2.0 de GDELT permite
   `STARTDATETIME`/`ENDDATETIME` desde 2017; en modo ArtList devuelve como máximo 3 meses de la ventana
   pedida (septiembre de 2025 cabe). Las noticias de TVN se obtienen con el filtro `domain:tvn-2.com`. → **Construimos nuestro propio snapshot siguiendo el PDF** (ver DL-008: estrategia del intervalo). Si el intervalo no es alcanzable para alguna fuente, se usan las fechas
   reales de extracción, documentado como desviación, o casos sintéticos claramente marcados.
3. **"Las noticias sobre sismos se vinculan con eventos USGS".** [OFICIAL] USGS cubre 2024 y las noticias
   están cerca de septiembre de 2025. Es probable que no haya coincidencia temporal. → El vínculo se hace
   solo cuando tiempo, lugar y magnitud son compatibles. Si no lo son, USGS sirve como **contexto histórico
   con advertencia temporal**, nunca como confirmación ("si no existe relación sustentada, no forzarla").
   Opcional: ampliar USGS a la ventana de las noticias como extensión documentada (AP-004).
4. **"Detectaremos contradicciones en el corpus real".** [SUPUESTO] Es poco probable encontrar conflictos
   numéricos genuinos en unos 200 titulares. → T05 se demuestra con un caso **sintético etiquetado**, y en el
   pitch no se afirma "detectamos N contradicciones reales" salvo que se midan.
5. **"Source DNA confirmará independencia".** Con metadatos, "procedencia independiente confirmada" solo es
   defendible para fuentes oficiales (USGS o World Bank frente a un medio). Entre medios, lo honesto casi
   siempre es *independencia desconocida*. Sí es detectable la *procedencia común* (titular idéntico o firma
   EFE/AFP/Reuters/AP en el titular). Eso responde directamente a la pregunta del jurado "si cinco medios
   replican la misma agencia, ¿cuántas fuentes independientes cuentas?" → **1**.
6. **"El LLM local cumple la mediana ≤15 s".** [EXTERNO, sin medir] Qwen3-8B Q4 en CPU genera unos 3–8
   tokens/s, y un paquete editorial de unas 700 tokens tarda 1,5–4 min. Con una GPU de 8 GB o más (unos
   40+ tokens/s) el tiempo cabe. → La métrica de latencia se reporta **por tarea** (Q&A frente a paquete)
   y **en hardware declarado**. Los paquetes se precalculan y Q&A usa un modelo más pequeño si hace falta.
7. **"P@5 frente a un editor".** No tenemos un editor de TVN. → Un integrante elige su top 5 **a ciegas,
   antes de ver el ranking**, y la evaluación se declara "exploratoria" [OFICIAL §9.1].
8. **"Los embeddings superan al baseline".** [SUPUESTO] En titulares cortos, TF-IDF de n-gramas de
   caracteres puede empatar. → Se mide, y si no ayuda se dice. El reto premia explicar "cuándo no ayuda la IA".

### 3.2 Funciones imposibles o de alto riesgo en el plazo
- **10 módulos como pantallas independientes**, en unas 52 h y con 3 personas → imposible con calidad.
  Se fusionan en **4 pantallas** (ver §5).
- **Sincronización automática con Notion vía MCP** → Notion aún no existe; la carga manual es válida. P2.
- **Contradicciones semánticas por LLM sobre todos los pares** → O(n²) llamadas en CPU. Solo se usan
  pares candidatos (mismo evento y mismo campo) en los eventos del top 10.

### 3.3 Riesgos de inferencia 100% local
| Riesgo | Mitigación |
|---|---|
| Sin GPU en el equipo del demo | Modo `cache`: salidas generadas antes con metadatos (modelo, prompt, hora). Modo `template`: borrador determinista a partir de afirmaciones. |
| Arranque en frío de Ollama (10–30 s) | `scripts/warmup.py` antes del pitch y `keep_alive` configurado. |
| RAM: bge-m3 (~2,3 GB) + qwen3:8b Q4 (~5–6 GB) | Embeddings precalculados y guardados; nunca se cargan junto al LLM en la demo. |
| Modo "thinking" de Qwen3 dispara la cantidad de tokens | Desactivarlo (`think=false` / `/no_think`). Medir. |
| JSON inválido | Ollama `format=<JSON schema>`, temperatura 0, validación Pydantic, 1 reintento y luego fallback `template`. |
| No determinismo | `seed` fijo y caché por hash(prompt + evidencia + modelo). |

### 3.4 Supuestos débiles de UX
- Un "Situation Room" con 200 tarjetas es ruido. Se muestran eventos, no señales, y por defecto el top 10.
- "Attention score" junto a "evidence status" puede leerse como "confianza". → La UI usa **dos ejes
  visuales distintos**: número y barra de componentes para prioridad, y una insignia textual de 3 niveles
  para evidencia. Nunca se muestran como porcentaje de verdad.
- Las etiquetas [HECHO] / [DECLARACIÓN] en cada oración pueden saturar. → Chips compactos y clic para ver
  la evidencia.

### 3.5 Afirmaciones que NO podemos hacer
- "Detectamos noticias falsas" / "verificamos la verdad".
- "X medios confirman" cuando no hay independencia demostrada.
- "Reduce el tiempo editorial en Y%" sin estudio medido.
- "La IA es mejor que el baseline" sin la tabla medida.
- "Funciona en tiempo real / monitoreo continuo" (es un snapshot por lotes).
- "Costo $0" sin matizar: el costo de **API** es $0 y el costo de hardware o electricidad se declara aparte.

### 3.6 Modos de fallo de la demo
| Fallo | Mitigación |
|---|---|
| Sin wifi en el Pitch Day | Todo corre desde el snapshot local (T10); Notion se presenta además desde PDF de respaldo (permitido como respaldo, no como sustituto). |
| El LLM en vivo tarda o falla | Botón "Generar" con fallback a caché, visiblemente etiquetado; nunca se oculta el modo. |
| La demo depende de un caso real que cambió | Se congela el snapshot y se fijan los IDs de los 5 casos del guion. |
| El jurado hace una pregunta Q&A fuera de lo ensayado | Abstención robusta por umbral de recuperación + validador numérico. |
| Proyector o resolución | La UI se prueba a 1280×720. |

### 3.7 Complejidad innecesaria
FastAPI + SPA separada, Qdrant/FAISS, PostgreSQL, microservicios y agentes múltiples dentro del producto
no suman puntos de rúbrica en un corpus de unas 300 señales. Ver CUT LIST.

---

## 4. Matriz de cobertura de rúbrica

Rúbrica oficial (100 pts, puntaje = Σ peso × nota/5). Condiciones previas (no puntúan, pero eliminan):
Notion, documentación, pitch, demo ejecutable, fuentes declaradas y sin secretos.

| Requisito / pts | Función SCAYL | Implementación | Evidencia / prueba | Dueño | Estado | Riesgo |
|---|---|---|---|---|---|---|
| **Utilidad TVN (20)** | Bandeja de eventos + Ficha de caso + Story Studio | `app/` 4 pantallas; `recommended_action` | Guion de demo CU-01..CU-04; P@5 exploratorio | Lead + A | Contrato listo | Medio: el valor es más débil con solo titulares |
| **Prototipo y flujo completo (20)** | Cargar→Organizar→Contextualizar→Priorizar→Explicar→Producir→Revisar | `python -m scayl.pipeline build` + `streamlit run app/Home.py` | T10; recorrido de punta a punta en la demo | Lead | Pendiente | Alto: integración en <52 h |
| **Uso efectivo de IA (15)** | Embeddings (agrupación, temas, recuperación) + LLM (afirmaciones, paquete, Q&A) | `scayl/intel`, `scayl/gen` | Tabla baseline frente a IA (macro-F1 de temas, B³-F1 de agrupación) | B + Lead | Pendiente | Medio: la IA puede no mejorar al baseline (se reporta igual) |
| **Evidencias y explicabilidad (15)** | Afirmaciones con evidence_id+campo, componentes de P, conflictos, abstención | `scayl/evidence`, validadores | T04, T05, T06, T08, T09; cobertura de citas al 100% | Lead | Contrato listo | Bajo |
| **Notion: ejecución y pitch (15)** | Espejo `docs/notion_mirror/` → Notion | Migración manual o MCP | ≥8 tareas, ≥3 decisiones, ≥5 fichas, matriz T01–T10, pitch | Lead + H1 | Espejo creado | **Alto: Notion no disponible aún** |
| **Calidad técnica y evaluación (10)** | Repo reproducible, pruebas, métricas | pytest, `scayl/eval`, Trust Lab | CI local verde; `eval/results/*.json` | B | Pendiente | Medio |
| **Seguridad, privacidad y ética (5)** | Fuente = dato, guard de inyección, sin secretos, derechos | `scayl/gen/guard.py`, `.env.example` | T07; `07_RISKS_AND_ETHICS.md` | Lead | Pendiente | Bajo |
| Cond.: demo sin fuente en vivo | Modo snapshot | `data/raw/v1` + manifest con SHA-256 | T10 con red desactivada | B | Pendiente | Bajo |
| Cond.: enlace del agente | App desplegada en modo snapshot | AP-001 | URL en README | A | Propuesta | Medio: derechos de redistribuir titulares |
| Cond.: PDF de herramientas IA | Bitácora continua | `docs/AI_TOOLS_USED.md` | PDF final | Todos | Creado | Bajo si se actualiza a diario |
| Métricas §9.1 | Trust Lab | `scayl/eval` | Cobertura de citas, validez (≥30 revisadas), abstención ≥80%, macro-F1, P@5, mediana y p95, tokens, costo | B | Pendiente | Medio: requiere tiempo humano de etiquetado |

---

## 5. Cambio estructural principal: 10 módulos → 4 pantallas + 1 motor

Los 10 módulos del brief se mantienen como **capacidades** del motor, pero la UI tiene 4 pantallas:

1. **Sala de Situación** (Situation Room): bandeja de eventos priorizados, matriz Prioridad × Evidencia y
   embudo "N señales → M eventos".
2. **Ficha de Caso**: una sola página con pestañas *Evento* (Event Room + línea de tiempo),
   *Fuentes* (Source DNA), *Evidencia* (Evidence Map + Conflict Lens + Temporal Guard),
   *Vacíos* (Investigation Gap), *Producir* (Story Studio) y *Revisión* (Human Review).
   Esa ficha **es** el objeto `fichas.jsonl` que pide el reto.
3. **Consultas**: Q&A en español con citas o abstención explícita.
4. **Trust Lab**: pruebas T01–T10, métricas medidas, baseline frente a IA y modelo/costo/latencia.

Motivo: el reto pide literalmente "abrir una ficha"; el jurado navega menos y el flujo de demo es lineal.

---

## 6. CUT LIST — no construir

| Función | Por qué se corta |
|---|---|
| Base vectorial (Qdrant/FAISS/Chroma) | Unos 300 vectores caben en un `numpy` en memoria; no suma rúbrica. |
| PostgreSQL | SQLite basta para revisiones y la cola de salida. |
| FastAPI + SPA (React) separada | Duplica contratos y despliegue; Streamlit sobre el núcleo Python es un solo proceso (AP-002). |
| Sincronización automática con Notion vía MCP | No es obligatoria y Notion aún no existe; queda en P2. |
| Clasificador de verdad/fake news | Prohibido por el reto. |
| Análisis de sentimiento/tono | El reto: "ni tono negativo… equivalen a verdad"; no aporta. |
| Mapa geográfico interactivo | Decorativo; basta un texto de lugar USGS. |
| Grafo animado de Source DNA | Una tabla de grupos de procedencia comunica mejor. |
| Monitoreo continuo / scheduler | [OFICIAL] "basta una carga por lote". |
| Multiagente dentro del producto | Añade latencia y opacidad; un pipeline determinista con 3 llamadas LLM es más defendible. |
| LLM para calcular puntajes | Lo calcula el código; el LLM no puntúa. |
| Fine-tuning | Sin datos ni tiempo. |
| TTS/video del guion, imágenes generadas | [OFICIAL] Fuera de alcance. |
| Autenticación/multiusuario | El revisor se identifica por nombre; basta para la trazabilidad. |
| Modalidad bancaria (SBP) | Fuera de alcance por decisión de equipo. |
| Chat con memoria conversacional | Q&A de un turno es más verificable. |

---

## 7. TOP RISKS

| # | Riesgo | Prob. | Impacto | Mitigación | Dueño |
|---|---|---|---|---|---|
| R1 | **Notion no habilitado a tiempo** → no admisión | Media | Crítico | Espejo Markdown fechado; migración manual en <1 h con plantilla lista; tener el espacio listo para migrar en cuanto se habilite la licencia | H1 |
| R2 | RSS/GDELT históricos difíciles de obtener para el intervalo oficial | Alta | Alto | DL-008: GDELT histórico (GKG con PAGE_TITLE) + sitemap TVN para septiembre de 2025, en un bloque de tiempo de 2 h; si falla, ventana reciente con desviación documentada y "cobertura efectiva" registrada | B |
| R3 | Plazo (~52 h) para el flujo completo | Alta | Alto | Rebanada delgada de punta a punta primero (M1), luego profundidad | Lead |
| R4 | Sin GPU → LLM lento | Media | Medio | Precálculo + modo caché etiquetado + modelo 4B para Q&A | B |
| R5 | Conflictos de merge en documentos compartidos | Alta | Medio | Propiedad por archivo; el tablero lo actualiza solo el Lead; los workers escriben en `docs/worklog/` | Lead |
| R6 | Citas inválidas o números alucinados en el borrador | Media | Alto (cita falsa = corrección obligatoria) | Validador post-generación: cada número del texto ∈ evidencia citada; oraciones inválidas se eliminan y se reportan | Lead |
| R7 | Derechos: redistribuir titulares/descripciones en el enlace público | Media | Medio | Despliegue con acceso restringido; solo titular + URL; descripciones solo en local | H1 |
| R8 | La IA no supera al baseline | Media | Bajo | Se reporta honestamente; puntúa en "cuándo no ayuda" | B |
| R9 | Etiquetado humano insuficiente (temas, agrupación, 30 afirmaciones, P@5) | Alta | Medio | Bloques de etiquetado agendados (H2/H3, unas 2 h en total) | B |
| R10 | Demo en vivo falla | Baja | Alto | Ensayo con red desactivada; warm-up; caché | Todos |

---

## 8. Orden de implementación

**P0 — debe funcionar (admisión + flujo completo)**
1. Contratos (hecho) · ingesta y validación con reporte de calidad (T01) · manifest con SHA-256 (T10).
2. Clasificación de temas (baseline por reglas + embeddings) · agrupación de eventos (T02, T03).
3. Puntaje P con componentes, rangos y desempate (T08) · estado de evidencia separado.
4. Evidencia: vínculo con World Bank y USGS + Temporal Guard (T04) + conflictos numéricos (T05).
5. Story Studio con validador de citas (T09) · Q&A con abstención (T06) · guard de inyección (T07).
6. Revisión humana (5 estados, SQLite, hash de evidencia).
7. UI de 4 pantallas · espejo Notion con ≥5 fichas · PDF de herramientas IA · enlace desplegado.

**P1 — ventaja competitiva**
- Source DNA con detección de agencias/titulares idénticos y conteo "máx. N independientes, 0 confirmadas".
- Trust Lab con tabla baseline frente a IA medida + latencia mediana/p95.
- Investigation Gap generado (WE KNOW / CLAIMED / INFER / DON'T KNOW / NEXT).
- Matriz Prioridad × Evidencia en la Sala de Situación.

**P2 — solo si sobra tiempo**
- Sincronización con Notion vía MCP y cola de salida automática.
- Contradicciones semánticas por LLM.
- Estudio de tiempo manual vs asistido.
- Extensión de USGS a la ventana de las noticias.

---

## 9. Decisiones internas (cerradas el 2026-10-06)

| # | Tema | Decisión |
|---|---|---|
| 1 | Intervalo de datos | DL-008: snapshot propio. Noticias de septiembre de 2025 vía GDELT DOC con `STARTDATETIME`/`ENDDATETIME`; TVN vía `domain:tvn-2.com`. |
| 2 | Benchmark | Propio: 60 consultas con la proporción oficial (40 dev + 20 reservadas). |
| 3 | Hardware | GPU de frictionspp-svg (AMD Radeon RX 9060 XT 8 GB, Vulkan; se creía RTX 4060) = máquina de demo y de precálculo; RTX 3050 = desarrollo con modelo pequeño; CPU = modo caché/plantilla (DL-006). |
| 4 | "Editor" independiente | **Humano 2**: elige el top 5 a ciegas apenas se congela el snapshot (antes de que exista ranking) y revisa ≥30 afirmaciones. Humano 3 etiqueta temas y agrupación. Humano 1 + Lead ajustan pesos. Nadie evalúa lo que ajustó (DL-010). |
| 5 | Enlace desplegado | AP-001 aceptada: Hugging Face Space con contraseña compartida en el correo de entrega; solo titular + URL. |
| 6 | Descripciones RSS | Solo en local; en el enlace público solo titular + URL. |
| 7 | Ideas 10/10 | Las 10 adoptadas + 2 surgidas de la investigación (DL-009, §10). |

---

## 10. Estado del arte: qué ya existe y cómo nos diferenciamos  [EXTERNO, búsqueda web 2026-10-06]

> Objetivo: no vender como novedad algo que ya existe. Fuentes consultadas por búsqueda; algunas páginas no
> se pudieron abrir desde el entorno cloud (se citan según el resumen del buscador).

| Capacidad | Ya existe en | Implicación para SCAYL |
|---|---|---|
| Agrupar noticias del mismo evento | **Ground News** (agrupa historias y cuenta fuentes por sesgo/propiedad), **Event Registry** (agrupación online y multilingüe de eventos) | **No** presentar la agrupación como innovación. Es infraestructura. |
| Contar el origen y no las copias (agencias) | `corroborate-mcp` (herramienta para desarrolladores: "40 copias de un cable = 1 origen"; "nunca declara verdadero, solo corroborado") | La idea existe para desarrolladores. Nuestro aporte es **integrarla en la decisión editorial** con etiquetas conservadoras ("independencia desconocida") y separada de la evidencia oficial. |
| Detección y priorización de afirmaciones verificables | **Full Fact AI** (human-in-the-loop, prioriza por daño), **Chequeabot** (Chequeado, adoptado por decenas de organizaciones de LatAm), **Newtral ClaimHunter**, **Factiverse** | Son herramientas de **fact-checking posterior**: verifican lo que otros dijeron. SCAYL actúa **antes de producir**: de la señal a una pieza investigable. No competir en "verificación". |
| Detección de tendencias | Dataminr, NewsWhip | Detectan señales pero no organizan evidencia ni producen. |
| IA local para redacciones | Investigación académica: "On-Premise AI for the Newsroom" (arXiv 2509.25494) | Respalda nuestra decisión 100% local (privacidad y costo) como dirección reconocida. |

**Hallazgo clave para el pitch:** Hagar, Agustianto y Diakopoulos, *"Not Wrong, But Untrue: LLM
Overconfidence in Document-Based Queries"* (arXiv 2509.25498). En una tarea periodística, el 30% de las
salidas de ChatGPT, Gemini y NotebookLM tuvo al menos una alucinación (40% en ChatGPT/Gemini). **La mayoría
no fueron cifras inventadas sino "sobreconfianza interpretativa": opiniones atribuidas convertidas en
afirmaciones generales.** Los autores piden "arquitecturas que impongan atribución precisa en lugar de
optimizar fluidez". → Ese es exactamente el diseño de SCAYL: tipos HECHO/DECLARACIÓN y el validador
`STATUS_MISMATCH`, que impide convertir una declaración en hecho. Lo medimos como métrica propia
(**tasa de preservación de atribución**, DL-009).

**Lo que sí podemos presentar como diferencial (combinación, no piezas sueltas):**
1. Prioridad y suficiencia de evidencia como **dos ejes separados**: "urgente, pero no publicable aún".
2. **Producción condicionada por la evidencia**: el borrador no puede afirmar como HECHO lo que no está sustentado, por construcción.
3. **Temporal Guard**: lo histórico nunca aparece como actual.
4. **Investigation Gap**: qué sabemos, qué se afirma, qué inferimos, qué no sabemos y qué preguntar.
5. **Recibo de trazabilidad** por decisión humana (hash de la evidencia).
6. **Todo medido y local**: costo de API $0, en hardware de consumo.

**Frases prohibidas en el pitch:** "primeros en agrupar noticias", "detectamos noticias falsas",
"verificamos hechos automáticamente", "N medios confirman".

Fuentes: [Reuters Institute 2026](https://reutersinstitute.politics.ox.ac.uk/news/ai-and-future-news-2026-what-we-learnt-about-its-impact-newsrooms-fact-checking-and-news) ·
[Full Fact AI](https://www.aitools-directory.com/tools/full-fact-fact-checking-tools/) ·
[Factiverse](https://www.factiverse.ai/industries/media-and-research) ·
[Chequeado/Chequeabot](https://journalismcourses.org/wp-content/uploads/2020/07/Caso_Chequeado_con_IA-6.pdf) ·
[corroborate-mcp](https://glama.ai/mcp/servers/chefcohen/corroborate-mcp) ·
[Ground News](https://apify.com/automation-lab/ground-news-bias-coverage-scraper) ·
[Event Registry](https://eventregistry.org/blog/new-to-event-registry-/) ·
[arXiv 2509.25498](https://arxiv.org/abs/2509.25498v1) · [arXiv 2509.25494](https://arxiv.org/pdf/2509.25494) ·
[GDELT DOC: búsqueda desde 2017](https://blog.gdeltproject.org/doc-2-0-updates-1-5-year-searching-and-updated-mobile-interface/)
