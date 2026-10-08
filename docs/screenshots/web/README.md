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
