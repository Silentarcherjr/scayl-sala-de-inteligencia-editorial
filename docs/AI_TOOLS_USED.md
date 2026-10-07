# Herramientas de IA usadas durante el desarrollo

> **Entregable oficial** (Bases §2–3): PDF con propósito, aplicación y resultados de cada herramienta IA.
> Bitácora continua; se exporta a PDF al cierre (M4). Cada integrante agrega sus entradas.

| Fecha (UTC) | Herramienta | Quién | Propósito | Aplicación concreta | Resultado | Verificación humana |
|---|---|---|---|---|---|---|
| 2026-10-06 | Claude Code (cloud), Lead | H1 + Claude | Análisis del reto y arquitectura | Lectura de los PDF oficiales, revisión crítica del brief, contratos Pydantic, plan, tareas de los workers y espejo Notion | `docs/PLAN_REVIEW.md`, `docs/ARCHITECTURE.md`, `scayl/contracts.py` + 3 pruebas en verde | Pendiente de revisión del equipo |
| 2026-10-06 | Claude Code + búsqueda web | H1 + Claude | Estado del arte y verificación técnica | Búsqueda de herramientas existentes (Ground News, Event Registry, Full Fact, Chequeabot, Factiverse, corroborate-mcp), papers (arXiv 2509.25498 y 2509.25494), capacidad histórica de GDELT DOC y modelos locales para 8 GB | PLAN_REVIEW §10, DL-006, DL-008 y DL-009 actualizados | Fuentes enlazadas; los datos de modelos se verificarán midiendo (B-10) |
| 2026-10-06 | Claude Code (cloud), Lead | H1 + Claude | Implementación del núcleo M1 | Puntaje, estado de evidencia, Source DNA, vínculo oficial, conflictos, validadores, plantilla, revisión, service y pipeline, con pruebas | 46 pruebas en verde; 2 fallos reales detectados por las pruebas y corregidos (ver 06) | Pendiente de revisión del equipo en el PR |
| 2026-10-06 | Codex + búsqueda web de documentación pública | frictionspp-svg | Construir adquisición reproducible y controles del snapshot | Fetchers DOC/GKG, RSS, WB y USGS; conservación de bytes; manifest SHA-256; adaptador RSS local; diccionario; pruebas sin red | 76 pruebas pasan (63 previas + 13 nuevas). Extracción parcial: 300 noticias GDELT, 540 observaciones WB, 82 eventos USGS; propuestas AP-008/AP-009 abiertas | Pendiente de decisiones de alcance y revisión del Lead; snapshot no congelado |
| 2026-10-07 | Claude Code (cloud), Lead | H1 + Claude | Implementación M2 (IA generativa) | Cliente Ollama, prompts v1, Story Studio, consultas con abstención, defensa contra inyección y pruebas con un LLM simulado | 63 pruebas en verde; 2 fallos reales más detectados y corregidos | Pendiente: validación en la RTX 4060 con el modelo real |
| 2026-10-07 | Codex | LowCrime | A-03: ficha de caso | Revisión y continuación de la página local, validación de revisiones, 9 pruebas AppTest y propuesta AP-011 para dependencias pendientes | 80 pruebas en verde; seis pestañas con fixture sintético; tarjeta A-08 y API de recibo pendientes | Pendiente de revisión del Lead en PR borrador |
| 2026-10-07 | Codex | LowCrime | Completar A-03/A-08 tras DL-020 | Tarjeta compartida, revisión del paquete visible, recibo descargable, AppTest y validación visual en Chromium con fixture sintético | 84 pruebas en verde; capturas a 1280×720; AP-011 aplicada | Pendiente de revisión final del Lead en PR #13 |
| 2026-10-07 | Codex | frictionspp-svg | Recuperar historial y garantizar manifest portable | Respaldo local, exclusión de ZIP/RSS, merge normal, separación de hashes locales, corte desde YAML y pruebas de copia sin auxiliares | 99 pruebas pasan; 118 hashes/tamaños locales verificados; B-01/B-02 aún incompletas | Pendiente de revisión del Lead |
| 2026-10-07 | Codex | LowCrime | A-01/A-02 | Home, navegación, filtros, matriz de evidencia y pruebas de UI; validación visual Chromium | 95 pruebas pasando; capturas y navegación a EVT-0003 verificadas | Pendiente del Lead en PR |
| 2026-10-07 | Codex | frictionspp-svg | Cerrar snapshot C-01 B-01/B-02 | Adaptador RSS con detección nula; adquisición DOC/GKG y USGS ampliado; auditoría de exclusiones; manifest portable; candidatos ciegos | 187 noticias (50 TVN), 540 WB, 82+87 USGS; manifest verificado; 114 pruebas pasan | Top 5 ciego y revisión del Lead pendientes |
| 2026-10-07 | Codex | LowCrime | A-04/A-09 | Consultas, citas y modo jurado; AppTest y capturas Chromium con snapshot real | 128 passed; abstención y respuesta extractiva verificadas | Pendiente del Lead |
| 2026-10-07 | Codex | LowCrime | A-07 | Agenda, pruebas y captura real Chromium | 123 passed, dos pruebas nuevas | Pendiente del Lead |
| 2026-10-07 | Codex | LowCrime | B-08 | P@5 por eventos, trazabilidad de ejecución y pruebas, limitación DL-024 | P@5 1/5 medido; 127 passed; otras métricas no medidas | Pendiente del Lead |
| 2026-10-07 | Claude Code | Lead (Silentarcherjr) | A-05/A-10, B-03, baseline B-05, revisión H-08 y PR #25–#27 | Trust Lab y simulador; `load_snapshot`; temas por reglas + agrupación TF-IDF; correcciones USGS con datos reales; integración de UI y evaluación | 136 pruebas; P@5 = 1/5 reproducida por B-08 | Revisado y mergeado por el Lead |
| 2026-10-07 | Codex | frictionspp-svg | B-05 IA y calibración sin top 5 | E5 multilingüe local; prototipos; 488 pares de 2025 anotados provisionalmente por IA; medición posterior C-01 | τ=0,87; 183→165 eventos; P@5 1/5→1/5; cuatro casos separados por guard temporal; 129 pruebas pasan; inferencia CPU | Revisión humana de etiquetas B-07 y revisión del Lead pendientes |
| 2026-10-07 | Codex + consulta de fuentes oficiales | frictionspp-svg | B-13/B-14, evidencia ACP/INEC | CSV históricos ACP, transcripción con hash del Anexo 4 INEC, manifest v1.1 y medición pareada | 812 filas (394 proyecciones null); estados 0 suficiente/131 parcial/34 insuficiente antes y después; AP-012 abierta; 152 pruebas pasan | Cotejo humano INEC y decisión del Lead pendientes |
| 2026-10-07 | Ollama local, Qwen3 8B + E5 | frictionspp-svg | Precálculo real top 15 | AMD RX 9060 XT Vulkan, 37/37 capas GPU; E5 CPU; caché inicialmente vacía | 15 paquetes live, 0 fallback; mediana 15068 ms, p95 17755 ms; citas brief/guion 49/49; resultados guardados en eval/results | Validez del apoyo no medida; revisión del Lead pendiente |

