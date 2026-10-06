# 04 · Diseño de solución

> Resumen para el jurado. Documento canónico: `docs/ARCHITECTURE.md`.

**Arquitectura:** snapshot congelado → validación/normalización → temas + agrupación (embeddings locales) → motor de evidencia determinista (Source DNA, vínculo oficial, Temporal Guard, conflictos, puntaje P, estado de evidencia) → LLM local acotado (afirmaciones, paquete editorial, Q&A) + validadores → UI Streamlit (4 pantallas) → revisión humana (SQLite) → Notion.

**Modelo de datos:** `NewsItem`, `IndicatorObservation`, `SeismicEvent` → `Event` (SourceDNA, Claim, Conflict, TemporalWarning, PriorityScore, EvidenceStatus, InvestigationGap) → `StoryPackage` / `QAAnswer` → `ReviewRecord` → `Ficha` (fichas.jsonl). Versión de contrato 0.1.0.

**Reglas:** P = 30R + 25I + 20U + 15N + 10E (`scoring-v1`, ver ARCHITECTURE §4.6); rangos bajo [0,40), medio [40,70), alto [70,100]; desempate U y luego ID.

**Modelos (provisional, DL-006):** embeddings bge-m3 / multilingual-e5-base; LLM qwen3:8b o qwen3:4b vía Ollama; temperatura 0, semilla 42, thinking off, salida JSON con esquema.

**Prompts:** `scayl/gen/prompts/*.vN.md` (pendiente v1).

**Límites del sistema:** no lee artículos completos; no verifica la verdad; no publica; métricas solo sobre etiquetas del equipo (exploratorias); snapshot por lotes.
