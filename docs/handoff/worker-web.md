# Relevo · worker-web · 2026-10-08 02:28 UTC

- **Motivo:** relevo preventivo al cerrar etapa; trabajo continúa.
- **Rama:** `worker-web/next-static` · **Commit anterior:** `0cff40c`; el commit de esta etapa incluye esta nota y se sube a origin.
- **PR abierto:** ninguno

## Tarea en curso
DL-034 — web Next.js estática. Etapa 2 completada.

## Hecho en esta sesión
Next.js App Router, sistema visual, layout y Sala con filtros y matriz

## Siguiente paso concreto
Etapa 3: ficha estática de los 165 casos

## Estado de las pruebas
npm lint y npm build OK; TypeScript sin errores. npm audit: 5 avisos transitivos de desarrollo en braces sin parche publicado; runtime sin vulnerabilidades reportadas.

## Archivos tocados
Consultar el commit de la etapa y git diff origin/main. Solo archivos autorizados por WEB_NEXT_PLAN.

## Bloqueos, dudas y decisiones pendientes
No modificar deploy/README.md: el usuario prohíbe cambios en deploy/. Registrar URL en README principal.

## Contexto que no está en el código
Python: .venv/bin/python; ruff: .venv/bin/ruff. Exportar con python -m scripts.export_web.
El exportador restaura el bundle procesado y el entorno tras prepare(). No usar agentes delegados.
