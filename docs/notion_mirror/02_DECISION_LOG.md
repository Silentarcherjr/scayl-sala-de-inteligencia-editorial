# 02 · Registro de decisiones

> Requisito oficial: ≥3 decisiones justificadas. Formato: decisión · alternativas · motivo · compromiso · evidencia · fecha.

### DL-001 · Modalidad editorial TVN únicamente
- **Alternativas:** editorial + bancaria; solo bancaria.
- **Motivo:** es la modalidad recomendada [OFICIAL §1]; el reto no exige dos productos; el plazo es de unas 52 h.
- **Compromiso:** renunciamos a la extensión SBP.
- **Evidencia:** doc TVN §1 "sin exigir dos productos completos". · **Fecha:** 2026-10-06

### DL-002 · Streamlit sobre núcleo Python (sin FastAPI + SPA en P0)
- **Alternativas:** FastAPI + React; FastAPI + HTMX; notebook.
- **Motivo:** una sola ruta de ejecución, despliegue gratuito, menos integración entre 3 personas; el reto acepta "interfaz web, dashboard o notebook".
- **Compromiso:** menor control visual; sin API HTTP para terceros.
- **Evidencia:** estimación de un ahorro de 8–12 h (AP-002). · **Fecha:** 2026-10-06 · **Reversible por los humanos.**

### DL-003 · 10 módulos → 4 pantallas (Sala de Situación, Ficha de Caso, Consultas, Trust Lab)
- **Alternativas:** una pantalla por módulo.
- **Motivo:** el reto pide "abrir una ficha"; la demo es lineal; el plazo.
- **Compromiso:** la Ficha de Caso concentra mucho contenido (se resuelve con pestañas). · **Fecha:** 2026-10-06

### DL-004 · Sin base de datos vectorial; numpy en memoria + embeddings precalculados
- **Alternativas:** FAISS, Qdrant, Chroma.
- **Motivo:** unos 300–600 vectores; búsqueda exacta en milisegundos; cero infraestructura; el despliegue no necesita torch.
- **Compromiso:** no escala a millones (no hace falta). · **Fecha:** 2026-10-06

### DL-005 · Generación "claim-first" con validador numérico determinista
- **Alternativas:** RAG libre con citas por párrafo; verificación con un segundo LLM.
- **Motivo:** garantiza 100% de cobertura de citas y elimina cifras inventadas por construcción; es barato en CPU.
- **Compromiso:** borradores más sobrios. · **Fecha:** 2026-10-06

### DL-006 · Modelos locales (PROVISIONAL, pendiente de B-10)
- **Hardware del equipo:** **AMD Radeon RX 9060 XT 8 GB, Vulkan** (frictionspp-svg; detectada por Ollama el 2026-10-06, se creía RTX 4060) = máquina de demo y de precálculo; RTX 3050 = desarrollo.
- **Candidatos:** embeddings `BAAI/bge-m3`, `intfloat/multilingual-e5-base` y `Qwen/Qwen3-Embedding-0.6B`. LLM en la 4060: `qwen3.5:9b` (Apache 2.0, unos 6,6 GB en Q4 según fuentes externas) frente a `qwen3:8b`. En la 3050: `qwen3:4b` frente a Gemma 4 E4B. Fallback sin GPU: caché/plantilla.
- **Referencia externa (no medida por nosotros):** unos 25–45 tokens/s en una RTX 4060 para modelos de 7–9B en Q4. **No aplica directamente**: la máquina real es AMD con Vulkan, cuyo rendimiento hay que medir (B-10).
- **Motivo:** multilingüe con buen español, licencia abierta, disponibles en Ollama/HF.
- **Evidencia:** _pendiente de medición en el hardware del equipo. No hay cifras todavía._ · **Fecha:** 2026-10-06

### DL-007 · Fechas definitivas según el doc TVN
- **Decisión:** el doc TVN (el más reciente) manda: intervalo de datos [2024-01-01, 2025-10-01). Fecha de entrega: peor caso jueves 8 de octubre a las 23:59 (Bases) hasta que se confirme.
- **Motivo:** indicación del equipo; jerarquía de autoridad. · **Fecha:** 2026-10-06

