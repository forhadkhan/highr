# Highr

Single-page marketing site for Highr Real Estate, Inc., a US real-estate company. Plain HTML, CSS and
JS with the Tailwind Play CDN. No build step, no dependencies to install.

## Run

Serve the folder with any static server (the page also opens straight from `index.html`):

```bash
python3 -m http.server 8000
```

## Page sections

Header (black, hides on scroll down) · Hero · Featured projects (filter tabs) · Reviews quote ·
About and stats · Testimonials carousel · Core team · Call to action · Marquee · Instagram gallery
(pinned, the footer slides over it) · Footer with contact form.

## Structure

```
index.html          page markup (semantic HTML) and Tailwind theme tokens
css/styles.css      custom styles on top of Tailwind (fonts, buttons, sections, motion)
js/
  reveal.js         scroll reveal (data-reveal, data-stagger, data-split)
  nav.js            header: mobile menu, hide on scroll, active link
  parallax.js       image parallax (data-parallax) and gallery drift (data-drift)
  tabs.js           project filter tabs
  counters.js       count-up stats
  slider.js         testimonials carousel
  form.js           contact form validation
assets/
  images/           photos (projects, team, social, hero, about) and og-image.jpg
  logos/            Highr logo, dark and white (SVG)
  icons/            favicon and UI icons (SVG, used as CSS masks via .icon-*)
  fonts/            self-hosted Poppins (woff2)
```

## Editing content

- **Text, cities, stats, team and testimonials** are plain markup in `index.html`. Stats count up
  from `data-count`, `data-prefix`, `data-suffix` and `data-decimals`.
- **Colors and type sizes** are tokens in the `@theme` block inside `index.html`.
- **Icons:** add an SVG to `assets/icons/` and a matching `.icon-*` rule in `css/styles.css`.

## Notes

- **Placeholders:** the San Francisco address, the `(212) 555-0142` phone number,
  `contact@highr.example` and the social links in the footer are made up. Replace them before launch.
- **Contact form:** it validates and shows a success message, but sends nothing until you set
  `data-endpoint="https://…"` on the `<form data-contact-form>`; it then POSTs the fields as JSON.
- **Testimonials** loop infinitely and autoplay every 5 s (`data-autoplay` on the slider; remove it to
  turn off). They pause on hover, focus, drag and when off screen.
- **Motion** respects `prefers-reduced-motion`; content stays visible without JavaScript.
- **Tailwind Play CDN** compiles in the browser and is meant for development. For production, swap it
  for the Tailwind CLI build (the `@theme` block in `index.html` moves into your CSS).
- **Not included:** Privacy Policy and Terms of Service pages.
