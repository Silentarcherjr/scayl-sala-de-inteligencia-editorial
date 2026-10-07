# AGENT_PROPOSALS — propuestas transversales

## AP-012 · Exigir compatibilidad semántica de la medida para vincular ACP
- Autor / fecha: frictionspp-svg + Codex · 2026-10-07 05:04 UTC.
- Estado: **ACEPTADA** (DL-026).
- Problema u oportunidad: la ejecución B-13/B-14 vincula contexto de Gatún con EVT-0161, «Populoso distrito de Panamá completa una semana sin homicidios tras imponer restricciones nocturnas», porque `recent.py` acepta la palabra genérica «restricción». No confirma la noticia, pero el contexto es irrelevante. Además «calado» y «nivel de Gatún» son medidas distintas: compartir pies no permite confirmar una con la otra.
- Cambio propuesto: el Lead acota palabras genéricas con entidades del Canal/agua; separa pertinencia contextual de compatibilidad exacta de medida para confirmación (nivel del lago observado, no calado de buques). Añadir regresiones con el titular real y un calado en pies numéricamente coincidente.
- Por qué mejora el proyecto: evita contexto irrelevante y futuras confirmaciones por coincidencia numérica entre medidas diferentes, sin flexibilizar evidencia para obtener suficientes.
- Dimensión de rúbrica: trazabilidad, evidencia oficial pertinente y precisión.
- Archivos/módulos afectados: scayl/evidence/recent.py (Lead), tests/test_recent.py (Lead).
- Riesgos: menos vínculos si los titulares omiten la entidad; mantener abstención conservadora.
- Esfuerzo estimado: ajuste local del Lead y dos regresiones.
- Recomendación: ACCEPT.
- Decisión (Lead/humano + fecha): **ACEPTADA** por el Lead, 2026-10-07 (DL-026). Implementada en `scayl/evidence/recent.py` con 3 regresiones; además se corrigió un fallo relacionado (contexto posterior al evento).

## AP-009 · Usar entradas históricas que el RSS actual de TVN sí conserva
- Autor / fecha: frictionspp-svg + Codex · 2026-10-06.
- Estado: **SUPERADA por DL-017**.
- Problema u oportunidad: GDELT DOC responde repetidamente 429 y las consultas TVN que respondieron no trajeron artículos; el muestreo histórico GKG no trajo TVN. Sin embargo, el RSS público descargado tiene 152 entradas: 48 con pubDate dentro de [2024-01-01, 2025-10-01), incluidas 3 de septiembre de 2025. La suposición de que el RSS solo contiene fechas actuales no se cumple en esta extracción.
- Cambio propuesto: incluir esas 48 entradas históricas, deduplicadas por URL, con origen=tvn_rss y fechas de publicación originales; conservar detección/extracción en 2026. Declarar la cobertura TVN más amplia que septiembre y conservar el RSS completo separado. Excluir del corpus las entradas posteriores al corte.
- Por qué mejora el proyecto: permite mantener el intervalo oficial sin fabricar fechas ni cambiar contratos; aporta al menos 20 registros reales del patrocinador.
- Dimensión de rúbrica: cobertura, reproducibilidad, procedencia y Temporal Guard.
- Archivos/módulos afectados: scayl/ingest/fetch_tvn.py, noticias.csv, manifest y catálogo. Ningún cambio de contracts.py ni del filtro oficial de B-03.
- Riesgos: publicación declarada por el RSS, no verificada contra el artículo; muestra histórica desigual y no exhaustiva. La fecha de detección de 2026 debe mantenerse visible como recirculación.
- Esfuerzo estimado: adaptador local y prueba de filtro por publicación.
- Recomendación: ACCEPT.
- Evidencia: data/raw/v1/responses/tvn-current/rss.xml y recibo SHA-256; data/raw/v1/tvn_rss_actual.json.
- Decisión (Lead/humano + fecha): **SUPERADA por DL-017, Lead, 2026-10-07**. Las 48 entradas antiguas quedan fuera; usar únicamente pubDate dentro de la ventana C-01 y fecha_deteccion nula.

