#!/usr/bin/env python3
"""Regenerate the community pages (<slug>.html) and the project cards on index.html.

    python3 tools/build-pages.py

Data lives in tools/projects.py. The header, footer, action bar and Tailwind theme of every
generated page are copied from index.html, so edit them there and run this script again.
Standard library only; the site itself needs no build step.
"""
import json
import re
import sys
from html import escape, unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from projects import PROJECTS  # noqa: E402
import legal  # noqa: E402

INDEX = ROOT / "index.html"
SITE_NAME = "Highr"
PHONE_TEL = "+12125550142"
SITE_URL = "https://forhadkhan.github.io/highr"  # GitHub Pages project URL; use the real domain, then re-run this script
DEMO = True  # demo site: ask search engines not to index the made-up company
NOINDEX = '<meta name="robots" content="noindex, nofollow">'
ORG = {
    "@type": "Organization",
    "@id": SITE_URL + "/#organization",
    "name": "Highr Real Estate, Inc.",
    "url": SITE_URL + "/",
    "logo": SITE_URL + "/assets/logos/logo-dark.svg",
    "telephone": "+1-212-555-0142",
    "email": "contact@highr.example",
    "address": {"@type": "PostalAddress", "streetAddress": "500 Market Street, Suite 1200",
                "addressLocality": "San Francisco", "addressRegion": "CA", "postalCode": "94105", "addressCountry": "US"},
}


def ld(data):
    """A JSON-LD script tag ('</' is escaped so the data can never close the tag)."""
    body = json.dumps({"@context": "https://schema.org", **data} if isinstance(data, dict) else data,
                      indent=2, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">\n{body}\n  </script>'


def faq_entities(src):
    out = []
    for q, a in re.findall(r'<summary class="faq__q"><span>(.*?)</span>.*?</summary>\s*<p class="faq__a">(.*?)</p>', src, flags=re.S):
        out.append({"@type": "Question", "name": unescape(q),
                    "acceptedAnswer": {"@type": "Answer", "text": unescape(re.sub(r"<[^>]+>", "", a))}})
    return out


def og_tags(title, desc, image, alt, url, size=(1200, 630)):
    """Open Graph and Twitter card tags; `image` is an absolute URL."""
    t, d, a = escape(title), escape(desc), escape(alt)
    return "\n  ".join([
        '<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="en_US">',
        f'<meta property="og:title" content="{t}">',
        f'<meta property="og:description" content="{d}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        f'<meta property="og:image:width" content="{size[0]}">',
        f'<meta property="og:image:height" content="{size[1]}">',
        f'<meta property="og:image:alt" content="{a}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{t}">',
        f'<meta name="twitter:description" content="{d}">',
        f'<meta name="twitter:image" content="{image}">',
        f'<meta name="twitter:image:alt" content="{a}">'])


def seo_index(src):
    return "\n  ".join(([NOINDEX] if DEMO else []) + [
        f'<link rel="canonical" href="{SITE_URL}/">',
        f'<meta property="og:url" content="{SITE_URL}/">',
        ld({**ORG}),
        ld({"@type": "FAQPage", "mainEntity": faq_entities(src)}),
    ])


def seo_project(p):
    kind = "GatedResidenceCommunity" if "Villas" in p["type"] else "ApartmentComplex"
    locality, region = [x.strip() for x in p["city"].split(",")]
    data = {"@type": kind, "name": p["name"], "url": f'{SITE_URL}/{p["slug"]}',
            "description": p["tagline"], "image": f'{SITE_URL}/assets/images/projects/{p["image"]}',
            "address": {"@type": "PostalAddress", "addressLocality": locality, "addressRegion": region, "addressCountry": "US"},
            "geo": {"@type": "GeoCoordinates", "latitude": p["coords"][0], "longitude": p["coords"][1]},
            "numberOfAccommodationUnits": int(re.sub(r"\D", "", p["homes"].split()[0])),
            "provider": {"@id": ORG["@id"]}}
    crumbs = {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Communities", "item": SITE_URL + "/#projects"},
        {"@type": "ListItem", "position": 2, "name": p["name"], "item": data["url"]}]}
    return "\n  ".join(([NOINDEX] if DEMO else []) + [f'<link rel="canonical" href="{data["url"]}">',
                        ld(data), ld(crumbs)])


