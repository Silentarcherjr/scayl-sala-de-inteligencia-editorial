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


## Extensión bancaria · DL-035 · 2026-10-08

`bank-{logistica_canal,economia}-{desktop,mobile}.png`: capturas reales completas del selector y los
dos boletines, con citas desplegadas de ejemplo. `bank-*-print.png`: primera página renderizada de
cada PDF A4, sin edición. Se inspeccionaron las 6 páginas de logística y 5 de economía: texto legible,
oraciones y secciones sin recortes, etiquetas, hipótesis, períodos y URLs visibles.

[bank-verification.json](bank-verification.json) registra Wi-Fi apagado/restaurado y bloqueo de otros
orígenes, cero solicitudes externas y errores de navegador. Ambos sectores funcionan en escritorio
y móvil, con dos/una columnas y sin desbordamiento. Se verificó el botón de impresión, apertura y
restauración de citas, y se contrastaron brief editorial y consulta guardada con sus datos originales.
La prueba acredita el export local; producción depende del merge del Lead y del despliegue Git.

§8: 230 pytest; Ruff; npm ci, lint y build aprobados. Lectura manual: resúmenes 179/171 palabras,
ningún consejo financiero, hipótesis condicionales separadas, Banco Mundial con período 2024 y aviso
histórico. El titular con cifras cuyo período no consta conserva el nulo y añade una advertencia
explícita; no se inventa una fecha. Las preguntas se derivan de los vacíos de evidencia existentes.
No se ha medido utilidad ni comprensión con analistas. El PR incluye ambos textos completos.
