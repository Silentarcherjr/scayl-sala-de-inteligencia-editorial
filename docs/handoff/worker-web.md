# Relevo · worker-web · 2026-10-08 02:29 UTC

- **Motivo:** relevo preventivo al cerrar etapa; trabajo continúa.
- **Rama:** `worker-web/next-static` · **Commit anterior:** `3942452`; el commit de esta etapa incluye esta nota y se sube a origin.
- **PR abierto:** ninguno

## Tarea en curso
DL-034 — web Next.js estática. Etapa 3 completada.

## Hecho en esta sesión
165 fichas estáticas con ocho pestañas, citas y paquetes validados

## Siguiente paso concreto
Etapa 4: Consultas y recorridos del jurado

## Estado de las pruebas
npm lint y build OK; 168 rutas exportadas, 165 casos

## Archivos tocados
Consultar el commit de la etapa y git diff origin/main. Solo archivos autorizados por WEB_NEXT_PLAN.

## Bloqueos, dudas y decisiones pendientes
No modificar deploy/README.md: el usuario prohíbe cambios en deploy/. Registrar URL en README principal.

## Contexto que no está en el código
Python: .venv/bin/python; ruff: .venv/bin/ruff. Exportar con python -m scripts.export_web.
El exportador restaura el bundle procesado y el entorno tras prepare(). No usar agentes delegados.
