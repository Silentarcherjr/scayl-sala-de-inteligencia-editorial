# Agenda de la mañana · A-07

Home monta app.components.agenda.agenda(bundle, weights) encima de los filtros. Presenta hasta
cinco eventos del snapshot completo, ordenados por P descendente, U descendente e ID ascendente.
No cambia al filtrar la tabla de abajo. Corte en hora de Panamá.

Cada tarjeta incluye título, P/rango, evidencia separada, marca sintética cuando corresponde,
las dos rationale de mayor contribución (peso × componente), recommended_action literal y enlace
a la ficha. Las fuentes sugeridas se conservan dentro de recommended_action; nunca se presentan
como evidencia. No se extraen instituciones ni se añaden recomendaciones inventadas.

Pruebas: 123 passed en esta rama (dos nuevas); los 7 tests de Consultas viven en el PR #25,
independiente. Se verifican contribuciones ponderadas, límite de cinco y estabilidad ante filtros.
Captura Chromium 1280×720 con snapshot real: [Agenda](screenshots/a07-agenda.png).
