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
- **Hardware del equipo:** RTX 4060 (8 GB) y RTX 3050. La 4060 es la máquina de demo y de precálculo.
- **Candidatos:** embeddings `BAAI/bge-m3`, `intfloat/multilingual-e5-base` y `Qwen/Qwen3-Embedding-0.6B`. LLM en la 4060: `qwen3.5:9b` (Apache 2.0, unos 6,6 GB en Q4 según fuentes externas) frente a `qwen3:8b`. En la 3050: `qwen3:4b` frente a Gemma 4 E4B. Fallback sin GPU: caché/plantilla.
- **Referencia externa (no medida por nosotros):** unos 25–45 tokens/s en una 4060 para modelos de 7–9B en Q4.
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
- **Decisión:** frictionspp-svg (empieza ya) toma los datos (B-01..B-07, B-11), la primera UI (A-01, A-02, A-08) y la parte semántica. LowCrime (llega más tarde) toma el resto de la UI (A-03..A-07, A-09, A-10), la evaluación (B-08, B-12), el despliegue (A-06) y el rol de editor independiente (H-08, B-09). El benchmark de modelos (B-10) lo hace quien tenga la RTX 4060.
- **Alternativas:** el reparto original por tipo (UI frente a datos).
- **Motivo:** el snapshot y una UI visible temprano desbloquean a todos y permiten probar antes; la llegada tardía de LowCrime es compatible con tareas que dependen de lo anterior. Además, que el editor llegue después ayuda a que elija el top 5 sin conocer el ranking.
- **Compromiso:** frictionspp-svg tiene más carga; `app/Home.py` es suyo y LowCrime aporta componentes. · **Fecha:** 2026-10-06