## AP-008 · Cardinalidad de la cuadrícula World Bank (B-01)
- Autor / fecha: frictionspp-svg + Codex · 2026-10-06.
- Estado: **ACEPTADA (DL-013)**.
- Problema u oportunidad: los seis países y seis indicadores enumerados para 2010–2024 generan 6 × 6 × 15 = 540 claves únicas, no las 1.350 filas indicadas en TASKS y el catálogo.
- Cambio propuesto: confirmar 540 filas como cardinalidad, conservando exactamente países, indicadores y años; el Lead corregiría los documentos canónicos.
- Por qué mejora el proyecto: evita inventar países, indicadores, años o duplicados para alcanzar un total incompatible.
- Dimensión de rúbrica: calidad técnica y trazabilidad de datos.
- Archivos/módulos afectados: docs/TASKS.md (Lead), catálogo y diccionario; adaptador local scayl/ingest/fetch_worldbank.py.
- Riesgos: el número 1.350 podría referirse a dimensiones adicionales no documentadas.
- Esfuerzo estimado: confirmación del alcance; implementación local calcula el producto cartesiano explícito.
- Recomendación: ACCEPT.
- Decisión (Lead/humano + fecha): **ACEPTADA por Lead, 2026-10-07, DL-013**. Cuadrícula de 540 filas (6 países × 6 indicadores × 15 años), sin ampliar dimensiones.

> Todo cambio que afecte arquitectura, UX global, contratos de datos, alcance, seguridad, evaluación,
> dependencias, interfaces u otros workers se propone **aquí primero**. El Lead decide; los humanos
> deciden lo marcado como "requiere aprobación humana".
> Estados: `ABIERTA` · `ACEPTADA` · `RECHAZADA` · `DIFERIDA`.

## Plantilla

```
## AP-NNN · <título>
- Autor / fecha:
- Estado:
- Problema u oportunidad:
- Cambio propuesto:
- Por qué mejora el proyecto:
- Dimensión de rúbrica:
- Archivos/módulos afectados:
- Riesgos:
- Esfuerzo estimado:
- Recomendación: ACCEPT / CONSIDER / DEFER
- Decisión (Lead/humano + fecha):
```

---

## AP-001 · Enlace "en ejecución" en modo snapshot con salidas IA precalculadas
- Autor / fecha: Lead · 2026-10-06
- Estado: **ACEPTADA (2026-10-06)**: Hugging Face Space con contraseña, solo titular + URL, modo caché
- Problema u oportunidad: las Bases exigen el "enlace del agente desarrollado y en ejecución"; el objetivo 100% local choca con un hosting sin GPU.
- Cambio propuesto: desplegar la app Streamlit en modo `cache` (sin Ollama ni torch) con `bundle.json` y la caché LLM generada localmente, cada salida etiquetada con su modelo, prompt y hora. Destino: Hugging Face Space (privado/compartido con el jurado) o Streamlit Community Cloud; alternativa: túnel desde una laptop el día de la evaluación. Solo titular + URL; sin descripciones.
- Por qué mejora el proyecto: cumple un entregable obligatorio sin pagar APIs y sin mentir sobre el modo.
- Dimensión de rúbrica: condición de entrega; Prototipo (20); Seguridad/derechos (5).
- Archivos/módulos afectados: `deploy/`, `README.md`, `app/` (insignia de modo).
- Riesgos: redistribución de titulares (mitigado con acceso restringido); hay que regenerar la caché si cambia el bundle.
- Esfuerzo estimado: 2–3 h.
- Recomendación: **ACCEPT**.

