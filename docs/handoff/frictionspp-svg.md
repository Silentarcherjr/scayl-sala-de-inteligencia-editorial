# Relevo · frictionspp-svg · 2026-10-07 05:08 UTC

- **Motivo de la parada:** relevo preventivo al cerrar el bloque solicitado, AGENTS §2b; sin porcentaje fiable de sesión.
- **Rama:** worker-b/recent-official-evidence · **Último commit de implementación:** 536e6c0 (empujado: sí). Este relevo queda en commit posterior, también empujado.
- **PR abierto:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/31, listo para revisión. Solo el Lead mergea.

## Tarea en curso
B-13/B-14, adición oficial ACP/INEC, manifest, comparación de evidencia y precálculo real top 15 entregados en PR31. Proyección histórica no recuperada y cotejo humano INEC pendiente. B-05 mergeada vía PR30; DL-025 acepta E5 y separación temporal de los cuatro desarrollos de El Niño.

## Hecho en esta sesión
- Fetch/merge normal limpio de main 61ee2fa: merge local b6f5e08; rama nueva propia. Sin rebase ni force-push.
- CSV histórico/proyección ACP, PDF INEC Anexo 4 e índice de publicación originales con recibos HTTP/UTC/SHA-256 en responses/acp y responses/inec.
- indicadores_recientes.csv, 13 columnas, 812 claves únicas: 394 niveles diarios de Gatún (2025-09-02..2026-09-30), 394 proyecciones null, 12+12 variaciones INEC (2025-09..2026-08), signos originales, porcentajes, cita Anexo 4 página PDF 1.
- Proyección disponible: fechas 2026-10-07..2026-12-06, sin evidencia de emisión antes del corte. No se retrodató ni inventó; es_proyeccion=true y null explícito para períodos solicitados. Esa parte de B-13 sigue sin valores.
- INEC, base 2024=100, publicado 14/09/2026: transcripción por Codex, identificada por hash del PDF; revisión humana pendiente. No recalculada desde índices redondeados. Septiembre 2026 no publicado al corte.
- fuentes.recientes.json amplía metadatos sin alterar fuentes.json previo. Manifest v1.1, padre archivado byte por byte. declare_addition exige huella del padre y rechaza modificaciones del raw previo. verify_manifest=[].
- Todos los blobs raw preparados en Git comparados con SHA/tamaños del manifest; reporte copiado coincide con su SHA. Ningún ZIP, rss.xml, archivo >50 MB o data/processed publicado. 207 ZIP y RSS siguen en disco; backup nunca se publica.
- Medición pareada, mismos titulares/temas/grupos E5 τ=0,87 y reglas; solo cambia lista de indicadores. 165 eventos: antes y después 0 suficiente, 131 parcial, 34 insuficiente. Cinco eventos reciben contexto ACP, ninguna confirmación central; sin titulares IPC coincidentes.
- AP-012 ABIERTA: «restricciones» vincula contexto Gatún con EVT-0161 (homicidios/restricciones nocturnas). No confirma, pero es irrelevante. Se propuso al Lead acotar pertinencia y separar calado de nivel; no se tocó su módulo.
- Precálculo real completo: GNU Make ausente; receta exacta ejecutada con .venv/Scripts/python -m scayl.pipeline build --snapshot data/raw/v1 --llm live --top 15. Ollama 0.40.0, qwen3:8b, RX 9060 XT 8 GiB Vulkan, 37/37 capas GPU. E5 CPU.
- Caché dedicada inicialmente vacía data/cache/llm/recent-official-20261007; 15 claims-v1 + 15 studio-v1. 15 paquetes live, 0 fallback. Studio mediana 15068 ms, p95 17755 ms, n=15 (percentil lineal tipo 7). Citas brief/guion conservados 49/49; 68 oraciones generadas, 63 conservadas incluyendo copy; tres STATUS_MISMATCH y dos UNCITED_FACT eliminadas. Citas no equivalen a validez de apoyo.
- Bundle/fichas/caché locales, sin subir data/processed. Reporte de metadatos y métricas en eval/results/b13-b14-*.json/jsonl.

## Siguiente paso concreto
1. Sincronizar con main, revisar nuevas decisiones y PR31; no mergearlo por cuenta propia.
2. Lead decide AP-012; repetir comparación si cambian sus reglas. No forzar suficientes.
3. Cotejo humano de los 24 valores INEC contra Anexo 4 p1. Correcciones mediante nueva adición/versionado, preservando raw congelado.
4. Si se obtiene edición histórica oficial de proyección emitida antes del corte, ingresar con recibo y nueva adición. Nunca usar el pronóstico descargado en octubre.
5. Prioridades anteriores pendientes: B-07 gold humano y B-10 benchmark comparativo. El precálculo no reemplaza ninguno.

## Estado de las pruebas
.venv/Scripts/python -m pytest -q --junitxml=docs/worklog/worker-b-recent-official-pytest.xml → 152 passed, 8.20 s. Manifest verify=[]; estados tras live siguen 0/131/34.
Pruebas: corte/nulos, emisión de proyección, huella PDF, signos, immutabilidad del padre, contrato/unicidad/ventana reales, latencia solo live.
Raw ACP usa CRCRLF, reporte Windows CRLF: conservar bytes; no normalizar para satisfacer diff --check. Código/tests/docs pasan ese control; atributos -text preservan hashes.

## Archivos tocados
- scayl/ingest/recent_official.py, manifest.py; scayl/eval/recent_official.py, generation_summary.py; dos módulos de pruebas.
- data/raw/v1: CSV reciente, fuentes adicionales, recibo de adición, manifest v1.1/padre y responses/acp/inec.
- eval/results/b13-b14-* y .gitattributes; docs/B13_B14_RECENT_OFFICIAL.md, DATA_DICTIONARY, catálogo, AGENT_PROPOSALS, AI_TOOLS_USED, worklog y pytest XML.

## Bloqueos, dudas y decisiones pendientes
- Proyección anterior al corte no disponible; revisión humana INEC y AP-012 pendientes. Support validity humana no medida. Los titulares no coinciden en medida/valor/fecha para confirmar su afirmación central.
- Manifest SHA-256: 6d7542a1b5e508340dde315c413d7954f4dddddd035996cfdae9c6c210f35535.
- CSV SHA-256: 8288ad7479f6a6dc7afd6b58b3565e7467f2089ea1e83fd025d7acac9c451cbd.
- Reporte SHA-256: 0f9fb7e8b9d801b3667784b6ee69fe2da148a09a00f9f624163a57f358cfab4d.

## Contexto que no está en el código
Python global no tiene pytest; usar .venv. Modelos y herramientas en models/, ignorado. Ollama iniciado oculto, logs models/ollama-recent-serve.*, puede seguir sirviendo en 127.0.0.1:11434. OLLAMA_MODELS=models/ollama, OLLAMA_VULKAN=1. Precálculo SCAYL_INTEL=ai, SCAYL_LLM_MODEL=qwen3:8b, caché dedicada indicada arriba. GH usa credencial Git autorizada solo en memoria; helper/cuerpo tmp/ ignorado. Antes de cada push rev-list origin/main..HEAD filtro zip/rss.xml debe quedar vacío; nunca push --all ni subir backup/wip-617d6e2.
