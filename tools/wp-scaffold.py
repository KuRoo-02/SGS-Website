#!/usr/bin/env python3
"""
SGS — WordPress content scaffolding over the REST API.

Creates everything that CAN be created reliably over the API:
  - media library uploads, with alt text and captions
  - pages (empty canvases for Elementor to fill)
  - post categories
  - news posts, with featured images and categories
  - the Primary nav menu
  - core site settings (title, tagline, timezone, permalinks note)

It does NOT create Elementor layouts. Elementor stores those in the
`_elementor_data` post meta, which WordPress does not expose to REST.
See WORDPRESS-SETUP.md section 6.

Idempotent: matches on slug and updates instead of duplicating, so it is
safe to re-run.

Setup
-----
1. wp-admin -> Users -> Profile -> Application Passwords -> add "sgs-scaffold"
2. Put these in ../.env.deploy (never committed):

       WP_URL=https://clientdomain.com
       WP_USER=admin-username
       WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx

Usage
-----
    python tools/wp-scaffold.py --dry-run     # show what would happen
    python tools/wp-scaffold.py               # apply
    python tools/wp-scaffold.py --only media  # media|pages|posts|menu|settings

Stdlib only — no pip install required.
"""

import argparse
import base64
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)                      # the Website/ folder
IMG = os.path.join(SITE, "assets", "img")
ENV = os.path.join(os.path.dirname(SITE), ".env.deploy")

# --------------------------------------------------------------------------
# Content
# --------------------------------------------------------------------------

PAGES = [
    # (title, slug, front_page?)
    ("Home",            "home",            True),
    ("About Us",        "about-us",        False),
    ("Our Services",    "our-services",    False),
    ("News & Events",   "news-events",     False),
    ("Contact Us",      "contact-us",      False),
    ("Privacy Notice",  "privacy-notice",  False),
    ("Terms of Use",    "terms-of-use",    False),
]

MENU_ITEMS = ["Home", "About Us", "Our Services", "News & Events", "Contact Us"]

CATEGORIES = [
    ("Company News",     "company-news"),
    ("Events",           "events"),
    ("Technical Updates", "technical-updates"),
]

# Alt text matters for accessibility and Elementor inherits it from the
# Media Library, so it is set once here rather than per widget.
MEDIA = {
    "hero-teleport.jpg":  "Satellite antennas at the SGS ground station in Rantau at sunset",
    "antenna-1.jpg":      "Two satellite antennas at the SGS teleport",
    "antenna-2.jpg":      "Satellite antennas at the SGS ground station in Rantau",
    "antenna-3.jpg":      "Satellite antenna on the SGS antenna farm",
    "antenna-4.jpg":      "Tracking antenna at the SGS ground station",
    "battery-room.jpg":   "Battery room supporting redundant power at the SGS facility",
    "facility-1.jpg":     "Overview of the SGS teleport site",
    "facility-2.jpg":     "The SGS teleport site and operations building in Rantau",
    "facility-3.jpg":     "The SGS facility building",
    "facility-4.jpg":     "The SGS ground station facility",
    "generator.jpg":      "Standby generator at the SGS facility",
    "office-space.jpg":   "Office and operations space at the SGS facility",
    "server-room-1.jpg":  "Equipment racks in the SGS server room",
    "server-room-2.jpg":  "Racks and cabling inside the SGS server room",
    "switchboard-1.jpg":  "Main switchboard room at the SGS facility",
    "switchboard-2.jpg":  "Secondary switchboard room at the SGS facility",
    "telco-room.jpg":     "Telecommunications room at the SGS facility",
    "weather-station.jpg": "Weather station at the SGS facility",
    "sgs-logo.png":       "SGS — Satcom Gateway Services logo",
    "sgs-logo-light.png": "SGS — Satcom Gateway Services logo, light version",
}

