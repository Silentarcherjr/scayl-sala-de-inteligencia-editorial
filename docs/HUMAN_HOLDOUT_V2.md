# Red-team v2: preguntas humanas y expectativas originales

`frictionspp-svg` escribió diez preguntas nuevas y sus expectativas de abstención
en la conversación, sin que se le mostraran `qa.py` ni `eval/redteam/cases.jsonl`.
Se guardaron literalmente en `eval/redteam/holdout_v2.jsonl`, con IDs HV2-01–10.
La respuesta original, revisor, hora UTC y hash están en
`eval/redteam/holdout_v2.provenance.json`. No se cambiaron preguntas ni expectativas.

Se ejecutó el runner existente, sin modificar código:

```bash
python -m scayl.eval.redteam --cases eval/redteam/holdout_v2.jsonl --output eval/results/holdout-v2.json
```

| Resultado | Num/den | Interpretación |
| --- | --- | --- |
| Abstenciones esperadas observadas | 6/6 | Todos los casos con expectativa humana de abstención |
| Abstenciones en controles con expectativa de respuesta | 4/4 | Menor es mejor; discrepancia respecto a lo esperado por el humano |
| Controles respondidos | 0/4 | No se respondió ninguno de los cuatro |
| Coincidencias con expectativas | 6/10 | Cuatro fallos HV2-03, HV2-05, HV2-07 y HV2-09 |
| Sondas del validador | no medido | Este set no contiene sondas |

Los cuatro controles preguntan por historia/geografía/moneda. El runner se abstuvo
por falta de evidencia pertinente en su corpus. `answerable_control` es la categoría
necesaria para contabilizar la expectativa humana de respuesta: no prueba que el
fixture contenga su respuesta. Por ello, 4/4 es **abstención falsa respecto a estas
expectativas**, no evidencia de rechazo de cuatro respuestas respaldadas por el corpus.
No se añadieron datos externos ni respuestas de conocimiento general para mejorar
el resultado. Los fallos se conservan y registran en 06.

El runner usa su fixture sintético y modo template/extractivo: no evalúa el bundle
real C-01, un LLM vivo ni el set reservado oficial del jurado. Estas diez preguntas
son un holdout humano respecto al desarrollo previo del código; no se afinó código
después de verlo. No demuestran resistencia general a ataques desconocidos.

El reporte original mantiene un `scope` fijo que dice «escrito por IA» y «sin gold
humano». Es una limitación de metadatos del runner. Se preservó el reporte sin
alterarlo; `eval/results/holdout-v2-summary.json` declara la procedencia humana,
conserva `raw_runner_scope` y copia los números sin cambios. Ambos reportes y la
copia archivada por el runner tienen hashes auditados.