### DL-008 · Snapshot propio y estrategia del intervalo de fechas
- **Decisión:** no existe paquete común disponible ni canal de consulta → construimos el snapshot siguiendo el PDF §6–7. Para las noticias se intenta primero el intervalo oficial [2024-01-01, 2025-10-01) (30 días previos a 2025-10-01; GDELT GKG histórico + sitemap TVN). Si en 2 h no hay ≥100 registros (≥20 TVN), se usa la ventana reciente y se documenta la desviación.
- **Alternativas:** solo ventana reciente (más simple, pero viola literalmente el intervalo); solo intervalo oficial (riesgo de volumen insuficiente).
- **Motivo:** el PDF prioriza el intervalo y también dice "registrar la cobertura efectiva"; documentar la desviación es más honesto que forzar los datos.
- **Compromiso:** con la ventana reciente, WB (≤2024) y USGS (2024) quedan aún más lejos en el tiempo → el Temporal Guard gana protagonismo (y eso es bueno para T04).
- **Fecha:** 2026-10-06 · **Estado:** propuesta del Lead, validar en equipo.

**Actualización DL-008 (2026-10-06):** la investigación indica que la API DOC de GDELT acepta `STARTDATETIME`/`ENDDATETIME` desde 2017. Con eso, septiembre de 2025 es alcanzable directamente y TVN se obtiene con `domain:tvn-2.com`. El plan GKG queda solo como respaldo. **Aprobada por el equipo.**

### DL-009 · Adoptar las 10 ideas "10/10" + 2 surgidas de la investigación
- **Decisión:** Agenda de la mañana, mini-estudio manual vs asistido, tarjeta de evidencia al hacer clic, simulador de pesos, tabla baseline vs IA con "dónde no ayudó", video offline, registro de prueba fallida → corrección, CI en GitHub Actions, set de 10 ataques y modo jurado. Más: **recibo de trazabilidad** y **métrica de preservación de atribución**.
- **Alternativas:** solo el MVP.
- **Motivo:** cada idea corresponde a un criterio "5 = excepcional y verificado" de la rúbrica o a una prueba dinámica del jurado. La investigación de mercado mostró que la agrupación y el conteo de orígenes ya existen (Ground News, Event Registry, corroborate-mcp). El diferencial debe ser la **producción condicionada por la evidencia con atribución obligatoria**, que responde a un problema documentado en arXiv 2509.25498.
- **Compromiso:** más alcance. Por eso la mayoría queda en P1, detrás del flujo P0.
- **Fecha:** 2026-10-06 · **Aprobada por el equipo.**

### DL-010 · Separación de roles en la evaluación
- **Decisión:** Humano 2 actúa como "editor" (top 5 a ciegas antes de que exista ranking y revisión de ≥30 afirmaciones). Humano 3 etiqueta temas y agrupación. Humano 1 + Lead ajustan pesos y umbrales.
- **Motivo:** quien ajusta el sistema no debe evaluarlo (evita fuga de información en P@5 y en la validez de sustento).
- **Compromiso:** el editor no es un periodista de TVN → P@5 se declara exploratoria. · **Fecha:** 2026-10-06

### DL-011 · Asignación de personas: frictionspp-svg carga el camino crítico
- **Decisión:** frictionspp-svg (empieza ya) toma los datos (B-01..B-07, B-11), la primera UI (A-01, A-02, A-08) y la parte semántica. LowCrime (llega más tarde) toma el resto de la UI (A-03..A-07, A-09, A-10), la evaluación (B-08, B-12), el despliegue (A-06) y el rol de editor independiente (H-08, B-09). El benchmark de modelos (B-10) lo hace frictionspp-svg, que tiene la RTX 4060.
- **Alternativas:** el reparto original por tipo (UI frente a datos).
- **Motivo:** el snapshot y una UI visible temprano desbloquean a todos y permiten probar antes; la llegada tardía de LowCrime es compatible con tareas que dependen de lo anterior. Además, que el editor llegue después ayuda a que elija el top 5 sin conocer el ranking.
- **Compromiso:** frictionspp-svg tiene más carga; `app/Home.py` es suyo y LowCrime aporta componentes. · **Fecha:** 2026-10-06

