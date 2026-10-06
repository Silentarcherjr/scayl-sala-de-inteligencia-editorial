# 07 · Riesgos y ética

| Área | Riesgo | Control |
|---|---|---|
| Privacidad | Nombres de personas en titulares | Solo se almacenan los titulares públicos; sin perfiles ni listas de personas; entidades solo como texto del titular. |
| Reputación | Acusaciones presentadas como hecho | Las acusaciones se etiquetan como DECLARACIÓN con atribución; validador `STATUS_MISMATCH`. |
| Derechos | Redistribuir artículos, imágenes o videos | Solo titular + URL + metadatos; descripciones RSS solo localmente; el despliegue tiene acceso restringido; condiciones por fuente en el catálogo. |
| Sesgos | Sobrerrepresentación de medios extranjeros (GDELT) o de un tema | Mostrar la distribución por medio y tema; Source DNA evita el efecto volumen; los pesos de impacto por tema son explícitos y justificables. |
| Ataques al agente | Inyección en el texto de una fuente | Delimitación como dato, guard de patrones, LLM sin herramientas ni secretos, esquema JSON + validadores (T07). |
| Alucinación | Cifras, citas o entrevistas inventadas | Generación claim-first + validador numérico + abstención (T06, T09). |
| Temporalidad | Dato histórico como actual | Temporal Guard + validador `TEMPORAL_PRESENT` (T04). |
| Automatización | Publicar sin control | Sin función de publicación; 5 estados; "aprobado como borrador" ≠ publicado. |
| Secretos | Tokens en código, logs o capturas | `.env` ignorado, `.env.example` vacío, escaneo antes de la entrega. |
| Costo | APIs pagas | Inferencia 100% local; costo de API $0. |

**Fuera de alcance (declarado):** detección de fake news, culpabilidad, audiencia, datos personales de clientes, contenido tras paywall, publicación automática y modalidad bancaria.
