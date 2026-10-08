# Relevo · worker-web · 2026-10-08 03:11 UTC

- **Motivo de la parada:** relevo preventivo al cerrar una etapa.
- **Rama:** `worker-web/next-static` · **Último commit:** el commit de esta etapa incluye esta nota; consultar `git log -1` (empujado al cerrar etapa).
- **PR abierto:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/67

## Tarea en curso
Mejoras de UX para evaluación autónoma del jurado, autorizadas por el usuario: recorrido guiado, fichas claras y métricas explicadas. Dentro de web/, sin cambiar contratos, datos ni dependencias.

## Hecho en esta sesión
Métricas con definiciones, lectura rápida, comparación honesta IA/reglas y valores originales desplegables. Recorrido de seis pantallas verificado en escritorio/móvil, con 12 capturas reales.

## Siguiente paso concreto
Actualizar PR #67, desplegar el commit final en scayl-editorial y verificar públicamente el recorrido. Merge reservado al Lead.

## Estado de las pruebas
197 pytest; ruff; npm ci/lint/build OK (172 rutas); recorrido físico offline OK; Wi-Fi restaurado; cero red externa/errores; datos exportados intactos

## Archivos tocados
Ver el commit de esta etapa. No modificar scayl/, app/, deploy/ ni tests/ existentes.

## Bloqueos, dudas y decisiones pendientes
Mergea el Lead. La rama de producción Vercel sigue siendo main; publicar explícitamente desde worker-web si corresponde.

## Contexto que no está en el código
Web pública https://scayl-editorial.vercel.app/. Python .venv/bin/python; Node bundled runtime. Para Playwright usar Chromium 1243 de la caché local. Nunca desactivar protección Vercel.
