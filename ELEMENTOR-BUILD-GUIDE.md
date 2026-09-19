# SGS Website — WordPress + Elementor Build Guide

Written for: the AetherLink developer who will rebuild this draft in WordPress.

This HTML draft is a **visual specification**, not code to be ported. Every pattern in it was
chosen because it maps to a native Elementor widget or setting. Nothing here needs a custom
plugin, a child-theme template, or hand-written JavaScript.

---

## 1. Stack

| Layer | Choice | Note |
|---|---|---|
| Theme | **Hello Elementor** | Unstyled base; nothing to fight |
| Builder | **Elementor Pro** | Required — Theme Builder, Forms, Loop Grid, Sticky, Floating Buttons |
| Layout primitive | **Container (Flexbox)** | Not the legacy Section/Column. Enable in Settings ▸ Features |
| Forms | Elementor Pro Form | Fallback: WPForms Lite / Fluent Forms |
| SEO | Rank Math or Yoast | Titles, meta, XML sitemap |
| Performance | LiteSpeed Cache or WP Rocket | cPanel hosting usually ships LiteSpeed |
| Images | Convert to WebP on upload | ShortPixel / Imagify / LiteSpeed's own converter |

---

## 2. Global Design System

Set these **once** in `Elementor ▸ Site Settings`. Then never pick a raw colour in a widget —
always choose the global swatch. This is what lets SGS restyle the whole site later from one place.

### 2.1 Global Colors

| Elementor slot | Name | Hex | Used for |
|---|---|---|---|
| Primary | SGS Maroon | `#440115` | Headings on light, dark section base, secondary buttons |
| Secondary | SGS Cyan | `#00B0EC` | Accent rules, icons on dark, eyebrow text on dark |
| Text | Ink | `#15191E` | Body copy |
| Accent | CTA Cyan | `#00769F` | Primary buttons and links **on light backgrounds** |
| Custom 1 | SGS Green | `#4A7A1F` | Success/licensing accents, "Events" tag |
| Custom 2 | Muted Text | `#545C66` | Secondary paragraphs |
| Custom 3 | Subtle Text | `#666D76` | Timestamps, hints, captions |
| Custom 4 | Border | `#E1E6EB` | Card and divider strokes |
| Custom 5 | Surface Tint | `#F0F3F6` | Alternating section backgrounds |
| Custom 6 | Maroon Deep | `#24000B` | Dark section gradient start |

> **Do not** use the bright `#00B0EC` for text or button fills on white — it only reaches
> 3.3:1 contrast and fails WCAG AA. The darker `#00769F` is the on-light variant. The bright
> cyan is correct on dark backgrounds. This distinction is already baked into the draft.

### 2.2 Global Fonts

Both are Google Fonts and available natively in Elementor's font picker.

| Slot | Family | Weights | Applied to |
|---|---|---|---|
| Primary | **Lexend** | 400, 500, 600, 700 | All headings, buttons, nav, labels, stat figures |
| Secondary | **Source Sans 3** | 400, 600 | Body copy, lists, table cells |

Typography scale (Site Settings ▸ Typography — set per heading tag):

| Tag | Desktop | Mobile | Weight | Line height | Letter spacing |
|---|---|---|---|---|---|
| H1 | 62px | 36px | 600 | 1.18 | −0.02em |
| H2 | 44px | 28px | 600 | 1.18 | −0.02em |
| H3 | 24px | 20px | 600 | 1.2 | −0.02em |
| H4 | 17px | 17px | 600 | 1.3 | −0.01em |
| Body | 17px | 16px | 400 | 1.65 | 0 |
| Lead | 20px | 17px | 400 | 1.6 | 0 |
| Eyebrow | 12px | 12px | 600 | 1.4 | 0.14em, UPPERCASE |

### 2.3 Layout defaults

- Content width: **1240px**
- Container padding (left/right): **24px**
- Widget space between: **24px**
- Section vertical padding: **104px** desktop / **72px** tablet / **56px** mobile
- Breakpoints: Desktop 1440 · Laptop 1024 · Tablet 768 · Mobile 480 (Elementor defaults are fine)

### 2.4 Global button styles

| Style | Background | Text | Border | Radius | Padding | Min height |
|---|---|---|---|---|---|---|
| Primary | `#00769F` | `#FFFFFF` | none | 8px | 13px 26px | 48px |
| Primary : hover | `#005C7E` | `#FFFFFF` | — | — | — | translateY(−2px) |
| Secondary (maroon) | `#440115` | `#FFFFFF` | none | 8px | 13px 26px | 48px |
| Ghost (on light) | transparent | `#15191E` | 1.5px `#C9D1D9` | 8px | 13px 26px | 48px |
| Ghost (on dark) | rgba(255,255,255,.06) | `#FFFFFF` | 1.5px rgba(255,255,255,.34) | 8px | 13px 26px | 48px |

