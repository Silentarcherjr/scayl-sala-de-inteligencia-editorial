# B-07 · Revisión humana asistida pendiente

`data/labels/topics_human.csv`: 100 titulares C-01 seleccionados sin ranking con semilla
20261007; tema_propuesto por E5, **tema_humano/confirmado/revisor pendientes**.
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

Estado actual: formularios preparados y solicitud enviada al humano; 0 etiquetas confirmadas.
La tarea está bloqueada en esa revisión. Se continúa el benchmark en un worktree para
mantener estos CSV disponibles y preservar ediciones humanas durante otras tareas.
