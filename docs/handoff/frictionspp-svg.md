# Relevo · frictionspp-svg

Actualizado: 2026-10-06 21:56 UTC. Rama: `worker-b/snapshot`. Destino de revisión: `main`.
El Lead revisa y mergea; este worker no mergea.

## Estado de entrega

El commit de implementación `eb61312` fue subido correctamente a `origin/worker-b/snapshot`
con `git push -u origin worker-b/snapshot`. Este relevo se añade en un commit posterior.
No hay PR abierto todavía. **B-01/B-02 siguen incompletas: el snapshot no está congelado.**

Implementados: fetchers DOC/GKG, RSS TVN, World Bank y USGS; escritura inmutable y recibos
SHA-256; constructor/verificador de manifest; adaptador RSS histórico; exportador de candidatos
ciegos; auditoría de adquisición; diccionario y pruebas. No se cambiaron contratos ni dependencias
fijadas. No se avanzó a la UI ni se generó un ranking para el editor.

## Datos disponibles y límites

La ejecución guardada en `data/raw/v1/acquisition-20261006T2140.json` registra:

- 300 noticias GDELT únicas combinando DOC y GKG; ninguna de TVN en esas respuestas.
- 540 observaciones WB para 6 países × 6 indicadores × 15 años; 0 valores nulos en esta descarga.
- 82 eventos USGS de 2024 dentro de la caja y magnitud requeridas.
- 152 entradas en el RSS TVN actual; 48 con publicación dentro del intervalo oficial completo,
  de las cuales 3 son de septiembre de 2025. No están incorporadas al corpus.

DOC sufrió errores 429; GKG es un muestreo histórico, no cobertura exhaustiva. Hay 76 filas GKG
excluidas con motivo en la auditoría. Las fechas de detección nunca sustituyen a las de publicación.

**Incluido en Git:** respuestas estructuradas DOC/WB/USGS, metadatos RSS sin descripciones,
recibos de solicitudes, auditorías y `acquisition_inventory.json`.

**Solo local:** ZIP auxiliares GKG (~910 MB), RSS XML con descripciones y directorio ignorado `models/`.
El inventario contiene también hashes de esos archivos locales: no debe confundirse con un snapshot
portable completo. Una clonación no incluye los ZIP ni el RSS XML original. No publicar descripciones
RSS ni modificar los bytes raw para resolver el empaquetado.

## Decisiones y trabajo pendientes

1. Resolver **AP-008** en `docs/AGENT_PROPOSALS.md`: las dimensiones WB producen 540 filas,
   aunque el plan dice 1.350. El worker no modifica TASKS ni el decision log.
2. Resolver **AP-009**: autorizar o rechazar el uso de las 48 entradas históricas conservadas
   en RSS, ampliando la cobertura TVN más allá de septiembre. Adaptador preparado, no aplicado.
3. Acordar el empaquetado de las fuentes auxiliares; completar `noticias.csv`, `fuentes.json`
   y `manifest.json`; comprobar integridad y cobertura. No declarar B-01/B-02 cerradas antes.
4. Generar `data/labels/editor_candidates.csv` sin puntajes al congelar el snapshot, para el top 5 ciego.
5. Abrir PR hacia `main` como borrador mientras haya pendientes; después seguir el orden del rol:
   A-01/A-08/A-02, B-03/B-04, B-11, B-05/B-07, B-06 y preparación/benchmark local.

## Verificación y entorno

Última ejecución guardada: **76/76 pruebas pasan**, 13 nuevas, en
`docs/worklog/worker-b-pytest.xml`. Comando:

```powershell
.\.venv\Scripts\python -m pytest -q
```

Se comprobó igualdad byte a byte de los 163 archivos raw preparados para el primer commit.
`data/raw/.gitattributes` impide conversión CRLF y preserva los hashes al clonar.
Fallos reales de extracción y correcciones: `docs/notion_mirror/06_TESTS_AND_METRICS.md`.

Entorno de esta ejecución: Windows, Python 3.14. Ollama portable 0.40.0 y GitHub CLI portable
2.102.0 están en `models/tools/`. `gh auth status` indicó que no había sesión, pero el push mediante
Git sí funcionó; no asumir que la ausencia de sesión en gh impide usar el remoto Git.

Modelos descargados localmente: `qwen3.5:9b`, `qwen3:8b`, `BAAI/bge-m3`,
`intfloat/multilingual-e5-base` y `Qwen/Qwen3-Embedding-0.6B`.
Ollama detectó **AMD Radeon RX 9060 XT, 8 GiB, Vulkan**, no RTX 4060.
Benchmark de calidad, latencia y tokens/s: **no medido**.

Detalle de actividad: `docs/worklog/worker-b.md`. Bitácora IA: `docs/AI_TOOLS_USED.md`.
