"""SCAYL ad: records the site with captions, cursor, highlights and title cards; logs timings for the mix.

    python tools/ad/record.py tools/ad/build/raw
Env: AD_BASE_URL (default http://127.0.0.1:3000; can be https://scayl-editorial.vercel.app),
     AD_VOICE_DIR (default tools/ad/build/voice; needs durations.json), PW_CHROMIUM (optional browser path).
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from playwright.async_api import async_playwright

BASE = os.environ.get("AD_BASE_URL", "http://127.0.0.1:3000").rstrip("/")
OUT = sys.argv[1]
W, H = 1920, 1080
ZOOM = 1.5
VOICE_DIR = Path(os.environ.get("AD_VOICE_DIR", Path(__file__).parent / "build" / "voice"))
DUR = json.loads((VOICE_DIR / "durations.json").read_text())
EVENTS = []
T0 = [None]


def log(kind, key=None, delay=0.0):
    EVENTS.append({"t": round(time.monotonic() - T0[0] + delay, 3), "kind": kind, "key": key})

OVERLAY_JS = r"""
(() => {
  if (window.__scayl) return; window.__scayl = true;
  const css = `
  #ad-cursor{position:fixed;z-index:2147483647;width:22px;height:22px;margin:-3px 0 0 -3px;pointer-events:none;
    transition:transform .08s;filter:drop-shadow(0 2px 3px rgba(0,0,0,.35))}
  #ad-cursor.down{transform:scale(.82)}
  .ad-ripple{position:fixed;z-index:2147483646;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;
    border:3px solid #f5b800;pointer-events:none;animation:adr .6s ease-out forwards}
  @keyframes adr{to{transform:scale(4);opacity:0}}
  #ad-cap{position:fixed;left:50%;bottom:44px;transform:translate(-50%,20px);opacity:0;z-index:2147483645;
    background:rgba(11,18,32,.94);color:#fff;border-radius:14px;padding:18px 30px 20px;max-width:1180px;
    box-shadow:0 18px 50px rgba(0,0,0,.35);font-family:Inter,system-ui,sans-serif;transition:all .45s ease;
    border-left:6px solid #f5b800;pointer-events:none}
  #ad-cap.on{opacity:1;transform:translate(-50%,0)}
  #ad-cap .k{font-size:15px;letter-spacing:.18em;text-transform:uppercase;color:#f5b800;font-weight:700;margin-bottom:6px}
  #ad-cap .t{font-size:30px;line-height:1.25;font-weight:650}
  .ad-hl{outline:4px solid #f5b800 !important;outline-offset:6px;border-radius:10px;transition:outline-color .3s}`;
  const s = document.createElement('style'); s.textContent = css; document.documentElement.appendChild(s);
  const c = document.createElement('div'); c.id = 'ad-cursor';
  c.innerHTML = '<svg viewBox="0 0 24 24" width="22" height="22"><path d="M3 2l7 19 2.5-7.5L20 11z" fill="#fff" stroke="#0b1220" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  document.documentElement.appendChild(c);
  addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; }, true);
  addEventListener('mousedown', e => { c.classList.add('down'); const r = document.createElement('div');
    r.className = 'ad-ripple'; r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px';
    document.documentElement.appendChild(r); setTimeout(() => r.remove(), 700); }, true);
  addEventListener('mouseup', () => c.classList.remove('down'), true);
  const cap = document.createElement('div'); cap.id = 'ad-cap'; cap.innerHTML = '<div class="k"></div><div class="t"></div>';
  document.documentElement.appendChild(cap);
  window.__cap = (k, t) => { cap.classList.remove('on'); setTimeout(() => {
      cap.querySelector('.k').textContent = k; cap.querySelector('.t').textContent = t; cap.classList.add('on'); }, 250); };
  window.__capOff = () => cap.classList.remove('on');
})();
"""

CARD = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;height:100%;background:#0b1220;color:#fff;font-family:Inter,system-ui,sans-serif;overflow:hidden}
.wrap{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 160px}
.line{font-size:76px;font-weight:800;letter-spacing:-.02em;line-height:1.1;opacity:0;transform:translateY(24px);
  animation:in .8s cubic-bezier(.2,.8,.2,1) forwards}
.small{font-size:34px;font-weight:500;color:#9fb0c8;margin-top:28px}
.acc{color:#f5b800}
.bar{width:90px;height:8px;background:#f5b800;margin-bottom:40px;opacity:0;animation:in .6s forwards}
@keyframes in{to{opacity:1;transform:none}}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;margin-top:56px}
.stat{border-top:6px solid #f5b800;background:#121c2f;border-radius:12px;padding:28px;opacity:0;transform:translateY(24px);
  animation:in .7s forwards}
.stat b{display:block;font-size:64px;font-weight:800}
.stat span{font-size:24px;color:#c7d2e2;line-height:1.3}
.logo{font-size:150px;font-weight:900;letter-spacing:.06em}
.url{font-size:40px;color:#f5b800;font-weight:700;margin-top:30px}
.foot{position:absolute;bottom:56px;left:160px;font-size:22px;color:#7d8da6;letter-spacing:.12em;text-transform:uppercase}
</style></head><body><div class="wrap">@@BODY@@</div>@@FOOT@@</body></html>"""


