# B-10: benchmark local del top 15

Ejecuciones reales del 7 de octubre de 2026, mismo snapshot C-01 y mismos
15 eventos en el mismo orden. E5 en CPU; Ollama local en AMD Radeon RX 9060 XT
8 GiB, Vulkan. No cambia el modelo predeterminado ni el ranking.

| Modelo | n Studio live | Mediana (ms) | p95 (ms) | Citas conservadas | Fallback por validación |
| --- | ---: | ---: | ---: | ---: | ---: |
| qwen3:8b | 15 | 14643 | 17600 | 49/49 | 0/15 |
| qwen3:4b | 15 | 9050 | 12898.2 | 25/25 | 3/15 |

El campo `mode=live` registra la llamada al modelo: los tres `EMPTY_BRIEF`
del modelo 4b también cuentan como respuestas live, pero el reporte indica
su fallback posterior. No confundir ambos campos.

8b generó 68 oraciones y conservó 64: eliminó 2 `UNCITED_FACT` y 2
`STATUS_MISMATCH`. 4b generó 49 y conservó 35: eliminó 7
`NUMBER_NOT_IN_EVIDENCE` y 7 `STATUS_MISMATCH`; además hubo 3 `EMPTY_BRIEF`
(estos son fallos de paquete, no otras tres oraciones eliminadas).

Recomendación para la demo: **qwen3:8b**. Entre los modelos medidos se exige
0 fallback, 15 muestras live y cobertura de citas >=95%; se elige la menor
mediana entre los elegibles. 4b mejora la latencia, pero no cumple el requisito
operativo de evitar briefs vacíos. Esta recomendación no mide veracidad.

Los reportes completos y sus hashes están en `eval/results/b10-*.json` y
`b10-*-generation_report.jsonl`. La corrida 8b es el precompute ya ejecutado
en `dc1a990`; la comparación verifica el orden exacto de los eventos. La
extracción de afirmaciones también usa el modelo, por lo que los prompts
de Studio pueden contener afirmaciones diferentes. Es una corrida por modelo,
n=15, sin intervalos de confianza. La latencia mide Studio, excluye extracción
de afirmaciones y no mide Q&A. La cobertura cuenta citas tras validar en brief
y guion, incluye disclaimers y excluye copy social; no mide validez del soporte
ni calidad editorial humana.

Para repetir, desde un checkout de main con modelos locales y Ollama:
copiar los reportes 8b guardados, usar una caché 4b nueva y vacía,
`SCAYL_INTEL=ai python -m scayl.eval.benchmark_packages`.
No subir `data/processed/`, cachés ni pesos de modelos.
