#!/usr/bin/env python3
"""Make responsive copies of the community photos (needs Pillow: pip install pillow).

For every assets/images/projects/<name>.webp (the full-size original) this writes
<name>-480.webp, <name>-800.webp and <name>-1200.webp, and stores a tiny placeholder per photo
in assets/images/projects/placeholders.json. tools/build-pages.py reads that file to build the
srcset attributes and the instant placeholder shown while a photo loads. Run it after adding or
replacing a photo, then run build-pages.py.

It also crops each original to a 1200x630 JPEG share image, assets/images/social/og-<name>.jpg,
used as the Open Graph / Twitter card image of that community's page.
"""
import base64
import io
import json
import re
from pathlib import Path

from PIL import Image, ImageOps

DIR = Path(__file__).resolve().parent.parent / "assets" / "images" / "projects"
WIDTHS = (480, 800, 1200)
QUALITY = 72
OG_DIR = DIR.parent / "social"
OG_SIZE = (1200, 630)


def main():
    placeholders = {}
    for src in sorted(DIR.glob("*.webp")):
        if re.search(r"-\d+\.webp$", src.name):
            continue  # a generated copy
        img = Image.open(src).convert("RGB")
        w, h = img.size
        for width in WIDTHS:
            if width >= w:
                continue
            out = DIR / f"{src.stem}-{width}.webp"
            img.resize((width, round(h * width / w)), Image.LANCZOS).save(out, "WEBP", quality=QUALITY, method=6)
            print(f"{out.name}: {out.stat().st_size // 1024} KB")
        og = ImageOps.fit(img, OG_SIZE, Image.LANCZOS)
        og_out = OG_DIR / f"og-{src.stem}.jpg"
        og.save(og_out, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"{og_out.name}: {og_out.stat().st_size // 1024} KB")
        tiny = img.resize((24, max(1, round(24 * h / w))), Image.LANCZOS)
        buf = io.BytesIO()
        tiny.save(buf, "WEBP", quality=40, method=6)
        placeholders[src.name] = "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
        print(f"{src.name}: placeholder {len(placeholders[src.name])} chars")
    (DIR / "placeholders.json").write_text(json.dumps(placeholders, indent=1) + "\n")


if __name__ == "__main__":
    main()