async def card(page, body, seconds, foot="", voice=None):
    await page.set_content(CARD.replace("@@BODY@@", body).replace("@@FOOT@@", f'<div class="foot">{foot}</div>' if foot else ""))
    import re as _re
    seconds = max(seconds, len(_re.sub("<[^>]+>", "", body)) / 14 + 1.5)  # readable title cards
    if voice:
        log("voice", voice, 0.35)
        seconds = max(seconds, DUR[voice] + 0.95)
    await page.wait_for_timeout(int(seconds * 1000))


async def goto(page, path):
    await page.goto(BASE + path, wait_until="networkidle")
    await page.evaluate(f"document.documentElement.style.zoom='{ZOOM}'")
    await page.evaluate(OVERLAY_JS)
    await page.mouse.move(W * 0.62, H * 0.42)
    await page.wait_for_timeout(500)


async def cap(page, kicker, text, hold, voice=None):
    await page.evaluate("([k,t]) => window.__cap(k,t)", [kicker, text])
    log("pop", None, 0.25)
    hold = max(hold, len(kicker + text) / 14 + 1.2)  # always enough time to read the caption
    if voice:
        log("voice", voice, 0.3)
        hold = max(hold, DUR[voice] + 0.9)
    await page.wait_for_timeout(int(hold * 1000))


async def scroll_to(page, selector, block="center", wait=1.4):
    await page.evaluate("([s,b]) => document.querySelector(s).scrollIntoView({behavior:'smooth',block:b})",
                        [selector, block])
    await page.wait_for_timeout(int(wait * 1000))


async def scroll_by(page, dy, wait=1.2):
    await page.evaluate(f"window.scrollBy({{top:{dy},behavior:'smooth'}})")
    await page.wait_for_timeout(int(wait * 1000))


async def move_click(page, locator, pause=0.35):
    await locator.scroll_into_view_if_needed()
    box = await locator.bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    await page.mouse.move(x, y, steps=28)
    await page.wait_for_timeout(int(pause * 1000))
    log("click")
    await page.mouse.down(); await page.wait_for_timeout(90); await page.mouse.up()


