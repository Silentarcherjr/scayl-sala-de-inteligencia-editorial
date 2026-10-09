# Auditoría de cumplimiento oficial — Notion SCAYL

Página propia: https://conscious-handbell-91a.notion.site/Ejecuci-n-y-evidencias-3f36d0f0b114811da938f83141dd5193
Última edición verificada UTC: 2026-10-09T04:23:32.886Z

Cambios: append8tareas reales DONE fuente tablero; tres decisiones DL003004010 con fechas motivos alternativas/compromisos reales; fechas extracción y campos6fuentes desde raw/recibos; T10 cambiado a automatizado y manual NO VERIFICADO; 287CI preservado como histórico, añadido442CI PR86 +7regresiones9rutas informados por raíz;5fichas preservadasNUEVO sin fabricar aprobaciones; avisoEVT0114 no demostrar falso conflicto; benchmarkIA/no etiquetas humanas y guion57palabras/no45–60s declarados como desviaciones.

Read-back completo confirma8IDs3decisiones442CI5fichas y límites. No corpus código modelos permisos ni terceros cambiados. No se afirma cumplimiento100%.

## Texto añadido

## 5. Plan de ejecución y decisiones justificadas
Registro histórico trasladado del repositorio; no implica nuevas aprobaciones ni cambios de estado al cierre. Fuente: [tablero versionado](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/blob/main/docs/notion_mirror/01_EXECUTION_BOARD.md). Fechas en UTC.
<table header-row="true" fit-page-width="true">
<tr><td>**ID · tarea**</td><td>**Responsable**</td><td>**Estado**</td><td>**Inicio UTC**</td><td>**Actualizado UTC · evidencia**</td></tr>
<tr><td>L-01 · Contratos de datos + fixture UI</td><td>Lead (H1+Claude)</td><td>DONE</td><td>2026-10-06 19:45</td><td>2026-10-06 20:30 · rama claude/fervent-babbage-q9fg7h</td></tr>
<tr><td>L-02 · Gobernanza + espejo Notion + onboarding</td><td>Lead</td><td>DONE</td><td>2026-10-06 19:40</td><td>2026-10-06 22:00 · misma rama</td></tr>
<tr><td>H-01 · Preparar espacio Notion para migrar</td><td>H1</td><td>DONE</td><td>2026-10-08 18:06</td><td>2026-10-08 20:40 · PR #76</td></tr>
<tr><td>B-01 · Snapshot propio según PDF</td><td>Worker B (H3)</td><td>DONE</td><td>2026-10-06 21:19</td><td>2026-10-07 03:06 · PR #19</td></tr>
<tr><td>B-10 · Benchmark de modelos locales</td><td>Worker B (H3)</td><td>DONE</td><td>2026-10-07 (hora no registrada)</td><td>2026-10-07 19:17 · PR #48</td></tr>
<tr><td>A-01 · Esqueleto Streamlit + FixtureService</td><td>Worker A (H2)</td><td>DONE</td><td>2026-10-07 (hora no registrada)</td><td>2026-10-07 02:40 · PR #18</td></tr>
<tr><td>L-03 · Puntaje P + estado de evidencia</td><td>Lead</td><td>DONE</td><td>2026-10-06 22:35</td><td>2026-10-06 23:30 · rama claude/fervent-babbage-q9fg7h</td></tr>
<tr><td>L-09 · Validadores + fallback template</td><td>Lead</td><td>DONE</td><td>2026-10-06 22:40</td><td>2026-10-06 23:30 · misma rama</td></tr>
</table>
### Tres decisiones justificadas
Fuente histórica: [registro de decisiones](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/blob/main/docs/notion_mirror/02_DECISION_LOG.md).
- **DL-003 · 2026-10-06:** concentrar diez módulos en cuatro pantallas (Sala, Ficha, Consultas y Trust Lab). Alternativa: una pantalla por módulo. Motivo: demo lineal, apertura de ficha exigida y plazo. Compromiso: la ficha concentra contenido y se organiza en pestañas.
- **DL-004 · 2026-10-06:** numpy en memoria y embeddings precalculados, sin base vectorial. Alternativas: FAISS, Qdrant o Chroma. Motivo: corpus pequeño, búsqueda exacta y ausencia de infraestructura adicional. Compromiso: no escala a millones de vectores.
- **DL-010 · 2026-10-06:** separar evaluación y ajuste. Humano 2 elige top 5 a ciegas y revisa afirmaciones; Humano 3 etiqueta temas/agrupación; Humano 1 y Lead ajustan. Motivo: evitar fuga de información. Compromiso: el editor no es periodista de TVN y Precision@5 es exploratorio.
### Aprobación humana y limitaciones de las fichas
Las cinco fichas de la sección 3 conservan su estado real **nuevo**. La página describe el mecanismo de revisión con justificación y recibo; no demuestra una aprobación editorial humana ya realizada. No se atribuye ninguna aprobación inexistente. **EVT-0114 contiene dos sismos agrupados por error:** no usar el 4.7 frente a 7.4 como demostración de contradicción real; usar EVT-0078 para el recorrido.
## 6. Catálogo: extracción y campos trazables
Complemento del catálogo de la sección 1, leído de archivos raw y recibos de descarga. Se conservan las condiciones, cobertura, transformaciones y hashes ya declarados.
<table header-row="true" fit-page-width="true">
<tr><td>**Fuente**</td><td>**Extracción UTC**</td><td>**Campos principales**</td></tr>
<tr><td>GDELT</td><td>2026-10-07 02:49:18.937411–02:56:29.271989</td><td>ID, título, URL, medio, idioma, publicación, detección y extracción; publicación puede ser nula</td></tr>
<tr><td>TVN RSS</td><td>2026-10-06 21:21:58.100143</td><td>Mismos campos de noticia; publicación RSS original, detección nula</td></tr>
<tr><td>Banco Mundial</td><td>2026-10-06 21:19:24.551363–21:21:22.468695</td><td>País, indicador, año, valor nullable, unidad, URL, extracción y licencia</td></tr>
<tr><td>ACP</td><td>2026-10-07 04:55:24.534602–04:55:24.793546</td><td>País, serie, período, valor, unidad, fuente, frecuencia y es_proyeccion</td></tr>
<tr><td>INEC</td><td>2026-10-07 04:55:25.189550</td><td>País, serie IPC, período, valor, unidad, fuente y extracción</td></tr>
<tr><td>USGS</td><td>Oficial: 2026-10-06 21:19:27.277126; extensión: 2026-10-07 02:47:29.647440</td><td>ID, magnitud, tiempo, actualización, coordenadas, profundidad, lugar, estado y URL</td></tr>
</table>
Diccionario completo y recibos: [diccionario](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/blob/main/docs/DATA_DICTIONARY.md) y [snapshot raw](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/tree/main/data/raw/v1).
## 7. Estado comprobado del cierre
Actualización registrada el 2026-10-09 04:23 UTC (2026-10-08 23:23 Panamá). El historial de 287 pruebas y 75 PR arriba corresponde a un corte anterior y se conserva como histórico.
- **CI del PR #86:** 442 pruebas aprobadas, según comprobación de cierre del agente responsable.
- **Comprobación de cierre:** 7 regresiones y 9 rutas verificadas, según el informe de auditoría de cierre; no representan una nueva evaluación del corpus.
- **T10:** ejecución automatizada con red bloqueada en pytest; no equivale a un ensayo presencial/manual con wifi apagado. Ese ensayo manual sigue **no verificado**.
No se recalcularon métricas históricas ni se reconstruyó el corpus.


### Desviaciones declaradas frente al PDF oficial
- **Benchmark v2:** 60 consultas, proporción 30 sustentadas / 10 contradicciones / 10 sin respuesta / 10 adversariales, dividido en 40 de desarrollo y 20 reservadas. Las 60 etiquetas figuran como escritas por IA y sin revisión humana. El PDF §7 pide etiquetas humanas: ese requisito no está cumplido por este benchmark; no se presenta como evaluación humana ni independiente.
- **Duración de guion:** el guion del paquete EVT-0101 tiene 57 palabras según recuento del snapshot; no asegura los 45–60 segundos exigidos. El validador permite SCRIPT_SHORT para evitar rellenar con contenido inventado. No se regeneraron borradores al cierre.
Estas desviaciones se declaran; no se afirma cumplimiento total del PDF.

