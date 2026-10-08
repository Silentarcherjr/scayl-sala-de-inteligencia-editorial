# Web Next.js estática (DL-034) · brief para el agente

> **Aprobado por el Lead (Humano 1, Silentarcherjr) el 2026-10-08 — DL-034.** Esta aprobación cubre las
> dependencias npm de `web/` y la carpeta nueva `web/`; no hace falta propuesta en `AGENT_PROPOSALS.md`
> para lo que está dentro de este brief. Cualquier cosa **fuera** de este alcance sí la requiere.
> **Plazo duro:** entrega el jueves 8 de octubre a las 23:59 (hora de Panamá). Prioriza terminar sobre pulir.

## 1. Objetivo
El jurado evalúa solo, del 9 al 12 de octubre, abriendo una URL. La demo actual en Streamlit funciona
pero no luce. Construir un **sitio Next.js estático** (export) con diseño cuidado que muestre los
**mismos datos y resultados** de SCAYL, desplegado en **Vercel**. Streamlit **no se elimina**: queda
como demo offline (T10) y como destino del enlace "pregunta libre".

Por qué estático alcanza: la demo pública no ejecuta IA en vivo. Eventos, puntajes, fichas, paquetes
IA (Qwen3 8B precalculado, modo `cache`) y métricas son datos fijos. Solo la **pregunta libre** de
Consultas necesita cómputo Python (BM25 + validadores); esa se enlaza a Streamlit (ver §5.3).

## 2. Reglas (no negociables)
- **No modificar** `scayl/`, `app/`, `deploy/`, `tests/` existentes ni datos en `data/` o `deploy/artifacts/`.
  Se agrega: `web/`, `scripts/export_web.py`, `tests/test_export_web.py`, `.github/workflows/web.yml`.
- **Rama:** `worker-web/next-static`, PR hacia `main`. Mergea el Lead.
- **Mismos números:** todo dato sale de `scripts/export_web.py`, que usa `scayl.service`. **Prohibido**
  recalcular en TypeScript algo que ya calcula Python, excepto el Simulador (§5.5, fórmula explícita).
- **Nulos:** nunca convertir `null` en `0` ni en `""`. Mostrar "no disponible".
- **Sin `descripcion` RSS:** el export debe fallar si algún `descripcion` tiene valor (reusar
  `deploy.prepare.check_public`).
- **Sin llamadas externas en runtime:** nada de APIs, analytics, CDNs ni Google Fonts en tiempo de
  ejecución. Fuentes con `next/font` (se autoalojan en el build) o locales. Sin claves ni secretos.
- **Seguridad:** prohibido `dangerouslySetInnerHTML`. Los enlaces a fuentes solo si el esquema es
  `http`/`https`, con `rel="noopener noreferrer"` y `target="_blank"`. El texto de fuentes es dato.
- **Avisos obligatorios** (los evalúa el reto; deben verse, no esconderse en tooltips):
  - "P mide atención, no probabilidad de verdad ni impacto. El estado de evidencia es independiente."
  - "Prioridad alta NO habilita publicación. Aprobado como borrador NO significa publicado."
  - En cada salida IA: modo (`cache` / `template`) y modelo (`ollama:qwen3:8b` o "no aplica").
    `template` se rotula como "Plantilla (sin IA generativa)".
  - "La procedencia independiente no puede determinarse con la evidencia disponible" cuando aplique
    (`source_dna.statement`), y "N publicaciones ≠ N confirmaciones".
  - Advertencias temporales (`temporal_warnings`): "Dato histórico — AAAA. No presentarlo como medición actual."
  - `text_scope_note` ("Basado únicamente en titular/metadatos") cuando exista.
  - Casos `synthetic`: etiqueta visible "SINTÉTICO".
- **Marca:** solo la **paleta** inspirada en TVN (§4). Nada de logo, nombre ni tipografía de TVN como
  marca de SCAYL. La marca es "SCAYL · Sala de Inteligencia Editorial".
- Registrar el trabajo en `docs/worklog/<tu-worker>.md` y una fila en `docs/AI_TOOLS_USED.md`.

## 3. Exportador de datos: `scripts/export_web.py`
Ejecutar igual que la demo offline (ver `scripts/demo_offline.py`): bundle público
`deploy/artifacts/v1/bundle.public.json` copiado a `data/processed/v1/bundle.json`, entorno
`SCAYL_LLM_MODE=cache`, `SCAYL_LLM_CACHE=deploy/artifacts/v1/llm`. Reusar `prepare()` de ese script.

