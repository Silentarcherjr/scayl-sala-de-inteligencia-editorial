# DL-035 · boletín Qwen: revisión humana pendiente

El Lead atribuyó el primer fallback al esquema: claim_ids tenía un valor por
defecto y no era obligatorio para Ollama. Se autorizó únicamente el esquema
en bulletin.py, prompt nuevo de texto idéntico y prueba nueva. Las tres secciones
exigen text/tag/claim_ids, sin campos extras, al menos una cita y enum de los IDs
enviados en el payload. No cambian contratos, validadores ni contenido del prompt.

Segundo y último intento autorizado, 2026-10-08T05:34:00.932743Z:
live, ollama:qwen3:8b, bulletin-v3; 33625ms; tokens_in2050, tokens_out1771;
validation.passed=true, issues=[]; no fallback. AMD RX9060XT8GiB/Vulkan,
Ollama0.40.0, Q4_K_M, contexto4096, temperatura0, seed42. Coste API0USD.
El resumen final se conserva por código, como ya disponía el camino de logística.

Caché temporal única:
tmp/bulletin-cache/8246efd0d0b94854f631a9e0f0a72bd4eb115af62e9302927297bc59dc010588.json.
Resultado validado y contexto/hashes locales: tmp/bulletin-live.json y
tmp/bulletin-run-context.json. Primer intento preservado en tmp/bulletin-cache-v2-rejected.
No se regeneró el modelo buscando otro texto.

Se mostró el texto completo al humano frictionspp-svg. **Aprobación pendiente**:
no copiar a caché pública, no exportar ni afirmar revisión humana terminada.
Advertencia destacada: el titular de 33 cupos y 14,94 metros tiene fuente, pero
período no disponible. El texto lo declara y prohíbe asumir condiciones actuales.
La cifra de exportaciones de 2024 conserva advertencia histórica. No se inventó período.

Verificación antes del export: 243 pytest con PYTHONUTF8=1, Ruff verde;
npm.cmd ci, npm.cmd run lint y npm.cmd run build pasan. npm ci informó cinco
avisos de vulnerabilidades altas en dependencias existentes; no se cambió el lockfile.
Tras aprobación aún faltan cache review, export_web, verificación del modo cache,
checks sobre ese export, deploy.prepare a destino nuevo y PR con boletín completo.
Corte duro: 2026-10-08 18:00 America/Panama (23:00Z).
