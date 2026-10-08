# Relevo · frictionspp-svg · 2026-10-08 05:47 UTC

- **Motivo de la parada:** tarea cerrada por decisión del Lead, opción A; relevo preventivo.
- **Rama:** worker-b/bulletin-qwen.
- **Último commit:** consultar git log -1; revert de código bab6ba8 y commit documental posterior.
- **PR abierto:** solo documentación; URL comunicada al humano al crear el PR.

## Tarea en curso
DL-035 precálculo Qwen: no se publica como salida de IA; el boletín sigue plantilla.

## Hecho en esta sesión
- Revert de 6cc5001 con git revert, sin reescribir historia; bab6ba8 restaura bulletin.py y su prueba, retira prompt v3.
- Se conservó documentación y texto completo del boletín pese al conflicto modify/delete documental del revert.
- Conclusión del Lead registrada: intento1 falla esquema; intento2 válido pero anclado a plantilla_validada.
- Igualdad exacta comprobada: observaciones9/9, hipótesis3/3, preguntas3/3 frente a la plantilla.
- No se copió caché, no se exportó ni se hizo nueva inferencia. Web y deploy intactos.

## Siguiente paso concreto
1. Lead: revisar el PR exclusivamente documental; integración a cargo del Lead.
2. Mantener el rótulo Plantilla (sin IA generativa). No reutilizar la caché temporal como IA publicada.
3. Posible mejora futura: quitar plantilla del payload; no hecha ni autorizada en esta conclusión.

## Estado de las pruebas
Pytest con PYTHONUTF8=1: 242 passed. Ruff check .: verde.
git diff origin/main -- scayl/ tests/ web/ deploy/ vacío tras revert.

## Archivos tocados
Solo diferencias documentales: docs/BULLETIN_QWEN_PRECOMPUTE.md (texto conservado y conclusión),
docs/AI_TOOLS_USED.md, docs/worklog/worker-b.md, docs/notion_mirror/06_TESTS_AND_METRICS.md y este relevo.

## Bloqueos, dudas y decisiones pendientes
Ninguno para la decisión: no publicar Qwen por anclaje a plantilla. Mejora futura fuera de esta tarea.

## Contexto que no está en el código
Intentos preservados localmente en tmp/bulletin-cache-v2-rejected y tmp/bulletin-cache, ignorados.
Texto íntegro válido en docs/BULLETIN_QWEN_PRECOMPUTE.md; metadata live no implica originalidad del contenido.
PYTHONUTF8=1 necesario en Windows para pruebas con read_text sin encoding.
Nunca subir backup/wip-617d6e2, ZIP, RSS, pesos ni data/processed; nunca push --all.
