# AGENT_PROPOSALS — propuestas transversales

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
- Autor / fecha: Lead · 2026-10-07 · Estado: **ABIERTA — requiere aprobación humana** (agrega alcance)
- Problema u oportunidad: con WB hasta 2024 (solo contexto) y noticias de 2026, casi ningún evento puede quedar "suficiente para el borrador". La aclaración C-02 permite fuentes adicionales y exige datos recientes en la demo.
- Cambio propuesto: (1) **ACP**, CSV de niveles históricos y proyectados del lago Gatún (evtms-rpts.pancanal.com/eng/h2o/), con la advertencia de la ACP de que es una estimación informativa; (2) **INEC**, IPC urbano nacional mensual 2025–2026 desde los cuadros PDF, citando cuadro y página. Contrato 0.3.0 aditivo: `IndicatorObservation.periodo` (p. ej. "2026-07" o "2026-09-28") y `fuente`; ids `ind:<fuente>:<serie>:<periodo>`. Vinculación: noticias del Canal → ACP; inflación → INEC. Coincidencia numérica ⇒ SUSTENTADA; discrepancia ⇒ conflicto.
- Por qué mejora el proyecto: permite afirmaciones recientes realmente sustentadas en la demo y muestra el Temporal Guard con datos reales (WB 2024 histórico frente a INEC 2026 reciente).
- Dimensión de rúbrica: Evidencias (15), Utilidad (20), cumplimiento de C-02.
- Archivos/módulos afectados: `scayl/contracts.py`, `scayl/evidence/linking.py` (Lead); fetchers en `scayl/ingest/` (worker con acceso a internet); catálogo.
- Riesgos: la extracción del PDF del INEC puede ser frágil (mitigación: pocas filas, verificación humana, cita de cuadro y página); tiempo.
- Esfuerzo estimado: ACP ~2 h; INEC ~3–4 h.
- Recomendación: **ACCEPT para ACP; CONSIDER para INEC** (solo si B-01 cierra a tiempo).
