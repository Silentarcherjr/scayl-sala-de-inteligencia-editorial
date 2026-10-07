# B-05 · Agrupación y temas multilingües

> **Actualización DL-029:** con 100 temas etiquetados por humanos, las reglas superan al clasificador por prototipos (macro-F1 0,76 frente a 0,25). Desde entonces `SCAYL_INTEL=ai` activa solo los embeddings E5 para agrupar; los temas usan reglas salvo `SCAYL_TOPICS=ai`.

`SCAYL_INTEL=ai` activa `SentenceTransformerEmbedder` y el clasificador por prototipos de la
taxonomía oficial. Modelo inicial: `intfloat/multilingual-e5-base`, ya aprobado en ARCHITECTURE §5.1.
Se carga desde `models/embeddings/intfloat--multilingual-e5-base` o la caché local; no se descarga
durante el pipeline. También acepta `SCAYL_EMBED_MODEL` y `SCAYL_EMBED_DEVICE`.
La inferencia medida fue **CPU**, PyTorch 2.14.1+cpu; no se declara ejecución GPU.

El modelo requiere prefijo `query: ` en tareas de similitud, incluso para idiomas distintos
del inglés ([ficha oficial](https://huggingface.co/intfloat/multilingual-e5-base)). Se conserva
el texto Unicode y se devuelve una matriz float32 normalizada L2. Imports de ML y carga de pesos
son diferidos. El clasificador selecciona el prototipo más cercano entre los siete valores
de `Topic`; su confianza es coseno, no una probabilidad calibrada ni un estado de evidencia.

## Calibración de desarrollo

- Fuente: 181 titulares DOC existentes de septiembre de 2025, fuera de C-01 (DL-018).
- 32 titulares seleccionados y 488 pares: 43 positivos, 445 negativos. Diez grupos de acontecimientos
  anotados provisionalmente por Codex a partir de titulares. **No son etiquetas humanas ni gold**;
  revisión humana y evaluación separada pendientes de B-07.
- Archivos: `data/labels/dev2025_news.jsonl`, `dev2025_cluster_pairs.csv`.
- Búsqueda predefinida: τ de 0,70 a 0,95, paso 0,01. Selección: F1 sobre pares de desarrollo;
  empate por precisión y luego τ más estricto. El calibrador rechaza datos desde C-01 y no abre
  `editor_top5.json`.
- Elegido τ=0,87: TP=42, FP=0, FN=1, TN=445, F1=0,988235. Es ajuste sobre el propio desarrollo,
  **no estimación de rendimiento generalizable**.
- Ejecución guardada: `eval/results/b05-dev2025-calibration.json`, con hashes de entradas.

## Evaluación posterior, sin modificar τ

`eval/results/b05-c01-before-after.json` registra el snapshot y la calibración por hash.
TF-IDF + reglas: **183 eventos**. E5 + prototipos: **165 eventos**.
P@5 exploratorio: **1/5 → 1/5**, sin ACP/INEC y con la asistencia previa al editor declarada en DL-024.
Cuenta los cinco puestos de eventos que contienen algún titular elegido; cobertura de titulares
elegidos se registra aparte, porque varios elegidos pueden caer en un solo evento.
No se usan esos resultados para seleccionar modelo, τ, prototipos o pesos.

Los cuatro casos solicitados siguen separados:

| Baseline | Fecha usada (detección, publicación desconocida) | Caso IA |
|---|---|---|
| EVT-0088 | 2026-09-05 | EVT-0078 |
| EVT-0127 | 2026-07-17 | EVT-0116 |
| EVT-0158 | 2026-08-15 | EVT-0143 |
| EVT-0096, francés | 2026-09-15 | EVT-0087 |

Todas las parejas están separadas por **más de 7 días** (mínimo 10, máximo 60), por lo que
la restricción temporal vigente impide reunirlas en un evento. Tres parejas en español
superan τ semánticamente; las parejas con francés tienen cosenos de 0,839 a 0,861, menores
que τ. Ambos diagnósticos se reportan; no se altera la arquitectura para forzar la unión.
Modificar el horizonte o añadir familias temáticas requiere propuesta y decisión del Lead.

## Reproducción y validación

```powershell
.\.venv\Scripts\python -m scayl.eval.calibrate_cluster
.\.venv\Scripts\python -m scayl.eval.compare_intel
.\.venv\Scripts\python -m pytest -q
```

El primer comando ajusta solo desarrollo; el segundo evalúa después del ajuste y escribe
`data/processed/v1/embeddings.npz` con ids, modelo y SHA-256 por texto (ignorado en Git).
Las métricas guardadas se obtuvieron con 187 noticias reales del snapshot v1. Las pruebas sin
pesos verifican normalización, Unicode, rechazo de resultados inválidos, lotes vacíos y taxonomía;
el modelo real se ejercitó en las ejecuciones guardadas. Suite: **129/129**.

El entorno Windows bloqueó una DLL de scikit-learn al cargarla después de PyTorch; se cargan
primero las dependencias nativas del agrupador. No se desactiva ninguna política del sistema.
`make precompute` queda pendiente de que el Lead mergee B-05, según la instrucción humana.
