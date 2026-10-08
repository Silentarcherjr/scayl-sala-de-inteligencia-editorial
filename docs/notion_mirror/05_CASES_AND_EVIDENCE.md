# 05 · Casos y evidencias (fichas)

> Requisito oficial: ≥5 fichas trazables con IDs, fuentes, puntaje desglosado, estado de evidencia, borrador y persona revisora; **≥1 con evidencia insuficiente**.
> Fichas **reales** del bundle público (`deploy/artifacts/v1/bundle.public.json`, snapshot v1.1). Cada una se abre en `https://scayl-editorial.vercel.app/caso/<ID>/`.
> La revisión humana se registra en la demo (Ficha → Revisión) con justificación obligatoria y recibo con hash; el snapshot público parte en estado `nuevo`.

| id_caso | Título | P (R/I/U/N/E) | Rango | Estado de evidencia | Fuentes | Evidencia oficial | Borrador | Revisión |
|---|---|---|---|---|---|---|---|---|
| EVT-0101 | Canal de Panamá aumentará a 33 los cupos diarios de tránsito y fija calado Neopanamax en 14,94 metros | 89,9 (0,96/0,9/0,8825/1,0/0,6) | alto | parcial: evidencia oficial de contexto, no respalda la afirmación central | 1 publicación, máx. 1 procedencia, 0 confirmadas | ind:acp:ACP.GATUN.NIVEL:2026-09-29; wb:PAN:NE.EXP.GNFS.ZS:2024 (histórico) | PKG-0101-studio-v1 · cache · qwen3:8b | nuevo |
| EVT-0116 | Canal de Panamá mantiene tránsitos y aplica ajustes de calado por El Niño | 72,3 (0,96/0,9/0,0/1,0/0,6) | alto | parcial | 1 publicación, máx. 1, 0 confirmadas | ind:acp:ACP.GATUN.NIVEL:2026-07-16; wb:PAN:NE.EXP.GNFS.ZS:2024 | PKG-0116-studio-v1 · cache · qwen3:8b | nuevo |
| EVT-0114 | Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica; no se reportan daños | 67,5 (0,8/0,9/0,0/1,0/0,6) | medio | parcial: 2 conflictos sin resolver (4.7 frente a USGS 4.5; 4.7 frente a 7.4) | 2 publicaciones, máx. 1, 0 confirmadas | usgs:us7000t0xy | PKG-0114-studio-v1 · cache · qwen3:8b | nuevo |
| EVT-0088 | Sismo de magnitud 3.6 sacude Panamá: epicentro al norte de Tocumen | 57,5 (0,8/0,7/0,0005/1,0/0,1) | medio | **insuficiente**: fuente única, sin evidencia oficial | 1 publicación, máx. 1, 0 confirmadas | ninguna | PKG-0088-template-v1 · plantilla | nuevo |
| EVT-0147 | Onda tropical trae fuertes lluvias y tormentas a Panamá | 59,9 (0,88/0,7/0,0/1,0/0,1) | medio | **insuficiente**: fuente única, sin evidencia oficial | 1 publicación, máx. 1, 0 confirmadas | ninguna | PKG-0147-template-v1 · plantilla | nuevo |

Distribución en el snapshot: 125 eventos insuficientes y 40 parciales. Ningún evento real llega a "suficiente para borrador" porque ningún titular cita una cifra oficial comparable; es abstención correcta, no un error. Los casos sintéticos etiquetados (B-04, `[SINTÉTICO]`) muestran cómo se ve un caso "suficiente".
