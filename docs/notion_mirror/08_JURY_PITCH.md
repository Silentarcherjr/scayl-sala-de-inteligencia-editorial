# 08 · Presentación al jurado (10 min + 5 de preguntas)

> Estructura oficial: problema → solución → demo → IA y evidencias → resultados → límites → próximos pasos.
> Regla: solo cifras medidas (fuente en `eval/results/`); lo no medido se dice "no medido".

| Min | Bloque | Qué decir |
|---|---|---|
| 0:00–1:00 | **Problema** | "Un editor de TVN recibe cientos de señales al día. Ver algo repetido no lo confirma, y un dato viejo puede parecer nuevo. El costo es tiempo y errores de contexto." |
| 1:00–2:00 | **Solución** | "SCAYL lleva la señal hasta una historia investigable: evento → prioridad → evidencia → vacíos → borrador citado → **decisión humana**. Con dos reglas: la prioridad no es verdad, y la IA no publica." |
| 2:00–6:00 | **Demo en vivo** (guion `docs/DEMO_SCRIPT.md`, escenas 1–6; respaldo: demo local) | Sala → Ficha del Canal (Source DNA, ACP con fecha, vacíos) → EVT-0078 (dos medios, independencia no demostrable, ACP fechada, dato histórico, vacíos) → Consultas (Gatún con fecha; "moneda" con abstención; cifra falsa con abstención) → borrador citado → aprobado como borrador con recibo. |
| 6:00–8:00 | **IA medida, no por moda** | "Usamos IA donde ganó y reglas donde perdió: E5 agrupa (F1 0,99 frente a 0,44 en evaluación de desarrollo utilizada para calibrar), pero para temas las reglas sacaron 0,76 contra 0,25. Qwen3 8B genera localmente (13,1 s de mediana, sin cargos de API; hardware y electricidad excluidos). Gemini es un proveedor externo opcional con cuota y costo sujetos al proyecto La evaluación de Qwen registró 45/45 frases con cita; los validadores comprueban las referencias y cifras." |
| 8:00–9:00 | **Confianza** | "442 pruebas automatizadas aprobadas. El red-team de desarrollo registró 16/16 abstenciones correctas y el set humano reservado, 6/6 trampas. La revisión humana de paquetes en modo plantilla registró sustento válido en 25/30 afirmaciones. Los resultados y su alcance están documentados." |
| 9:00–10:00 | **Límites y siguientes pasos** | "Hoy solo hay titulares, así que ningún caso real llega a 'suficiente', y eso es lo correcto. Siguientes pasos: cuerpos de artículos con licencia de TVN, más fuentes oficiales (SINAPROC, MEF) y operación diaria." Cierre: **"SCAYL no decide qué se publica: acorta el camino de la señal a una historia trazable, lista para la decisión humana."** |

## Respuestas preparadas (pruebas dinámicas del jurado)
- **"¿De dónde viene esta cifra y de qué año es?"** → Tarjeta de evidencia: `evidence_id`, campo, valor, período y URL (ej.: `ind:acp:ACP.GATUN.NIVEL:2026-09-29`).
- **"Si cinco medios replican la misma agencia, ¿cuántas fuentes independientes hay?"** → Una procedencia. Source DNA agrupa por medio, titular idéntico o firma de agencia, y nunca declara independencia que no puede demostrar.
- **"¿Qué pasa si no hay evidencia?"** → Abstención con motivo y con la información que faltaría (Consultas: "¿Cuál es la moneda oficial de Panamá?").
- **"¿Y si una fuente trae instrucciones maliciosas?"** → Se marca como dato sospechoso, nunca se cita ni se envía al modelo; red-team 16/16 (Trust Lab).
- **"Muéstrame una decisión, una prueba fallida y su corrección."** → DL-027: el red-team encontró que el modo sin modelo copiaba titulares con inyección (6/16); se corrigió con reglas generales y pruebas de regresión (16/16). Registro completo en 06.
- **"¿Por qué ningún evento es 'suficiente'?"** → Ningún titular del corpus cita una cifra oficial comparable (Gatún, IPC). Confirmar sin cifra sería inventar. Los casos sintéticos etiquetados (B-04) muestran cómo se ve un "suficiente".
- **"¿Cuánto tiempo ahorra?"** → El ahorro de tiempo es una hipótesis para validar en una redacción; las métricas actuales evalúan calidad y comportamiento técnico.
- **"¿Cuánto cuesta?"** → $0 de API para Qwen local, excluyendo hardware y electricidad. Gemini externo opcional: cuota/costo sujetos al proyecto; costo global no medido.

## Material
- Capturas: `docs/screenshots/final/` · Respaldo: demo local · Métricas: Trust Lab y `eval/results/latest.json`.

Consultas ofrece Gemini externo opcional para redacción citada; cada salida identifica su modo. `/verificar/` compara evidencia de forma determinista, sin IA generativa.