# PLACEHOLDER CONTENT. Every post below was written to demonstrate the
# layout — none of it is real SGS news. Replace before launch.
POSTS = [
    {
        "title": "SGS expands LEO gateway capability with SPACESAIL",
        "slug": "sgs-expands-leo-gateway-capability-with-spacesail",
        "date": "2026-09-02T09:00:00",
        "category": "Company News",
        "image": "antenna-2.jpg",
        "excerpt": ("The Rantau teleport adds tracking capability for the SPACESAIL "
                    "low-earth-orbit constellation, giving customers a single Malaysian "
                    "landing point for hybrid GEO–LEO architectures."),
        "content": """
<p><strong>RANTAU, NEGERI SEMBILAN —</strong> Satcom Gateway Services Sdn Bhd (SGS) has extended the capability of its carrier-neutral teleport to support gateway operations for the SPACESAIL low-earth-orbit constellation, adding a low-latency layer to a site that has until now served geostationary traffic.</p>
<p>The addition means customers can reach both orbital regimes through a single Malaysian landing point. Traffic from the APStar geostationary fleet and from SPACESAIL now terminates in the same data hall, on the same fibre, under the same operational team.</p>
<h2>Why hybrid architectures matter</h2>
<p>Geostationary and low-earth-orbit networks solve different problems. GEO delivers broad, predictable regional coverage from a fixed orbital slot. LEO delivers latency low enough for interactive applications, at the cost of a constellation that must be tracked continuously.</p>
<blockquote><p>Satellite networks require more than bandwidth. They require dependable ground infrastructure, operational expertise and the ability to respond to the technical demands of mission-critical communications.</p></blockquote>
<h2>What is available now</h2>
<ul>
<li>Gateway hosting for the SPACESAIL LEO constellation alongside APStar-5C, APStar-6D and APStar-9</li>
<li>Hybrid GEO–LEO router solutions with antenna options for enterprise, maritime and remote operations</li>
<li>Low-cost LEO IoT terminals for sensors, remote monitoring and emergency communications</li>
<li>Managed bandwidth packages spanning both networks under one commercial agreement</li>
</ul>
<h2>Ground infrastructure behind the service</h2>
<p>The Rantau site sits 68&nbsp;km from Kuala Lumpur International Airport and 80&nbsp;km from the metropolitan area. It is linked to the TSGI ground station (KL1) by 65&nbsp;km of dark fibre operating in full redundancy, with Telekom Malaysia and Fiberail both present on site.</p>
""",
    },
    {
        "title": "Dark fibre to KL1 now operating in full redundancy",
        "slug": "dark-fibre-to-kl1-full-redundancy",
        "date": "2026-08-14T09:00:00",
        "category": "Technical Updates",
        "image": "telco-room.jpg",
        "excerpt": "65 km of dark fibre between the SGS and TSGI ground stations completes commissioning.",
        "content": "<p>Placeholder article. Replace with the real update before launch.</p>",
    },
    {
        "title": "Meet the SGS team at the regional satellite forum",
        "slug": "meet-sgs-regional-satellite-forum",
        "date": "2026-07-28T09:00:00",
        "category": "Events",
        "image": "office-space.jpg",
        "excerpt": "Our engineering and commercial teams will be available for gateway hosting discussions.",
        "content": "<p>Placeholder article. Replace with the real event details before launch.</p>",
    },
    {
        "title": "SGS confirmed as an MCMC-licensed NFP and NSP",
        "slug": "sgs-mcmc-licensed-nfp-nsp",
        "date": "2026-06-11T09:00:00",
        "category": "Company News",
        "image": "facility-3.jpg",
        "excerpt": "Individual licences underpin long-term gateway hosting and network service agreements.",
        "content": "<p>Placeholder article. Replace with the real announcement before launch.</p>",
    },
    {
        "title": "Standby power and battery plant upgrade completed",
        "slug": "standby-power-battery-plant-upgrade",
        "date": "2026-05-19T09:00:00",
        "category": "Technical Updates",
        "image": "generator.jpg",
        "excerpt": "Generator and UPS works extend autonomy for gateway and colocation customers.",
        "content": "<p>Placeholder article. Replace with the real update before launch.</p>",
    },
    {
        "title": "Managed satcom bandwidth packages launched",
        "slug": "managed-satcom-bandwidth-packages",
        "date": "2026-04-03T09:00:00",
        "category": "Company News",
        "image": "antenna-1.jpg",
        "excerpt": "Lower-CAPEX options for enterprise, oil & gas, maritime and rural deployments.",
        "content": "<p>Placeholder article. Replace with the real announcement before launch.</p>",
    },
]

SETTINGS = {
    "title": "Satcom Gateway Services Sdn Bhd",
    "description": "Carrier-neutral satellite teleport and data centre in Malaysia",
    "timezone": "Asia/Kuala_Lumpur",
    "date_format": "j F Y",
    "default_ping_status": "closed",
    "default_comment_status": "closed",
}

# --------------------------------------------------------------------------
# Plumbing
# --------------------------------------------------------------------------

DRY = False


