# SGS — WordPress Setup Runbook (cPanel shared hosting)

Written for: whoever provisions the hosting and installs WordPress for SGS.

Order of work:

1. **This file** — hosting prerequisites, WordPress install, plugins, scaffolding
2. **`ELEMENTOR-BUILD-GUIDE.md`** — the Global Kit, Theme Builder templates and page layouts
3. **`tools/wp-scaffold.py`** — optional: creates the media, pages, categories, posts and menu over the REST API

---

## 1. Hosting prerequisites — do this BEFORE installing anything

Most "Elementor is broken on shared hosting" problems are these five settings. Shared
cPanel plans ship with defaults well below what Elementor needs, and the symptoms are
misleading: the editor spins forever, saves silently fail, or complex pages lose widgets.

In cPanel ▸ **MultiPHP INI Editor** (or **Select PHP Version ▸ Options**):

| Setting | Minimum | Recommended | What breaks without it |
|---|---|---|---|
| PHP version | 8.1 | **8.2 / 8.3** | Elementor drops support for old PHP |
| `memory_limit` | 256M | **512M** | Editor white-screens on long pages |
| `max_execution_time` | 120 | **300** | Saving a long page times out |
| `max_input_vars` | 3000 | **5000** | **Widgets silently vanish on save** |
| `post_max_size` | 32M | **64M** | Template/kit imports fail |
| `upload_max_filesize` | 32M | **64M** | Image uploads rejected |

`max_input_vars` is the one that causes the most wasted hours — the page saves without
error and parts of the layout are simply gone. Set it before building, not after.

Also enable in cPanel ▸ **Select PHP Version ▸ Extensions**:
`imagick` (or `gd`), `curl`, `mbstring`, `zip`, `intl`, `dom`, `xml`.

**Verify after install** with Tools ▸ Site Health ▸ Info ▸ Server. Do not trust the
cPanel UI alone — some hosts override per-domain.

---

## 2. Install WordPress

cPanel ▸ **WordPress Toolkit** or **Softaculous**:

- Install to the **document root** of the domain, not a `/wp` subfolder
- Admin username: **not** `admin` — use something unguessable
- Strong password, stored in a password manager
- Site title: `Satcom Gateway Services Sdn Bhd`
- Tagline: `Carrier-neutral satellite teleport and data centre in Malaysia`
- Tick "limit login attempts" if the installer offers it

Then in wp-admin:

- **Settings ▸ Permalinks** → **Post name** (required — the pretty URLs in the draft depend on it)
- **Settings ▸ Reading** → tick *Discourage search engines* **while building**, untick at launch
- **Settings ▸ Discussion** → untick *Allow people to submit comments* (a B2B teleport site has no use for comments)
- **Settings ▸ General** → timezone `Asia/Kuala_Lumpur`, date format `j F Y`
- Delete the sample page, the "Hello World" post and the default plugins (Akismet/Hello Dolly) if unused

### SSL

