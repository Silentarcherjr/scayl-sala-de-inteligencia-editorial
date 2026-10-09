# Guion de demostración · recorrido local y web

Objetivo: mostrar el flujo **señal → evento → prioridad → evidencia → investigación → producción → revisión humana**. La variante local utiliza el snapshot y las respuestas guardadas; la variante web incluye consultas con evidencia y verificación determinista.

## Antes de grabar (5 min, una sola vez)
```bash
git pull                                   # main actualizado
python -m venv .venv
.venv\Scripts\activate                     # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python scripts/demo_offline.py             # deja la app en http://localhost:8501
```
1. Abre `http://localhost:8501` en el navegador y espera a que cargue la Sala.
2. **Apaga el wifi** (o desconecta el cable). Muestra el ícono de "sin conexión" al iniciar el video.
3. Pantalla a 1280×720 o más; cierra pestañas y notificaciones; zoom del navegador al 100–110%.
4. Ten a mano las 3 preguntas de la escena 4 para pegarlas.

Si algo falla durante la grabación: detén, corrige y **vuelve a grabar la escena completa**. No cortes a mitad de una respuesta.

## Escenas

| # | Tiempo | Pantalla | Qué hacer | Qué decir (resumen) |
|---|---|---|---|---|
| 0 | 0:00–0:15 | Escritorio | Mostrar wifi apagado | "Todo lo que van a ver corre en esta laptop, sin internet. Los datos son un snapshot público congelado: 187 señales del 2 de octubre de 2025 al 30 de septiembre de 2026." |
| 1 | 0:15–0:50 | **Sala de Situación** | Recorrer la agenda de la mañana (top 5) y la matriz | "187 señales se agrupan en 165 eventos. Cada evento tiene **prioridad** (0–100, explicable) y, por separado, **estado de evidencia**. Que algo sea urgente no lo vuelve cierto." Señalar que el top está en *parcial* o *insuficiente*: "ninguno llega a 'suficiente': el corpus son solo titulares y no inventamos confirmaciones." |
| 2 | 0:50–1:50 | **Ficha** de EVT-0101 (Canal: 33 cupos diarios) | Pestañas: Evento → Fuentes (Source DNA) → Evidencia → Vacíos | "La prioridad se descompone en R, I, U, N y E con su regla. Source DNA cuenta procedencias, no titulares: si cinco medios copian a una agencia, es una sola fuente. La evidencia oficial de la ACP aparece **con su fecha** (nivel de Gatún del 29/09) y como contexto: no confirma el titular. Y aquí está lo que **no** sabemos y a quién verificar." |
| 3 | 1:50–2:30 | **Ficha** de EVT-0078 (Canal reduce el tránsito por El Niño) | Pestañas Fuentes → Evidencia → Vacíos | "Dos medios distintos publican la historia, pero SCAYL no puede demostrar que sean independientes: dos titulares no son dos confirmaciones. El dato oficial de la ACP (Gatún, 84,0 pies) lleva su fecha, 4 de septiembre, y el del Banco Mundial se marca como histórico, de 2024. El contexto oficial no confirma el titular: por eso el estado es *parcial* y aquí está qué falta verificar." |
| 4 | 2:30–3:20 | **Consultas** | Pegar, una por una: (a) "¿Cuál es el nivel actual del lago Gatún?" (b) "¿Cuál es la moneda oficial de Panamá?" (c) "¿La inflación de Panamá fue 12% en 2024?" | (a) "Responde con la última medición **y su fecha**, citada." (b) "Se abstiene: no está en el corpus. No responde de memoria." (c) "La cifra de la pregunta no aparece en la evidencia: se abstiene en vez de confirmarla o inventar otra." |
| 5 | 3:20–3:50 | **Ficha → Producir y Revisión** (EVT-0101) | Mostrar el borrador con etiquetas HECHO/DECLARACIÓN y citas; aprobar **como borrador** con nombre y justificación; descargar el recibo | "El borrador lo generó un modelo local (qwen3:8b), validado por código: cada frase lleva su cita. La IA no publica: un editor aprueba **como borrador**, con justificación, y queda un recibo." |
| 6 | 3:50–4:15 | **Trust Lab** | Recorrer métricas | "442 pruebas automatizadas aprobadas. El red-team de desarrollo obtuvo 16/16 abstenciones correctas; el set humano reservado, 6/6 trampas. Las 45 frases evaluadas llevan cita. La generación local registró 13,1 segundos de mediana; Gemini externo opcional tiene cuota y costo sujetos al proyecto. Cada métrica conserva su alcance." |
| 7 | 4:15–4:30 | **Simulador de pesos** | Mover un peso y ver el nuevo orden | "Un editor puede probar otros pesos; el ranking oficial no cambia sin autor y justificación." Cierre: "SCAYL no decide qué se publica: acorta el camino de la señal a una historia investigable y trazable." |

## Evidencia y control de calidad
Los casos del recorrido conservan las fechas y procedencias de sus fuentes. La detección de contradicciones se evalúa además con T05 sobre casos sintéticos identificados como tales. Registro técnico: [control de agrupación](EVT0114_FALSE_CONFLICT.md) y [pruebas y métricas](notion_mirror/06_TESTS_AND_METRICS.md).

## Cuidados
- No muestres datos personales, pestañas ajenas ni la contraseña del Space.
- No digas "verdadero" ni "confirmado" si la pantalla dice *parcial*.
- Si el número de un evento cambia (por ejemplo, tras regenerar el bundle), busca el caso por su titular.
- Duración meta: 4–5 min. Exporta en MP4 1080p o 720p.

## Variante web de 3 minutos (jurado en vivo)
Para la web desplegada (https://scayl-editorial.vercel.app/), sigue el recorrido de `docs/D_UX_AUDIT.md` §2:
Sala → EVT-0101 (puntaje y evidencia ACP fechada) → EVT-0078 (procedencia no demostrable, ACP fechada, dato histórico y vacíos) →
EVT-0101 Producir (cabecera «IA local precalculada · no es inferencia en vivo») → Consultas «Sin respuesta» →
EVT-0101 Revisión («aprobado como borrador · NO publicado» y recibo). Todos los casos son reales; el snapshot no
tiene eventos sintéticos.
