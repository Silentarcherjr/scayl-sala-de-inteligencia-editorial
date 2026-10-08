# SCAYL · Web pública estática (DL-034)

Demo principal: https://scayl-editorial.vercel.app/
Versión de respaldo: Streamlit local sin internet (`python scripts/demo_offline.py`).

Next.js App Router + TypeScript + Tailwind, export estático con 165 rutas de caso. Las fuentes Inter
se autoalojan durante el build; para compilar por primera vez se necesita internet. El resultado
`out/` se sirve sin Python, Ollama, claves ni llamadas externas. Los enlaces a fuentes y servicios
externos solo se abren por acción del lector y requieren internet.

```bash
# Desde la raíz, con el entorno Python activo:
python scripts/export_web.py
python -m pytest -q
ruff check .

# Web:
cd web
npm ci
npm run lint
npm run build
npx serve out
```

El exportador utiliza `scayl.service`, reutiliza `scripts.demo_offline.prepare()` y restaura el entorno
procesado al terminar. No modifica los artefactos originales. Rechaza descripciones RSS y citas a ese
campo mediante `deploy.prepare.check_public` antes de escribir cualquier salida. Conserva nulos e IDs.
Lee las constantes de Consultas y Trust Lab mediante AST, sin ejecutar sus páginas Streamlit.

Los aportes ponderados y las razones de la agenda se exportan desde Python; TypeScript no recalcula
el ranking oficial. Solo el simulador aplica la fórmula autorizada, con enteros cuya suma sigue siendo
100 y redondeo a una decimal compatible con Python. Las simulaciones son locales y no guardan decisiones.
El estado de evidencia es independiente del puntaje. DL-036 añade revisión validada por la API y registro en el navegador; no existe una acción de publicación.

Los recorridos del jurado son recorridos de evidencia/procedencia, no respuestas de IA inventadas.
Si no existe el caso demostrativo en el snapshot, se informa y se enlaza a Trust Lab. En la respuesta
extractiva de plantilla, la fecha de generación se fija al corte del snapshot para mantener el export
reproducible; las fechas guardadas en las salidas de caché se conservan. Solo `meta.exported_at` varía
entre exports con los mismos datos y commit. `meta.git_commit` registra el commit de origen del export.

Verificación completa y capturas: [docs/screenshots/web](../docs/screenshots/web/README.md).
197 pruebas Python; lint y build web aprobados; cinco pantallas en escritorio y móvil con Wi-Fi apagado,
0 llamadas externas y 0 errores. Tres casos contrastados mediante Streamlit AppTest; paridad de las
165 filas del simulador frente a Python. La auditoría de dependencias de desarrollo está documentada
junto a las capturas; no se ocultan ni se omiten los checks.

Vercel: proyecto `hacks10/scayl-editorial`, repositorio
`Silentarcherjr/scayl-sala-de-inteligencia-editorial`, Root Directory `web`. La configuración
versionada de DL-036 usa preset `framework: null`, `npm ci && node scripts/prepare-python.mjs`,
`npm run build` y Output Directory `out`; páginas estáticas y funciones Python independientes.
No se necesita configurar secretos ni variables de entorno del producto. La rama de producción
Git sigue siendo `main`; el Lead revisa y mergea, y la integración Git despliega los siguientes pushes.
Desplegar por Git (o enviar la raíz del repositorio con el CLI), para disponer de los archivos que
`prepare-python.mjs` copia desde `scayl/` y los artefactos públicos. Enviar únicamente `web/` falla
porque el proyecto tiene Root Directory `web` y necesita sus archivos hermanos en el build.

No se modifica `deploy/README.md` porque el encargo prohíbe editar `deploy/`; esta página y el README
principal registran la URL y el procedimiento de la nueva web.

## Evaluación autónoma del jurado

`/recorrido/` ofrece cinco pasos: agenda, evidencia, paquete editorial, revisión humana y abstención.
Los enlaces `#evidencia`, `#producir`, `#revision` y `#conflictos` seleccionan la pestaña correspondiente
sin backend. `/consultas/#sin-respuesta` abre el ejemplo guardado de abstención. La duración sugerida
no es una medición de usabilidad. Los datos y salidas originales se conservan.