## AP-002 · Streamlit sobre el núcleo Python en lugar de FastAPI + frontend separado
- Autor / fecha: Lead · 2026-10-06
- Estado: **ACEPTADA por Lead (DL-002)** — los humanos pueden revertirla hoy
- Problema u oportunidad: el brief prefiere FastAPI; con unas 52 h y 3 personas, una API HTTP + SPA duplica contratos, despliegue y puntos de fallo.
- Cambio propuesto: UI en Streamlit que importa `scayl.service` directamente. FastAPI solo si aparece un consumidor real (P2).
- Por qué mejora el proyecto: una sola ruta de ejecución (`make demo`), despliegue gratuito trivial y menos integración.
- Dimensión de rúbrica: Prototipo (20); Calidad técnica (10) "arquitectura proporcional".
- Archivos/módulos afectados: `app/`, `scayl/service.py`.
- Riesgos: menos control visual que React; se mitiga con componentes y CSS mínimos.
- Esfuerzo estimado: ahorra unas 8–12 h.
- Recomendación: **ACCEPT**.

## AP-003 · Fusionar los 10 módulos en 4 pantallas
- Autor / fecha: Lead · 2026-10-06 · Estado: **ACEPTADA por Lead (DL-003)**
- Problema u oportunidad: 10 módulos como pantallas no caben en el plazo y fragmentan la demo.
- Cambio propuesto: Sala de Situación · Ficha de Caso (6 pestañas) · Consultas · Trust Lab. Los 10 módulos siguen como capacidades.
- Por qué mejora el proyecto: el reto pide "abrir una ficha"; la demo es lineal.
- Dimensión de rúbrica: Utilidad (20), Prototipo (20). Archivos: `app/`.
- Riesgos: ninguno relevante. Esfuerzo: reduce trabajo. Recomendación: **ACCEPT**.

## AP-006 · Recibo de trazabilidad y métrica de preservación de atribución
- Autor / fecha: Lead · 2026-10-06 · Estado: **ACEPTADA (DL-009)**
- Problema u oportunidad: la investigación (arXiv 2509.25498) muestra que el error típico de los LLM en redacciones es convertir declaraciones atribuidas en hechos.
- Cambio propuesto: medir explícitamente la preservación de atribución y emitir un recibo con hash por cada decisión humana.
- Dimensión de rúbrica: Evidencias (15), IA (15), Notion (15: trazabilidad). Archivos: `scayl/gen/validators.py`, `scayl/review/`, `scayl/eval/`.
- Riesgos: bajos. Esfuerzo: 2–3 h. Recomendación: **ACCEPT**.

## AP-004 · Ampliar USGS a la ventana de las noticias
- Autor / fecha: Lead · 2026-10-06 · Estado: **ACEPTADA (DL-017, 2026-10-07)**: con la ventana oficial de 2026, sin esta extensión ningún sismo de 2024 coincide con las noticias
- Problema u oportunidad: USGS oficial cubre 2024 y las noticias rondan septiembre de 2025; puede que no haya vínculos sismo–noticia.
- Cambio propuesto: descarga adicional de USGS con la misma caja y M≥3 para la ventana de las noticias, en un archivo separado (`eventos_ext.geojson`) declarado como extensión.
- Por qué mejora el proyecto: permite demostrar un HECHO sustentado real.
- Dimensión de rúbrica: Evidencias (15). Archivos: `scayl/ingest/`, catálogo.
- Riesgos: desviación del paquete común (se documenta). Esfuerzo: 1 h. Recomendación: **CONSIDER** si el snapshot real no trae ningún vínculo.

## AP-005 · Generación "claim-first" con validador numérico
- Autor / fecha: Lead · 2026-10-06 · Estado: **ACEPTADA por Lead (DL-005)**
- Problema u oportunidad: el riesgo principal de un LLM local pequeño es inventar cifras o citas; una cita falsa obliga a corregir antes del cierre.
- Cambio propuesto: el LLM solo ve afirmaciones con ID y debe citarlas por oración; un validador determinista elimina oraciones con números o fechas que no estén en la evidencia citada.
- Por qué mejora el proyecto: la cobertura de citas al 100% es verificable por construcción; el diferenciador es demostrable en vivo.
- Dimensión de rúbrica: Evidencias (15), IA (15), Seguridad (5).
- Archivos/módulos afectados: `scayl/gen/*`.
- Riesgos: borradores más escuetos (aceptable). Esfuerzo: 3–4 h. Recomendación: **ACCEPT**.

