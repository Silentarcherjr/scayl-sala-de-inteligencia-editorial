# ONBOARDING — cómo empezar (frictionspp-svg / LowCrime + Codex/Astra)

> Lee esto completo una vez (unos 5 min). Luego pega en tu agente el mensaje de §4.

## 1. Preparar el entorno (una vez)
```bash
git clone https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial.git
cd scayl-sala-de-inteligencia-editorial
python -m venv .venv
# Linux/macOS: source .venv/bin/activate      Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements.txt
make test            # o: python -m pytest -q   → debe decir "3 passed"
cp .env.example .env # nunca subas .env
```
Sin `make` (Windows): `python scripts/make_ui_fixture.py` y `python -m pytest -q`.

### IA local (solo para la máquina con GPU; necesario para B-10 y la demo)
1. Instala Ollama (https://ollama.com) y descarga los candidatos: `ollama pull qwen3.5:9b`, `ollama pull qwen3:8b` (GPU de 8 GB) o `ollama pull qwen3:4b` (3050). Si un tag no existe, anota el que uses.
2. Instala torch con CUDA según https://pytorch.org (elige tu versión de CUDA) y luego `pip install -r requirements-ai.txt`.

## 2. Reglas en 60 segundos (detalle en `AGENTS.md`)
- Trabaja en **tu rama**: `worker-a/<tema>` o `worker-b/<tema>`. Abre un PR hacia `main`; el Lead lo revisa y lo mergea.
- Solo tocas los **archivos permitidos** de tu tarea (`docs/TASKS.md`). Cambiar contratos, config, dependencias o archivos ajenos requiere primero una propuesta en `docs/AGENT_PROPOSALS.md`.
- No edites `docs/TASKS.md` ni el tablero ni el decision log. Escribe tu avance en `docs/worklog/<worker-a|worker-b>.md` (solo agregar, hora UTC).
- Las dependencias de `requirements*.txt` ya están aprobadas. Una nueva requiere propuesta.
- `pytest` en verde antes de cada PR. Sin secretos. Sin métricas inventadas.
- Usaste IA (Codex/Astra) → agrega una fila en `docs/AI_TOOLS_USED.md` (entregable oficial).
- **Relevo:** cuando el agente se acerque al límite de su sesión (~15%) o cuando le escribas **"RELEVO"**, se detiene y deja `docs/handoff/<usuario>.md` para que otro agente continúe (AGENTS.md §2b). Si cambias de agente o de sesión, el nuevo empieza leyendo ese archivo.
- Cada vez que una prueba falle de verdad y la corrijas, anótalo en `docs/notion_mirror/06_TESTS_AND_METRICS.md` → "Registro de pruebas fallidas" (el jurado lo pedirá).

## 3. Ritmo y puntos de sincronización
| Cuándo | Qué |
|---|---|
| Hoy, al terminar el día | PR con lo avanzado (aunque sea parcial y en borrador) |
| Mié 7, 10:00 (Panamá) | Snapshot congelado en `main` (frictionspp-svg). **LowCrime hace su top 5 a ciegas** (H-08) apenas llegue, antes de ver cualquier ranking |
| Mié 7, 14:00 | **M1**: `make demo` de punta a punta sin LLM |
| Mié 7, 23:59 | **M2**: IA integrada |
| Jue 8, 14:00 | **M3**: métricas + despliegue + Notion |
| Jue 8, 20:00 | Congelación de código; ensayo offline |

Si te bloqueas más de 30 min: escribe en tu worklog **qué** te bloquea y avisa al Humano 1 (Silentarcherjr).

## 4. Instrucciones para cada agente
Cada persona le pega a su agente (Codex/Astra) el mensaje corto de abajo; las instrucciones completas están en el repo.

- **frictionspp-svg** → `docs/agents/frictionspp-svg.md` (empieza ya: datos, semántica y primera UI).
- **LowCrime** → `docs/agents/LowCrime.md` (llega más tarde: resto de la UI, evaluación, Trust Lab y despliegue; es el editor independiente).

Mensaje estándar para **cada sesión nueva** del agente (cambia `<usuario>`). Incluye la sincronización con `main`,
así el humano no tiene que ejecutar nada a mano:
```
Estás en el repo SCAYL. Antes de leer cualquier archivo, sincroniza tu rama de trabajo:
  a. git status; si hay cambios sin commit, haz commit en tu rama con prefijo "WIP:".
  b. git fetch origin && git merge origin/main   (merge normal: NO rebase, NO force-push).
  c. Si hay conflictos, detente sin resolverlos a ciegas y muéstrame qué archivos chocan.
  d. git push y confirma: rama, último commit y que el merge fue limpio.
Después, lee y sigue al pie de la letra docs/agents/<usuario>.md (rol, orden de tareas y reglas; AGENTS.md es
obligatorio), empezando por la sección "📌 Notas del Lead pendientes" si existe. Si existe
docs/handoff/<usuario>.md, léelo también y continúa desde ahí. Trabaja en ramas propias y abre PR hacia main;
no mergees tú. Cuando te quede ~15% de sesión, o si escribo RELEVO, detente y deja el relevo según AGENTS.md §2b.
```
Si el agente todavía no tiene rama propia (primera sesión), en el paso b crea la rama desde `main`
(`git switch -c worker-a/<tema>` o `worker-b/<tema>`) en lugar de hacer merge.

## 6. Tareas humanas (sin Codex)
- **LowCrime (editor):** H-08 top 5 a ciegas a partir de `data/labels/editor_candidates.csv` → `data/labels/editor_top5.json` con hora; luego, en M3, revisar ≥30 afirmaciones (B-09). No mires el ranking antes de entregar tu top 5.
- **frictionspp-svg:** etiquetar ≥100 titulares por tema y los pares de agrupación (B-07).
- **Todos:** publicaciones en redes con @hackiathon @viamatica @adenbs y #hackIAthon #AgenteIA #retohackIAthon #hackIAthonPanamá (H-03).
