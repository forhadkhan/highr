#!/usr/bin/env python3
"""Regenerate the community pages (<slug>.html) and the project cards on index.html.

    python3 tools/build-pages.py

Data lives in tools/projects.py. The header, footer, action bar and Tailwind theme of every
generated page are copied from index.html, so edit them there and run this script again.
Standard library only; the site itself needs no build step.
"""
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from projects import PROJECTS  # noqa: E402
import legal  # noqa: E402

INDEX = ROOT / "index.html"
SITE_NAME = "Highr"
PHONE_TEL = "+12125550142"


def card(p, i):
    ongoing = p["status"] == "ongoing"
    if ongoing:
        status = (f'<span class="status-ring" style="--p: {p["progress"]}" aria-hidden="true"></span>'
                  f'<span>{p["progress"]}% built · Completes {p["eta"]}</span>')
    else:
        status = ('<span class="status-ring status-ring--done" aria-hidden="true"><i class="icon icon-check-circle"></i></span>'
                  '<span>Ready to move in</span>')
    delay = 0 if i % 2 == 0 else 120
    return f'''            <li class="project-item" data-status="{p["status"]}" data-reveal data-reveal-delay="{delay}">
              <article class="flex h-full flex-col gap-6 md:gap-8">
                <div class="project-media" data-reveal="clip">
                  <img src="assets/images/projects/{p["image"]}" alt="{escape(p["alt"])}" width="1500" height="1002" loading="lazy" class="h-full w-full object-cover">
                </div>
                <div class="flex flex-col gap-4 md:gap-6">
                  <p class="flex items-center gap-3 text-body-lg">{status}</p>
                  <h3 class="text-h3"><a href="{p["slug"]}.html" class="card-link">{p["name"]}</a></h3>
                  <p class="max-w-[607px] text-ink-700">{p["card"]}</p>
                </div>
                <ul class="mt-auto flex flex-wrap items-center gap-x-8 gap-y-3 text-body-lg">
                  <li class="flex items-center gap-3"><i class="icon icon-building text-ink-700"></i>{p["type"]}</li>
                  <li class="flex items-center gap-3"><i class="icon icon-map-pin text-ink-700"></i>{p["city"]}</li>
                </ul>
                <p class="flex flex-wrap items-center justify-between gap-x-6 gap-y-2 border-t border-ink-100 pt-5 text-body-lg">
                  <span>From <strong class="font-medium">{p["price"]}</strong> · {p["beds"]} · {p["size"]}</span>
                  <span class="card-more" aria-hidden="true">View details <i class="icon icon-chevron-right"></i></span>
                </p>
              </article>
            </li>
'''


def patch_index(src):
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
    tailwind = grab(src, "<!-- Tailwind v4 Play CDN -->", "</style>")
    # Subpage links: sections of the home page get an index.html prefix; #contact stays local.
    header = header.replace('href="#top"', 'href="index.html"').replace('aria-label="Highr, back to top"', 'aria-label="Highr, home"')
    header = re.sub(r'href="#(projects|about|process|testimonial|faq|visit)"', r'href="index.html#\1"', header)
    footer = footer.replace('<a href="#top" aria-label="Highr, back to top" data-reveal>', '<a href="index.html" aria-label="Highr, home" data-reveal>')
    return header, footer, actionbar, tailwind


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
            <a href="{o["slug"]}.html" class="other-card">
              <div class="project-media"><img src="assets/images/projects/{o["image"]}" alt="{escape(o["alt"])}" width="1500" height="1002" loading="lazy" class="h-full w-full object-cover"></div>
              <span class="mt-5 flex flex-col gap-1.5">
                <span class="text-h4">{o["name"]}</span>
                <span class="text-ink-700">{o["city"]} · From {o["price"]}</span>
              </span>
            </a>
          </li>
''' for i, o in enumerate(others))

    if ongoing:
        progress_head = f'''<p class="text-h1 leading-none" data-count="{p["progress"]}" data-prefix="" data-suffix="%" data-decimals="0">{p["progress"]}%</p>
            <div class="meter" role="progressbar" aria-label="Construction progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{p["progress"]}"><span style="width: {p["progress"]}%"></span></div>
            <p class="max-w-[420px] text-ink-700">Construction is {p["progress"]}% complete. Handover is planned for {p["eta"]}, and reserved buyers receive progress updates throughout the build.</p>'''
        progress_title = "Construction progress"
    else:
        progress_head = f'''<p class="text-h1 leading-none">Done</p>
            <p class="max-w-[420px] text-ink-700">{p["name"]} was completed in {p["eta"].replace("Completed ", "")} and is lived in today. Homes marked move-in ready can be handed over within weeks of reservation.</p>'''
        progress_title = "Built and lived in"

    title = f'{p["name"]} – {p["type"]} in {p["city"]} | {SITE_NAME}'
    desc = f'{p["tagline"]} Homes from {p["price"]}. See pricing, home types and location.'

    return f'''<!DOCTYPE html>
<html lang="en-US" class="scroll-smooth">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta name="theme-color" content="#ffffff">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_US">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(p["tagline"])}">
  <meta property="og:image" content="assets/images/og-image.jpg">
  <meta name="twitter:card" content="summary_large_image">

  <link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">

  <link rel="preload" href="assets/fonts/poppins-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/poppins-500.woff2" as="font" type="font/woff2" crossorigin>

  <link rel="stylesheet" href="css/styles.css">

  {tailwind}
</head>

<body class="bg-white font-sans text-base font-medium text-ink antialiased">
  <script>document.documentElement.classList.add('js');</script>
  <a href="#main" class="skip-link">Skip to content</a>

  {header}

  <main id="main">
    <section id="top" class="hero bg-white" aria-labelledby="project-title">
      <div class="container-page">
        <div class="flex flex-col items-start gap-6 md:gap-8">
          <nav class="crumbs" aria-label="Breadcrumb" data-reveal="fade">
            <ol>
              <li><a href="index.html#projects">Communities</a></li>
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
      <img src="assets/images/projects/{p["image"]}" alt="{escape(p["alt"])}" width="1500" height="1002" fetchpriority="high" class="hero-media__img" data-parallax="0.12">
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

    <section id="homes" class="section-y bg-smoke" aria-labelledby="types-title">
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
            <span class="btn__label"><span>Request floor plans</span><span aria-hidden="true">Request floor plans</span></span>
          </a>
          <p class="max-w-[460px] text-sm text-ink-700">Prices are starting prices and may change. Floor plans, finish packages and current availability are sent by your advisor.</p>
        </div>
      </div>
    </section>

    <section id="progress" class="section-y bg-white" aria-labelledby="progress-title">
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
  <link rel="icon" href="assets/icons/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="assets/icons/apple-touch-icon.png">
  <link rel="preload" href="assets/fonts/poppins-400.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/poppins-500.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="css/styles.css">

  {tailwind}
</head>

<body class="bg-white font-sans text-base font-medium text-ink antialiased">
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
    for page in legal.PAGES:
        (ROOT / f'{page["slug"]}.html').write_text(legal_page(page, parts), encoding="utf-8")
    print(f"index.html cards + {len(PROJECTS)} community pages + {len(legal.PAGES)} legal pages written")


if __name__ == "__main__":
    main()
