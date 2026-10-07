# Relevo · frictionspp-svg · 2026-10-07 02:38 UTC

- **Motivo:** relevo preventivo al cerrar la corrección del historial y manifest, según AGENTS.md §2b (sin porcentaje fiable de sesión).
- **Rama local:** worker-b/frictionspp-svg. Upstream y destino exclusivo: origin/worker-b/snapshot.
- **Último commit de implementación:** c1f67ae, subido. Este relevo queda en un commit posterior.
- **PR:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/19 (borrador hacia main; solo el Lead mergea).

## Tarea en curso
B-01/B-02 siguen incompletas. Snapshot NO congelado. Esta sesión reparó el historial y la portabilidad del manifest; no adquirió noticias nuevas.

## Hecho en esta sesión
- backup/wip-617d6e2 apunta a 89c48c0: SOLO LOCAL, NUNCA SUBIR. Contiene ZIP y RSS con descripciones.
- Historial reconstruido desde a525a6f por instrucción humana; archivos recuperados en disco y retirados del índice. Exclusiones en .gitignore y merge normal 0997fb9, sin rebase ni force-push.
- Bitácora IA conserva filas de ambos lados en una tabla ordenada.
- Objetos a525a6f..HEAD sin ZIP ni rss.xml. Permanecen en disco 117 ZIP y RSS (195516 bytes).
- Manifest excluye auxiliares locales, comprueba sus hashes contra el inventario antes de congelar y lee corte de data_window.v1.yaml.
- acquisition_inventory.json: 118 hashes/tamaños verificados, anotados disponibilidad="solo local" por instrucción humana; respuestas raw intactas.
- AP-008 ACEPTADA (DL-013, 540 filas); AP-009 SUPERADA (DL-017). Las notas del Lead siguen pendientes.

## Siguiente paso concreto
1. Sincronizar con main y revisar notas del Lead. Nunca push --all ni subir backup.
2. Actualizar fetchers a scayl/config/data_window.v1.yaml: noticias [2025-10-02, 2026-10-01), 30 días previos al corte ampliables a 90. GDELT publicación nula; RSS publicación=pubDate y detección nula (el adaptador anterior aún usa extracción como detección: corregir con prueba).
3. Descargar DOC diario de ventana nueva, GKG como respaldo. Conservar raw 2025 y auditar fuera_de_ventana_C-01. Escribir salidas nuevas de forma inmutable.
4. Construir noticias deduplicadas, fuentes.json y eventos_ext.geojson (USGS ampliado separado del oficial 2024). Reconciliar inventario con nuevas respuestas sin sobrescribir bytes raw: build_manifest rechaza hashes locales ausentes/inconsistentes en inventario existente.
5. Congelar/verificar manifest y exportar candidatos ciegos. Actualizar catálogo/diccionario (aún contiene comandos históricos), pruebas y PR. Solo entonces borrar Notas del Lead pendientes.
6. Después B-13 ACP y B-14 INEC; luego B-03/B-04, B-11, B-05/B-07, B-06 y B-10. Sin UI (DL-020: LowCrime).

## Estado de las pruebas
.\.venv\Scripts\python -m pytest -q --junitxml=docs/worklog/worker-b-manifest-pytest.xml → 99 passed.
Dos pruebas nuevas: copia sin auxiliares verifica y detecta alteración del inventario; hashes inconsistentes impiden congelar.
No se verificó v1 congelado: aún faltan noticias.csv, fuentes.json y manifest. Python global no tiene pytest; usar .venv.

## Archivos tocados
.gitignore; scayl/ingest/manifest.py; tests/test_snapshot_fetchers.py; data/raw/v1/acquisition_inventory.json; docs/AGENT_PROPOSALS.md; docs/DATA_DICTIONARY.md; docs/AI_TOOLS_USED.md; docs/worklog/worker-b.md y reporte XML.

## Bloqueos, dudas y decisiones pendientes
- Falta cobertura nueva ≥100 noticias/≥20 TVN. Las cifras antiguas (300 GDELT, 540 WB, 82 USGS) no prueban cobertura C-01.
- No falta autorizar AP-008/AP-009.
- Usuario exige git push -u origin HEAD:worker-b/snapshot; no crear otra rama remota.
- tmp/ sin seguimiento: auditoría del WIP, cuerpo del PR y helper de autenticación sin secretos guardados. No añadir indiscriminadamente.

## Contexto que no está en el código
- El respaldo tiene archivos prohibidos para publicación; no subirlo.
- gh portable en models/tools/gh/bin/gh.exe, sin sesión propia. PR creado con credencial Git existente solo en memoria, sin mostrarla ni persistirla.
- Modelos/Ollama siguen locales en models/. GPU AMD RX 9060 XT 8 GiB Vulkan; benchmark no medido.