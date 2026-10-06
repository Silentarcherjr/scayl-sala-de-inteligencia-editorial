# 08 · Presentación al jurado (10 min + 5 de preguntas)

> Estructura oficial: problema → solución → demo → IA y evidencias → resultados → límites → próximos pasos. Se presenta **desde Notion**.

| Min | Bloque | Contenido |
|---|---|---|
| 0–1 | Problema y usuario | El editor de TVN recibe cientos de señales; repetición ≠ confirmación; el costo es tiempo y errores de contexto. |
| 1–2 | Solución y alcance | SCAYL: señal → evento → prioridad → evidencia → investigación → producción → revisión humana. Datos públicos congelados (TVN, GDELT, WB, USGS). |
| 2–6 | Demo (4 min) | Guion en `docs/MASTER_PLAN.md` §5. |
| 6–8 | Arquitectura, IA, baseline, métricas | Diagrama; embeddings frente a TF-IDF (tabla medida); LLM local acotado + validadores; Trust Lab. |
| 8–9 | Valor operativo | Solo valor medido o hipótesis claramente marcada. |
| 9–10 | Riesgos, límites y próximos pasos | Solo titulares; independencia rara vez demostrable; snapshot por lotes; próximos pasos: cuerpos con licencia, fuentes oficiales panameñas (INEC, SINAPROC, ACP). |

## Respuestas preparadas (pruebas dinámicas del jurado)
- **"¿De dónde proviene esta cifra y de qué año es?"** → chip de cita → evidence_id, campo, valor, año y URL.
- **"Si cinco medios replican la misma agencia, ¿cuántas fuentes independientes cuentas?"** → Una procedencia. Source DNA lo muestra.
- **"¿Qué pasa si no hay evidencia o una fuente intenta cambiar las instrucciones?"** → Abstención (T06) e inyección ignorada y marcada (T07).
- **"Muéstrame una decisión, una prueba fallida y su corrección."** → 02_DECISION_LOG + registro en 06.

**Cierre:** "SCAYL no decide qué se publica. Reduce el tiempo entre detectar una señal y obtener una historia investigable y trazable, lista para la decisión editorial humana."
