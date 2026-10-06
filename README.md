# Highr

Marketing site for Highr Real Estate, Inc., a US developer of new-build homes. Plain HTML, CSS and JS
plus a compiled Tailwind stylesheet. It needs a static server that maps `/page` to `page.html` (GitHub Pages and `tools/serve.py` do);
Node is needed only to rebuild the Tailwind CSS.

**Demo site.** Highr is a fictional company. Live at https://forhadkhan.github.io/highr/ (GitHub Pages,
branch `main`, root). Every page carries `noindex` (set `DEMO = False` in `tools/build-pages.py` to remove it)
and the footer says so.

## Run

```bash
python3 tools/serve.py 8000
```

Links use short URLs (`/privacy`, `/skyline-haven`, `./` for the home page), as GitHub Pages serves them. Use
`tools/serve.py` locally, which maps them to the `.html` files. Opening the files straight from disk
(`file://`) no longer works for links between pages.

## Pages

| File | What it is |
|---|---|
| `index.html` | Home: hero, trust bar, communities (filter tabs), reviews, about and stats, testimonials, team, how it works, FAQ, call to action, gallery, footer with contact form |
| `skyline-haven.html`, `the-atria-tower.html`, `coastline-residences.html`, `verdant-grove.html` | One page per community: facts, overview, home types and pricing, construction progress, location map, other communities |
| `privacy.html`, `terms.html` | Privacy Policy and Terms of Use (templates, see Notes) |
| `sitemap.xml`, `robots.txt` | Search-engine files |

The community and legal pages are **generated**. Do not edit them by hand.

## Structure

```
index.html          home page markup; source of the header, footer and action bar
css/
  styles.css        custom styles (fonts, buttons, sections, motion)
  tailwind.src.css  Tailwind entry and theme tokens (colors, type scale)
  tailwind.css      compiled output, committed
js/                 reveal, nav, parallax, tabs, counters, slider, form, actionbar, lightbox
tools/
  build-pages.py    generator (standard-library Python)
  projects.py       data for the four communities
  legal.py          text of the Privacy Policy and Terms
  optimize-images.py  responsive photo copies and placeholders (needs Pillow)
assets/             images, logos, icons (SVG, used as CSS masks via .icon-*), fonts (Poppins woff2)
```

## Editing

- **Communities** (name, price, beds, size, status, progress, home types, milestones, nearby places,
  coordinates): edit `tools/projects.py`, then run `python3 tools/build-pages.py`. This rewrites the
  community cards on the home page (between the `projects:start/end` markers) and the four pages.
- **Header, footer, action bar:** edit them in `index.html`, then run the generator so the other pages
  pick up the change.
- **Legal text:** `tools/legal.py`, then run the generator.
- **Domain:** set `SITE_URL` in `tools/build-pages.py` and run it. It writes canonical URLs, Open Graph
  URLs, JSON-LD and `sitemap.xml`. Also change the Open Graph image URL in `index.html`.
- **Styles:** Tailwind utility classes live in the markup, theme tokens in `css/tailwind.src.css`.
  After adding classes run:

  ```bash
  npm install      # first time only
  npm run build:css
  ```

  Run the generator first if you changed a generated page, so the build sees its classes.
- **Floor plans and gallery:** each home type gets a plan in `assets/plans/<slug>-<n>.svg`, generated
  as a schematic layout (labelled "illustrative, not to scale" on the page). To use a real plan, save it as
  `assets/plans/<slug>-<n>.png` (or `.webp`, `.jpg`, or your own `.svg`); the generator keeps real files and only
  overwrites the ones it made. `n` is the row number in `types` (1 = first). A community page shows a Gallery
  section when its entry in `tools/projects.py` has `"gallery": [("file.webp", "alt text"), ...]` with at least
  two images placed in `assets/images/projects/`.
- **Community photos:** put the full-size original (about 1500 px wide, `.webp`) in `assets/images/projects/`, then run
  `pip install pillow` once and `python3 tools/optimize-images.py`. It makes 480, 800 and 1200 px copies and a tiny
  placeholder per photo; `build-pages.py` adds the `srcset` so phones download 20 to 60 KB instead of 150 to 300 KB,
  and the placeholder shows while the photo loads. Commit the copies and `placeholders.json`.
- **Lightbox:** `js/lightbox.js` opens any `<a href="full.jpg" data-lightbox="group" data-caption="…">` in a modal
  viewer (floor plans and gallery use it). Links sharing a group name get previous/next; the overlay is a solid
  dimmed black with no blur. Without JavaScript the link opens the image.
- **Stats** count up from `data-count`, `data-prefix`, `data-suffix` and `data-decimals`.
- **Icons:** add an SVG to `assets/icons/` and a matching `.icon-*` rule in `css/styles.css`.
- **Structured data:** Organization and FAQPage (built from the FAQ markup) on the home page,
  ApartmentComplex or GatedResidenceCommunity plus BreadcrumbList on each community page.

## Replace before launch

All of this is made up for the template:

- Address, phone `(212) 555-0142`, `contact@highr.example`, social links, office hours.
- Licence numbers in the footer (California DRE #01234567, CSLB #1234567) and the trust-bar claims
  (10-year structural warranty, fixed-price contracts).
- Every number in `tools/projects.py`: prices, sizes, availability, progress, dates, nearby travel times,
  coordinates and unit counts. Stats, reviews and testimonials on the home page.
- Photos and plans: each community has one image, so no Gallery section shows, and the floor plans are
  generated schematics. Add real photos (`gallery`) and plans (`assets/plans/`), see Editing.
- `SITE_URL` in `tools/build-pages.py` (currently the GitHub Pages URL), and the og:image URL in `index.html`.
- **Contact form:** name and email are required (phone, tour date, contact method and message are optional);
  errors show under each field. It validates and shows a success message but sends nothing until you set
  `data-endpoint="https://…"` on the `<form data-contact-form>`; it then POSTs the fields as JSON.
  The form on a community page preselects that community (`data-interest`), and `?interest=Name` works
  on any page.
- **Privacy and Terms** are generic US templates, not legal advice. Have a lawyer review them against
  what you actually collect (and add a cookie notice if you add analytics).

## Notes

- **Map:** an OpenStreetMap embed (loads from openstreetmap.org when the page is online).
- **Testimonials** loop and autoplay every 5 s (`data-autoplay` on the slider; remove it to turn off).
  They pause on hover, focus, drag and when off screen.
- **Motion** respects `prefers-reduced-motion`; content stays visible without JavaScript.
- **Mobile:** a bottom bar with Call, WhatsApp and Book a tour appears after the hero.
