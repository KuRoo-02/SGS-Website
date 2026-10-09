"""Build the SGS News & Events archive and the Single Post template.

No sample articles are created: SGS publishes the real ones from wp-admin.
Both layouts therefore have to read as finished while the newsroom is still
empty, which is what the "What we publish here" band and the self-retiring
.sgs-feed-empty block are for.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap
from sgs import *

wp = WP(); M = wp.media_map(); P = wp.page_map()
PID = P["news-events"]

EMPTY = ("The SGS newsroom is live. Announcements, technical updates and event news "
         "will be posted here as they happen. In the meantime, our engineering team "
         "is reachable directly.")

# Shared card styling for the Posts grid, so archive and related match.
CARD = dict(
    columns=3, columns_tablet=2, columns_mobile=1,
    row_gap=px(32), column_gap=px(32),
    thumbnail_size="medium_large",
    show_excerpt="yes", excerpt_length=22,
    meta_data=["date"], meta_separator=" &middot; ",
    show_read_more="yes", read_more_text="Read more",
    box_border="yes", box_border_color=BORDER,
    box_border_width=px(1), box_border_radius=box(14, 14, 14, 14),
    title_color=INK, excerpt_color=MUTED, meta_color=SUBTLE,
    read_more_color=CTA,
    title_typography_typography="custom",
    title_typography_font_family="Lexend",
    title_typography_font_size=px(18),
    title_typography_font_weight="600",
    excerpt_typography_typography="custom",
    excerpt_typography_font_size=px(15),
    meta_typography_typography="custom",
    meta_typography_font_size=px(13),
)

# ===========================================================================
# News & Events archive page
# ===========================================================================
EL = [page_hero(
    'Home &nbsp;/&nbsp; News &amp; Events', "Newsroom", "News &amp; Events",
    "Announcements, technical updates and where to find the SGS team across the region's "
    "satellite and telecommunications calendar.")]

EL.append(section([
    C([posts_w("classic",
               widget={"posts_post_type": "post",
                       "pagination_type": "numbers_and_prev_next",
                       "pagination_prev_label": "&larr; Previous",
                       "pagination_next_label": "Next &rarr;"},
               **CARD)],
      content_width="boxed", padding=box(0, 24, 0, 24)),
    feed_empty("Nothing published yet", EMPTY),
], _css_classes="sgs-feed"))

# Stays accurate whether or not anything is published yet.
EL.append(section([
    head_block("What we publish here", "Three kinds of update.", green=True),
    grid([
        plain_card("Announcements", "Company &amp; capability news",
                   "New services, licences, partnerships and milestones at the Rantau ground "
                   "station.", cols=3),
        plain_card("Technical", "Infrastructure updates",
                   "Antenna, power, fibre and data-hall work that affects how the site serves "
                   "hosted gateways.", cols=3),
        plain_card("Events", "Where to find us",
                   "Conferences, forums and industry events across the Asia-Pacific satellite "
                   "calendar.", cols=3),
    ]),
], tint=True))

EL.append(cta_band())

c, _ = wp.put_layout(PID, EL)
wp.set_page_template(PID, "elementor_header_footer")
print("news archive %d -> %s, %d sections" % (PID, c, len(EL)))


# ===========================================================================
# Single Post template
# ===========================================================================
single = [
    # dark hero carrying the post title and meta
    C([C([W("post-info", {
              "post_info_meta_data": ["terms"],
              "terms_taxonomy": "category",
              "text_color": CYAN,
              "icon_color": CYAN,
              "typography_typography": "custom",
              "typography_font_family": "Lexend",
              "typography_font_size": px(12),
              "typography_font_weight": "600",
              "typography_letter_spacing": px(1.7),
              "typography_text_transform": "uppercase",
              "show_icon": ""}),
          # dynamic tag written explicitly -- see note in sgs.py
          post_title(
              title_color="#FFFFFF",
              typography_typography="custom",
              typography_font_family="Lexend",
              typography_font_size=px(46),
              typography_font_size_mobile=px(30),
              typography_font_weight="600",
              typography_line_height={"unit": "em", "size": 1.16, "sizes": []}),
          W("post-info", {
              "post_info_meta_data": ["date", "author"],
              "text_color": "#FFFFFF9E", "icon_color": CYAN,
              "view": "inline", "icon_size": px(14),
              "typography_typography": "custom", "typography_font_size": px(13.5)})],
         content_width="boxed", width=px(80, "%"), width_tablet=px(100, "%"),
         flex_gap=gap(0, 14), padding=box(0, 24, 0, 24))],
      content_width="full",
      padding=box(96, 0, 96, 0), padding_mobile=box(60, 0, 60, 0),
      background_background="gradient", background_color=MAROON_D,
      background_color_b=INK,
      background_gradient_angle={"unit": "deg", "size": 150}),

    # body + sidebar
    section([
        C([
            half([post_featured(image_size="large",
                                image_border_radius=box(14, 14, 14, 14)),
                  W("theme-post-content", {
                        "text_color": "#2A3039",
                        "typography_typography": "custom",
                        "typography_font_size": px(17),
                        "typography_line_height": {"unit": "em", "size": 1.75, "sizes": []}}),
                  W("divider", {"color": BORDER, "weight": px(1), "gap": px(24)}),
                  W("share-buttons", {
                        "share_buttons": [
                            {"_id": eid(), "button": "linkedin"},
                            {"_id": eid(), "button": "email"},
                            {"_id": eid(), "button": "x-twitter"}],
                        "view": "icon-text", "shape": "rounded", "columns": "0",
                        "skin": "minimal"}),
                 ], width=px(66, "%"), width_tablet=px(100, "%"), flex_gap=gap(0, 24)),

            half([C([W("heading", {"title": "Recent posts", "header_size": "h4",
                                   "title_color": SUBTLE,
                                   "typography_typography": "custom",
                                   "typography_font_family": "Lexend",
                                   "typography_font_size": px(12),
                                   "typography_font_weight": "600",
                                   "typography_letter_spacing": px(1.6),
                                   "typography_text_transform": "uppercase"}),
                     posts_w("cards",
                             widget={"posts_post_type": "post", "pagination_type": "",
                                     "posts_exclude": ["current_post"],
                                     },
                             posts_per_page=4, columns=1,
                             show_excerpt="", show_read_more="",
                             meta_data=["date"], thumbnail="none",
                             row_gap=px(14),
                             box_border_width=px(0), box_shadow_box_shadow_type="",
                             title_color=INK, meta_color=SUBTLE,
                             title_typography_typography="custom",
                             title_typography_font_family="Lexend",
                             title_typography_font_size=px(15),
                             title_typography_font_weight="600")],
                    content_width="full", width=px(100, "%"), flex_gap=gap(0, 14),
                    background_background="classic", background_color="#FFFFFF",
                    border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
                    border_color=BORDER, border_radius=box(14, 14, 14, 14),
                    padding=box(24, 24, 24, 24)),
                  C([W("heading", {"title": "Talk to SGS", "header_size": "h4",
                                   "title_color": "#FFFFFF9E",
                                   "typography_typography": "custom",
                                   "typography_font_family": "Lexend",
                                   "typography_font_size": px(12),
                                   "typography_font_weight": "600",
                                   "typography_letter_spacing": px(1.6),
                                   "typography_text_transform": "uppercase"}),
                     para("Gateway hosting, capacity or colocation &mdash; tell us your "
                          "requirements and we will scope them against the site.", dark=True,
                          size=15),
                     btn("Contact us", "/contact-us/", "primary")],
                    content_width="full", width=px(100, "%"), flex_gap=gap(0, 12),
                    background_background="gradient", background_color="#340010",
                    background_color_b=INK,
                    background_gradient_angle={"unit": "deg", "size": 150},
                    border_radius=box(14, 14, 14, 14), padding=box(26, 26, 26, 26)),
                 ], width=px(34, "%"), width_tablet=px(100, "%"), flex_gap=gap(0, 24)),
        ], content_width="boxed", flex_direction="row", flex_align_items="flex-start",
           flex_gap=gap(48), padding=box(0, 24, 0, 24), **STACK_TABLET),
    ]),

    # related
    section([
        head_block("Keep reading", "Related updates", size=32),
        C([posts_w("classic",
                   widget={"posts_post_type": "post", "pagination_type": "",
                           "posts_exclude": ["current_post"],
                           },
                   posts_per_page=3, columns=3, columns_tablet=2, columns_mobile=1,
                   row_gap=px(32), column_gap=px(32),
                   thumbnail_size="medium_large",
                   show_excerpt="yes", excerpt_length=16,
                   meta_data=["date"],
                   box_border="yes", box_border_color=BORDER,
                   box_border_width=px(1), box_border_radius=box(14, 14, 14, 14),
                   title_color=INK, excerpt_color=MUTED, meta_color=SUBTLE,
                   title_typography_typography="custom",
                   title_typography_font_family="Lexend",
                   title_typography_font_size=px(17),
                   title_typography_font_weight="600")],
          content_width="boxed", padding=box(0, 24, 0, 24)),
    ], tint=True),

    cta_band(),
]

c, sid, action = wp.upsert_template("SGS Single Post", "sgs-single-post",
                                    "single-post", single)
print("single-post template -> %s id=%s (%s)" % (c, sid, action))
cc, _ = wp.set_conditions(sid, [{"name": "singular", "sub_name": "post"}])
print("  conditions -> %s" % cc)

print("cache cleared:", wp.clear_cache())
for tid, info in wp.template_state().items():
    print("  %-4s %-12s %-18s active=%s" % (tid, info["type"], info["title"], info["active"]))
