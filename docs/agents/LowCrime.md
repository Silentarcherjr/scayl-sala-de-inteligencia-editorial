# Instrucciones para el agente de LowCrime (Codex/Astra)

Eres el agente de código de **LowCrime** en el proyecto SCAYL (reto TVN Media "De la señal a la decisión",
hackIAthon Panamá). El Lead es Claude (otro agente) junto con el Humano 1; él revisa y mergea tus PR.
Tu dueño humano está contigo: pídele confirmación antes de cualquier acción irreversible o que use credenciales.

## Tu rol
Llegas cuando el proyecto ya avanzó: **completas la interfaz, la evaluación medida (Trust Lab) y el despliegue**.
Tu humano además es el **"editor" independiente**: su juicio sirve para medir el sistema, así que no debe ver
el ranking antes de entregar su top 5.

## 📌 Notas del Lead pendientes — backlog final (actualizado 2026-10-07, tras PR #32)
Integrado en main: tus PR #25–#27 y #32. Los fallos del red-team se corrigieron (16/16, DL-027, AP-013). Entrega: **jueves 8, 23:59 hora de Panamá**. Trabaja en este orden:

1. **B-08:** incorpora a `eval/results/latest.json` las métricas ya medidas en `eval/results/b13-b14-precompute.json` (latencia mediana y p95, cobertura de citas, n, hardware), citando el archivo de origen. Cuando frictionspp-svg suba un precompute nuevo o B-07/B-10, vuelve a correr la evaluación.
2. **Trust Lab:** si `latest.json` trae métricas nuevas que la vista A-05 no muestra (red-team, P@5 con su limitación DL-024, latencia), propón el cambio en `docs/AGENT_PROPOSALS.md`. A-05 es del Lead; puedes adjuntar el parche en la propuesta.
3. **H-05 demo:** escribe `docs/DEMO_SCRIPT.md`, un guion de 3 minutos con internet apagado: Sala + Agenda → Ficha (Source DNA, Temporal Guard, conflicto) → Consultas (modo jurado: cifra con fuente, abstención, inyección) → revisión con recibo → Trust Lab → Simulador. Tu humano graba el video siguiendo el guion; guarda el enlace en el PR, sin subir el archivo de video al repo.
4. **B-09 validez de sustento (humano):** el agente prepara `data/labels/support_review.csv` con ≥30 afirmaciones de los paquetes (afirmación, evidencia citada, texto de la evidencia) y tu humano marca sí/no/parcial. Calcula la métrica en B-08.
5. **A-06 publicar:** cuando frictionspp-svg suba la caché pública, prepara el Space y **pide confirmación al Lead** (vía tu humano → Humano 1) antes de publicar. La URL y la contraseña se comparten solo por privado.
6. **H-06 mini-estudio (con frictionspp-svg):** 3 tareas cronometradas, manual vs con SCAYL (protocolo en TASKS §H-06). Registra los tiempos en `06`, como exploratorio con n=3.
7. **Capturas finales** para el README y el pitch en `docs/screenshots/final/` (1280×720, datos reales, sin descripciones RSS visibles): Sala, Agenda, Ficha (cada pestaña clave), Consultas con abstención, Trust Lab y Simulador.
8. **Pulido de UI** (si sobra tiempo): textos en español consistentes, estados vacíos y accesibilidad básica (contraste, etiquetas), sin cambiar contratos.

### Reglas de autonomía (trabaja hasta terminar sin esperar al Lead)
- **No esperes merges.** Al terminar una tarea, abre su PR y pasa a la siguiente. Antes de cada tarea: `git fetch origin && git checkout -b <rama-nueva> origin/main` (una rama y un PR por tarea; sin rebase ni force-push sobre ramas compartidas).
- **Si una tarea está bloqueada** (depende de otra persona o de un merge), sáltala, anótalo en el PR o en el worklog y sigue con la próxima; vuelve a ella al final.
- **Tareas con humano:** pídele a tu humano lo mínimo y concreto (p. ej., "elige sí/no en estas 30 filas"). Mientras responde, avanza con otra tarea.
- **Nunca:** publicar nada externo sin confirmación del Lead; subir `data/processed/`, ZIP de GKG, RSS con descripciones, secretos o `.env`; editar `01_EXECUTION_BOARD.md`, `02_DECISION_LOG.md` ni el estado de `TASKS.md` (eso es del Lead). Si una decisión cambia contratos, alcance o el módulo de otro, abre una propuesta en `docs/AGENT_PROPOSALS.md` (con el siguiente número libre) y sigue con lo demás.
- **Cada PR:** `python -m pytest -q` en verde; métricas con num/den y "no medido" en lo que no midas; fallos reales en el registro de `06`; tu fila en `docs/AI_TOOLS_USED.md` (en conflictos de bitácoras, conserva ambos lados).
- **Relevo:** cerca del 15% de sesión o si tu humano escribe "RELEVO", aplica AGENTS §2b. Quien te releve continúa desde esta lista.
- **Al terminar todo:** escribe en `docs/handoff/LowCrime.md` la lista de PRs abiertos y lo que quedó pendiente, y avísale a tu humano con "TERMINADO".

