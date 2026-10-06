# ONBOARDING — cómo empezar (Humano 2 / Humano 3 + Codex/Astra)

> Lee esto completo una vez (unos 5 min). Luego pega en Codex el prompt de tu rol (§4 o §5).

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
1. Instala Ollama (https://ollama.com) y descarga los candidatos: `ollama pull qwen3.5:9b`, `ollama pull qwen3:8b` (4060) o `ollama pull qwen3:4b` (3050). Si un tag no existe, anota el que uses.
2. Instala torch con CUDA según https://pytorch.org (elige tu versión de CUDA) y luego `pip install -r requirements-ai.txt`.

## 2. Reglas en 60 segundos (detalle en `AGENTS.md`)
- Trabaja en **tu rama**: `worker-a/<tema>` o `worker-b/<tema>`. Abre un PR hacia `main`; el Lead lo revisa y lo mergea.
- Solo tocas los **archivos permitidos** de tu tarea (`docs/TASKS.md`). Cambiar contratos, config, dependencias o archivos ajenos requiere primero una propuesta en `docs/AGENT_PROPOSALS.md`.
- No edites `docs/TASKS.md` ni el tablero ni el decision log. Escribe tu avance en `docs/worklog/<worker-a|worker-b>.md` (solo agregar, hora UTC).
- Las dependencias de `requirements*.txt` ya están aprobadas. Una nueva requiere propuesta.
- `pytest` en verde antes de cada PR. Sin secretos. Sin métricas inventadas.
- Usaste IA (Codex/Astra) → agrega una fila en `docs/AI_TOOLS_USED.md` (entregable oficial).
- Cada vez que una prueba falle de verdad y la corrijas, anótalo en `docs/notion_mirror/06_TESTS_AND_METRICS.md` → "Registro de pruebas fallidas" (el jurado lo pedirá).

## 3. Ritmo y puntos de sincronización
| Cuándo | Qué |
|---|---|
| Hoy, al terminar el día | PR con lo avanzado (aunque sea parcial y en borrador) |
| Mié 7, 10:00 (Panamá) | Snapshot congelado en `main` (Worker B). **Humano 2 hace su top 5 a ciegas** (H-08) |
| Mié 7, 14:00 | **M1**: `make demo` de punta a punta sin LLM |
| Mié 7, 23:59 | **M2**: IA integrada |
| Jue 8, 14:00 | **M3**: métricas + despliegue + Notion |
| Jue 8, 20:00 | Congelación de código; ensayo offline |

Si te bloqueas más de 30 min: escribe en tu worklog **qué** te bloquea y avisa al Humano 1.

## 4. Prompt para Codex — Worker A (Humano 2: UI)
```
Eres Worker A del proyecto SCAYL (reto TVN Media, hackIAthon). Antes de escribir código lee, en este orden:
AGENTS.md, docs/ARCHITECTURE.md (§3 contratos y §6 interfaces), scayl/contracts.py,
tests/fixtures/ui_bundle.example.json y en docs/TASKS.md las secciones A-01, A-08, A-02, A-03, A-07, A-04, A-09, A-10, A-05, A-06.

Objetivo: la UI Streamlit de 4 pantallas (Sala de Situación, Ficha de Caso, Consultas, Trust Lab) que lee
el fixture mediante app/service_client.py con las mismas firmas que scayl/service.py (ARCHITECTURE §6).
Cuando el Lead publique scayl/service.py, solo se cambia SCAYL_UI_SOURCE=service.

Orden de trabajo (un PR por bloque, rama worker-a/ui-<bloque>):
1) A-01 esqueleto + FixtureService + navegación  2) A-08 tarjeta de evidencia  3) A-02 Sala de Situación
4) A-03 Ficha de Caso (6 pestañas)  5) A-07 Agenda de la mañana  6) A-04 Consultas + A-09 Modo jurado
7) A-10 simulador de pesos (con un stub de rescore mientras L-15 no exista)  8) A-05 Trust Lab  9) A-06 despliegue.

Reglas obligatorias: solo archivos permitidos de cada tarea (app/**, tests/ui/**, deploy/**); no modifiques
scayl/ ni contratos (si algo falta, escribe una propuesta en docs/AGENT_PROPOSALS.md y usa un adaptador local);
horas en America/Panama; insignia SINTÉTICO en ítems sintéticos; el puntaje P nunca se muestra como
probabilidad de verdad y el estado de evidencia es una insignia distinta; "aprobado como borrador" no es publicar;
si una métrica no existe, muestra "no medido". Pruebas con streamlit.testing.v1.AppTest. Ejecuta
python -m pytest -q antes de cada PR. Registra tu avance en docs/worklog/worker-a.md y el uso de IA en
docs/AI_TOOLS_USED.md. En la descripción del PR: tarea cerrada, pruebas, capturas a 1280x720, desviaciones.
```

## 5. Prompt para Codex — Worker B (Humano 3: datos y evaluación)
```
Eres Worker B del proyecto SCAYL (reto TVN Media, hackIAthon). Antes de escribir código lee, en este orden:
AGENTS.md, docs/ARCHITECTURE.md (§3 contratos, §4.1 validación, §5.1 interfaz semántica), scayl/contracts.py,
docs/notion_mirror/03_DATA_CATALOG.md, docs/notion_mirror/02_DECISION_LOG.md (DL-006, DL-008, DL-010) y en
docs/TASKS.md las secciones B-01..B-12 y "Contratos de las tareas 10/10".

Objetivo: el snapshot congelado y reproducible + la inteligencia semántica (temas, agrupación, recuperación)
con baseline frente a IA + la evaluación medida que alimenta el Trust Lab.

Orden de trabajo (un PR por bloque, rama worker-b/<bloque>):
1) B-01 fetchers + snapshot data/raw/v1 según el PDF §6–7 y DL-008 (GDELT DOC con STARTDATETIME/ENDDATETIME
   para 2025-09-01..2025-10-01 partido por día; TVN con domain:tvn-2.com; World Bank 6 países × 6 indicadores ×
   2010–2024 con cuadrícula completa y nulos; USGS 2024 en la caja oficial). Bloque de tiempo de 2 h para el
   intervalo; si no se alcanza, aplica el respaldo de DL-008 y documenta la desviación.
   + B-02 manifest SHA-256 + docs/DATA_DICTIONARY.md. Actualiza 03_DATA_CATALOG.md (solo tus filas).
   APENAS el snapshot esté listo: genera data/labels/editor_candidates.csv (titulares en orden aleatorio, sin
   puntajes) para que el Humano 2 elija su top 5 a ciegas (H-08), ANTES de que exista cualquier ranking.
2) B-10 benchmark de modelos locales en la máquina con GPU (puede correr en paralelo).
3) B-03 validación y normalización (T01) + B-04 casos sintéticos  4) B-11 GitHub Actions
5) B-05 embeddings/temas/agrupación (baseline TF-IDF + IA) + B-07 etiquetas humanas
6) B-06 recuperación  7) B-08 evaluación → eval/results/latest.json  8) B-12 set de 10 ataques.

Reglas obligatorias: solo archivos permitidos (scayl/ingest/**, scayl/intel/**, scayl/eval/**, data/**, tests/
de tus módulos, .github/workflows/**); no modifiques scayl/contracts.py ni scayl/config/ (propuesta en
docs/AGENT_PROPOSALS.md si hace falta). UTF-8, ISO 8601 UTC, nunca convertir nulos en 0, publicación ≠ detección,
unidades originales, data/raw inmutable. Solo titulares + URL + metadatos: nada de cuerpos de artículos.
Los casos alterados se marcan sintéticos. El set "reservado" del benchmark nunca entra al corpus ni a los prompts.
Ninguna métrica inventada: todo sale de una ejecución guardada, con numerador y denominador. Las pruebas que
necesitan modelo llevan @pytest.mark.needs_model. Ejecuta python -m pytest -q antes de cada PR. Registra tu
avance en docs/worklog/worker-b.md y el uso de IA en docs/AI_TOOLS_USED.md.
```

## 6. Tareas humanas (sin Codex)
- **Humano 2 (editor):** H-08 top 5 a ciegas (mié 10:00) → `data/labels/editor_top5.json` con hora; luego, en M3, revisar ≥30 afirmaciones (B-09). No mires el ranking antes de entregar tu top 5.
- **Humano 3:** etiquetar ≥100 titulares por tema y los pares de agrupación (B-07).
- **Todos:** publicaciones en redes con @hackiathon @viamatica @adenbs y #hackIAthon #AgenteIA #retohackIAthon #hackIAthonPanamá (H-03).
