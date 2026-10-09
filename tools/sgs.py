"""Shared Elementor building blocks for the SGS site.

Mirrors the draft's design system. Import alongside wpb.

Notes that cost time and are encoded here so they are not rediscovered:
 - Child containers in a flex row default to 100% width, so grid children
   MUST carry an explicit width or every grid stacks into one column.
 - Global button padding from the kit is ignored; buttons set their own
   so they clear the 48px tap target.
"""
from wpb import eid, px, box, gap

MAROON   = "#440115"
MAROON_D = "#24000B"
INK      = "#12040A"
CYAN     = "#00B0EC"
CTA      = "#00769F"
CTA_H    = "#005C7E"
GREEN    = "#7EBF41"
GREEN_T  = "#4A7A1F"
GREEN_D  = "#3F6619"
TEXT     = "#15191E"
MUTED    = "#545C66"
SUBTLE   = "#666D76"
ON_DARK  = "#C0B2B7"
BORDER   = "#E1E6EB"
TINT     = "#F0F3F6"

COLW = {2: (48, 48, 100), 3: (31.5, 48, 100), 4: (23.2, 48, 100)}


def colw(cols):
    d, t, m = COLW[cols]
    return {"width": px(d, "%"), "width_tablet": px(t, "%"), "width_mobile": px(m, "%")}


def C(children, **s):
    base = {"content_width": "boxed"}
    base.update(s)
    # Containers register the CSS-classes control as "css_classes"; widgets
    # register it as "_css_classes". Handing a container the widget spelling
    # stores the value happily and then renders no class at all, so normalise.
    if "_css_classes" in base:
        base["css_classes"] = base.pop("_css_classes")
    return {"id": eid(), "elType": "container", "settings": base, "elements": children}


def W(t, s):
    return {"id": eid(), "elType": "widget", "widgetType": t, "settings": s, "elements": []}


def ico(name, lib="fa-solid"):
    return {"value": "%s fa-%s" % (lib, name), "library": lib}


def eyebrow(text, dark=False, green=False):
    return W("heading", {
        "title": text, "header_size": "div",
        "title_color": CYAN if dark else (GREEN_T if green else CTA),
        "typography_typography": "custom", "typography_font_family": "Lexend",
        "typography_font_size": px(12), "typography_font_weight": "600",
        "typography_letter_spacing": px(1.7), "typography_text_transform": "uppercase"})


def h2(text, dark=False, size=None):
    s = {"title": text, "header_size": "h2", "title_color": "#FFFFFF" if dark else INK}
    if size:
        s.update({"typography_typography": "custom", "typography_font_family": "Lexend",
                  "typography_font_size": px(size), "typography_font_weight": "600",
                  "typography_line_height": {"unit": "em", "size": 1.18, "sizes": []}})
    return W("heading", s)


def h3(text, dark=False, size=19):
    return W("heading", {
        "title": text, "header_size": "h3", "title_color": "#FFFFFF" if dark else INK,
        "typography_typography": "custom", "typography_font_family": "Lexend",
        "typography_font_size": px(size), "typography_font_weight": "600",
        "typography_line_height": {"unit": "em", "size": 1.2, "sizes": []}})


def para(html, dark=False, lead=False, color=None, size=None):
    return W("text-editor", {
        "editor": html if html.startswith("<") else "<p>%s</p>" % html,
        "text_color": color or (ON_DARK if dark else MUTED),
        "typography_typography": "custom",
        "typography_font_size": px(size or (20 if lead else 17)),
        "typography_line_height": {"unit": "em", "size": 1.6 if lead else 1.65, "sizes": []}})


def btn(text, link, variant="primary"):
    s = {"text": text, "link": {"url": link}, "text_padding": box(16, 26, 16, 26),
         "typography_typography": "custom", "typography_font_family": "Lexend",
         "typography_font_size": px(15), "typography_font_weight": "600",
         "border_radius": box(8, 8, 8, 8)}
    if variant == "primary":
        s.update({"background_color": CTA, "button_text_color": "#FFFFFF",
                  "background_hover_color": CTA_H})
    elif variant == "maroon":
        s.update({"background_color": MAROON, "button_text_color": "#FFFFFF"})
    elif variant == "ghost-light":
        s.update({"background_background": "classic", "background_color": "#FFFFFF14",
                  "button_text_color": "#FFFFFF", "border_border": "solid",
                  "border_width": box(1.5, 1.5, 1.5, 1.5, linked=True),
                  "border_color": "#FFFFFF57"})
    else:
        s.update({"background_background": "classic", "background_color": "#00000000",
                  "button_text_color": TEXT, "border_border": "solid",
                  "border_width": box(1.5, 1.5, 1.5, 1.5, linked=True),
                  "border_color": "#C9D1D9"})
    return W("button", s)


