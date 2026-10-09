# Modo opcional "IA online en vivo" (Gemini) para Preguntas y respuestas

**Estado:** implementado y probado solo con HTTP simulado (sin clave real). **Apagado por defecto.** Si no se
configuran las variables de entorno, SCAYL se comporta exactamente igual que antes (respuestas guardadas /
plantilla). Requiere aprobación humana explícita antes de activarse con una clave real (AGENTS.md §4: sin APIs
pagas sin aprobación).

## Diseño

- `scayl/gen/llm.py`: `GeminiBackend`, misma interfaz que `OllamaBackend` (`chat_json`). Llama a
  `https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent` con
  `responseMimeType: application/json` + `responseSchema` (el esquema JSON de Q&A convertido al subconjunto de
  Gemini), `temperature: 0`, `maxOutputTokens: 600`, tiempo de espera de 12 s. Usa solo la biblioteca estándar
  (`urllib`): `requests` no forma parte del runtime Python de Vercel y no se añaden dependencias.
- Nuevo modo `online` en `LLM` (`live` = Ollama local, `cache` y `template` sin cambios). En modo `online`
  **no se lee ni se escribe la caché compartida de la demo**. `GenerationMeta.mode = "online"`,
  `model = "gemini:<modelo>"`; `params.cost_usd = "no medido"` (el campo `cost_usd = 0.0` no significa gratis).
- Errores del proveedor (sin clave, red, tiempo agotado, HTTP ≠ 200, salida no JSON) se mapean a
  `LLMUnavailable`/`LLMError`, y Q&A vuelve a la respuesta extractiva actual con la observación visible
  `ONLINE_FALLBACK` en la validación.
- `scayl/gen/qa.py`: el proveedor se llama **solo** después de que la recuperación y el pre-guard determinista
  encontraron evidencia suficiente. Nunca se llama si la pregunta contiene instrucciones (inyección), si falta
  evidencia, si el período no existe, si la cifra planteada no está en la evidencia o si se pide un dato actual con
  solo datos históricos. La salida pasa por los mismos validadores que con Ollama (citas inexistentes, cifras fuera
  de la evidencia, temporalidad, eco de inyección); si nada sobrevive, el sistema se abstiene.
- UI: etiqueta "IA online en vivo · proveedor externo (Gemini)" en `web/components/shared.tsx`.

## Privacidad: qué se envía a Google

Solo: la pregunta (truncada a 300 caracteres) y hasta 8 unidades de evidencia **pública** recuperadas
(`evidence_id`, extracto de texto ≤ 400 caracteres, período, si es oficial), dentro del bloque
`DATOS_NO_CONFIABLES`, más las instrucciones del prompt `qa.v1`. No se envían cuerpos de artículos, datos de
revisores, registros de revisión ni el set reservado del jurado. La clave se lee de `GEMINI_API_KEY`, se envía solo
en la cabecera `x-goog-api-key` (nunca en la URL), no se registra en logs y no se devuelve en ninguna respuesta. La
pregunta tampoco se registra (`log_message` del handler está silenciado).

## Control de acceso y límites (web/api/ask)

El modo online se usa **solo si** se cumplen todas:

1. `GEMINI_API_KEY` configurada en el servidor;
2. `SCAYL_LIVE_ACCESS_CODE` configurada en el servidor;
3. el JSON de la solicitud trae `"mode": "online"` y `"access_code"` igual al código (comparación en tiempo
   constante).

En cualquier otro caso se ignora y se responde como siempre (caché pública). `"mode": "live"` sigue rechazado
(422). Guarda adicional: tope de llamadas al proveedor por instancia (`SCAYL_LIVE_MAX_CALLS`, por defecto 50);
al agotarse, respuesta extractiva con `ONLINE_FALLBACK`. Es un contador en memoria por instancia serverless: **no
es un límite de gasto**.

## Cómo activarlo (Vercel → Project → Settings → Environment Variables)

| Variable | Obligatoria | Valor |
|---|---|---|
| `GEMINI_API_KEY` | sí | clave de Google AI Studio (nunca en el repositorio) |
| `SCAYL_LIVE_ACCESS_CODE` | sí | código compartido solo con quien deba probar |
| `SCAYL_GEMINI_MODEL` | no | por defecto `gemini-2.5-flash-lite` |
| `SCAYL_LIVE_MAX_CALLS` | no | por defecto `50` (por instancia) |

Luego redeploy. Prueba: `POST /api/ask` con `{"question": "...", "mode": "online", "access_code": "..."}`.
La interfaz actual no tiene campo para el código; la etiqueta de modo sí reconoce `online`.

## Tope de costo

El tope real de gasto **debe** fijarse fuera de la app: en Google AI Studio (límites de uso / cuota del proyecto) y
en Google Cloud Billing (presupuesto con alertas, o usar el nivel gratuito sin facturación activada). El contador
por instancia es solo una guarda extra. El costo por llamada **no se mide** en SCAYL ("no medido").

## Inferencia local vs. externa

- `live` (Ollama): modelo abierto local; los datos no salen de la máquina.
- `online` (Gemini): proveedor externo; la pregunta y extractos públicos salen hacia Google. Etiquetado
  explícitamente en la UI y en `generated_by`. Las respuestas del jurado guardadas (caché) no cambian y nunca se
  mezclan con salidas online.
