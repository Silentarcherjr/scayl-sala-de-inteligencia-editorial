# Relevo · worker-web · 2026-10-08 02:35 UTC

- **Motivo:** relevo preventivo al cerrar etapa; trabajo continúa.
- **Rama:** `worker-web/next-static` · **Commit anterior:** `ae7ced8`; el commit de esta etapa incluye esta nota y se sube a origin.
- **PR abierto:** ninguno

## Tarea en curso
DL-034 — web Next.js estática. Etapa 6 completada.

## Hecho en esta sesión
Workflow web con npm ci, lint y build; actions fijadas y sin secretos

## Siguiente paso concreto
Etapa 7: README, capturas, recorrido offline, contraste Streamlit y PR

## Estado de las pruebas
197 passed; ruff OK; npm ci/lint/build OK

## Archivos tocados
Consultar el commit de la etapa y git diff origin/main. Solo archivos autorizados por WEB_NEXT_PLAN.

## Bloqueos, dudas y decisiones pendientes
No modificar deploy/README.md: el usuario prohíbe cambios en deploy/. Registrar URL en README principal.

## Contexto que no está en el código
Python: .venv/bin/python; ruff: .venv/bin/ruff. Exportar con python -m scripts.export_web.
El exportador restaura el bundle procesado y el entorno tras prepare(). No usar agentes delegados.
