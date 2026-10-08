# Documentación técnica

> Fuente canónica: el repositorio (`docs/ARCHITECTURE.md`, `docs/notion_mirror/`, `eval/results/`). Toda cifra de esta página está medida en el repo; lo que no se midió se declara "no medido".

## 1. Arquitectura

```
Snapshot congelado (data/raw/v1, manifest con SHA-256)
  noticias GDELT + RSS TVN · ACP (lago Gatún) · INEC (IPC) · World Bank · USGS
        │
        ▼  scayl.ingest     validar · normalizar · excluir con motivo · reporte de calidad      (T01)
        ▼  scayl.intel      temas por reglas · agrupación con E5 multilingüe · índice BM25       (T02, T03)
        ▼  scayl.evidence   Source DNA · vínculo oficial · Temporal Guard · conflictos ·
        │                   puntaje P · estado de evidencia · vacíos de investigación            (T04, T05, T08)
        ▼  scayl.gen        LLM local (Qwen3 8B) → validadores deterministas → fallback plantilla (T06, T07, T09)
        ▼  bundle.json      165 eventos + paquetes + evidencia
        │
        ├─ Web Next.js (Vercel): páginas estáticas + funciones Python (consulta libre y revisión)
        └─ Streamlit: demo offline completa (T10) y versión de respaldo
```

- **Núcleo Python por lotes** (pydantic, numpy, rank-bm25, PyYAML). Un solo contrato de datos (`scayl/contracts.py`).
- **IA en tres puntos acotados**, siempre detrás de validadores: extracción de afirmaciones, paquete editorial y respuestas a consultas.
- **Sin publicación automática:** no existe ninguna función que publique.

## 2. Modelo de datos

`NewsItem`, `IndicatorObservation`, `SeismicEvent` → **`Event`** (SourceDNA, Claim, Conflict, TemporalWarning, PriorityScore, EvidenceStatus, InvestigationGap) → `StoryPackage` / `QAAnswer` / `SectorBulletin` → `ReviewRecord` → `Ficha` (contrato oficial).

Cada cita es un `EvidenceRef`: `evidence_id`, tipo, campo, valor, período, URL y extracto. Los nulos nunca se convierten en cero.

## 3. Reglas de priorización (`scoring-v1`)

**P = 30·R + 25·I + 20·U + 15·N + 10·E** (cada componente entre 0 y 1).

| Componente | Peso | Qué mide |
|---|---|---|
| R · Relevancia | 30 | Relación con Panamá y con los temas del reto |
| I · Impacto potencial | 25 | Peso editorial del tema y evidencia oficial pertinente |
| U · Urgencia | 20 | Recencia respecto al corte del snapshot |
| N · Novedad | 15 | Ausencia de eventos previos similares |
| E · Evidencia disponible | 10 | Evidencia oficial y procedencias posibles |

Rangos: bajo [0, 40), medio [40, 70), alto [70, 100]. Desempate: U y luego ID. **P mide atención, no probabilidad de verdad.** El estado de evidencia (insuficiente / parcial / suficiente para borrador) se calcula aparte.

## 4. Modelos y uso de IA

| Uso | Modelo | Por qué |
|---|---|---|
| Agrupación de titulares en eventos | E5 multilingüe (local) | F1 **0,99** frente a 0,44 de TF-IDF (pares de desarrollo usados para calibrar τ: resultado optimista) |
| Temas | **Reglas** (no IA) | Macro-F1 **0,76** frente a 0,25 de E5: usamos IA solo donde ganó |
| Borradores editoriales | Qwen3 8B en Ollama (local, GPU AMD RX 9060 XT) | Mediana **13,1 s**, p95 17,0 s (n = 15); costo de API **$0** (sin incluir hardware ni electricidad, no medidos) |
| Consultas | BM25 + plantilla extractiva; salidas de Qwen precalculadas | Respuestas reproducibles, sin red |

Parámetros del LLM: temperatura 0, semilla 42, salida JSON con esquema. Prompts versionados en `scayl/gen/prompts/*.vN.md`.

