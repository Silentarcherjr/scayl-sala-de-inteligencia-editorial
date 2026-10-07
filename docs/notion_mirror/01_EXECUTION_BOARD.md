# 01 · Plan y ejecución (tablero)

> Mantenido por el Lead. Fuente detallada: `docs/TASKS.md`. Horas en UTC.
> Requisito oficial: ≥8 tareas, con responsables, estados y cronología, registradas **durante** la ejecución.

| ID | Tarea | Responsable | Estado | Inicio (UTC) | Actualizado (UTC) | Commit/PR | Resultado |
|---|---|---|---|---|---|---|---|
| L-01 | Contratos de datos + fixture de UI | Lead (H1+Claude) | DONE | 2026-10-06 19:45 | 2026-10-06 20:30 | rama claude/fervent-babbage-q9fg7h | `scayl/contracts.py`, fixture sintético, 3 pruebas en verde |
| L-02 | Docs de gobernanza + espejo Notion + onboarding | Lead | DONE | 2026-10-06 19:40 | 2026-10-06 22:00 | rama claude/fervent-babbage-q9fg7h | PLAN_REVIEW, ARCHITECTURE, MASTER_PLAN, TASKS, AGENTS, CLAUDE, espejo |
| H-01 | Preparar el espacio Notion para migrar | H1 | TODO | — | — | — | — |
| B-01 | Snapshot propio `data/raw/v1` según el PDF (DL-008) | Worker B (H3) | TODO | — | — | — | — |
| B-10 | Benchmark de modelos locales | Worker B (H3) | TODO | — | — | — | — |
| A-01 | Esqueleto Streamlit + FixtureService | Worker A (H2) | TODO | — | — | — | — |
| L-03 | Puntaje P + estado de evidencia | Lead | DONE | 2026-10-06 22:35 | 2026-10-06 23:30 | rama claude/fervent-babbage-q9fg7h | scoring-v1, rangos, desempate, simulador; 11 pruebas T08 |
| L-09 | Validadores + fallback template | Lead | DONE | 2026-10-06 22:40 | 2026-10-06 23:30 | rama claude/fervent-babbage-q9fg7h | 7 validadores; 1 fallo real corregido (cifras de fechas) |
| H-02 | Bitácora de herramientas IA → PDF | Todos | DOING | 2026-10-06 19:40 | 2026-10-06 20:45 | — | Bitácora iniciada |
| H-04 | Migrar a Notion | H1 + Lead | BLOCKED | — | — | — | Sin acceso a Notion todavía |

## Cronología
- **2026-10-06 19:40 UTC** — Lectura de las especificaciones oficiales; inspección del repo (vacío); prueba de acceso a las fuentes (bloqueadas en el entorno cloud).
- **2026-10-06 20:45 UTC** — Revisión crítica del plan, contratos y tareas de los workers publicados (M0 parcial).
- **2026-10-06 21:40 UTC** — El equipo aprueba DL-008 (snapshot propio), DL-009 (ideas 10/10) y AP-001. Investigación de mercado y modelos (PLAN_REVIEW §10). PR #1 abierto para mergear M0.
- **2026-10-06 22:00 UTC** — AP-007 (Claude en la nube) diferida: primero se mide el modelo local. Dependencias fijadas y verificadas en un venv limpio. `docs/ONBOARDING.md` con prompts para Worker A/B. M0 listo para mergear.
- **2026-10-06 22:20 UTC** — PR #1 mergeado (M0). Reparto por persona (DL-011): frictionspp-svg (camino crítico) y LowCrime (UI restante, evaluación, despliegue, editor). Instrucciones en `docs/agents/`.
- **2026-10-06 23:30 UTC** — Núcleo M1 del Lead: puntaje scoring-v1 + simulador, estado de evidencia, Source DNA, vínculo WB/USGS + Temporal Guard, conflictos numéricos, ensamblado de eventos, validadores claim-first, paquete plantilla, registro de revisiones con recibo, `service.py` y `pipeline.py`. 46 pruebas en verde; 2 fallos reales registrados con su corrección. Esperando B-03/B-05 para correr con datos reales.
- **2026-10-07 00:30 UTC** — M2 del Lead: cliente Ollama con caché, defensa contra inyección, prompts v1, Story Studio con LLM, extracción de afirmaciones, consultas con abstención y reporte de generación. 63 pruebas (T06, T07 y T09 con LLM simulado). 2 fallos reales más registrados con su corrección. Pendiente: probar en la RTX 4060 con datos reales.
- **2026-10-07 01:00 UTC** — Protocolo de relevo entre sesiones de agentes (≈15% de sesión o "RELEVO" del usuario) → `docs/handoff/`.
- **2026-10-07 01:30 UTC** — Revisión de `worker-b/snapshot` (frictionspp-svg): fetchers + manifest + 13 pruebas (76/76 en verde). Decisiones DL-013 (WB 540 filas), DL-014 (RSS TVN histórico) y DL-015 (urgencia GDELT). GPU real: AMD RX 9060 XT 8 GB (Vulkan). B-01 sigue abierta: falta `noticias.csv`, `fuentes.json` y el manifest congelado.
- **2026-10-07 02:30 UTC** — **Aclaración oficial C-01**: noticias en [2025-10-02, 2026-10-01). DL-017 supera DL-008/DL-014; AP-004 aceptada (USGS ampliado). Ventana centralizada en `scayl/config/data_window.v1.yaml`. frictionspp-svg debe volver a descargar las noticias (notas en su archivo de agente).
- **2026-10-07 03:00 UTC** — **Aclaración oficial C-02**: fuentes adicionales permitidas; otras fechas solo para desarrollo; demo con datos recientes. DL-018 (2025 = conjunto de desarrollo). AP-010 (ACP + INEC) pendiente de aprobación del equipo.
- **2026-10-07 03:30 UTC** — AP-010 aceptada por el equipo (DL-019): contrato 0.3.0, `scayl/evidence/recent.py` (ACP + INEC: confirmación por cifra y fecha, contexto con período), consultas incluidas. 71 pruebas. Descarga asignada a frictionspp-svg (B-13/B-14).