| 2026-10-07 | Codex | LowCrime | B-12/B-08 y A-06 | Set sintético de 16 ataques + 4 controles; runner service.ask/validador, métricas y preparación HF protegida | 156 pruebas; abstención 6/16 y 0/4, sondas 9/9; capturas locales; sin publicación ni LLM vivo | Pendiente del Lead, fallos de producto AP-012 |
| 2026-10-07 05:43 UTC | Codex / modelos locales | frictionspp-svg | Backlog 1 precompute DL-026 | Backlog final del Lead | 172 pytest verdes; 15 paquetes medidos, E5 activo, qwen3:8b Vulkan RX9060XT; resultados final-precompute en eval/results; procesados locales. | Revisión del Lead pendiente |
| 2026-10-07 05:48 UTC | Codex / modelos locales | frictionspp-svg | Backlog 2 cache publica A-06 | Backlog final del Lead | 187 noticias sin descripcion,165eventos,30entradas auditadas,15/15cache; stage preparado sin publicar;174pytest verdes; aviso @LowCrime en PR. | Revisión del Lead pendiente |
| 2026-10-07 05:51 UTC | Codex / modelos locales | frictionspp-svg | B-11 CI | Backlog final del Lead | 172pytest verdes,ruff tests verde; workflow Python3.12 con pytest y ruff check .;36avisos globales fuera de tests reportados,sin ocultarlos ni modificar modulos Lead. | Revisión del Lead pendiente |
| 2026-10-07 05:56 UTC | Codex / modelos locales | frictionspp-svg | B-07 pendiente humano | Backlog final del Lead | 100temas propuestos y32titulares para488pares;0confirmados;metricas no medido;174pytest;solicitud enviada,seguirbenchmark. | Revisión del Lead pendiente |

## Herramientas de IA dentro del producto (no son de desarrollo)

| Componente | Modelo | Uso | Costo |
|---|---|---|---|
| Embeddings | _DL-006, pendiente_ | Temas, agrupación, recuperación | $0 (local) |
| LLM | _DL-006, pendiente_ | Afirmaciones, paquete editorial, Q&A | $0 (local) |

### Uso adicional · 2026-10-07 · LowCrime
Codex: B-08 importación de mediciones existentes, trazabilidad y pruebas de métricas vacías/inválidas.
No generó etiquetas humanas ni tiempos; conserva fuente, n, hardware y no medido. Revisión Lead pendiente.
Codex · LowCrime · 2026-10-07 · AP-014: revisión de Trust Lab y parche propuesto de métricas/limitaciones; no aplicado, pendiente del Lead.
