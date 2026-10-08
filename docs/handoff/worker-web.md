# Relevo · worker-web · 2026-10-08 03:04 UTC

- **Motivo de la parada:** relevo preventivo al cerrar una etapa.
- **Rama:** `worker-web/next-static` · **Último commit:** el commit de esta etapa incluye esta nota; consultar `git log -1` (empujado al cerrar etapa).
- **PR abierto:** https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/pull/67

## Tarea en curso
Mejoras de UX para evaluación autónoma del jurado, autorizadas por el usuario: recorrido guiado, fichas claras y métricas explicadas. Dentro de web/, sin cambiar contratos, datos ni dependencias.

## Hecho en esta sesión
Portada con entrada clara, recorrido estático de cinco pasos, enlaces directos a pestañas y abstención; explicación de datos congelados y preguntas libres.

## Siguiente paso concreto
Resumen de decisión al inicio de fichas y acciones claras.

## Estado de las pruebas
197 pytest OK; lint y build OK (172 rutas); verificación del navegador al cierre

## Archivos tocados
Ver el commit de esta etapa. No modificar scayl/, app/, deploy/ ni tests/ existentes.

## Bloqueos, dudas y decisiones pendientes
Mergea el Lead. La rama de producción Vercel sigue siendo main; publicar explícitamente desde worker-web si corresponde.

## Contexto que no está en el código
Web pública https://scayl-editorial.vercel.app/. Python .venv/bin/python; Node bundled runtime. Para Playwright usar Chromium 1243 de la caché local. Nunca desactivar protección Vercel.
