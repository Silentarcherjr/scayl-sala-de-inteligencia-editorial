# Relevo · frictionspp-svg · 2026-10-07T20:02:05.872997Z

- **Motivo de la parada:** checkpoint preventivo AGENTS §2b tras completar B-07; continúa la interacción para red-team v2.
- **Rama:** `worker-b/human-inputs`, nueva desde origin/main `5b6fd71` (PR #51).
- **Último commit antes de este relevo:** `9fcd12f`; empujado junto con el checkpoint posterior.
- **PR abierto:** ninguno nuevo. Se abrirá un solo PR al final con B-07 y holdout v2, según el humano.

## Tarea en curso
B-07 completo. Esperar diez preguntas trampa nuevas escritas por frictionspp-svg,
sin mostrarle qa.py ni eval/redteam/cases.jsonl, con expected_abstain sí/no por pregunta.
La solicitud interactiva ya está enviada. No fabricar preguntas ni expectativas humanas.

## Hecho en esta sesión
- Main integra los PR #37–#40 y #48–#50 vía #51; CI y Ruff corregidos por el Lead.
- No se importó cc327d1 porque sus estados de PR/CI quedaron desactualizados.
- Temas: 100/100 etiquetas humanas explícitas, en diez bloques.
- Agrupación: 32/32 titulares, en bloques 10/10/10/2. El humano confirmó los grupos propuestos con «ok» en cada bloque.
- Revisor frictionspp-svg, hora UTC y respuesta original por bloque en data/labels/human_review_log.jsonl.
- CSV conserva esquema. Evaluación auditada con hashes en eval/results/b07-human-review-summary.json.
- Macro-F1 de temas: baseline 0.7568136932192232, IA 0.24645960051496715; n=100, siete clases, zero_division=0.
- Agrupación, 488 pares de desarrollo: baseline P=12/12, R=12/43, F1=0.43636363636363634; IA P=42/42, R=42/43, F1=0.988235294117647.
- Revisión asistida, no gold ciego. El desarrollo de agrupación ya sirvió para calibrar τ; no es generalización a holdout. Recall relativo al pool.
- No se ajustaron modelos, prototipos, τ ni ranking con estas respuestas; no se leyó editor_top5.

## Siguiente paso concreto
1. En sesión nueva, fetch + merge origin/main sin rebase; detenerse ante conflictos. Leer notas del Lead.
2. Recibir las diez preguntas humanas y la expectativa de abstención sí/no. Si falta o es ambigua, preguntar; no inferir su respuesta.
3. Guardar eval/redteam/holdout_v2.jsonl en el formato del runner, con IDs estables, category, question, synthetic=true y expected_abstain. Auditar procedencia humana y UTC. No mostrar ni copiar preguntas existentes.
4. Ejecutar python -m scayl.eval.redteam --cases eval/redteam/holdout_v2.jsonl --output eval/results/holdout-v2.json, sin cambiar runner ni qa.py. Reportar num/den tal como salgan, aunque malos. Registrar fallos reales en 06 sin alterar código para mejorar holdout.
5. Actualizar documentación, AI_TOOLS_USED y worklog; python -m pytest -q y ruff check . verdes; un solo PR hacia main. Solo el Lead mergea.

## Estado de las pruebas
Tras completar B-07: python -m pytest -q → 188 passed; ruff check . → All checks passed.
Auditoría verifica todas las filas contra las respuestas del JSONL. Holdout v2 aún no medido.

## Archivos tocados
data/labels/topics_human.csv; dev2025_groups_human.csv; human_review_log.jsonl;
data/labels/.gitattributes; eval/results/b07-human-metrics.json;
eval/results/b07-human-review-summary.json; eval/results/.gitattributes;
docs/B07_HUMAN_REVIEW.md; docs/worklog/worker-b.md; docs/AI_TOOLS_USED.md; este relevo.

## Bloqueos, dudas y decisiones pendientes
Solo faltan las preguntas humanas y su ejecución para el alcance actual. H-06 queda fuera de la última solicitud.
No hay cambios en contratos, arquitectura, dependencias ni código del evaluador/runner.

## Contexto que no está en el código
Python .venv/Scripts/python.exe; Ruff .venv/Scripts/ruff.exe. E5 local CPU, modelos ignorados en models/.
En Windows las ejecuciones reales con E5 se escalan por la política DLL. Ollama local disponible, pero red-team usa runner en modo template.
tmp/record_human_topics.py y tmp/record_human_groups.py requieren entradas explícitas; no sobrescriben filas revisadas.
tmp/human-*-response-*.txt y la bitácora trackeada preservan respuestas originales. No preparar formularios de nuevo: perdería etiquetas.
Antes de cada push: git rev-list --objects origin/main..HEAD filtrado por zip/rss.xml debe estar vacío.
Nunca subir processed, GKG ZIP, RSS con descripciones, modelos, secretos ni backup/wip-617d6e2. Nunca push --all.
