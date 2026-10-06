#!/usr/bin/env python3
"""Make the Open Graph / Twitter card images (needs Pillow and Google Chrome).

Writes 1200 x 630 JPEGs with the Highr logo, a headline and a call to action over a photo:
  assets/images/og-image.jpg                  home page (also used by the Privacy and Terms pages)
  assets/images/social/og-<photo>.jpg         one per community, from tools/projects.py
Text is set in Poppins and the photo is cropped by Chrome, so the images match the site.
Run it after changing a community's name, price, type or photo, then run build-pages.py.
"""
import io
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from projects import PROJECTS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"
FONTS = ROOT / "assets" / "fonts"
LOGO = ROOT / "assets" / "logos" / "logo-white.svg"
CHROME = "google-chrome"
CHEVRON = ('<svg viewBox="0 0 24 24" width="30" height="30" fill="currentColor" aria-hidden="true">'
           '<path d="M13.172 12l-4.95-4.95 1.414-1.414L16 12l-6.364 6.364-1.414-1.414z"/></svg>')

CSS = """
@font-face { font-family: Poppins; font-weight: 400; src: url('@f400@'); }
@font-face { font-family: Poppins; font-weight: 500; src: url('@f500@'); }
@font-face { font-family: Poppins; font-weight: 600; src: url('@f600@'); }
* { margin: 0; box-sizing: border-box; }
html, body { width: 1200px; height: 630px; overflow: hidden; }
body { position: relative; font-family: Poppins, sans-serif; color: #fff;
  background: #1e1e1e url('@photo@') center / cover no-repeat; }
.shade { position: absolute; inset: 0;
  background: linear-gradient(90deg, rgb(0 0 0 / .82) 0%, rgb(0 0 0 / .6) 52%, rgb(0 0 0 / .12) 100%); }
.content { position: relative; height: 100%; padding: 64px 72px; display: flex; flex-direction: column; }
.logo { height: 46px; width: auto; align-self: flex-start; }
.main { margin-top: auto; max-width: 760px; }
.kicker { font-size: 28px; font-weight: 500; opacity: .85; margin-bottom: 14px; }
h1 { font-size: @h1@px; font-weight: 600; line-height: 1.06; letter-spacing: -0.01em; }
.offer { font-size: 36px; font-weight: 400; margin-top: 18px; }
.offer b { font-weight: 600; }
.cta { display: inline-flex; align-items: center; gap: 6px; margin-top: 34px; padding: 16px 20px 16px 34px;
  border-radius: 100px; background: #fff; color: #1e1e1e; font-size: 30px; font-weight: 500; }
"""


def card(photo, kicker, headline, offer, cta, h1):
    css = CSS
    for key, value in {"f400": (FONTS / "poppins-400.woff2").as_uri(), "f500": (FONTS / "poppins-500.woff2").as_uri(),
                       "f600": (FONTS / "poppins-600.woff2").as_uri(), "photo": photo.as_uri(), "h1": str(h1)}.items():
        css = css.replace(f"@{key}@", value)
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{css}</style></head><body>
<div class="shade"></div>
<div class="content">
  <img class="logo" src="{LOGO.as_uri()}" alt="">
  <div class="main">
    {f'<p class="kicker">{escape(kicker)}</p>' if kicker else ''}
    <h1>{escape(headline)}</h1>
    <p class="offer">{offer}</p>
    <span class="cta">{escape(cta)}{CHEVRON}</span>
  </div>
</div></body></html>"""


def render(html, out):
    with tempfile.TemporaryDirectory() as tmp:
        page, png = Path(tmp) / "card.html", Path(tmp) / "card.png"
        page.write_text(html, encoding="utf-8")
        subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                        "--force-device-scale-factor=1", "--window-size=1200,630", "--virtual-time-budget=4000",
                        f"--screenshot={png}", page.as_uri()], check=True, capture_output=True)
        img = Image.open(io.BytesIO(png.read_bytes())).convert("RGB")
    if img.size != (1200, 630):
        img = img.crop((0, 0, 1200, 630))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print(f"{out.relative_to(ROOT)}: {out.stat().st_size // 1024} KB")


def main():
    render(card(IMAGES / "hero-background.webp", "", "New-build homes designed to last",
                "Austin · Chicago · Charleston · Portland", "Book a show-home tour", 76),
           IMAGES / "og-image.jpg")
    for p in PROJECTS:
        photo = IMAGES / "projects" / p["image"]
        render(card(photo, f'{p["type"]} in {p["city"]}', p["name"],
                    f'Homes from <b>{escape(p["price"])}</b>', "Book a tour", 84),
               IMAGES / "social" / f'og-{Path(p["image"]).stem}.jpg')


if __name__ == "__main__":
    main()
