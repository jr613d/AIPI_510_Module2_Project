"""Open the built story in headless Chrome, fail on console errors, save screenshots.
Run with the ASTRA venv (playwright): tests/render_check.py [out_dir]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
page_path = ROOT / "dashboard" / "seats_and_voices.html"
out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tests" / "shots"
out.mkdir(parents=True, exist_ok=True)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME, headless=True)
    for name, w, scheme in [("desktop", 1200, "light"), ("mobile", 400, "light"), ("desktop-dark", 1200, "dark")]:
        ctx = b.new_context(viewport={"width": w, "height": 900}, color_scheme=scheme, device_scale_factor=1)
        pg = ctx.new_page()
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.goto(page_path.as_uri())
        pg.wait_for_timeout(1200)
        sw = pg.evaluate("document.documentElement.scrollWidth"); cw = pg.evaluate("document.documentElement.clientWidth")
        nfig = pg.evaluate("document.querySelectorAll('figure.chart svg').length")
        print(f"{name}: scrollWidth={sw} clientWidth={cw} svg_figures={nfig} height={pg.evaluate('document.body.scrollHeight')}")
        if sw > cw + 1:
            errors.append(f"{name}: horizontal overflow {sw} > {cw}")
        pg.screenshot(path=str(out / f"{name}.png"), full_page=True)
        # also click every table toggle once to make sure tables build
        n = pg.evaluate("(() => { let n=0; document.querySelectorAll('figure.chart button.tbl').forEach(b => { b.click(); n++; }); return n; })()")
        pg.wait_for_timeout(200)
        ctx.close()
    b.close()
print("console errors:", len(errors))
for e in errors: print("  ", e[:300])
sys.exit(1 if errors else 0)