def load_env():
    if not os.path.exists(ENV):
        sys.exit(f"Missing {ENV}\nSee WORDPRESS-SETUP.md section 4.")
    env = {}
    with open(ENV, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$', line)
            if m:
                env[m.group(1)] = m.group(2).strip('"')
    missing = [k for k in ("WP_URL", "WP_USER", "WP_APP_PASSWORD") if not env.get(k)]
    if missing:
        sys.exit("Missing in .env.deploy: " + ", ".join(missing)
                 + "\nSee WORDPRESS-SETUP.md section 4.")
    env["WP_URL"] = env["WP_URL"].rstrip("/")
    return env


class WP:
    def __init__(self, env):
        self.base = env["WP_URL"] + "/wp-json/wp/v2"
        raw = f'{env["WP_USER"]}:{env["WP_APP_PASSWORD"]}'.encode()
        self.auth = "Basic " + base64.b64encode(raw).decode()

    def _req(self, method, path, data=None, headers=None, raw=None):
        url = path if path.startswith("http") else self.base + path
        hdrs = {"Authorization": self.auth, "Accept": "application/json"}
        body = None
        if raw is not None:
            body = raw
        elif data is not None:
            body = json.dumps(data).encode()
            hdrs["Content-Type"] = "application/json"
        hdrs.update(headers or {})
        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                txt = r.read().decode()
                return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:400]
            raise SystemExit(f"\n  HTTP {e.code} on {method} {url}\n  {detail}\n")
        except urllib.error.URLError as e:
            raise SystemExit(f"\n  Cannot reach {url}\n  {e.reason}\n")

    def get(self, path, **params):
        params = {k: v for k, v in params.items() if v is not None}
        if params:
            path += ("&" if "?" in path else "?") + urllib.parse.urlencode(params)
        return self._req("GET", path)

    def post(self, path, data):
        return self._req("POST", path, data=data)

    def upload(self, filepath, alt):
        name = os.path.basename(filepath)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        with open(filepath, "rb") as fh:
            blob = fh.read()
        return self._req("POST", "/media", raw=blob, headers={
            "Content-Type": ctype,
            "Content-Disposition": f'attachment; filename="{name}"',
        })


def find_by_slug(wp, endpoint, slug, **extra):
    hits = wp.get(endpoint, slug=slug, per_page=1, status="any"
                  if endpoint in ("/pages", "/posts") else None, **extra) or []
    return hits[0] if hits else None


def say(action, what, extra=""):
    tag = {"create": "+", "update": "~", "skip": "=", "info": " "}[action]
    print(f"  {tag} {what}{(' — ' + extra) if extra else ''}")


# --------------------------------------------------------------------------
# Steps
# --------------------------------------------------------------------------

def do_settings(wp):
    print("\nSETTINGS")
    if DRY:
        for k, v in SETTINGS.items():
            say("info", f"{k} = {v}")
        return
    wp.post("/settings", SETTINGS)
    for k, v in SETTINGS.items():
        say("update", f"{k}", str(v))
    say("info", "Permalinks", "set to 'Post name' manually in Settings > Permalinks")


def do_media(wp):
    print("\nMEDIA")
    existing = {}
    page = 1
    while True:
        batch = wp.get("/media", per_page=100, page=page)
        if not batch:
            break
        for m in batch:
            existing[m["slug"]] = m
        if len(batch) < 100:
            break
        page += 1

    ids = {}
    for fname, alt in MEDIA.items():
        path = os.path.join(IMG, fname)
        if not os.path.exists(path):
            say("skip", fname, "not found on disk")
            continue
        slug = os.path.splitext(fname)[0]
        if slug in existing:
            ids[fname] = existing[slug]["id"]
            if not DRY:
                wp.post(f"/media/{existing[slug]['id']}", {"alt_text": alt})
            say("update", fname, f"id={ids[fname]} alt set")
            continue
        if DRY:
            say("create", fname, f"upload + alt: {alt[:45]}")
            continue
        m = wp.upload(path, alt)
        wp.post(f"/media/{m['id']}", {"alt_text": alt})
        ids[fname] = m["id"]
        say("create", fname, f"id={m['id']}")
    return ids


def do_pages(wp):
    print("\nPAGES")
    made = {}
    for title, slug, is_front in PAGES:
        found = find_by_slug(wp, "/pages", slug)
        if found:
            made[title] = found["id"]
            say("skip", title, f"exists id={found['id']}")
            continue
        if DRY:
            say("create", title, f"/{slug}")
            continue
        p = wp.post("/pages", {"title": title, "slug": slug,
                               "status": "publish", "content": ""})
        made[title] = p["id"]
        say("create", title, f"id={p['id']} /{slug}")
    front = made.get("Home")
    if front and not DRY:
        wp.post("/settings", {"show_on_front": "page", "page_on_front": front})
        say("update", "Front page", "set to Home")
    elif DRY:
        say("info", "Front page", "would be set to Home")
    return made


def do_categories(wp):
    print("\nCATEGORIES")
    made = {}
    for name, slug in CATEGORIES:
        found = find_by_slug(wp, "/categories", slug)
        if found:
            made[name] = found["id"]
            say("skip", name, f"exists id={found['id']}")
            continue
        if DRY:
            say("create", name)
            continue
        c = wp.post("/categories", {"name": name, "slug": slug})
        made[name] = c["id"]
        say("create", name, f"id={c['id']}")
    return made


