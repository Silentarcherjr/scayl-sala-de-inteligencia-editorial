# H-06 · Tres tareas manual vs SCAYL

Participan LowCrime y frictionspp-svg. Acordar un operador humano por par (la misma persona realiza
ambas condiciones) y quién cronometra. Completar `data/labels/time_study.csv`. No introducir tiempos
simulados o inferidos por IA. Copia estable para el humano mientras cambia la rama: `tmp/h06/`.

Usar el mismo snapshot v1, corte 2026-10-01, mismos archivos/titulares y acceso a fuentes en ambas
condiciones. Registrar equipo, familiaridad, modo template/cache/live, interrupciones y cambios de
conectividad en notes. En manual usar navegador y archivos fuente; no consultar ranking ni paquetes.
En asistido usar la app local con ese snapshot. Preparar ambas antes de iniciar el cronómetro.

| Tarea | Resultado entregable en ambas condiciones | Orden sugerido |
|---|---|---|
| H06-1 | Un tema del día y tres vacíos concretos de verificación; justificar elección | manual → asistido |
| H06-2 | Una cifra de inflación de Panamá con campo/valor, fuente, período y aclaración sobre actualidad | asistido → manual |
| H06-3 | Para un caso del Canal, publicaciones y grupos de procedencia; explicar qué independencia puede o no determinarse | manual → asistido |

Fijar el mismo caso/cifra antes de cada par y anotarlo. Iniciar al leer la tarea; detener al guardar
el resultado completo. Registrar segundos positivos sin redondear a minutos, salida escrita de cada
condición, operador, orden real y fecha UTC. No repetir hasta obtener un tiempo favorable. Si hay
interrupción, declararla; si no terminó, dejar tiempo vacío y describirlo. Es aprendizaje repetido de
la misma tarea: el orden alternado no elimina ese sesgo. No comparar calidad desigual como ahorro.

```bash
python -m scayl.eval.time_study
```

El resumen en `eval/results/time-study.json` muestra no medido hasta completar tres pares con tiempos,
operador, fecha y resultados. n=0 al preparar; n previsto=3. Después informa cada par, diferencia total
y mediana de diferencias, incluso si SCAYL tarda más. El humano coteja la calidad. Registrar resultado
en `06_TESTS_AND_METRICS.md` como **exploratorio, n=3**, sin afirmaciones causales de ahorro.
