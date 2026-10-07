# Relevo · frictionspp-svg · 2026-10-07 19:14 UTC

- **Motivo de la parada:** bloqueos humanos tras recorrer el backlog completo, incluido B-06 opcional. No se afirma que las métricas humanas estén completas.
- **Rama del workspace principal:** `worker-b/human-labels-final`. Commit previo `f1648c4`; este relevo va en un commit posterior empujado. Mantener esta rama para recibir ediciones humanas.
- **PR abierto de esta rama:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/40 (borrador; etiquetas pendientes).
- **Sincronización:** fetch + merge normal con origin/main limpio; main `dc1a990`. No rebase ni force-push. Cada tarea independiente nace de origin/main; solo el Lead mergea.

## Tarea en curso
Backlog final de docs/agents/frictionspp-svg.md. Código autónomo entregado por PR; volver ahora a holdout v2, B-07 y H-06 cuando lleguen entradas humanas. CI necesita los avisos fuera de tests resueltos por el Lead.

## Hecho en esta sesión
- 1 precalculo actualizado: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/37; `worker-b/final-precompute`; `fea2d5a` empujado.
- 2 cache publica revisada: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/38; `worker-b/public-reviewed-cache`; `196e758` empujado.
- 3 B-11 workflow y lint tests: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/39; `worker-b/ci-final`; `09c0d40` empujado.
- 5 B-07 formularios; revision humana pendiente: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/40; `worker-b/human-labels-final`; `f1648c4` empujado.
- B-10: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/48; `worker-b/benchmark-final`; `e8df9de` empujado.
- B-04: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/49; `worker-b/synthetic-final`; `da26728` empujado.
- B-06: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/50; `worker-b/retrieval-final`; `7824fde` empujado.
- H-06 compartido: protocolo/runner del PR https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/45 de LowCrime, sin duplicar su PR. Copias locales estables `tmp/h06/H06_MINI_STUDY.md` y `tmp/h06/time_study.csv` (campos humanos vacíos).
- B-10: 8b mediana14643/p9517600ms, citas49/49, fallback0/15; 4b mediana9050/p9512898.2ms, citas25/25, EMPTY_BRIEF3/15. Recomendar8b para demo; no cambió default. Citas tras validación no equivalen a soporte verificado.
- B-04: T01/T02/T03/T05/T07 y suficiente ACP85.1pies inventado; corpus separado, seis casos ejecutados, sin tocar raw. Bundle sintético local ignorado.
- B-06: flag hybrid=False predeterminado; opt-in BM25+E5, sin integración en qa.py. Smoke real3/3consultas sobre1314unidades; precisión no medida. Integración futura requiere propuesta.

## Siguiente paso concreto
1. Antes de leer/cambiar más: git fetch origin y git merge origin/main, sin rebase; detenerse si hay conflictos. Revisar notas nuevas del Lead.
2. Recibir diez preguntas trampa manuscritas y expected_abstain sí/no, sin que el humano lea qa.py/cases.jsonl. No fabricar el holdout. Crear rama nueva desde main y guardar eval/redteam/holdout_v2.jsonl con id/category/question/synthetic/expected_abstain, luego ejecutar runner sin cambios: `python -m scayl.eval.redteam --cases eval/redteam/holdout_v2.jsonl --output eval/results/holdout-v2.json`. Reportar num/den aunque malos. Documentar origen humano: el runner etiqueta scope de desarrollo por defecto, no alterarlo para mejorar resultados.
3. Revisar respuestas humanas en `data/labels/topics_human.csv` (100 filas) y `dev2025_groups_human.csv` (32 filas). Completar etiqueta/grupo humano, confirmado=si y revisor. No sobrescribir estos formularios ni tomar propuestas como gold. En rama B-07 ejecutar `python -m scayl.eval.human_labels evaluate` tras confirmar: macro-F1 y P/R/F1 sobre488pares de desarrollo. No recalibrar tau ni leer editor_top5. PR40 sigue borrador hasta medir.
4. H-06: seis tiempos reales y resultados escritos de tres pares manual/asistido, misma persona por par, orden y fecha UTC. Plantilla local tmp/h06/time_study.csv; protocolo del PR45. Cuando exista medición, coordinar con LowCrime su runner, sin inventar tiempos ni duplicar PR. n=3 exploratorio.
5. Al cerrar también las tareas humanas, actualizar este relevo y avisar TERMINADO. Por ahora no están terminadas.

## Estado de las pruebas
- PR37:172passed; PR38:174passed; PR39:172passed y Ruff tests verde; PR40:174passed.
- PR48 B-10:172passed. PR49 B-04:173passed. PR50 B-06:176passed y Ruff propio verde.
- CIglobal PR39 conserva36avisos fuera de tests, reportados en eval/results/b11-ruff.json. No afirmar CI global verde. La instrucción del Lead permite corregir tests solamente.
- B-07:0/100temas y0/32grupos confirmados, métricas no medidas. Holdout humano y H-06 no medidos.
- Fallos reales corregidos y anotados en06: EvidenceRef no tiene unit (se conserva en excerpt), script smoke usaba report.total pero loader devuelve dict. Desconexiones transitorias de GitHub se reintentaron; los PR y pushes finales se verificaron.

## Archivos tocados
Ver cada PR listado: resultados reales en eval/results; docs/B10_MODEL_BENCHMARK.md, B04_SYNTHETIC_DEMO.md, B06_RETRIEVAL_EXPERIMENT.md y B07_HUMAN_REVIEW.md; bitácora append-only worker-b y AI_TOOLS_USED. Worktrees de benchmark/synthetic/retrieval bajo tmp/worktrees.

## Bloqueos, dudas y decisiones pendientes
Solicitudes humanas enviadas de nuevo al retomar; ninguna respuesta recibida. CI necesita Lead. No hay publicación externa ni cambios de arquitectura/contratos. Se mantiene el criterio conservador de independencia; datos reales no se alteran para obtener suficiente.

## Contexto que no está en el código
Python local `.venv/Scripts/python.exe` (Python3.14); workflow exige3.12. GNU Make ausente: receta equivalente exacta ejecutada. AMD RX9060XT8GiB, Ollama Vulkan; E5 CPU. Modelos/CLI locales ignorados en models; worktrees usan junction. Ollama localhost11434; qwen3:8b y qwen3:4b disponibles. La latencia medida es Studio, excluye llamadas de claims y QA. Una corrida/modelo, n15.
Raíz conserva bundle real8b en data/processed/v1 y caché final-precompute-20261007 local. B-04 bundle aparte en tmp/worktrees/synthetic/data/processed/synthetic-demo. No subir processed, ZIP, RSS con descripciones, secretos ni backup/wip-617d6e2. Nunca push--all. Antes de CADA push: git rev-list --objects origin/main..HEAD filtrado por zip/rss.xml debe ser vacío. Todos los pushes de esta sesión cumplieron el guard.
