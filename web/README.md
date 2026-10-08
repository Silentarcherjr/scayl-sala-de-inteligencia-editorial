# SCAYL · Web pública estática (DL-034)

Demo principal: https://scayl-editorial.vercel.app/
Respaldo y consultas libres: https://scayl-demo.streamlit.app/

Next.js App Router + TypeScript + Tailwind, export estático con 165 rutas de caso. Las fuentes Inter
se autoalojan durante el build; para compilar por primera vez se necesita internet. El resultado
`out/` se sirve sin Python, Ollama, claves ni llamadas externas. Los enlaces a fuentes y servicios
externos solo se abren por acción del lector y requieren internet.

```bash
# Desde la raíz, con el entorno Python activo:
python scripts/export_web.py
python -m pytest -q
ruff check .

# Web:
cd web
npm ci
npm run lint
npm run build
npx serve out
```

El exportador utiliza `scayl.service`, reutiliza `scripts.demo_offline.prepare()` y restaura el entorno
procesado al terminar. No modifica los artefactos originales. Rechaza descripciones RSS y citas a ese
campo mediante `deploy.prepare.check_public` antes de escribir cualquier salida. Conserva nulos e IDs.
Lee las constantes de Consultas y Trust Lab mediante AST, sin ejecutar sus páginas Streamlit.

Los aportes ponderados y las razones de la agenda se exportan desde Python; TypeScript no recalcula
el ranking oficial. Solo el simulador aplica la fórmula autorizada, con enteros cuya suma sigue siendo
100 y redondeo a una decimal compatible con Python. Las simulaciones son locales y no guardan decisiones.
El estado de evidencia es independiente del puntaje. La revisión pública es de solo lectura.

Los recorridos del jurado son recorridos de evidencia/procedencia, no respuestas de IA inventadas.
Si no existe el caso demostrativo en el snapshot, se informa y se enlaza a Trust Lab. En la respuesta
extractiva de plantilla, la fecha de generación se fija al corte del snapshot para mantener el export
reproducible; las fechas guardadas en las salidas de caché se conservan. Solo `meta.exported_at` varía
entre exports con los mismos datos y commit. `meta.git_commit` registra el commit de origen del export.

Verificación completa y capturas: [docs/screenshots/web](../docs/screenshots/web/README.md).
197 pruebas Python; lint y build web aprobados; cinco pantallas en escritorio y móvil con Wi-Fi apagado,
0 llamadas externas y 0 errores. Tres casos contrastados mediante Streamlit AppTest; paridad de las
165 filas del simulador frente a Python. La auditoría de dependencias de desarrollo está documentada
junto a las capturas; no se ocultan ni se omiten los checks.

Vercel: proyecto `hacks10/scayl-editorial`, repositorio
`Silentarcherjr/scayl-sala-de-inteligencia-editorial`, Root Directory `web`, preset Next.js,
`npm ci`, `npm run build`, Output Directory automático (sin override), sin variables de entorno.
Next.js publica el export `out/`; el adaptador Vercel necesita conservar su directorio interno `.next/`. La rama de producción Git sigue siendo
`main`; el despliegue inicial se realiza explícitamente desde `worker-web/next-static` sin mergear.
El Lead revisa y mergea el PR. Los siguientes pushes a `main` se despliegan mediante la integración Git.

No se modifica `deploy/README.md` porque el encargo prohíbe editar `deploy/`; esta página y el README
principal registran la URL y el procedimiento de la nueva web.
