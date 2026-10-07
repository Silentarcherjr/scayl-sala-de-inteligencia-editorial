# B-13/B-14 · Evidencia ACP e INEC para C-01

Adición autorizada: manifest **v1.1**, corte `2026-10-01T00:00:00Z`. Padre archivado
byte por byte en `manifest.before-97a5cd2b7ac6.json`; ningún raw anterior modificado.
`fuentes.recientes.json` amplía `fuentes.json`; el manifest reúne ambas listas.
ZIP GKG y RSS con descripciones siguen siendo solo locales.

| Serie | Período | Filas | Valores disponibles |
|---|---|---:|---:|
| ACP.GATUN.NIVEL | 2025-09-02 → 2026-09-30 | 394 | 394 |
| ACP.GATUN.PROYECCION | misma cuadrícula solicitada | 394 | 0; todos null |
| INEC.IPC.VAR_MENSUAL | 2025-09 → 2026-08 | 12 | 12 |
| INEC.IPC.VAR_INTERANUAL | 2025-09 → 2026-08 | 12 | 12 |

**812 filas**, 394 valores nulos; claves únicas (serie, período), 13 columnas del contrato.
`load_snapshot` las devuelve además de las 540 observaciones WB.

## Fuentes y ausencias

- [ACP](https://evtms-rpts.pancanal.com/eng/h2o/index.html): CSV histórico y proyección
  originales con recibos SHA-256 en `responses/acp/`. **Estimación informativa**; sin
  licencia abierta declarada. Solo datos numéricos, sin dashboard ni gráficos. Períodos
  son fechas civiles declaradas por ACP (Panamá); extracción UTC. Sin interpolación.
- Proyección obtenida después del corte: fechas 2026-10-07..2026-12-06, sin prueba de emisión
  anterior al corte. No se admiten esos valores ni se reconstruye un pronóstico; cuadrícula
  solicitada null, `es_proyeccion=true`. **Falta una edición histórica oficial** para
  completar esa parte de B-13.
- [INEC, Anexo 4, página PDF 1](https://www.inec.gob.pa/archivos/A0705547520260914092740Anexo%204.pdf):
  IPC nacional urbano, base 2024=100. Publicado 14/09/2026 según índice oficial guardado.
  Codex transcribió variaciones con signos y precisión originales, sin recalcular desde
  índices redondeados. PDF, recibo y transcripción identificada por hash en `responses/inec/`.
  **Cotejo humano pendiente**; INEC declara CC BY 4.0. Septiembre 2026 no publicado al corte.

## Medición guardada

`eval/results/b13-b14-evidence-before-after.json`: mismos titulares, temas, grupos E5,
τ=0,87 y reglas a ambos lados; solo cambian indicadores. Sin LLM ni ajustes con top 5.

| Estado | Antes | Después |
|---|---:|---:|
| suficiente_para_borrador | 0 | 0 |
| parcial | 131 | 131 |
| insuficiente | 34 | 34 |
| Total | 165 | 165 |

Cinco eventos reciben contexto ACP; ninguno tiene coincidencia numérica/temporal de nivel
observado que sustente su afirmación central. Los titulares de calado describen otra medida;
no hay titulares IPC coincidentes. Los parciales ya tenían contexto oficial.

**AP-012 abierta:** EVT-0161, homicidios/restricciones nocturnas, recibe contexto irrelevante
de Gatún por una palabra genérica. Se propuso al Lead acotar pertinencia y separar calado de
nivel del lago. Su módulo no fue modificado; la medición conserva las reglas y esa limitación.

## Reproducción

```powershell
python -m scayl.ingest.recent_official data/raw/v1
python -m scayl.ingest.manifest data/raw/v1 --verify
python -m pytest -q
# Requiere E5 local; no modifica data/processed:
python -m scayl.eval.recent_official
```

Adquisición con `scayl.ingest.common.download`: URL, UTC, HTTP, SHA-256 y bytes originales.
Adaptador offline valida la huella del PDF. `declare_addition(parent_sha256=..., version='v1.1')`
archiva el padre y rechaza modificaciones de raw previo; congelador normal sigue inmutable.

## Precálculo local

GNU Make ausente en Windows; se ejecutó su receta exacta:

```powershell
$env:SCAYL_INTEL = 'ai'
$env:SCAYL_LLM_MODEL = 'qwen3:8b'
$env:SCAYL_LLM_CACHE = 'data/cache/llm/recent-official-20261007'
python -m scayl.pipeline build --snapshot data/raw/v1 --llm live --top 15
python -m scayl.eval.generation_summary
```

Ollama 0.40.0, AMD RX 9060 XT 8 GiB, Vulkan, **37/37 capas GPU**; E5 CPU.
Caché dedicada inicialmente vacía. Resumen y copia del reporte de metadatos en
`eval/results/b13-b14-precompute.json` y `b13-b14-generation_report.jsonl`.
Bundle/fichas/caché permanecen locales; **data/processed no se sube**.
Cobertura: citas en brief/guion conservados, con disclaimers en denominador; no equivale a
validez de apoyo. Latencia: respuestas exitosas Story Studio live, no llamadas claims ni
caché/fallback; p95 lineal (tipo 7), mediana y tamaño de muestra en el resumen guardado.

Resultado real: **15 live**, 0 fallback; mediana **15068 ms**, p95 **17755 ms** (n=15).
Cobertura de citas conservadas **49/49**, 68 oraciones generadas y 63 conservadas
(incluye copy); cinco eliminaciones: tres STATUS_MISMATCH y dos UNCITED_FACT.
