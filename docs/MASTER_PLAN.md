# MASTER_PLAN — SCAYL Sala de Inteligencia Editorial

> Equipo SCAYL · Reto TVN Media "De la señal a la decisión" · Modalidad editorial (única).
> Actualizado: 2026-10-06 por Lead. Detalle de tareas en `docs/TASKS.md`; crítica en `docs/PLAN_REVIEW.md`.

## 1. Promesa del producto
> Transformar el ruido informativo en una decisión editorial investigable: qué merece atención, qué
> sabemos realmente, qué falta verificar y qué puede producirse responsablemente con la evidencia disponible.

Recorrido: SEÑAL → EVENTO → PRIORIDAD → EVIDENCIA → INVESTIGACIÓN → PRODUCCIÓN → REVISIÓN HUMANA.
La IA no decide qué es verdad ni qué se publica.

## 2. Calendario

El doc TVN (fuente de verdad) no fija la fecha y propone 3 días. Usamos las fechas de Bases como
**peor caso**: entrega el **jueves 8 de octubre a las 23:59 (hora de Panamá)**, Pitch Day el 16 de octubre.
Horas en hora de Panamá (UTC−5).

| Bloque | Ventana | Hito | Criterio de salida |
|---|---|---|---|
| D1 · Inicio + diseño | mar 6, tarde y noche | **M0 — Contratos y datos** | Contratos y docs mergeados; workers con tareas; snapshot (oficial o Plan B) en `data/raw/v1` con manifest |
| D2 · mañana | mié 7, hasta 14:00 | **M1 — Rebanada delgada de punta a punta** | `make demo` muestra bandeja → ficha → paquete `template` → revisión, con datos reales y sin LLM; T01–T04, T08 y T10 en verde |
| D2 · tarde y noche | mié 7, hasta 23:59 | **M2 — IA integrada** | Embeddings + afirmaciones LLM + Story Studio validado + Q&A con abstención; T05, T06, T07 y T09 en verde |
| D3 · mañana | jue 8, hasta 14:00 | **M3 — Evaluación + despliegue** | Trust Lab con métricas medidas; tabla baseline frente a IA; enlace desplegado; Notion migrado (si está disponible) |
| D3 · tarde | jue 8, hasta 20:00 | **M4 — Congelación** | Código congelado; PDF de herramientas IA; pitch ensayado sin red |
| D3 · cierre | jue 8, hasta 22:00 | **Entrega** | Correo a hackiathon@viamatica.com con repo, enlace y PDF (margen de 2 h) |
| Post | 9–16 oct | Pitch Day (si somos finalistas) | Ensayos, set reservado, pulido sin romper |

## 3. Prioridades
- **P0** (admisión + flujo completo): ingesta/validación, temas, agrupación, puntaje, estado de evidencia,
  vínculo oficial + Temporal Guard, conflictos numéricos, Story Studio validado, Q&A con abstención, guard
  de inyección, revisión humana, UI de 4 pantallas, espejo Notion, PDF de herramientas IA y enlace.
- **P1** (ventaja): Source DNA con agencias; Trust Lab completo con baseline frente a IA medido;
  Investigation Gap generado; matriz Prioridad × Evidencia.
- **P2** (si sobra): sincronización con Notion vía MCP; contradicciones semánticas por LLM; estudio de
  tiempo manual vs asistido; USGS ampliado.

## 4. Pantallas
1. **Sala de Situación**: embudo "N señales → M eventos → top 5"; tabla de eventos (P, rango,
   componentes en mini-barras, tema, recencia en hora de Panamá, publicaciones, insignia de evidencia,
   procedencia, conflicto, acción); matriz Prioridad × Evidencia.
2. **Ficha de Caso**: pestañas Evento · Fuentes · Evidencia · Vacíos · Producir · Revisión.
3. **Consultas**: pregunta en español → respuesta con chips de cita, o abstención con "qué información se necesita".
4. **Trust Lab**: T01–T10 (caso, entrada, esperado, observado, evidencia) + métricas + modelo/costo.

## 5. Guion de demo (4 min dentro del pitch de 10)
| t | Pantalla | Mensaje | Requisito cubierto |
|---|---|---|---|
| 0:00 | Sala de Situación | "N señales se convirtieron en M eventos. Estos cinco merecen atención, y así se calcula cada puntaje." | CU-01, T08 |
| 0:30 | Ficha → Fuentes | "Siete publicaciones no son siete confirmaciones: hay una agencia replicada y la independencia es desconocida." | CU-03, T02 |
| 1:10 | Ficha → Evidencia | Cifra con fuente, año y unidad; advertencia "dato histórico 2024"; conflicto con las versiones A y B. | CU-02, T04, T05 |
| 1:55 | Consultas | Pregunta sin respuesta → abstención explícita. | CU-04, T06 |
| 2:25 | Ficha (caso sintético) | Fuente con inyección marcada e ignorada. | T07 |
| 2:45 | Producir | Brief, guion y copy con [HECHO]/[DECLARACIÓN]/[INFERENCIA] y citas; validación aprobada. | T09 |
| 3:25 | Revisión | "Requiere evidencia" → registro con revisor, hora y hash. | §8 control humano |
| 3:45 | Trust Lab | Pruebas y métricas medidas, costo de API $0. | §9.1 |

Cierre: *"SCAYL no decide qué se publica. Reduce el tiempo entre detectar una señal y tener una historia
investigable y trazable, lista para la decisión editorial humana."*

## 6. Modelo de trabajo multiagente
- Ramas: `claude/*` (Lead), `worker-a/*` (UI) y `worker-b/*` (datos/eval), con PR a `main`. El Lead revisa y mergea.
- Los workers implementan cambios locales directamente; los transversales pasan antes por `AGENT_PROPOSALS.md`.
- Tablero oficial (`notion_mirror/01_EXECUTION_BOARD.md`) lo actualiza **solo el Lead** al mergear;
  cada worker escribe en `docs/worklog/<worker>.md` (solo agrega) y en la descripción de su PR.
- Integración: el Lead mergea a `main` al menos en cada hito (M1–M4).

## 7. Definición de "terminado" del proyecto
- [ ] `make demo` funciona en una máquina limpia sin internet (con snapshot y caché).
- [ ] T01–T10 automatizadas y en verde (o documentada la que falle con su corrección).
- [ ] Trust Lab muestra solo métricas medidas, con numerador y denominador.
- [ ] ≥5 fichas (≥1 insuficiente), ≥8 tareas y ≥3 decisiones en Notion o en el espejo.
- [ ] README con instalación, ejecución, demo offline, datos, modelos, licencias y evaluación.
- [ ] Sin secretos (scan) y `.env.example` presente.
- [ ] PDF de herramientas IA y enlace desplegado.
