# A-03 · Ficha de Caso

Estado: implementada y probada con datos sintéticos; **integración pendiente de A-08 / AP-011**.
No cerrar A-03 todavía. La página conserva y completa el archivo local que existía sin seguimiento.

Ejecutar desde la raíz del repositorio, con el entorno de dependencias activado:

```powershell
python -m streamlit run app/pages/1_Ficha_de_Caso.py
```

La página usa exclusivamente `scayl.service` y los contratos. Acepta `?event_id=EVT-0002`
y permite seleccionar otro caso. Si no hay bundle procesado, el servicio carga el fixture
sintético; un bundle vacío muestra un aviso. No se debe mostrar un ranking real al editor
antes de que entregue H-08. En esta ejecución aún no existe `editor_candidates.csv`.

- **Evento:** titulares de `bundle.news` filtrados por `member_ids`, fechas de publicación y
  detección separadas en America/Panama, entidades, recirculación, alcance y componentes de P.
- **Fuentes:** grupos, motivos y declaración literal de procedencia; publicaciones e independencia
  se muestran por separado.
- **Evidencia:** afirmaciones, referencias completas, advertencias temporales y versiones A/B del
  conflicto lado a lado, sin seleccionar una cifra ganadora.
- **Vacíos:** los cinco bloques de investigación; lo ausente aparece como no disponible.
- **Producir:** paquete, etiquetas por oración, desplegables de afirmaciones y citas, validación,
  modo/modelo/prompt, latencia y tokens (ausentes: no medido). Generar usa el modo del servicio.
- **Revisión:** estados permitidos, revisor y justificación obligatorios, historial y hash de evidencia.
  Se revalida la transición al enviar y se presentan los errores del servicio.

El paquete generado queda en la sesión por snapshot/caso. Como el servicio actual registra solo
el paquete del snapshot, guardar una revisión queda deshabilitado si difiere del visible. El botón
**Volver al paquete del snapshot** permite revisar el paquete identificado en Revisión. Aprobar
como borrador no publica contenido.

La tarjeta compartida A-08 no existe todavía en main. `show_refs()` es un adaptador temporal que
expone `EvidenceRef` completo en JSON; no es una implementación alternativa de la tarjeta.
AP-011 pide su ruta de importación, la persistencia del paquete revisado y una API para descargar
el recibo. No se modificaron contratos, servicio, dependencias ni archivos de frictionspp-svg.

Validación: `python -m pytest -q` → **80 passed**, incluidos 9 casos AppTest de
`tests/ui/test_case_page.py`. Ejecución local: Python 3.14.7, Streamlit 1.65.0, entorno `.venv` ya
existente (no se cambiaron versiones fijadas). No se verificó visualmente en navegador ni se midió
con datos reales/modelo local. No hay capturas de navegador; los AppTest verifican el árbol de UI.