def seo_legal(page):
    url = f'{SITE_URL}/{page["slug"]}'
    return "\n  ".join(([NOINDEX] if DEMO else []) + [f'<link rel="canonical" href="{url}">'])


def sitemap():
    pages = [""] + [p["slug"] for p in PROJECTS] + [x["slug"] for x in legal.PAGES]
    urls = "".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>\n" for u in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def robots():
    if DEMO:
        return "User-agent: *\nDisallow: /\n"  # demo: keep out of search engines (pages also carry noindex)
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n"


def beds_label(beds):
    """'0–3 beds' -> 'Studio–3 beds' (a 0-bedroom home is a studio)."""
    return beds.replace("0–", "Studio–", 1) if beds.startswith("0–") else beds


PROJECT_IMG = Path(__file__).resolve().parent.parent / "assets" / "images" / "projects"
SIZES_CARD = "(min-width: 1280px) 640px, (min-width: 768px) 46vw, 70vw"


def photo_attrs(image, sizes):
    """srcset/sizes for a community photo, from the copies made by tools/optimize-images.py."""
    stem = image.rsplit(".", 1)[0]
    found = [(w, f"assets/images/projects/{stem}-{w}.webp") for w in (480, 800, 1200)
             if (PROJECT_IMG / f"{stem}-{w}.webp").exists()]
    if not found:
        return ""
    found.append((1500, f"assets/images/projects/{image}"))
    srcset = ", ".join(f"{u} {w}w" for w, u in found)
    return f' srcset="{srcset}" sizes="{sizes}"'


def placeholder_style(image):
    """Inline style that paints a tiny placeholder behind a photo until it loads."""
    try:
        data = json.loads((PROJECT_IMG / "placeholders.json").read_text())
    except (OSError, ValueError):
        return ""
    uri = data.get(image)
    return f' style="background-image: url({uri})"' if uri else ""


def card(p, i):
    ongoing = p["status"] == "ongoing"
    if ongoing:
        status = (f'<span class="status-ring" style="--p: {p["progress"]}" aria-hidden="true"></span>'
                  f'<span>{p["progress"]}% built · {p["eta"]}</span>')
    else:
        status = ('<span class="status-ring status-ring--done" aria-hidden="true"><i class="icon icon-check-circle"></i></span>'
                  '<span>Ready to move in</span>')
    delay = 0 if i % 2 == 0 else 120
    return f'''            <li class="project-item" data-status="{p["status"]}" data-reveal data-reveal-delay="{delay}">
              <article class="flex h-full flex-col gap-6">
                <div class="project-media" data-reveal="clip"{placeholder_style(p["image"])}>
                  <img src="assets/images/projects/{p["image"]}"{photo_attrs(p["image"], SIZES_CARD)} alt="{escape(p["alt"])}" width="1500" height="1002" loading="lazy" decoding="async" class="h-full w-full object-cover">
                  <p class="status-badge">{status}</p>
                </div>
                <div class="flex flex-col gap-3">
                  <ul class="card-meta">
                    <li>{icon("map-pin")}{p["city"]}</li>
                    <li>{icon("building")}{p["type"]}</li>
                  </ul>
                  <h3 class="text-h3"><a href="{p["slug"]}" class="card-link">{p["name"]}</a></h3>
                  <p class="max-w-[607px] text-ink-700">{p["card"]}</p>
                </div>
                <dl class="spec mt-auto">
                  <div class="spec__item"><dt>{icon("price-tag")}From</dt><dd>{p["price"]}</dd></div>
                  <div class="spec__item"><dt>{icon("bed")}Bedrooms</dt><dd>{beds_label(p["beds"])}</dd></div>
                  <div class="spec__item"><dt>{icon("ruler")}Area</dt><dd>{p["size"]}</dd></div>
                </dl>
                <p class="card-more" aria-hidden="true">View details {icon("chevron-right")}</p>
              </article>
            </li>
'''


