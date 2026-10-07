# A-03 · Ficha de Caso

Estado: A-03 y A-08 implementadas; listas para revisión del Lead en PR #13.
AP-011 aceptada y aplicada (DL-020). La navegación desde Home sigue en A-01/A-02.

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

El paquete generado queda en la sesión por snapshot/caso. Revisión pasa ese paquete visible a
`service.review(..., package=...)`; el recibo registra su id y sha256. El botón
**Volver al paquete del snapshot** permite volver al paquete original. Cada registro del historial
incluye el hash del recibo y su descarga JSON mediante `service.receipt()`. Un recibo ausente se
señala sin ocultar el historial. Aprobar como borrador no publica contenido.

La tarjeta compartida `app.components.evidence_card.evidence_card(ref)` se abre pulsando el valor
citado. Muestra id, tipo, campo, valor, período, URL y extracto, preservando nulos y el cero.
Los datos World Bank llevan advertencia histórica; otros períodos se muestran sin atribuirles
vigencia actual. La usan las afirmaciones, los conflictos y el paquete; está disponible para Consultas.
No se modificaron contratos, servicio, dependencias ni archivos de frictionspp-svg.

Validación: `python -m pytest -q` → **84 passed**, incluidos 12 casos AppTest en `tests/ui/`.
Se verifica el hash del paquete generado y revisado, la descarga disponible y los nulos de la tarjeta.
Entorno local existente: Python 3.14.7, Streamlit 1.65.0; no se cambiaron versiones fijadas.
Comprobación visual en Chromium a 1280×720 con fixture sintético, modo template y estado temporal
aislado: generación, revisión e historial. No se midieron datos reales ni modelo local.

Capturas: [tarjeta histórica](screenshots/a03-evidencia.png),
[conflictos lado a lado](screenshots/a03-conflictos.png),
[revisión del paquete generado y recibo](screenshots/a03-revision.png).