def do_posts(wp, cats, media):
    print("\nPOSTS  (placeholder content — replace before launch)")
    for p in POSTS:
        found = find_by_slug(wp, "/posts", p["slug"])
        payload = {
            "title": p["title"], "slug": p["slug"], "status": "publish",
            "date": p["date"], "excerpt": p["excerpt"],
            "content": p["content"].strip(),
            "comment_status": "closed",
        }
        if p["category"] in cats:
            payload["categories"] = [cats[p["category"]]]
        if p["image"] in media:
            payload["featured_media"] = media[p["image"]]
        if DRY:
            say("create" if not found else "update", p["title"][:52],
                f"[{p['category']}]")
            continue
        if found:
            wp.post(f"/posts/{found['id']}", payload)
            say("update", p["title"][:52], f"id={found['id']}")
        else:
            r = wp.post("/posts", payload)
            say("create", p["title"][:52], f"id={r['id']}")


def do_menu(wp, pages):
    print("\nMENU")
    menus = wp.get("/menus", per_page=100) or []
    menu = next((m for m in menus if m.get("slug") == "primary"
                 or m.get("name") == "Primary"), None)
    if DRY:
        say("create" if not menu else "skip", "Primary menu")
        for i, t in enumerate(MENU_ITEMS, 1):
            say("info", f"  {i}. {t}")
        return
    if not menu:
        menu = wp.post("/menus", {"name": "Primary", "slug": "primary"})
        say("create", "Primary menu", f"id={menu['id']}")
    else:
        say("skip", "Primary menu", f"exists id={menu['id']}")

    def _title(i):
        # WP returns title as {"rendered": ...} in some contexts and a plain
        # string in others; handle both rather than assume.
        t = i.get("title")
        return (t.get("rendered") or t.get("raw") or "") if isinstance(t, dict) else (t or "")

    have = {_title(i) for i in
            (wp.get("/menu-items", menus=menu["id"], per_page=100) or [])}
    for order, title in enumerate(MENU_ITEMS, 1):
        if title in have:
            say("skip", title)
            continue
        pid = pages.get(title)
        if not pid:
            say("skip", title, "page not found")
            continue
        wp.post("/menu-items", {"title": title, "menus": menu["id"],
                                "object": "page", "object_id": pid,
                                "type": "post_type", "menu_order": order,
                                "status": "publish"})
        say("create", title)


# --------------------------------------------------------------------------

def main():
    global DRY
    ap = argparse.ArgumentParser(description="Scaffold SGS content into WordPress.")
    ap.add_argument("--dry-run", action="store_true", help="show what would change")
    ap.add_argument("--only", choices=["settings", "media", "pages",
                                       "categories", "posts", "menu"],
                    help="run a single step")
    a = ap.parse_args()
    DRY = a.dry_run

    env = load_env()
    wp = WP(env)

    print(f"Target : {env['WP_URL']}")
    print(f"User   : {env['WP_USER']}")
    print(f"Mode   : {'DRY RUN — nothing will be written' if DRY else 'APPLY'}")

    me = wp.get("/users/me")
    print(f"Auth   : ok as '{me.get('name')}' ({', '.join(me.get('roles', []))})")
    if "administrator" not in me.get("roles", []):
        sys.exit("  This user is not an administrator — scaffolding will fail.")

    steps = a.only
    media = cats = {}
    pages = {}
    if steps in (None, "settings"):
        do_settings(wp)
    if steps in (None, "media"):
        media = do_media(wp)
    if steps in (None, "pages"):
        pages = do_pages(wp)
    if steps in (None, "categories"):
        cats = do_categories(wp)
    if steps in (None, "posts"):
        if not cats:
            cats = {n: (find_by_slug(wp, "/categories", s) or {}).get("id")
                    for n, s in CATEGORIES}
            cats = {k: v for k, v in cats.items() if v}
        if not media:
            media = {}
            for m in (wp.get("/media", per_page=100) or []):
                for fname in MEDIA:
                    if os.path.splitext(fname)[0] == m["slug"]:
                        media[fname] = m["id"]
        do_posts(wp, cats, media)
    if steps in (None, "menu"):
        if not pages:
            pages = {t: (find_by_slug(wp, "/pages", s) or {}).get("id")
                     for t, s, _ in PAGES}
            pages = {k: v for k, v in pages.items() if v}
        do_menu(wp, pages)

    print("\nDone." if not DRY else "\nDry run complete — nothing was written.")
    print("\nNext: Elementor layouts are NOT created by this script.")
    print("      Follow ELEMENTOR-BUILD-GUIDE.md, starting with the Global Kit (§2).")


if __name__ == "__main__":
    main()