**Every button must be at least 48px tall.** This is a tap-target requirement, not a preference.

---

## 3. Theme Builder templates

Build these three first, in `Templates ▸ Theme Builder`.

### 3.1 Header (`Header` template, display condition: Entire Site)

Two stacked containers:

**Row 1 — utility bar**
- Container, full width, background `#24000B`, min-height 40px, padding 0 24px
- Left: Icon List widget, **horizontal** layout, 3 items (email / phone / location), icon colour `#00B0EC`, text `#C0B2B7`, 13px
- Right: Text Editor — "● Teleport operational 24 / 7" in `#7EBF41`
- **Hide on Mobile** (or reduce to the email item only)

**Row 2 — main header**
- Container, flex row, align centre, min-height 84px, background `#FFFFFF`
- **Motion Effects ▸ Sticky: Top**, "Sticky on: Desktop, Tablet, Mobile"
- Under Sticky, set *Effects Offset* 0 and add a box-shadow on the sticky state
- Left: **Site Logo** widget, height 42px, plus a Text Editor for "Satcom Gateway Services / SDN BHD · MALAYSIA"
- Centre/right: **Nav Menu** widget
  - Menu: `Primary`
  - Layout: Horizontal · Pointer: **Underline** · Animation: Fade
  - Breakpoint: **Tablet (1024px)** → hamburger below this
  - Mobile dropdown: Full Width, background `#FFFFFF`
  - Typography: Lexend 15px / 500 · Active item 600, colour `#440115`
- Far right: **Button** widget "Talk to our team" (Primary style) → `/contact-us/`, **Hide on Tablet & Mobile**

### 3.2 Footer (`Footer` template, display condition: Entire Site)

- Container, background `#12040A`, padding 80px 24px 0
- Inner container, flex row, 4 columns at `1.7fr / 1fr / 1fr / 1.3fr`, gap 48px 32px
  - **Col 1:** white logo (Image widget) + Text Editor blurb + a pill "Strategic alliance partner of APT Satellite (APStar)"
  - **Col 2:** Heading "COMPANY" + Icon List (no icons) — About SGS, Licences & regulation, Our facility, News & Events, Contact Us
  - **Col 3:** Heading "SERVICES" + Icon List — the six service anchors
  - **Col 4:** Heading "GET IN TOUCH" + Icon List with icons — address, email, phone, business hours
