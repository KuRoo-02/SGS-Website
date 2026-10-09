"""Build the SGS home page in Elementor over REST."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap

wp = WP()
M = wp.media_map()
P = wp.page_map()
HOME = P["home"]

def img(slug):
    m = M.get(slug, {})
    return {"id": m.get("id"), "url": m.get("url")}

def url(slug):
    return M.get(slug, {}).get("url", "")

MAROON   = "#440115"
MAROON_D = "#24000B"
INK      = "#12040A"
CYAN     = "#00B0EC"
CTA      = "#00769F"
GREEN    = "#7EBF41"
GREEN_T  = "#4A7A1F"
TEXT     = "#15191E"
MUTED    = "#545C66"
ON_DARK  = "#C0B2B7"
BORDER   = "#E1E6EB"
TINT     = "#F0F3F6"


def C(children, **s):
    base = {"content_width": "boxed"}
    base.update(s)
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
        "typography_letter_spacing": px(1.7), "typography_text_transform": "uppercase",
    })


def h2(text, dark=False, size=None):
    s = {"title": text, "header_size": "h2",
         "title_color": "#FFFFFF" if dark else INK}
    if size:
        s.update({"typography_typography": "custom", "typography_font_family": "Lexend",
                  "typography_font_size": px(size), "typography_font_weight": "600",
                  "typography_line_height": {"unit": "em", "size": 1.18, "sizes": []}})
    return W("heading", s)


def para(html, dark=False, lead=False, color=None):
    return W("text-editor", {
        "editor": html if html.startswith("<") else "<p>%s</p>" % html,
        "text_color": color or (ON_DARK if dark else MUTED),
        "typography_typography": "custom",
        "typography_font_size": px(20 if lead else 17),
        "typography_line_height": {"unit": "em", "size": 1.6 if lead else 1.65, "sizes": []},
    })


def btn(text, link, variant="primary"):
    s = {"text": text, "link": {"url": link},
         "text_padding": box(16, 26, 16, 26),
         "typography_typography": "custom", "typography_font_family": "Lexend",
         "typography_font_size": px(15), "typography_font_weight": "600",
         "border_radius": box(8, 8, 8, 8)}
    if variant == "primary":
        s.update({"background_color": CTA, "button_text_color": "#FFFFFF",
                  "background_hover_color": "#005C7E"})
    elif variant == "maroon":
        s.update({"background_color": MAROON, "button_text_color": "#FFFFFF"})
    elif variant == "ghost-light":
        s.update({"background_background": "classic", "background_color": "#FFFFFF14",
                  "button_text_color": "#FFFFFF", "border_border": "solid",
                  "border_width": box(1.5, 1.5, 1.5, 1.5, linked=True),
                  "border_color": "#FFFFFF57"})
    else:  # ghost
        s.update({"background_background": "classic", "background_color": "#00000000",
                  "button_text_color": TEXT, "border_border": "solid",
                  "border_width": box(1.5, 1.5, 1.5, 1.5, linked=True),
                  "border_color": "#C9D1D9"})
    return W("button", s)


# Child containers in a flex row default to 100% width, i.e. one per line.
# These are the widths that actually produce 3- and 4-up grids.
COLW = {3: (31.5, 48, 100), 4: (23.2, 48, 100), 2: (48, 48, 100)}

def colw(cols):
    d, t, m = COLW[cols]
    return {"width": px(d, "%"), "width_tablet": px(t, "%"), "width_mobile": px(m, "%")}


def card(icon, title, body, link=None, dark=False, accent=CTA, cols=3):
    s = {
        "selected_icon": ico(icon), "title_text": title, "description_text": body,
        "position": "top", "title_size": "h3",
        "primary_color": accent,
        "icon_space": px(18),
        "title_color": "#FFFFFF" if dark else INK,
        "description_color": ON_DARK if dark else MUTED,
        "title_typography_typography": "custom",
        "title_typography_font_family": "Lexend",
        "title_typography_font_size": px(19),
        "title_typography_font_weight": "600",
        "description_typography_typography": "custom",
        "description_typography_font_size": px(15.5),
        "icon_size": px(26),
        "icon_padding": px(13),
        "view": "framed", "shape": "square", "border_radius_icon": box(8, 8, 8, 8),
    }
    if link:
        s["link"] = {"url": link}
    return C([W("icon-box", s)],
             content_width="full", **colw(cols),
             background_background="classic",
             background_color="#FFFFFF0B" if dark else "#FFFFFF",
             border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
             border_color="#FFFFFF24" if dark else BORDER,
             border_radius=box(14, 14, 14, 14),
             padding=box(30, 28, 30, 28))


def grid(cards, cols=3, g=32):
    return C(cards, content_width="boxed", flex_direction="row",
             flex_wrap="wrap", flex_gap=gap(g),
             padding=box(0, 24, 0, 24))


def section(children, dark=False, tint=False, pad=104, **extra):
    s = dict(content_width="full",
             padding=box(pad, 0, pad, 0),
             padding_tablet=box(72, 0, 72, 0),
             padding_mobile=box(56, 0, 56, 0),
             flex_gap=gap(0, 44))
    if dark:
        s.update(background_background="gradient",
                 background_color=MAROON_D, background_color_b=INK,
                 background_gradient_angle={"unit": "deg", "size": 160})
    elif tint:
        s.update(background_background="classic", background_color=TINT)
    else:
        s.update(background_background="classic", background_color="#FFFFFF")
    s.update(extra)
    return C(children, **s)


def head_block(eb, title, lead=None, dark=False, green=False, center=False, maxw=760):
    kids = [eyebrow(eb, dark, green), h2(title, dark)]
    if lead:
        kids.append(para(lead, dark, lead=True))
    return C(kids, content_width="boxed",
             flex_gap=gap(0, 14),
             padding=box(0, 24, 0, 24),
             flex_align_items="center" if center else "flex-start",
             text_align="center" if center else "left")


EL = []

# ---------------------------------------------------------------- 1. HERO
EL.append(C([
    C([
        W("heading", {"title": "Strategic alliance partner of APT Satellite (APStar), Hong Kong",
                      "header_size": "div", "title_color": "#FFFFFFD9",
                      "typography_typography": "custom", "typography_font_size": px(13),
                      "typography_font_weight": "500"}),
        W("heading", {"title": "A carrier-neutral teleport at the centre of Asia's satellite networks.",
                      "header_size": "h1", "title_color": "#FFFFFF"}),
        para("SGS operates satellite ground infrastructure in Rantau, Negeri Sembilan "
             "&mdash; gateway hosting, uplink, capacity leasing, backhaul and colocation, "
             "delivered from a single integrated site licensed by the MCMC.",
             dark=True, lead=True, color="#FFFFFFD6"),
        C([btn("Explore our services", "/our-services/", "primary"),
           btn("Tour the facility", "/about-us/#facility", "ghost-light")],
          content_width="full", flex_direction="row", flex_gap=gap(12),
          width=px(100, "%")),
    ], content_width="boxed", width=px(62, "%"), width_tablet=px(100, "%"),
       flex_gap=gap(0, 20), padding=box(0, 24, 0, 24)),
],
    content_width="full",
    min_height=px(680), min_height_mobile=px(560),
    flex_justify_content="center",
    padding=box(96, 0, 96, 0), padding_mobile=box(64, 0, 64, 0),
    background_background="classic",
    background_image=img("hero-teleport"),
    background_position="center center", background_size="cover",
    background_overlay_background="gradient",
    background_overlay_color="rgba(36,0,11,0.94)",
    background_overlay_color_b="rgba(18,4,10,0.32)",
    background_overlay_gradient_angle={"unit": "deg", "size": 100},
))

# fact strip
def fact(v, l):
    return C([
        W("heading", {"title": v, "header_size": "div", "title_color": "#FFFFFF",
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(22), "typography_font_weight": "600",
                      "typography_line_height": {"unit": "em", "size": 1.15, "sizes": []}}),
        W("heading", {"title": l, "header_size": "div", "title_color": "#FFFFFFA8",
                      "typography_typography": "custom", "typography_font_size": px(13)}),
    ], content_width="full", width=px(100, "%"), flex_gap=gap(0, 4),
       flex_justify_content="flex-end",
       border_border="solid", border_width=box(0, 0, 0, 1), border_color="#FFFFFF1C",
       padding=box(0, 0, 0, 22))

EL.append(C([
    C([fact("C-Band, Ku-Band, Ka-Band", "Frequency bands supported"),
       fact("GEO + LEO", "APStar fleet &amp; SPACESAIL constellation"),
       fact("65 km", "Dark fibre, full redundancy to KL1"),
       fact("Tier III", "Class data centre &amp; colocation")],
      content_width="boxed", flex_direction="row", flex_gap=gap(0),
      padding=box(22, 24, 22, 24)),
], content_width="full", background_background="classic",
   background_color="#0C0A14E6",
   border_border="solid", border_width=box(1, 0, 0, 0), border_color="#FFFFFF21"))

# -------------------------------------------------------- 2. LICENCES
def lic(code, title, body):
    return C([
        W("heading", {"title": code, "header_size": "div", "title_color": "#3F6619",
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(14), "typography_font_weight": "700",
                      "typography_letter_spacing": px(0.6),
                      "background_color": "#EEF7E4"}),
        C([W("heading", {"title": title, "header_size": "h4", "title_color": INK}),
           para(body)],
          content_width="full", width=px(100, "%"), flex_gap=gap(0, 4)),
    ], content_width="full", width=px(100, "%"),
       flex_direction="row", flex_gap=gap(16), flex_align_items="flex-start",
       background_background="classic", background_color="#FFFFFF",
       border_border="solid", border_width=box(1, 1, 1, 4), border_color=BORDER,
       border_radius=box(8, 8, 8, 8), padding=box(22, 22, 22, 22))

EL.append(section([
    C([
        C([eyebrow("Licensed &amp; regulated", green=True),
           h2("Operating within Malaysia's communications and multimedia framework.", size=30),
           para("Satcom Gateway Services Sdn Bhd holds the relevant licences and registrations "
                "issued by the Malaysian Communications and Multimedia Commission (MCMC).")],
          content_width="full", width=px(100, "%"), flex_gap=gap(0, 14)),
        C([lic("NFP", "Network Facilities Provider &mdash; Individual Licence",
               "Authorises SGS to own or provide network facilities."),
           lic("NSP", "Network Service Provider &mdash; Individual Licence",
               "Authorises SGS to provide network services."),
           lic("ASP(C)", "Applications Service Provider &mdash; Class",
               "Registered for the provision of applications services.")],
          content_width="full", width=px(100, "%"), flex_gap=gap(0, 14)),
    ], content_width="boxed", flex_direction="row", flex_gap=gap(56),
       flex_align_items="center", padding=box(0, 24, 0, 24)),
], pad=72)

)

# -------------------------------------------------------- 3. SERVICES
SERVICES = [
    ("satellite-dish", "Teleport &amp; Gateway Services",
     "Antenna positions, RF chain, equipment space and site operations to bring an operator&rsquo;s gateway into service.", "/our-services/#gateway", CTA),
    ("satellite", "Satellite Capacity Leasing",
     "Managed GEO capacity across APStar-5C, APStar-6D and APStar-9, plus low-latency LEO via SPACESAIL.", "/our-services/#capacity", GREEN_T),
    ("tower-broadcast", "Satellite Broadband &amp; Backhaul",
     "Enterprise VSAT networks and backhaul for sites where terrestrial infrastructure is limited or unavailable.", "/our-services/#broadband", MAROON),
    ("ship", "Satellite Mobility",
     "Maritime and aeronautical connectivity supported by Ku-band mobility beams and hybrid GEO&ndash;LEO routing.", "/our-services/#mobility", CTA),
    ("server", "Data Centre &amp; Colocation",
     "Carrier-neutral Tier III-class rack space, redundant power and interconnection, metres from the antenna farm.", "/our-services/#datacentre", GREEN_T),
    ("screwdriver-wrench", "Technical &amp; Ground-Segment Services",
     "Installation, commissioning, maintenance and remote support delivered by the team that runs the station.", "/our-services/#technical", MAROON),
]
EL.append(section([
    head_block("What we do", "Six service lines, one integrated ground segment.",
               "From hosting an operator's gateway on our antenna farm to leasing capacity and "
               "racking equipment in our data hall &mdash; SGS covers the full path from space to fibre.",
               center=True),
    grid([card(i, t, b, l, accent=a) for i, t, b, l, a in SERVICES], cols=3),
    C([btn("View all services", "/our-services/", "maroon")],
      content_width="boxed", flex_align_items="center", padding=box(0, 24, 0, 24)),
]))

# -------------------------------------------------------- 4. FACILITY
EL.append(section([
    C([
        C([W("image", {"image": img("antenna-array"), "image_size": "large",
                       "border_radius": box(14, 14, 14, 14)})],
          content_width="full", width=px(100, "%")),
        C([eyebrow("The ground station"),
           h2("Purpose-built for mission-critical satellite operations."),
           para("Our Kuala Lumpur gateway (KL2) sits 68&nbsp;km from KLIA and 80&nbsp;km from the "
                "metropolitan core &mdash; far enough for a clean RF environment, close enough for "
                "engineering access. It is linked to the TSGI ground station (KL1) by 65&nbsp;km of "
                "dark fibre operating in full redundancy."),
           W("icon-list", {
               "icon_list": [{"_id": eid(), "text": t, "selected_icon": ico("circle-check")}
                             for t in [
                   "Antenna farm supporting C-band, Ku-band and Ka-band operations",
                   "Dual telecommunications providers &mdash; Telekom Malaysia and Fiberail",
                   "Redundant power: utility feed, generator and battery plant",
                   "Dedicated telco room, server rooms and main switchboard rooms",
                   "On-site weather station and 24/7 monitored operations"]],
               "space_between": px(10), "icon_color": GREEN_T, "icon_size": px(15),
               "text_color": MUTED,
               "icon_typography_typography": "custom", "icon_typography_font_size": px(15.5)}),
           C([btn("View the facility", "/about-us/#facility", "maroon"),
              btn("Request a site visit", "/contact-us/", "ghost")],
             content_width="full", width=px(100, "%"), flex_direction="row", flex_gap=gap(12)),
          ], content_width="full", width=px(100, "%"), flex_gap=gap(0, 16)),
    ], content_width="boxed", flex_direction="row", flex_gap=gap(64),
       flex_align_items="center", padding=box(0, 24, 0, 24)),
], tint=True))

# -------------------------------------------------------- 5. FLEET (dark)
FLEET = [
    ("GEO &middot; 138&deg;E", "APStar-5C", "FS-1300 platform, 34 C-band and 32 Ku-band transponders, regional Ku-HTS payload, 15+ year design life."),
    ("GEO &middot; 134&deg;E", "APStar-6D", "Five-beam Ku-band user payload with a Ka-band gateway over Kuala Lumpur, optimised for aero and maritime mobility."),
    ("GEO", "APStar-9", "Broad regional coverage supporting video distribution, data and telecom services across the Asia-Pacific."),
    ("LEO Constellation", "SPACESAIL", "Low-latency LEO capacity building toward a 648-satellite constellation, hosted through the SGS LEO gateway."),
]
def fleet_card(tag, title, body):
    return C([
        W("heading", {"title": tag, "header_size": "div", "title_color": CYAN,
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(12), "typography_font_weight": "700",
                      "typography_letter_spacing": px(1.4)}),
        W("heading", {"title": title, "header_size": "h3", "title_color": "#FFFFFF"}),
        para(body, dark=True),
    ], content_width="full", **colw(4), flex_gap=gap(0, 10),
       background_background="classic", background_color="#FFFFFF0B",
       border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
       border_color="#FFFFFF24", border_radius=box(14, 14, 14, 14),
       padding=box(30, 28, 30, 28))

EL.append(section([
    head_block("Satellite fleet", "GEO reach and LEO responsiveness, from one gateway.",
               "SGS provides gateway hosting and capacity across the APStar geostationary fleet "
               "and the SPACESAIL low-earth-orbit constellation &mdash; so a single commercial "
               "relationship can cover both.", dark=True),
    grid([fleet_card(*f) for f in FLEET], cols=4, g=28),
    C([btn("See our capacity &amp; fleet options", "/our-services/#capacity", "primary")],
      content_width="boxed", padding=box(0, 24, 0, 24)),
], dark=True))

# -------------------------------------------------------- 6. VIDEO BAND
def vrow(video_slug, poster_slug, eb, title, body, link_text, link, flip=False):
    media = C([], content_width="full", width=px(54, "%"), width_tablet=px(100, "%"),
              min_height=px(400), min_height_mobile=px(260),
              background_background="video",
              background_video_link=url(video_slug),
              background_video_fallback=img(poster_slug),
              background_play_on_mobile="yes",
              border_radius=box(8, 8, 8, 8),
              overflow="hidden")
    panel = C([eyebrow(eb, dark=True),
               W("heading", {"title": title, "header_size": "h3", "title_color": "#FFFFFF",
                             "typography_typography": "custom",
                             "typography_font_family": "Lexend",
                             "typography_font_size": px(30), "typography_font_weight": "600",
                             "typography_line_height": {"unit": "em", "size": 1.18, "sizes": []}}),
               para(body, dark=True),
               btn(link_text, link, "primary")],
              content_width="full", width=px(46, "%"), width_tablet=px(100, "%"),
              flex_gap=gap(0, 14),
              background_background="classic", background_color="#080C1ACC",
              border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
              border_color="#FFFFFF21", border_radius=box(8, 8, 8, 8),
              padding=box(34, 34, 34, 34),
              margin=box(0, 0, 0, -70) if not flip else box(0, -70, 0, 0),
              margin_tablet=box(-40, 0, 0, 0),
              z_index=2)
    kids = [panel, media] if flip else [media, panel]
    return C(kids, content_width="boxed", flex_direction="row",
             flex_align_items="center", flex_gap=gap(0),
             padding=box(0, 24, 0, 24))

EL.append(section([
    vrow("constellation", "constellation-poster", "GEO + LEO",
         "Two orbits, one landing point.",
         "SGS hosts gateway operations for the APStar geostationary fleet and the SPACESAIL "
         "low-earth-orbit constellation on the same site &mdash; so a hybrid network needs one "
         "teleport, one engineering team and one agreement.",
         "See capacity leasing", "/our-services/#capacity"),
    vrow("dish", "dish-poster", "Ground segment",
         "The part of the network that stays on the ground.",
         "Antenna positions, RF chain, secure equipment space, redundant power &mdash; and the "
         "engineers who keep it all running. Carrier-neutral, MCMC-licensed, and 68&nbsp;km from "
         "Kuala Lumpur International Airport.",
         "Inside the facility", "/about-us/#facility", flip=True),
], dark=True))

# -------------------------------------------------------- 7. STATS
def stat(num, suffix, label):
    return C([W("counter", {
        "starting_number": 0, "ending_number": num, "suffix": suffix, "title": label,
        "duration": 1400,
        "number_color": MAROON,
        "typography_number_typography": "custom",
        "typography_number_font_family": "Lexend",
        "typography_number_font_size": px(44),
        "typography_number_font_weight": "600",
        "title_color": MUTED,
        "typography_title_typography": "custom",
        "typography_title_font_size": px(15),
    })], content_width="full", **colw(4),
        background_background="classic", background_color="#FFFFFF",
        border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
        border_color=BORDER, padding=box(30, 22, 30, 22), text_align="center")

EL.append(section([
    C([stat(3, "+", "GEO satellites hosted"),
       stat(648, "", "Target LEO constellation size"),
       stat(65, " km", "Redundant dark fibre to KL1"),
       stat(24, "/7", "Monitored teleport operations")],
      content_width="boxed", flex_direction="row", flex_gap=gap(1),
      padding=box(0, 24, 0, 24)),
], pad=72))

# -------------------------------------------------------- 8. WHY SGS
WHY = [
    ("shield-halved", "Carrier-neutral by design", "No preferred upstream. Operators, carriers and enterprises interconnect on equal terms with multiple fibre providers on site.", CTA),
    ("globe", "GEO and LEO under one roof", "Hybrid architectures combining geostationary reach with LEO latency, including hybrid router solutions for resilient links.", GREEN_T),
    ("handshake", "Backed by APStar", "A strategic alliance partner under APT Satellite Holdings, giving direct access to established regional fleet capacity.", MAROON),
    ("certificate", "Licensed and accountable", "MCMC individual licences as NFP and NSP, plus ASP(C) registration &mdash; a regulated counterparty for long-term hosting.", CTA),
    ("wave-square", "Engineering depth on site", "Installation, integration, commissioning, maintenance and remote support delivered by the team that runs the station.", GREEN_T),
    ("chart-line", "Positioned for growth", "Capacity and floor space to scale with cloud, OTT and IoT traffic, plus lower-CAPEX options using refurbished VSAT hardware.", MAROON),
]
EL.append(section([
    head_block("Why SGS", "Satellite networks need more than bandwidth.",
               "They need dependable ground infrastructure, operational expertise and a partner "
               "able to respond to the technical demands of mission-critical communications.",
               center=True),
    grid([card(i, t, b, accent=a) for i, t, b, a in WHY], cols=3),
], tint=True))

# -------------------------------------------------------- 9. INDUSTRIES
IND = [("industry", "Oil &amp; Gas", "Offshore platforms, pipelines and remote field operations.", MAROON),
       ("anchor", "Maritime", "VSAT connectivity for vessels, fleets and port operations.", CTA),
       ("seedling", "Agriculture", "Plantation telemetry, sensors and rural connectivity.", GREEN_T),
       ("landmark", "Government", "Resilient and emergency communications for public agencies.", MAROON)]
EL.append(section([
    head_block("Primary target industries", "Built for operations where terrestrial networks stop.",
               center=True),
    grid([card(i, t, b, accent=a, cols=4) for i, t, b, a in IND], cols=4, g=28),
]))

# -------------------------------------------------------- 10. PRODUCTS
PROD = [
    ("01", "Hybrid GEO&ndash;LEO connectivity", "A hybrid router solution integrating GEO and LEO networks for resilient, low-latency links that hold up when one network degrades."),
    ("02", "LEO data communication for IoT", "Ultra-low-cost LEO connectivity for connected devices, sensors and remote monitoring &mdash; and for emergency use where terrestrial networks are unavailable."),
    ("03", "Managed satcom bandwidth", "Cost-effective bandwidth packages tailored to enterprise, oil &amp; gas, maritime and rural deployments, with lower-CAPEX equipment options."),
]
def prod_card(num, title, body):
    return C([
        W("heading", {"title": num, "header_size": "div", "title_color": CTA,
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(12), "typography_font_weight": "700",
                      "typography_letter_spacing": px(1.4)}),
        W("heading", {"title": title, "header_size": "h3", "title_color": INK}),
        para(body),
    ], content_width="full", **colw(3), flex_gap=gap(0, 10),
       background_background="classic", background_color="#FFFFFF",
       border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
       border_color=BORDER, border_radius=box(14, 14, 14, 14), padding=box(30, 28, 30, 28))

EL.append(section([
    head_block("New in 2026", "Products added for the hybrid era.", green=True),
    grid([prod_card(*p) for p in PROD], cols=3),
]))

# -------------------------------------------------------- 11. NEWS
EL.append(section([
    C([C([eyebrow("Newsroom"), h2("Latest news &amp; events", size=34)],
         content_width="full", width=px(70, "%"), flex_gap=gap(0, 10)),
       C([btn("View all updates", "/news-events/", "ghost")],
         content_width="full", width=px(30, "%"), flex_align_items="flex-end")],
      content_width="boxed", flex_direction="row", flex_align_items="flex-end",
      padding=box(0, 24, 0, 24)),
    C([W("posts", {
        "posts_post_type": "post", "posts_per_page": 3, "posts_posts_per_page": 3,
        "columns": 3, "columns_tablet": 2, "columns_mobile": 1,
        "pagination_type": "", "show_excerpt": "yes", "excerpt_length": 18,
        "meta_data": ["date"],
        "item_gap": px(32),
        "box_border": "yes", "box_border_color": BORDER,
        "box_border_radius": box(14, 14, 14, 14),
        "title_color": INK, "excerpt_color": MUTED,
    })], content_width="boxed", padding=box(0, 24, 0, 24)),
], tint=True))

# -------------------------------------------------------- 12. CTA
EL.append(C([
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
      flex_gap=gap(48), padding=box(0, 24, 0, 24)),
],
    content_width="full",
    padding=box(84, 0, 84, 0), padding_mobile=box(56, 0, 56, 0),
    background_background="gradient",
    background_color="#340010", background_color_b=INK,
    background_gradient_angle={"unit": "deg", "size": 120},
))

c, b = wp.put_layout(HOME, EL)
print("home page %d -> %s, %d top-level sections" % (HOME, c, len(EL)))
wp.set_page_template(HOME, "elementor_header_footer")
print("cache cleared:", wp.clear_cache())
