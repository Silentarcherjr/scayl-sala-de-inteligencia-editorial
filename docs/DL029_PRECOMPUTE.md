# Precálculo y caché pública después de DL-029

Ejecución sobre main `f951bb249fdcb5b163d15e2d8bbae91131075594`, del
2026-10-07T20:54:46Z al 2026-10-07T20:59:06Z. Snapshot C-01 sin modificar:
187 noticias, 165 eventos; manifest verificado, SHA-256
`6d7542a1b5e508340dde315c413d7954f4dddddd035996cfdae9c6c210f35535`.
DL-029 aplica temas por reglas (`SCAYL_TOPICS=baseline`) y agrupación E5
(`SCAYL_INTEL=ai`, `intfloat/multilingual-e5-base`). No se cambió código,
umbrales, pesos, modelos ni prompts.

GNU Make no está instalado en esta máquina Windows. Se ejecutó su receta exacta,
con una carpeta de caché nueva para exigir inferencia en vivo:

```powershell
$env:SCAYL_INTEL = 'ai'
$env:SCAYL_TOPICS = 'baseline'
$env:SCAYL_LLM_MODEL = 'qwen3:8b'
$env:SCAYL_LLM_CACHE = 'data/cache/llm/precompute-dl029-20261007T205446Z'
$env:SCAYL_EMBED_DEVICE = 'cpu'
$env:OLLAMA_HOST = 'http://127.0.0.1:11434'
python -m scayl.pipeline build --snapshot data/raw/v1 --llm live --top 15
```

Hardware: AMD Radeon RX 9060 XT 8 GiB, Ollama 0.40.0 con Vulkan;
37/37 capas del modelo en GPU, qwen3:8b Q4_K_M, contexto 4096, E5 en CPU.
Ollama estaba detenido al primer sondeo: se inició el servicio local oculto y
se comprobó el modelo antes de correr. Registro del fallo en `06_TESTS_AND_METRICS.md`.

Resultados guardados en `eval/results/dl029-precompute.json` y
`dl029-precompute-generation_report.jsonl` (huella del JSONL en el resumen):

| Métrica | Resultado medido |
|---|---|
| Studio en vivo / paquetes solicitados | 15/15 |
| Fallback / paquetes solicitados | 0/15 |
| Latencia mediana, n=15 | 13131 ms |
| Latencia p95, n=15 | 16997,5 ms |
| Cobertura de citas brief/guion conservados | 45/45 |
| Oraciones generadas / conservadas, incluye copy | 67 / 59 |
| Rechazos del validador | STATUS_MISMATCH: 1; NUMBER_NOT_IN_EVIDENCE: 4; UNKNOWN_CLAIM: 1; UNCITED_FACT: 2 |

Latencia de respuestas Studio exitosas, reloj de pared; no incluye llamadas de
claims. Percentil lineal tipo 7. Cobertura significa presencia de claim_ids en
brief/guion conservados, incluyendo avisos no factuales; excluye copy social.
Validez del apoyo y revisión humana de exactitud: **no medidas**.

El top 15 público anterior y el actual comparten 5/15 eventos. Los IDs y sus
entradas/salidas están en `eval/results/dl029-public-cache-audit.json`.
Nuevo orden: EVT-0101, EVT-0116, EVT-0078, EVT-0051, EVT-0083, EVT-0143,
EVT-0165, EVT-0081, EVT-0108, EVT-0107, EVT-0114, EVT-0133, EVT-0141,
EVT-0145, EVT-0160.

## Artefactos públicos y preparación del Space

`deploy/artifacts/v1/` contiene el bundle público y solamente las 30 entradas
consumidas (15 claims y 15 Studio). Se retiraron 20 claves obsoletas. El bundle
mantiene 15 paquetes cache y 150 template; no se cambian sus modos.
`PUBLIC_CACHE_REVIEW.json` registra procedencia, prompts, claves y hashes.

Antes de construir los prompts se verificó descripcion=null en 187/187 noticias.
Tras exportar se validaron 32/32 JSON con la guardia pública, incluido rechazo
de citas a descripcion; hashes y lista exacta de archivos coinciden con la auditoría.
Se aplicaron el esquema y los validadores reales del pipeline. La revisión del
agente no sustituye revisión humana del apoyo. La salida cruda de caché vuelve
a validarse al usarse.

Preparación local comprobada con el código existente:

```powershell
python -m deploy.prepare --bundle deploy/artifacts/v1/bundle.public.json --cache deploy/artifacts/v1/llm --out tmp/dl029-space-stage
```

118/118 archivos preparados coinciden con sus hashes; sus JSON pasan la guardia
pública y no contiene ZIP ni rss.xml. Stage, caché local, pesos y data/processed
permanecen ignorados. No se publicó el Space. LowCrime puede preparar un destino
nuevo desde estos artefactos después de la revisión del Lead; ver
`docs/PUBLIC_REVIEWED_CACHE.md`.

Validación local: 188 pruebas pasan; `ruff check .` en verde.
