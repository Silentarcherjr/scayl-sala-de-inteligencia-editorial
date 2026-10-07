# A-06 · Preparación local del Space (sin publicar)

AP-001 aceptada; publicación pendiente de confirmación del Lead. No se creó Space ni se usaron
credenciales HF. El acceso se cierra si falta `SCAYL_SPACE_PASSWORD`; ese valor será un **Secret**
de runtime del Space, nunca un archivo, argumento Docker o variable pública.

```bash
make public-bundle
python -m deploy.prepare --out deploy/stage
```

Windows sin make (equivalente exacto de la receta):

```powershell
$env:Path = "$PWD\.venv\Scripts;$env:Path"
$env:SCAYL_INTEL = 'baseline'
python -m scayl.pipeline build --snapshot data/raw/v1 --llm cache --top 15 --public
python -m deploy.prepare --out deploy/stage
```

`deploy/stage/` está ignorado por Git. Es el contexto Docker y futuro repositorio del Space:
README con `sdk: docker`, puerto 7860, Dockerfile, dependencias fijadas existentes, app, núcleo,
bundle público, evaluación y `data/cache/llm/`. El script rechaza destino existente para no borrar
trabajo; una nueva preparación usa otra carpeta. No copia `.env`, raw, etiquetas, revisiones, modelos
ni cachés Python. Conserva hashes de todos los archivos en `PREPARATION.json` (`published: false`).

Comprueba que no hay `news.descripcion`, ninguna cita a `descripcion`, ni decisiones de revisión.
**Caché precalculada:** esta máquina no tiene entradas LLM. La carpeta se incluye vacía; los 183
paquetes de esta preparación son template. Antes de una demo con IA precalculada, el dueño de B-10
debe aportar caché pública revisada y repetir build/preparación. No renombrar template a cache.
`--public` borra descripciones de news, pero no reconstruye cachés antiguas: no incluir entradas
derivadas de RSS privado. El inspector estructural no detecta paráfrasis; revisar esa procedencia.

La entrada `app/space.py` autentica antes de ejecutar páginas. También se generan envoltorios para
Home y cada página: un enlace directo exige contraseña. El adaptador de hosting fuerza cache incluso
si alguien solicita live; Consultas ofrece solo cache. Las salidas conservan su modo real y fallback.
La rotación/eliminación del Secret revoca sesiones; cerrar sesión limpia preguntas y resultados.
El estado de revisión es efímero, anunciado en la interfaz; reiniciar el contenedor lo pierde.

Verificación local tras preparar: con un Secret efímero en el entorno (sin escribirlo en capturas),
desde stage ejecutar `python -m streamlit run app/space.py --server.port 7860` con `PYTHONPATH` al stage
y `SCAYL_HOSTED=1`. Para Docker, `docker build -t scayl-space deploy/stage` y suministrar el Secret
solo al ejecutar. En esta sesión **el motor Docker no está activo**: build/container no medidos.
AppTest cubre acceso cerrado, contraseña incorrecta/correcta, rotación, rutas directas y cache forzada;
capturas Chromium verifican el artefacto local. No equivalen a despliegue HF probado.

Después de confirmación del Lead: crear Space Docker **privado** (la contraseña de la app no protege
archivos de un repositorio público), configurar el Secret, subir solo el stage auditado, comprobar
acceso del jurado y recorridos. Probar credenciales ausentes/incorrectas y enlaces directos antes de
compartir. A-06 no se declara desplegada hasta tener URL y comprobación remota.

Referencia: [Docker Spaces: puerto, UID 1000 y secrets de runtime](https://huggingface.co/docs/hub/spaces-sdks-docker).

Preparación comprobada de esta sesión: `deploy/stage-final/` (ignorado), inventario y hashes en
`deploy/preparation-report.json`. `deploy/stage/` conserva una preparación anterior; no usarla para
publicar. Se conserva porque la revisión automática bloqueó su limpieza. Para reconstruir, elegir
una carpeta nueva y regenerar inventario/capturas. La prueba de Chromium verificó login por URL
`/Trust_Lab`, lectura de métricas y cierre de sesión; no abrió conexión con HF.

## Backlog final · 2026-10-07
Nueva preparación desde dc1a990 (AP-013 y evidencia ACP/INEC): `deploy/stage-backlog-final/`, solo local.
Estado medido en `deploy/readiness-backlog.json`:187 señales,183 eventos,0 descripciones RSS,0 entradas
cache y183 paquetes template. Es preparación funcional con fallbacks, no prueba de precálculo LLM.
No existe data/cache/llm en este checkout. Se pidió al humano solo la ruta/PR de la caché pública revisada.
Motor Docker aún inactivo; build y HF no medidos. Volver al final del backlog; si sigue sin caché, mantener
bloqueado. No pedir confirmación de publicación antes de recibir/auditar caché y probar el contenedor.
La contraseña y URL se entregarán por canal privado después de confirmación del Lead, nunca en el PR.
