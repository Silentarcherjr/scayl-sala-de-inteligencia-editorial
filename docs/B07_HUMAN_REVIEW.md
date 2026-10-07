# B-07 · Revisión humana asistida

`data/labels/topics_human.csv`: 100 titulares C-01 seleccionados sin ranking con semilla
20261007; tema_propuesto por E5, con tema_humano/confirmado/revisor completados
mediante revisión interactiva explícita de `frictionspp-svg`.
Rellenar tema_humano con uno de los siete temas, confirmado=si y revisor. No basta con
tema_propuesto para obtener una métrica humana.

`dev2025_groups_human.csv`: 32 titulares de desarrollo, fecha y grupo provisional derivado
de pares anotados por Codex. El humano confirma/corrige grupo_humano, confirmado y revisor.
La equivalencia de grupos deriva las 488 etiquetas de pares; así no necesita marcar cada
pareja por separado. Mismo evento, no desarrollos distintos de una historia; regla temporal
de siete días. Revisión asistida, no gold ciego. Revisor debe mirar todos los 32 titulares.

```powershell
python -m scayl.eval.human_labels prepare
# Tras completar ambas revisiones (sin cambiar tau/prototipos ni ranking):
python -m scayl.eval.human_labels evaluate
```

El preparador no sobrescribe formularios existentes. Evaluación guarda
`eval/results/b07-human-metrics.json`: macro-F1 de temas baseline/IA (siete clases,
zero_division=0) y TP/FP/FN/TN, P/R/F1 en los pares. Exige al menos 100 temas revisados
y todos los titulares de los pares antes de medir cada componente. Sin revisión, **no medido**.
El desarrollo ya se usó para calibrar τ provisional: los resultados no son generalización
a un conjunto reservado. No se recalibra ni se lee editor_top5.

La revisión interactiva registra únicamente confirmaciones o correcciones explícitas del
humano, con revisor `frictionspp-svg`. `data/labels/human_review_log.jsonl` conserva la
respuesta original, los IDs, propuesta y etiqueta humana, y la hora UTC de cada bloque.
El CSV conserva su esquema; la hora se vincula por ID mediante esta bitácora. No se copian
propuestas a etiquetas humanas sin autorización explícita.

Estado: revisión en curso en `worker-b/human-inputs`; el conteo actual se obtiene de las
filas con `confirmado=si`. Las métricas se vuelven a ejecutar al terminar todos los bloques.

Temas completados el 2026-10-07: 100/100 etiquetas explícitas de `frictionspp-svg`.
La ejecución guardada en `eval/results/b07-human-metrics.json` mide macro-F1
baseline=0.7568136932192232 e IA=0.24645960051496715, sobre las siete clases
oficiales (`zero_division=0`). No se ajustaron modelos, prototipos ni umbrales con
estas respuestas. Es revisión asistida con propuestas visibles; no gold ciego.
Agrupación completada el 2026-10-07: 32/32 titulares revisados explícitamente por
`frictionspp-svg`, en cuatro bloques (10/10/10/2); confirmó las propuestas mostradas.
La equivalencia de esos grupos deriva las etiquetas de los 488 pares de desarrollo.

| Método | Precisión | Recall relativo al pool | F1 | TP/FP/FN/TN |
| --- | --- | --- | --- | --- |
| baseline | 12/12 = 1.0 | 12/43 = 0.2790697674 | 0.4363636364 | 12/0/31/445 |
| IA | 42/42 = 1.0 | 42/43 = 0.9767441860 | 0.9882352941 | 42/0/1/445 |

Estos pares de desarrollo de 2025 ya se usaron para calibrar τ con etiquetas
provisionales. La revisión asistida no transforma el conjunto en un holdout ni
estima recall absoluto sobre todos los eventos posibles. Los modelos, τ y los
prototipos permanecen sin ajustar con esta revisión. En temas, IA tiene menor
macro-F1 que el baseline en este conjunto; no se oculta ese resultado.

La auditoría en `eval/results/b07-human-review-summary.json` comprueba 100/100 temas
y 32/32 grupos contra la bitácora y conserva sus hashes y los del evaluador.
Validación tras completar B-07: 188 pruebas y `ruff check .` verdes.
