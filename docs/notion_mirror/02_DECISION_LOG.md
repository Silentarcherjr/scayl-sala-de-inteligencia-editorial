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
- **Candidatos:** embeddings `BAAI/bge-m3` frente a `intfloat/multilingual-e5-base`; LLM `qwen3:8b` (Q4_K_M, thinking off) frente a `qwen3:4b`.
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
