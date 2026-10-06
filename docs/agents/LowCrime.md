# Instrucciones para el agente de LowCrime (Codex/Astra)

Eres el agente de código de **LowCrime** en el proyecto SCAYL (reto TVN Media "De la señal a la decisión",
hackIAthon Panamá). El Lead es Claude (otro agente) junto con el Humano 1; él revisa y mergea tus PR.
Tu dueño humano está contigo: pídele confirmación antes de cualquier acción irreversible o que use credenciales.

## Tu rol
Llegas cuando el proyecto ya avanzó: **completas la interfaz, la evaluación medida (Trust Lab) y el despliegue**.
Tu humano además es el **"editor" independiente**: su juicio sirve para medir el sistema, así que no debe ver
el ranking antes de entregar su top 5.

## ⚠️ Relevo de sesión (lee esto primero)
- **Al empezar:** si existe `docs/handoff/LowCrime.md`, léelo antes que cualquier otra cosa y continúa desde su "Siguiente paso concreto".
- **Al acercarte al límite (~15% restante)**, o si tu humano escribe **"RELEVO"**: detente, haz commit (`WIP:` si está a medias), escribe `docs/handoff/LowCrime.md` con la plantilla `docs/handoff/TEMPLATE.md`, haz push y avísale a tu humano. Si no puedes ver tu límite, díselo a tu humano al empezar y haz un relevo preventivo al terminar cada tarea. Detalle en `AGENTS.md` §2b.

## Primero: ponte al día (unos 10 min)
1. `git pull`; lee `AGENTS.md`, `docs/MASTER_PLAN.md` y `docs/worklog/*.md` (qué hicieron los demás).
2. `docs/ARCHITECTURE.md` §3, §5.2 (validadores) y §6 (interfaces); `scayl/contracts.py`; `tests/fixtures/ui_bundle.example.json`.
3. En `docs/TASKS.md`: la tabla (tus filas dicen **W**) y las secciones A-03..A-07, A-09, A-10, B-08, B-12, más "Contratos de las tareas 10/10".
4. `docs/AGENT_PROPOSALS.md`: revisa si hay algo abierto que te afecte.

## Antes de tocar código: tarea humana H-08 (bloqueante para P@5)
Si `data/labels/editor_candidates.csv` existe y `data/labels/editor_top5.json` todavía no: **pide a tu humano
que elija su top 5 leyendo solo ese CSV**, sin abrir la app con datos reales ni ningún ranking. Guarda
`{"editor": "LowCrime", "picked_at_utc": "...", "ids": [...], "criterio": "..."}` y súbelo en un PR propio.

## Orden de trabajo (un PR por bloque; rama `worker-a/<bloque>` para UI, `worker-b/<bloque>` para eval)
1. **A-03 · Ficha de Caso (6 pestañas)**; los titulares de cada evento están en `bundle.news` (contrato 0.2.0), filtrando por `event.member_ids`; muestra `event.security_flags` como aviso "fuente con instrucciones sospechosas, tratada como dato"; en `app/pages/1_Ficha_de_Caso.py` (reutiliza la tarjeta de evidencia de `app/components/` hecha por frictionspp-svg; no la reescribas: si le falta algo, propón el cambio en su PR o en AGENT_PROPOSALS).
2. **A-07 · Agenda de la mañana** (bloque superior de la Sala de Situación; coordina con frictionspp-svg porque `app/Home.py` es suyo: crea el componente en `app/components/agenda.py` y pídele que lo monte, o acuérdenlo en el PR).
3. **A-04 + A-09 · Consultas + Modo jurado** en `app/pages/2_Consultas.py`.
4. **A-10 · Simulador de pesos** (usa un stub de `rescore` hasta que el Lead publique L-15).
5. **B-08 · Evaluación** (fuentes ya disponibles del Lead: `data/processed/<snap>/generation_report.jsonl` para la cobertura de citas, las eliminaciones por código, la preservación de atribución, la latencia y los tokens; `scayl.service.ask()` para el benchmark de consultas y la abstención; `pytest` para T01–T10) (`scayl/eval/**`, salida `eval/results/latest.json` con el esquema de TASKS B-08) + **A-05 · Trust Lab** en `app/pages/3_Trust_Lab.py`.
6. **B-12 · Set de 10 ataques** (`data/labels/redteam.jsonl`, marcados como sintéticos) y su métrica de resistencia.
7. **A-06 · Despliegue** (construye el bundle con `make public-bundle`, que reutiliza la caché y quita las descripciones del RSS; incluye `data/cache/llm/` en el Space) en un Hugging Face Space con contraseña, modo caché, solo titular + URL (AP-001; carpeta `deploy/**`).

## Reglas clave (el detalle está en AGENTS.md)
- Solo tocas tus archivos permitidos. Para cambiar contratos, `scayl/config/`, dependencias o archivos de otros: primero propuesta en `docs/AGENT_PROPOSALS.md`.
- UI: horas en America/Panama; insignia `SINTÉTICO`; el puntaje P nunca se muestra como probabilidad de verdad; el estado de evidencia es una insignia distinta; "aprobado como borrador" no es publicar; métrica ausente = "no medido".
- Evaluación: solo resultados de ejecuciones guardadas, con numerador, denominador y fallos visibles; P@5 se declara exploratoria; el set reservado nunca entra al corpus ni a los prompts.
- `python -m pytest -q` en verde antes de cada PR (UI: `streamlit.testing.v1.AppTest`).
- No edites `docs/TASKS.md`, el tablero ni el decision log. Escribe tu avance en `docs/worklog/worker-a.md` (hora UTC; solo agregar).
- Agrega una fila en `docs/AI_TOOLS_USED.md` por cada uso relevante de IA (entregable oficial).
- Si una prueba falla de verdad y la corriges, anótalo en `docs/notion_mirror/06_TESTS_AND_METRICS.md` → "Registro de pruebas fallidas".
