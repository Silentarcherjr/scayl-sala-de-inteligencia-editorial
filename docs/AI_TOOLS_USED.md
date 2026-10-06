# Herramientas de IA usadas durante el desarrollo

> **Entregable oficial** (Bases §2–3): PDF con propósito, aplicación y resultados de cada herramienta IA.
> Bitácora continua; se exporta a PDF al cierre (M4). Cada integrante agrega sus entradas.

| Fecha (UTC) | Herramienta | Quién | Propósito | Aplicación concreta | Resultado | Verificación humana |
|---|---|---|---|---|---|---|
| 2026-10-06 | Claude Code (cloud), Lead | H1 + Claude | Análisis del reto y arquitectura | Lectura de los PDF oficiales, revisión crítica del brief, contratos Pydantic, plan, tareas de los workers y espejo Notion | `docs/PLAN_REVIEW.md`, `docs/ARCHITECTURE.md`, `scayl/contracts.py` + 3 pruebas en verde | Pendiente de revisión del equipo |
| 2026-10-06 | Claude Code + búsqueda web | H1 + Claude | Estado del arte y verificación técnica | Búsqueda de herramientas existentes (Ground News, Event Registry, Full Fact, Chequeabot, Factiverse, corroborate-mcp), papers (arXiv 2509.25498 y 2509.25494), capacidad histórica de GDELT DOC y modelos locales para 8 GB | PLAN_REVIEW §10, DL-006, DL-008 y DL-009 actualizados | Fuentes enlazadas; los datos de modelos se verificarán midiendo (B-10) |
| 2026-10-06 | Claude Code (cloud), Lead | H1 + Claude | Implementación del núcleo M1 | Puntaje, estado de evidencia, Source DNA, vínculo oficial, conflictos, validadores, plantilla, revisión, service y pipeline, con pruebas | 46 pruebas en verde; 2 fallos reales detectados por las pruebas y corregidos (ver 06) | Pendiente de revisión del equipo en el PR |
| 2026-10-07 | Claude Code (cloud), Lead | H1 + Claude | Implementación M2 (IA generativa) | Cliente Ollama, prompts v1, Story Studio, consultas con abstención, defensa contra inyección y pruebas con un LLM simulado | 63 pruebas en verde; 2 fallos reales más detectados y corregidos | Pendiente: validación en la RTX 4060 con el modelo real |

## Desarrollo · frictionspp-svg · B-01/B-02 · 2026-10-06

| Fecha (UTC) | Herramienta | Quién | Propósito | Aplicación concreta | Resultado | Verificación humana |
|---|---|---|---|---|---|---|
| 2026-10-06 | Codex + búsqueda web de documentación pública | frictionspp-svg | Construir adquisición reproducible y controles del snapshot | Fetchers DOC/GKG, RSS, WB y USGS; conservación de bytes; manifest SHA-256; adaptador RSS local; diccionario; pruebas sin red | 76 pruebas pasan (63 previas + 13 nuevas). Extracción parcial: 300 noticias GDELT, 540 observaciones WB, 82 eventos USGS; propuestas AP-008/AP-009 abiertas | Pendiente de decisiones de alcance y revisión del Lead; snapshot no congelado |

## Herramientas de IA dentro del producto (no son de desarrollo)

| Componente | Modelo | Uso | Costo |
|---|---|---|---|
| Embeddings | _DL-006, pendiente_ | Temas, agrupación, recuperación | $0 (local) |
| LLM | _DL-006, pendiente_ | Afirmaciones, paquete editorial, Q&A | $0 (local) |
