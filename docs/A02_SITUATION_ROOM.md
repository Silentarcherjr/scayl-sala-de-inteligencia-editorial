# Sala de Situación · A-01/A-02

Ejecutar desde la raíz, con el entorno de dependencias activado:

```powershell
python -m streamlit run app/Home.py
```

La navegación nativa de Streamlit descubre Ficha de Caso, Consultas, Trust Lab y Simulador de pesos.
Consultas es una página provisional explícita hasta el bloque A-04/A-09. Las otras páginas usan las
implementaciones existentes; no se modifican A-05 ni A-10. `app/service_client.py` reexporta las
operaciones básicas del servicio canónico, sin caché ni datos alternativos.

Home lee `scayl.service.load_bundle()`. Presenta el embudo global señales recibidas → válidas →
eventos → hasta cinco casos, el corte en Panamá y el snapshot. Las filas están ordenadas por P
descendente, U descendente e ID ascendente. P se conserva tal como viene en el bundle.

La tabla incluye publicación y detección por separado, nulos explícitos, procedencia, conflicto y
acción recomendada. Tiene desplazamiento horizontal para acceder a todas las columnas a 1280×720.
Los filtros de tema y evidencia actualizan las filas, los detalles y la matriz completa de nueve celdas;
los conteos del embudo conservan los totales del snapshot. Sin coincidencias se muestra un aviso.

Cada detalle separa las insignias de atención y evidencia, identifica casos sintéticos y muestra
contribuciones R/I/U/N/E según los pesos oficiales del servicio. Incluye las explicaciones de cada
componente, la frase de procedencia y la advertencia de que prioridad alta no habilita publicación.
Los enlaces **Abrir ficha** incluyen `event_id`; se verificó que EVT-0003 abre sus seis pestañas.

Validación: **95 pruebas pasando**, seis nuevas para Home, la página provisional y el cliente del
servicio con almacenamiento SQLite temporal aislado. Chromium a 1280×720 con fixture sintético;
no se expuso ranking real al editor. H-08 sigue pendiente: aún no existe editor_candidates.csv.

Capturas: [Home](screenshots/a02-sala.png), [componentes y evidencia](screenshots/a02-componentes.png).

Siguiente bloque: A-07, componente Agenda de la mañana montado en la parte superior de Home.
