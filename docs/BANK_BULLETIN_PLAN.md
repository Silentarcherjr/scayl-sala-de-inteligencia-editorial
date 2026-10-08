# Extensión bancaria: boletín de entorno (DL-035) · brief para el agente

> **Aprobado por el Lead (Humano 1, Silentarcherjr) el 2026-10-08 — DL-035.** Cubre los cambios aditivos
> descritos aquí en `scayl/contracts.py`, `scayl/gen/`, `scayl/service.py`, `scripts/export_web.py` y `web/`.
> Lo que esté fuera de este alcance requiere propuesta. **Plazo duro:** jueves 8 de octubre, 23:59 (hora de
> Panamá). Si a las 18:00 de Panamá no está estable la etapa 3, se entrega solo hasta la etapa que pase la
> verificación completa (§8) y el resto se descarta. **Nunca** mergear algo a medias.

## 1. Qué pide el reto (PDF TVN, citar al documentar)
- La modalidad bancaria se admite **"como alternativa o extensión, sin exigir dos productos completos"**.
  SCAYL sigue siendo editorial; esto es una **extensión** que demuestra que *el mismo núcleo* sirve a otro usuario.
- **Usuario:** analista de estudios económicos o riesgo **sectorial**. Nunca evalúa clientes.
- **Salida "boletín de entorno":** resumen de **hasta 250 palabras**, **sectores potencialmente relacionados**,
  **horizonte temporal**, **evidencia** y **3 preguntas para el analista**. **Separar observación de hipótesis de
  impacto.** "No recomendar compra/venta ni inferir pérdidas, impagos o exposición de una cartera inexistente."
- **CU-05:** "¿Qué señales públicas del entorno logístico debo revisar?" → contexto sectorial, **no** un score de
  clientes **ni** una alerta regulatoria definitiva.
- **T09:** "Formato útil, citas pertinentes y distinción de hechos e inferencias."
- Restricción común: con solo titular/metadatos, decir **"Basado únicamente en titular/metadatos"**.
- **Fuera de alcance:** datos de la SBP (extensión opcional del PDF; no hay tiempo para incorporarlos bien).

## 2. Reglas (no negociables)
- Rama `worker-web/bank-bulletin`, PR a `main`. Mergea el Lead. Un commit por etapa (§7).
- **Solo cambios aditivos.** No modificar comportamiento existente: Story Studio, Q&A, ranking, contratos
  existentes, Streamlit (`app/`), `deploy/` ni pruebas existentes. Todas las pruebas actuales deben seguir verdes.
- **Reutilizar** el patrón de `scayl/gen/studio.py`: prompt versionado, datos como bloque no confiable
  (`guard.data_block`), salida con esquema, **validadores deterministas** y **fallback a plantilla**.
- Ninguna cifra puede aparecer en el boletín si no está en la evidencia citada (reusar `numbers_in` /
  `evidence_numbers` y `check_sentence` de `scayl/gen/validators.py`). Nulos nunca se convierten en 0.
- Datos históricos (Banco Mundial, años anteriores) siempre con su período y la advertencia temporal existente.
- **Lenguaje prohibido** (validador nuevo, case-insensitive, también en la plantilla): recomendaciones de inversión
  ("comprar", "vender", "invertir", "recomendamos", "oportunidad de inversión"), y "impago", "mora", "default",
  "pérdida(s)", "cartera", "exposición", "solvencia", "riesgo de crédito", "calificación crediticia",
  "cliente(s)". Si aparece en una salida LLM → se descarta esa oración y se registra un `ValidationIssue`
  (`FORBIDDEN_BANKING_TERM`); si la salida queda sin resumen → fallback a plantilla.
  Excepción: el **aviso fijo** de alcance (§3) puede nombrar estos conceptos para negarlos.
- Ninguna API paga. LLM solo vía el `LLM` existente (Ollama local / caché). Modo visible en la UI.

## 3. Contrato (aditivo en `scayl/contracts.py`, `CONTRACT_VERSION` → `0.4.0`, comentario "additive")
```python
class SectorBulletin(_Model):
    bulletin_id: str            # BUL-<sector>-v1
    sector: str                 # "logistica_canal" | "economia"
    question: str               # p. ej. CU-05 literal para logística
    horizon: str                # texto: ventana del snapshot, p. ej. "septiembre 2026 (corte 2026-10-01)"
    summary: list[TaggedSentence]          # <= 250 palabras en total
    observations: list[TaggedSentence]     # tag HECHO/DECLARACION, cada una con claim_ids o evidence_ids
    impact_hypotheses: list[TaggedSentence]  # tag HIPOTESIS o INFERENCIA, nunca HECHO
    related_sectors: list[str]             # sectores potencialmente relacionados (texto corto)
    analyst_questions: list[str] = Field(min_length=3, max_length=3)
    event_ids: list[str]                   # eventos usados, en orden de prioridad oficial
    sources: list[EvidenceRef]
    scope_disclaimer: str | None           # "Basado únicamente en titular/metadatos" cuando aplique
    limits_notice: str                     # aviso fijo de alcance (texto abajo)
    validation: ValidationReport
    generated_by: GenerationMeta
```
`limits_notice` fijo: *"Boletín de contexto sectorial para análisis. No evalúa clientes, no recomienda
comprar ni vender, no infiere pérdidas, impagos ni exposición de cartera, y no es una alerta regulatoria."*

