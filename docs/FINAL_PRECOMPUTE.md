# Precálculo después de DL-026/DL-027

Ejecución real desde main `dc1a990`, E5 activo (CPU), qwen3:8b en AMD RX 9060 XT 8 GiB,
Ollama 0.40.0 Vulkan, 37/37 capas GPU. Caché dedicada inicialmente vacía.
GNU Make no está instalado; se ejecutó exactamente su receta con Python:

```powershell
$env:SCAYL_INTEL = 'ai'
$env:SCAYL_LLM_MODEL = 'qwen3:8b'
$env:SCAYL_LLM_CACHE = 'data/cache/llm/final-precompute-20261007'
python -m scayl.pipeline build --snapshot data/raw/v1 --llm live --top 15
python -m scayl.eval.precompute_report
```

15/15 paquetes live, 0/15 fallback; mediana **14643 ms**, p95 **17600 ms**, n=15.
Percentil lineal tipo 7, latencia de respuestas Studio exitosas, sin llamadas claims.
Cobertura de citas brief/guion conservados **49/49**; 68 oraciones generadas y 64 conservadas
(incluye copy). Eliminadas dos UNCITED_FACT y dos STATUS_MISMATCH. No mide validez del apoyo.
Resultados originales con hashes en `eval/results/final-precompute.json` y su JSONL.
Bundle, fichas y caché permanecen locales. Los resultados anteriores siguen intactos.

Validación: 172 pruebas pasan; carga real E5 comprobada por el pipeline. El ingest entrega
187 noticias con descripcion=null. La caché pública se revisa en otra tarea/PR antes de exportarla.
