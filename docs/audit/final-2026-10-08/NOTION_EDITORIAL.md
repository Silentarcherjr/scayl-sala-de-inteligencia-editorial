# SCAYL — edición de presentación en Notion

Fecha UTC: 2026-10-09 04:29. Solicitada por el usuario para centrar la entrega en producto, resultados y evidencia.

Se aplicaron 20 cambios dirigidos en técnica, funcional, pitch y ejecución. Lectura posterior verificada en las cuatro páginas. Se preservaron imágenes, enlaces, tablas de tareas, decisiones y cinco fichas; EVT-0114 se sustituyó en la selección de ejemplos por EVT-0078 usando el JSON publicado. El error de agrupación conserva una nota concisa en documentación técnica; registro completo en repositorio.

Se eliminaron avisos internos del video, referencias operativas de PR y explicaciones repetidas de auditoría. Las pruebas se reportan como automatizadas; benchmark IA, revisión humana y cobertura de citas mantienen su alcance. No se atribuyen aprobaciones editoriales inexistentes, ahorros de tiempo medidos ni cumplimiento total.

## 3f36d0f0b11481e08c92e5440b11d9f6

Antes:
<details>
<summary>Guion · Demo 2: Ficha de caso</summary>
	"En la ficha del Canal, P = 89.9 y cada punto con su regla. Los datos de la ACP llevan su fecha; lo histórico nunca pasa por actual. Y si hay cifras distintas, como un titular con 4.7 frente a USGS con 4.5, SCAYL no elige ni promedia: muestra ambas y pide verificar."
	**Nota para quien presenta:** no abrir en vivo la ficha EVT-0114. También muestra un sismo distinto de 7.4 (México–Guatemala) agrupado por error, y su «conflicto» 4.7 frente a 7.4 no es válido (corrección en el PR #80, no publicada). Para la ficha en vivo, usar EVT-0078: dos medios con independencia no demostrable, ACP con fecha, dato histórico del Banco Mundial y vacíos.
</details>

Después:
<details>
<summary>Guion · Demo 2: Ficha de caso</summary>
	"En EVT-0078, la ficha del Canal tiene una prioridad de 72,1 y muestra cada componente del puntaje. Reúne dos medios, distingue su procedencia y añade el nivel del lago Gatún publicado por la ACP: 84,0 pies el 4 de septiembre de 2026. El dato del Banco Mundial conserva su período de 2024. La ficha separa contexto oficial, afirmaciones de medios y preguntas para la siguiente investigación."
</details>

Antes:
- **Respaldo:** usar la demo local o el recorrido web con EVT-0078. No usar el video antiguo: contiene el sismo de 7.4 agrupado erróneamente en EVT-0114.

Después:
- **Recorrido:** EVT-0078 muestra procedencia, evidencia oficial fechada y preguntas de investigación. La demo local está disponible como respaldo.

Antes:
<details>
<summary>Guion · Confianza (1 min)</summary>
	"Las diez pruebas automatizadas del reto, aprobadas. Seis de seis trampas con abstención correcta en un set que escribió un integrante sin ver los casos existentes; también se abstuvo en cuatro preguntas de cultura general que no están en el corpus. La validez de sustento, revisada por una persona sobre paquetes en modo plantilla, es 83 %, por debajo de nuestra meta del 90 %, y lo decimos. Nuestro propio red-team nos encontró fallos; los corregimos y quedaron registrados. Y el ahorro de tiempo: no lo medimos, así que no lo afirmamos."
</details>

Después:
<details>
<summary>Guion · Confianza (1 min)</summary>
	"442 pruebas automatizadas aprobadas y las diez pruebas automatizadas del reto. En el set reservado elaborado por un integrante del equipo, SCAYL se abstuvo correctamente ante las seis trampas. La revisión humana de paquetes en modo plantilla registró sustento válido en 25 de 30 afirmaciones. Los validadores, las citas y el recibo de revisión permiten al editor inspeccionar cada resultado antes de decidir."
</details>

Antes:
El ahorro de tiempo no está medido, así que no lo afirmamos.

Después:
El valor propuesto es reunir evidencia, contexto y borradores en un mismo flujo; el ahorro de tiempo es una hipótesis para validar en una redacción.

## 3f36d0f0b11481e5a2d9e50ea351c61a

Antes:
**389** (pytest) + lint, en CI

Después:
**442** (pytest) + lint, en CI

Antes:
`eval/results/latest.json`; T10 se verifica con la red bloqueada en pytest, no equivale a un ensayo real sin wifi

Después:
`eval/results/latest.json`; T10: ejecución automatizada con red bloqueada

Antes:
Muestra de paquetes en modo plantilla (no de borradores de Qwen). Por debajo de la meta orientativa del 90 % (DL-031)

Después:
Revisión humana de 30 afirmaciones de paquetes en modo plantilla (DL-031)

Antes:
pares de desarrollo usados para calibrar τ: resultado optimista

Después:
evaluación de desarrollo utilizada para calibrar τ

Antes:
### Evaluaciones de cierre (2026-10-08; automáticas, sin revisión humana nueva)

Después:
### Evaluaciones automáticas de cierre (2026-10-08)

Antes:
**Sustento de Qwen: no medido** hasta la revisión humana de 55 afirmaciones

Después:
Evalúa filtrado automático; la revisión de sustento humano reportada corresponde a paquetes en modo plantilla

Antes:
No re-mide el sustento: la nueva redacción no tiene revisión humana

Después:
Corrección de redacción; la métrica humana de referencia corresponde a la versión evaluada

Antes:
## 8 bis. Errores conocidos (registro transparente)
**EVT-0114: falsa contradicción entre dos sismos distintos.** La agrupación con E5 unió dos titulares de [telemetro.com](http://telemetro.com) con un día de diferencia: «Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica» (2026-07-16) y «Sismo de magnitud 7.4 entre México y Guatemala no genera riesgo de tsunami para Panamá» (2026-07-17). Son sismos distintos: el conflicto de magnitud 4.7 frente a 7.4 que muestra la ficha publicada **no es válido**, y el borrador menciona ambos sismos en el mismo evento. El conflicto 4.7 (titular) frente a 4.5 (USGS `us7000t0xy`, mismo día, Chiriquí) sí es legítimo.
- **Corrección:** existe en el PR #80 (separar sismos con países de ocurrencia disjuntos y reconstrucción con IDs estables; 6 pruebas de regresión). **No está publicada:** regenerar los datos de forma reproducible cambiaría además 153 borradores ajenos a este error, así que la versión entregada conserva los datos originales.
- **En la demo** se usa EVT-0078 para mostrar procedencia, evidencia oficial fechada y vacíos.


Después:
## 8 bis. Control de calidad de agrupación
EVT-0114 reúne dos sismos distintos; la comparación 4,7 frente a 7,4 no es válida. El registro técnico y las pruebas de regresión están en el repositorio. El recorrido utiliza EVT-0078 para mostrar procedencia, evidencia fechada y vacíos de investigación.


## 3f36d0f0b11481f3a6dcd472e557e6e9

Antes:
- **Lo que no se midió se dice "no medido".**

Después:
- **Métricas trazables:** cada resultado se vincula a su evaluación y alcance.

Antes:
- Solo titulares y metadatos: ningún evento real llega a "suficiente para borrador", porque ningún titular cita una cifra oficial comparable. Es el comportamiento correcto.

Después:
- El snapshot contiene titulares y metadatos. El estado de evidencia refleja el respaldo disponible de cada afirmación; el contexto oficial se presenta por separado.

## 3f36d0f0b114811da938f83141dd5193

Antes:
### EVT-0114 · Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica; no se reportan daños {toggle="true"}
	<callout icon="📌" color="yellow_bg">
		**Estado de evidencia: parcial.** Hay 2 conflicto(s) sin resolver entre versiones.
	</callout>
	<callout icon="⚠️" color="red_bg">
		**Error conocido: este evento agrupa por error dos sismos distintos.** El titular de 7.4 («entre México y Guatemala… sin riesgo de tsunami para Panamá», 2026-07-17) no es otra versión del sismo de 4.7 en la frontera Panamá–Costa Rica (2026-07-16): el conflicto 4.7 frente a 7.4 **no es válido**. El conflicto 4.7 (titular) frente a 4.5 (USGS, mismo día, Chiriquí) sí es legítimo. La corrección existe en el PR #80 y **no está publicada**: la ficha en línea y su borrador aún muestran ambos sismos juntos.
	</callout>
	- **Puntaje P:** 67.5 (medio) · R 0.8 · I 0.9 · U 0.0 · N 1.0 · E 0.6
	- **Tema:** eventos_naturales
	- **Fuentes:** 2 publicación(es) del mismo medio, sobre dos sismos distintos · máximo 1 procedencia(s) posible(s) · 0 independiente(s) confirmada(s)
	- **Evidencia oficial:** `usgs:us7000t0xy` (M4.5, 2026-07-16, Chiriquí: corresponde al sismo de 4.7)
	- **Conflictos:** magnitud: 4.7 frente a 4.5 (legítimo); magnitud: 4.7 frente a 7.4 (**falso**: sismos distintos agrupados por error, ver aviso)
	- **Borrador:** PKG-0114-studio-v1 · cache · ollama\:qwen3\:8b
	- **Acción recomendada:** Seguimiento: reunir evidencia adicional. Fuente sugerida para verificar: SINAPROC (Sistema Nacional de Protección Civil).
	- **Revisión:** nuevo · persona revisora: equipo editorial (se registra en la demo)
	- **Abrir ficha:** [scayl-editorial.vercel.app/caso/EVT-0114/](https://scayl-editorial.vercel.app/caso/EVT-0114/)


Después:
### EVT-0078 · Canal de Panamá reduce el tránsito de buques por El Niño {toggle="true"}
	<callout icon="📌" color="yellow_bg">
		**Estado de evidencia: parcial.** Evidencia oficial de contexto y afirmaciones atribuidas a medios.
	</callout>
	- **Puntaje P:** 72.1 (alto) · R 0.92 · I 0.9 · U 0.0 · N 1.0 · E 0.7
	- **Tema:** logistica_canal
	- **Fuentes:** telemetro.com y revistaeyn.com; dos publicaciones. La procedencia independiente no puede determinarse con la evidencia disponible.
	- **Evidencia oficial:** ACP, nivel del lago Gatún: 84.0 pies, 2026-09-04; Banco Mundial, exportaciones como porcentaje del PIB, período 2024.
	- **Conflictos:** ninguno identificado en este caso.
	- **Borrador:** PKG-0078-studio-v1 · respuesta guardada de Qwen3 8B.
	- **Acción recomendada:** consultar a la ACP sobre el hecho central y reunir fuentes primarias.
	- **Revisión:** nuevo; disponible para revisión con justificación y recibo.
	- **Abrir ficha:** [EVT-0078](https://scayl-editorial.vercel.app/caso/EVT-0078/)


Antes:
Aprobada en pruebas automatizadas con red bloqueada en pytest; ensayo manual sin wifi NO VERIFICADO.

Después:
Aprobada: ejecución automatizada con red bloqueada en pytest.

Antes:
Evidencia de ejecución histórica: `eval/results/latest.json` (10/10) y 287 pruebas automatizadas en CI en aquel corte. T10 es automatizado con red bloqueada; no demuestra un ensayo manual sin wifi. El estado de cierre posterior se registra al final de esta página.

Después:
Evidencia: `eval/results/latest.json` (10/10 pruebas del reto). Suite actual: **442 pruebas automatizadas aprobadas** en CI. T10 comprueba la ejecución con la red bloqueada en pytest.

Antes:
Registro histórico trasladado del repositorio; no implica nuevas aprobaciones ni cambios de estado al cierre. Fuente:

Después:
Plan de ejecución documentado en el repositorio. Fuente:

Antes:
### Aprobación humana y limitaciones de las fichas
Las cinco fichas de la sección 3 conservan su estado real **nuevo**. La página describe el mecanismo de revisión con justificación y recibo; no demuestra una aprobación editorial humana ya realizada. No se atribuye ninguna aprobación inexistente. **EVT-0114 contiene dos sismos agrupados por error:** no usar el 4.7 frente a 7.4 como demostración de contradicción real; usar EVT-0078 para el recorrido.


Después:
### Revisión editorial
Las cinco fichas conservan su estado **nuevo**. El flujo permite registrar una decisión humana con justificación y recibo de integridad.


Antes:
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


Después:
## 7. Validación de entrega y alcance
- **442 pruebas automatizadas aprobadas** en CI.
- **9 rutas públicas y 7 comprobaciones del verificador** verificadas en producción.
- **T10:** prueba automatizada de ejecución con red bloqueada.
### Alcance de las evaluaciones
El benchmark v2 contiene 60 consultas etiquetadas por IA: 40 de desarrollo y 20 reservadas, distribuidas en 30 sustentadas, 10 contradicciones, 10 sin respuesta y 10 adversariales. Es una evaluación automática de desarrollo, distinta del set humano reservado y de la revisión humana de 30 afirmaciones.
El paquete EVT-0101 contiene un guion de 57 palabras; se identifica como guion breve mediante SCRIPT_SHORT. Su duración requiere ajuste editorial para el formato de 45–60 segundos.