def patch_index(src):
    seo = seo_index(src)
    src, n = re.subn(r"(<!-- seo:start[^>]*-->\n).*?(\s*<!-- seo:end -->)", lambda m: m.group(1) + "  " + seo + "\n  " + m.group(2).lstrip(), src, flags=re.S)
    if n != 1:
        raise SystemExit("index.html: seo:start / seo:end markers not found")
    cards = "".join(card(p, i) for i, p in enumerate(PROJECTS))
    new, n = re.subn(r"(<!-- projects:start[^>]*-->\n).*?(\s*<!-- projects:end -->)",
                     lambda m: m.group(1) + cards + m.group(2), src, flags=re.S)
    if n != 1:
        raise SystemExit("index.html: projects:start / projects:end markers not found")
    return new


def grab(src, start, end, include_end=True):
    i = src.index(start)
    j = src.index(end, i) + (len(end) if include_end else 0)
    return src[i:j]


def layout_parts(src):
    header = grab(src, '<header id="site-header"', "</header>")
    footer = grab(src, '<footer id="contact"', "</footer>")
    actionbar = grab(src, '<nav class="actionbar"', "</nav>")
    tailwind = grab(src, "<!-- Compiled Tailwind", 'tailwind.css">')
    # Subpage links: sections of the home page get a ./ prefix; #contact stays local.
    header = header.replace('href="#top"', 'href="./"').replace('aria-label="Highr, back to top"', 'aria-label="Highr, home"')
    header = re.sub(r'href="#(projects|about|process|testimonial|faq|visit)"', r'href="./#\1"', header)
    footer = footer.replace('<a href="#top" aria-label="Highr, back to top" data-reveal>', '<a href="./" aria-label="Highr, home" data-reveal>')
    return header, footer, actionbar, tailwind


PLAN_DIR = ROOT / "assets" / "plans"


def plan_svg(name, beds, baths):
    """Schematic room layout for one home type. Illustrative only, not to scale."""
    beds = int(beds)
    full = int(float(baths))
    rooms = ["Studio" if beds == 0 else f"Bedroom {i}" for i in range(1, beds + 1)] if beds else ["Sleeping"]
    wet = ["Bath"] * max(full, 1) + (["Powder"] if float(baths) % 1 else [])
    right = rooms + wet
    ncols = -(-len(right) // 4)
    per = -(-len(right) // ncols)
    cols = [right[i:i + per] for i in range(0, len(right), per)]
    x0, y0, w, h = 16, 16, 368, 268
    left_w = round(w * (0.42 if len(cols) < 2 else 0.34))
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" width="400" height="300" role="img" data-generated="true">',
           f'<title>{escape(name)} layout</title><rect width="400" height="300" fill="#f4f4f4"/>',
           f'<g fill="#fff" stroke="#111" stroke-width="2" font-family="Poppins, Arial, sans-serif" font-size="11" text-anchor="middle">']

    def cell(label, x, y, cw, ch):
        out.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}"/>'
                   f'<text x="{x + cw / 2:.0f}" y="{y + ch / 2 + 4:.0f}" fill="#444" stroke="none">{escape(label)}</text>')

    half = round(h * 0.58)
    cell("Living / Dining", x0, y0, left_w, half)
    cell("Kitchen", x0, y0 + half, left_w, h - half)
    cw = (w - left_w) / len(cols)
    for ci, col in enumerate(cols):
        x = round(x0 + left_w + ci * cw)
        wd = round(x0 + left_w + (ci + 1) * cw) - x
        weights = [0.55 if r in ("Bath", "Powder") else 1 for r in col]
        total, y = sum(weights), y0
        for r, wt in zip(col, weights):
            ch = round(h * wt / total)
            cell(r, x, y, wd, ch)
            y += ch
    out.append('</g></svg>')
    return "".join(out)