Las fichas muestran primero un resumen derivado de `gap`, `claims`, `evidence_status_reason` y
`recommended_action`; no generan afirmaciones nuevas. Sus botones seleccionan y enfocan la pestaña
correspondiente. Las fechas muestran día, mes y año en hora de Panamá. Los modos `cache` y `template`
conservan sus valores técnicos y añaden una explicación comprensible.

Pruebas y métricas añade una lectura rápida y definiciones por tarea: agrupar noticias, clasificar temas
y comprobar sustento humano. Los F1 se formatean con hasta tres decimales; los valores completos,
muestras, corridas y limitaciones permanecen en los desplegables. No se combinan conjuntos ni se
infiere una mejora general de IA. Ver `docs/screenshots/web/jury-verification.json`: seis pantallas,
escritorio/móvil, recorrido completo, enlaces profundos, teclado y cero peticiones externas con Wi-Fi
apagado y restaurado. La comprensión con una persona nueva aún no se ha medido.

DL-036 reemplaza los avisos que derivaban consulta/revisión a Streamlit: ambos formularios están
en esta web. Streamlit permanece como versión de respaldo en el pie. Notion es opcional según C-03.


## Boletín de entorno logístico · DL-035 / revisión del PR #71

El brief oficial *hackIAthon — reto TVN Media*, modalidad bancaria, CU-05/T09, admite una extensión
del núcleo editorial. `/boletin/` entrega únicamente **Logística y Canal**, con la pregunta CU-05 literal:
«¿Qué señales públicas del entorno logístico debo revisar?». Se retiró el segundo sector por el ruido
del clasificador de temas: agrupaba titulares judiciales, deportivos y de promoción institucional
poco pertinentes para un analista. No se modifica ese clasificador ni el ranking editorial. Esta
reducción de alcance fue solicitada por el Lead en la revisión del PR #71 y prevalece sobre la
entrega dual originalmente descrita en [BANK_BULLETIN_PLAN.md](../docs/BANK_BULLETIN_PLAN.md).

La página muestra usuario, horizonte en Panamá, modo/modelo, límites visibles, síntesis y observaciones
con citas, tres hipótesis condicionales con sustento, sectores relacionados, tres preguntas verificables,
eventos usados y fuentes. El resumen se construye por código y no repite las observaciones: mide eventos
y dominios de medios, advierte que repetición no es corroboración, compara observaciones fechadas del
Gatún y presenta exportaciones como contexto histórico. Los conteos son mediciones locales del snapshot
con entradas y método en su tarjeta; no son indicadores externos ni medidas de independencia.

El texto numérico utiliza como máximo dos decimales; cada valor completo permanece en su tarjeta de
fuente. El adaptador de redondeo, exclusivamente en `scayl/gen/bulletin.py`, usa decimal y
`ROUND_HALF_UP` a dos decimales, sobre el valor exacto de la fila citada. No usa una tolerancia genérica
ni admite redondeos a un decimal. `check_sentence`, `numbers_in` y los validadores compartidos
permanecen intactos; nuevas pruebas rechazan cifras incorrectas, exceso de precisión y magnitudes
infladas por la ambigüedad de separadores decimales. Nulos nunca se transforman en cero.

El LLM existente puede generar observaciones/hipótesis en modo local/caché mediante JSON con esquema,
Pydantic y el prompt nuevo `bulletin.v2.md`. El resumen logístico se conserva determinista. Se
registran los descartes y se aplica fallback ante salida incompleta, duplicación del resumen,
hipótesis sin observación citada, cifras inventadas, inyección o términos financieros prohibidos.
El aviso fijo de alcance sigue siendo la única excepción al vocabulario prohibido.

La entrega es **Plantilla (sin IA generativa)**: sin GPU ni caché revisada para esta extensión. El
backend simulado se usa exclusivamente en pruebas y no aporta textos a la demo. Los titulares no
se traducen; se rotulan «titular en idioma original (idioma)» según sus metadatos. Los indicadores
son contexto y no corroboran los titulares; un período ausente sigue nulo y se declara sin
inventar fecha de publicación ni confundirla con detección/corte. La pertinencia del titular en
maratí y la utilidad/comprensión de analistas no están medidas.

