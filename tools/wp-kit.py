#!/usr/bin/env python3
"""
SGS — write the Elementor Global Kit over the REST API.

Elementor 4.x registers its meta with show_in_rest, so the kit's
`_elementor_page_settings` is writable directly. Everything in the build
inherits from this, so it goes in before any layout work.

Values mirror ELEMENTOR-BUILD-GUIDE.md section 2 and the draft's tokens.

Reads existing kit settings and merges, so anything already configured by
hand survives. Run with --dry-run to see the payload without writing.

    python tools/wp-kit.py --dry-run
    python tools/wp-kit.py
"""
import argparse, base64, io, json, os, re, ssl, sys
import urllib.request, urllib.error

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV = os.path.join(os.path.dirname(SITE), ".env.deploy")

# --------------------------------------------------------------------------
# Brand tokens. The two cyans and two greens are deliberate: the logo colours
# fail WCAG AA as text on white, so the darker variants carry text on light
# backgrounds and the bright ones are for dark backgrounds and accents.
# --------------------------------------------------------------------------
SYSTEM_COLORS = [
    {"_id": "primary",   "title": "SGS Maroon",   "color": "#440115"},
    {"_id": "secondary", "title": "SGS Cyan",     "color": "#00B0EC"},
    {"_id": "text",      "title": "Ink",          "color": "#15191E"},
    {"_id": "accent",    "title": "CTA Cyan",     "color": "#00769F"},
]
CUSTOM_COLORS = [
    {"_id": "sgsgreen",  "title": "SGS Green",      "color": "#4A7A1F"},
    {"_id": "sgsgrnbrt", "title": "Green Bright",   "color": "#7EBF41"},
    {"_id": "muted",     "title": "Muted Text",     "color": "#545C66"},
    {"_id": "subtle",    "title": "Subtle Text",    "color": "#666D76"},
    {"_id": "border",    "title": "Border",         "color": "#E1E6EB"},
    {"_id": "surface2",  "title": "Surface Tint",   "color": "#F0F3F6"},
    {"_id": "maroondp",  "title": "Maroon Deep",    "color": "#24000B"},
    {"_id": "inkdeep",   "title": "Ink Deep",       "color": "#12040A"},
    {"_id": "ctahover",  "title": "CTA Cyan Hover", "color": "#005C7E"},
    {"_id": "ondark",    "title": "On Dark Muted",  "color": "#C0B2B7"},
]

DISPLAY = "Lexend"
BODY = "Source Sans 3"

def typo(_id, title, family, size_d, size_t, size_m, weight, lh, ls=None,
         transform=None):
    t = {
        "_id": _id, "title": title,
        "typography_typography": "custom",
        "typography_font_family": family,
        "typography_font_weight": str(weight),
        "typography_font_size": {"unit": "px", "size": size_d, "sizes": []},
        "typography_font_size_tablet": {"unit": "px", "size": size_t, "sizes": []},
        "typography_font_size_mobile": {"unit": "px", "size": size_m, "sizes": []},
        "typography_line_height": {"unit": "em", "size": lh, "sizes": []},
    }
    if ls is not None:
        t["typography_letter_spacing"] = {"unit": "px", "size": ls, "sizes": []}
    if transform:
        t["typography_text_transform"] = transform
    return t

SYSTEM_TYPOGRAPHY = [
    typo("primary",   "Primary",   DISPLAY, 44, 34, 28, 600, 1.18, -0.9),
    typo("secondary", "Secondary", DISPLAY, 24, 22, 20, 600, 1.2,  -0.5),
    typo("text",      "Text",      BODY,    17, 17, 16, 400, 1.65),
    typo("accent",    "Accent",    DISPLAY, 15, 15, 15, 600, 1.4,   0.2),
]
CUSTOM_TYPOGRAPHY = [
    typo("h1big",   "H1 Hero",  DISPLAY, 62, 44, 36, 600, 1.18, -1.2),
    typo("lead",    "Lead",     BODY,    20, 18, 17, 400, 1.6),
    typo("eyebrow", "Eyebrow",  DISPLAY, 12, 12, 12, 600, 1.4,   1.7, "uppercase"),
    typo("small",   "Small",    BODY,    15, 15, 15, 400, 1.6),
]

def px(n):      return {"unit": "px", "size": n, "sizes": []}
def box(t, r, b, l, unit="px"):
    return {"unit": unit, "top": str(t), "right": str(r),
            "bottom": str(b), "left": str(l), "isLinked": False}

