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
