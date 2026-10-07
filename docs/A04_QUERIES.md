# Consultas y modo jurado · A-04/A-09

Ejecutar `python -m streamlit run app/Home.py` y abrir Consultas. La página utiliza `service.ask()`;
no calcula respuestas ni inventa citas. El modo solicitado puede ser cache, template o live (Ollama).
El resultado muestra siempre `generated_by.mode`, incluso si hubo respaldo a template o abstención.

Cada oración conserva su etiqueta y enlaza sus identificadores de evidencia con las tarjetas A-08.
Los campos, valores, períodos, URL y extractos proceden de las referencias devueltas por el servicio.
La abstención muestra el motivo y la información necesaria. Los códigos de validación permanecen
visibles, incluido EXTRACTIVE_MODE cuando no se utilizó un modelo. Fecha de generación en Panamá.

Modo jurado: cuatro botones con las preguntas de TASKS A-09. Cifras y procedencia llevan a fichas
existentes; ausencia de evidencia precarga una consulta para 2035; fuente maliciosa busca security_flags.
Cuando no hay un caso demostrativo en el snapshot se indica y se enlaza a Trust Lab. Nunca se
fabrica un caso ni se presenta el fixture como noticia real.

Pruebas: siete casos AppTest para modos, citas, abstención, pregunta vacía y rutas del jurado.
La navegación se prueba desde Home, el punto de entrada real. Suite completa: 128 passed.
Bundle local regenerado tras H-08: 187 señales, 183 eventos, modo template. Sin APIs pagas.

Capturas: [abstención](screenshots/a04-abstencion.png), [respuesta citada](screenshots/a04-citas.png).
No se publican el bundle ni las descripciones RSS. H-08 aceptada con la limitación de DL-024:
el editor vio una propuesta de IA, coincidente en 1 de 5; P@5 será exploratoria sobre eventos.

## Pulido final de textos (2026-10-07)
Consultas conserva etiquetas visibles de formulario y añade ejemplo/ayuda para país y período.
La ayuda de modos distingue cache/template/live; en hosting solo explica caché y respaldo, sin ofrecer
Ollama como si estuviera disponible. Ficha aclara qué significa un apartado vacío y cómo preparar
un paquete ausente; la ayuda de Generar dice explícitamente que crear borrador no aprueba ni publica.
Sin cambios en contratos, lógica, colores ni módulos A-05/A-10. No se declara auditoría WCAG completa.
