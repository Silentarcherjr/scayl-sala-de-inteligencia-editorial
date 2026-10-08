# Relevo · worker-web · 2026-10-08 02:31 UTC

- **Motivo:** relevo preventivo al cerrar etapa; trabajo continúa.
- **Rama:** `worker-web/next-static` · **Commit anterior:** `5bf3b34`; el commit de esta etapa incluye esta nota y se sube a origin.
- **PR abierto:** ninguno

## Tarea en curso
DL-034 — web Next.js estática. Etapa 4 completada.

## Hecho en esta sesión
Consultas con ejemplos precalculados, recorridos jurado, buscador y pregunta libre enlazada

## Siguiente paso concreto
Etapa 5: Trust Lab y Simulador de pesos

## Estado de las pruebas
npm lint y build OK; 169 rutas

## Archivos tocados
Consultar el commit de la etapa y git diff origin/main. Solo archivos autorizados por WEB_NEXT_PLAN.

## Bloqueos, dudas y decisiones pendientes
No modificar deploy/README.md: el usuario prohíbe cambios en deploy/. Registrar URL en README principal.

## Contexto que no está en el código
Python: .venv/bin/python; ruff: .venv/bin/ruff. Exportar con python -m scripts.export_web.
El exportador restaura el bundle procesado y el entorno tras prepare(). No usar agentes delegados.
