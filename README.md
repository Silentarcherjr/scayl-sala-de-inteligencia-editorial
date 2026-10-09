# SCAYL — Sala de Inteligencia Editorial

[![CI](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/actions/workflows/ci.yml/badge.svg)](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/actions/workflows/ci.yml)

Prototipo para el reto **TVN Media · "De la señal a la decisión"** (hackIAthon Panamá, modalidad editorial).

Como extensión bancaria, ofrece un **boletín de entorno sectorial** con citas, hipótesis separadas y preguntas para un analista; la modalidad principal sigue siendo editorial (brief TVN Media, CU-05/T09; [DL-035](docs/BANK_BULLETIN_PLAN.md)).

SCAYL convierte un snapshot congelado de señales públicas en **eventos priorizados**. Cada evento trae su
**evidencia trazable**, sus **vacíos de investigación** y un **borrador editorial citado**, listo para la
revisión humana. **La IA no decide qué es verdad ni qué se publica**: "aprobado como borrador" no significa publicado.

![Sala de Situación](docs/screenshots/final/01-sala.png)

## Qué hace

| Etapa | Cómo | Dónde verlo |
|---|---|---|
| Señal → evento | Validación del snapshot y agrupación semántica con E5 multilingüe local (187 señales → 165 eventos) | Sala de Situación |
| Prioridad | `P = 30R + 25I + 20U + 15N + 10E` (`scoring-v1`), con cada componente y su regla visibles | Ficha · Evento, Simulador |
| Evidencia | Estado de evidencia **separado** de la prioridad. **Source DNA** cuenta procedencias, no titulares. Fuentes oficiales: ACP, INEC, USGS y World Bank | Ficha · Fuentes, Evidencia |
| Tiempo | **Temporal Guard**: todo dato lleva su fecha; lo histórico nunca se presenta como actual | Ficha, Consultas |
| Conflictos | Las cifras incompatibles se muestran juntas, sin elegir ni promediar (ej.: titular 4.7 / USGS 4.5) | Ficha · Evidencia |
| Investigación | Qué se sabe, qué se afirma, qué falta y a quién verificar | Ficha · Vacíos |
| Producción | Borrador con LLM local (qwen3:8b). Cada frase etiquetada HECHO/DECLARACIÓN y con `evidence_id`; validadores por código eliminan cifras sin respaldo, presentes falsos e inyecciones | Ficha · Producir |
| Consultas | Respuestas solo con evidencia del corpus, citadas; **abstención explícita** si falta evidencia | Consultas (modo jurado) |
| Revisión | Estados con transiciones guardadas, justificación obligatoria y recibo con hash | Ficha · Revisión |
| Confianza | Resultados con numerador, denominador y alcance de evaluación | Trust Lab |

## Resultados y validación

| Resultado | Evidencia y alcance |
|---|---|
| **442 pruebas automatizadas aprobadas** | Suite Python, lint y compilación web en CI |
| **T01–T10 aprobadas** | Pruebas automatizadas del reto; T10 ejecutado con la red bloqueada |
| **45/45 frases con cita** | Top 15 generado con Qwen3 8B; mide cobertura de citas |
| **25/30 afirmaciones con sustento válido** | Revisión humana de paquetes en modo plantilla |
| **6/6 trampas con abstención correcta** | Set reservado elaborado por un integrante del equipo |
| **13,1 s de latencia mediana** | Generación local de 15 paquetes con Qwen3 8B en AMD RX 9060 XT; p95 17,0 s |

Las evaluaciones conservan sus entradas, resultados y alcance en [pruebas y métricas](docs/notion_mirror/06_TESTS_AND_METRICS.md) y [eval/results/](eval/results/). Cobertura de citas y sustento editorial son mediciones distintas; los resultados de desarrollo se identifican como tales.

## Probarlo

