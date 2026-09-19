# SGS — Website Design Draft

Static HTML/CSS draft of the new **Satcom Gateway Services Sdn Bhd** website, built as a
click-through design for client sign-off before the WordPress + Elementor build.

**To view:** open `index.html` in any browser. No server, build step or install needed.

---

## Pages

| File | Page | Notes |
|---|---|---|
| `index.html` | Home | Hero, 6 service lines, facility, fleet, stats, industries, news teaser |
| `about.html` | About Us | Company profile, MCMC licences, APStar alliance, facility gallery |
| `services.html` | Our Services | The 6 service sections, capacity table, FAQ |
| `news.html` | News & Events | Post grid, category filter, pagination |
| `news-article.html` | Article template | Single-post layout with sidebar and related posts |
| `contact.html` | Contact Us | Enquiry form, contact details, map, click-to-call |

Every page is responsive (375 / 768 / 1024 / 1440px) and carries the floating click-to-call
button.

---

## The six service lines

The brief specified six service sections. The company profile lists seven service names, so
**Satellite Backhaul** is folded into section 03 rather than dropped — all seven topics are
covered across the six sections:

1. Teleport & Gateway Services
2. Satellite Capacity Leasing
3. Satellite Broadband, Enterprise Networks **& Backhaul**
4. Satellite Mobility
5. Data Centre & Colocation Services
6. Technical & Ground-Segment Services

If SGS would rather see seven separate sections, splitting 03 back into two is a small change.

---

## Design system

Sampled from the SGS logo, then extended into an accessible ramp.

| Role | Hex | |
|---|---|---|
| Brand maroon | `#440115` | logo; dark sections, secondary buttons |
| Brand cyan | `#00B0EC` | logo; accents and icons **on dark** |
| Brand green | `#7EBF41` | logo; status indicators |
| CTA cyan (on light) | `#00769F` | primary buttons and links on white |
| Accessible green | `#4A7A1F` | licensing accents, "Events" tag |
| Ink | `#15191E` | body text |

The bright logo cyan and green only reach ~3.3:1 and ~2.9:1 contrast on white, which fails
WCAG AA for text. The draft therefore uses darkened variants wherever the colour carries text,
and the original brand colours wherever they sit on dark backgrounds or are purely decorative.
The logo itself is untouched.

**Type:** Lexend (headings, UI) + Source Sans 3 (body). Both are Google Fonts, both are
available natively in Elementor.

---

## Built to be rebuilt in Elementor

Every pattern maps to a stock Elementor widget — no custom plugin, child theme or bespoke
JavaScript is required. See **`ELEMENTOR-BUILD-GUIDE.md`** for the full widget-by-widget map,
global colour/font setup, Theme Builder templates, gradient values and launch checklist.

The JavaScript in `assets/js/main.js` exists only so the draft is clickable. Each function is
labelled with the Elementor feature that replaces it:

| Draft JS | Elementor equivalent |
|---|---|
| mobile nav | Nav Menu widget (built-in hamburger) |
| sticky header | Motion Effects ▸ Sticky |
| scroll reveal | Motion Effects ▸ Entrance Animation |
| counters | Counter widget |
| accordion / tabs | Accordion / Tabs widgets |
| gallery lightbox | Gallery widget lightbox |
| contact form | Elementor Pro Form widget |

---

## Quality checks run on this draft

- **Contrast:** automated audit across all 6 pages — 0 failures against WCAG AA
  (4.5:1 body, 3:1 large text)
- **Tap targets:** all links, buttons and controls ≥ 44×44px
- **Responsive:** no horizontal scroll at 390 / 820 / 1440px on any page
- **Markup:** no unclosed tags, no duplicate IDs, all internal links and anchors resolve,
  all `aria-controls` targets exist, every image has alt text, one `<h1>` per page
- **JS:** no console errors on any page
- Keyboard accessible: skip link, visible focus rings, arrow-key tabs, Esc-to-close
  lightbox and menu, `prefers-reduced-motion` respected

---

## Content sources

- `Materials/SGS Company Profile 2026.pdf` — facility specs, satellite fleet, coordinates,
  fibre topology, target industries, 2026 product additions
- `Materials/WEBSITEEEE.docx` — company profile, licensing, service descriptions, contact details
- `Materials/Facility Photos/` — 18 photos, optimised into `assets/img/`
- `https://www.apstar.com/` — parent-company reference for tone and information architecture

All body copy is drawn from the two supplied documents. Headlines and connective copy were
written for the web.

---

## Needs confirmation before build

1. **Phone number** — the profile shows `+066944990`; the draft renders `+60 6-694 4990`
   in all `tel:` links. Please confirm the correct number.
2. **News & Events articles** — all six posts are placeholder copy demonstrating the layout.
3. **"Tier III"** — the draft says "Tier III-class" throughout. If SGS holds actual Uptime
   Institute certification, the wording can be strengthened and a badge added.
4. **Privacy Notice / Terms of Use** — linked in the footer, not yet written.
5. **Social profiles** — no SGS handles supplied.
6. **Map** — draft uses OpenStreetMap so it works offline; swap to Google Maps in the build.

---

## Notes

- `assets/img/facility-4.jpg` and `switchboard-2.jpg` are optimised but unused — kept as
  spares for the WordPress build.
- The maroon **"DRAFT DESIGN PREVIEW"** bar at the top of each page is a review aid.
  Delete the `<div class="draft-flag">` block before any client-facing deployment.
- Photos were resized to 1400px wide and re-encoded at quality 80 (~150–260KB each, down from
  ~900KB). Convert to WebP during the WordPress build.

---

## Structure

```
Website/
├── index.html · about.html · services.html
├── news.html · news-article.html · contact.html
├── assets/
│   ├── css/style.css      design system + all components, commented by section
│   ├── js/main.js         ~250 lines, no dependencies
│   └── img/               18 optimised photos + logo (dark and light variants)
├── ELEMENTOR-BUILD-GUIDE.md
└── README.md
```
