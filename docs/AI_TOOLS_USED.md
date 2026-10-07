# Herramientas de IA usadas durante el desarrollo

> **Entregable oficial** (Bases §2–3): PDF con propósito, aplicación y resultados de cada herramienta IA.
> Bitácora continua; se exporta a PDF al cierre (M4). Cada integrante agrega sus entradas.

| Fecha (UTC) | Herramienta | Quién | Propósito | Aplicación concreta | Resultado | Verificación humana |
|---|---|---|---|---|---|---|
| 2026-10-06 | Claude Code (cloud), Lead | H1 + Claude | Análisis del reto y arquitectura | Lectura de los PDF oficiales, revisión crítica del brief, contratos Pydantic, plan, tareas de los workers y espejo Notion | `docs/PLAN_REVIEW.md`, `docs/ARCHITECTURE.md`, `scayl/contracts.py` + 3 pruebas en verde | Pendiente de revisión del equipo |
| 2026-10-06 | Claude Code + búsqueda web | H1 + Claude | Estado del arte y verificación técnica | Búsqueda de herramientas existentes (Ground News, Event Registry, Full Fact, Chequeabot, Factiverse, corroborate-mcp), papers (arXiv 2509.25498 y 2509.25494), capacidad histórica de GDELT DOC y modelos locales para 8 GB | PLAN_REVIEW §10, DL-006, DL-008 y DL-009 actualizados | Fuentes enlazadas; los datos de modelos se verificarán midiendo (B-10) |
| 2026-10-06 | Claude Code (cloud), Lead | H1 + Claude | Implementación del núcleo M1 | Puntaje, estado de evidencia, Source DNA, vínculo oficial, conflictos, validadores, plantilla, revisión, service y pipeline, con pruebas | 46 pruebas en verde; 2 fallos reales detectados por las pruebas y corregidos (ver 06) | Pendiente de revisión del equipo en el PR |
| 2026-10-07 | Claude Code (cloud), Lead | H1 + Claude | Implementación M2 (IA generativa) | Cliente Ollama, prompts v1, Story Studio, consultas con abstención, defensa contra inyección y pruebas con un LLM simulado | 63 pruebas en verde; 2 fallos reales más detectados y corregidos | Pendiente: validación en la RTX 4060 con el modelo real |

| 2026-10-07 | Codex | LowCrime | A-03: ficha de caso | Revisión y continuación de la página local, validación de revisiones, 9 pruebas AppTest y propuesta AP-011 para dependencias pendientes | 80 pruebas en verde; seis pestañas con fixture sintético; tarjeta A-08 y API de recibo pendientes | Pendiente de revisión del Lead en PR borrador |
| 2026-10-07 | Codex | LowCrime | Completar A-03/A-08 tras DL-020 | Tarjeta compartida, revisión del paquete visible, recibo descargable, AppTest y validación visual en Chromium con fixture sintético | 84 pruebas en verde; capturas a 1280×720; AP-011 aplicada | Pendiente de revisión final del Lead en PR #13 |
| 2026-10-07 | Claude Code (cloud), Lead | H1 + Claude | UI: Trust Lab y simulador de pesos | Páginas Streamlit, funciones de servicio, 5 AppTest y capturas con Chromium headless | 89 pruebas en verde; detectada y desactivada la telemetría de Streamlit | Capturas en docs/screenshots/a05, a10 |

## Herramientas de IA dentro del producto (no son de desarrollo)
| Componente | Modelo | Uso | Costo |
|---|---|---|---|
| Embeddings | _DL-006, pendiente_ | Temas, agrupación, recuperación | $0 (local) |
| LLM | _DL-006, pendiente_ | Afirmaciones, paquete editorial, Q&A | $0 (local) |
