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
