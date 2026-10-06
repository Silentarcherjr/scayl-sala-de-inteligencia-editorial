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
