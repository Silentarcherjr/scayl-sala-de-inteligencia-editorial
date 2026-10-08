# SCAYL · Web pública estática (DL-034)

Demo principal: https://scayl-editorial.vercel.app/
Respaldo y consultas libres: https://scayl-demo.streamlit.app/

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
El estado de evidencia es independiente del puntaje. La revisión pública es de solo lectura.

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
`Silentarcherjr/scayl-sala-de-inteligencia-editorial`, Root Directory `web`, preset Next.js,
`npm ci`, `npm run build`, Output Directory automático (sin override), sin variables de entorno.
Next.js publica el export `out/`; el adaptador Vercel necesita conservar su directorio interno `.next/`. La rama de producción Git sigue siendo
`main`; el despliegue inicial se realiza explícitamente desde `worker-web/next-static` sin mergear.
El Lead revisa y mergea el PR. Los siguientes pushes a `main` se despliegan mediante la integración Git.

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

El aviso visible «La revisión humana con registro y la consulta libre funcionan en la versión de
trabajo: https://scayl-demo.streamlit.app/» aparece junto al modo de solo lectura de cada ficha, en
el paso de revisión del recorrido y en el pie de todas las páginas. La demo pública permite
inspeccionar; Streamlit ofrece las acciones con registro. Notion es opcional según C-03.


## Boletín de entorno sectorial · DL-035

El brief oficial *hackIAthon — reto TVN Media*, modalidad bancaria, CU-05/T09, admite una extensión
del mismo núcleo editorial. El alcance aprobado está en [BANK_BULLETIN_PLAN.md](../docs/BANK_BULLETIN_PLAN.md).
`/boletin/` permite elegir Logística y Canal o Economía: pregunta, horizonte en Panamá, modo/modelo,
límites visibles, resumen de hasta 250 palabras, observaciones citadas, hipótesis condicionales separadas,
sectores potencialmente relacionados, tres preguntas y enlaces a los cinco eventos priorizados.
No modifica ranking, Story Studio, Q&A ni revisión editorial. No incorpora SBP ni información de entidades.

`scripts/export_web.py` agrega únicamente `bulletins.json` a sus salidas. La función nueva
`service.sector_bulletin` usa el LLM existente en modo local/caché, prompt `bulletin.v1.md`, JSON con esquema
y validación Pydantic. El control determinista elimina términos financieros prohibidos, cifras ajenas
a la evidencia, citas desconocidas, instrucciones de fuentes y datos históricos sin período/advertencia.
Un fallo, caché ausente o salida sin resumen, observaciones e hipótesis válidos activa la plantilla y
registra `LLM_FALLBACK`. El aviso fijo de alcance es la única excepción al vocabulario prohibido.

Los boletines versionados son **Plantilla (sin IA generativa)**, no salidas del modelo simulado. El
precálculo con GPU (etapa 4 opcional) se omite: no hay ejecución ni caché aprobada para esta extensión.
Las pruebas usan un backend simulado aislado; sus resultados no se exportan. La revisión humana del
sustento sectorial y la comprensión de analistas aún no están medidas. Los titulares se conservan
en su idioma original; pueden ser poco pertinentes para el usuario sectorial. Los indicadores
son contexto, no corroboran esos titulares. Un período ausente queda nulo y se declara en pantalla;
no se confunde la fecha del snapshot con la fecha del hecho.

«Imprimir / guardar PDF» abre las citas durante la impresión y restaura su estado al terminar. La
hoja de impresión es exclusiva del boletín: conserva identificadores de sustento, períodos y URLs
en la sección de fuentes, evitando repetir los desplegables completos en cada oración.

Verificación de §8: 230 pruebas Python, Ruff, `npm ci`, lint y build (173 rutas), lectura completa de
ambos boletines y navegación con Wi-Fi apagado/restaurado. Resúmenes medidos: 179/171 palabras.
Escritorio 1440 × 1000, móvil 390 × 844; cero solicitudes externas, errores y desbordamientos. PDF
A4 de 6/5 páginas revisados visualmente, incluidos fuentes e hipótesis. Evidencia en
[bank-verification.json](../docs/screenshots/web/bank-verification.json) y capturas `bank-*.png`.
Los avisos de dependencias de desarrollo ya documentados en la web siguen vigentes; no se añadieron
dependencias ni se alteró el lockfile. El Lead revisa los dos textos completos en el PR antes de mergear.
