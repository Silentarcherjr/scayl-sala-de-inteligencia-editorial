# Documentación funcional

## 1. Problema

Un equipo editorial recibe cientos de señales al día. **Que varios medios repitan una noticia no la confirma**, y **un dato viejo puede parecer nuevo**. Preparar una pieza con evidencia trazable toma tiempo, y los errores de contexto cuestan credibilidad.

## 2. Usuarios

| Usuario | Qué necesita | Qué le da SCAYL |
|---|---|---|
| **Editor/a de TVN** (principal) | Decidir qué investigar hoy | Agenda priorizada con motivos, estado de evidencia y acción sugerida |
| **Periodista** | Investigar un tema sin errores de contexto | Ficha con fuentes, cifras oficiales fechadas, conflictos y vacíos |
| **Productor/a digital** | Preparar piezas rápido | Borrador con título, brief, guion y copy social, todo citado |
| **Analista bancario** (extensión) | Contexto sectorial | Boletín de entorno con observaciones e hipótesis separadas |

## 3. Flujo principal

**Señal → evento → prioridad → evidencia → vacíos → borrador citado → decisión humana**

1. **Cargar y organizar:** 187 señales públicas se validan y se agrupan en **165 eventos**.
2. **Priorizar:** cada evento recibe un puntaje de atención P con sus cinco componentes y la regla de cada uno.
3. **Contextualizar:** se vinculan datos oficiales (ACP, INEC, Banco Mundial, USGS) con su fecha.
4. **Explicar:** qué se reporta, qué está respaldado, qué falta verificar y a quién preguntar.
5. **Producir:** un borrador donde cada frase está etiquetada (HECHO, DECLARACIÓN…) y citada.
6. **Revisar:** una persona cambia el estado con justificación obligatoria y recibe un recibo con hash SHA-256 (integridad del contenido; no es una firma).

## 4. Pantallas

### Empieza aquí
Recorrido guiado de unos 3 minutos para quien llega por primera vez.

![Empieza aquí](img/jury-inicio-desktop.png)

### Sala de Situación
Indicadores del snapshot, **Agenda de la mañana** (top 5 con motivos y acción) y tabla filtrable por tema y estado de evidencia, con la matriz Prioridad × Evidencia.

![Sala de Situación](img/01-sala.png)

### Ficha de Caso
Resumen "Qué puedes hacer con este caso", desglose de P y pestañas: Evento, Fuentes (Source DNA), Evidencia, Afirmaciones, Conflictos, Vacíos, Producir y Revisión.

![Ficha de Caso](img/jury-ficha-desktop.png)

### Consultas
Preguntas libres en español respondidas solo con evidencia del corpus, citada, o con **abstención explícita** si falta evidencia. Incluye el Modo jurado con preguntas preparadas.

![Consultas](img/jury-consultas-desktop.png)

### Revisión humana
Cinco estados (nuevo → en revisión → requiere evidencia / aprobado como borrador / descartado). Justificación obligatoria y recibo con hash. **Aprobado como borrador NO significa publicado.**

![Revisión](img/python-api-review-desktop.png)

### Pruebas y métricas (Trust Lab)
Las pruebas T01–T10, las métricas con numerador y denominador, y lo que no se midió.

![Pruebas y métricas](img/jury-metricas-desktop.png)

### Boletín (extensión bancaria)
Boletín de entorno logístico (CU-05) con observaciones citadas, hipótesis separadas y tres preguntas para el analista. Se puede imprimir o guardar como PDF.

![Boletín](img/bank-logistica_canal-desktop.png)

## 5. Casos de uso del reto

| Caso | Cómo lo resuelve SCAYL | Dónde verlo |
|---|---|---|
| **CU-01** ¿Qué cinco temas merecen revisión hoy y por qué? | Agenda de la mañana con P, motivos, evidencia y vacíos | Sala de Situación |
| **CU-02** Tema económico con serie oficial, sin confundir histórico con actual | Temporal Guard: "Dato histórico — 2024" | Ficha · Evidencia |
| **CU-03** Repetición frente a corroboración | Source DNA: una agencia replicada cuenta como una procedencia | Ficha · Fuentes |
| **CU-04** Cifra inexistente o contradicción | Abstención con motivo, o ambas versiones visibles (titular 4.7 frente a USGS 4.5) | Consultas · Ficha · Conflictos |
| **CU-05** Señales del entorno logístico para un banco | Boletín de entorno sectorial | Boletín (banca) |

## 6. Reglas de producto

- **La prioridad no es verdad:** P mide atención; el estado de evidencia es independiente.
- **N publicaciones ≠ N confirmaciones.**
- **La IA no publica:** "aprobado como borrador" no significa publicado.
- **Si no hay evidencia, se abstiene:** no responde de memoria.
- **Lo que no se midió se dice "no medido".**

## 7. Límites (declarados)

- Solo titulares y metadatos: ningún evento real llega a "suficiente para borrador", porque ningún titular cita una cifra oficial comparable. Es el comportamiento correcto.
- La independencia entre medios casi nunca es demostrable con metadatos; el sistema lo declara.
- Snapshot congelado, no monitoreo en tiempo real.
- La revisión de la demo pública se guarda en el navegador de quien la usa.
- El boletín bancario es una plantilla, sin IA generativa.

## 8. Cómo probarlo

1. Abre https://scayl-editorial.vercel.app/ y entra a **Empieza aquí**.
2. En **Consultas**, prueba "¿Qué pasa con el Canal de Panamá y El Niño?" (responde con citas) y "¿Cuántos turistas llegarán a Panamá en 2035?" (se abstiene).
3. Abre una ficha, revisa **Fuentes** y **Evidencia**, y registra una revisión.
