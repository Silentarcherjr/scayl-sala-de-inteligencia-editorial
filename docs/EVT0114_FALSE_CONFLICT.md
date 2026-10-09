# EVT-0114: falso conflicto 4.7 vs 7.4 — corrección de código, datos públicos sin cambiar

## Diagnóstico (2026-10-08)
- EVT-0114 agrupa dos titulares de telemetro.com detectados con un día de diferencia:
  `gdt-d8c316078fe594bf3304` «Sismo de magnitud 4.7 sacude la frontera entre Panamá y Costa Rica» (2026-07-16) y
  `gdt-c6b01656acfd72f77213` «Sismo de magnitud 7.4 entre México y Guatemala no genera riesgo de tsunami para Panamá»
  (2026-07-17). La agrupación E5 los unió por similitud de redacción; son sismos distintos.
- Consecuencia publicada: conflicto CNF-0114-002 (4.7 vs 7.4), afirmación CLM-0114-004 dentro del mismo evento y un
  paquete de Qwen que menciona ambos sismos.
- El vínculo USGS es **válido**: `us7000t0xy`, M4.5, 2026-07-16 10:33 UTC, «3 km ENE of Santa Cruz, Panama»
  (−82,73; 8,65, Chiriquí, a unos 25 km de Costa Rica), el mismo día que el titular del 4.7. CNF-0114-001 (4.7 vs 4.5)
  es un conflicto legítimo entre fuentes.

## Corrección de código (este PR)
- `scayl/intel/cluster.py::split_distinct_quakes`: dos titulares sísmicos del mismo grupo cuyos países de ocurrencia
  son disjuntos se separan. Reutiliza la regla de lugar de `scayl/evidence/linking.py`: «para Panamá» indica a quién
  afecta, no dónde ocurrió. Un titular sin lugar no se separa.
- `scayl/pipeline.py`: `build --clusters-from <bundle>` reutiliza la agrupación y los IDs de un bundle previo (no
  requiere E5) y `stable_ids` conserva los IDs existentes; las piezas nuevas reciben IDs a partir del máximo.
- `tests/test_cluster_distinct_quakes.py`: 6 pruebas (dos sismos distintos con fechas cercanas y magnitudes
  diferentes; mismo sismo por provincia y país; titular sin lugar; no sísmicos intactos; IDs estables; reconstrucción
  que conserva el conflicto legítimo 4.7 vs 4.5 y elimina el 4.7 vs 7.4).

## Ensayo de regeneración (no publicado)
```bash
SCAYL_LLM_CACHE=deploy/artifacts/v1/llm python -m scayl.pipeline build --snapshot data/raw/v1 --llm cache \
  --top 15 --public --clusters-from deploy/artifacts/v1/bundle.public.json --out <dir>
```
| Capa | Resultado frente a `deploy/artifacts/v1/bundle.public.json` |
|---|---|
| Eventos | 165 → 166. Solo cambia EVT-0114 (1 publicación, P 67,5 sin cambio, conflicto 4.7 vs USGS 4.5, estado parcial) y aparece EVT-0166 (7.4 México–Guatemala, P 57,5, puesto 35, insuficiente, sin conflictos). Ningún otro ID cambia; prioridad, afirmaciones, evidencia, Source DNA y vacíos de los otros 164 son idénticos; top 15 y ranking idénticos |
| Paquetes | 153 difieren. No por esta corrección: el código de plantilla y validadores integrado en PR #78 cambia la redacción al regenerar. EVT-0114 pasaría de Qwen (caché) a plantilla porque su prompt cambia |

## Decisión: NO-GO para los datos públicos
Una regeneración reproducible cambiaría 153 paquetes ajenos a este problema. La alternativa sería empalmar solo dos
eventos en un bundle generado por otra versión del código, lo que no es una salida consistente de un único
procedimiento. Se conserva `5dc1797` como versión estable y los datos públicos no cambian. Para publicar la
corrección hace falta una decisión explícita:
1. **Regenerar todo** con `--clusters-from` y revisar los 153 paquetes (incluyen los calificadores de atribución que
   corrigen los fallos de la revisión humana de sustento), o
2. **Regenerar con la versión de código del bundle publicado** más solo esta corrección.

En ambos casos EVT-0114 necesitaría una nueva generación con Qwen3 8B o quedaría en modo plantilla, y la métrica de
cobertura de citas (45/45) seguiría describiendo la corrida precalculada, no el bundle nuevo.

## Limitaciones
- La regla trabaja a nivel de país; dos sismos distintos en el mismo país y días cercanos no se separan con ella.
- Solo titulares: no hay coordenadas en las noticias.