## AP-007 · Proveedor opcional Claude (Sonnet 5.5) como comparación medida
- Autor / fecha: Lead · 2026-10-06 · Estado: **DIFERIDA** (equipo, 2026-10-06): primero se mide el modelo local (B-10); solo se reabre si la calidad local resulta insuficiente
- Problema u oportunidad: un modelo local de 8–9B puede dar borradores más pobres en español que un modelo de frontera; el equipo pregunta si usar Sonnet en la demo en vivo.
- Cambio propuesto: `scayl/gen/llm.py` con dos proveedores tras la misma interfaz: `ollama` (por defecto, offline) y `anthropic` (`claude-sonnet-5-5`, opcional con `ANTHROPIC_API_KEY`). Los mismos prompts, esquema JSON y validadores. El Trust Lab compara local frente a Sonnet: validez de citas, preservación de atribución, latencia y costo medidos.
- Por qué mejora el proyecto: convierte la elección de modelo en un resultado medido ("IA: mejora o limitación medida"); mantiene el relato local/$0 y el modo offline (T10).
- Dimensión de rúbrica: IA (15), Calidad técnica (10).
- Archivos/módulos afectados: `scayl/gen/llm.py`, `.env.example`, `requirements-ai.txt` (+`anthropic`), Trust Lab, docs de costo.
- Riesgos: costo (estimado de unos US$3–6 por 200 llamadas); dependencia de red (mitigada con fallback local y caché); solo se envían titulares públicos.
- Esfuerzo estimado: 1–2 h.
- Recomendación: **CONSIDER**. Local como camino principal; Sonnet como comparación y como respaldo de calidad si B-10 muestra borradores locales débiles.

## AP-010 · Evidencia oficial reciente: ACP (nivel del lago Gatún) e INEC (IPC mensual)
- Autor / fecha: Lead · 2026-10-07 · Estado: **ACEPTADA por el equipo (ACP + INEC), DL-019**
- Problema u oportunidad: con WB hasta 2024 (solo contexto) y noticias de 2026, casi ningún evento puede quedar "suficiente para el borrador". La aclaración C-02 permite fuentes adicionales y exige datos recientes en la demo.
- Cambio propuesto: (1) **ACP**, CSV de niveles históricos y proyectados del lago Gatún (evtms-rpts.pancanal.com/eng/h2o/), con la advertencia de la ACP de que es una estimación informativa; (2) **INEC**, IPC urbano nacional mensual 2025–2026 desde los cuadros PDF, citando cuadro y página. Contrato 0.3.0 aditivo: `IndicatorObservation.periodo` (p. ej. "2026-07" o "2026-09-28") y `fuente`; ids `ind:<fuente>:<serie>:<periodo>`. Vinculación: noticias del Canal → ACP; inflación → INEC. Coincidencia numérica ⇒ SUSTENTADA; discrepancia ⇒ conflicto.
- Por qué mejora el proyecto: permite afirmaciones recientes realmente sustentadas en la demo y muestra el Temporal Guard con datos reales (WB 2024 histórico frente a INEC 2026 reciente).
- Dimensión de rúbrica: Evidencias (15), Utilidad (20), cumplimiento de C-02.
- Archivos/módulos afectados: `scayl/contracts.py`, `scayl/evidence/linking.py` (Lead); fetchers en `scayl/ingest/` (worker con acceso a internet); catálogo.
- Riesgos: la extracción del PDF del INEC puede ser frágil (mitigación: pocas filas, verificación humana, cita de cuadro y página); tiempo.
- Esfuerzo estimado: ACP ~2 h; INEC ~3–4 h.
- Recomendación: **ACCEPT para ACP; CONSIDER para INEC** (solo si B-01 cierra a tiempo).

