"""Build the SGS Theme Builder header + footer over REST."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap, gcolor, gtypo

wp = WP()
media = wp.media_map()
pages = wp.page_map()
menu_id = wp.menu_id("Primary")

LOGO = media.get("sgs-logo", {})
LOGO_LIGHT = media.get("sgs-logo-light", {})
print("logo id=%s  logo-light id=%s  menu id=%s" % (LOGO.get("id"), LOGO_LIGHT.get("id"), menu_id))

MAROON_DEEP = "#24000B"
INK_DEEP = "#12040A"
ON_DARK = "#C0B2B7"
CYAN = "#00B0EC"
GREEN = "#7EBF41"
CTA = "#00769F"


def ico(name, lib="fa-solid"):
    return {"value": "%s fa-%s" % (lib, name), "library": lib}


def container(children, **s):
    base = {"content_width": "boxed"}
    base.update(s)
    return {"id": eid(), "elType": "container", "settings": base, "elements": children}


def widget(wtype, settings):
    return {"id": eid(), "elType": "widget", "widgetType": wtype,
            "settings": settings, "elements": []}


# ===========================================================================
# HEADER
# ===========================================================================

topbar = container([
    container([
        widget("icon-list", {
            "view": "inline",
            "icon_list": [
                {"_id": eid(), "text": "info@satcomgs.com",
                 "selected_icon": ico("envelope"),
                 "link": {"url": "mailto:info@satcomgs.com"}},
                {"_id": eid(), "text": "+60 6-694 4990",
                 "selected_icon": ico("phone"),
                 "link": {"url": "tel:+6066944990"}},
                # Elementor bundles Font Awesome 5, where this marker is
                # "map-marker-alt". The FA6 name "location-dot" silently
                # renders no icon at all.
                {"_id": eid(), "text": "Rantau, Negeri Sembilan, Malaysia",
                 "selected_icon": ico("map-marker-alt")},
            ],
            "space_between": px(22),
            "icon_color": CYAN,
            "icon_size": px(13),
            "text_color": ON_DARK,
            "icon_typography_typography": "custom",
            "icon_typography_font_size": px(13),
        }),
        widget("text-editor", {
            "editor": ('<p style="margin:0;color:%s;font-weight:600;">'
                       '&#9679;&nbsp; Teleport operational 24 / 7</p>' % GREEN),
            "text_color": GREEN,
            "typography_typography": "custom",
            "typography_font_size": px(13),
        }),
    ],
        content_width="boxed",
        flex_direction="row",
        flex_justify_content="space-between",
        flex_align_items="center",
        flex_gap=gap(24),
        padding=box(0, 24, 0, 24),
    )
],
    content_width="full",
    background_background="classic",
    background_color=MAROON_DEEP,
    min_height=px(40),
    flex_justify_content="center",
    padding=box(6, 0, 6, 0),
    hide_mobile="hidden-mobile",
)

# Logo plus company name, as a lockup. A child container in a flex row needs
# an explicit width or it claims the whole row and pushes the nav off-screen.
brand = container([
    widget("image", {
        "image": {"id": LOGO.get("id"), "url": LOGO.get("url")},
        "width": px(130),
        "image_size": "full",
        "link_to": "custom",
        "link": {"url": "/"},
    }),
    widget("text-editor", {
        "editor": ('<p style="margin:0;line-height:1.25;font-family:Lexend,sans-serif;'
                   'font-weight:600;font-size:15px;color:#15191E;">'
                   'Satcom Gateway Services</p>'
                   '<p style="margin:0;line-height:1.3;font-size:12px;color:#666D76;">'
                   'Sdn Bhd &middot; Malaysia</p>'),
        "hide_mobile": "hidden-mobile",
    }),
],
    content_width="full",
    width=px(30, "%"), width_tablet=px(42, "%"), width_mobile=px(46, "%"),
    flex_direction="row",
    flex_align_items="center",
    flex_gap=gap(14),
)

main_bar = container([
    container([
        brand,
        widget("nav-menu", {
            "menu": "primary",
            "layout": "horizontal",
            "pointer": "underline",
            "animation_line": "fade",
            "align_items": "end",
            "menu_typography_typography": "custom",
            "menu_typography_font_family": "Lexend",
            "menu_typography_font_size": px(15),
            "menu_typography_font_weight": "500",
            "color_menu_item": "#15191E",
            "color_menu_item_hover": "#440115",
            "color_menu_item_active": "#440115",
            "pointer_color_menu_item_hover": CYAN,
            "pointer_color_menu_item_active": CYAN,
            "padding_horizontal_menu_item": px(14),
            "toggle_align": "right",
            "toggle_size": px(22),
            "toggle_color": "#15191E",
        }),
        widget("button", {
            "text": "Talk to our team",
            "link": {"url": "/contact-us/"},
            "text_padding": box(16, 26, 16, 26),
            "background_color": CTA,
            "button_text_color": "#FFFFFF",
            "hide_tablet": "hidden-tablet",
            "hide_mobile": "hidden-mobile",
        }),
    ],
        content_width="boxed",
        flex_direction="row",
        flex_align_items="center",
        flex_justify_content="space-between",
        flex_gap=gap(24),
        padding=box(0, 24, 0, 24),
        min_height=px(92),
        min_height_mobile=px(80),
    )
],
    content_width="full",
    background_background="classic",
    background_color="#FFFFFF",
    border_border="solid",
    border_width=box(0, 0, 1, 0),
    border_color="#E1E6EB",
    sticky="top",
    sticky_on=["desktop", "tablet", "mobile"],
    sticky_offset=0,
    sticky_effects_offset=0,
)

c, tid, action = wp.upsert_template(
    "SGS Header", "sgs-header", "header", [topbar, main_bar],
    conditions=["include/general"])
print("header template -> %s id=%s (%s)" % (c, tid, action))


# ===========================================================================
# FOOTER
# ===========================================================================

def link_list(items):
    return widget("icon-list", {
        "view": "traditional",
        "icon_list": [{"_id": eid(), "text": t, "link": {"url": u},
                       "selected_icon": {"value": "", "library": ""}} for t, u in items],
        "space_between": px(4),
        "text_color": ON_DARK,
        "text_color_hover": CYAN,
        "icon_typography_typography": "custom",
        "icon_typography_font_size": px(15),
    })


def col_heading(text):
    return widget("heading", {
        "title": text, "header_size": "h4",
        "title_color": "#FFFFFF",
        "typography_typography": "custom",
        "typography_font_family": "Lexend",
        "typography_font_size": px(13),
        "typography_font_weight": "600",
        "typography_letter_spacing": px(1.6),
        "typography_text_transform": "uppercase",
    })


brand_col = container([
    widget("image", {
        "image": {"id": LOGO_LIGHT.get("id"), "url": LOGO_LIGHT.get("url")},
        "width": px(150), "image_size": "full",
        # the column goes full width on a tablet and an image widget centres
        # by default, which floats the logo into the middle of the footer
        "align": "left",
    }),
    widget("text-editor", {
        "editor": ("<p>Satcom Gateway Services Sdn Bhd is a Malaysia-based satellite "
                   "communications and teleport services provider, operating "
                   "carrier-neutral ground infrastructure for enterprise, "
                   "telecommunications, maritime and satellite network operators.</p>"),
        "text_color": ON_DARK,
        "typography_typography": "custom",
        "typography_font_size": px(15),
    }),
], content_width="full", width=px(31, "%"), width_tablet=px(100, "%"), width_mobile=px(100, "%"), flex_gap=gap(18))

company_col = container([
    col_heading("Company"),
    link_list([
        ("About SGS", "/about-us/"),
        ("Licences & regulation", "/about-us/#licences"),
        ("Our facility", "/about-us/#facility"),
        ("News & Events", "/news-events/"),
        ("Contact Us", "/contact-us/"),
    ]),
], content_width="full", width=px(20, "%"), width_tablet=px(26, "%"), width_mobile=px(100, "%"), flex_gap=gap(18))

services_col = container([
    col_heading("Services"),
    link_list([
        ("Teleport & gateway", "/our-services/#gateway"),
        ("Capacity leasing", "/our-services/#capacity"),
        ("Broadband & backhaul", "/our-services/#broadband"),
        ("Satellite mobility", "/our-services/#mobility"),
        ("Data centre & colocation", "/our-services/#datacentre"),
        ("Technical services", "/our-services/#technical"),
    ]),
], content_width="full", width=px(21, "%"), width_tablet=px(30, "%"), width_mobile=px(100, "%"), flex_gap=gap(18))

contact_col = container([
    col_heading("Get in touch"),
    widget("icon-list", {
        "view": "traditional",
        "icon_list": [
            {"_id": eid(),
             "text": "Lot 23126, Jalan Kuala Sawah,<br>Batu 10 Kampung Ribu,<br>71200 Rantau, Negeri Sembilan, Malaysia",
             "selected_icon": ico("map-marker-alt")},
            {"_id": eid(), "text": "info@satcomgs.com",
             "selected_icon": ico("envelope"),
             "link": {"url": "mailto:info@satcomgs.com"}},
            {"_id": eid(), "text": "+60 6-694 4990",
             "selected_icon": ico("phone"),
             "link": {"url": "tel:+6066944990"}},
            {"_id": eid(), "text": "Monday &ndash; Friday, 09:00 &ndash; 17:00 (MYT)",
             "selected_icon": ico("clock")},
        ],
        "space_between": px(14),
        "icon_color": CYAN,
        "icon_size": px(15),
        "text_color": ON_DARK,
        "icon_typography_typography": "custom",
        "icon_typography_font_size": px(15),
    }),
], content_width="full", width=px(24, "%"), width_tablet=px(34, "%"), width_mobile=px(100, "%"), flex_gap=gap(18))

footer_cols = container(
    [brand_col, company_col, services_col, contact_col],
    content_width="boxed",
    flex_direction="row",
    flex_wrap="wrap",
    flex_align_items="flex-start",
    flex_gap=gap(32, 48),
    padding=box(0, 24, 64, 24),
)

footer_bottom = container([
    widget("text-editor", {
        "editor": "<p>&copy; 2026 Satcom Gateway Services Sdn Bhd. All rights reserved.</p>",
        "text_color": ON_DARK,
        "typography_typography": "custom",
        "typography_font_size": px(13.5),
    }),
    widget("text-editor", {
        "editor": ('<p style="text-align:right;">'
                   '<a href="/privacy-notice/">Privacy notice</a> &nbsp;&nbsp; '
                   '<a href="/terms-of-use/">Terms of use</a> &nbsp;&nbsp; '
                   '<a href="/contact-us/">Contact Us</a></p>'),
        "text_color": ON_DARK,
        "typography_typography": "custom",
        "typography_font_size": px(13.5),
    }),
],
    content_width="boxed",
    flex_direction="row",
    flex_direction_mobile="column",
    flex_justify_content="space-between",
    flex_align_items="center",
    flex_align_items_mobile="flex-start",
    flex_gap=gap(16),
    padding=box(22, 24, 22, 24),
    border_border="solid",
    border_width=box(1, 0, 0, 0),
    border_color="#FFFFFF1A",
)

footer = container(
    [footer_cols, footer_bottom],
    content_width="full",
    background_background="classic",
    background_color=INK_DEEP,
    padding=box(80, 0, 0, 0),
    padding_mobile=box(56, 0, 0, 0),
)

c, fid, action = wp.upsert_template(
    "SGS Footer", "sgs-footer", "footer", [footer],
    conditions=["include/general"])
print("footer template -> %s id=%s (%s)" % (c, fid, action))

print("cache cleared:", wp.clear_cache())
