# Highr

Static real-estate / architecture landing page. Plain HTML, CSS and JS with the Tailwind Play CDN.
No build step.

## Run

Serve the folder with any static server (the page also opens straight from `index.html`):

```bash
python3 -m http.server 8000
```

## Structure

```
index.html          page markup (semantic HTML)
css/styles.css      design tokens + custom styles on top of Tailwind
js/
  reveal.js         scroll reveal (data-reveal, data-stagger, data-split)
  nav.js            header: mobile menu, hide on scroll, active link
  parallax.js       image parallax (data-parallax) and gallery drift (data-drift)
  tabs.js           project filter tabs
  counters.js       count-up stats
  slider.js         testimonials carousel
  form.js           contact form validation
assets/
  images/           photos (projects, team, social, hero, about, og-image)
  logos/            brand logos (SVG)
  icons/            favicon and UI icons (SVG, used as CSS masks)
  fonts/            self-hosted Poppins
```

## Notes

- **Contact form:** it validates and shows a success message, but sends nothing until you set
  `data-endpoint="https://…"` on the `<form data-contact-form>`; it then POSTs the fields as JSON.
- **Placeholders:** the address, phone number, `contact@highr.example` and social links are
  placeholders. Replace them in the footer.
- **Tailwind Play CDN** compiles in the browser and is meant for development. For production,
  swap it for the Tailwind CLI build (the `@theme` block in `index.html` moves into your CSS).
- **Testimonials** autoplay every 5 s (`data-autoplay` on the slider; remove it to turn off) and pause on hover, focus, drag and off screen.
- **Motion** respects `prefers-reduced-motion`; content stays visible without JavaScript.
