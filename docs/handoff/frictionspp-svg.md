# Relevo · frictionspp-svg · 2026-10-07 04:50 UTC

- **Motivo de la parada:** relevo preventivo al cerrar B-05 IA, AGENTS §2b; sin porcentaje fiable de sesión.
- **Rama:** worker-b/b05-multilingual · **Último commit de implementación:** e31c66d (56632bb implementación principal). El relevo queda en commit posterior; se empuja toda esta rama.
- **PR abierto:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/28 hacia main, listo para revisión. Solo el Lead mergea.

## Tarea en curso
B-05 IA implementada y medida. B-13 ACP, B-14 INEC, B-07 humano y B-10 pendientes.
El usuario cambió prioridad: B-05 primero, luego ACP/INEC, luego etiquetas/benchmark. make precompute solo cuando B-05 esté mergeado.

## Hecho en esta sesión
- Fetch y merge de main: fast-forward a 2db3455. Main ya contiene snapshot C-01 (PR #19), B-03 y baseline (DL-023), top5 del editor y DL-024.
- Borrador local antiguo de validate.py preservado en data/cache/local-drafts/validate-before-dl024.py, ignorado. Se usa la implementación del Lead.
- Rama propia worker-b/b05-multilingual.
- SentenceTransformerEmbedder: intfloat/multilingual-e5-base local, Unicode, query prefix, float32 L2 normalizado; imports/pesos diferidos; sin red ni nuevas dependencias. CPU por defecto, SCAYL_EMBED_DEVICE opcional.
- topics_ai.classify: prototipos de los siete temas oficiales; confianza es coseno, no probabilidad/verdad.
- 181 titulares DOC septiembre 2025 conservados para desarrollo. 32 anotados provisionalmente por Codex, diez grupos, 488 pares (43 positivos/445 negativos). NO gold humano; B-07 pendiente.
- Calibración SOLO desarrollo: rejilla predefinida 0,70–0,95 paso 0,01; F1, desempate precisión y τ estricto. Seleccionado τ=0,87, TP42 FP0 FN1 TN445. DEFAULT_TAU actualizado. Calibrador rechaza C-01 y no abre editor_top5.
- Evaluación posterior C-01 con τ fijado: 183→165 eventos; P@5 exploratorio 1/5→1/5. Cuatro casos solicitados NO se agrupan.
- Diagnóstico: EVT-0127 17/07; EVT-0158 15/08; EVT-0088 05/09; EVT-0096 francés 15/09/2026. Todas las parejas exceden 7 días (mínimo10/máximo60). Cosenos españoles >0,87; franceses 0,839–0,861. No se cambió el guard temporal ni pesos para forzar coincidencia.
- Medición REAL en CPU (torch 2.14.1+cpu, CUDA no disponible), no GPU. E5 pesos disponibles en models/embeddings/intfloat--multilingual-e5-base.
- Resultados guardados eval/results/b05-dev2025-calibration.json y b05-c01-before-after.json. Matriz real y hashes de textos en data/processed/v1/embeddings.npz, ignorado.
- Se comprobó integración SCAYL_INTEL=ai con 3 noticias: 3 etiquetas y 3 grupos.
- Atributos específicos -text para entradas dev2025 y resultados B05: hashes guardados coinciden ahora con blobs Git, incluidos CSV/JSON con CRLF.
- Ningún ZIP ni rss.xml con descripciones se publica. backup/wip-617d6e2 permanece EXCLUSIVAMENTE local.

## Siguiente paso concreto
1. Sincronizar rama con main y revisar decisiones. El PR #28 está para el Lead; no mergearlo.
2. Continuar B-13 ACP y luego B-14 INEC según TASKS; snapshot v1 ya congelado: adición declarada v1.1/nuevo inventario y recibo, nunca sobrescribir bytes raw previos. Una rama por bloque.
3. B-07: revisión/etiquetas humanas, pool de pares DL-016, etiquetas de temas ≥100. Las anotaciones provisionales de 2025 no reemplazan gold humano. No retocar τ/prototipos/pesos usando C-01 o editor_top5.
4. B-10 benchmark: hardware AMD RX 9060 XT Vulkan para Ollama; PyTorch actual es CPU. No inventar métricas GPU.
5. Cuando B-05 esté mergeado, ejecutar make precompute en máquina de demo según instrucción humana. El top5 ya existe; asistencia previa al editor declarada en DL-024.

## Estado de las pruebas
.\.venv\Scripts\python -m pytest -q --junitxml=docs/worklog/worker-b-b05-pytest.xml → 129 passed.
Pruebas sin pesos: Unicode, L2 float32, lotes vacíos, salida inválida, taxonomía, guard de 7 días y rechazo de C-01 en calibración. Modelos reales ejercitados en ejecuciones guardadas.
Imports nativos fallaron inicialmente bajo política DLL Windows; ejecutar fuera del sandbox y cargar dependencias de clustering antes del modelo permitió ejecutar. No se desactivó seguridad Windows.
Python global no tiene pytest; usar .venv.

## Archivos tocados
scayl/intel/embed_st.py, topics_ai.py, cluster.py; scayl/eval/calibrate_cluster.py, compare_intel.py; tests/test_intel_ai.py.
data/labels/dev2025_news.jsonl, dev2025_cluster_pairs.csv y .gitattributes; eval/results/b05-*.json y .gitattributes.
docs/B05_MULTILINGUAL.md, docs/AI_TOOLS_USED.md, docs/worklog/worker-b.md, worker-b-b05-pytest.xml.

## Bloqueos, dudas y decisiones pendientes
- Cuatro titulares no pueden formar un evento con el guard vigente de 7 días. Cambiar horizonte/familias temáticas sería transversal: proponer y esperar decisión; no hacerlo silenciosamente.
- P@5 cuenta puestos de eventos que contienen elegidos; cobertura de titulares seleccionados se registra aparte para evitar contar varias elecciones del mismo evento como varios puestos.
- Revisión humana de etiquetas pendiente. F1 de calibración es sobre el propio desarrollo provisional, no rendimiento generalizable.
- make precompute pendiente del merge humano de B-05.

## Contexto que no está en el código
- Modelos y herramientas en models/, ignorado. GH CLI models/tools/gh/bin/gh.exe. PR creado con credencial Git existente SOLO en memoria.
- tmp/ ignorado: cuerpo/helper del PR actual. No añadir indiscriminadamente.
- Rama remota de esta tarea: worker-b/b05-multilingual (nuevo pedido worker-b/*). Rama de snapshot anterior sigue separada. Nunca push --all ni subir backup.