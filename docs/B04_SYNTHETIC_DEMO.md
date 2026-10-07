# B-04: demostraciones sintéticas separadas

`data/synthetic/cases.jsonl` contiene seis casos inventados. Todos los titulares
llevan `[SINTÉTICO]`, `origen=sintetico` y `sintetico=true`. No son noticias ni
observaciones oficiales reales y no entran al snapshot congelado ni al ranking.

| Caso | Demostración | Resultado ejecutado |
| --- | --- | --- |
| T01 | Fecha imposible, detección válida | Publicación nula y bandera fecha_invalida |
| T02 | Tres publicaciones; dos firman EFE | Tres publicaciones, cero independencias confirmadas |
| T03 | Publicación 2024, detección septiembre 2025 | Recirculación, sin convertir detección en publicación |
| T05 | Dos porcentajes incompatibles | Conflicto numérico; evidencia parcial |
| T07 | Inyección en titular y descripción inventados | Bandera posible_inyeccion; sin llamar al LLM |
| SUFICIENTE | Nivel inventado de Gatún: 85,1 pies en titular y observación | suficiente_para_borrador, cifra sustentada dentro del caso |

La observación de ACP es **inventada**: nombre y licencia lo dicen explícitamente,
URL `example.invalid`. Su contrato no tiene un campo sintético; por eso se guarda
solo dentro del caso marcado, se etiqueta el nombre y se prohíbe usar URLs reales.
No se añade a `data/raw/`. El estado suficiente autoriza únicamente un borrador.

Ejecutar `python -m scayl.ingest.synthetic_demo` reproduce la normalización y las
reglas existentes del Lead sin modificarlas. Guarda el bundle aislado en
`data/processed/synthetic-demo/bundle.json` (ignorado) y el reporte con hash de
entrada en `eval/results/b04-synthetic.json`. No produce paquetes LLM ni cambia
el bundle real. Para mostrarlo en UI hace falta elegir este bundle explícitamente
por el mecanismo de carga existente; no cambia el servicio predeterminado.

T03 usa una ventana amplia **solo en este replay** para conservar su fecha de
2024. No modifica C-01. Los grupos son casos controlados declarados en el archivo;
esto prueba evidencia y procedencia, no mide la calidad del clustering.

Validación: seis casos ejecutados; las pruebas comprueban etiquetas, nulidad,
agencia, recirculación, conflicto, seguridad y apoyo numérico. No son gold humano
ni métricas del corpus real. Un bundle de prueba nunca habilita publicación.
