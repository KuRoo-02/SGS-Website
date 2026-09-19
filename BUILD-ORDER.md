# SGS — Elementor Build Order

Written for: whoever builds the site in Elementor. Follow top to bottom.

The sequence matters. Each step is built on the one before, so working out of
order means redoing things — most of all the Global Kit, which everything inherits.

**Keep the draft open in a second tab as your visual reference:**
**https://sgs.syahiriyad.com**

Estimated **25–30 hours** if you are comfortable in Elementor. Add 30–50% if you
are learning it. Most of that is steps 4–8.

---

## Step 0 — Hosting (before WordPress)

1. Upload `tools/sgs-preflight.php` to the document root, visit it, fix what it flags
2. Add the `Authorization` header rule to `.htaccess` (§0 of `WORDPRESS-SETUP.md`)
3. Delete `sgs-preflight.php`

Do not skip. `max_input_vars` below 3000 will make long pages lose widgets on save,
silently, and you will not connect the symptom to the cause.

---

## Step 1 — WordPress + plugins  (~45 min)

Follow `WORDPRESS-SETUP.md` §2–§3. Then:

- Elementor ▸ Settings ▸ Features → enable **Flexbox Container**
- Elementor ▸ Settings ▸ General → tick **Disable Default Colors** and **Disable Default Fonts**
- Activate the Elementor Pro licence

Those two "Disable Default" boxes matter: leave them off and the theme fights your
Global Kit all the way through.

---

## Step 2 — Content scaffolding  (~15 min, or ~40 min by hand)

```bash
python tools/wp-scaffold.py --dry-run
python tools/wp-scaffold.py
```

Creates 20 images with alt text, 7 pages, 3 categories, 6 posts, the Primary menu.
If REST is blocked, create them by hand — `WORDPRESS-SETUP.md` §4 Option B lists
every title and slug.

Then set **Settings ▸ Reading** → static front page = Home.

---

## Step 3 — Global Kit + Custom CSS  (~1.5 h) — DO NOT SKIP

**Everything downstream inherits from this.** An hour here saves a day later.

1. `ELEMENTOR-BUILD-GUIDE.md` §2.1 → Global Colors (all 10)
2. §2.2 → Global Fonts (Lexend + Source Sans 3) and the type scale per heading tag
3. §2.3 → layout defaults: content width 1240, padding 24, section padding 104/72/56
4. §2.4 → the four global button styles, all **min-height 48px**
5. Paste **all** of `tools/elementor-custom-css.css` into
   **Site Settings ▸ Custom CSS**

> The bright logo cyan `#00B0EC` fails contrast as text on white. Use `#00769F`
> for text and buttons on light backgrounds. The Global Kit has both — pick the
> right one. This is already decided for you throughout the draft.

**Checkpoint:** create a scratch page, drop a Heading and a Button. They should
already look like the draft with no manual styling. If not, fix it now.

---

## Step 4 — Header + Footer  (~3 h)

`ELEMENTOR-BUILD-GUIDE.md` §3.1 and §3.2. Theme Builder ▸ Header / Footer,
display condition **Entire Site**.

- Header row 1 = utility bar (hidden on mobile)
- Header row 2 = logo + Nav Menu + CTA button, **Motion Effects ▸ Sticky: Top**,
  add CSS class `sgs-glass`
- Nav Menu breakpoint: **Tablet (1024px)**
- Footer = 4 columns `1.7fr / 1fr / 1fr / 1.3fr`, bottom row gets `sgs-footer-legal`

**Put the address, email, phone and hours in a Global Widget.** They appear on every
page; without this you will edit the phone number in sixty places.

**Checkpoint:** header and footer correct on every page, sticky works, hamburger
works at 1024px and below.

---

## Step 5 — Home  (~5 h) — build your reusable parts here

This page contains most of the patterns. Build each one properly, then
**right-click ▸ Save as Template** so later pages are paste jobs.

In order:

1. **Hero** — Container, class `sgs-hero`, background `hero-teleport.jpg` at
   `center 42%`. Badge, H1, lead, two buttons.
2. **Fact strip** — child Container `sgs-strip`, four children `sgs-strip-item`
   at widths 31/23/23/23. → **Save as Template**
3. **Licence row** — three Containers, class `sgs-licence`. → **Save as Template**
4. **Service cards ×6** — Icon Box, class `sgs-card`. Build ONE, style it fully,
   then duplicate five times and change text. → **Save as Template**
