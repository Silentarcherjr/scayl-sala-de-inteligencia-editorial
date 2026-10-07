# Worklog · worker-b

> Solo agregar. Formato: `AAAA-MM-DD HH:MM UTC · tarea · qué se hizo · resultado/commit`.

2026-10-06 21:40 UTC · B-01/B-02 · Codex leyó AGENTS, arquitectura, contratos, fixture, decisiones, catálogo, TASKS y PLAN_REVIEW §2. Rama propia `worker-b/snapshot`. Implementados fetchers públicos sin credenciales, respuestas inmutables con recibos SHA-256, manifest verificable, exportador ciego y diccionario. No se modificaron contratos, dependencias, tablero ni decision log.

2026-10-06 21:40 UTC · B-01 · Auditoría guardada en `data/raw/v1/acquisition-20261006T2140.json`: 300 titulares GDELT únicos combinados (DOC parcial + GKG), 0 TVN en esas respuestas; 540 observaciones WB, 0 nulos; 82 sismos; RSS 152 entradas, 48 publicadas dentro del intervalo oficial. DOC dio 429 repetidamente; GKG conservó ZIPs originales y registró 76 filas inválidas. Extracción parcial, no snapshot final. No se aplicó ventana reciente ni se inventaron fechas.

2026-10-06 21:40 UTC · Gobernanza · AP-008: 6×6×15=540, no 1.350; AP-009: usar las 48 entradas históricas que realmente conserva RSS ampliando la cobertura TVN. Ambas ABIERTAS, preguntadas al humano. Adaptador local preparado y probado; no se aplicó al corpus. Candidatos ciegos pendientes hasta congelar snapshot.

2026-10-06 21:40 UTC · Calidad · `.venv/Scripts/python -m pytest -q --junitxml=docs/worklog/worker-b-pytest.xml`: 76/76 pasan. Entorno real Windows, Python 3.14 (único Python disponible); dependencias fijadas originales, sin editarlas. Fallos reales de extracción y correcciones documentados en 06. Bitácora de herramientas IA actualizada.

2026-10-06 21:40 UTC · Preparación B-10 · Ollama portable 0.40.0 y GitHub CLI portable 2.102.0 en `models/tools`, ignorado por Git, verificados con SHA-256 oficial. Ollama escucha solo en 127.0.0.1:11434; qwen3.5:9b (6,6 GB) y qwen3:8b (5,2 GB) aparecen instalados. Hardware detectado por Ollama: AMD Radeon RX 9060 XT, 8 GiB, backend Vulkan; no RTX 4060. Benchmark: no medido. Descargas HF de los tres embeddings iniciadas sin token. GitHub CLI no tiene sesión autenticada; PR aún no abierto.

2026-10-06 21:43 UTC · B-01/B-02 · Descargas de los tres embeddings completadas según `models/embeddings-download.log`. Preparación del commit con datos estructurados y recibos: los ZIP GKG (~910 MB) y el RSS XML con descripciones permanecen solo locales; no se publican. `acquisition_inventory.json` inventaría sus SHA-256 y explicita estado parcial. Se añade `data/raw/.gitattributes` para impedir cambios de bytes por autocrlf. El PR debe ser borrador hasta completar el snapshot, empaquetado y decisiones AP-008/AP-009; no cierra B-01/B-02 todavía.

2026-10-06 21:56 UTC · Publicación y relevo · Por instrucción explícita del humano se mostraron status, branch -vv y log -10, y se ejecutó `git push -u origin worker-b/snapshot`: éxito, rama remota creada en eb61312. Git funciona con el remoto aunque gh no tenga sesión. Se detectó que el relevo solicitado no existía; se crea `docs/handoff/frictionspp-svg.md` con estado parcial, datos incluidos/locales, decisiones pendientes, pruebas y entorno, para subirlo en un segundo commit. Sin merge.


## 2026-10-07 02:35 UTC - Historial y manifest portable

Respaldo backup/wip-617d6e2 exclusivamente local; reconstruido historial sin ZIP/RSS y push normal 0997fb9 a origin/worker-b/snapshot. Los 117 ZIP y RSS permanecen en disco; 118 hashes y tamanos verificados. Manifest excluye auxiliares locales, valida inventario y lee corte YAML. Solo se anota disponibilidad del inventario previo por instruccion humana; hashes y respuestas intactos. AP-008/AP-009 actualizadas segun Lead. Pruebas: 99/99, docs/worklog/worker-b-manifest-pytest.xml; Python global sin pytest, usar .venv. Snapshot todavia no congelado.

