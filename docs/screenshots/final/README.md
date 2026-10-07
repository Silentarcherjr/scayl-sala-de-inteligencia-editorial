# Capturas de entrega · 1280×720

**Actualización tras PR #51:** las imágenes 10, 12 y 13 provienen del stage público con
contraseña `deploy/stage-human-reviewed`, código `5b6fd71`, 187 señales y 165 eventos,
15 paquetes cache y 150 template. Muestran AP-014 aplicada y B-09 completa (25/30).
Su procedencia y hashes están en cada entrada de `manifest.json`; sustituyen para esas
imágenes la procedencia general del lote original. Las otras diez imágenes no se recapturaron.
No es un despliegue HF. La muestra humana evaluada es template, no la caché LLM.

Capturas reales de Chromium local sobre `main` dc1a990, snapshot v1 con ACP/INEC, bundle público sin
descripciones RSS: 187 señales,183 eventos baseline, paquetes template. No se editaron las imágenes
ni se publicaron revisiones/simulaciones. Estado de revisión temporal. Hashes de bundle/evaluación/PNG
en `manifest.json`. No son imágenes de un Space desplegado ni el video H-05 (responsabilidad del Lead).

| Archivo | Pantalla / uso en pitch |
|---|---|
| [01-sala.png](01-sala.png) | Embudo y separación atención/evidencia |
| [02-agenda.png](02-agenda.png) | Primeras tarjetas del top5, motivos y fuentes sugeridas |
| [03-ficha-evento.png](03-ficha-evento.png) | Evento EVT-0111: titular, fechas y alcance |
| [04-ficha-fuentes.png](04-ficha-fuentes.png) | Publicaciones frente a independencia no confirmada |
| [05-ficha-evidencia.png](05-ficha-evidencia.png) | Contexto WB histórico y ACP fechado, no medición actual |
| [06-ficha-vacios.png](06-ficha-vacios.png) | Qué sabemos, afirmamos y falta verificar |
| [07-ficha-producir.png](07-ficha-producir.png) | Paquete template, alcance y validación |
| [08-ficha-revision.png](08-ficha-revision.png) | Control humano; formulario sin enviar |
| [09-consultas-abstencion.png](09-consultas-abstencion.png) | Pregunta fuera del corpus: motivo e información necesaria |
| [10-trust-lab.png](10-trust-lab.png) | Revisión humana 25/30, abstención y latencia con n |
| [11-simulador.png](11-simulador.png) | Pesos oficiales y ranking, sin registrar cambios |
| [12-space-acceso.png](12-space-acceso.png) | Ruta directa protegida por contraseña, sin datos antes de entrar |
| [13-trust-lab-procedencia.png](13-trust-lab-procedencia.png) | Red-team, limitación DL-024 y procedencia del precompute |

La captura actual de Trust Lab incluye #41 y AP-014 integradas vía #51. La evaluación distingue
la revisión humana template de las mediciones importadas de precompute y red-team.
La evaluación mostrada tiene su propia fecha de ejecución; no se presenta como recalculada al capturar.

Reproducir: ejecutar `python -m scayl.pipeline build --snapshot data/raw/v1 --llm cache --top 15 --public`
con SCAYL_INTEL=baseline; iniciar Streamlit Home, fijar viewport1280×720, abrir EVT-0111 y recorrer las
seis pestañas; en Consultas preguntar por turistas en Bocas del Toro en agosto de2035 y enfocar Resultado.
No cargar RSS/descripciones ni rellenar datos personales para hacer capturas.
