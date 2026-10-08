# Relevo · worker-web · 2026-10-08 04:44 UTC

- **Motivo de la parada:** relevo preventivo al cerrar etapa.
- **Rama:** `worker-web/bank-bulletin` · **Último commit:** el commit de etapa incluye esta nota; consultar `git log -1` (push al cerrar).
- **PR abierto:** pendiente hasta completar §8; buscar PR de worker-web/bank-bulletin al cierre.

## Tarea en curso
DL-035 / docs/BANK_BULLETIN_PLAN.md. Etapa 5. Cambios aditivos; no alterar Story Studio, Q&A, ranking, app/, deploy/ ni pruebas existentes.

## Hecho en esta sesión
Documentación de extensión DL-035, modos reales, límites y pruebas. Etapas 1/2/3/5 completas; etapa 4 opcional omitida sin GPU/caché revisada. Ambos textos listos para incluir íntegros en el PR.

## Siguiente paso concreto
Abrir PR a main con ambos boletines completos, adjuntarlo y esperar revisión/merge del Lead.

## Estado de las pruebas
Sección 8 aprobada: 230 pytest, ruff, npm ci/lint/build; textos leídos y capturas escritorio/móvil/impresión, Wi-Fi restaurado

## Archivos tocados
Ver commit de etapa. Permitidos por DL-035: contrato nuevo, scayl/gen/bulletin.py y prompt nuevo, función nueva de servicio, export, web/ y tests/test_bulletin.py.

## Bloqueos, dudas y decisiones pendientes
Precálculo con GPU opcional requiere humano y revisión; no tocar deploy/artifacts ni afirmar inferencia real sin ejecución. Corte duro: 8 de octubre, 18:00 Panamá; si etapa 3 no pasa §8, entregar última estable. Mergea el Lead.

## Contexto que no está en el código
Python .venv/bin/python; ruff .venv/bin/ruff. Node bundled runtime; compilar Next requiere escalación de sandbox. Exportar a /tmp y copiar solo bulletins.json para no cambiar los JSON existentes. Contrato 0.4.0 es aditivo.