## 5. Controles y validadores

- **Generación claim-first:** el modelo solo ve afirmaciones numeradas dentro de un bloque de datos no confiable y debe citar sus IDs en cada frase.
- **Validador numérico:** elimina cualquier cifra que no esté en la evidencia citada.
- **Temporal Guard:** todo dato lleva su fecha; lo histórico ("Dato histórico — 2024") nunca se presenta como actual.
- **Defensa contra inyección:** las fuentes marcadas como sospechosas no se citan ni se envían al modelo.
- **Abstención:** si no hay evidencia, el sistema lo dice y señala qué fuente faltaría.
- **Fallback:** cualquier fallo del modelo vuelve a la plantilla determinista, y la interfaz muestra el modo real (`cache` / `template`).

## 6. Pruebas y métricas medidas

| Métrica | Resultado | Alcance |
|---|---|---|
| Pruebas del reto T01–T10 | **10/10 aprobadas** (pruebas automatizadas) | `eval/results/latest.json`; T10 se verifica con la red bloqueada en pytest, no equivale a un ensayo real sin wifi |
| Pruebas automatizadas | **287** (pytest) + lint, en CI | GitHub Actions |
| Cobertura de citas del borrador | **45/45** | Top 15 con Qwen3 8B; mide presencia de cita, no validez del sustento |
| Validez de sustento (revisión humana) | **25/30 = 83 %** | Muestra de paquetes en modo plantilla (no de borradores de Qwen). Por debajo de la meta orientativa del 90 %; se explica en DL-031 |
| Abstención en set reservado escrito por un humano | **6/6** trampas | Escrito por un integrante del equipo sin ver los casos existentes; también se abstuvo en 4/4 controles de cultura general (6/10 frente a sus expectativas, DL-030) |
| Abstención en red-team de desarrollo | 16/16 (antes 6/16) | Set sintético; corregido sobre ese mismo set (DL-027) |
| Precision@5 frente al top 5 del editor | 1/5 | Exploratoria (DL-024) |
| Ahorro de tiempo | **No medido** | No lo afirmamos |

## 7. Despliegue

| Superficie | Tecnología | Detalle |
|---|---|---|
| Demo principal | Next.js estático en Vercel + funciones Python | Consulta libre y revisión en modo caché; sin claves ni costo |
| Respaldo | Streamlit Community Cloud | Mismo stage auditado |
| Offline | `python scripts/demo_offline.py` o `npx serve out` | Sin descargas ni llamadas externas; T10 verificado en pytest con la red bloqueada |

Solo se publican el bundle público (sin descripciones RSS) y la caché revisada; cada archivo del stage tiene un hash verificado.

## 8. Seguridad, privacidad y derechos

- Solo titulares, URL y metadatos: no se redistribuyen artículos, imágenes ni videos.
- Sin datos personales ni perfiles; las acusaciones se etiquetan como DECLARACIÓN con atribución.
- Sin secretos en el repositorio (`.env` ignorado; `.env.example` sin valores secretos).
- Inferencia 100 % local: ningún dato de la redacción sale a un tercero.

## 9. Decisiones técnicas clave

37 decisiones registradas (DL-001 a DL-037) en `docs/notion_mirror/02_DECISION_LOG.md`. Las principales:
- **DL-002** Núcleo Python con interfaz simple para llegar a tiempo.
- **DL-027** El red-team encontró fallos (6/16); se corrigieron con reglas generales y pruebas de regresión.
- **DL-029** Temas por reglas, agrupación con E5: la IA solo donde ganó.
- **DL-034 / DL-036** Web Next.js con funciones Python en modo caché.
- **DL-035** Extensión bancaria acotada: boletín de entorno sectorial.

## 10. Reproducir

```bash
pip install -r requirements.txt
python scripts/demo_offline.py          # demo sin internet en http://localhost:8501
python -m pytest -q && ruff check .     # pruebas
cd web && npm ci && npm run build       # web estática
```