2026-10-07 02:38 UTC - relevo preventivo: ver docs/handoff/frictionspp-svg.md. c1f67ae subido a origin/worker-b/snapshot; PR borrador #19. Siguiente: adquisicion C-01; B-01/B-02 incompletas.

## 2026-10-07T02:58:25.658387Z - B-01/B-02 C-01
Snapshot congelado: 187 noticias, 50 TVN; 159/22 en 90 dias. 540 WB, 82 USGS oficiales y 87 ampliados. RSS deteccion nula; GKG muestreo 18 UTC diario, DOC parcial por 429. Raw anteriores conservados y excluidos. Manifest y copia sin auxiliares verifican. 187 candidatos ciegos exportados y aviso dado al humano; no ranking real. Suite 114/114 (timeout UI inicial, repeticion pasa sin cambios). Ver worker-b-c01-verification.json y worker-b-c01-final-pytest.xml.

## 2026-10-07 04:47 UTC · B-05 IA
Sincronizado main por fast-forward a 2db3455. El borrador local de validate.py se preservó en data/cache/local-drafts/validate-before-dl024.py; se usa B-03 integrado por Lead. Rama nueva worker-b/b05-multilingual.
Implementados SentenceTransformerEmbedder E5 local y clasificación por prototipos. Calibración provisional sobre 32 titulares de 2025 y 488 pares anotados por Codex: 43 positivos, 445 negativos; τ=0,87, TP42 FP0 FN1 TN445. No es gold humano ni evaluación generalizable. No leyó C-01/top5.
Evaluación posterior: 183→165 eventos; P@5 exploratorio 1/5→1/5. Cuatro casos quedan separados: fechas 17/07, 15/08, 05/09 y 15/09/2026, mínimo 10 días; todas las parejas bloqueadas por límite de 7 días. Coseno francés menor que τ también. No se modificó horizonte ni pesos.
Medición real E5 en CPU (torch 2.14.1+cpu, CUDA no disponible). Matrices ignoradas en processed/v1/embeddings.npz. Resultados en eval/results/b05-dev2025-calibration.json y b05-c01-before-after.json. Integración SCAYL_INTEL=ai comprobada con tres noticias: 3 etiquetas/3 grupos.
129/129 pruebas pasan, worker-b-b05-pytest.xml. Carga nativa inicial falló en DLL sklearn después de PyTorch; verificación con orden inverso e implementación local de carga antes del modelo permitió ejecutar. No se relajó ninguna política Windows.

2026-10-07 04:50 UTC - relevo preventivo: ver docs/handoff/frictionspp-svg.md. B-05 PR #28; 129 pruebas pasan; 183 a 165 eventos, P@5 1/5 ambos. Siguiente B-13 ACP y B-14 INEC; precompute tras merge.

2026-10-07 05:07 UTC - B-13/B-14: merge limpio b6f5e08 desde main 61ee2fa; rama worker-b/recent-official-evidence. Adicion v1.1 con raw previos intactos: 394 niveles Gatun, 394 proyecciones null (fuera de corte), 24 INEC. Manifest verify []. Medicion E5: 165 eventos, antes/despues 0 suficiente,131 parcial,34 insuficiente. AP-012 contexto ACP irrelevante abierta. Precálculo equivalente a make (no instalado): 15 live qwen3:8b, Vulkan AMD RX9060XT 37/37 capas; mediana15068ms p9517755ms, citas49/49,0fallback. 152 pytest verdes. Resultados eval/results/b13-b14-*. No processed ni ZIP/RSS a Git.

2026-10-07 05:12 UTC - relevo preventivo: ver docs/handoff/frictionspp-svg.md. PR31; implementacion536e6c0;152passed;15live. Siguiente Lead AP-012,cotejoINEC y proyeccionhistorica.

2026-10-07 18:57 UTC - B-10: Benchmark GPU top15: 8b 14643/17600 ms, citas49/49, fallback0/15; 4b 9050/12898.2 ms, citas25/25, EMPTY_BRIEF3/15. Recomiendo8b. 172 pruebas verdes; reportes reales guardados.
