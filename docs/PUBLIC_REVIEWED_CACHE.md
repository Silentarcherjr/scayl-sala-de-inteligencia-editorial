# Caché pública revisada para A-06

Artefactos en `deploy/artifacts/v1/`: bundle público (187 señales, 165 eventos) y **30 entradas**
de caché consumidas realmente (15 claims y 15 Studio). Los 15 paquetes prioritarios son cache;
el resto conserva template. No se renombra ningún modo ni se despliega nada.

Procedencia: main dc1a990, reglas DL-026/DL-027, precálculo qwen3:8b con E5 CPU y Ollama Vulkan.
Se comprobó **antes de construir prompts** que las 187 noticias tenían descripcion=null.
Solo titulares/metadatos; bundle y entradas revisados por Codex: esquema, ausencia de
descripciones/citas a descripcion y aplicación del pipeline/validadores reales. No es revisión
humana de validez del apoyo. El caché conserva salida cruda del modelo: cualquier oración
rechazada vuelve a validarse al leer; la UI muestra solamente el paquete validado.

`PUBLIC_CACHE_REVIEW.json` lista las claves usadas, versión de prompt, huella de entrada,
huella del código y manifest, hashes de cada artefacto y alcance de revisión. Nunca se copia
una carpeta de caché completa, historial humano, raw RSS, ZIP, secretos o pesos de modelos.
`data/processed/` continúa local; este directorio contiene exclusivamente el artefacto público
autorizado para preparar A-06. La publicación del Space requiere confirmación del Lead.

```powershell
$env:SCAYL_INTEL = 'ai'
# Equivalente de make public-bundle; cache, top15, public=True, sin inferencia LLM:
python -m scayl.ingest.export_public_cache --cache data/cache/llm/final-precompute-20261007 --out deploy/artifacts/v1
# Para LowCrime, tras integrar el PR; destino nuevo, sin subir el stage:
python -m deploy.prepare --bundle deploy/artifacts/v1/bundle.public.json --cache deploy/artifacts/v1/llm --out deploy/stage-reviewed
```

No sobrescribir destino existente. Para reproducir, usar otro destino y comparar hashes.
E5 local solo se necesita para reconstruir, no para servir el bundle ya exportado.