«Imprimir / guardar PDF» abre citas y restaura su estado al terminar. El estilo se limita al boletín:
conserva identificadores, valores completos, períodos, URLs y método de conteos, evitando repetir
los desplegables enteros en cada oración. §8 se verificó de nuevo: 242 pytest, Ruff, npm ci/lint/build
y prueba con Wi-Fi apagado/restaurado, escritorio/móvil, impresión y flujo editorial existente.
Capturas y resultado: [bank-verification.json](../docs/screenshots/web/bank-verification.json).
El texto final íntegro está en el PR #71 para revisión y merge del Lead. Los avisos de desarrollo
ya documentados siguen vigentes; no se añadieron dependencias ni se modificó el lockfile.

## DL-036 · consulta libre y revisión en Next.js

`output: "export"` permanece: Next genera 173 páginas estáticas en `out/` y no contiene Route Handlers.
Vercel usa el preset `framework: null` de `web/vercel.json`, sirve `out/` y detecta por separado los
handlers Python nativos `api/ask.py` y `api/review.py`. No hay FastAPI ni servidor Next en runtime.
El `installCommand` ejecuta `scripts/prepare-python.mjs`: copia solo `scayl/` (sin bytecode), el
`bundle.public.json` y la caché pública de `deploy/artifacts/v1/llm` a `.python-runtime/` ignorado.
`includeFiles` empaqueta ese directorio en las funciones; nunca va a `out/`. No se copian raw, labels,
state ni pruebas. Runtime Python 3.13 y cuatro dependencias fijadas igual que el núcleo:
numpy, pydantic, rank-bm25 y PyYAML. Importar SCAYL no carga las dependencias ML/UI.

`POST /api/ask {question}` admite hasta 300 caracteres. El adaptador fija bundle/modelo/caché y
`mode=cache` aunque el entorno indique live. Usa `service.ask` con los validadores originales.
Un miss produce la misma plantilla o abstención de SCAYL, con modo/modelo visibles. La API nunca
contacta Ollama ni fuentes externas. Los botones del Modo jurado siguen usando `qa.json`.
Si la red/API falla, una coincidencia exacta usa su respuesta guardada; si no existe, se muestran los
ejemplos guardados con aviso explícito de que no responden a la pregunta libre. Un error 4xx muestra
los campos inválidos. Preguntas y nombres no se registran en logs de aplicación.

`POST /api/review {event_id, from_state, to_state, reviewer, justification}` valida enums,
`REVIEW_TRANSITIONS`, persona no vacía (máximo 100) y justificación obligatoria (máximo 500).
Genera los mismos campos/hashes de evidencia y paquete que `ReviewStore`, sin llamarlo ni escribir
SQLite/archivos/outbox. Añade el hash SHA-256 del bundle público (no un manifest de raw) y declara
que el estado previo lo aporta el navegador. No es un estado compartido ni una identidad autenticada.
El navegador conserva también el JSON exacto de la respuesta para descargarlo sin alterar la representación numérica (10.0 frente a 10) usada por el hash canónico. Cada recibo lleva hash propio, fecha UTC y aviso de no publicación; la UI muestra Panamá,
guarda historial por caso en `localStorage` versionado y permite descargar el JSON. No incluye datos
personales del corpus; solo el nombre que ingresa la persona revisora para esta demo.

Offline: `npm run build && npx serve out`. El snapshot, citas, paquetes y ejemplos funcionan sin API.
La pregunta libre avisa que usa respuestas guardadas; una revisión nueva requiere la API y, si falla,
no crea una decisión. Los recibos previamente guardados siguen disponibles para inspección/descarga.
Streamlit queda únicamente como versión de respaldo en el pie. La producción sigue igual hasta que
el Lead mergee; si no está estable a las 18:00 de Panamá del 8 de octubre, no debe mergearse.

Pruebas: `node scripts/prepare-python.mjs` desde `web/` y `python -m pytest -q` desde la raíz.
`tests/test_python_api.py` comprueba paridad semántica de cinco preguntas (timestamps de invocación
excluidos), bloqueo de live, matriz completa de transiciones, límites/JSON/errores, ausencia de
persistencia y paridad de hashes con la revisión existente. Ninguna prueba anterior se modifica.

Preview verificado del código `b697606`: https://scayl-editorial-5ljnkhvsk-hacks10.vercel.app/.
Resultado: 287 pytest, Ruff, npm ci/lint/build (173 rutas), cinco respuestas reales con paridad
semántica, diez errores 4xx remotos, dos decisiones encadenadas con recarga/descarga, fallos de red,
móvil y offline con Wi-Fi apagado/restaurado. Evidencia en
[python-api-verification.json](../docs/screenshots/web/python-api-verification.json).