- Divider, then a flex row: copyright left (`© [current year]` via Elementor's shortcode or a dynamic tag), legal links right
- Footer headings: Lexend 13px / 600 / `0.12em` letter-spacing / UPPERCASE / `#FFFFFF`
- Footer links: `#C0B2B7`, hover `#00B0EC`

### 3.3 Single Post (`Single Post` template, condition: All Posts)

See §5.2.

---

## 4. Reusable pattern → widget map

This is the core reference. Left column is the CSS class in the draft; right column is what to build.

| Draft pattern | Elementor build |
|---|---|
| `.hero` | Container, min-height 82vh, **Background: Image** (`hero-teleport.jpg`), position `center 42%`, **Background Overlay** = the two-layer gradient in §6. Inner container flex column, content max-width 720px |
| `.hero__strip` | Child container pinned at the bottom of the hero: flex row, 4 equal columns, background `rgba(18,4,10,.55)`, backdrop blur 8px, 1px left dividers `rgba(255,255,255,.11)`. Each cell = Heading (24px) + Text (13px) |
| `.page-hero` | Container with **Background: Gradient**, padding 112px 0, breadcrumb via Rank Math/Yoast breadcrumb shortcode or the Breadcrumbs widget |
| `.card` (service/feature) | **Icon Box** widget. Icon position Top, icon size 26px in a 52px rounded box, card background `#FFFFFF`, border 1px `#E1E6EB`, radius 14px, padding 32px. Hover: `translateY(-4px)` + shadow |
| `.card--dark` | Same Icon Box, background `rgba(255,255,255,.045)`, border `rgba(255,255,255,.14)`, heading `#FFFFFF`, text `#C0B2B7`, **`.card__num` label must use the bright `#00B0EC`** |
| `.licence-card` | Icon Box, *left* icon position — but replace the icon with a Text widget badge ("NFP"), 4px left border `#7EBF41` |
| `.stats` / `[data-count-to]` | **Counter** widget ×4 in a 4-column container. Number: Lexend 46px/600 `#440115`. Suffix for "+", "km", "/7" |
| `.tick-list` | **Icon List** widget, check icon, icon colour `#4A7A1F`, 10px spacing |
| `.pill` / `.pill-row` | Icon List set to **horizontal**, or Button widgets styled as pills. Any *clickable* pill needs min-height 44px |
| `.accordion` | **Accordion** widget. Toggle icon: plus → rotates 45° when open. First item open by default |
| `.tabs` | **Tabs** widget, horizontal, active border-bottom 3px `#00B0EC` |
| `.gallery` | **Gallery** widget (Justified or Grid), Lightbox **On**, 4 columns, 12px gap, caption overlay on hover |
| `.data-table` | **TablePress** plugin, or a plain HTML Table widget. On dark sections override the text to `#F7F3F4` — the default light-mode table colours are unreadable there |
| `.spec-table` | Icon List with two-column rows, or TablePress with borders hidden |
| `.timeline` | **Icon List** vertical with a connecting line, or the Timeline widget in any add-on pack. Not worth a plugin on its own — an Icon List is fine |
| `.media-stack` | Two Image widgets in a container: main image, plus a second absolutely positioned (Advanced ▸ Position: Absolute, offset right −18px / bottom −28px) with a 5px white border |
| `.cta-band` | Container, gradient background, flex row, `space-between`, wraps on mobile |
| `.post-card` | **Loop Grid** widget + a Loop Item template (see §5.1) |
| `.float-actions` | **Floating Buttons** widget — "Click to Call" |
| `[data-reveal]` | Advanced ▸ **Motion Effects ▸ Entrance Animation: Fade In Up**, duration 500ms. Stagger via the Animation Delay field: 0 / 70 / 140 / 210ms |

---

## 5. News & Events

### 5.1 Archive (the `news.html` layout)

1. Create a **Loop Item** template (`Templates ▸ Theme Builder ▸ Loop Item`):
   - Container, radius 14px, `overflow: hidden`, border 1px `#E1E6EB`
   - Featured Image (dynamic), aspect ratio 16:10, hover scale 1.05
   - Post Terms widget positioned absolute top-left = the category tag.
     Colour per category: Company News `#00769F`, Events `#4A7A1F`, Technical Updates `#440115`
   - Post Info (date) → the meta row
   - Post Title (H3, links to post)
   - Post Excerpt, 20 words
   - Button "Read more" with arrow icon
2. On the News page, drop a **Loop Grid** widget:
   - Source: Posts · Template: the Loop Item above
   - Columns 3 / 2 / 1 · Pagination: Numbers + Previous/Next
   - First post: give it `grid-column: span 2` via a CSS class for the featured treatment (optional)
3. Category filter row: either Elementor Pro's **Taxonomy Filter** widget wired to the Loop Grid,
   or a simple Nav Menu of category links. The filter widget is the better UX.

### 5.2 Single article (the `news-article.html` layout)

`Single Post` template, two-column container `1fr / 320px`:

- **Main column:** Post Title (H1) in the dark hero container, then Featured Image, then **Post Content**
- Style the Post Content widget's typography once — that is what makes SGS's own posts look right
  without them touching any settings: body 17px/1.75, H2 30px with 64px top margin,
  blockquote with a 3px `#00B0EC` left border
- **Sidebar:** sticky (Advanced ▸ Motion Effects ▸ Sticky, offset 108px)
  - Posts widget, 4 recent, title + date only
  - Categories list
  - A dark CTA card → Contact
- Below: Posts widget, 3 related by category
- Share: Elementor Pro **Share Buttons** widget (LinkedIn, Email)

### 5.3 Categories to create

`Company News` · `Events` · `Technical Updates`

---

## 6. Exact gradient values

Copy these into the Background Overlay / Background Gradient fields. Elementor's gradient UI only
does two stops, so for the multi-layer ones use **Advanced ▸ Custom CSS** on the container, or
paste them into the theme's Additional CSS against a container CSS class.

**Dark section** (`.section--dark`)
```css
background:
  radial-gradient(1100px 520px at 12% -10%, rgba(0,176,236,.16), transparent 62%),
  radial-gradient(760px 420px at 92% 108%, rgba(126,191,65,.13), transparent 60%),
  linear-gradient(160deg, #24000B 0%, #12040A 100%);
```

**Hero scrim** (over the photo)
```css
background:
  linear-gradient(100deg, rgba(36,0,11,.94) 0%, rgba(36,0,11,.80) 38%,
                  rgba(18,4,10,.42) 72%, rgba(18,4,10,.30) 100%),
  linear-gradient(to top, rgba(18,4,10,.72) 0%, transparent 42%);
```

**Page hero** (interior pages)
```css
background:
  radial-gradient(900px 400px at 8% 0%, rgba(0,176,236,.20), transparent 60%),
  radial-gradient(620px 340px at 96% 100%, rgba(126,191,65,.14), transparent 60%),
  linear-gradient(150deg, #24000B 0%, #12040A 100%);
```

**CTA band**
```css
background:
  radial-gradient(760px 340px at 82% 12%, rgba(0,176,236,.26), transparent 62%),
  radial-gradient(560px 320px at 6% 96%, rgba(126,191,65,.18), transparent 60%),
  linear-gradient(120deg, #340010 0%, #12040A 100%);
```

If you prefer to avoid Custom CSS entirely: use a single `160deg` linear gradient from `#24000B`
to `#12040A` and stack one Elementor "Background Overlay" radial on top. It is ~90% of the effect.

---

## 7. Content management — what SGS must be able to edit

The brief commits to SGS updating routine content without developer help. That constrains how you
build, so treat these as requirements, not nice-to-haves:

| SGS needs to | Build so that |
|---|---|
| Edit any body text | It lives in a Text Editor / Heading widget, **never** baked into a Custom CSS block or an image |
| Swap any photo | It is an Image widget or a container Background Image, not a CSS `background` in Custom CSS |
| Add a news post | Posts → Add New. The Loop Item template handles all styling. No page editing needed |
| Update the phone / email / address | Put each in a **Global Widget** (or use a plugin like "Reusable Blocks"). Then one edit updates the header, footer and contact page together. **This matters — the phone number appears 6+ times per page** |
| Upload a PDF / brochure | Media Library + a Button widget with a File link |
| Change business hours | Same Global Widget as the contact block |

Also: name every Elementor container and widget sensibly in the Navigator panel. SGS's team will
be looking at that tree, not at markup.

---

## 8. Accessibility requirements (already met in the draft — keep them)

These were verified in the draft with an automated audit; do not regress them:

- **Text contrast ≥ 4.5:1** on all body text, ≥ 3:1 on large text. This is why the CTA cyan is
  `#00769F` and not `#00B0EC`, and why the green is `#4A7A1F` and not `#7EBF41`.
- **Tap targets ≥ 44×44px** for every link, button and form control.
- Every image needs real alt text. Elementor pulls it from the Media Library — fill it in there
  once per image rather than per widget.
- One `<H1>` per page. In Elementor, set page hero titles to H1 and every other heading to H2/H3.
- Keep focus outlines visible. If the theme removes them, add:
  `:focus-visible { outline: 3px solid #00B0EC; outline-offset: 3px; }`
- Enable "Respect reduced motion" behaviour — keep entrance animations short (≤500ms) and
  never use them on text the user must read immediately.
- The mobile menu must not be positioned off-screen with a transform. Elementor's own dropdown is
  fine; a custom slide-in panel will add horizontal page scroll (this bit us in the draft).

---

## 9. Launch checklist

- [ ] SSL issued and forced (cPanel AutoSSL + "Force HTTPS" in the cache plugin)
- [ ] Permalinks: Post name
- [ ] Pages: Home, About Us, Our Services, News & Events, Contact Us + Privacy Notice, Terms of Use
- [ ] `Primary` menu created and assigned; Home set as the static front page
- [ ] Elementor Form on Contact delivering to `info@satcomgs.com`, **plus** an SMTP plugin
      (WP Mail SMTP) — cPanel PHP mail lands in spam
- [ ] Form: honeypot + reCAPTCHA v3 enabled
- [ ] Click-to-call number verified live on a real handset
- [ ] Google Search Console verified + XML sitemap submitted
- [ ] GA4 property connected (Site Kit or a GTM container)
- [ ] Meta titles and descriptions written for all 5 pages (the draft's `<title>` and
      `<meta name="description">` are usable first drafts)
- [ ] OG image set (the hero teleport photo works well)
- [ ] Content migrated from the existing EasyStore site
- [ ] 301 redirects mapped from old EasyStore URLs to the new structure
- [ ] Images converted to WebP; LCP image (hero) preloaded and **not** lazy-loaded
- [ ] 404 page styled
- [ ] Test at 375 / 768 / 1024 / 1440px
- [ ] DNS cutover + post-launch smoke test of the form and phone links

---

## 10. Known open items

These need SGS to confirm before launch — they are placeholders in the draft:

1. **Phone number.** The company profile lists `+066944990`. The draft renders this as
   `+60 6-694 4990` (Negeri Sembilan landline format) in all `tel:` links.
   **Confirm the correct number before launch.**
2. **News & Events content.** All six articles in the draft are placeholder copy written to
   demonstrate the layout. SGS supplies the real posts.
3. **Map embed.** The draft uses OpenStreetMap so it works offline. Swap for the Google Maps
   embed via Elementor's Google Maps widget.
4. **Privacy Notice / Terms of Use.** Linked in the footer, not yet written.
5. **Social profiles.** APStar links LinkedIn and Facebook; no SGS handles were supplied.
6. **Tier III.** The profile says "Tier III Data Centra". The draft says "Tier III-class"
   throughout, because an uncertified claim of Uptime Institute Tier III certification is a
   commercial risk. Confirm whether SGS holds actual certification — if so, the wording can be
   strengthened and the certificate badge displayed.
