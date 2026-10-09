# SCAYL — correcciones Notion verificadas

Fecha UTC: 2026-10-09T03:59:40Z (2026-10-08 22:59 Panamá).
Herramienta: Notion connector, update_content dirigido; read-back fetch posterior.
No se cambiaron permisos, publicación, imágenes, corpus ni otras páginas.

## ⚙️ Documentación técnica

URL: https://www.notion.so/3f36d0f0b11481e5a2d9e50ea351c61a
Última edición verificada: 2026-10-09T03:59:37.291Z

Antes:
Consulta libre y revisión en modo caché; sin claves ni costo

Después:
Consulta con evidencia y revisión; Gemini externo opcional con clave solo en servidor. Cuota y costo sujetos al proyecto de Google.

Antes:
- Inferencia 100 % local: ningún dato de la redacción sale a un tercero.

Después:
- Qwen3 8B se ejecuta localmente; la web sirve sus respuestas guardadas, que no son inferencia en vivo. Gemini es un proveedor externo opcional: se envían a Google la pregunta y hasta 8 extractos de evidencia pública. Su cuota y costo dependen del proyecto; no introducir datos personales.

Antes:
Parámetros del LLM: temperatura 0, semilla 42, salida JSON con esquema. Prompts versionados en `scayl/gen/prompts/*.vN.md`.

Después:
Parámetros de Qwen local: temperatura 0, semilla 42, salida JSON con esquema. Prompts versionados en `scayl/gen/prompts/*.vN.md`.
### Consultas y verificador en la versión pública
- **Consulta con evidencia:** recuperación BM25 y respuesta extractiva citada; funciona independientemente de Gemini. Las respuestas guardadas se identifican como precalculadas.
- **Gemini opcional:** proveedor externo elegido por el usuario; recibe la pregunta y hasta 8 extractos públicos. La salida JSON pasa por validadores de citas y cifras; ante falta de evidencia o inyección, el sistema se abstiene antes de llamar al proveedor. Cuota y costo sujetos al proyecto de Google.
- **Verificador:** recuperación y comparación deterministas de cifra, indicador, país, período y unidad; no usa IA generativa. «Compatible» no significa verdadero, confirmado ni listo para publicar.

Read-back: contiene Gemini y verificador, no contiene las tres afirmaciones engañosas auditadas.

## 🎤 Presentación Pitch Day

URL: https://www.notion.so/3f36d0f0b11481e08c92e5440b11d9f6
Última edición verificada: 2026-10-09T03:59:39.682Z

Antes:
cero dólares de API (sin contar hardware ni electricidad) y ningún dato sale de la redacción.

Después:
sin costo de API para esa ejecución local (hardware y electricidad excluidos). Las respuestas guardadas de la web no son inferencia en vivo. El modo opcional Gemini usa un proveedor externo: envía la pregunta y hasta 8 extractos públicos, con cuota y costo sujetos al proyecto de Google.

Antes:
\$0 de API: todo corre local. El hardware y la electricidad no están incluidos ni medidos. El ahorro de tiempo no está medido, así que no lo afirmamos.

Después:
Qwen local no genera cargos de API; hardware y electricidad están excluidos. Gemini es externo y opcional: su cuota y costo dependen del proyecto de Google. El ahorro de tiempo no está medido, así que no lo afirmamos.

Antes:
## Preguntas preparadas

Después:
## Funciones actuales para la demo
- **Consultas:** «Consulta con evidencia» funciona sin Gemini. El modo opcional «IA generativa en vivo (Gemini)» envía la pregunta y hasta 8 extractos públicos a Google; muestra el modo real y valida citas y cifras. Cuota y costo sujetos al proyecto.
- **Verificar:** compara determinísticamente cifra, indicador, país, período y unidad; no usa IA generativa. «Compatible» no significa verdadero ni listo para publicar.
- **Respaldo:** usar la demo local o el recorrido web con EVT-0078. No usar el video antiguo: contiene el sismo de 7.4 agrupado erróneamente en EVT-0114.
## Preguntas preparadas

Read-back: contiene Gemini y verificador, no contiene las tres afirmaciones engañosas auditadas.

## Página del equipo

https://www.notion.so/3f36d0f0b11481188e1ae1f61304fe7d
Fetch actual no contiene video ni recomendación plan B, por lo que no se modificó.

Nota: las imágenes existentes de las diapositivas se preservaron; esta corrección actualiza el guion y añade aclaración visible de funciones y límites.


## Publicación autorizada y acceso (2026-10-09 04:13 UTC / 23:13 Panamá)

La persona autorizó explícitamente: «Sí, publica las cuatro páginas propias de SCAYL».
La página del equipo se publicó desde Compartir → Publicar. Las tres páginas hijas muestran por herencia «Deshacer / Ver sitio», es decir, publicadas.
Antes de publicación, todas estaban compartidas con Todos en hackIAthon 4taEd (54 miembros de espacio de equipo, acceso completo).
URLs reales:
- https://conscious-handbell-91a.notion.site/SCAYL-Sala-de-Inteligencia-Editorial-3f36d0f0b11481188e1ae1f61304fe7d
- https://conscious-handbell-91a.notion.site/Documentaci-n-t-cnica-3f36d0f0b11481e5a2d9e50ea351c61a
- https://conscious-handbell-91a.notion.site/Documentaci-n-funcional-3f36d0f0b11481f3a6dcd472e557e6e9
- https://conscious-handbell-91a.notion.site/Presentaci-n-Pitch-Day-3f36d0f0b11481e08c92e5440b11d9f6
Las cuatro renderizan en la vista pública Chrome, con «Comienza ahora» y sin formulario de acceso. Técnica y Pitch incluyen las correcciones tras hidratación; funcional contiene Gemini/Verificar.
HTTP anónimo Python obtuvo 403 (bloqueo automatizado de Notion); no se afirma HTTP200. Browser IAB dejó de estar disponible tras selección de Chrome; comprobación adicional en sesión totalmente limpia pendiente del agente raíz si su IAB funciona.
/tmp/scayl-correo-final.txt actualizado con los cuatro enlaces públicos reales. Correo no enviado.
