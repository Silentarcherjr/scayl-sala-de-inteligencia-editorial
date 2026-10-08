# Relevo · frictionspp-svg · 2026-10-08 05:27 UTC

- **Motivo de la parada:** bloqueo de DL-035 etapa 4: fallback; el usuario ordenó detenerse sin reintentos.
- **Rama:** worker-b/bulletin-qwen, desde main a117cae.
- **Último commit:** consultar git log -1; este relevo se guarda y se empuja en esa rama.
- **PR abierto:** ninguno para DL-035; no cumple la condición live sin fallback.

## Tarea en curso
Precálculo del boletín logistica_canal con Qwen real. Detenido tras el único intento.

## Hecho en esta sesión
- Fetch, checkout main y pull --no-rebase: avance limpio a a117cae; rama propia creada.
- prepare() de demo_offline; bundle público sin descripciones en 187/187 noticias.
- Ollama0.40.0, qwen3:8b Q4_K_M, GPU AMD RX9060XT8GiB/Vulkan, misma configuración DL-029.
- Respuesta cruda live: latencia40262ms, tokens_in2050, tokens_out1253; esquema sin claim_ids.
- Resultado del servicio: mode=template, model=null. Motivo exacto: Se usó la plantilla determinista: La salida no conservó resumen, observaciones e hipótesis válidos.
- Códigos: {'LLM_FALLBACK': 1, 'UNCITED_FACT': 13, 'BANKING_UNCITED_HYPOTHESIS': 3, 'BANKING_HYPOTHESES_INCOMPLETE': 1, 'BANKING_SYNTHESIS_REQUIRED': 1, 'EMPTY_BULLETIN': 1}. No se alteró la respuesta, no hubo segundo intento.
- Caché pública intacta (comparación de todos los hashes antes/después), sin export ni código modificado.

## Siguiente paso concreto
1. Informar al Lead del fallback y de claim_ids omitidos. No reintentar ni reparar la caché cruda sin nuevas instrucciones.
2. El Lead decide corrección del camino LLM/prompt, fuera del alcance de esta tarea de datos. Corte duro: PR estable antes de 2026-10-08 18:00 America/Panama (23:00Z); de lo contrario no se entrega.
3. Solo tras nueva autorización y una ejecución válida: mostrar texto completo al humano frictionspp-svg; nunca asumir aprobación ni copiar caché antes.

## Estado de las pruebas
Inicial:10 failed/232 passed por CP1252; PYTHONUTF8=1:242 passed. Ruff check . verde.
npm.cmd ci falló con EACCES al descargar zod-validation-error desde registry.npmjs.org; lint/build y deploy.prepare no ejecutados. No se reintentó tras la orden de parada por fallback.

## Archivos tocados
Solo docs/AI_TOOLS_USED.md, docs/worklog/worker-b.md, docs/notion_mirror/06_TESTS_AND_METRICS.md y este relevo.
scayl/, app/, web/ y deploy/artifacts/ intactos.

## Bloqueos, dudas y decisiones pendientes
Salida real sin claim_ids: falla validación y provoca plantilla. Revisión humana no iniciada.
No hay PR de caché ni boletín IA válido para entrega; no se modificó el código para conseguir verde.

## Contexto que no está en el código
Resultado local: tmp/bulletin-live.json; contexto/hashes/modelo: tmp/bulletin-run-context.json.
Único archivo crudo rechazado: tmp/bulletin-cache/82c1828a70e19bab6e748f0a6cf2a410e55009feb67dd8d074742557418fe301.json; nunca copiarlo a caché pública.
La plantilla final tiene generated_by.latency_ms=0 y tokens nulos; cifras40262/2050/1253 solo del intento crudo.
PYTHONUTF8=1 permite ejecutar la suite en Windows. Ollama sigue en localhost:11434.
backup/wip-617d6e2 solo local, nunca push --all. Sin secretos, ZIP, RSS ni data/processed en commits.