**Demo web principal:** [SCAYL · Sala de Inteligencia Editorial](https://scayl-editorial.vercel.app/).
Next.js estático en Vercel: los mismos 165 eventos, componentes, evidencia y paquetes de SCAYL.
Las consultas guiadas usan resultados precalculados; la consulta libre usa la API Python con evidencia o, por elección del usuario, Gemini externo en modo `online`. Las salidas guardadas no son inferencia en vivo.
`/verificar/` recupera y compara evidencia de forma determinista, sin IA generativa. Compatible no significa verdadero ni listo para publicar.
La revisión de la demo web valida la decisión y guarda recibos en este navegador (DL-036).

**Extensión bancaria:** abre `/boletin/` para leer el boletín de Logística y Canal (CU-05) y usa «Imprimir / guardar PDF». El boletín incluido es una plantilla, sin IA generativa; no evalúa personas ni recomienda operaciones.

**Web local (una vez construido el export, funciona sin internet):**
```bash
cd web
npm ci
npm run build
npx serve out
```
Para regenerar los datos públicos desde el bundle revisado, ejecuta desde la raíz
`python scripts/export_web.py` con el entorno Python del proyecto activo. Los JSON de
`web/public/data/` están versionados; el frontend se exporta estático; las funciones de consultas y revisión usan Python. Gemini necesita configuración secreta en el servidor.
Detalles y evidencia de verificación en `web/README.md` y `docs/screenshots/web/`.

**Demo sin internet (recomendado, sin GPU ni compilación):**
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/demo_offline.py                       # http://localhost:8501
```
Usa el bundle público y las salidas precalculadas de `deploy/artifacts/v1`, sin descripciones RSS.

**Pipeline completo desde el snapshot:**
```bash
python -m scayl.pipeline build --snapshot data/raw/v1            # modo template, sin modelo
pip install -r requirements-ai.txt                                # E5 + cliente Ollama (opcional)
python -m scayl.pipeline build --snapshot data/raw/v1 --llm live  # requiere Ollama con qwen3:8b
python -m pytest -q && ruff check .
```

**Respaldo offline:** la app Streamlit se ejecuta en local con `python scripts/demo_offline.py`.

## Datos (snapshot `data/raw/v1`, manifest con SHA-256)
- **Noticias:** GDELT (metadatos) y RSS de TVN, del 2025-10-02 al 2026-09-30 (aclaración oficial C-01). Solo titulares y metadatos.
- **Indicadores:** World Bank 2010–2024 (contexto histórico); ACP, nivel diario del lago Gatún; INEC, IPC mensual.
- **Sismos:** USGS.

Licencias y procedencia en `docs/notion_mirror/03_DATA_CATALOG.md`.

## Alcance

- Snapshot congelado de titulares y metadatos públicos, con períodos y fuentes trazables.
- La evidencia oficial de contexto se distingue del respaldo directo a una afirmación.
- Source DNA declara la procedencia disponible; varios medios no equivalen automáticamente a confirmaciones independientes.
- Qwen3 8B genera paquetes localmente; la web identifica sus respuestas guardadas. Gemini es externo y opcional, con cuotas y costo sujetos al proyecto de Google.
- La decisión editorial requiere revisión humana. Los detalles de evaluación y control de calidad están en la documentación técnica.

## Documentación

| Documento | Para qué |
|---|---|
| [Recorrido guiado](https://scayl-editorial.vercel.app/recorrido/) | Punto de entrada para evaluar la aplicación |
| [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) | Guion del recorrido y demo local |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitectura y contratos |
| [Documentación de entrega](docs/notion/) | Páginas de Notion entregadas (aclaración oficial [C-04](docs/official_clarifications.md)): documentación técnica, documentación funcional y presentación del Pitch Day, importables como Markdown |
| [Registro de ejecución y evaluación](docs/notion_mirror/) | Registro de trabajo durante el evento: decisiones (02), métricas y fallos corregidos (06), pitch (08) |
| [docs/PLAN_REVIEW.md](docs/PLAN_REVIEW.md) | Revisión del reto, matriz de rúbrica y riesgos |
| [docs/AI_TOOLS_USED.md](docs/AI_TOOLS_USED.md) | Bitácora de herramientas de IA usadas en el desarrollo |
| `AGENTS.md`, `CLAUDE.md`, `docs/TASKS.md` | Cómo trabajó el equipo humano + agentes |

Equipo SCAYL: Silentarcherjr, frictionspp-svg y LowCrime, con agentes de código (Claude Code y Codex) bajo revisión humana.