def plan_asset(slug, n, name, beds, baths):
    """Path of the plan image. A real file named assets/plans/<slug>-<n>.(png|webp|jpg|svg) wins;
    otherwise an illustrative SVG is generated. Returns (relative path, is_generated)."""
    PLAN_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{slug}-{n}"
    for ext in ("png", "webp", "jpg", "svg"):
        f = PLAN_DIR / f"{base}.{ext}"
        if f.exists() and 'data-generated' not in f.read_text(errors="ignore")[:400]:
            return f"assets/plans/{f.name}", False
    f = PLAN_DIR / f"{base}.svg"
    f.write_text(plan_svg(name, beds, baths))
    return f"assets/plans/{f.name}", True


def icon(name, cls=""):
    return f'<i class="icon icon-{name} {cls}" aria-hidden="true"></i>'


def project_page(p, parts, others):
    header, footer, actionbar, tailwind = parts
    ongoing = p["status"] == "ongoing"
    header = header.replace('data-nav-link>Homes', 'data-nav-link aria-current="true">Homes')
    footer = footer.replace("data-contact-form", f'data-contact-form data-interest="{p["name"]}"', 1)
    lat, lon = p["coords"]
    bbox = f"{lon - 0.012:.4f}%2C{lat - 0.008:.4f}%2C{lon + 0.012:.4f}%2C{lat + 0.008:.4f}"
    map_src = f"https://www.openstreetmap.org/export/embed.html?bbox={bbox}&amp;layer=mapnik&amp;marker={lat}%2C{lon}"
    map_link = f"https://www.openstreetmap.org/?mlat={lat}&amp;mlon={lon}#map=15/{lat}/{lon}"

    if ongoing:
        status = (f'<span class="status-ring" style="--p: {p["progress"]}" aria-hidden="true"></span>'
                  f'<span>{p["progress"]}% built · Completes {p["eta"]}</span>')
    else:
        status = ('<span class="status-ring status-ring--done" aria-hidden="true"><i class="icon icon-check-circle"></i></span>'
                  f'<span>Ready to move in · {p["eta"]}</span>')

    facts = [("Homes from", p["price"]), ("Bedrooms", p["beds"].replace(" beds", "").replace(" bed", "")),
             ("Home size", p["size"]), ("Community", p["homes"]),
             ("Handover" if ongoing else "Status", p["eta"] if ongoing else "Completed")]
    if not ongoing:
        facts[4] = ("Completed", p["eta"].replace("Completed ", ""))
    facts_html = "".join(
        f'''          <div class="flex flex-col gap-3 bg-white p-6 sm:p-8" data-reveal data-reveal-delay="{i * 70}">
            <dt class="text-ink-700">{k}</dt>
            <dd class="text-h4">{v}</dd>
          </div>
''' for i, (k, v) in enumerate(facts))

    avail_cls = {"Available": "pill--ok", "Move-in ready": "pill--ok", "Limited": "pill--warn", "Few left": "pill--warn", "Waitlist": ""}
    rows = "".join(
        f'''              <tr>
                <th scope="row" data-label="Home type">{t}</th>
                <td data-label="Bedrooms">{b if str(b) != "0" else "Studio"}</td>
                <td data-label="Bathrooms">{ba}</td>
                <td data-label="Size (sq ft)">{sq}</td>
                <td data-label="From">{pr}</td>
                <td data-label="Availability"><span class="pill {avail_cls.get(av, '')}">{av}</span></td>
              </tr>
''' for (t, b, ba, sq, pr, av) in p["types"])

    highlights = "".join(f'            <li class="flex items-start gap-3">{icon("check-circle", "mt-0.5 text-success")}<span>{h}</span></li>\n' for h in p["highlights"])
    nearby = "".join(f'            <li class="flex items-baseline justify-between gap-6 border-b border-ink-100 py-4"><span>{n}</span><span class="shrink-0 text-ink-700">{t}</span></li>\n' for n, t in p["nearby"])
    steps = "".join(
        f'''            <li data-state="{state}" data-reveal data-reveal-delay="{i * 60}">
              <p class="text-body-lg">{name}</p>
              <p class="text-sm text-ink-700">{when}</p>
            </li>
''' for i, (name, state, when) in enumerate(p["milestones"]))
    other_cards = "".join(
        f'''          <li data-reveal data-reveal-delay="{i * 100}">
            <a href="{o["slug"]}" class="other-card">
              <div class="project-media"{placeholder_style(o["image"])}><img src="assets/images/projects/{o["image"]}"{photo_attrs(o["image"], SIZES_CARD)} alt="{escape(o["alt"])}" width="1500" height="1002" loading="lazy" decoding="async" class="h-full w-full object-cover"></div>
              <span class="mt-5 flex flex-col gap-1.5">
                <span class="text-h4">{o["name"]}</span>
                <span class="text-ink-700">{o["city"]} · From {o["price"]}</span>
              </span>
            </a>
          </li>
''' for i, o in enumerate(others))

    plan_items, any_generated = "", False
    for n, (t, b, ba, sq, pr, av) in enumerate(p["types"], 1):
        src, gen = plan_asset(p["slug"], n, t, b, ba)
        any_generated = any_generated or gen
        kind = "Schematic floor plan" if gen else "Floor plan"
        bed_txt = "Studio" if str(b) == "0" else f"{b} bed"
        plan_items += f'''          <li data-reveal data-reveal-delay="{(n - 1) % 2 * 100}">
            <figure class="plan">
              <div class="plan__img"><a href="{src}" class="zoom" data-lightbox="plans" data-caption="{escape(t)} · {bed_txt} · {ba} bath · {sq} sq ft"><img src="{src}" alt="{kind} of the {escape(t)}: {bed_txt}, {ba} bath, {sq} sq ft" width="400" height="300" loading="lazy"><span class="zoom__hint">{icon("zoom-in")}</span><span class="sr-only">View larger</span></a></div>
              <figcaption><span class="text-h4">{t}</span><span class="text-ink-700">{bed_txt} · {ba} bath · {sq} sq ft</span></figcaption>
            </figure>
          </li>
'''
    plan_cols = "xl:grid-cols-4" if len(p["types"]) == 4 else "xl:grid-cols-3"
    plan_note = ("Illustrative layouts, not to scale. Dimensioned plans for each home are sent by your advisor."
                 if any_generated else "Dimensions and finishes vary by home. Your advisor sends the full plan set.")
    plans_html = f'''    <section id="plans" class="section-y bg-white" aria-labelledby="plans-title">
      <div class="container-page">
        <div class="flex flex-col gap-6">
          <p class="text-body-lg" data-reveal>Layouts</p>
          <h2 id="plans-title" class="max-w-[640px] text-h2" data-reveal data-split data-reveal-delay="80">Floor plans</h2>
        </div>
        <ul class="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 {plan_cols} md:mt-[60px]">
{plan_items}        </ul>
        <p class="mt-6 text-sm text-ink-700">{plan_note}</p>
      </div>
    </section>

'''

    gallery = p.get("gallery", [])
    gallery_html = ""
    if len(gallery) >= 2:
        shots = "".join(
            f'''          <li class="gallery-grid__item" data-reveal data-reveal-delay="{i % 3 * 80}"><a href="assets/images/projects/{g}" class="zoom" data-lightbox="gallery" data-caption="{escape(alt)}"><img src="assets/images/projects/{g}" alt="{escape(alt)}" width="1500" height="1002" loading="lazy" class="h-full w-full object-cover"><span class="zoom__hint">{icon("zoom-in")}</span><span class="sr-only">View larger</span></a></li>
''' for i, (g, alt) in enumerate(gallery))
        gallery_html = f'''    <section id="gallery" class="bg-white pb-[var(--section-y)]" aria-labelledby="gallery-title">
      <div class="container-page">
        <h2 id="gallery-title" class="text-h2" data-reveal data-split>Gallery</h2>
        <ul class="gallery-grid mt-10 md:mt-[60px]">
{shots}        </ul>
      </div>
    </section>

'''

    if ongoing:
        progress_head = f'''<p class="text-h1 leading-none" data-count="{p["progress"]}" data-prefix="" data-suffix="%" data-decimals="0">{p["progress"]}%</p>
            <div class="meter" role="progressbar" aria-label="Construction progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{p["progress"]}"><span style="width: {p["progress"]}%"></span></div>
            <p class="max-w-[420px] text-ink-700">Construction is {p["progress"]}% complete. Handover is planned for {p["eta"]}, and reserved buyers receive progress updates throughout the build.</p>'''
        progress_title = "Construction progress"
    else:
        progress_head = f'''<p class="text-h1 leading-none">Done</p>
            <p class="max-w-[420px] text-ink-700">{p["name"]} was completed in {p["eta"].replace("Completed ", "")} and is lived in today. Homes marked move-in ready can be handed over within weeks of reservation.</p>'''
        progress_title = "Built and lived in"

    title = f'{p["name"]} – {p["type"]} in {p["city"].split(",")[0]}'
    if len(title) + len(SITE_NAME) + 3 <= 60:
        title += f' | {SITE_NAME}'  # the brand only when the whole title stays within 60 characters
    desc = f'{p["tagline"]} Homes from {p["price"]}.'

    return f'''<!DOCTYPE html>
<html lang="en-US" class="scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta name="theme-color" content="#ffffff">

  {og_tags(title, p["tagline"], f'{SITE_URL}/assets/images/social/og-{Path(p["image"]).stem}.jpg', f'{p["name"]}, {p["type"]} in {p["city"]}', f'{SITE_URL}/{p["slug"]}')}
  {seo_project(p)}

  <link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">

  <link rel="preload" href="assets/fonts/poppins-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/poppins-500.woff2" as="font" type="font/woff2" crossorigin>

  <link rel="stylesheet" href="css/styles.css">

  {tailwind}
</head>

<body class="bg-white font-sans text-base font-normal text-ink antialiased">
  <script>document.documentElement.classList.add('js');</script>
  <a href="#main" class="skip-link">Skip to content</a>

  {header}

  <main id="main">
    <section id="top" class="hero bg-white" aria-labelledby="project-title">
      <div class="container-page">
        <div class="flex flex-col items-start gap-6 md:gap-8">
          <nav class="crumbs" aria-label="Breadcrumb" data-reveal="fade">
            <ol>
              <li><a href="./#projects">Communities</a></li>
              <li>{icon("chevron-right")}</li>
              <li aria-current="page">{p["name"]}</li>
            </ol>
          </nav>
          <p class="flex items-center gap-3 text-body-lg" data-reveal data-reveal-delay="60">{status}</p>
          <h1 id="project-title" class="text-h1" data-reveal data-split data-reveal-delay="100">{p["name"]}</h1>
          <p class="max-w-[620px] text-lead text-ink-700" data-reveal data-reveal-delay="300">{p["tagline"]}</p>
          <div class="flex flex-wrap items-center gap-x-7 gap-y-5" data-reveal data-reveal-delay="420">
            <a href="#contact" class="btn">
              <span class="btn__label"><span>Request details</span><span aria-hidden="true">Request details</span></span>
            </a>
            <a href="tel:{PHONE_TEL}" class="link-quiet">Call (212) 555-0142</a>
          </div>
        </div>
      </div>
    </section>

    <div class="hero-media">
      <img src="assets/images/projects/{p["image"]}"{photo_attrs(p["image"], "100vw")} alt="{escape(p["alt"])}" width="1500" height="1002" fetchpriority="high" class="hero-media__img" data-parallax="0.12">
    </div>

    <section class="section-y bg-white" aria-label="Key facts">
      <div class="container-page">
        <dl class="grid grid-cols-1 gap-px border border-ink-100 bg-ink-100 sm:grid-cols-2 xl:grid-cols-5">
{facts_html}        </dl>
      </div>
    </section>

    <section class="bg-white pb-[var(--section-y)]" aria-labelledby="overview-title">
      <div class="container-page">
        <div class="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_0.85fr] lg:gap-[100px]">
          <div class="flex flex-col gap-6">
            <h2 id="overview-title" class="text-h2" data-reveal data-split>About {p["name"]}</h2>
            <div class="flex flex-col gap-6" data-stagger="120" data-stagger-base="150">
              <p class="max-w-[640px] text-ink-700" data-reveal>{p["overview"][0]}</p>
              <p class="max-w-[640px] text-ink-700" data-reveal>{p["overview"][1]}</p>
            </div>
          </div>
          <div class="flex flex-col gap-6" data-reveal data-reveal-delay="120">
            <h3 class="text-h4">Highlights</h3>
            <ul class="flex flex-col gap-4 text-body-lg">
{highlights}            </ul>
          </div>
        </div>
      </div>
    </section>

{gallery_html}    <section id="homes" class="section-y bg-smoke" aria-labelledby="types-title">
      <div class="container-page">
        <div class="flex flex-col gap-6">
          <p class="text-body-lg" data-reveal>Pricing</p>
          <h2 id="types-title" class="max-w-[640px] text-h2" data-reveal data-split data-reveal-delay="80">Home types and pricing</h2>
        </div>
        <div class="mt-10 md:mt-[60px]" data-reveal data-reveal-delay="120">
          <table class="types">
            <thead>
              <tr><th scope="col">Home type</th><th scope="col">Bedrooms</th><th scope="col">Bathrooms</th><th scope="col">Size (sq ft)</th><th scope="col">From</th><th scope="col">Availability</th></tr>
            </thead>
            <tbody>
{rows}            </tbody>
          </table>
        </div>
        <div class="mt-8 flex flex-wrap items-center gap-x-8 gap-y-4">
          <a href="#contact" class="btn">
            <span class="btn__label"><span>Request detailed plans</span><span aria-hidden="true">Request detailed plans</span></span>
          </a>
          <p class="max-w-[460px] text-sm text-ink-700">Prices are starting prices and may change. Finish packages and current availability are sent by your advisor.</p>
        </div>
      </div>
    </section>

{plans_html}    <section id="progress" class="section-y bg-white" aria-labelledby="progress-title">
      <div class="container-page">
        <div class="grid grid-cols-1 gap-10 lg:grid-cols-[1fr_0.85fr] lg:gap-[100px]">
          <div class="flex flex-col items-start gap-6">
            <h2 id="progress-title" class="text-h2" data-reveal data-split>{progress_title}</h2>
            {progress_head}
          </div>
          <ol class="timeline" aria-label="Construction milestones">
{steps}          </ol>
        </div>
      </div>
    </section>

    <section id="location" class="section-y bg-smoke" aria-labelledby="location-title">
      <div class="container-page">
        <div class="grid grid-cols-1 gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:gap-[80px]">
          <div class="flex flex-col gap-6">
            <p class="text-body-lg" data-reveal>{p["area"]}</p>
            <h2 id="location-title" class="text-h2" data-reveal data-split data-reveal-delay="80">Location</h2>
            <ul class="mt-2 text-body-lg" data-reveal data-reveal-delay="160">
{nearby}            </ul>
            <a href="{map_link}" target="_blank" rel="noopener noreferrer" class="link-quiet self-start" data-reveal>Open in OpenStreetMap</a>
          </div>
          <div class="map" data-reveal="clip">
            <iframe src="{map_src}" title="Map showing the location of {p["name"]} in {p["area"]}" loading="lazy" referrerpolicy="no-referrer"></iframe>
          </div>
        </div>
      </div>
    </section>

    <section class="section-y bg-white" aria-labelledby="other-title">
      <div class="container-page">
        <h2 id="other-title" class="text-h2" data-reveal data-split>Other communities</h2>
        <ul class="mt-10 grid grid-cols-1 gap-x-6 gap-y-12 sm:grid-cols-3 md:mt-[60px]">
{other_cards}        </ul>
      </div>
    </section>
  </main>

  {footer}

  {actionbar}

  <script src="js/reveal.js" defer></script>
  <script src="js/nav.js" defer></script>
  <script src="js/parallax.js" defer></script>
  <script src="js/counters.js" defer></script>
  <script src="js/form.js" defer></script>
  <script src="js/actionbar.js" defer></script>
  <script src="js/lightbox.js" defer></script>
</body>
</html>
'''