async def highlight(page, selector, on=True):
    await page.evaluate("([s,on]) => { const e=document.querySelector(s); if(e) e.classList.toggle('ad-hl', on); }",
                        [selector, on])


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=os.environ.get("PW_CHROMIUM") or None,
                                          args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        ctx = await browser.new_context(viewport={"width": W, "height": H}, record_video_dir=OUT,
                                        record_video_size={"width": W, "height": H}, locale="es-PA")
        page = await ctx.new_page()
        T0[0] = time.monotonic()

        # 0 · Problem
        await card(page, '<div class="bar"></div><div class="line">Cada día llegan cientos de señales.</div>', 2.8, voice="c1")
        await card(page, '<div class="bar"></div><div class="line">Repetir una noticia <span class="acc">no la confirma.</span></div>'
                         '<div class="line small" style="animation-delay:.5s">Y un dato viejo puede parecer nuevo.</div>', 3.6, voice="c2")
        await card(page, '<div class="line logo">SCAYL</div><div class="line small" style="animation-delay:.4s">'
                         'Sala de Inteligencia Editorial · <span class="acc">de la señal a la decisión</span></div>', 3.4,
                   "hackIAthon · reto TVN Media", voice="c3")

        # 1 · Sala de Situación
        await goto(page, "/")
        await scroll_by(page, 300, 1.0)  # keep the metric cards above the caption
        await cap(page, "Sala de Situación", "187 señales públicas → 165 eventos priorizados, listos para la reunión editorial.", 3.6, voice="sala1")
        await page.get_by_text("Cinco casos para empezar").evaluate("e => e.scrollIntoView({behavior:'smooth',block:'start'})")
        await page.wait_for_timeout(1600)
        await cap(page, "Prioridad ≠ verdad", "Cada caso trae su prioridad explicable — y, aparte, el estado real de su evidencia.", 3.6, voice="sala2")

        # 2 · Ficha: what we know / score / dates
        await move_click(page, page.get_by_role("link", name="Investigar").first)
        await page.wait_for_load_state("networkidle")
        await page.evaluate(f"document.documentElement.style.zoom='{ZOOM}'"); await page.evaluate(OVERLAY_JS)
        await page.wait_for_timeout(600)
        await cap(page, "Ficha de caso", "Qué se reporta, qué está respaldado y qué falta verificar — en una sola vista.", 3.8, voice="ficha1")
        await scroll_by(page, 470, 1.4)
        await highlight(page, ".score-panel")
        await cap(page, "Atención editorial · 89.9 / 100", "Cada punto con su regla: relevancia, impacto, urgencia, novedad, evidencia.", 3.6, voice="ficha2")
        await highlight(page, ".score-panel", False)
        await page.evaluate("() => { const w=[...document.querySelectorAll('p.warning')].find(e=>e.textContent.includes('(ACP)')); if(w){w.classList.add('ad-hl'); w.scrollIntoView({behavior:'smooth',block:'center'});} }")
        await page.wait_for_timeout(1300)
        await cap(page, "Temporal Guard", "Los datos oficiales del Canal (ACP) siempre llevan su fecha. Lo histórico nunca pasa por actual.", 3.8, voice="ficha3")

        # 3 · Provenance (EVT-0078). Not EVT-0114: it groups two different quakes by mistake (docs/EVT0114_FALSE_CONFLICT.md)
        await goto(page, "/caso/EVT-0078/")
        await move_click(page, page.get_by_role("tab", name="Fuentes"))
        await page.wait_for_timeout(500)
        await scroll_to(page, "#tab-1", "start", 1.4)
        await highlight(page, "#case-panel")
        await cap(page, "Procedencia, no conteo", "Dos medios publican la historia, pero su independencia no se puede demostrar: no son dos confirmaciones.", 4.6, voice="conflicto")

        # 4 · Producir
        await goto(page, "/caso/EVT-0101/")
        await move_click(page, page.get_by_role("tab", name="Producir"))
        await page.wait_for_timeout(500)
        await scroll_to(page, "#tab-6", "start", 1.4)
        await scroll_by(page, 380, 1.2)
        await cap(page, "Borrador con IA local", "Qwen3 8B en una GPU local: cada frase etiquetada como HECHO o DECLARACIÓN, y citada.", 4.0, voice="producir1")
        await scroll_by(page, 520, 1.3)
        await cap(page, "Validado por código", "Cifras sin respaldo o un 'actual' sin fecha se eliminan antes de que un editor las vea.", 3.6, voice="producir2")

        # 5 · Consultas
        await goto(page, "/consultas/")
        box = page.locator("textarea").first
        await move_click(page, box)
        await page.keyboard.type("¿Cuál es el nivel actual del lago Gatún?", delay=38)
        await move_click(page, page.get_by_role("button", name="Consultar"))
        await page.wait_for_timeout(1300)
        await page.evaluate("() => { const h=[...document.querySelectorAll('h2,h3')].find(e=>e.textContent.includes('nivel actual del lago')); if(h){ const blk=h.nextElementSibling||h; blk.classList.add('ad-hl'); h.scrollIntoView({behavior:'smooth',block:'start'});} }")
        await page.wait_for_timeout(1300)
        await cap(page, "Consultas con evidencia", "Responde con la última medición oficial — y su fecha, citada.", 3.6, voice="consulta1")
        await scroll_to(page, "textarea", "center", 1.0)
        await move_click(page, box)
        await box.fill("")  # platform-independent clear (Control+A does not select all on macOS)
        await page.keyboard.type("¿Cuál es la moneda oficial de Panamá?", delay=38)
        await move_click(page, page.get_by_role("button", name="Consultar"))
        await page.wait_for_timeout(1300)
        await scroll_by(page, 300, 1.1)
        await page.evaluate("() => { const w=[...document.querySelectorAll('.warning, [class*=warn]')].find(e=>e.textContent.includes('No hay evidencia suficiente')); if(w){w.classList.add('ad-hl'); w.scrollIntoView({behavior:'smooth',block:'center'});} }")
        await page.wait_for_timeout(700)
        await cap(page, "Abstención explícita", "Si no está en la evidencia, no responde de memoria: dice qué fuente faltaría.", 4.0, voice="consulta2")

        # 6 · Human review (nuevo → en revisión → aprobado como borrador)
        await goto(page, "/caso/EVT-0101/")
        await move_click(page, page.get_by_role("tab", name="Revisión"))
        await page.wait_for_timeout(500)
        await scroll_to(page, "#review-state", "center", 1.2)
        await move_click(page, page.locator("#reviewer"))
        await page.keyboard.type("Editora de turno", delay=28)
        await move_click(page, page.locator("#justification"))
        await page.keyboard.type("Caso prioritario: pasa a revisión.", delay=18)
        await move_click(page, page.get_by_role("button", name="Registrar revisión"))
        await page.wait_for_timeout(1200)
        await page.select_option("#review-state", "aprobado_como_borrador")
        await move_click(page, page.locator("#justification"))
        await page.keyboard.type("Citas revisadas; falta confirmar con la ACP antes de publicar.", delay=18)
        await cap(page, "Revisión humana", "La IA no publica. Un editor aprueba como borrador, con justificación y recibo verificable.", 2.4, voice="revision")
        await move_click(page, page.get_by_role("button", name="Registrar revisión"))
        await page.wait_for_timeout(1300)
        await scroll_by(page, 360, 1.4)
        await page.wait_for_timeout(1600)

        # 7 · Trust Lab
        await goto(page, "/trust-lab/")
        await scroll_by(page, 200, 1.0)
        await cap(page, "Pruebas y métricas", "Medimos todo — y decimos lo que no medimos. La IA se usa donde ganó; las reglas, donde no.", 4.4, voice="trust1")
        await scroll_by(page, 650, 1.6)
        await cap(page, "T01–T10 aprobadas", "Fechas inválidas, duplicados, conflictos, abstención, inyección: cada caso del reto, probado.", 3.6, voice="trust2")

        # 8 · Banking extension
        await goto(page, "/boletin/")
        await cap(page, "Extensión bancaria", "El mismo núcleo de evidencia, como boletín de entorno para un analista de estudios económicos.", 3.6, voice="boletin")
        await scroll_by(page, 520, 1.6)
        await page.wait_for_timeout(1200)

        # 9 · Close
        await card(page,
            '<div class="bar"></div><div class="line" style="font-size:60px">Medido, no prometido.</div><div class="grid">'
            '<div class="stat" style="animation-delay:.3s"><b>45/45</b><span>frases del borrador con cita verificable</span></div>'
            '<div class="stat" style="animation-delay:.55s"><b>6/6</b><span>abstenciones correctas en un set humano independiente</span></div>'
            '<div class="stat" style="animation-delay:.8s"><b>13 s</b><span>por borrador, con IA local en GPU</span></div>'
            '<div class="stat" style="animation-delay:1.05s"><b>$0</b><span>en APIs: todo corre local</span></div></div>', 5.2, voice="stats")
        await card(page,
            '<div class="line" style="font-size:66px">SCAYL no decide qué se publica.</div>'
            '<div class="line" style="font-size:66px;animation-delay:.6s">Acorta el camino de la <span class="acc">señal</span> a la <span class="acc">decisión</span>.</div>'
            '<div class="line url" style="animation-delay:1.2s">scayl-editorial.vercel.app</div>', 5.6,
            "Equipo SCAYL · hackIAthon TVN Media 2026", voice="cierre")
        EVENTS.append({"t": round(time.monotonic() - T0[0], 3), "kind": "end", "key": None})
        Path(OUT).mkdir(parents=True, exist_ok=True)
        await ctx.close()
        await browser.close()
        Path(OUT, "events.json").write_text(json.dumps(EVENTS, indent=1))


asyncio.run(main())