Escribe en `web/public/data/` (archivos **versionados en git**, para que Vercel no necesite Python):

| Archivo | Contenido | Fuente |
|---|---|---|
| `meta.json` | `snapshot_version`, `snapshot_cutoff_utc`, `signals_total`, `signals_valid`, `events_total`, `weights` (`service.official_weights()`), `exported_at`, `git_commit` | `service.load_bundle()` |
| `events.json` | Lista **resumida** y **ordenada** (P desc, U desc, `event_id` asc; igual que `app/Home.py::ranked_events`): `event_id, title, topic, priority{score,tier,components}, evidence_status, recommended_action, last_published, first_detected, source_dna{publications,max_possible_independent,confirmed_independent}, has_conflicts, is_recirculated, synthetic, package_mode` | `Event` |
| `cases/<EVT-ID>.json` | `Event.model_dump(mode="json")` completo + `headlines` (por `member_ids`: `id_noticia, titulo, medio, url, idioma, fecha_publicacion, origen`; **sin** `descripcion`) + `package` (`service.get_package(id)`, puede ser `null`) | `Event`, `NewsItem`, `StoryPackage` |
| `qa.json` | Respuestas precalculadas (`QAAnswer` en JSON) a cada pregunta de `EXAMPLES` y a cada flujo de `JURY` en `app/pages/2_Consultas.py`; reproducir exactamente lo que hace esa página en modo `cache`. Incluir `label` y `question` | `service.ask(...)` |
| `trust_lab.json` | `service.trust_lab()` y `service.generation_summary()` | — |

Requisitos del exportador: determinista (mismo input → mismos bytes salvo `exported_at`), JSON con
`ensure_ascii=False`, ordenado, y que corra `check_public` sobre todo lo exportado.
`tests/test_export_web.py`: exporta a `tmp_path`, verifica 0 `descripcion` con valor, que `events.json`
tenga la longitud de `bundle.events` en el orden de `ranked_events`, y que cada `cases/*.json` exista.

## 4. Sistema visual
- **Paleta:** azul `#005588` (primario), azul claro `#0077C8` (etiquetas de sección), amarillo `#FEC526`
  (acentos finos), marino `#0B1220` (barra/encabezado), texto `#2A2A2A`, gris `#5A6673`, fondos `#FFFFFF`
  y `#F2F4F7`, bordes `#DCE1E7`. Prioridad: alto `#C2410C`, medio `#B45309`, bajo `#5A6673`.
  Evidencia: insuficiente rojo apagado, parcial ámbar, suficiente_para_borrador verde (siempre con texto,
  nunca solo color).
- **Tipografía:** Inter (o similar) vía `next/font`; títulos 700–800, cifras con `tabular-nums`.
- **Estilo:** redacción digital moderna: encabezado marino fijo con "SCAYL", etiqueta de sección
  (texto `#0077C8` en mayúsculas + barrita amarilla) sobre cada título, tarjetas blancas con sombra
  suave y borde superior de color, mucho aire, responsive (debe verse bien en un portátil y en un móvil).
- **Stack:** Next.js (App Router) + TypeScript + Tailwind CSS. Versiones **fijadas** en `package.json`
  y `package-lock.json` versionado. `output: "export"`, `images: { unoptimized: true }`, `trailingSlash: true`.
  Componentes propios; se permite `lucide-react` para íconos y una librería de gráficos ligera
  (p. ej. Recharts) si hace falta. Nada más sin preguntar.

## 5. Pantallas
1. **Sala de Situación** (`/`):
   - Encabezado con snapshot y corte (hora de Panamá, `America/Panama`).
   - 4 KPIs (señales recibidas, válidas, eventos, top 5) y los dos avisos de §2.
   - **Agenda de la mañana:** top 5 en tarjetas grandes con titular, badge P y tier, badge de evidencia,
     las 2 razones principales (mayor `peso×componente`, ver `app/components/agenda.py::top_reasons`),
     acción sugerida y botón "Investigar" → ficha.
   - Tabla filtrable por tema y estado de evidencia (búsqueda por texto en titular) con las columnas de
     `app/Home.py`, y la matriz Prioridad × Evidencia que se recalcula con los filtros.