def legal_page(page, parts):
    header, footer, actionbar, tailwind = parts
    body = ""
    for heading, blocks in page["sections"]:
        body += f'      <section class="flex flex-col gap-4" data-reveal>\n        <h2 class="text-h4">{heading}</h2>\n'
        for b in blocks:
            if isinstance(b, tuple):
                items = "".join(f"          <li>{escape(i)}</li>\n" for i in b[1])
                body += f'        <ul class="flex list-disc flex-col gap-2 pl-6 text-ink-700">\n{items}        </ul>\n'
            else:
                body += f'        <p class="text-ink-700">{escape(b)}</p>\n'
        body += "      </section>\n"
    title = f'{page["title"]} | {SITE_NAME}'
    return f'''<!DOCTYPE html>
<html lang="en-US" class="scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(page["description"])}">
  <meta name="theme-color" content="#ffffff">
  {og_tags(title, page["description"], f"{SITE_URL}/assets/images/og-image.jpg", "Highr, new-build homes designed to last", f'{SITE_URL}/{page["slug"]}')}
  {seo_legal(page)}
  <link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
  <link rel="preload" href="assets/fonts/poppins-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/poppins-500.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="css/styles.css">

  {tailwind}
</head>

<body class="bg-white font-sans text-base font-normal text-ink antialiased">
  <script>document.documentElement.classList.add('js');</script>
  <a href="#main" class="skip-link">Skip to content</a>

  {header}

  <main id="main">
    <section id="top" class="hero bg-white" aria-labelledby="legal-title">
      <div class="container-page">
        <div class="flex max-w-[760px] flex-col items-start gap-6">
          <h1 id="legal-title" class="text-h1" data-reveal data-split>{page["title"]}</h1>
          <p class="text-sm text-ink-700" data-reveal data-reveal-delay="200">Last updated {legal.UPDATED}</p>
          <p class="text-lead text-ink-700" data-reveal data-reveal-delay="300">{escape(page["intro"])}</p>
        </div>
      </div>
    </section>

    <div class="container-page section-y">
      <div class="flex max-w-[760px] flex-col gap-10">
{body}      </div>
    </div>
  </main>

  {footer}

  {actionbar}

  <script src="js/reveal.js" defer></script>
  <script src="js/nav.js" defer></script>
  <script src="js/form.js" defer></script>
  <script src="js/actionbar.js" defer></script>
</body>
</html>
'''


def main():
    src = INDEX.read_text(encoding="utf-8")
    new = patch_index(src)
    if new != src:
        INDEX.write_text(new, encoding="utf-8")
    parts = layout_parts(new)
    for p in PROJECTS:
        others = [o for o in PROJECTS if o is not p][:3]
        (ROOT / f'{p["slug"]}.html').write_text(project_page(p, parts, others), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(sitemap(), encoding="utf-8")
    (ROOT / "robots.txt").write_text(robots(), encoding="utf-8")
    for page in legal.PAGES:
        (ROOT / f'{page["slug"]}.html').write_text(legal_page(page, parts), encoding="utf-8")
    print(f"index.html cards + {len(PROJECTS)} community pages + {len(legal.PAGES)} legal pages written")


if __name__ == "__main__":
    main()
