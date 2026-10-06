# 01 · Plan y ejecución (tablero)

> Mantenido por el Lead. Fuente detallada: `docs/TASKS.md`. Horas en UTC.
> Requisito oficial: ≥8 tareas, con responsables, estados y cronología, registradas **durante** la ejecución.

| ID | Tarea | Responsable | Estado | Inicio (UTC) | Actualizado (UTC) | Commit/PR | Resultado |
|---|---|---|---|---|---|---|---|
| L-01 | Contratos de datos + fixture de UI | Lead (H1+Claude) | DONE | 2026-10-06 19:45 | 2026-10-06 20:30 | rama claude/fervent-babbage-q9fg7h | `scayl/contracts.py`, fixture sintético, 3 pruebas en verde |
| L-02 | Docs de gobernanza + espejo Notion | Lead | DONE | 2026-10-06 19:40 | 2026-10-06 20:45 | rama claude/fervent-babbage-q9fg7h | PLAN_REVIEW, ARCHITECTURE, MASTER_PLAN, TASKS, AGENTS, CLAUDE, espejo |
| H-01 | Preparar el espacio Notion para migrar | H1 | TODO | — | — | — | — |
| B-01 | Snapshot propio `data/raw/v1` según el PDF (DL-008) | Worker B (H3) | TODO | — | — | — | — |
| B-10 | Benchmark de modelos locales | Worker B (H3) | TODO | — | — | — | — |
| A-01 | Esqueleto Streamlit + FixtureService | Worker A (H2) | TODO | — | — | — | — |
| L-03 | Puntaje P + estado de evidencia | Lead | TODO | — | — | — | — |
| L-09 | Validadores + fallback template | Lead | TODO | — | — | — | — |
| H-02 | Bitácora de herramientas IA → PDF | Todos | DOING | 2026-10-06 19:40 | 2026-10-06 20:45 | — | Bitácora iniciada |
| H-04 | Migrar a Notion | H1 + Lead | BLOCKED | — | — | — | Sin acceso a Notion todavía |

## Cronología
- **2026-10-06 19:40 UTC** — Lectura de las especificaciones oficiales; inspección del repo (vacío); prueba de acceso a las fuentes (bloqueadas en el entorno cloud).
- **2026-10-06 20:45 UTC** — Revisión crítica del plan, contratos y tareas de los workers publicados (M0 parcial).
- **2026-10-06 21:40 UTC** — El equipo aprueba DL-008 (snapshot propio), DL-009 (ideas 10/10) y AP-001. Investigación de mercado y modelos (PLAN_REVIEW §10). PR #1 abierto para mergear M0.
