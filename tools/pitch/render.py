import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
HERE = Path(__file__).parent
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=1)
        await pg.goto((HERE / "slides.html").as_uri()); await pg.wait_for_load_state("networkidle")
        await pg.evaluate("document.fonts.ready")
        for i in range(1, 11):
            await pg.locator(f"#s{i}").screenshot(path=str(HERE / f"slide{i:02d}.png"))
        await b.close()
asyncio.run(main())