2. **Ficha de Caso** (`/caso/[id]/`, `generateStaticParams` sobre los 165):
   - Titular, P grande con desglose R/I/U/N/E (barras con `contribución/peso` y la justificación de
     `rationale`), estado de evidencia con motivo, acción recomendada, avisos.
   - Pestañas: **Evento** (tema, entidades, línea de tiempo, titulares del evento con medio y enlace),
     **Fuentes** (Source DNA: grupos de procedencia, statement, N publicaciones ≠ N confirmaciones),
     **Evidencia** (evidencia oficial como tarjetas de cita desplegables: id, tipo, campo, valor,
     período, URL, extracto; ver `app/components/evidence_card.py`), **Afirmaciones** (claims con tipo
     y estado), **Conflictos** (versión A vs B lado a lado, verificación pendiente), **Vacíos**
     (`gap`: qué sabemos / qué se afirma / qué inferimos / qué no sabemos / 3 preguntas a investigar),
     **Producir** (paquete: título propuesto, ángulo, brief, guion, copy social con etiquetas
     HECHO/DECLARACION/INFERENCIA/HIPOTESIS, verificaciones pendientes, fuentes, validación y modo/modelo).
   - **Revisión** se muestra como solo lectura: "La revisión humana se registra en la versión de trabajo;
     en esta demo pública es de solo lectura." (No hay backend que guarde decisiones.)
3. **Consultas** (`/consultas/`):
   - Botones del Modo jurado + ejemplos; al pulsar se muestra la respuesta precalculada de `qa.json`
     (oraciones con etiqueta, citas desplegables, o abstención con motivo e información necesaria;
     validación y modo/modelo).
   - Buscador de casos por texto (cliente, sobre `events.json`).
   - Bloque "¿Pregunta libre?" con enlace a https://scayl-demo.streamlit.app/ explicando que la búsqueda
     sobre el corpus corre en Python y que las preguntas sin salida precalculada usan plantilla.
4. **Trust Lab** (`/trust-lab/`): T01–T10 como tarjetas (estado, esperado, evidencia), métricas con
   numerador/denominador, "no medido" donde corresponda, modelo/costo, red-team y limitaciones.
   Mismo contenido que `app/pages/3_Trust_Lab.py`.
5. **Simulador de pesos** (`/simulador/`): sliders R/I/U/N/E (enteros, suma 100) que recalculan en el
   cliente `P = Σ peso_k × componente_k` y reordenan; mostrar "orden oficial vs simulado" y aclarar que
   **no cambia** el ranking oficial. Comparar con `app/pages/4_Simulador_de_pesos.py` y `service.simulate_weights`.
6. **Pie de página** en todas: snapshot, "Demo con salidas IA precalculadas (Qwen3 8B local) · modo cache",
   enlace al repositorio y a la versión Streamlit.

## 6. Orden de trabajo (entregar por etapas, cada una desplegable)
1. `scripts/export_web.py` + test + datos en `web/public/data/` → commit.
2. Esqueleto Next.js + sistema visual + layout + Sala de Situación → `npm run build` OK → commit.
3. Ficha de Caso → commit. 4. Consultas → commit. 5. Trust Lab + Simulador → commit.
6. `.github/workflows/web.yml`: `npm ci && npm run lint && npm run build` en `web/`.
7. README: sección "Probarlo" con la URL de Vercel como principal y Streamlit como respaldo/offline.

## 7. Verificación antes del PR
- `python -m pytest -q` y `ruff check .` en verde (incluye el test nuevo).
- `cd web && npm ci && npm run build` sin errores ni warnings de tipos; `npx serve out` y recorrer las
  5 pantallas **con el wifi apagado** (debe funcionar offline: valida que no hay llamadas externas).
- Contrastar 3 casos al azar (incluido el top 1, EVT-0101) contra la versión Streamlit: mismo P, mismos
  componentes, mismo estado de evidencia, mismo paquete y modo.
- Buscar en `web/` que no exista `dangerouslySetInnerHTML`, `fetch("http`, ni claves.
- Capturas de las 5 pantallas en `docs/screenshots/web/`.

## 8. Despliegue (lo hace el humano o el agente con la sesión del humano)
Vercel → *Add New Project* → importar `Silentarcherjr/scayl-sala-de-inteligencia-editorial` →
**Root Directory: `web`** → framework Next.js → Deploy. Sin variables de entorno. Registrar la URL en
`README.md` y `deploy/README.md`. Mientras el repo sea privado, Vercel necesita acceso a él desde la
integración de GitHub.
