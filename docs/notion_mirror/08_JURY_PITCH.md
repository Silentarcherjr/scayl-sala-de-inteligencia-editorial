# 08 · Presentación al jurado (10 min + 5 de preguntas)

> Estructura oficial: problema → solución → demo → IA y evidencias → resultados → límites → próximos pasos.
> Regla: solo cifras medidas (fuente en `eval/results/`); lo no medido se dice "no medido".

| Min | Bloque | Qué decir |
|---|---|---|
| 0:00–1:00 | **Problema** | "Un editor de TVN recibe cientos de señales al día. Ver algo repetido no lo confirma, y un dato viejo puede parecer nuevo. El costo es tiempo y errores de contexto." |
| 1:00–2:00 | **Solución** | "SCAYL lleva la señal hasta una historia investigable: evento → prioridad → evidencia → vacíos → borrador citado → **decisión humana**. Con dos reglas: la prioridad no es verdad, y la IA no publica." |
| 2:00–6:00 | **Demo en vivo** (guion `docs/DEMO_SCRIPT.md`, escenas 1–6; plan B: el video) | Sala → Ficha del Canal (Source DNA, ACP con fecha, vacíos) → sismo con conflicto 4.7/4.5/7.4 → Consultas (Gatún con fecha; "moneda" con abstención; cifra falsa con abstención) → borrador citado → aprobado como borrador con recibo. |
| 6:00–8:00 | **IA medida, no por moda** | "Usamos IA donde ganó y reglas donde perdió: E5 agrupa (F1 0,99 frente a 0,44), pero para temas las reglas sacaron 0,76 contra 0,25. El LLM es local (qwen3:8b, 13 s de mediana, $0) y lo vigila código: 45/45 frases con cita; las frases sin respaldo se eliminan." |
| 8:00–9:00 | **Confianza** | "Nuestro propio red-team nos encontró fallos: 6/16. Los corregimos: 16/16. Luego un integrante escribió preguntas nuevas sin ver los casos existentes: 6/6 trampas con abstención correcta, aunque también se abstuvo en 4/4 preguntas de cultura general que no están en el corpus. Cada fallo y su corrección está en el registro." |
| 9:00–10:00 | **Límites y siguientes pasos** | "Hoy solo hay titulares, así que ningún caso real llega a 'suficiente', y eso es lo correcto. Siguientes pasos: cuerpos de artículos con licencia de TVN, más fuentes oficiales (SINAPROC, MEF) y operación diaria." Cierre: **"SCAYL no decide qué se publica: acorta el camino de la señal a una historia trazable, lista para la decisión humana."** |

## Respuestas preparadas (pruebas dinámicas del jurado)
- **"¿De dónde viene esta cifra y de qué año es?"** → Tarjeta de evidencia: `evidence_id`, campo, valor, período y URL (ej.: `ind:acp:ACP.GATUN.NIVEL:2026-09-29`).
- **"Si cinco medios replican la misma agencia, ¿cuántas fuentes independientes hay?"** → Una procedencia. Source DNA agrupa por medio, titular idéntico o firma de agencia, y nunca declara independencia que no puede demostrar.
- **"¿Qué pasa si no hay evidencia?"** → Abstención con motivo y con la información que faltaría (Consultas: "¿Cuál es la moneda oficial de Panamá?").
- **"¿Y si una fuente trae instrucciones maliciosas?"** → Se marca como dato sospechoso, nunca se cita ni se envía al modelo; red-team 16/16 (Trust Lab).
- **"Muéstrame una decisión, una prueba fallida y su corrección."** → DL-027: el red-team encontró que el modo sin modelo copiaba titulares con inyección (6/16); se corrigió con reglas generales y pruebas de regresión (16/16). Registro completo en 06.
- **"¿Por qué ningún evento es 'suficiente'?"** → Ningún titular del corpus cita una cifra oficial comparable (Gatún, IPC). Confirmar sin cifra sería inventar. Los casos sintéticos etiquetados (B-04) muestran cómo se ve un "suficiente".
- **"¿Cuánto tiempo ahorra?"** → No medido (mini-estudio pendiente); no lo afirmamos.
- **"¿Cuánto cuesta?"** → $0 de API: todo corre local. El hardware está declarado (RX 9060 XT 8 GB).

## Material
- Capturas: `docs/screenshots/final/` · Video: grabación local del Humano 1 (H-05) · Métricas: Trust Lab y `eval/results/latest.json`.