def ticks(items, dark=False):
    return W("icon-list", {
        "icon_list": [{"_id": eid(), "text": t, "selected_icon": ico("circle-check")}
                      for t in items],
        "space_between": px(10), "icon_color": GREEN_T if not dark else GREEN,
        "icon_size": px(15), "text_color": ON_DARK if dark else MUTED,
        "icon_typography_typography": "custom", "icon_typography_font_size": px(15.5)})


def pills(items, dark=False):
    return W("icon-list", {
        "view": "inline",
        "icon_list": [{"_id": eid(), "text": t,
                       "selected_icon": {"value": "", "library": ""}} for t in items],
        "space_between": px(10),
        "text_color": ON_DARK if dark else MUTED,
        "icon_typography_typography": "custom", "icon_typography_font_size": px(13.5)})


def card(icon, title, body, link=None, dark=False, accent=CTA, cols=3):
    s = {"selected_icon": ico(icon), "title_text": title, "description_text": body,
         "position": "top", "title_size": "h3", "primary_color": accent,
         "icon_space": px(18),
         "title_color": "#FFFFFF" if dark else INK,
         "description_color": ON_DARK if dark else MUTED,
         "title_typography_typography": "custom",
         "title_typography_font_family": "Lexend",
         "title_typography_font_size": px(19), "title_typography_font_weight": "600",
         "description_typography_typography": "custom",
         "description_typography_font_size": px(15.5),
         "icon_size": px(26), "icon_padding": px(13),
         "view": "framed", "shape": "square",
         "border_radius_icon": box(8, 8, 8, 8)}
    if link:
        s["link"] = {"url": link}
    return C([W("icon-box", s)], content_width="full", **colw(cols),
             background_background="classic",
             background_color="#FFFFFF0B" if dark else "#FFFFFF",
             border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
             border_color="#FFFFFF24" if dark else BORDER,
             border_radius=box(14, 14, 14, 14), padding=box(30, 28, 30, 28))


def plain_card(tag, title, body, dark=False, cols=3, tag_color=None):
    kids = []
    if tag:
        kids.append(W("heading", {
            "title": tag, "header_size": "div",
            "title_color": tag_color or (CYAN if dark else CTA),
            "typography_typography": "custom", "typography_font_family": "Lexend",
            "typography_font_size": px(12), "typography_font_weight": "700",
            "typography_letter_spacing": px(1.4)}))
    kids += [h3(title, dark), para(body, dark, size=15.5)]
    return C(kids, content_width="full", **colw(cols), flex_gap=gap(0, 10),
             background_background="classic",
             background_color="#FFFFFF0B" if dark else "#FFFFFF",
             border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
             border_color="#FFFFFF24" if dark else BORDER,
             border_radius=box(14, 14, 14, 14), padding=box(30, 28, 30, 28))


def grid(cards, g=32):
    return C(cards, content_width="boxed", flex_direction="row", flex_wrap="wrap",
             flex_gap=gap(g), padding=box(0, 24, 0, 24))


def section(children, dark=False, tint=False, pad=104, anchor=None, **extra):
    s = dict(content_width="full", padding=box(pad, 0, pad, 0),
             padding_tablet=box(72, 0, 72, 0), padding_mobile=box(56, 0, 56, 0),
             flex_gap=gap(0, 44))
    if dark:
        s.update(background_background="gradient", background_color=MAROON_D,
                 background_color_b=INK,
                 background_gradient_angle={"unit": "deg", "size": 160})
    elif tint:
        s.update(background_background="classic", background_color=TINT)
    else:
        s.update(background_background="classic", background_color="#FFFFFF")
    if anchor:
        s["_element_id"] = anchor
    s.update(extra)
    return C(children, **s)


def head_block(eb, title, lead=None, dark=False, green=False, center=False, size=None):
    kids = [eyebrow(eb, dark, green), h2(title, dark, size)]
    if lead:
        kids.append(para(lead, dark, lead=True))
    return C(kids, content_width="boxed", flex_gap=gap(0, 14),
             padding=box(0, 24, 0, 24),
             flex_align_items="center" if center else "flex-start",
             text_align="center" if center else "left")


def page_hero(crumb, eb, title, lead):
    return C([
        C([W("text-editor", {
                "editor": '<p>%s</p>' % crumb,
                "text_color": "#FFFFFF94",
                "typography_typography": "custom", "typography_font_size": px(13)}),
           eyebrow(eb, dark=True),
           W("heading", {"title": title, "header_size": "h1", "title_color": "#FFFFFF"}),
           para(lead, dark=True, lead=True, color="#FFFFFFCC")],
          content_width="boxed", width=px(72, "%"), width_tablet=px(100, "%"),
          flex_gap=gap(0, 14), padding=box(0, 24, 0, 24))],
        content_width="full",
        padding=box(104, 0, 104, 0), padding_mobile=box(64, 0, 64, 0),
        background_background="gradient", background_color=MAROON_D,
        background_color_b=INK,
        background_gradient_angle={"unit": "deg", "size": 150})


def split(left, right, media_first=False, g=64, align="center"):
    kids = [right, left] if media_first else [left, right]
    return C(kids, content_width="boxed", flex_direction="row",
             flex_gap=gap(g), flex_align_items=align, padding=box(0, 24, 0, 24))


