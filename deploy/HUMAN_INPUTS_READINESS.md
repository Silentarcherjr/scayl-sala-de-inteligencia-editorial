# A-06 · Stage probado con caché pública revisada

Preparado desde main `5b6fd71`, sin publicar. El stage local vigente es
`deploy/stage-human-reviewed/` (ignorado). Sustituye, para esta entrega, los stages anteriores
sin caché; no borrarlos ni usarlos para publicar. Inventario: `preparation-human-inputs.json`;
pruebas y hashes: `readiness-human-inputs.json`.

```powershell
python -m deploy.prepare --bundle deploy/artifacts/v1/bundle.public.json --cache deploy/artifacts/v1/llm --out deploy/stage-human-reviewed
```

Usar un destino nuevo si ya existe. Se comprobaron los 31 hashes de
`artifacts/v1/PUBLIC_CACHE_REVIEW.json`: bundle y 30 entradas de caché. El stage conserva
187 señales, 165 eventos, 15 paquetes cache y 150 template. La inspección recursiva no encontró
descripciones RSS ni referencias al campo `descripcion`; conserva la revisión de procedencia
de frictionspp-svg. La inspección estructural no constituye una nueva auditoría semántica.

El motor Docker no está activo (pipe Docker Desktop Linux inexistente), por lo que build y
contenedor quedan **no medido**. Se probó el stage con Streamlit local en 127.0.0.1:8518,
`PYTHONPATH` apuntando al stage, `SCAYL_HOSTED=1`, `SCAYL_LLM_MODE=cache` y una contraseña
sintética efímera en el entorno. No se usaron credenciales de HF.

- Chromium: ruta directa `/Trust_Lab` bloqueada antes de autenticar, contraseña incorrecta
  rechazada, acceso correcto, métricas visibles y cierre de sesión efectivo.
- AppTest sobre el stage: ausencia de contraseña cierra el acceso; cuatro rutas directas
  protegidas; contraseña incorrecta seguida de correcta; rotación/eliminación revocan acceso.
- Consultas ofrece únicamente `cache`. El adaptador fuerza cache incluso con `mode='live'`:
  los 15 paquetes precalculados se regeneraron desde caché, con el backend Ollama sustituido
  por una excepción para detectar cualquier intento de llamada. Cero llamadas.
- Las consultas sin entrada precalculada pueden caer a template, con el modo real visible.

Capturas reales: `docs/screenshots/final/10-trust-lab.png`, `12-space-acceso.png` y
`13-trust-lab-procedencia.png`, con hashes y procedencia por archivo.

El stage está listo para revisión del Lead. **No está publicado**: falta su confirmación antes
de crear/subir el Space. Docker y HF remoto no están validados; la prueba local es la alternativa
solicitada. Después de la confirmación, usar un Space privado y configurar la contraseña como
Secret de runtime. No incluirla en Git ni en el PR. URL y contraseña se comparten por privado.

## Evaluación mostrada

B-09 completada por LowCrime: 25 sí, 3 no, 2 parcial; validez estricta 25/30 (83,3%).
Las 30 afirmaciones pertenecen a la muestra **template** congelada anteriormente, cuyo hash
original consta en `support_review.meta.json`. No validan las salidas LLM de la caché pública.
La IA transcribió las decisiones humanas; no eligió etiquetas ni completó comentarios ausentes.

B-08 se ejecutó con el bundle público entregado colocado temporalmente en
`data/processed/v1/bundle.json` (ruta que exige el CLI); se restauró después el bundle local
anterior. El hash registrado en la corrida corresponde a `artifacts/v1/bundle.public.json`.
Para reproducir, usar ese bundle en la ruta de entrada del CLI y ejecutar:

```powershell
python -m scayl.eval.run --support-review "$PWD/data/labels/support_review.csv" --pytest-report tmp/human-inputs-pytest.xml --redteam-report eval/results/runs/20261007T174649391539Z.redteam.json
```

La evidencia pytest está archivada en la nueva corrida; puede usarse ese XML para reproducir
la importación. El red-team y el precompute se importan con su fecha/hardware originales,
sin presentarlos como ejecuciones nuevas. P@5 sigue 1/5, exploratoria, con DL-024 visible.
Lo no medido permanece así. El stage solo copia `latest.json`; los archivos de evidencia
referenciados permanecen en el repositorio, no se sirven como descargas en el Space.
