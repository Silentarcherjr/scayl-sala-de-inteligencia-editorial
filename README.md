# SCAYL — Sala de Inteligencia Editorial

Prototipo para el reto **TVN Media · "De la señal a la decisión"** (hackIAthon Panamá).
Convierte un snapshot congelado de señales públicas (TVN RSS, GDELT, World Bank, USGS) en eventos
priorizados, con evidencia trazable, vacíos de investigación y un borrador editorial citado, listo
para **revisión humana**. SCAYL no decide qué es verdad ni qué se publica.

> **Estado: M0 (contratos y plan).** El pipeline y la UI todavía no existen; ver `docs/MASTER_PLAN.md`.

## Mapa de la documentación
| Documento | Para qué |
|---|---|
| `docs/PLAN_REVIEW.md` | Revisión crítica, discrepancias con el reto, matriz de rúbrica, CUT LIST, riesgos |
| `docs/MASTER_PLAN.md` | Hitos, prioridades, guion de demo |
| `docs/ARCHITECTURE.md` | Arquitectura y contratos canónicos |
| `docs/TASKS.md` | Tareas asignables con su definición de terminado |
| `docs/AGENT_PROPOSALS.md` | Propuestas transversales |
| `AGENTS.md` / `CLAUDE.md` | Reglas para agentes de código / Lead |
| `docs/notion_mirror/` | Espejo temporal de las páginas obligatorias de Notion |
| `docs/AI_TOOLS_USED.md` | Bitácora de herramientas IA (entregable PDF) |

## Instalación y pruebas (estado actual)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make fixture   # regenera tests/fixtures/ui_bundle.example.json (sintético)
make test
```

## Ejecución (objetivo M1)
```bash
cp .env.example .env
make demo      # build del snapshot + streamlit; funciona sin internet
```

## Datos, modelos y licencias
Ver `docs/notion_mirror/03_DATA_CATALOG.md` y `docs/ARCHITECTURE.md` §5. Inferencia 100% local (Ollama); costo de API $0.
