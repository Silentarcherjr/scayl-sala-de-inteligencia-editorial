# Web estática · DL-034

Capturas de `web/out` servido con `npx serve@14.2.4 out`, viewport 1440×1000 y móvil 390×844.
Se recorrieron las cinco pantallas, filtros y matriz, las ocho pestañas, citas, ambas versiones del
conflicto EVT-0114, ejemplos y recorridos del jurado, buscador y simulador.

La prueba se repitió con Wi-Fi `en0` apagado y verificado por `networksetup`; luego se restauró al
estado inicial (encendido). Chromium bloqueó además toda petición fuera de localhost. Resultado:
**0 peticiones externas y 0 errores del navegador**. Las fuentes Inter se sirven desde `_next/static/media`.
Los enlaces explícitos a fuentes, GitHub y Streamlit requieren internet al abrirse.

Paridad mediante Streamlit AppTest y `scayl.service`, muestreo reproducible con semilla 34:
EVT-0101 (top 1), EVT-0139 y EVT-0027: mismo P, componentes, estado, paquete completo y modo.
Simulación R=10, I=25, U=40, N=15, E=10: las 165 filas coinciden con `service.simulate_weights`.
Los pesos oficiales reproducen las 165 puntuaciones y posiciones; restablecerlos recupera el orden.

Checks: `python -m pytest -q`: 197 passed. `ruff check .`: OK.
`web/`: `npm ci`, `npm run lint`, `npm run build`: OK; 171 rutas exportadas, incluidos 165 casos.
Sin errores ni warnings de TypeScript. Sin patrones de HTML sin escapar, fetch HTTP externo o claves
según el escaneo de fuentes. Ningún archivo existente en `scayl/`, `app/`, `deploy/`, `data/` o `tests/`
fue modificado; solo se añadió `tests/test_export_web.py`.

`npm audit` reporta cinco avisos transitivos de desarrollo por `braces` (máxima versión publicada 3.0.3,
sin parche disponible). Llegan a través de `eslint-config-next`; no se incorporan al runtime estático.
No se aplica el downgrade automático propuesto por npm. ESLint 9.39.1 muestra aviso de fin de soporte
al instalar, pero lint y build no tienen warnings de tipos. El lockfile conserva las versiones exactas.

Las capturas y `verification.json` documentan el recorrido local; no acreditan por sí mismas el
acceso público de un despliegue Vercel. Ese acceso se verifica separadamente al publicar.

## Mejora para evaluación autónoma · 2026-10-08

Capturas `jury-*-desktop.png` (1440 × 1000) y `jury-*-mobile.png` (390 × 844) muestran las seis
pantallas, incluido el nuevo recorrido. Son capturas reales del export servido en localhost, sin edición.
Resultado: [jury-verification.json](jury-verification.json). Wi-Fi en `en0` apagado durante el recorrido
y restaurado a su estado original (On). El navegador también bloqueó cualquier origen externo.

Se verificaron los cinco pasos de inicio a fin, pestañas enlazadas y recarga, navegación de teclado,
citas desplegables, paquetes guardados, abstención, métricas originales y ausencia de desbordamiento
horizontal. Tres fichas (EVT-0101, EVT-0139, EVT-0027) conservan P, motivos, advertencias, brief y modo.
Los datos exportados no cambiaron respecto a la entrega contrastada con Streamlit. Cero errores de
navegador y cero peticiones externas. No es una prueba de comprensión con usuarios; esa aún no se midió.

La misma verificación pasó sin autenticación en https://scayl-editorial.vercel.app/ (escritorio/móvil).
Resultado: [jury-public-verification.json](jury-public-verification.json). Producción READY, despliegue
`dpl_CWXktnUR4TqmMGyTp5F2hE3XziTw`, código `957ecf08568f2f79fb8209d1ea5d6830e5691e71`.


## Extensión bancaria logística · revisión del Lead del PR #71

`bank-logistica_canal-{desktop,mobile}.png`: capturas reales del único boletín entregado, con citas
desplegadas de ejemplo. `bank-logistica_canal-print.png`: primera página renderizada del PDF A4, sin
edición. El boletín del segundo sector y sus capturas se retiraron por el clasificador de temas
ruidoso: sus titulares eran poco pertinentes para un analista sectorial. No cambia la web editorial.

[bank-verification.json](bank-verification.json) documenta Wi-Fi apagado/restaurado y bloqueo de otros
orígenes, cero solicitudes externas y errores, escritorio/móvil sin desbordamiento y dos/una columnas.
Se verifican CU-05, resumen de síntesis distinto de las observaciones, tres hipótesis citadas, preguntas
verificables, etiqueta del titular en maratí, valor redondeado en texto y valor íntegro en la tarjeta,
botón de impresión/restauración de citas y brief/consulta editorial conservados. El PDF incluye
fuentes, períodos, URLs y trazabilidad de los conteos. La evidencia corresponde al export local;
producción depende del merge del Lead y del despliegue Git.

§8: 242 pytest; Ruff; npm ci, lint y build aprobados. Lectura manual del boletín completo: sin consejo
financiero, hipótesis condicionales distintas de las observaciones, secuencia fechada del Gatún,
exportaciones 2024 con aviso histórico y períodos ausentes explícitos. No se ha medido utilidad ni
comprensión con analistas. El PR incluye el boletín final completo y las limitaciones de pertinencia.

Resumen medido: **112 palabras** en cuatro elementos de síntesis, cinco eventos y seis dominios de
medios. PDF A4 de **cinco páginas**, todas inspeccionadas: etiquetas completas, texto y URLs legibles,
bloque de hipótesis diferenciado y sin páginas vacías. Las tarjetas de conteo imprimen entradas y método.

## DL-036 · API Python y revisión en navegador

Preview probado de `b697606`: https://scayl-editorial-5ljnkhvsk-hacks10.vercel.app/ (protección
normal de previews de Vercel; pruebas con credencial temporal del proyecto, nunca guardada aquí).
Dos funciones nativas `api/ask` y `api/review`, 31.07 MB cada una, Python 3.13. Las páginas siguen
siendo export estático. `python-api-verification.json` contiene las cinco respuestas reales,
paridad semántica con `service.ask`, verificación del hash del recibo, diez errores 4xx remotos,
prueba de estado no persistente, historial/recarga/descarga y fallos de red sin inventar decisiones.
287 pytest, Ruff, npm ci/lint/build (173 rutas); datos, motor, pruebas anteriores y lockfile intactos.

`python-api-*-static.png` muestra Sala, ficha, Consultas, Trust Lab y simulador en `npx serve out`;
`python-api-review-desktop.png` muestra decisiones reales del preview; las capturas móviles `*-preview`/`*-offline` prueban
la lectura y el aviso de error. El recibo conserva el JSON exacto y su SHA-256 verifica incluso
después de recargar localStorage. Wi-Fi apagado/restaurado: cinco pantallas y tres casos
comparados, cero peticiones externas, cero errores JavaScript. La consulta libre usa una respuesta
guardada solo si coincide la pregunta; los ejemplos alternativos se identifican como tales. Una
revisión nueva exige la API; los recibos existentes siguen accesibles offline en ese navegador.
Avisos transitivos npm/ESLint preexistentes sin cambios ni omisión de checks.
