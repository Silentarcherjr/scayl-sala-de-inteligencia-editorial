# Relevo · worker-web · 2026-10-08 16:03 UTC

- **Motivo:** relevo preventivo al cerrar DL-036.
- **Rama:** `worker-web/python-api` · **Último commit:** consultar `git log -1` (el commit de evidencia incluye esta nota y se empuja).
- **PR:** se abre tras el commit de evidencia; localizar por rama con `gh pr view worker-web/python-api`.

## Tarea en curso
DL-036, aprobada por el Lead vía usuario: consulta libre y revisión real en Next.js sin depender de Streamlit. Implementación y verificación terminadas; mergea el Lead. Corte duro 18:00 Panamá 8/oct: no mergear una versión inestable.

## Hecho en esta sesión
Dos handlers Python nativos en web/api, sin FastAPI/dependencias nuevas. Cuatro pins iguales al núcleo. Preparador copia scayl/bundle público/caché pública, no raw/labels/state. CacheOnlyLLM equivale a deploy.runtime.enforce_cache y fija modo/modelo/path, nunca live. API revisión valida REVIEW_TRANSITIONS y campos, genera recibo con hashes de evidencia/paquete/bundle/recibo sin persistencia. UI libre + fallback qa.json honesto, revisión con localStorage versionado, historial y descarga JSON. Avisos de no publicación y almacenamiento visibles. Streamlit solo respaldo en pie.

## Siguiente paso concreto
Revisar PR de worker-web/python-api (incluye cinco respuestas JSON reales y preview); el Lead mergea. Tras merge, comprobar dominio público /consultas/ y /caso/EVT-0101/#revision. No promover previews ni mergear desde este worker sin nueva autorización. No se requiere ni propone estudio con periodistas/analistas.

## Estado de las pruebas
287 pytest, Ruff, npm ci/lint/build, 173 páginas. Preview READY de código b697606: https://scayl-editorial-5ljnkhvsk-hacks10.vercel.app/. Cinco respuestas con paridad service.ask (solo timestamps variables excluidos), diez errores remotos, transiciones válidas/invalidas, recibo hash/download/reload (JSON exacto evita 10.0→10), fallo API sin decisiones. Wi-Fi apagado/restaurado en npx serve out, cinco pantallas y tres casos sin peticiones externas/errores; móvil sin overflow. Evidencia/capturas docs/screenshots/web/python-api-*.

## Archivos tocados
Solo web/, tests/test_python_api.py nuevo, README, AI_TOOLS_USED, worklog/handoff propios y screenshots. scayl/app/deploy/data/pruebas anteriores/lockfile sin cambios.

## Bloqueos, dudas y decisiones pendientes
Ninguno técnico; pendiente revisión/merge Lead. Preview protegido por Vercel: probado con token temporal dev del mismo proyecto, no publicado. Estado previo aportado por navegador; nombre de revisor no autenticado, no hay estado compartido. Avisos npm/ESLint preexistentes sin cambios. Notion opcional C-03; repo sigue privado hasta autorización final.

## Contexto que no está en el código
Proyecto hacks10/scayl-editorial (prj_JLxK8fBUTTiXBKfRJl57iVonjfL5), rootDirectory web. vercel.json framework null/output out permite estático + Python. Desplegar por Git con repo completo: CLI desde web/ envía raíz equivocada. CLI autenticado funciona; MCP get_project dio403 y se usó fallback CLI autorizado. .python-runtime generado ignorado; env.local con OIDC temporal solo para pruebas, no imprimir/commitear. Playwright y Node bundled, Python .venv. Servidor temporal55330 se termina al entregar; Wi-Fi se restaura con finally. Scripts de pruebas locales /tmp/scayl-api-{e2e,static,remote}.cjs y /tmp/scayl-api-offline.py.