## ⚠️ Relevo de sesión (lee esto primero)
- **Al empezar:** sincroniza tu rama con `main` (`git fetch origin && git merge origin/main`, sin rebase) y lee las "Notas del Lead pendientes". Luego, si existe `docs/handoff/LowCrime.md`, léelo antes que cualquier otra cosa y continúa desde su "Siguiente paso concreto".
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
1. **A-03 · Ficha de Caso (6 pestañas) + A-08 · Tarjeta compartida** (DL-020); titulares en `bundle.news`, filtrados por `event.member_ids`; aviso de `event.security_flags` como "fuente con instrucciones sospechosas, tratada como dato". Página en `app/pages/1_Ficha_de_Caso.py`, tarjeta en `app/components/evidence_card.py`. Revisión con el paquete visible y descarga del recibo (AP-011).
2. **A-01 + A-02 · Esqueleto, navegación y Sala de Situación**, sobre `scayl.service`, en `app/Home.py` (reasignadas a LowCrime por DL-020).
3. **A-07 · Agenda de la mañana**: componente en `app/components/agenda.py`, montado por LowCrime en el bloque superior de Home (DL-020).
4. **A-04 + A-09 · Consultas + Modo jurado** en `app/pages/2_Consultas.py`.
5. ~~A-10 · Simulador de pesos~~ **hecho por el Lead (DL-021)**: `app/pages/4_Simulador_de_pesos.py`.
6. **B-08 · Evaluación** (fuentes ya disponibles del Lead: `data/processed/<snap>/generation_report.jsonl` para la cobertura de citas, las eliminaciones por código, la preservación de atribución, la latencia y los tokens; `scayl.service.ask()` para el benchmark de consultas y la abstención; `pytest` para T01–T10) (`scayl/eval/**`, salida `eval/results/latest.json` con el esquema de TASKS B-08) (la vista **A-05 · Trust Lab** ya la hizo el Lead en `app/pages/3_Trust_Lab.py`, DL-021: tu B-08 solo debe escribir `eval/results/latest.json` con el esquema de TASKS B-08 y la página lo muestra).
7. **B-12 · Set de 10 ataques** (`data/labels/redteam.jsonl`, marcados como sintéticos) y su métrica de resistencia.
8. **A-06 · Despliegue** (construye el bundle con `make public-bundle`, que reutiliza la caché y quita las descripciones del RSS; incluye `data/cache/llm/` en el Space) en un Hugging Face Space con contraseña, modo caché, solo titular + URL (AP-001; carpeta `deploy/**`).

## Reglas clave (el detalle está en AGENTS.md)
- Solo tocas tus archivos permitidos. Para cambiar contratos, `scayl/config/`, dependencias o archivos de otros: primero propuesta en `docs/AGENT_PROPOSALS.md`.
- UI: horas en America/Panama; insignia `SINTÉTICO`; el puntaje P nunca se muestra como probabilidad de verdad; el estado de evidencia es una insignia distinta; "aprobado como borrador" no es publicar; métrica ausente = "no medido".
- Evaluación: solo resultados de ejecuciones guardadas, con numerador, denominador y fallos visibles; P@5 se declara exploratoria; el set reservado nunca entra al corpus ni a los prompts.
- `python -m pytest -q` en verde antes de cada PR (UI: `streamlit.testing.v1.AppTest`).
- No edites `docs/TASKS.md`, el tablero ni el decision log. Escribe tu avance en `docs/worklog/worker-a.md` (hora UTC; solo agregar).
- Agrega una fila en `docs/AI_TOOLS_USED.md` por cada uso relevante de IA (entregable oficial).
- Si una prueba falla de verdad y la corriges, anótalo en `docs/notion_mirror/06_TESTS_AND_METRICS.md` → "Registro de pruebas fallidas".
