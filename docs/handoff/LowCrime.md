# Relevo · LowCrime · 2026-10-07 05:14 UTC

- **Motivo de la parada:** relevo preventivo al cerrar el bloque solicitado (AGENTS §2b).
- **Rama:** worker-a/redteam-deploy · **Último commit de implementación:** be92dbe (empujado: sí); relevo en commit posterior.
- **PR abierto:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/32 (hacia main; no mergeado por este agente).

## Tarea en curso
B-12 y ampliación B-08 entregadas para revisión. A-06 preparada localmente; publicación explícitamente
pendiente de confirmación del Lead. No quedan cambios de implementación sin commit.

## Hecho en esta sesión
- Fetch + merge limpio de origin/main a 61ee2fa, integración de PR #25/#26/#27 vía #29. Rama nueva desde main.
- Baseline de pruebas integrado: 146 passed. Leídos AGENTS, LowCrime (sin notas pendientes nuevas), relevo,
  arquitectura, tareas, PLAN_REVIEW §2, propuestas, bitácoras y DL-024/025.
- B-12: 16 ataques (inyección en titulares, cifras, actualidad histórica, sin respuesta) + cuatro controles.
  Set sintético de desarrollo anotado por IA en eval/redteam; no gold humano ni set reservado.
  Runner usa service.ask(template) real, corpus temporal y validador real; no modelo ni red.
  Guarda originales, sondas, rechazos y hashes; restaura rutas/cachés incluso ante excepción.
- Medido: abstención correcta 6/16; incorrecta 0/4; resistencia estricta 6/16; controles 4/4; sondas 9/9.
  RT01–04 devuelven instrucciones del titular. RT05–06/RT09–12 devuelven contexto sin abstenerse.
  No afirmar que estos últimos inventan cifras. AP-012 deja corrección de qa.py al Lead.
- B-08: --redteam-report archiva evidencia y recalcula num/den desde observaciones. Sin argumento,
  sigue no medido. P@5 pública baseline 1/5 con DL-024; generación viva, latencia y soporte humano no medidos.
- Ejecutado equivalente Python exacto de make public-bundle en Windows, SCAYL_INTEL=baseline:
  187 señales → 183 eventos. news.descripcion nulas; cero cache LLM local, 183 paquetes template.
- A-06: deploy/prepare.py crea paquete allowlist, Dockerfile, Secret de runtime, envoltorios de acceso
  por contraseña para todas las páginas, cache forzada y cierre de sesión. Rutas directas comprobadas.
  UI solo ofrece cache cuando SCAYL_HOSTED=1; modos reales de salida preservados.
- Paquete final local ignorado: deploy/stage-final. Inventario publicado en deploy/preparation-report.json.
  deploy/stage es anterior; NO usar. Limpieza automática bloqueada por política, se conservó y se creó otro.
- Capturas Chromium locales a06-space-login.png y b12-abstencion.png, 1280×720; login por /Trust_Lab,
  métricas reales y logout verificados. Servidor y Chromium cerrados al terminar.

## Siguiente paso concreto
1. Sincronizar con main como ordena AGENTS (ante conflictos detenerse). Revisar PR #32 y AP-012.
2. El Lead decide/arregla ruta extractiva y política temporal/premisas. No cambiar sus archivos sin decisión.
3. Tras su cambio, repetir runner y B-08 conservando originales/fallos, sin adaptar expectativas para obtener verde.
4. Para A-06: obtener caché pública revisada de B-10 si se exige IA precalculada. Repetir public-bundle y
   preparar carpeta NUEVA. El inspector estructural detecta descripcion/ref, no paráfrasis de cachés antiguas.
5. Probar build Docker con motor activo (aquí no estaba), luego pedir/esperar confirmación del Lead antes
   de crear/subir el Space. Debe ser privado; contraseña de app no protege archivos de un repo público.
   Configurar SCAYL_SPACE_PASSWORD como Secret, probar recorridos remotos; todavía no hay URL desplegada.

## Estado de las pruebas
python -m pytest -q --junitxml=eval/results/pytest-redteam.xml → 156 passed (10 nuevas, incl. parametrización).
No pruebas omitidas/desactivadas. La suite verde comprueba el evaluador y hosting; NO implica resistir
los 16 ataques: diez fallos de producto registrados. Pruebas de acceso, rotación, logout, rutas directas,
cache obligatoria, aislamiento offline, contabilidad y restauración tras error. Fallos/correcciones en 06.
Artefacto B-08 final runs/20261007T051054682410Z.json y sus .pytest.xml/.redteam.json; latest idéntico.
Hashes de entradas y de todos los archivos del stage final comprobados.

## Archivos tocados
- scayl/eval/redteam.py, run.py; eval/redteam/**, eval/results/**; tests/test_redteam.py.
- deploy/** (sin stages), README.md, app/pages/2_Consultas.py (solo selector hospedado); tests/test_deploy.py.
- Capturas, docs/B08_EVALUATION.md, AGENT_PROPOSALS AP-012, 06, AI_TOOLS_USED, worklog y relevo.
- Sin cambios de contratos, dependencias, A-05/A-10, TASKS, tablero ni decision log.

## Bloqueos, dudas y decisiones pendientes
- AP-012 ABIERTA: corregir el código del Lead. El PR de evaluación no reclama resistencia perfecta.
- A-06 sin publicar por instrucción humana. Docker/HF no medidos; no credenciales HF utilizadas.
- Sin cache LLM local: el paquete funciona con fallback template. No describirlo como inferencia precalculada
  efectivamente medida. Banner explica la caída a template, salida conserva metadatos reales.
- Métricas no medidas siguen no medido. No mezclar baseline183 con evaluación E5 de B-05 (165 eventos).

## Contexto que no está en el código
Repo: C:/Users/Cbast/Downloads/scayl-sala-de-inteligencia-editorial-main/scayl-working.
Python global no tiene pytest. Usar .venv/Scripts/python.exe, o anteponer .venv/Scripts a Path.
Comandos:
  python -m scayl.eval.redteam
  python -m pytest -q --junitxml=eval/results/pytest-redteam.xml
  python -m scayl.eval.run --snapshot v1 --pytest-report eval/results/pytest-redteam.xml --redteam-report eval/results/redteam-latest.json
  python -m scayl.pipeline build --snapshot data/raw/v1 --llm cache --top 15 --public
  python -m deploy.prepare --out deploy/stage-NUEVO
No pasar stdout de eval a Select-Object -First: cierra el pipe y devuelve error aunque guarde artefactos.
Preview final usó cwd stage-final, PYTHONPATH al stage, SCAYL_HOSTED=1, estado temporal y contraseña solo
sintética local (no reutilizar para HF). Puerto8516, Chromium9226; ambos cerrados. Script de captura en TEMP.