cPanel ▸ **SSL/TLS Status** → run **AutoSSL** (free Let's Encrypt). Then set both the
WordPress Address and Site Address to `https://`, and force HTTPS in the cache plugin
or via `.htaccess`.

---

## 3. Theme and plugins

**Theme:** Hello Elementor (free, from the WordPress repo). Do not buy a theme — it would
only fight the design.

**Plugins — install these and nothing else to start:**

| Plugin | Why |
|---|---|
| **Elementor** (free) | Base builder |
| **Elementor Pro** | Required. Theme Builder, Loop Grid, Taxonomy Filter, Forms, Sticky, Share Buttons |
| **Rank Math** *or* **Yoast SEO** | Titles, meta descriptions, XML sitemap, breadcrumbs |
| **WP Mail SMTP** | **Required.** cPanel PHP `mail()` lands in spam — the contact form will appear to work and silently not arrive |
| **LiteSpeed Cache** *or* **WP Super Cache** | Use LiteSpeed only if the host runs LiteSpeed (most cPanel hosts do) |
| **ShortPixel** *or* **Imagify** | WebP conversion |
| **Wordfence** *or* **Solid Security** | Basic hardening on shared hosting |
| **UpdraftPlus** | Scheduled offsite backups |

Activate the Elementor Pro licence before building — some widgets are hidden until it is.

**Elementor ▸ Settings ▸ Features:** enable **Flexbox Container**. The whole build guide
assumes containers, not the legacy Section/Column.

**Elementor ▸ Settings ▸ General:** set *Disable Default Colors* and *Disable Default Fonts*
so the theme cannot override the Global Kit.

---

## 4. Scaffolding the content

Two ways. Both end in the same place.

### Option A — automated over the REST API (faster, repeatable)

1. In wp-admin: **Users ▸ Profile ▸ Application Passwords** → add one named `sgs-scaffold`, copy the generated password
2. Add to `.env.deploy` in the project root (never committed):

   ```dotenv
   WP_URL=https://the-client-domain.com
   WP_USER=your-admin-username
   WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
   ```

3. Dry run first, then apply:

   ```bash
   python tools/wp-scaffold.py --dry-run
   python tools/wp-scaffold.py
   ```

This uploads all 18 images with alt text, creates the 6 pages, the 3 News categories,
the 6 posts with featured images, and the primary menu. It is idempotent — running it
twice updates rather than duplicates.

It does **not** build Elementor layouts. See the honest limitation in §6.

### Option B — by hand

Create in this order, then follow `ELEMENTOR-BUILD-GUIDE.md`:

**Pages** (Pages ▸ Add New, leave content empty — Elementor fills them):

| Title | Slug |
|---|---|
| Home | `home` (then Settings ▸ Reading → set as static front page) |
| About Us | `about-us` |
| Our Services | `our-services` |
| News & Events | `news-events` |
| Contact Us | `contact-us` |
| Privacy Notice | `privacy-notice` |
| Terms of Use | `terms-of-use` |

**Post categories:** `Company News`, `Events`, `Technical Updates`

**Menu** (Appearance ▸ Menus), named `Primary`:
Home · About Us · Our Services · News & Events · Contact Us

**Media:** upload everything from `assets/img/`, and fill in the **alt text** on each
image in the Media Library — Elementor inherits it from there, so doing it once saves
doing it per widget, and it is an accessibility requirement.

---

## 5. Then build the design

Hand over to **`ELEMENTOR-BUILD-GUIDE.md`**:

- §2 Global Kit — colours, fonts, type scale, button styles *(do this first; everything depends on it)*
- §3 Theme Builder — header, footer, single post
- §4 Pattern → widget map
- §5 News & Events
- §6 Gradient values
- §9 Launch checklist

Keep the live draft open beside the editor as the visual reference: **https://sgs.syahiriyad.com**

---

## 6. What cannot be automated — read before expecting magic

Elementor stores each page's layout as internal JSON in the `_elementor_data` post meta.
That field is **not exposed to the REST API**, so a page created over the API arrives as
an empty Elementor canvas. You get the page, not the design.

Elementor layouts can be imported as `.json` templates (Templates ▸ Import), and that
JSON can be generated — but the schema is internal, undocumented and version-sensitive.
Expect a generated kit to land at roughly 70–80% and need fixing by hand, not to import
perfectly first time.

**So the realistic split is:**

| Automatable | Manual |
|---|---|
| Media + alt text | Header / footer templates |
| Pages, posts, categories | Page section layouts |
| Menus | Loop Item template |
| Site settings, permalinks | Global Kit (fast by hand anyway) |
| Plugin install *(if WP-CLI available)* | Anything visual |

Shared cPanel plans sometimes expose **Terminal** with WP-CLI. If yours does,
`wp plugin install`, `wp option update` and `wp post create` are faster than the API for
setup. Check cPanel ▸ Terminal before doing it by hand.

---

## 7. Migrating to production

If you build on a staging subdomain first (e.g. `staging.clientdomain.com`):

1. **UpdraftPlus** (Migrate/Clone) or **All-in-One WP Migration** — both work on shared hosting
2. Or Duplicator: build the package, upload `installer.php` + archive to the live root
3. After migration:
   - Search-replace the staging URL → live URL (the plugins do this; verify)
   - **Settings ▸ Reading** → untick *Discourage search engines*
   - Re-save **Permalinks**
   - Re-activate the Elementor Pro licence on the new domain
   - **Elementor ▸ Tools ▸ Regenerate CSS & Data**
   - Re-test the contact form end to end
4. Then the DNS cutover and the launch checklist in the build guide

---

## 8. Quick sanity checks before handing to the client

- [ ] Site Health shows no critical issues
- [ ] `max_input_vars` ≥ 3000 confirmed in Site Health ▸ Info ▸ Server
- [ ] Contact form actually delivers to `info@satcomgs.com` — send a real test
- [ ] Click-to-call works from a physical phone
- [ ] All six pages render at 375 / 768 / 1024 / 1440px
- [ ] *Discourage search engines* is **off**
- [ ] XML sitemap reachable and submitted to Search Console
- [ ] GA4 firing (check Realtime)
- [ ] Backups scheduled and one restore tested
- [ ] SGS's own admin account created, with the agency account kept separate
