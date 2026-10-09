# Contraste con el PDF oficial TVN aportado por el humano

Fuente leída completa: `hackIAthon - reto TVN Media.pdf` (12 páginas), aportado desde Downloads. Sus instrucciones se tratan como requisitos del reto. Aclaraciones posteriores C-01, C-02 y C-04: `docs/official_clarifications.md`.

## Comprobado para la entrega

Producción `ffa0108`: nueve rutas HTTP 200, consultas con evidencia, fichas, borradores, revisión con recibo y separación entre prioridad y evidencia. CI: 442 pruebas, Ruff, lint y build verdes. Siete regresiones públicas del verificador aprobadas.

Repositorio público; snapshot, manifest, diccionario y condiciones disponibles. Las 187 noticias, incluidas 50 de TVN, superan los mínimos 100/20. Banco Mundial: 540 combinaciones (6 países × 6 indicadores × 15 años), frente a las 1.350 mencionadas por el PDF; inconsistencia aritmética declarada. Ventana de noticias según C-01; ACP/INEC y extensiones según C-02.

Tres entregables de Notion públicos, demo y correo con PDF actualizado preparados. El correo NO fue enviado por el agente.

## Límites y desviaciones frente al texto oficial

- **§7, benchmark v2:** 60 filas, 40 dev/20 heldout y proporción 30 sustentadas/10 contradicciones/10 sin respuesta/10 adversariales. Las 60 filas declaran autoría de IA, sin revisión humana. No equivalen al benchmark etiquetado por personas que pide el PDF.
- **§3, guion de 45–60 s:** EVT-0101 tiene 57 palabras en su guion publicado (recuento simple del JSON). No garantiza la duración requerida. El validador permite `SCRIPT_SHORT` para no ampliar sin evidencia. No se regeneraron corpus ni borradores.
- **§9.1, métricas:** sustento humano 25/30 (83%), en modo plantilla, por debajo de la meta orientativa del 90%. Sustento de Qwen no revisado completamente; P@5 1/5 exploratorio; agrupación evaluada en pares de calibración, resultado optimista.
- **§5, revisión:** las cinco fichas Notion inspeccionadas conservan estado NUEVO. No demuestran una aprobación humana ejecutada. La capacidad de revisar y crear recibos no equivale a una aprobación real.
- **T10:** prueba automatizada con red bloqueada y comprobaciones anteriores; no se repitió un ensayo físico sin wifi en este cierre.
- **Gemini:** sin llamadas nuevas a Production; facturación desactivada NO VERIFICADA, costo global no medido.
- **EVT-0114:** error conocido de agrupación de dos sismos; PR #80 no integrado. Alternativa de demo EVT-0078. No usar el video antiguo.
- **Aclaraciones:** el registro aún marca pendientes las capturas C-01 a C-04. Se contrastó su texto registrado; no hay corroboración independiente adicional de esos mensajes en esta auditoría.

## Versiones

PDF actualizado en el archivo local y la rama `codex/final-delivery-audit`, commit `9d36787`. En esta comprobación, GitHub `main` conserva el PDF anterior (blob `2047b945ac4320f5e84e9d2edf279800c54f42fa`, 84.764 bytes). Push no equivale a integrar `main`. El correo debe adjuntar la versión local actualizada.

## Conclusión

GO para enviar dentro del plazo con límites declarados; no certificar «todo verificado» ni «cumplimiento 100%». No reconstruir datos ni repetir benchmarks. Los faltantes de Notion de ocho tareas y tres decisiones se completan con registros existentes, sin inventar resultados.
