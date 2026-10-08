# Relevo · worker-web · 2026-10-08 04:34 UTC

- **Motivo de la parada:** relevo preventivo al cerrar etapa.
- **Rama:** `worker-web/bank-bulletin` · **Último commit:** el commit de etapa incluye esta nota; consultar `git log -1` (push al cerrar).
- **PR abierto:** pendiente hasta completar §8; buscar PR de worker-web/bank-bulletin al cierre.

## Tarea en curso
DL-035 / docs/BANK_BULLETIN_PLAN.md. Etapa 2. Cambios aditivos; no alterar Story Studio, Q&A, ranking, app/, deploy/ ni pruebas existentes.

## Hecho en esta sesión
Página /boletin/, selector, citas, límites visibles y estilo de impresión; export público aditivo.

## Siguiente paso concreto
Implementar camino LLM, validación y fallback con backend simulado.

## Estado de las pruebas
pytest 218; ruff; npm lint y build, 173 rutas

## Archivos tocados
Ver commit de etapa. Permitidos por DL-035: contrato nuevo, scayl/gen/bulletin.py y prompt nuevo, función nueva de servicio, export, web/ y tests/test_bulletin.py.

## Bloqueos, dudas y decisiones pendientes
Precálculo con GPU opcional requiere humano y revisión; no tocar deploy/artifacts ni afirmar inferencia real sin ejecución. Corte duro: 8 de octubre, 18:00 Panamá; si etapa 3 no pasa §8, entregar última estable. Mergea el Lead.

## Contexto que no está en el código
Python .venv/bin/python; ruff .venv/bin/ruff. Node bundled runtime; compilar Next requiere escalación de sandbox. Exportar a /tmp y copiar solo bulletins.json para no cambiar los JSON existentes. Contrato 0.4.0 es aditivo.
