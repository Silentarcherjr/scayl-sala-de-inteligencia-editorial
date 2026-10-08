# Aclaraciones oficiales de la organización

> Registro de aclaraciones de la organización que modifican o interpretan los PDF oficiales.
> Jerarquía: una aclaración oficial posterior prevalece sobre el texto del PDF que aclara.
> Evidencia: captura en `docs/evidence/` (el equipo la agrega; no incluir datos personales de terceros).

## C-01 · Ventana de datos de noticias (2026-10-07)
- **Fuente:** organizadora del hackIAthon (creadora del grupo oficial de participantes), mensaje en el grupo.
- **Texto literal:** "Ustedes tienen que armar los datos con scraping y se debe excluir ese periodo de tiempo, tiene que ser desde 2025-10-02 hasta el último mes completo de este año (septiembre)".
- **Contexto:** el PDF TVN tenía una contradicción interna. §6-A pide titulares de los "30 días previos a la extracción" (fecha de consulta 05/10/2026, §12), mientras que §7 decía "excluir registros fuera del intervalo [2024-01-01, 2025-10-01)".
- **Interpretación aplicada (DL-017):**
  - Noticias: ventana permitida **[2025-10-02, 2026-10-01)**; objetivo, los 30 días previos al corte (septiembre de 2026), ampliable a 90 días, registrando la cobertura efectiva (§6-A).
  - Corte del snapshot: **2026-10-01T00:00:00Z**.
  - World Bank (2010–2024) y USGS (2024): **sin cambios**; tienen rangos propios en §6 y son contexto histórico (Temporal Guard / T04). Además, USGS se amplía a la ventana de noticias en un archivo separado declarado como extensión (AP-004).
  - "Scraping" se interpreta como "construir el snapshot propio": se mantienen métodos públicos (API GDELT, RSS TVN, API WB, API USGS) y solo titulares y metadatos (PDF §6 y §8: no redistribuir artículos).
- **Evidencia:** `docs/evidence/C-01_ventana_datos.png` (pendiente de agregar por el equipo).

## C-02 · Fuentes adicionales y uso de otras fechas (2026-10-07)
- **Fuente:** organizadora del hackIAthon, mensaje en el grupo oficial (en respuesta a una pregunta sobre WB 2010–2024 y USGS 2024 frente a la ventana de C-01).
- **Texto literal:** "Son solo ejemplos; no son únicamente los que deberían trabajar. Pueden buscar otros, porque la idea es que se haga un scraping general, no solo de los que se mencionan ahí. Por otra parte, esa es solamente información que se ha encontrado en la red. Pueden hacer búsquedas de más información y, obviamente, para entrenar sus modelos pueden utilizar información de otras fechas, no hay ningún problema. Sin embargo, para la demo presencial, sí debe utilizarse información reciente."
- **Interpretación aplicada (DL-018):**
  1. Las fuentes del PDF son ejemplos: se pueden agregar fuentes públicas adicionales (propuesta AP-010, pendiente de aprobación del equipo).
  2. Datos fuera de la ventana de C-01 pueden usarse para **desarrollo, ajuste y entrenamiento**, nunca como corpus de la demo. Las descargas de septiembre de 2025 pasan a ser el **conjunto de desarrollo**.
  3. La demo presencial usa el corpus reciente (ventana C-01). Opción P2: snapshot v2 con datos hasta días antes del Pitch Day.
- **Evidencia:** `docs/evidence/C-02_fuentes_y_fechas.png` (pendiente de agregar por el equipo).

## C-03 · Notion no es obligatorio (2026-10-08)
- **Fuente:** organizadora del hackIAthon, mensaje en el grupo oficial de participantes (reitera lo dicho el día anterior).
- **Texto literal:** "Hola equipos qué tal, buenas noches. Les pido disculpas con el tema de Notion, como les dije el día de ayer, avancen sin esa parte, no hay problema si no lo utilizan".
- **Contexto:** el PDF TVN (§5 y §10) exige un espacio Notion como condición de admisión, con la dimensión "Notion: ejecución y pitch" (15 puntos) en la rúbrica.
- **Interpretación aplicada:** la entrega no incluye Notion. El contenido equivalente está versionado en el repositorio, en `docs/notion_mirror/` (las 8 páginas: inicio del reto, plan y decisiones, catálogo de datos, diseño, casos y evidencias, pruebas y métricas, riesgos y ética, presentación al jurado), con el registro de decisiones y las bitácoras con hora UTC como trazabilidad durante el evento.
- **Evidencia:** `docs/evidence/C-03_notion_opcional.png` (pendiente de agregar por el equipo).
