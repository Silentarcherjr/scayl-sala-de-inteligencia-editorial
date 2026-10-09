# Análisis de Precision@5 (C5) — por qué 1/5 y qué no cambiamos

> Análisis del Lead (IA) sobre el bundle publicado (`web/public/data/bundle.json`, 165 eventos, `scoring-v1`) y la
> selección exploratoria `data/labels/editor_top5.json` (un integrante, 2026-10-07, antes de existir el ranking).
> **No se ajustaron pesos con esta lista**: es el conjunto de evaluación; ajustarlo a ella sería sobreajuste.

## Dónde quedó cada elección del editor
| Rango del sistema | Evento | P | Titular | Noticias |
|---|---|---|---|---|
| 3 | EVT-0078 | 72,1 | Canal de Panamá reduce el tránsito de buques por El Niño | 2 |
| 6 | EVT-0143 | 69,9 | El Canal aplica nueva reducción del calado para enfrentar El Niño | 1 |
| 10 | EVT-0107 | 67,5 | Cuarto Puente sobre el Canal: 39 % de avance | 1 |
| 19 | EVT-0087 | 65,1 | El Niño fait baisser le niveau du canal de Panama (francés) | 1 |
| 23 | EVT-0121 | 65,1 | ¿Por qué el Canal listó su bono en Latinex? | 1 |

Top 5 del sistema: EVT-0101 (cupos y calado Neopanamax, 89,9), EVT-0116 (ajustes de calado por El Niño, 72,3),
**EVT-0078** (72,1, coincide), EVT-0051 (buque gasífero surcoreano, 70,9), EVT-0083 (titular en maratí, 69,9).

## Diagnóstico
1. **Mismo tema, distinto hecho.** Los diez eventos (editor y sistema) son de `logistica_canal`. El sistema no prioriza
   un tema equivocado: ordena dentro del mismo tema con señales débiles. Entre el puesto 3 y el 23 hay solo 7 puntos de P.
2. **Una historia partida en varios eventos.** «El Niño reduce tránsito/calado del Canal» aparece como EVT-0078,
   EVT-0116, EVT-0143 y EVT-0087 (en francés). La métrica cuenta eventos, así que la fragmentación penaliza dos veces: la
   historia ocupa varios puestos y ninguno suma volumen. Es un problema de agrupación, no de pesos.
3. **R e I casi constantes dentro del tema.** Todo titular del Canal recibe la misma relevancia y el mismo peso
   editorial, de modo que deciden U (aproximada por la hora de detección de GDELT cuando falta la fecha de publicación) y
   E. Por eso suben noticias de relleno (buque que cruza el Canal, titular en maratí).
4. **El volumen apenas pesa** (1–2 noticias por evento) y **el interés público** (impacto en el país, movilidad,
   finanzas públicas), que fue el criterio declarado del editor, no tiene un componente explícito.

## Qué haríamos (no aplicado en la entrega)
- Agrupar a nivel de historia, incluidas las variantes multilingües, antes de rankear; validarlo con pares **nuevos**,
  no con los de calibración.
- Un componente de interés público por subtema (operación del Canal frente a noticias de paso), diseñado con criterios
  editoriales de TVN y evaluado con **nuevas selecciones ciegas** de varias personas.
- Volver a medir P@5 con un panel, no con una sola lista exploratoria.

## Lectura honesta
- P@5 = 1/5 frente a una sola selección exploratoria; su incertidumbre es enorme (n = 5, un evaluador).
- Leído por historia en lugar de por evento, el top 5 del sistema sí contiene la historia de El Niño que eligió el
  editor (3 de sus 5 elecciones). Es una **lectura cualitativa a posteriori**, no una métrica: no la reportamos como P@5.
