# Relevo · worker-web · 2026-10-08 02:23 UTC

- **Motivo:** relevo preventivo al cerrar etapa; trabajo continúa.
- **Rama:** `worker-web/next-static` · **Commit anterior:** `ea61718`; el commit de esta etapa incluye esta nota y se sube a origin.
- **PR abierto:** ninguno

## Tarea en curso
DL-034 — web Next.js estática. Etapa 1 completada.

## Hecho en esta sesión
Exportador público, dos pruebas y 165 fichas JSON versionadas

## Siguiente paso concreto
Etapa 2: Next.js, layout y Sala de Situación

## Estado de las pruebas
2 pruebas nuevas pasan; baseline 195 passed; ruff exportador OK

## Archivos tocados
Consultar el commit de la etapa y git diff origin/main. Solo archivos autorizados por WEB_NEXT_PLAN.

## Bloqueos, dudas y decisiones pendientes
No modificar deploy/README.md: el usuario prohíbe cambios en deploy/. Registrar URL en README principal.

## Contexto que no está en el código
Python: .venv/bin/python; ruff: .venv/bin/ruff. Exportar con python -m scripts.export_web.
El exportador restaura el bundle procesado y el entorno tras prepare(). No usar agentes delegados.