### DL-012 · Contrato 0.2.0 y diseño de generación/consultas (M2)
- **Decisión:** (a) contrato 0.2.0, aditivo: `Event.security_flags` y `UIBundle.news/indicators/seismic` (la Sala de Eventos necesita los titulares de cada evento y las consultas necesitan todas las filas del Banco Mundial). (b) Cliente Ollama por HTTP (`requests`), sin dependencia nueva; caché direccionada por contenido; modos live/cache/template. (c) Consultas: prefiltro determinista (cobertura de términos ≥0,6; año pedido presente; valor nulo ⇒ abstención) antes de llamar al LLM; las respuestas pasan por los mismos validadores que el Story Studio; sin modelo, modo extractivo etiquetado. (d) Afirmaciones extraídas por LLM: siempre DECLARACION/SOLO_REPORTADA atribuida al medio.
- **Alternativas:** cliente `ollama` de Python; recuperación densa para la abstención; que el LLM decida solo cuándo abstenerse.
- **Motivo:** la abstención determinista es verificable y no depende del modelo; menos dependencias; los mismos validadores en todos los textos generados.
- **Compromiso:** el umbral 0,6 es heurístico. B-08 debe medir la tasa de abstención correcta e incorrecta y ajustarlo con el benchmark de desarrollo, nunca con el reservado.
- **Fecha:** 2026-10-06

### DL-013 · Cuadrícula del Banco Mundial: 540 filas (resuelve AP-008)
- **Decisión:** ACEPTADA. Se usan exactamente los 6 países, 6 indicadores y 15 años (2010–2024) que enumera el PDF, es decir 540 combinaciones con nulos explícitos.
- **Alternativas:** inventar dimensiones para llegar a 1.350.
- **Motivo:** el PDF es internamente inconsistente (6×6×15 = 540); entre un total y una enumeración explícita gana la enumeración, y no se inventan datos. Discrepancia D18 en PLAN_REVIEW.
- **Fecha:** 2026-10-07 · Propuesta por frictionspp-svg.

### DL-014 · Usar las 48 entradas históricas del RSS de TVN (resuelve AP-009), con condiciones
- **Decisión:** ACEPTADA con condiciones: (1) solo entradas con `pubDate` dentro de [2024-01-01, 2025-10-01); (2) `origen=tvn_rss`, `fecha_publicacion` = pubDate original; (3) **`fecha_deteccion` = null**: el RSS no aporta una señal de detección y la descarga de 2026 queda en `fecha_extraccion`; así no se marcan falsamente como "recirculadas"; (4) `alcance_texto=titular_metadatos` (las descripciones no entran al corpus publicado); (5) el catálogo declara la cobertura real de TVN (2024-01 a 2025-09, solo 3 en septiembre de 2025) y que la fecha proviene del RSS, sin verificar contra el artículo.
- **Alternativas:** solo septiembre de 2025 (3 registros, por debajo del mínimo oficial de 20); ventana reciente de 2026 (fuera del intervalo oficial).
- **Motivo:** son datos reales del patrocinador, con fecha original y dentro del intervalo oficial; cumplen el mínimo de ≥20 registros de TVN sin fabricar fechas.
- **Compromiso:** la mayoría de las noticias de TVN son antiguas respecto al corte, por lo que tendrán urgencia baja. Es lo correcto: el puntaje lo refleja con honestidad.
- **Fecha:** 2026-10-07 · Propuesta por frictionspp-svg.

### DL-015 · Urgencia de noticias GDELT sin fecha de publicación
- **Decisión:** GDELT solo aporta la detección (seendate); la publicación queda **nula**, como manda el contrato. Para la urgencia (U), y solo si no existe ninguna fecha de publicación en el evento, se usa la detección más reciente como **aproximación explícita** ("Fecha de publicación desconocida; aproximación por detección") en la justificación del componente. Nunca se muestra ni se guarda como fecha de publicación.
- **Motivo:** sin esto, todos los eventos solo-GDELT tenían U=0 y el ranking quedaba distorsionado (hallazgo al revisar el snapshot de frictionspp-svg).
- **Fecha:** 2026-10-07

### DL-016 · Evaluación de la agrupación por pool de pares candidatos
- **Decisión:** las etiquetas de agrupación (B-07) se toman sobre un pool de pares: todos los pares que proponen el baseline o la IA, más pares difíciles (mismo día y palabra clave, no agrupados) y un control al azar. El etiquetado es ciego al método. Se reportan precisión, **recall relativo** al pool y F1 por método.
- **Alternativas:** muestra aleatoria de noticias (casi no produce pares del mismo evento: métrica vacía); etiquetar todos los pares (O(n²), inviable).
- **Motivo:** es la práctica estándar de evaluación por *pooling*. Da una comparación baseline frente a IA con datos reales y declara sus límites con honestidad.
- **Compromiso:** el recall es relativo, no absoluto; se declara así en el Trust Lab.
- **Fecha:** 2026-10-07

