# Anuncio en video de SCAYL (para el jurado)

Pipeline reproducible que **graba el sitio real**, con cursor, subtítulos, resaltados y placas, le añade **voz en
off**, **música original** generada por código (sin derechos de terceros) y efectos suaves, y exporta un MP4 en
1080p. Todo es código: para editar el video se cambia el guion y se vuelve a renderizar.

## Requisitos (una vez)
```bash
pip install playwright pillow numpy edge-tts      # + sherpa-onnx si usas Kokoro, + faster-whisper para --transcribe
python -m playwright install chromium
# ffmpeg y ffprobe en el PATH (Windows: winget install Gyan.FFmpeg)
```

## Flujo
```bash
# 1) El sitio: la web en Vercel o una copia local idéntica (mismo build y la misma API Python)
cd web && npm ci && node scripts/prepare-python.mjs && npm run build && cd ..
python tools/ad/serve.py web          # deja http://127.0.0.1:3000 (o usa AD_BASE_URL=https://scayl-editorial.vercel.app)

# 2) La voz: una línea de narration.json = un WAV (las duraciones marcan el ritmo del video)
python tools/ad/voice.py edge es-PA-RobertoNeural

# 3) Renderizar
python tools/ad/make_ad.py            # -> tools/ad/build/SCAYL_anuncio.mp4

# 4) Revisar como lo haría un humano: hojas de contacto y transcripción de la voz
python tools/ad/inspect_video.py tools/ad/build/SCAYL_anuncio.mp4 --transcribe
```

## Dónde se edita cada cosa
| Quiero cambiar… | Archivo |
|---|---|
| Lo que dice la voz | `narration.json` (luego `voice.py … --only clave1,clave2`) |
| Subtítulos, escenas, orden, qué se clica | `record.py` (llamadas `cap(...)`, `card(...)`, `goto(...)`) |
| Placas de apertura y cierre | `record.py` (`card(...)` y la plantilla `CARD`) |
| Volumen de música, voz y efectos; ducking | `mix.py` (sección *ducking + mix*) |
| Duración mínima de cada subtítulo | `record.py`: `len(kicker + text) / 14 + 1.2` (≈14 caracteres por segundo) |

## Reglas
- Cada cifra que aparezca debe estar medida en el repo (`eval/results/latest.json`, `06_TESTS_AND_METRICS.md`).
- No mostrar contraseñas, datos personales ni descripciones RSS.
- Los videos y audios generados viven en `tools/ad/build/` (ignorado por git): se comparten fuera del repo.
- La voz pronuncia "SCAYL" según el motor. Si suena mal, escríbelo fonéticamente en `narration.json`
  (por ejemplo "Escáil") y regenera esas líneas.

## Cómo "ve" el video un agente
`inspect_video.py` extrae fotogramas cada N segundos, los junta en hojas de contacto con la marca de tiempo y,
con `--transcribe`, transcribe la mezcla final. El agente abre las imágenes y lee la transcripción para
comprobar el encuadre, la legibilidad de los subtítulos, la sincronía y que la voz se entienda sobre la música.