SETTINGS = {
    # --- global colours and fonts ---
    "system_colors": SYSTEM_COLORS,
    "custom_colors": CUSTOM_COLORS,
    "system_typography": SYSTEM_TYPOGRAPHY,
    "custom_typography": CUSTOM_TYPOGRAPHY,
    "default_generic_fonts": "sans-serif",

    # --- layout ---
    "container_width": px(1240),
    "space_between_widgets": px(24),
    "page_title_selector": "h1.entry-title",
    "viewport_tablet": 1024,
    "viewport_mobile": 767,

    # --- body text ---
    "body_typography_typography": "custom",
    "body_typography_font_family": BODY,
    "body_typography_font_size": px(17),
    "body_typography_font_size_mobile": px(16),
    "body_typography_font_weight": "400",
    "body_typography_line_height": {"unit": "em", "size": 1.65, "sizes": []},
    "body_color": "#15191E",

    # --- links ---
    "link_normal_color": "#00769F",
    "link_hover_color": "#005C7E",

    # --- headings inherit the display face ---
    "h1_typography_typography": "custom",
    "h1_typography_font_family": DISPLAY,
    "h1_typography_font_size": px(62),
    "h1_typography_font_size_tablet": px(44),
    "h1_typography_font_size_mobile": px(36),
    "h1_typography_font_weight": "600",
    "h1_typography_line_height": {"unit": "em", "size": 1.18, "sizes": []},
    "h1_typography_letter_spacing": px(-1.2),
    "h1_color": "#12040A",

    "h2_typography_typography": "custom",
    "h2_typography_font_family": DISPLAY,
    "h2_typography_font_size": px(44),
    "h2_typography_font_size_tablet": px(34),
    "h2_typography_font_size_mobile": px(28),
    "h2_typography_font_weight": "600",
    "h2_typography_line_height": {"unit": "em", "size": 1.18, "sizes": []},
    "h2_typography_letter_spacing": px(-0.9),
    "h2_color": "#12040A",

    "h3_typography_typography": "custom",
    "h3_typography_font_family": DISPLAY,
    "h3_typography_font_size": px(24),
    "h3_typography_font_size_mobile": px(20),
    "h3_typography_font_weight": "600",
    "h3_typography_line_height": {"unit": "em", "size": 1.2, "sizes": []},
    "h3_color": "#12040A",

    "h4_typography_typography": "custom",
    "h4_typography_font_family": DISPLAY,
    "h4_typography_font_size": px(17),
    "h4_typography_font_weight": "600",
    "h4_color": "#12040A",

    # --- buttons: 48px min height is a tap-target rule, not a preference ---
    "button_typography_typography": "custom",
    "button_typography_font_family": DISPLAY,
    "button_typography_font_size": px(15),
    "button_typography_font_weight": "600",
    "button_text_color": "#FFFFFF",
    "button_background_color": "#00769F",
    "button_border_radius": box(8, 8, 8, 8),
    "button_text_padding": box(13, 26, 13, 26),
    "button_hover_text_color": "#FFFFFF",
    "button_background_hover_color": "#005C7E",

    # Elementor has no min-height control for global buttons, and padding alone
    # rendered them at 39px. 44px is the tap-target floor, 48px is the design.
    # Focus ring and reduced-motion belong here too: Elementor respects neither
    # by default, and both are accessibility requirements rather than polish.
    "custom_css": (
        ".elementor-button{min-height:48px;display:inline-flex;align-items:center;"
        "justify-content:center;gap:10px;} "
        ":focus-visible{outline:3px solid #00B0EC;outline-offset:3px;border-radius:2px;} "
        "@media (prefers-reduced-motion:reduce){*,*::before,*::after{"
        "animation-duration:.01ms !important;animation-iteration-count:1 !important;"
        "transition-duration:.01ms !important;}"
        ".elementor-invisible{visibility:visible !important;opacity:1 !important;}}"
        # The Posts widget renders nothing at all on an empty query
        # (nothing_found_message belongs to Archive Posts, not Posts), which
        # would leave a blank band wherever a feed is placed. These two rules
        # swap in a written empty state and retire it by itself the moment SGS
        # publishes a first post -- no template edit needed.
        " .sgs-feed-empty{display:none;}"
        " .sgs-feed:not(:has(article)) .sgs-feed-empty{display:flex;}"
    ),

    # --- images ---
    "image_border_radius": box(8, 8, 8, 8),
}