### DL-017 · Ventana de noticias según aclaración oficial C-01 (supera DL-007, DL-008 y DL-014)
- **Decisión:** las noticias van en **[2025-10-02, 2026-10-01)**, con corte del snapshot el **2026-10-01T00:00:00Z** (objetivo: 30 días previos al corte, ampliable a 90). World Bank 2010–2024 y USGS 2024 se mantienen como contexto histórico. **AP-004 aceptada:** USGS ampliado a la ventana de noticias en un archivo separado. Las 48 entradas históricas de TVN (DL-014) quedan fuera; se usan las entradas del RSS dentro de la ventana nueva. Las fechas se centralizan en `scayl/config/data_window.v1.yaml`.
- **Origen:** aclaración de la organizadora en el grupo oficial (2026-10-07), registrada en `docs/official_clarifications.md` (C-01) con captura como evidencia.
- **Alternativas:** mantener el intervalo del §7 (contradice a la organización y al §6-A, "30 días previos a la extracción").
- **Motivo:** jerarquía de autoridad: una aclaración oficial posterior prevalece sobre el PDF. Además, resuelve la contradicción §6-A/§7 que marcamos el día 1 (PLAN_REVIEW D14/D19).
- **Compromiso:** hay que volver a descargar las noticias. Los fetchers, el manifest y las pruebas de frictionspp-svg se reutilizan sin cambios; las respuestas de 2025 ya descargadas se conservan (raw inmutable) y quedan fuera del corpus con motivo registrado. La distancia temporal entre noticias de 2026 y datos WB de 2024 refuerza la demostración del Temporal Guard (T04).
- **Fecha:** 2026-10-07

### DL-018 · Conjunto de desarrollo con datos de 2025; demo solo con datos recientes (aclaración C-02)
- **Decisión:** las descargas fuera de la ventana C-01 (GDELT de septiembre de 2025 y las 48 entradas históricas del RSS de TVN) se conservan como **conjunto de desarrollo**: ajuste de umbrales (agrupación τ, abstención θ), pruebas de etiquetado y del benchmark de desarrollo. La **evaluación reportada** y la **demo** usan solo el corpus de la ventana [2025-10-02, 2026-10-01).
- **Alternativas:** descartar esos datos; o mezclarlos con el corpus de la demo (lo prohíbe C-02 para la demo).
- **Motivo:** aprovecha trabajo ya hecho y evita ajustar con los mismos datos que se evalúan y se muestran, lo cual es más defendible ante el jurado.
- **Compromiso:** el desarrollo y la demo tienen distribuciones temporales distintas; las métricas se reportan sobre 2026.
- **Fecha:** 2026-10-07

### DL-019 · Evidencia oficial reciente: ACP e INEC (AP-010 aceptada por el equipo)
- **Decisión:** se agregan el nivel del lago Gatún (ACP, CSV) y el IPC mensual (INEC, PDF) como evidencia oficial reciente. Contrato 0.3.0 (aditivo): `IndicatorObservation.periodo/fuente/frecuencia/es_proyeccion`. Un titular queda SUSTENTADO solo con coincidencia numérica **y** temporal; si no, el dato oficial es contexto citado con su fecha. Las proyecciones nunca son hechos.
- **Alternativas:** solo WB 2024 (sin evidencia reciente: casi ningún evento sería "suficiente"); fuentes más amplias (sin tiempo).
- **Motivo:** la aclaración C-02 permite fuentes adicionales y exige datos recientes en la demo; mejora Evidencias (15) y Utilidad (20).
- **Compromiso:** la extracción del PDF del INEC puede ser frágil (mitigación: pocas filas, cuadro y página citados, verificación humana); la coincidencia numérica puede ser casual, por eso la afirmación pide "verificar que sea la misma medida".
- **Fecha:** 2026-10-07 · Aprobada por el equipo.

### DL-020 · AP-011 aceptada y reasignación de la UI a LowCrime
- **Decisión:** (1) `service.review(..., package=...)` registra el paquete que el revisor está viendo (id + sha256 en el recibo) y `service.receipt(review_id)` expone el recibo. (2) LowCrime, ya activo, toma A-01, A-02 y A-08; frictionspp-svg queda con datos (B-01, B-13, B-14, B-03..B-07, B-10, B-11).
- **Alternativas:** mantener la UI inicial en frictionspp-svg (que además tiene el snapshot y dos fuentes nuevas); dejar la revisión atada solo al paquete del snapshot.
- **Motivo:** el cuello de botella era frictionspp-svg; la tarjeta A-08 bloqueaba A-03. Revisar contenido distinto del mostrado rompería la trazabilidad (hallazgo de LowCrime).
- **Fecha:** 2026-10-07

