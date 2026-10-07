# AGENTS.md — reglas para todos los agentes de código (Claude, Codex, Astra…)

Proyecto: **SCAYL — Sala de Inteligencia Editorial** · Reto TVN Media "De la señal a la decisión".
Antes de tocar código lee: `docs/ARCHITECTURE.md` (canónico), tu tarea en `docs/TASKS.md` y
`docs/PLAN_REVIEW.md` §2 (requisitos oficiales que el brief no traía).

## 1. Alcance de tus cambios
- **Cambio local** (dentro de los "archivos permitidos" de tu tarea, sin cambiar contratos): hazlo.
- **Cambio transversal** (contratos en `scayl/contracts.py`, `scayl/config/`, interfaces de §6 de
  ARCHITECTURE, nuevas dependencias, alcance, seguridad, evaluación, archivos de otro dueño):
  **primero** escribe una propuesta en `docs/AGENT_PROPOSALS.md` (plantilla incluida) y espera la decisión.
  Mientras tanto, trabaja con un adaptador local.
- No cambies silenciosamente la arquitectura. No borres pruebas ajenas. No desactives ni saltes pruebas para obtener verde.

## 2. Git
- Rama por worker: `worker-a/<tema>`, `worker-b/<tema>`. El Lead usa `claude/<tema>`. PR hacia `main`; mergea el Lead.
- Commits pequeños con mensaje en imperativo: `ingest: validate dates and keep nulls (T01)`.
- Antes de abrir un PR: `python -m pytest -q` en verde; sin secretos; describe qué tarea cierra, qué pruebas añadiste y cualquier desviación.
- No edites `docs/TASKS.md`, `01_EXECUTION_BOARD.md` ni `02_DECISION_LOG.md`: los actualiza el Lead.
  Registra tu avance en `docs/worklog/<tu-worker>.md` (solo agregar, con hora UTC).

## 2b. Protocolo de relevo (obligatorio)
Las sesiones de los agentes tienen límite. Para que otro agente pueda continuar sin perder trabajo:

1. **Cuándo detenerse:**
   - **Automático:** cuando te quede **~15% o menos** de la sesión (contexto, tokens o tiempo, lo que primero se agote). No empieces otra subtarea: pasa directamente al relevo.
   - **A pedido del usuario:** si tu humano escribe **"RELEVO"** (o "para y haz el resumen"), detente en ese momento, aunque estés a mitad de algo.
   - **Si no puedes ver tus límites:** no intentes adivinarlos. Avísale una vez a tu humano al empezar ("no veo mi límite de sesión; escribe RELEVO cuando quieras que me detenga") y además haz un relevo preventivo **cada vez que cierres una tarea** del orden de trabajo.
2. **Qué hacer al detenerte** (en este orden; reserva el margen para esto):
   1. Deja el código en un estado coherente. Si hay cambios a medias, haz commit de todas formas con el prefijo `WIP:` en tu rama (nunca en `main`). Las pruebas pueden fallar en un WIP, pero indícalo.
   2. Escribe `docs/handoff/<tu-usuario>.md` usando `docs/handoff/TEMPLATE.md`. Sobrescribe el anterior; el historial queda en git.
   3. Agrega una línea en tu `docs/worklog/` ("relevo: ver docs/handoff/<usuario>.md").
   4. `git push` de tu rama.
   5. Dile a tu humano en una línea: rama, último commit y siguiente paso.
3. **Al empezar una sesión nueva:** primero **sincroniza tu rama con `main`** (`git fetch origin && git merge origin/main`, sin rebase ni force-push; ante conflictos, detente y avisa a tu humano), porque las notas del Lead y las decisiones nuevas llegan por `main`. Luego, si existe `docs/handoff/<tu-usuario>.md` (en tu rama o en `main`), léelo **primero** y continúa desde "Siguiente paso concreto". Comprueba con `git log` y `pytest` que el estado coincide con lo que dice el relevo.

## 3. Datos
- UTF-8, IDs estables, ISO 8601 en **UTC** en datos; la UI muestra **hora de Panamá**.
- **Nunca** reemplaces un nulo por 0 o por "". Conserva las unidades originales.
- `fecha_publicacion` ≠ `fecha_deteccion` (seendate de GDELT).
- `data/raw/` es inmutable y está cubierto por `manifest.json` (SHA-256). Transforma hacia `data/processed/` y registra la transformación.
- Casos alterados = **sintéticos**: `origen=sintetico`, título con prefijo `[SINTÉTICO]` y archivo en `data/synthetic/`.
- No guardes cuerpos de artículos, imágenes ni contenido protegido. Datos personales: mínimos.
- El set reservado del jurado (si existe) **jamás** entra al corpus ni a los prompts.

## 4. IA
- 100% local: Ollama + modelos abiertos. **Prohibido** añadir APIs pagas sin aprobación humana.
- El LLM no calcula: puntajes, fechas, conteos y comparaciones numéricas son código.
- El texto de las fuentes va como **dato** delimitado; nunca se concatena a instrucciones.
- Toda salida LLM: JSON con esquema → validación Pydantic → validadores de `scayl/gen/validators.py`.
- Prompts versionados en `scayl/gen/prompts/<nombre>.vN.md`; nunca edites una versión publicada, crea `vN+1`.
- Toda métrica viene de una ejecución guardada. **No inventes números.** Si no se midió: "no medido".

## 5. Producto (no negociable)
- Puntaje P = 30R + 25I + 20U + 15N + 10E es de **atención**, no de verdad ni de impacto. Muestra los componentes.
- Estado de evidencia (insuficiente / parcial / suficiente para el borrador) es independiente de P.
- Prioridad alta **no** habilita publicación. "Aprobado como borrador" **no** es publicar.
- N publicaciones ≠ N confirmaciones. Sin evidencia de independencia: "La procedencia independiente no puede determinarse con la evidencia disponible."
- No inventar entrevistas, citas textuales, imágenes, cifras, causalidad ni condiciones actuales.
- Nada de clasificación de verdad/fake, perfiles de personas ni acusaciones no atribuidas.

## 6. Calidad
- Python ≥3.11, tipado, funciones puras cuando sea posible, sin estado global oculto.
- Dependencias **fijadas** (`==`) en `requirements.txt` (núcleo) o `requirements-ai.txt` (ML). Una dependencia nueva requiere propuesta.
- Pruebas con pytest; las que requieren modelo llevan `@pytest.mark.needs_model`.
- Secretos solo en `.env` (ignorado). Nunca en código, logs, prompts ni capturas.

## 7. Documentación
- Cada PR que cambie comportamiento actualiza la doc relevante (README, catálogo de datos, pruebas y métricas).
- Registra en `docs/AI_TOOLS_USED.md` qué herramienta IA usaste, para qué y con qué resultado (requisito oficial de entrega).