5. **Facility split** — two columns, second image absolute with `sgs-float-img`
6. **Stats ×4** — Counter widgets
7. **Why SGS ×6** — reuse the card template
8. **Industries ×4** — reuse the card template
9. **News teaser** — Posts widget, 3 latest
10. **CTA band** — Container, class `sgs-cta-band`. → **Save as Template**
    *(this one reappears on 5 pages)*

Add entrance animations last: Advanced ▸ Motion Effects ▸ Fade In Up, 500ms,
delays 0 / 70 / 140 / 210ms across items in a row.

**Checkpoint:** Home matches the draft at 1440px. Do not move on until it does —
every later page reuses these parts.

---

## Step 6 — About + Services  (~6 h)

Mostly assembly from Step 5's templates.

- Both start with a `sgs-page-hero` Container
- Dark sections get class `sgs-dark`
- About: the facility gallery is an Elementor **Gallery** widget, lightbox on,
  4 columns. Alt text comes from the Media Library, already set by the scaffold.
- Services: the capacity table is inside a `sgs-dark` section, so the table widget
  needs class `sgs-table-dark` or the text will be unreadable
- Services FAQ: Accordion widget, first item open

Section IDs matter — the footer and homepage link to them. Set
Advanced ▸ CSS ID to: `gateway`, `capacity`, `broadband`, `mobility`,
`datacentre`, `technical`, and `facility` on About.

---

## Step 7 — News & Events  (~4 h)

1. **Loop Item template** (Theme Builder ▸ Loop Item) — featured image, Post Terms
   with class `sgs-post-tag`, date, title, excerpt, read-more
2. **News page** — Loop Grid using that template, 3/2/1 columns, pagination.
   Build the page as a normal **Page**, not a category archive
3. **Taxonomy Filter** widget above the grid, pointed at the Loop Grid

> The Taxonomy Filter does **not** work with "Current Query". The query must be
> defined inside the Loop Grid. Build it as an archive and the filter silently
> does nothing.

4. **Featured post** — Posts widget above showing 1 latest, then set the Loop Grid's
   Query ▸ Offset to **1** so it is not repeated
5. **Single Post template** — style the **Post Content** widget's typography once
   (body 17px/1.75, H2 30px with 64px top margin, blockquote 3px `#00B0EC` left
   border). This is what makes SGS's own future posts look right without them
   touching anything.
6. Sticky sidebar: Motion Effects ▸ Sticky, offset 108

Drop the "4 min read" — not a native field, not worth a plugin.

---

## Step 8 — Contact  (~2 h)

- Elementor **Form** widget, fields per the draft
- Actions After Submit: **Email** → `info@satcomgs.com`, plus **Redirect** or an
  inline success message
- Enable the honeypot and reCAPTCHA v3
- Google Maps widget for the location
- Contact links get class `sgs-contact-link` so they meet the 44px tap target
- Floating Buttons widget → **Click to Call**

**Send a real test email and confirm it arrives.** WP Mail SMTP must be configured
first, or it will silently fail.

---

## Step 9 — Responsive pass  (~3 h)

Check every page at **1440 / 1024 / 768 / 390**. Elementor's responsive mode is
per-widget, so expect to adjust font sizes and paddings at tablet and mobile.

Watch for:
- Any horizontal scroll (the usual culprit is a fixed width or a wide table)
- 4-column grids → 2 on tablet, 1 on mobile
- The hero fact strip stacking correctly
- Tables inside a scrollable wrapper
- Buttons still 48px tall

---

## Step 10 — Launch  (~3 h)

`ELEMENTOR-BUILD-GUIDE.md` §9. The ones most often missed:

- **Settings ▸ Reading** → untick *Discourage search engines*
- Elementor ▸ Tools ▸ **Regenerate CSS & Data**
- Re-save Permalinks
- Meta titles + descriptions for all 5 pages (the draft's `<title>` and
  `<meta name="description">` are usable first drafts)
- Test the form again on the live domain
- GA4 + Search Console + sitemap
- Replace the six placeholder news posts with real content, or unpublish them

---

## Sanity checklist before handover

- [ ] Global Kit drives everything — no hard-coded hex in widgets
- [ ] Contact details are a Global Widget, editable in one place
- [ ] Contact form delivers a real email
- [ ] No horizontal scroll at 390px on any page
- [ ] Every image has alt text
- [ ] One H1 per page
- [ ] Keyboard tab order works and focus is visible
- [ ] Placeholder news posts replaced or unpublished
- [ ] SGS has their own admin account, separate from the agency account

---

## If you get stuck

Send a screenshot of the section next to the draft and say which page it is.
Most mismatches are one of: a Global Kit value not applied, a missing CSS class
from `elementor-custom-css.css`, or container padding set on the wrong element.