### DL-021 · El Lead toma A-05 (vista del Trust Lab) y A-10 (simulador de pesos)
- **Decisión:** para liberar a LowCrime (Sala de Situación, Agenda, Consultas y despliegue), el Lead implementa la vista del Trust Lab y el simulador de pesos. LowCrime conserva B-08 (evaluación), que escribe `eval/results/latest.json`.
- **Detalle:** el Trust Lab muestra solo resultados medidos, con numerador y denominador, y "no medido" en lo demás; además resume `generation_report.jsonl` (cobertura de citas, eliminaciones por validador, preservación de atribución, latencia y tokens). El simulador re-rankea sin tocar el ranking oficial y exige autor y justificación para registrar el cambio (`data/state/weight_changes.jsonl` + cola de Notion), como pide el PDF §4.
- **Hallazgo:** Streamlit envía telemetría de uso a internet por defecto; se desactiva en `.streamlit/config.toml` (demo offline y privacidad).
- **Fecha:** 2026-10-07

### DL-022 · B-03 (`load_snapshot`) sube antes que ACP/INEC
- **Decisión:** después de congelar el snapshot, frictionspp-svg hace primero B-03 (validación y carga) y luego B-13/B-14.
- **Motivo:** sin `load_snapshot` el pipeline no corre con datos reales, y eso bloquea el hito M1, la prueba en la GPU, el top 5 a ciegas y la evaluación. ACP e INEC suman evidencia, pero no bloquean el flujo.
- **Fecha:** 2026-10-07

### DL-023 · El Lead implementa B-03 y el baseline de B-05; primera corrida con datos reales
- **Decisión:** frictionspp-svg se quedó sin sesión con el snapshot congelado; B-03 (`load_snapshot`) y el baseline de B-05 (temas por reglas + agrupación TF-IDF) los implementa el Lead para desbloquear M1. frictionspp-svg conserva la variante IA (embeddings), la calibración con el conjunto de desarrollo, las etiquetas, el benchmark, ACP e INEC.
- **Resultado medido (snapshot C-01):** 187 señales → 187 válidas (0 excluidas; 131 códigos de idioma normalizados) → 183 eventos; 3 alto, 59 medio, 121 bajo; 144 con evidencia insuficiente, 39 parcial, **0 suficiente**. Sin ACP/INEC no hay confirmación oficial reciente (confirma la necesidad de AP-010).
- **Hallazgos en datos reales** (corregidos, ver 06): (1) un titular que **negaba** un sismo quedó "confirmado" por USGS; (2) una diferencia de magnitud 4.7 vs 4.5 se absorbía sin mostrarse.
- **Salvaguarda P@5:** `data/processed/*/` no se sube a `main` hasta que exista el top 5 ciego (H-08).
- **Fecha:** 2026-10-07

