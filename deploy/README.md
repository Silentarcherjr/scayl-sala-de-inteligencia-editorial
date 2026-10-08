# A-06 · Publicación

> **Actualización 2026-10-08 (cierre):** la URL de Streamlit Community Cloud redirige a inicio de sesión y se retiró de los enlaces de entrega; la demo pública es https://scayl-editorial.vercel.app/ y el respaldo es la app Streamlit local (`scripts/demo_offline.py`).
>
> **Estado anterior: DESPLEGADA** en https://scayl-demo.streamlit.app/ (Streamlit Community Cloud, modo cache). **Acceso abierto desde DL-033**: `SCAYL_PUBLIC_ACCESS = "1"` en los Secrets de Streamlit; sin ese interruptor la app vuelve a exigir `SCAYL_SPACE_PASSWORD` y se cierra si falta. Verificación remota más abajo.

## Ruta vigente: Streamlit Community Cloud (DL-032)
Hugging Face exige PRO (pago) para Spaces Docker o Gradio, así que se publica gratis en Streamlit Community Cloud.

1. Genera el stage auditado en una carpeta nueva:
   `python -m deploy.prepare --bundle deploy/artifacts/v1/bundle.public.json --cache deploy/artifacts/v1/llm --out deploy/stage-cloud`
2. Sube **solo el contenido del stage** a un repositorio GitHub dedicado (p. ej. `scayl-demo`). No subas el repo de trabajo: el stage no tiene `.env`, raw, etiquetas ni estado.
3. En share.streamlit.io: *Create app* → repo dedicado, rama `main`, archivo principal **`app/space.py`**. En *Advanced settings*: **Python 3.12**. En *Secrets*: `SCAYL_PUBLIC_ACCESS = "1"` para acceso abierto (DL-033), o `SCAYL_SPACE_PASSWORD = "<contraseña>"` para exigir contraseña. La contraseña la escribe un humano; nunca va a Git.
4. `app/space.py` se configura solo: agrega la raíz del stage a `sys.path` y fija por defecto modo cache, `SCAYL_HOSTED=1` y las rutas de datos del stage. No hace falta ninguna otra variable.
5. Verifica en remoto: sin contraseña no entra, una contraseña incorrecta se rechaza, y con la correcta cargan Sala, Ficha, Consultas y Trust Lab.
6. **Tras publicar cambios en `deploy/space.py` o `deploy/runtime.py`, haz *Reboot app* en share.streamlit.io.** Streamlit solo recarga lo que está bajo `app/`; los módulos de `deploy/` quedan en caché y la app mezcla versiones (visto en DL-033: sidebar visible pero páginas bloqueadas).
7. Al sincronizar `scayl-demo`, conserva los archivos que no vienen del stage (p. ej. `.devcontainer/`, que crea Streamlit).

Probado en local (DL-032): stage sin `PYTHONPATH` ni otras variables, solo la contraseña → acceso pedido, autenticación correcta, Sala en modo cache.

**Publicado:** https://scayl-demo.streamlit.app/ desde el repo público [`Silentarcherjr/scayl-demo`](https://github.com/Silentarcherjr/scayl-demo) (`main` = `f4c7de1`), stage `deploy/stage-cloud` generado desde `ff3a7c2`; solo los 118 archivos inventariados en `PREPARATION.json`, con hashes verificados. Python 3.12; contraseña solo en Secrets de Streamlit.
Verificación remota (2026-10-07): `/` y `/Trust_Lab` piden contraseña; una contraseña incorrecta se rechaza. El recorrido autenticado remoto lo confirmó el Humano 1 en la URL pública: con la contraseña correcta cargan las vistas. El agente no conoce la contraseña. En local, con la correcta, cargaron Sala, Ficha, Consultas y Trust Lab sin excepciones.

**Para republicar** (si cambian código o datos de la demo): regenera el stage en una carpeta **nueva** y pruébalo. Después sube a `scayl-demo` **solo** los archivos inventariados en `PREPARATION.json` más ese archivo: las pruebas locales dejan `__pycache__/` y `data/state/reviews.sqlite` dentro del stage, y no deben publicarse. Nunca se edita `scayl-demo` a mano.

## Preparación original para HF Space Docker (requiere PRO; no se usa)


**Estado vigente tras PR #51:** [stage con caché pública probado localmente](HUMAN_INPUTS_READINESS.md).
`deploy/stage-human-reviewed/` contiene 30 entradas revisadas y la evaluación B-09 completa.
(Histórico: este stage no se publicó; la entrega usa Streamlit Cloud, ver arriba.) Las preparaciones sin caché descritas abajo
son históricas y no deben usarse para la entrega actual.

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
(Histórico.) La contraseña se entrega por canal privado, nunca en un PR; la URL vigente está arriba.