def load_env():
    env = {}
    for line in io.open(ENV, encoding="utf-8"):
        m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$', line)
        if m:
            env[m.group(1)] = m.group(2).strip('"')
    for k in ("WP_URL", "WP_USER", "WP_APP_PASSWORD"):
        if not env.get(k):
            sys.exit("Missing %s in .env.deploy" % k)
    env["WP_URL"] = env["WP_URL"].rstrip("/")
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--kit-id", type=int, default=None,
                    help="override the kit post id (detected automatically)")
    a = ap.parse_args()

    env = load_env()
    auth = "Basic " + base64.b64encode(
        ("%s:%s" % (env["WP_USER"], env["WP_APP_PASSWORD"])).encode()).decode()
    ctx = ssl.create_default_context()

    def call(path, method="GET", data=None):
        r = urllib.request.Request(env["WP_URL"] + path, method=method,
            headers={"User-Agent": "sgs-kit", "Authorization": auth,
                     "Accept": "application/json"})
        if data is not None:
            r.add_header("Content-Type", "application/json")
            r.data = json.dumps(data).encode()
        try:
            with urllib.request.urlopen(r, timeout=60, context=ctx) as x:
                return x.status, json.load(x)
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode())
            except Exception:
                return e.code, None

    # find the kit
    kit_id = a.kit_id
    if not kit_id:
        c, items = call("/wp-json/wp/v2/elementor_library?per_page=100&status=any&context=edit")
        if c != 200:
            sys.exit("Cannot list elementor_library (%s)" % c)
        kits = [i for i in items
                if (i.get("meta") or {}).get("_elementor_template_type") == "kit"]
        if not kits:
            sys.exit("No kit found. Open Elementor once to create one.")
        kit_id = kits[0]["id"]

    c, kit = call("/wp-json/wp/v2/elementor_library/%d?context=edit" % kit_id)
    if c != 200:
        sys.exit("Cannot read kit %s (%s)" % (kit_id, c))

    existing = (kit.get("meta") or {}).get("_elementor_page_settings") or {}
    if isinstance(existing, str):
        existing = json.loads(existing) if existing.strip() else {}

    merged = dict(existing)
    merged.update(SETTINGS)

    print("Kit post id : %d" % kit_id)
    print("Existing    : %d setting(s) -> %s" % (len(existing), sorted(existing.keys())))
    print("Writing     : %d setting(s)" % len(SETTINGS))
    print("  %d global colours (%d system + %d custom)"
          % (len(SYSTEM_COLORS) + len(CUSTOM_COLORS), len(SYSTEM_COLORS), len(CUSTOM_COLORS)))
    print("  %d typography presets" % (len(SYSTEM_TYPOGRAPHY) + len(CUSTOM_TYPOGRAPHY)))
    print("  fonts: %s (display) + %s (body)" % (DISPLAY, BODY))

    if a.dry_run:
        print("\nDRY RUN — nothing written.")
        return

    # NB: _elementor_page_settings is registered as type "object", so it must
    # be sent as a dict. (_elementor_data, by contrast, is a JSON *string*.)
    c, res = call("/wp-json/wp/v2/elementor_library/%d" % kit_id, "POST",
                  {"meta": {"_elementor_page_settings": merged}})
    if c not in (200, 201):
        sys.exit("Write failed: %s %s" % (c, res))

    # read back and confirm it actually persisted
    c, kit2 = call("/wp-json/wp/v2/elementor_library/%d?context=edit" % kit_id)
    got = (kit2.get("meta") or {}).get("_elementor_page_settings")
    got = json.loads(got) if isinstance(got, str) else (got or {})
    ok = (len(got.get("system_colors", [])) == len(SYSTEM_COLORS)
          and len(got.get("custom_colors", [])) == len(CUSTOM_COLORS)
          and got.get("container_width", {}).get("size") == 1240)
    print("\nVerified read-back: %s" % ("OK" if ok else "MISMATCH"))
    print("  colours stored    : %d system, %d custom"
          % (len(got.get("system_colors", [])), len(got.get("custom_colors", []))))
    print("  typography stored : %d system, %d custom"
          % (len(got.get("system_typography", [])), len(got.get("custom_typography", []))))
    print("  container_width   : %s" % (got.get("container_width", {}).get("size")))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
