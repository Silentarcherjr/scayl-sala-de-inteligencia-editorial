# Presentación · Pitch Day

> Para presentar: en Notion, activa **Ancho completo** y **Texto grande** (menú ··· arriba a la derecha) y avanza con la rueda del mouse. Cada bloque separado por una línea es una "diapositiva". Duración: 10 minutos más 5 de preguntas.

---

# SCAYL
## Sala de Inteligencia Editorial
**De la señal a la decisión** · hackIAthon Panamá · Reto TVN Media

---

# 1 · El problema · 1 min

Cada día una redacción recibe **cientos de señales**.

- Que varios medios repitan una noticia **no la confirma**.
- Un dato viejo **puede parecer nuevo**.
- Preparar una pieza con evidencia trazable **toma tiempo**.

El costo: tiempo y errores de contexto que dañan la credibilidad.

---

# 2 · La solución · 1 min

**SCAYL lleva una señal hasta una historia investigable:**

Señal → evento → prioridad → evidencia → vacíos → borrador citado → **decisión humana**

Dos reglas que no se negocian:
1. **La prioridad no es verdad.**
2. **La IA no publica.**

Datos públicos: noticias (GDELT y RSS de TVN), ACP, INEC, Banco Mundial y USGS, en un snapshot congelado con hash.

---

# 3 · Demo · 4 min

**https://scayl-editorial.vercel.app/**

1. **Sala de Situación:** 187 señales → 165 eventos priorizados.
2. **Ficha del Canal:** P = 89.9 con cada componente y su regla; datos de la ACP con fecha.
3. **Conflicto:** titular 4.7 frente a USGS 4.5. SCAYL no elige ni promedia: muestra ambas. *(Mencionarlo, pero no abrir en vivo la ficha EVT-0114: también muestra un sismo distinto de 7.4 agrupado por error; corrección en el PR #80, no publicada. Para la ficha en vivo, usar EVT-0078.)*
4. **Consulta:** el nivel del lago Gatún, con fecha y cita.
5. **Abstención:** "¿Cuál es la moneda oficial de Panamá?" → no está en la evidencia, no inventa.
6. **Borrador citado** → **aprobado como borrador**, con justificación y recibo.

![Sala de Situación](img/01-sala.png)

---

# 4 · IA medida, no por moda · 2 min

**Usamos IA donde ganó y reglas donde perdió.**

| Tarea | IA | Reglas | Usamos |
|---|---|---|---|
| Agrupar titulares | **E5: F1 0,99** (pares de calibración: optimista) | TF-IDF: 0,44 | IA |
| Clasificar temas | E5: 0,25 | **Reglas: 0,76** | Reglas |

**El borrador lo escribe un LLM local** (Qwen3 8B): mediana de 13 s, **$0** de API (sin contar hardware ni electricidad), esa inferencia es local. Consultas también ofrece Gemini externo opcional con pregunta y extractos públicos; cuota y costo dependen del proyecto. Verificar es determinista, sin IA generativa.

**Y lo vigila el código:** **45/45** frases conservadas con cita (cobertura, no validez del sustento); las frases sin cita o con cifras sin respaldo se eliminan antes de llegar al editor.

---

# 5 · Confianza: medido, no prometido · 1 min

- **T01–T10:** las 10 pruebas automatizadas del reto, aprobadas (T10 con la red bloqueada en pytest).
- **6/6** trampas con abstención correcta en un set escrito por un humano sin ver los casos existentes; también se abstuvo en las 4 preguntas de cultura general fuera del corpus (6/10 frente a sus expectativas).
- **25/30 = 83 %** de validez de sustento en revisión humana (muestra de paquetes plantilla): por debajo de la meta del 90 %, y lo decimos.
- Nuestro propio red-team nos encontró fallos (6/16); los corregimos y quedaron registrados.
- **Ahorro de tiempo: no medido.** No lo afirmamos.

![Pruebas y métricas](img/jury-metricas-desktop.png)

---

# 6 · El mismo núcleo, otro usuario · 30 s

**Extensión bancaria:** un boletín de entorno logístico para un analista sectorial.

Observaciones citadas · hipótesis separadas · tres preguntas para el analista.

Sin evaluar clientes, sin recomendar operaciones, sin inferir pérdidas.

---

# 7 · Límites y próximos pasos · 30 s

**Límites honestos**
- Hoy solo hay titulares: ningún caso real llega a "suficiente", y eso es lo correcto.
- La independencia entre medios casi nunca se puede demostrar con metadatos.

**Próximos pasos**
- Cuerpos de artículos con licencia de TVN.
- Más fuentes oficiales (SINAPROC, MEF).
- Snapshot diario con datos recientes y operación en la redacción.

---

# SCAYL no decide qué se publica.
## Acorta el camino de la **señal** a la **decisión**.

Demo: https://scayl-editorial.vercel.app/ · Código: https://github.com/Silentarcherjr/scayl-sala-de-inteligencia-editorial

---

## Preguntas preparadas

- **¿De dónde viene esta cifra?** → Tarjeta de evidencia: ID, campo, valor, período y URL.
- **Si cinco medios replican una agencia, ¿cuántas fuentes independientes hay?** → Una procedencia.
- **¿Qué pasa si no hay evidencia?** → Se abstiene y dice qué fuente faltaría.
- **¿Y si una fuente trae instrucciones maliciosas?** → Se marca como sospechosa; nunca se cita ni se envía al modelo.
- **¿Cuánto cuesta?** → $0 de API para Qwen local, excluyendo hardware y electricidad. Gemini es externo: cuota y costo sujetos al proyecto; costo global no medido.
- **¿Cuánto tiempo ahorra?** → No medido; no lo afirmamos.