### DL-024 · Top 5 del editor aceptado con limitación declarada; P@5 preliminar
- **Decisión:** se acepta la selección de LowCrime (PR #23) como referencia de P@5, que sigue siendo **exploratoria**. En la entrega se declara que el editor vio antes una propuesta generada por IA (coincide con su elección en 1 de 5) y que **no** vio el ranking del sistema ni la app con datos reales. No se presenta como selección independiente sin asistencia.
- **Resultado preliminar (baseline TF-IDF + reglas, sin ACP/INEC):** P@5 = 1/5. Posiciones de los elegidos: 2, 6, 12, 22 y 26 de 183 eventos. B-08 (LowCrime) la recalcula con el pipeline final.
- **Lectura:** 3 de los 5 elegidos tratan El Niño en el Canal, pero quedan como eventos separados (EVT-0088, EVT-0096, EVT-0158, y además EVT-0127, que no fue elegido). La agrupación TF-IDF no une titulares con redacción distinta ni en otro idioma. La variante con embeddings (B-05 IA) es la mejora prevista y se mide contra este baseline. **No se ajustan pesos para "acertar" el top 5** (sería sobreajuste a 5 etiquetas).
- **`data/processed/`:** sigue fuera de git. El bundle completo incluye descripciones de RSS (derechos), así que cada máquina lo regenera con `make demo`; la versión pública solo se genera con `--public`.
- **Fecha:** 2026-10-07

### DL-025 · B-05 IA aceptada (E5 multilingüe); se corrige la lectura de DL-024
- **Decisión:** se mergea PR #28 (frictionspp-svg): embeddings `intfloat/multilingual-e5-base` locales (sin descargas en tiempo de ejecución) y temas por prototipos de la taxonomía oficial. τ = 0,87 elegido **solo** con 488 pares de desarrollo 2025; el calibrador rechaza datos C-01 y no lee el top 5.
- **Resultado medido (C-01):** 183 eventos (TF-IDF) → 165 (E5). P@5 exploratoria 1/5 → 1/5, reportada sin ajustar nada.
- **Corrección a DL-024:** los 4 titulares de El Niño en el Canal tienen fechas 17/07, 15/08, 05/09 y 15/09/2026. Son **desarrollos distintos de una misma historia**, no duplicados: la regla de 7 días los separa correctamente. La lectura "fallo de agrupación" de DL-024 era incorrecta. Además, el par en francés tiene coseno menor que τ.
- **Limitación declarada:** los pares de desarrollo fueron anotados por un agente (Codex), no son gold humano. La revisión humana queda en B-07; hasta entonces F1 de agrupación se reporta como "calibración sobre etiquetas provisionales", no como métrica de evaluación.
- **Robustez (Lead):** el pipeline solo usa IA si el modelo local carga de verdad. Si falta el paquete o los pesos, cae al baseline TF-IDF con aviso (`select_embedder`, 2 pruebas nuevas).
- **Fecha:** 2026-10-07

### DL-026 · Evidencia oficial reciente integrada; AP-012 aceptada; 0 "suficiente" es un resultado honesto
- **Decisión:** se mergea PR #31 (frictionspp-svg): 394 niveles diarios de Gatún (ACP) y 24 variaciones del IPC (INEC, CC BY 4.0) como adición declarada v1.1 del snapshot. Se conservan los bytes previos y el manifest padre. La proyección ACP anterior al corte **no existe** en la fuente: queda nula, no se inventa.
- **AP-012 aceptada** y ampliada por el Lead en `recent.py`:
  1. palabras genéricas (restricción, agua, calado, El Niño) solo cuentan junto a "Canal";
  2. una cifra confirma el nivel de Gatún solo si el titular nombra esa medida, y nunca si la cifra es un calado (misma unidad, otra medida);
  3. **fallo propio corregido:** el contexto usaba el último dato antes del corte, no antes del evento. Un titular de julio recibía el nivel del 30/09.
- **Por qué sigue habiendo 0 eventos "suficiente":** ningún titular del corpus C-01 menciona una cifra del nivel de Gatún ni del IPC. Sin una cifra que comparar no hay confirmación, solo contexto. No se relajan las reglas para fabricar "suficientes": en el pitch se presenta como abstención correcta. Los casos "suficiente" se muestran con el fixture SINTÉTICO, etiquetado.
- **Precálculo medido (B-10 parcial):** qwen3:8b en AMD RX 9060 XT (Vulkan), 15/15 en vivo, 0 de respaldo. Mediana 15,1 s, p95 17,8 s (n = 15); la meta orientativa de ≤15 s se supera por 0,1 s, se reporta tal cual. Cobertura de citas 49/49 oraciones conservadas; el validador eliminó 5 (3 STATUS_MISMATCH, 2 UNCITED_FACT). Costo de API $0.
- **Consecuencia:** cambian afirmaciones de contexto, así que el caché LLM de esos eventos debe regenerarse (`make precompute` otra vez en la GPU).
- **Fecha:** 2026-10-07

### DL-027 · Red-team B-12: fallos reales en Consultas corregidos (AP-013)
- **Hallazgo (LowCrime, PR #32):** con 16 ataques sintéticos, la abstención correcta era **6/16**. Fallos:
  - el modo sin modelo **citaba textualmente** titulares con inyección (RT01–04);
  - no había abstención ante cifras falsas en la pregunta (RT05–06);
  - devolvía filas históricas cuando se pedía un dato "actual / hoy / este año" (RT09–11);
  - aceptaba un año porque coincidía con la fecha de un titular ajeno (RT12).
- **Corrección (Lead, `scayl/gen/qa.py`) con reglas generales, no específicas del set:**
  1. las fuentes marcadas como posible inyección se recuperan solo para explicar la abstención; nunca se citan ni se envían al modelo;
  2. el modo extractivo pasa por el mismo validador (`check_sentence`) que el modelo;
  3. guardia de premisa falsa: si una cifra de la pregunta no está en la evidencia pertinente, el sistema se abstiene (las fechas no cuentan como cifras);
  4. guardia de actualidad: con solo datos históricos, abstención; con series recientes (ACP/INEC), se responde con la más reciente **y su período**;
  5. el año pedido debe pertenecer a una unidad que trate el tema;
  6. fechas en español → ISO ("28 de septiembre de 2026" → 2026-09-28), y "hoy/actual" no se usan como términos de búsqueda.
- **Resultado medido:** abstención correcta 16/16; abstención incorrecta 0/4; controles 4/4; sondas del validador 9/9; 172 pruebas.
- **Limitación declarada (sobreajuste):** la corrección se hizo después de ver el set, que fue escrito por un agente IA. Mitigación: reglas generales; 7 regresiones nuevas redactadas de otra forma; verificación manual con datos reales (preguntas "actual" responden con INEC 2026-08 y Gatún 2026-09-30, con su fecha). **Pendiente: un set reservado nuevo**, escrito por alguien que no haya visto el código, para medir sin sesgo.
- **Fecha:** 2026-10-07

### DL-028 · Integración del backlog final (PR #37–#49); modelo de demo: qwen3:8b
- **Integrado:** precompute repetido (#37), caché pública revisada (#38), CI (#39), preparación de B-07 (#40), B-08 con métricas importadas (#41), AP-014 (#42), preparación de B-09 (#43), Space preparado (#44), protocolo H-06 (#45), capturas finales (#46), pulido de UI (#47), benchmark B-10 (#48) y casos sintéticos B-04 (#49). 184 pruebas; `ruff check .` en verde.
- **Modelo para la demo: qwen3:8b.** Medido en el top 15 (n = 15, una corrida por modelo, AMD RX 9060 XT Vulkan): 8b, mediana 14,6 s, p95 17,6 s, citas 49/49, 0 respaldos; 4b, mediana 9,1 s, p95 12,9 s, citas 25/25, pero 3 paquetes vacíos (EMPTY_BRIEF) tras validar. Se prefiere calidad estable a velocidad.
- **AP-014 aceptada:** el Trust Lab muestra red-team (num/den, fallos, alcance sintético), la limitación de P@5 (DL-024) y el hardware y el archivo de origen de cada métrica importada.
- **Limpieza de lint (Lead):** 44 avisos de estilo de ruff en `scayl/` resueltos sin cambiar comportamiento (orden de imports, `datetime.UTC`, literales). Dos excepciones justificadas con `noqa`.
- **Pendiente humano (no se inventa):** B-07 (100 temas + 32 titulares), B-09 (30 afirmaciones), H-06 (tiempos) y set reservado de red-team v2. Mientras falten, sus métricas siguen "no medido".
- **Fecha:** 2026-10-07

### DL-029 · Temas por reglas, agrupación por E5: decisión por medición humana
- **Medición (B-07):** 100 titulares C-01 etiquetados por un humano del equipo (después de ver la propuesta de la IA). Macro-F1 de temas: **reglas 0,76 frente a prototipos E5 0,25**. Que el humano viera antes la propuesta IA no la favoreció.
- **Decisión:** el pipeline separa temas y agrupación. Temas por **reglas** por defecto (`SCAYL_TOPICS=baseline`); agrupación con **E5** cuando el modelo local carga (`SCAYL_INTEL=ai`, 183 → 165 eventos). No se reentrena ni se ajusta nada con estas 100 etiquetas.
- **Para el pitch:** usamos IA donde mide mejor y reglas donde la IA perdió. Es una decisión por evidencia, no por moda.
- **Consecuencia:** al cambiar los temas cambia el componente I de la prioridad y con él el ranking. La caché LLM del top 15 y la caché pública deben regenerarse (frictionspp-svg: `make precompute` + caché pública). P@5 y B-08 se recalculan después.
- **Fecha:** 2026-10-07

### DL-030 · B-07 y set reservado humano (red-team v2) integrados
- **B-07 (frictionspp-svg, humano):**
  - temas, macro-F1 con n = 100: reglas 0,757 frente a E5 0,246;
  - agrupación, pares de desarrollo revisados por humano: TF-IDF F1 0,44 (P 12/12, R 12/43) frente a E5 F1 0,99 (P 42/42, R 42/43).
  - Confirma DL-029: reglas para temas, E5 para agrupar.
  - **Limitación:** los pares de agrupación son el conjunto de desarrollo usado para calibrar τ, así que el F1 es optimista y no es una evaluación ciega.
- **Set reservado v2 (10 preguntas escritas por un humano sin ver el código):** 6/6 trampas con abstención correcta. Las 4 preguntas esperadas como "respondibles" eran de cultura general (moneda, año de inauguración del Canal, provincia más grande, presidente que inauguró el Canal) y **no están en el corpus** (verificado: 0 coincidencias). SCAYL responde solo con evidencia citada, no de memoria, así que la abstención es el comportamiento diseñado. Se reportan ambas lecturas sin reescribir las expectativas humanas: 6/10 según las expectativas del autor; 10/10 con el criterio "solo con evidencia del corpus".
- **Para el pitch:** "no responde de memoria" es una garantía, no una carencia; se muestra con HV2-07 ("¿Cuál es la moneda oficial de Panamá?" → abstención con la información que faltaría).
- **Fecha:** 2026-10-07

### DL-031 · B-09: validez de sustento 25/30, reportada sin retocar
- **Resultado (LowCrime, humano):** 25 sí, 2 parcial y 3 no sobre 30 afirmaciones de paquetes template: **83%**, por debajo de la meta orientativa (≥90%).
- **Revisión del Lead (sin cambiar etiquetas):** los 5 casos no "sí" (SR04, SR05, SR10, SR19, SR25) son frases "Según <medio>: <titular>" cuya evidencia es ese mismo titular, palabra por palabra. Dos están en otro idioma (portugués; inglés con maratí) y uno es un caso judicial ajeno a Panamá. Lo más probable es que el revisor juzgara relevancia o veracidad, no sustento. Es un hallazgo de producto: **la cita textual de un titular irrelevante o en otro idioma no le sirve al editor aunque esté "respaldada"**. Siguiente paso fuera de alcance: filtrar por relevancia para Panamá e idioma antes de producir.
- **No se re-etiqueta** después de ver el resultado (sería sesgo). En la entrega se reporta 25/30 con esta lectura.
- **Evaluación final consolidada:** `eval/results/latest.json` integra citas 45/45, validez 25/30, red-team 16/16, temas (0,76 / 0,25), agrupación (0,44 / 0,99), P@5 1/5 y latencia 13,1 / 17,0 s. Siguen "no medido": tokens, preservación de atribución y latencia de Consultas.
- **Fecha:** 2026-10-07

### DL-032 · Publicación en Streamlit Community Cloud (HF Docker exige pago)
- **Hecho:** al crear el Space, Hugging Face respondió `402 Payment Required`: los Spaces Docker o Gradio en CPU gratuita requieren PRO. No se creó nada.
- **Decisión:** no pagar (regla: sin costos sin aprobación) y publicar en **Streamlit Community Cloud** (gratis), con el mismo stage auditado, desde un repositorio GitHub dedicado que contiene solo el stage. La contraseña va en *Secrets*, que la plataforma expone como variable de entorno: el mismo control de acceso de A-06.
- **Cambio técnico:** `deploy/space.py` se autoconfigura (stage en `sys.path`, modo cache y rutas por defecto) porque esa plataforma no usa el Dockerfile. Con Docker no cambia nada: los valores del entorno tienen prioridad. Verificado en local sin `PYTHONPATH` y con solo la contraseña.
- **Fecha:** 2026-10-08
- **Actualización 2026-10-08 · A-06 DESPLEGADA:** https://scayl-demo.streamlit.app/ (Streamlit Community Cloud, Python 3.12, modo cache, contraseña solo en Secrets y entregada por canal privado).
  - **Código:** repo público `Silentarcherjr/scayl-demo` (`main` = `f4c7de1`), que contiene solo el stage `deploy/stage-cloud` generado desde `ff3a7c2`: los 118 archivos inventariados en `PREPARATION.json` más ese archivo, con hashes verificados.
  - **Verificación:** en local, sin contraseña no entra, la incorrecta se rechaza y con la correcta cargan Sala, Ficha, Consultas y Trust Lab. En remoto, `/` y `/Trust_Lab` piden contraseña y la incorrecta se rechaza; el Humano 1 confirmó el recorrido autenticado. URL registrada por el PR #61.
  - **Lección:** las pruebas locales dejan `__pycache__/` y `data/state/reviews.sqlite` dentro del stage, así que para publicar se copia solo lo inventariado.
  - **Regla:** `scayl-demo` no se edita a mano. Si cambian código o datos de la demo, se regenera el stage en una carpeta nueva, se prueba y se republica desde la sesión local del Humano 1.
