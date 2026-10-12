"""Build the SGS Our Services page."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap
from sgs import *

wp = WP(); M = wp.media_map(); P = wp.page_map()
PID = P["our-services"]
def img(s): m = M.get(s, {}); return {"id": m.get("id"), "url": m.get("url")}

EL = []

# ---------------------------------------------------------------------------
# The fleet, from SGS Company Profile 2026 and the client's confirmed beam
# list. Names are kept exactly as those sources write them: "APStar-5C", not
# "APSTAR-5C", and "Ku ID beam" rather than a guess at what ID stands for.
#
# Every figure below is transcribed from the profile. APStar-6C and APStar-7
# appear only in the confirmed beam list, so they carry the band and nothing
# more -- no slot, no coverage, because neither was supplied.
# ---------------------------------------------------------------------------
FLEET = [
    ("APStar-5C", "138&deg;E",
     "FS-1300 platform, in service since the first half of 2018 with a design life "
     "beyond 15 years. 34 C-band and 32 Ku-band transponders plus a regional Ku-HTS "
     "payload.",
     [("Peak EIRP", "C-band 41&nbsp;dBW &middot; Ku-band 58&nbsp;dBW"),
      ("Peak G/T", "C-band 0&nbsp;dB/K &middot; Ku-band 12&nbsp;dB/K"),
      ("Gain control", "FGM and ALC"),
      ("Polarization", "Dual linear")],
     ["C-band", "Ku HTS beam", "Ku ID beam"]),

    ("APStar-6D", "134&deg;E",
     "Launched 2019, with the gateway in Kuala Lumpur. Optimised for mobility "
     "services, especially aeronautical and maritime.",
     [("Malaysia beams", "5 beams &mdash; 40, 51, 54, 55, 57"),
      ("User beam", "Ku-band"),
      ("Gateway beam", "Ka-band"),
      ("Gateway", "Kuala Lumpur")],
     ["Ku-band user beam"]),

    ("APStar-9", "142&deg;E",
     "DFH-4 platform, in service since 18 November 2015, with a 15-year lifetime and "
     "station keeping of &plusmn;0.05&deg;.",
     [("C-band", "2 fixed beams &mdash; SEA beam over Indonesia, Malaysia and PNG; "
                 "AP beam across the Asia Pacific region"),
      ("Ku-band", "3 fixed beams &mdash; West, North and South &mdash; plus 1 "
                  "elliptical steerable"),
      ("EIRP", "SEA beam 41&ndash;44&nbsp;dBW &middot; West beam 45&ndash;49&nbsp;dBW"),
      ("Channel control", "FGM / ALC")],
     ["C-band", "Ku West beam"]),

    ("APStar-6C", None,
     "Part of the confirmed SGS fleet. Detailed parameters available from our "
     "engineering team on request.",
     [], ["C-band"]),

    ("APStar-7", None,
     "Part of the confirmed SGS fleet. Detailed parameters available from our "
     "engineering team on request.",
     [], ["C-band"]),

    ("SPACESAIL", "LEO Constellation",
     "90 commercial satellites on orbit and building toward 648, landed through the "
     "SGS LEO gateway at Rantau.",
     [], ["LEO gateway hosting", "Hybrid GEO&ndash;LEO routing"]),
]

BEAMS = [(sat, beam) for sat, _slot, _d, _specs, beams in FLEET[:-1] for beam in beams]


def _spec_list(specs):
    rows = []
    for k, v in specs:
        rows.append(
            # border:0 because the theme puts a hairline on every th/td and a
            # spec list wants to read as prose, not as a nested table
            '<tr><th style="text-align:left;vertical-align:top;border:0;'
            'padding:5px 14px 5px 0;color:#7E89A3;font-weight:600;'
            'font-size:12.5px;white-space:nowrap;">'
            + k + '</th><td style="border:0;padding:5px 0;color:#D3DAE8;'
            'font-size:13.5px;">'
            + v + "</td></tr>")
    return ('<table style="width:100%;border-collapse:collapse;">'
            + "".join(rows) + "</table>")


def sat_card(name, slot, blurb, specs, beams, cols=3):
    """The orbital slot carries the card instead of a photograph -- there is no
    per-satellite imagery in the materials, and the slot set in cyan says more
    than a stock dish would."""
    kids = [W("heading", {"title": slot or "&nbsp;", "header_size": "div",
                          "title_color": CYAN if slot else "#00000000",
                          "typography_typography": "custom",
                          "typography_font_family": "Lexend",
                          "typography_font_size": px(24),
                          "typography_font_weight": "600"}),
            h3(name, size=21),
            para(blurb, size=15)]
    if specs:
        kids.append(W("html", {"html": _spec_list(specs)}))
    kids += [W("divider", {"color": BORDER, "weight": px(1), "gap": px(13)}),
             W("heading", {"title": "SGS capacity", "header_size": "div",
                           "title_color": SUBTLE,
                           "typography_typography": "custom",
                           "typography_font_family": "Lexend",
                           "typography_font_size": px(11),
                           "typography_font_weight": "700",
                           "typography_letter_spacing": px(1.4),
                           "typography_text_transform": "uppercase"}),
             ticks(beams)]
    return C(kids, content_width="full", **colw(cols), flex_gap=gap(0, 8),
             background_background="classic", background_color=SURFACE,
             border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
             border_color=BORDER, border_radius=box(14, 14, 14, 14),
             padding=box(28, 26, 30, 26))


# Built by concatenation, not %-formatting: the inline styles are full of
# percent signs and every one would need doubling.
_TH = ("text-align:left;padding:13px 16px;color:#A9B3C9;font-size:12.5px;"
       "letter-spacing:.06em;text-transform:uppercase;font-weight:700;"
       "border-bottom:1px solid #2E3758;")
_TD = "padding:13px 16px;color:#E9EDF6;border-bottom:1px solid #1D2440;"
_rows = []
for _i, (_sat, _beam) in enumerate(BEAMS):
    _zebra = ' style="background:rgba(255,255,255,.035);"' if _i % 2 else ""
    _rows.append("<tr" + _zebra + ">"
                 '<td style="' + _TD + 'font-weight:600;white-space:nowrap;">'
                 + _sat + "</td>"
                 '<td style="' + _TD + '">' + _beam + "</td></tr>")
BEAM_TABLE = ('<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;">'
              '<table style="width:100%;border-collapse:collapse;font-size:15px;">'
              "<thead><tr>"
              '<th style="' + _TH + '">Satellite</th>'
              '<th style="' + _TH + '">Band / beam</th>'
              "</tr></thead><tbody>" + "".join(_rows) + "</tbody></table></div>")


EL.append(page_hero(
    'Home &nbsp;/&nbsp; Our Services', "Our services",
    "Reliable satellite capacity and end-to-end ground solutions.",
    "SGS supports a broad range of satellite communication applications &mdash; from hosting an "
    "operator's gateway on our antenna farm through to leasing capacity, hauling traffic onto "
    "fibre and racking equipment in our data hall."))

# --- index ----------------------------------------------------------------
IDX = [("01", "Teleport &amp; Gateway Services", "#gateway"),
       ("02", "Satellite Capacity Leasing", "#capacity"),
       ("03", "Satellite Broadband, Enterprise &amp; Backhaul", "#broadband"),
       ("04", "Satellite Mobility", "#mobility"),
       ("05", "Data Centre &amp; Colocation Services", "#datacentre"),
       ("06", "Technical &amp; Ground-Segment Services", "#technical")]

def idx_card(num, title, link):
    return C([
        W("heading", {"title": num, "header_size": "div", "title_color": CTA,
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(12), "typography_font_weight": "700",
                      "typography_letter_spacing": px(1.4)}),
        W("heading", {"title": title, "header_size": "h3", "title_color": INK,
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(17), "typography_font_weight": "600",
                      "link": {"url": link}})],
        content_width="full", **colw(3), flex_gap=gap(0, 6),
        background_background="classic", background_color=SURFACE,
        border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
        border_color=BORDER, border_radius=box(14, 14, 14, 14), padding=box(22, 22, 22, 22))

EL.append(section([grid([idx_card(*i) for i in IDX], g=20)], tint=True, pad=64))

# The fleet is the thing customers arrive looking for, so it gets a band of
# its own above the service detail rather than only a section further down.
EL.append(C([
    C([C([eyebrow("SGS Satellite Fleet", dark=True),
          h2("%d beams across five APStar satellites." % len(BEAMS), dark=True, size=30),
          para("C-band, Ku-band and Ku-HTS capacity, landed at the SGS teleport "
               "in Rantau.", dark=True)],
         content_width="full", width=px(62, "%"), width_tablet=px(100, "%"),
         flex_gap=gap(0, 10)),
       C([btn("See the fleet", "#fleet", "primary"),
          btn("Beam by beam", "#beams", "ghost-light")],
         content_width="full", width=px(38, "%"), width_tablet=px(100, "%"),
         flex_direction="row", flex_wrap="wrap", flex_gap=gap(12), **BTN_STACK,
         flex_justify_content="flex-end", flex_justify_content_tablet="flex-start")],
      content_width="boxed", flex_direction="row", flex_align_items="center",
      flex_gap=gap(40), padding=box(0, 24, 0, 24), **STACK_TABLET)],
    content_width="full", padding=box(52, 0, 52, 0),
    background_background="gradient", background_color="#131A33",
    background_color_b=SPACE_D,
    background_gradient_angle={"unit": "deg", "size": 120},
    border_border="solid", border_width=box(1, 0, 1, 0), border_color=BORDER))

# --- 01 gateway -----------------------------------------------------------
EL.append(section([split(
    half([eyebrow("01 &mdash; Teleport &amp; Gateway Services"),
          h2("Host your gateway on our ground."),
          para("Infrastructure and operational support for satellite gateway and ground-segment "
               "deployments. SGS provides the antenna positions, RF chain, equipment space, power "
               "and people required to bring a gateway into service &mdash; and to keep it in service."),
          ticks(["Antenna hosting and uplink infrastructure across C, Ku and Ka bands",
                 "Gateway hosting for APStar-5C, APStar-6D and the SPACESAIL LEO constellation",
                 "Secure equipment rooms directly adjacent to the antenna farm",
                 "Redundant power and environmental systems",
                 "Installation, integration, commissioning and ongoing site operations"]),
          C([btn("Discuss a gateway deployment", "/contact-us/", "maroon")],
            content_width="full", width=px(100, "%"))]),
    figure(img("antenna-3")))], anchor="gateway"))

# --- 02 capacity (dark) ---------------------------------------------------


TABLE = """<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;"><table style="width:100%;border-collapse:collapse;font-size:15px;">
<thead><tr style="background:#FFFFFF17;">
<th style="text-align:left;padding:14px 16px;color:#fff;font-size:13px;letter-spacing:.04em;text-transform:uppercase;">Business model</th>
<th style="text-align:left;padding:14px 16px;color:#fff;font-size:13px;letter-spacing:.04em;text-transform:uppercase;">What SGS provides</th>
<th style="text-align:left;padding:14px 16px;color:#fff;font-size:13px;letter-spacing:.04em;text-transform:uppercase;">Typical customer</th>
</tr></thead><tbody>
<tr><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;font-weight:600;">Gateway hosting</td><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;">Antenna position, RF chain, equipment space, power, site operations</td><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;">Satellite operators and constellation programmes</td></tr>
<tr style="background:#FFFFFF0D;"><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;font-weight:600;">Capacity leasing</td><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;">GEO and LEO space segment, managed and monitored</td><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;">Service providers, ISPs, enterprise networks</td></tr>
<tr><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;font-weight:600;">End-to-end managed service</td><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;">Space segment plus teleport, backhaul, IP and terminals</td><td style="padding:14px 16px;color:#F7F3F4;border-bottom:1px solid #FFFFFF1A;">Enterprises without in-house satcom engineering</td></tr>
<tr style="background:#FFFFFF0D;"><td style="padding:14px 16px;color:#F7F3F4;font-weight:600;">Colocation only</td><td style="padding:14px 16px;color:#F7F3F4;">Carrier-neutral rack space, power and interconnection</td><td style="padding:14px 16px;color:#F7F3F4;">Carriers, broadcasters, network operators</td></tr>
</tbody></table></div>"""

EL.append(section([
    head_block("02 &mdash; Satellite Capacity Leasing", "Managed capacity, matched to the mission.",
               "Access to satellite capacity across the APStar geostationary fleet and the "
               "SPACESAIL LEO constellation, packaged as a managed service rather than raw "
               "megahertz.", dark=True),
    C([W("html", {"html": TABLE})], content_width="boxed", padding=box(0, 24, 0, 24)),
    C([figure(img("spacesail-radome"),
              "The SPACESAIL LEO radome on the facility roof at Rantau."),
       figure(img("spectrum-analyzer"),
              "Spectrum analysis &mdash; carrier monitoring and link verification on site.")],
      content_width="boxed", flex_direction="row", flex_gap=gap(32),
      padding=box(0, 24, 0, 24)),
], dark=True, anchor="capacity"))

# --- the fleet, in full ---------------------------------------------------
EL.append(section([
    head_block("SGS Satellite Fleet",
               "The fleet, satellite by satellite.",
               "Every beam below is landed at the SGS teleport, so the space segment and "
               "the ground segment come from one site and one engineering team. "
               "Figures are from the SGS company profile.", center=True),
    grid([sat_card(*f) for f in FLEET[:3]], g=28),
    grid([sat_card(*f) for f in FLEET[3:]], g=28),
], anchor="fleet"))

# --- confirmed capacity, beam by beam -------------------------------------
EL.append(section([
    head_block("Confirmed capacity", "Beam by beam.",
               "Footprint maps, EIRP and G/T figures and a link budget for your "
               "terminal are available from our engineering team on request.",
               dark=True),
    C([W("html", {"html": BEAM_TABLE})], content_width="boxed",
      padding=box(0, 24, 0, 24)),
    C([btn("Request footprints &amp; link budgets", "/contact-us/", "primary"),
       btn("Talk to our engineers", "/contact-us/", "ghost-light")],
      content_width="boxed", flex_direction="row", flex_wrap="wrap",
      flex_gap=gap(12), **BTN_STACK, padding=box(0, 24, 0, 24)),
], dark=True, anchor="beams"))

# --- 03 broadband ---------------------------------------------------------
EL.append(section([split(
    half([eyebrow("03 &mdash; Satellite Broadband, Enterprise Networks &amp; Backhaul"),
          h2("From the dish to the internet, without leaving the site."),
          para("Connectivity solutions for businesses and organisations requiring reliable "
               "communications beyond conventional terrestrial networks &mdash; plus satellite "
               "backhaul for locations where terrestrial infrastructure is limited or unavailable."),
          ticks(["Satellite broadband and enterprise VSAT networks",
                 "Satellite backhaul for remote sites and rural cell towers",
                 "IP gateway provisioning and network integration",
                 "Two on-site telecommunications providers: Telekom Malaysia and Fiberail",
                 "65&nbsp;km of dark fibre to the KL1 ground station in full redundancy",
                 "Console Connect (PCCW Global) under evaluation for worldwide reach"])]),
    figure(img("telco-room"),
           "Telco room &mdash; carrier hand-off point for Telekom Malaysia and Fiberail."),
    media_first=True)], tint=True, anchor="broadband"))

# --- 04 mobility ----------------------------------------------------------
EL.append(section([split(
    half([eyebrow("04 &mdash; Satellite Mobility"),
          h2("Connectivity that moves with the asset."),
          para("Connectivity services supporting mobile and maritime applications. APStar-6D's "
               "user beams are optimised for mobility, making the SGS gateway a natural landing "
               "point for vessels and aircraft operating across the region."),
          ticks(["Maritime VSAT for vessels, fleets and port operations",
                 "Aeronautical connectivity supported by Ku-band mobility beams",
                 "Hybrid GEO&ndash;LEO router solutions for resilient, low-latency links",
                 "Roaming across the APStar footprint from a single gateway relationship"]),
          pills(["Maritime", "Aero", "Offshore energy", "Land mobile"])]),
    figure(img("antenna-4")))], anchor="mobility"))

# --- 05 data centre -------------------------------------------------------
EL.append(section([split(
    half([eyebrow("05 &mdash; Data Centre &amp; Colocation Services"),
          h2("Carrier-neutral space beside the antenna farm."),
          para("Secure infrastructure for hosting satellite, telecommunications and network "
               "equipment. Because the data hall shares a site with the teleport, gateway and IT "
               "infrastructure sit metres apart rather than cities apart."),
          ticks(["Tier III-class data centre environment",
                 "Secure equipment racks with controlled access",
                 "Redundant power: utility feed, standby generator and battery plant",
                 "Environmental control and continuous monitoring",
                 "Gateway and broadcasting infrastructure hosting"]),
          C([btn("See the facility", "/about-us/#facility", "maroon")],
            content_width="full", width=px(100, "%"))]),
    figure(img("server-room-1")), media_first=True)], tint=True, anchor="datacentre"))

# --- 06 technical ---------------------------------------------------------
TECH = [("Deploy", "Installation &amp; integration",
         "Antenna, RF and baseband installation, integrated with the customer's network architecture."),
        ("Verify", "Commissioning &amp; testing",
         "Line-up, link-budget verification and acceptance testing before traffic is carried."),
        ("Sustain", "Maintenance &amp; site operations",
         "Preventive and corrective maintenance, spares handling and day-to-day site operations."),
        ("Support", "Remote &amp; managed support",
         "Monitoring, remote hands and managed services covering cloud, OTT and IoT traffic growth.")]
EL.append(section([
    split(figure(img("rf-engineer"),
                 "RF testing at the equipment racks &mdash; commissioning and fault-finding on site."),
          half([eyebrow("06 &mdash; Technical &amp; Ground-Segment Services"),
                h2("The engineering behind the link."),
                para("Installation, commissioning, maintenance, remote support and operational "
                     "assistance for satellite communication infrastructure &mdash; delivered by "
                     "the team that runs the station day to day.", lead=True)])),
    grid([plain_card(t, n, b, cols=4) for t, n, b in TECH], g=28),
], anchor="technical"))

# --- products (dark) ------------------------------------------------------
PROD = [("01", "Hybrid GEO&ndash;LEO connectivity",
         "A hybrid router solution integrating GEO and LEO networks for resilient, low-latency "
         "links that hold up when one network degrades. Hardware bundle plus pricing models for "
         "enterprise, maritime and remote operations."),
        ("02", "LEO data communication for IoT",
         "Ultra-low-cost LEO connectivity for connected devices, sensors and remote monitoring "
         "&mdash; and for emergency use where terrestrial networks are unavailable. IoT terminals "
         "and flexible pricing for large-scale deployments."),
        ("03", "Managed satcom bandwidth",
         "Cost-effective packages tailored to enterprise, oil &amp; gas, maritime and rural "
         "deployments. Lower-cost equipment options, including refurbished VSAT antennas and BUCs "
         "to reduce customer CAPEX.")]
EL.append(section([
    head_block("New in 2026", "Products added for the hybrid era.", dark=True),
    grid([plain_card(n, t, b, dark=True, cols=3) for n, t, b in PROD]),
], dark=True))

# --- industries -----------------------------------------------------------
IND = [("industry", "Oil &amp; Gas", "Offshore platforms, pipelines and remote field operations.", MAROON),
       ("anchor", "Maritime", "VSAT connectivity for vessels, fleets and port operations.", CTA),
       ("seedling", "Agriculture", "Plantation telemetry, sensors and rural connectivity.", GREEN_T),
       ("landmark", "Government", "Resilient and emergency communications for public agencies.", MAROON)]
EL.append(section([
    head_block("Primary target industries", "Built for operations where terrestrial networks stop.",
               green=True, center=True),
    grid([card(i, t, b, accent=a, cols=4) for i, t, b, a in IND], g=28),
]))

# --- FAQ ------------------------------------------------------------------
FAQ = [("Which frequency bands can SGS support?",
        "Our infrastructure supports C-band, Ku-band and Ka-band operations, covering both "
        "traditional wide-beam payloads and High Throughput Satellite architectures, as well as "
        "LEO gateway systems."),
       ("Is the teleport genuinely carrier-neutral?",
        "Yes. Two telecommunications providers are present on site &mdash; Telekom Malaysia and "
        "Fiberail &mdash; and customers may interconnect with either. We are also evaluating "
        "Console Connect from PCCW Global to extend multi-platform connectivity worldwide."),
       ("What happens if the primary fibre path fails?",
        "The SGS ground station (KL2) is connected to the TSGI ground station (KL1), 70.9&nbsp;km "
        "away, by 65&nbsp;km of dark fibre operating in a full redundancy mode."),
       ("Can SGS reduce the equipment CAPEX for a new deployment?",
        "Our managed satcom bandwidth packages are designed around lower-cost equipment, and can "
        "incorporate refurbished VSAT antennas and BUCs where the link budget allows."),
       ("Does SGS provide operational support after commissioning?",
        "Yes. SGS provides installation, integration, commissioning, maintenance, remote support "
        "and ongoing site operations &mdash; delivered by the team that runs the station.")]
EL.append(section([
    head_block("Common questions", "Frequently asked", center=True),
    C([W("accordion", {
        "tabs": [{"_id": eid(), "tab_title": q, "tab_content": "<p>%s</p>" % a} for q, a in FAQ],
        "selected_icon": ico("plus"), "selected_active_icon": ico("minus"),
        "title_color": INK, "tab_active_color": CYAN,
        "content_color": MUTED,
        "border_color": BORDER,
        "title_typography_typography": "custom",
        "title_typography_font_family": "Lexend",
        "title_typography_font_size": px(17), "title_typography_font_weight": "600",
    })], content_width="boxed", padding=box(0, 24, 0, 24),
       width=px(900), max_width=px(900)),
], tint=True))

EL.append(cta_band())

c, _ = wp.put_layout(PID, EL)
wp.set_page_template(PID, "elementor_header_footer")
print("services page %d -> %s, %d sections | cache %s" % (PID, c, len(EL), wp.clear_cache()))
