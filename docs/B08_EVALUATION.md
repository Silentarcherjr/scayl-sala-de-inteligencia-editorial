# B-08 · Evaluación reproducible

```powershell
python -m scayl.pipeline build --snapshot data/raw/v1 --llm template
python -m pytest -q --junitxml=eval/results/pytest-b08.xml
python -m scayl.eval.run --snapshot v1 --pytest-report eval/results/pytest-b08.xml
```

La ejecución escribe eval/results/latest.json y una copia fechada en eval/results/runs/, con el
reporte pytest archivado y hashes SHA-256 del bundle, las etiquetas y el reporte de pruebas.
No se versiona el bundle con descripciones RSS. El evaluador no llama a APIs ni al modelo.

## Resultado guardado
P@5 = **1/5 = 0,20**, sobre **183 eventos** del baseline TF-IDF + reglas, sin ACP/INEC.
Las noticias del editor se mapean mediante member_ids a eventos únicos; varias noticias del mismo
evento cuentan una vez. El denominador sigue siendo cinco posiciones del ranking del sistema.
Orden: P descendente, U descendente, event_id ascendente. No se cambian pesos para mejorar coincidencia.

| Noticia elegida | Evento | Posición |
|---|---|---|
| gdt-f63259a11c73800d786e | EVT-0088 | 2 |
| gdt-11224bbdacde85be739d | EVT-0096 | 22 |
| gdt-23509ef75cdfc7ffa759 | EVT-0117 | 12 |
| gdt-01a0b491689ea24c2bae | EVT-0158 | 6 |
| gdt-6d81d100f4164a825bf7 | EVT-0134 | 26 |

**Limitación DL-024:** el editor vio una propuesta de IA antes de elegir, coincidente en 1 de 5.
No vio el ranking del sistema ni la app con datos reales. La selección no es independiente sin
asistencia. P@5 es exploratoria y se recalcula cuando cambie el pipeline, sin reutilizar este número
como resultado del sistema futuro. La agrupación puede cambiar los eventos únicos seleccionados.

IDs ausentes/ambiguos, selección inválida, menos de cinco eventos o casos sintéticos producen
"no medido", sin convertir problemas de correspondencia en cero aciertos.

## Alcance y pendientes
Esta corrida mide P@5 y enlaza pruebas T01–T10 identificadas en el JUnit guardado. La suite de esta
rama tiene **127 passed**, seis pruebas nuevas de evaluación. Tests sintéticos/simulados no equivalen
a validación con LLM real ni al ensayo sin wifi. Fallos y skips quedan visibles si se adjunta otra corrida.

Cobertura/validez de citas, atribución, benchmarks de abstención, macro-F1, agrupación, tokens y
latencias permanecen con status "no medido" y valores nulos: no se calcularon en esta corrida.
Sus conjuntos etiquetados/evaluadores y mediciones de generación quedan pendientes. El costo de API
0,0 se refiere a este evaluador local; no estima hardware ni electricidad.

Trust Lab existente consume latest.json sin cambios en A-05. [Captura](screenshots/b08-evaluacion.png).
La limitación detallada está en el JSON y este documento; la vista del Lead muestra la marca exploratoria.