def half(children, **extra):
    s = dict(content_width="full", width=px(100, "%"), width_tablet=px(100, "%"),
             flex_gap=gap(0, 16))
    s.update(extra)
    return C(children, **s)


def figure(image, caption=None, radius=14):
    kids = [W("image", {"image": image, "image_size": "large",
                        "border_radius": box(radius, radius, radius, radius)})]
    if caption:
        kids.append(para(caption, size=14, color=SUBTLE))
    return half(kids, flex_gap=gap(0, 10))


def cta_band():
    return C([
        C([C([h2("Ready to put your gateway on the ground in Malaysia?", dark=True, size=38),
              para("Tell us about your coverage, capacity and hosting requirements &mdash; our "
                   "engineering team will come back with a site and service proposal.", dark=True)],
             content_width="full", width=px(58, "%"), width_tablet=px(100, "%"),
             flex_gap=gap(0, 12)),
           C([btn("Contact SGS", "/contact-us/", "primary"),
              btn("info@satcomgs.com", "mailto:info@satcomgs.com", "ghost-light")],
             content_width="full", width=px(42, "%"), width_tablet=px(100, "%"),
             flex_direction="row", flex_gap=gap(12), flex_justify_content="flex-end")],
          content_width="boxed", flex_direction="row", flex_align_items="center",
          flex_gap=gap(48), padding=box(0, 24, 0, 24))],
        content_width="full",
        padding=box(84, 0, 84, 0), padding_mobile=box(56, 0, 56, 0),
        background_background="gradient", background_color="#340010",
        background_color_b=INK,
        background_gradient_angle={"unit": "deg", "size": 120})


# ---------------------------------------------------------------------------
# Dynamic tags and the Posts widget
#
# Two things here were expensive to find out:
#
#  1. A widget whose control has a *dynamic default* (theme-post-title,
#     theme-post-featured-image) does NOT resolve it on the frontend unless
#     the tag is written explicitly into settings["__dynamic__"]. The dynamic
#     default only prefills the editor. Without it the widgets render
#     "Add Your Heading Text Here" and placeholder.png.
#     The featured-image tag is named "post-featured-image", NOT
#     "featured-image" as the widget class suggests.
#
#  2. Every control a Posts *skin* registers is prefixed with the skin id,
#     so it is classic_posts_per_page, not posts_per_page. Unprefixed keys
#     are silently ignored, which is why the widget always showed 6 posts.
#     This applies to style controls too (classic_title_color, classic_row_gap).
# ---------------------------------------------------------------------------
import json as _json
import urllib.parse as _up


def dyn(name, settings=None):
    """Elementor dynamic-tag shortcode, as tag_data_to_tag_text() builds it."""
    return '[elementor-tag id="%s" name="%s" settings="%s"]' % (
        eid(), name, _up.quote(_json.dumps(settings or {}), safe=""))


def post_title(**style):
    s = {"__dynamic__": {"title": dyn("post-title")}}
    s.update(style)
    return W("theme-post-title", s)


def post_featured(**style):
    s = {"__dynamic__": {"image": dyn("post-featured-image")}}
    s.update(style)
    return W("theme-post-featured-image", s)


def posts_w(skin="classic", widget=None, **skin_opts):
    """Posts widget. skin_opts are prefixed with the skin id; `widget` holds
    the widget-level controls (posts_* query group, pagination_*,
    nothing_found_message) which are NOT prefixed."""
    s = {"_skin": skin}
    for k, v in skin_opts.items():
        s["%s_%s" % (skin, k)] = v
    s.update(widget or {})
    return W("posts", s)


def feed_empty(title, body, on_tint=False):
    """Written empty state for a Posts feed.

    Paired with the .sgs-feed / .sgs-feed-empty rules in the kit's custom CSS:
    hidden by default, shown only while the feed has no <article>. It therefore
    disappears on its own as soon as SGS publishes, with no template edit.
    """
    panel = C([h3(title, size=20),
               para(body, size=16),
               C([btn("Contact SGS", "/contact-us/", "primary"),
                  btn("info@satcomgs.com", "mailto:info@satcomgs.com", "ghost")],
                 content_width="full", width=px(100, "%"), flex_direction="row",
                 flex_wrap="wrap", flex_gap=gap(12), flex_justify_content="center")],
              content_width="full", width=px(100, "%"),
              flex_gap=gap(0, 12), flex_align_items="center", text_align="center",
              padding=box(46, 28, 46, 28),
              background_background="classic",
              background_color="#FFFFFF" if on_tint else TINT,
              border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
              border_color=BORDER, border_radius=box(14, 14, 14, 14))
    # The gutter has to be padding on the boxed wrapper, not margin on the
    # panel: margin on an already-boxed container pushes it past the viewport.
    return C([panel], content_width="boxed", _css_classes="sgs-feed-empty",
             padding=box(0, 24, 0, 24))
