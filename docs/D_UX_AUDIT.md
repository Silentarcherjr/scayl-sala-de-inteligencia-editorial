# Auditoría de producto y UX (Subagente D) · 2026-10-08

Alcance: flujo **señal → evento → prioridad → evidencia → vacíos → borrador → revisión humana** en la web
Next.js (`web/`, desplegada en https://scayl-editorial.vercel.app/) y en la app Streamlit de respaldo (`app/`).
Método: lectura completa del código de `web/app`, `web/components` y `web/lib`; inspección de los datos que
consume la web (`web/public/data/*.json`); `npm run build` y `npm run lint`; `curl` de las páginas desplegadas;
cálculo de contraste de los tokens de color; `pytest` completo. **No** se hizo una verificación visual en
navegador a 1280×720 ni en móvil: el diseño adaptable se revisó leyendo el CSS.

## 1. Hallazgos y correcciones

| # | Severidad | Hallazgo | Corrección |
|---|---|---|---|
| H1 | Media | `GenerationNote` rotulaba **cualquier** modo distinto de `template` como «Salida IA precalculada». Una salida `live` (si alguna vez se habilita) se habría presentado como precalculada, y un modo desconocido como IA guardada. Las abstenciones no se distinguían en la cabecera del modo. | Etiqueta explícita por modo: `template` = «Plantilla · sin IA generativa», `cache` = «IA local precalculada · no es inferencia en vivo», `live` = «IA en vivo · modelo local»; modo desconocido = «no reconocido… trátalo como no verificado». Las respuestas abstenidas muestran «Abstención explícita ·» delante del modo. (`web/components/shared.tsx`, `answer-view.tsx`) |
| H2 | Media | En la cabecera de la ficha, la prioridad aparecía como una insignia suelta «alto» junto a «parcial»: puede leerse como «confianza alta». | Insignias «P 89.9 · atención alto» y «evidencia parcial». Igual en la agenda («P … · atención …») y la columna de la tabla «P (atención) / rango». (`case-view.tsx`, `app/page.tsx`, `situation.tsx`) |
| H3 | Media‑baja | El estado de revisión y el historial mostraban «aprobado como borrador» sin la aclaración en el mismo renglón (el aviso existía, pero arriba del formulario). | El estado se muestra como «aprobado como borrador · NO publicado» en el estado actual, el selector y el historial. (`review-form.tsx`) |
| H4 | Baja | El pie decía «Demo con salidas IA precalculadas (Qwen3 8B local) · modo cache», pero 150 de 165 paquetes y todos los ejemplos de Consultas son `template`. | Pie: «Demo sin IA en vivo · salidas guardadas: IA local precalculada (modo cache, Qwen3 8B) o plantilla (modo template); cada salida indica su modo». (`layout.tsx`) |
| H5 | Baja | Un caso inexistente (`/caso/EVT-9999/`) devolvía la página 404 por defecto de Next.js, en inglés y sin salida. | Página 404 en español con enlaces a la Sala y a la búsqueda de casos. (`web/app/not-found.tsx`) |
| H6 | Baja | Trust Lab: la tarjeta «Latencia medida» mostraba «Ver medición» aunque la latencia de paquetes sí está medida. | Muestra «Paquetes: mediana 13.1 s · p95 17 s (n=15) · Consultas: no medido», leído de `trust_lab.json`. (`trust-lab/page.tsx`) |
| H7 | Baja | Streamlit mostraba solo «Modo: cache» / «Modo de generación: template», sin explicar qué significa. | Línea adicional en lenguaje llano por modo (misma tabla que la web) en Ficha y Consultas. (`app/components/theme.py`, `app/pages/1_Ficha_de_Caso.py`, `app/pages/2_Consultas.py`) |

### Comprobado sin defectos (sin cambios)
- **P ≠ probabilidad de verdad**: el aviso «P mide atención, no probabilidad de verdad ni impacto» está en la Sala, la ficha, el recorrido y el simulador; la matriz Prioridad × Evidencia los muestra como ejes separados.
- **Métricas**: todo lo que muestra Trust Lab sale de `trust_lab.json` (con numerador/denominador y alcance). `tokens` y `attribution_preservation` dicen «no medido»; las limitaciones dicen «No se afirma ahorro de tiempo editorial: no medido». Costo API US$ 0,00 con la aclaración de hardware. Los conjuntos de red‑team y abstención declaran su alcance («sintético de desarrollo escrito por IA»).
- **Publicación**: no existe ningún control de «publicar». El recibo de `/api/review` incluye «Aprobado como borrador NO significa publicado». La validación del paquete en Streamlit dice «No autoriza publicación».
- **Solo titular**: los casos llevan «Basado únicamente en titular/metadatos».
- **Datos históricos**: las citas `wb:` con período muestran «Dato histórico — AAAA. No presentarlo como medición actual».
- **Estados vacíos/errores**: sin evidencia oficial, sin conflictos, sin paquete, sin coincidencias de búsqueda, API caída en Consultas (cae a la respuesta guardada exacta o lo dice) y en Revisión (no registra y lo dice).
- **Enlaces**: `/`, `/recorrido/`, `/consultas/`, `/trust-lab/`, `/simulador/`, `/boletin/`, `/caso/EVT-0101/`, `/caso/EVT-0114/` → 200 en producción; `GET /api/ask` → 405 (solo POST, esperado). Los enlaces externos pasan por `safeUrl` (solo http/https) con `rel="noopener noreferrer"`.
- **Accesibilidad**: no hay imágenes (sin `alt` pendiente); todos los campos tienen `<label>` o `aria-label`; pestañas con roles ARIA y flechas; enlace «Saltar al contenido»; `aria-live` en resultados. Contraste de los tokens (WCAG AA ≥ 4.5): texto atenuado 5.3, eyebrow 4.7, insignias alto 4.65 / medio 4.8 / parcial 5.2 / insuficiente 6.0, navegación 10.4.
- **Diseño**: puntos de corte en 1000 px y 640 px; las tablas anchas van en `.table-wrap` con desplazamiento horizontal propio, así que la página no se desborda; a 640 px las rejillas pasan a 1 columna y la navegación se envuelve.

### Riesgos que no corregí (fuera de alcance o requieren decisión del Lead)
- **No hay eventos sintéticos en el snapshot** (`synthetic: false` en los 165). La insignia SINTÉTICO está implementada, pero no aparecerá en la demo. Lo sintético está en los conjuntos de evaluación y ya se rotula en Trust Lab.
- El modo jurado n.º 4 de Consultas («Fuente con instrucciones maliciosas») no tiene caso en el snapshot y muestra un estado vacío honesto; no usarlo en la demo.
- El jurado n.º 2 («5 medios replican una agencia») usa EVT‑0046 (2 publicaciones, 2 medios, máximo 1 independiente): es correcto, pero no son 5 medios. Para la demo es mejor EVT‑0114.
- `DEMO_SCRIPT.md` (escena 6) cita un «conjunto reservado escrito por un humano»; existe en `eval/results/holdout-v2*.json`, pero la web de Trust Lab no lo muestra. Al narrar sobre la web, cita solo lo que está en pantalla.
- La consulta libre y la revisión dependen de `/api/*` en Vercel. En una exportación estática sin API, la consulta libre cae a las respuestas guardadas y la revisión no registra nada (lo dice).

## 2. Recorrido de 3 minutos para el jurado (web desplegada)

Todos los casos son **reales** (titulares públicos del corpus). **Ninguno es sintético**. Si se mostrara uno, la
insignia SINTÉTICO aparece en la tarjeta y la ficha.

| Tiempo | Pantalla | Qué mostrar | Qué decir (idea) |
|---|---|---|---|
| 0:00–0:20 | **Sala de Situación** `/` | Agenda top 5, aviso amarillo, matriz Prioridad × Evidencia | **Elegir un evento**: «187 señales → 165 eventos. P mide atención, no verdad: el top está en *parcial*.» |
| 0:20–0:45 | **EVT‑0101** (Canal: 33 cupos) → panel de puntaje | R, I, U, N, E con su aporte y su regla; insignia «P 89.9 · atención alto» junto a «evidencia parcial» | **Prioridad explicable**: «Cada punto tiene regla y razón. Urgente no es lo mismo que cierto.» |
| 0:45–1:05 | EVT‑0101 → pestaña **Evidencia** | ACP: nivel de Gatún 84.88 al **29‑09‑2026**; Banco Mundial 2024 con aviso «Dato histórico» | **Evidencia oficial con fecha**: «El contexto oficial no confirma el titular, y lo histórico nunca se presenta como actual.» |
| 1:05–1:30 | **EVT‑0114** (sismo 4.7) → **Fuentes**, luego **Conflictos** | 2 publicaciones → máx. 1 independiente, 0 confirmadas; conflicto 4.7 vs USGS 4.5 y 4.7 vs 7.4 | **Procedencia independiente + contradicción**: «Dos titulares no son dos confirmaciones. SCAYL no elige ni promedia: muestra las dos versiones con su fuente.» |
| 1:30–1:45 | EVT‑0114 → **Vacíos** | Qué sabemos / qué se afirma / qué no sabemos / 3 preguntas | **Vacío**: «Lo que no sabemos (daños, contenido completo) y qué investigar.» |
| 1:45–2:10 | **EVT‑0101 → Producir** | Cabecera «IA local precalculada · no es inferencia en vivo» (qwen3:8b), frases HECHO/DECLARACIÓN con «Ver sustento», «Basado únicamente en titular/metadatos» | **Borrador responsable**: «Salida guardada de un modelo local, no IA en vivo. Cada frase lleva su cita (evidence_id + campo).» |
| 2:10–2:25 | **Consultas** → «Sin respuesta» (`/consultas/#sin-respuesta`) | «Abstención explícita · Plantilla» + información necesaria | **Abstención**: «Turistas en 2035: no está en el corpus, así que no responde.» |
| 2:25–3:00 | **EVT‑0101 → Revisión** | nuevo → en revisión → **aprobado como borrador · NO publicado**, con nombre y justificación; descargar el recibo JSON (hash de evidencia y del paquete) | **Decisión humana verificable**: «La IA no publica. Una persona aprueba como borrador, con justificación y un recibo verificable.» |

Plan B, si `/api/review` falla en vivo: decirlo, mostrar el mensaje de error honesto («No se registró una nueva
decisión») y pasar a la app Streamlit local (Ficha → Revisión), que guarda la revisión en SQLite.

## 3. Verificación
- `npm run build` ✓ (173 páginas estáticas) · `npm run lint` ✓ (0 avisos).
- `pytest -q` ✓ 287 pruebas aprobadas tras los cambios en `app/`.
- No se agregaron dependencias ni se tocaron los datos del pipeline (`web/public/data`).
