# Relevo del Lead — cierre del 2026-10-08 (entrega 23:59 UTC-5)

> Documento vivo: se actualiza tras cada integración. Si este agente se corta, otro agente con acceso a GitHub
> continúa desde aquí. Rama de trabajo: **`claude/final-delivery`** (PR abierto contra `main`).
> Referencia estable de recuperación: tag local `stable-pre-final` = `b4d03f0` (main antes del cierre; 287 pruebas, CI verde).

## Reglas para quien continúe
- No hacer merge a `main` ni redeploy (Vercel) sin confirmación explícita de Silentarcherjr en el chat.
- No enviar el correo: lo envía una persona (`docs/ENTREGA_CORREO.md`).
- No tocar `data/labels/*` (revisiones humanas inmutables) ni bajar umbrales de evidencia.
- `python -m pytest -q` y `ruff check .` en verde antes de cada commit (excluir `.claude/` si hay worktrees locales).
- No mencionar a otros equipos en el repositorio.

## Estado (actualizar en cada paso)
| ID | Resp. | P | Estado | Cambio | Pruebas | Métrica | Commit | Decisión |
|---|---|---|---|---|---|---|---|---|
| E0 | Lead | P0 | HECHO | PDF herramientas IA `docs/ai_tools/SCAYL_Herramientas_IA.pdf`, borrador de correo, retiro del enlace Streamlit (exige login) en README/Notion/footer web | build+lint web, pytest | — | 02f9ca2, 7e4adf2 | GO |
| D | Sub D | P0 | HECHO | Etiqueta de modo por salida (plantilla/caché/vivo/abstención), P como «atención», «aprobado como borrador · NO publicado», 404 en español, tarjeta de latencia | build 173 págs, lint, pytest | — | ca5215c, 916fcc7 | GO |
| E | Sub E | P0 | HECHO | `docs/QA_FINAL_AUDIT.md`: T01–T10 10/10 (automatizadas), sha256 coinciden, sin secretos; alcances de métricas corregidos en README y `docs/notion/` | pytest, ruff, red-team 22 | — | 645695a, 0cf98a6 | GO |
| A | Sub A | P1 | HECHO | 5 fallos de la revisión de sustento (SR04/05/10/19/25) corregidos en plantilla + 8 validadores nuevos (entidad, unidad, cambio relativo, negación, causalidad, acusación, escritura no latina, fecha); robustez ante salida malformada | +47 pruebas | `eval/results/a-validators-before-after.json` (automático; sustento nuevo NO revisado por humanos) | a224c57, 6fa0576, a7bd012 | GO |
| C | Sub C | P1 | HECHO | Conflictos solo entre cifras comparables (indicador+período+lugar+unidad), desmentidos, guardas de lugar/proyección, Source DNA con sufijos sindicados | +49 pruebas | Set sintético: precisión 5/15→8/8, recall 5/8→8/8 (dev, optimista); posthoc 1/3→2/2 | c281d82, 75bcdab, dcc76d4 | GO |
| B | Sub B + Lead | P1 | HECHO | Benchmark QA v2 (40 dev + 20 reservadas, escrito por IA, sin revisión humana); normalización ISO/sinónimos, lugares USGS en español, rerank, abstención ante pregunta con instrucciones | +5 pruebas; T06/T07 verdes | Reservadas: respondidas con cita 9/14→11/14; abstención indebida 5/14→3/14; abstención correcta 6/6; fugas 0/4; lados de contradicción en top 5 3/3→2/3 (regresión). E5 no medido | cherry-picks de ead8dfa, 10c4a81, 86acee3 | GO |
| Q | Lead | P1 | HECHO | Corrida real de Qwen3 8B (M1 Max, top 30, agrupación TF-IDF porque E5 no está en caché), revalidada con validadores nuevos; muestra `data/labels/support_review_qwen_live.csv` (55 afirmaciones, 29 eventos) | +1 prueba | 30/30 en vivo, 0 fallback; mediana 19,5 s; 115→111 oraciones (2 descartes correctos por cargo inventado, 2 estrictos por cita). Sustento: NO medido hasta revisión humana | ac66493 | GO |

## Notas importantes
- **El bundle público (web/public/data) NO se regeneró**: los cambios de A y C aplican al regenerar. En la demo, EVT-0114 aún
  muestra el 7.4 (sismo México–Guatemala) como versión en conflicto; C demostró que es un falso conflicto. Regenerar el bundle
  exige revisar paridad web/Streamlit: decisión del Lead/humano, no automática.
- Hallazgo de A: una oración de Qwen en la caché nombra a «José Raúl Mulino» sin estar en la evidencia citada (ENTITY_NOT_IN_EVIDENCE).

## Requiere acción humana
1. **Repositorio privado** (404 sin sesión). E auditó: sin secretos en los 911 archivos versionados. Hacerlo público o retirar el enlace del correo.
2. **Notion** está en el espacio «hackIAthon 4taEd» y pide inicio de sesión. Si el jurado no es miembro: Compartir → Publicar en la web (las 4 páginas).
3. **Enviar el correo** (`docs/ENTREGA_CORREO.md`) a hackiathon@viamatica.com con el PDF adjunto.
4. Revisión humana de las afirmaciones de Qwen (muestra en preparación) y estudio H-06 (n=0, no medido).
5. Ensayo real sin wifi (H-05) — T10 solo está verificado con red bloqueada en pytest.