## AP-011 · Integración de A-03 con la tarjeta A-08 y la revisión del paquete
- Autor / fecha: LowCrime (Codex) · 2026-10-07
- Estado: **ACEPTADA (DL-020, 2026-10-07)**
- Problema u oportunidad: en main no existen `app/components/` ni A-08. Además, `service.generate_package()` devuelve un paquete sin persistirlo y `service.review()` vincula siempre el paquete del snapshot; la API pública tampoco expone la descarga del recibo.
- Cambio propuesto: frictionspp-svg publica la ruta de importación de `evidence_card(ref)` (A-08); LowCrime conecta allí el adaptador local de A-03. El Lead define persistencia/identidad del paquete revisado y acceso al recibo desde `service`, sin lecturas directas de SQLite desde la UI.
- Por qué mejora el proyecto: evita duplicar la tarjeta y aprobar un paquete distinto del visible; permite completar la trazabilidad requerida por L-16.
- Dimensión de rúbrica: Evidencias, control humano y trazabilidad.
- Archivos/módulos afectados: `app/pages/1_Ficha_de_Caso.py` (LowCrime), `app/components/` (frictionspp-svg), `scayl/service.py` y eventualmente `scayl/review/` (Lead).
- Adaptador local mientras se decide: referencias completas en JSON desplegable; identificación explícita del paquete del snapshot en Revisión; se bloquea guardar si el paquete visible difiere, con opción de volver al snapshot. No se implementa otra tarjeta ni se cambia el servicio. PR de A-03 en borrador hasta integrar A-08.
- Riesgos: A-03 no se declara cerrada mientras falte la tarjeta compartida; descarga del recibo pendiente de API.
- Esfuerzo estimado: integración UI ~1 h tras publicar las interfaces.
- Recomendación: ACCEPT.
- Decisión (Lead/humano + fecha): **ACEPTADA por Lead, 2026-10-07, DL-020**. `service.review(..., package=...)` y `service.receipt(review_id)` publicados en main. A-08, A-01 y A-02 reasignadas a LowCrime. A-08 implementada e integrada en A-03; se retira el adaptador JSON y el bloqueo temporal de revisión. El recibo identifica el contenido visible por id y sha256.

## AP-013 · Validar la salida extractiva y revisar el prefiltro temporal de Consultas
- Nota del Lead: llegó numerada como AP-012, número que ya usaba frictionspp-svg; se renumera a AP-013.
- Autor / fecha: LowCrime (Codex), 2026-10-07.
- Estado: **ACEPTADA** (DL-027).
- Problema: RT01–04 reproducen instrucciones de titulares en la respuesta de service.ask(template). El validador posterior sí las rechaza. RT05–06 y RT09–12 no se abstienen ante premisas numéricas o períodos ausentes/actuales; devuelven filas históricas, etiquetadas con año. No se afirma que hayan inventado esas cifras.
- Cambio propuesto: aplicar check_sentence también en _extractive, con abstención explícita si no sobrevive contenido; revisar consultas de actualidad y condición de año pedido (el año de publicación de otra unidad puede permitir una fila histórica). Acordar política para corregir premisas frente a abstenerse.
- Por qué mejora: respuesta extractiva y LLM comparten controles; errores y limitaciones visibles.
- Dimensión de rúbrica: seguridad, evidencia y evaluación.
- Archivos afectados: scayl/gen/qa.py, pruebas T06/T07 (dueño Lead).
- Adaptador local: scayl/eval/redteam.py valida después y registra el original intacto; no altera servicio, umbrales ni prompts.
- Riesgos: más abstenciones; medir también los cuatro controles contestables. El set es desarrollo sintético de IA, no gold humano ni prueba viva.
- Esfuerzo estimado: un bloque de revisión + regresiones.
- Recomendación: ACCEPT.
- Decisión (Lead/humano + fecha): **ACEPTADA** por el Lead, 2026-10-07 (DL-027). Política: ante una premisa con una cifra ausente, el sistema **se abstiene**; no corrige con otra cifra sin que se le pregunte por ella.
