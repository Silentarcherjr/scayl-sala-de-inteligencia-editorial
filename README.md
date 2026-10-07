# SCAYL — Sala de Inteligencia Editorial

[![CI](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/actions/workflows/ci.yml/badge.svg)](https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial/actions/workflows/ci.yml)

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

## Para el equipo
Empieza por **`docs/ONBOARDING.md`** (configuración del entorno + prompts listos para Codex).

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

## IA local (opcional)
Ollama + `pip install -r requirements-ai.txt` (instala antes torch con CUDA desde pytorch.org). Ver `docs/ONBOARDING.md` §1.

## Datos, modelos y licencias
Ver `docs/notion_mirror/03_DATA_CATALOG.md` y `docs/ARCHITECTURE.md` §5. Inferencia 100% local (Ollama); costo de API $0.

## Recorrido visual

![Sala de Situación con el snapshot público](docs/screenshots/final/01-sala.png)

[Galería para el pitch: Agenda, las seis pestañas de Ficha, abstención, Trust Lab y Simulador](docs/screenshots/final/README.md).
Capturas locales de main dc1a990,1280×720, datos reales sin descripciones RSS. Trust Lab debe recapturarse
al integrar las nuevas métricas de PR #41; no representan un despliegue HF.

## Despliegue
Preparación del Hugging Face Space con contraseña y modo cache: [deploy/README.md](deploy/README.md).
Ejecutar `make public-bundle` y `python -m deploy.prepare`. Sin publicación hasta confirmación del Lead.
La preparación local actual no tiene caché LLM: las salidas se etiquetan template. El paquete no incluye
descripciones RSS, raw, etiquetas ni secretos.