## 4. Núcleo: `scayl/gen/bulletin.py` (+ `scayl/gen/prompts/bulletin.v1.md`)
- **Selección de eventos:** los de `topic == sector`, en el orden oficial (`ranked_events` de Home), top 5.
  Para `economia` incluir además los indicadores oficiales ya presentes en esos eventos (`official_evidence`).
- `build_template_bulletin(events, sector, cutoff)`: **determinista**, sin LLM. Observaciones = afirmaciones
  `SUSTENTADA` o `SOLO_REPORTADA` de esos eventos (con su tag y claim_ids, reportadas como "se reporta");
  hipótesis = frases fijas por sector redactadas como hipótesis condicionales y genéricas, sin cifras
  (p. ej. logística: "Si se mantienen los ajustes de calado, podrían variar los tiempos de tránsito; requiere
  verificación con la ACP."); preguntas = derivadas de `gap.investigate_next` de los eventos + preguntas
  fijas por sector; `related_sectors` = lista fija por sector (logística: transporte marítimo, comercio
  exterior, zona libre / logística terrestre; economía: consumo, construcción, turismo).
- `generate_bulletin(sector, llm)`: si `llm.mode == "template"` → plantilla. Si no, prompt con los claims
  numerados en bloque de datos, esquema JSON, validación (§2) y **fallback a plantilla** ante cualquier fallo,
  igual que `studio.generate_with_report`. Registrar el fallback en `validation.issues`.
- `service.sector_bulletin(sector) -> SectorBulletin` (aditivo).
- **Precálculo con IA (opcional, etapa 4):** si frictionspp-svg puede correr Ollama `qwen3:8b` en su equipo,
  `python -m scayl.gen.bulletin --precompute` genera en modo `live` las 2 entradas y las guarda en la caché
  (mismo mecanismo de `cache_key`); se copian a `deploy/artifacts/v1/llm/` solo tras revisión humana de
  procedencia. Sin eso, el boletín queda en modo `template`, rotulado como "Plantilla (sin IA generativa)".

## 5. Web (`web/`)
- Exportar `web/public/data/bulletins.json` desde `scripts/export_web.py` (dos boletines: `logistica_canal`
  con la pregunta CU-05 literal, y `economia`). Mismas comprobaciones de `check_public`.
- Página nueva `/boletin/` con etiqueta de sección **"Extensión bancaria · boletín de entorno"**:
  - Encabezado: usuario ("Analista de estudios económicos o riesgo sectorial"), pregunta, horizonte, modo/modelo.
  - `limits_notice` **visible arriba**, no colapsado.
  - Dos columnas en escritorio (una en móvil): **Observación** (lo que dicen las fuentes, con citas desplegables
    reutilizando el componente de cita existente) | **Hipótesis de impacto** (rotuladas HIPÓTESIS, color distinto,
    con "requiere verificación").
  - Resumen (≤250 palabras), sectores relacionados como chips, 3 preguntas para el analista, eventos usados con
    enlace a su ficha, fuentes, validación y "Basado únicamente en titular/metadatos" si aplica.
  - Botón "Imprimir / guardar PDF" con `window.print()` y hoja de estilos `@media print` (el boletín es un
    entregable que un analista enviaría). Sin dependencias nuevas.
  - Selector entre los dos boletines.
- Navegación: añadir "Boletín (banca)" al final. En la portada, una tarjeta pequeña: *"El mismo núcleo, otro
  usuario: boletín de entorno para un analista bancario (extensión prevista por el reto)."*
- README: una línea en "Probarlo" y en la descripción.

## 6. Pruebas (`tests/test_bulletin.py`, nuevas)
- Plantilla: 3 preguntas exactas, ≤250 palabras, toda cifra presente en evidencia citada, `impact_hypotheses`
  sin tag HECHO, `observations` sin tag HIPOTESIS, `limits_notice` presente, eventos en orden oficial.
- Validador de lenguaje prohibido: oración LLM con "recomendamos comprar" / "riesgo de impago" / "cartera"
  → eliminada + `FORBIDDEN_BANKING_TERM`; resumen vacío → fallback a plantilla.
- LLM simulado (como en las pruebas existentes de Story Studio): cifra inventada → eliminada; inyección en un
  titular → no obedecida; JSON inválido → fallback.
- Dato histórico WB en un boletín → conserva período y advertencia.
- Export: `bulletins.json` existe, 2 boletines, 0 `descripcion`.

## 7. Orden de trabajo (cada etapa, commit + push)
1. Contrato + `bulletin.py` (plantilla) + validador de términos + `service.sector_bulletin` + pruebas.
2. Export + página `/boletin/` + navegación + impresión.
3. Camino LLM con validación y fallback + pruebas con LLM simulado.
4. (Opcional, depende de un humano con GPU) precálculo `qwen3:8b`, revisión y caché.
5. Docs: README, `web/README.md`, worklog, `docs/AI_TOOLS_USED.md`. El Lead registra en el decision log.

## 8. Verificación antes del PR
- `python -m pytest -q` (todas, viejas y nuevas) y `ruff check .` verdes; `cd web && npm ci && npm run lint && npm run build`.
- Leer los dos boletines completos y comprobar a mano: ninguna recomendación, ninguna inferencia de pérdidas
  o cartera, hipótesis claramente separadas, cada cifra con fuente y período, preguntas útiles para un analista.
  Pegar ambos textos en la descripción del PR para que el Lead los revise.
- Wifi apagado: `/boletin/` funciona y se imprime.
- Capturas en `docs/screenshots/web/` (escritorio, móvil y vista de impresión).
