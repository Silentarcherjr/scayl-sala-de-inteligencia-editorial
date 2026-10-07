# B-09 · Revisión humana de sustento

`data/labels/support_review.csv` contiene 30 afirmaciones únicas de paquetes públicos baseline,
modo **template**. No mide la calidad de un LLM vivo. El algoritmo recorre el primer enunciado factual
de cada paquete por rondas brief/script; es una muestra determinista, no aleatoria. El meta adjunto
congela SHA del bundle y de las columnas inmutables. No se sube el bundle procesado.

El humano lee `statement` (oración del paquete) y `evidence_json` (afirmaciones citadas y sus referencias:
campo, valor/texto, período y URL). Debe evaluar **sustento por esa evidencia**, no verdad de la noticia.
Una declaración atribuida puede estar sustentada por el titular sin que el hecho declarado esté confirmado.

Completar solo:

- `decision`: `sí`, `no` o `parcial`; dejar vacía si aún no revisó.
- `reviewer`: nombre o identificador del humano.
- `reviewed_at_utc`: fecha/hora UTC ISO8601, por ejemplo `2026-10-07T18:00:00Z`.
- `comment`: motivo opcional, recomendable para no/parcial.

Métrica estricta = filas sí / todas las filas revisadas. Parcial no suma al numerador y aparece en
fallos, separado de no. Hasta completar toda la muestra (>=30), `support_validity` sigue **no medido**;
se informa el progreso sin presentar un parcial sesgado como resultado final. No rellenar etiquetas con IA.

```bash
python -m scayl.eval.support_review  # exporta; rechaza sobrescribir etiquetas
python -m scayl.eval.support_review --measure
python -m scayl.eval.run --snapshot v1 --support-review data/labels/support_review.csv --redteam-report eval/results/redteam-latest.json
```

B-08 detecta el CSV por defecto, valida integridad y archiva CSV+meta con la ejecución. Antes de revisar
otra generación, exportar otro archivo con `--output`; no atribuir etiquetas a textos distintos.
En esta sesión el humano tiene copia estable en `tmp/b09/` mientras el agente cambia de rama.
Resultado pendiente de sus etiquetas. Este PR no rellena respuestas ni reclama B-09 medida.
