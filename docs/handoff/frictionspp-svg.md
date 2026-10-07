# Relevo · frictionspp-svg · 2026-10-07T20:45:22.309333Z

- **Motivo de la parada:** tareas de la última solicitud completas; revisión y merge quedan al Lead.
- **Rama:** `worker-b/human-inputs`, nueva desde origin/main PR #51; merge limpio del PR #52, main `5dcac75`.
- **Último commit antes de este relevo:** `eb5444a`, empujado. Este relevo se guarda en un commit posterior de la misma rama.
- **PR único abierto:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/53 (listo para revisión, no mergeado por el worker).

## Tarea en curso
Terminadas las entradas humanas interactivas B-07 y red-team v2, su evaluación y documentación.
El Lead revisa PR #53. No queda ninguna etiqueta, pregunta ni medición solicitada pendiente.

## Hecho en esta sesión
- Revisión de 100 titulares de temas en diez bloques, con etiquetas explícitas de frictionspp-svg.
- Revisión de 32 titulares de agrupación en bloques 10/10/10/2. El humano confirmó las propuestas de cada bloque con «ok».
- Revisor frictionspp-svg, respuestas originales, IDs, propuestas y hora UTC por bloque en data/labels/human_review_log.jsonl; CSV sin cambiar esquema. Auditoría 132/132 filas.
- Temas macro-F1, n=100 y siete clases: baseline 0.7568136932192232, IA 0.24645960051496715. No tuning con estas etiquetas.
- Agrupación, 488 pares: baseline P12/12, R12/43, F1=0.43636363636363634; IA P42/42, R42/43, F1=0.988235294117647.
- Desarrollo 2025 previamente usado para calibrar τ provisional; revisión asistida con propuestas visibles, no gold ciego ni holdout de clustering. Recall relativo al pool.
- Diez preguntas trampa nuevas y expectativas originales del humano en eval/redteam/holdout_v2.jsonl; revisor/UTC/texto original/hash en holdout_v2.provenance.json.
- Runner sin cambiar código ni expectativas: abstenciones esperadas6/6; abstenciones en controles con expectativa de respuesta4/4; controles respondidos0/4; coincidencias6/10. Fallan HV2-03/05/07/09, conservados en reporte y registro de fallos06.
- Los controles de conocimiento general no tienen soporte garantizado en el fixture. El runner señala falta de evidencia; el resultado de abstención falsa es relativo a la expectativa humana, no prueba de rechazo de respuestas sustentadas.
- Fixture sintético template/extractivo; no LLM vivo, bundle C-01 ni set reservado oficial. Scope fijo «IA/sin gold humano» preservado en raw; companion corrige procedencia y conserva números originales.
- No cambios propios en scayl, runner, qa.py, prototipos, τ, ranking ni casos existentes. PR #52 del Lead cambió independientemente pipeline a temas por reglas/E5 agrupación; incorporado mediante merge limpio.
- PR #53 agrupa todo; ningún otro PR nuevo en esta sesión. No se reutilizaron ramas anteriores ni se importó cc327d1 obsoleto.

## Siguiente paso concreto
1. Lead: revisar PR #53 y actualizar estados de TASKS/tablero/decision log si procede. Solo el Lead mergea.
2. Si llega otra solicitud, comenzar con fetch + merge origin/main sin rebase; detenerse ante conflictos. Leer notas nuevas. No volver a preparar ni sobrescribir formularios revisados.
3. No cambiar las expectativas ni afinar QA con este holdout para mejorar los números. Para otra evaluación, definir datos/expectativas y nuevo conjunto aparte antes de ajustar código.

## Estado de las pruebas
Tras el merge de main actualizado: python -m pytest -q →188 passed; ruff check . →All checks passed.
Integridad de 132 etiquetas, diez preguntas, hashes de fuentes/reportes y código propio intacto: verificada.
Los cuatro fallos del holdout son discrepancias de expectativas y se reportan aunque pytest esté verde.
Checks remotos del PR: consultar su ejecución sobre el último commit; no confundirlos con pruebas locales.

## Archivos tocados
data/labels/topics_human.csv, dev2025_groups_human.csv, human_review_log.jsonl y .gitattributes;
eval/redteam/holdout_v2.jsonl, holdout_v2.provenance.json y .gitattributes;
eval/results/b07-human-metrics.json, b07-human-review-summary.json, holdout-v2.json,
holdout-v2-summary.json y copia archivada runs/redteam-20261007T202802939484Z.json, con .gitattributes;
docs/B07_HUMAN_REVIEW.md, HUMAN_HOLDOUT_V2.md, AI_TOOLS_USED.md, notion_mirror/06_TESTS_AND_METRICS.md,
worklog/worker-b.md y este relevo. Ver diff del PR para los detalles completos.

## Bloqueos, dudas y decisiones pendientes
No hay bloqueos de implementación del alcance solicitado. Revisión/merge pendientes del Lead.
H-06 quedó fuera de esta última solicitud; no se inventaron tiempos humanos.

## Contexto que no está en el código
Python .venv/Scripts/python.exe; Ruff .venv/Scripts/ruff.exe. Modelo E5 local CPU; ejecutado escalado en Windows por política DLL.
tmp contiene helpers y copias de respuestas; los originales importantes están también en la bitácora/provenance trackeadas.
Reportes guardados sin normalizar saltos de línea para preservar hashes. No se subieron data/processed, modelos,
GKG ZIP, RSS con descripciones, secretos ni backup/wip-617d6e2. Todos los pushes pasaron el guard de objetos ZIP/rss.xml.
Un push demoró por la conexión; luego confirmó subida. No rebase, force-push ni push --all.
