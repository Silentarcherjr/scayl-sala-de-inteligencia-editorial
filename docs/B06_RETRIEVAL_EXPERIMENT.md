# B-06: recuperador opcional y aislado

`scayl.intel.retrieve.Retriever` ofrece `search(query, k)` con resultados
`(evidence_id, score, EvidenceRef)`. Usa un índice por instancia, sin estado global
ni dependencias nuevas. `hybrid=False` es el valor predeterminado: no carga E5.
`hybrid=True` activa el modelo multilingüe local ya disponible en B-05.

```python
from scayl.intel.retrieve import Retriever, units_from_bundle
index = Retriever(units_from_bundle(bundle), hybrid=True)
hits = index.search("nivel del lago Gatún", k=5)
```

BM25 usa IDF positiva de Robertson, k1=1.5, b=0.75; normaliza con s/(1+s).
El híbrido promedia esa puntuación con el coseno E5 recortado a [0,1]. Los empates
se ordenan por ID. Los puntajes son similitudes, **no probabilidades**. No se ha
calibrado un umbral de abstención; no se reutiliza el umbral de Consultas.

Las unidades son titulares, valores con período y unidad de WB/ACP/INEC y
magnitudes USGS. No se indexan cuerpos ni descripciones. Se excluyen noticias
marcadas por el escáner de inyección (también si la inyección está en descripción),
consultas con inyección y valores nulos; un cero observado sí se conserva.
Las proyecciones se identifican explícitamente. No se interpreta como evidencia
del presente ni como confirmación una coincidencia semántica o un dato histórico.

El caller debe suministrar un bundle curado; recuperar no aplica las guardias
de período, premisa falsa, actualidad o validación de respuesta de `qa.py`.
**No se integra con Consultas**: sustituir su recuperador exige propuesta y
decisión del Lead, con evaluación independiente de abstención y seguridad.

Validación: cuatro pruebas nuevas para flag, búsqueda sin solapamiento léxico con
vectores sintéticos, orden estable, campos de citas, nulos/cero, inyección y
vectores inválidos. `python -m pytest -q`: 176 passed. Ruff de los dos archivos
nuevos: verde. El smoke con E5 real y snapshot C-01 guarda tres consultas
ejecutadas (3/3) en `eval/results/b06-smoke.json`. Ese smoke demuestra funcionamiento,
no mide P/R, soporte, calidad humana ni latencia Q&A: **no medido**.
