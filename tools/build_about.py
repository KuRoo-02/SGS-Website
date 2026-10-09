"""Build the SGS About Us page."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap
from sgs import *

wp = WP(); M = wp.media_map(); P = wp.page_map()
PID = P["about-us"]
def img(s): m = M.get(s, {}); return {"id": m.get("id"), "url": m.get("url")}

EL = []

EL.append(page_hero(
    'Home &nbsp;/&nbsp; About Us', "Company profile",
    "Satellite ground infrastructure, operated from Malaysia.",
    "Satcom Gateway Services Sdn Bhd (SGS) is a Malaysia-based satellite communications and "
    "teleport services provider supporting the evolving needs of enterprise, telecommunications, "
    "maritime and satellite network operators."))

# --- who we are -----------------------------------------------------------
EL.append(section([split(
    half([eyebrow("Who we are"),
          h2("Established to provide reliable, scalable satellite communication infrastructure."),
          para("SGS operates and manages satellite ground infrastructure designed to support "
               "gateway, uplink and connectivity requirements. Our capabilities span teleport "
               "operations, satellite broadband, enterprise connectivity, satellite mobility, "
               "satellite backhaul, satellite capacity leasing, data centre and colocation "
               "services, and related satellite ground-segment support."),
          para("Our facilities provide the infrastructure required to host and operate critical "
               "satellite gateway equipment, including antenna systems, secure equipment racks, "
               "redundant power and supporting environmental systems. SGS also provides technical "
               "and operational support covering installation, integration, commissioning, "
               "maintenance and ongoing site operations.")]),
    figure(img("facility-2"),
           "The SGS ground station (KL2) &mdash; antenna farm, operations building and data hall "
           "on one secured site."))]))

# --- at a glance (dark) ---------------------------------------------------
EL.append(section([
    head_block("At a glance", "What SGS brings to the region.", dark=True),
    grid([
        plain_card(None, "Strategic alliance under APStar Hong Kong",
                   "SGS operates as a strategic alliance partner under APT Satellite Holdings, "
                   "connecting Malaysian ground infrastructure to an established regional fleet.",
                   dark=True, cols=2),
        plain_card(None, "Carrier-neutral teleport",
                   "A satellite ground station in Rantau, Negeri Sembilan, open to multiple "
                   "operators and carriers on equal commercial terms.", dark=True, cols=2),
        plain_card(None, "Integrated data centre &amp; IP gateway",
                   "Tier III-class data centre space, IP gateway and network services co-located "
                   "with the antenna farm &mdash; no intermediate haul between dish and rack.",
                   dark=True, cols=2),
        plain_card(None, "GEO and LEO gateway hosting",
                   "Hosting across APStar-9, APStar-5C, APStar-6D and the SPACESAIL LEO "
                   "constellation.", dark=True, cols=2),
    ]),
], dark=True))

# --- licences -------------------------------------------------------------
def lic(code, title, body):
    return C([
        W("heading", {"title": code, "header_size": "div", "title_color": GREEN_D,
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(14), "typography_font_weight": "700"}),
        h3(title, size=17), para(body, size=15)],
        content_width="full", **colw(3), flex_gap=gap(0, 8),
        background_background="classic", background_color="#FFFFFF",
        border_border="solid", border_width=box(1, 1, 1, 4), border_color=BORDER,
        border_radius=box(8, 8, 8, 8), padding=box(24, 24, 24, 24))

EL.append(section([
    head_block("Licensed &amp; regulated", "A regulated counterparty for long-term hosting.",
               "Satcom Gateway Services Sdn Bhd operates within Malaysia's communications and "
               "multimedia regulatory framework and holds relevant licences and registrations "
               "issued by the MCMC.", green=True),
    grid([lic("NFP", "Network Facilities Provider",
              "Individual Licence. Authorises SGS to own or provide network facilities."),
          lic("NSP", "Network Service Provider",
              "Individual Licence. Authorises SGS to provide network services."),
          lic("ASP(C)", "Applications Service Provider",
              "Class registration for the provision of applications services.")]),
]))

# --- built for reliable connectivity --------------------------------------
EL.append(section([split(
    half([eyebrow("Our approach"), h2("Built for reliable connectivity."),
          para("Satellite networks require more than bandwidth. They require dependable ground "
               "infrastructure, operational expertise and the ability to respond to the technical "
               "demands of mission-critical communications."),
          para("SGS combines teleport infrastructure, satellite ground systems and technical "
               "capabilities to provide an integrated environment for satellite network deployment "
               "and operations. Our infrastructure supports C-band, Ku-band and Ka-band, while our "
               "experience extends across both traditional satellite networks and emerging Low "
               "Earth Orbit technologies."),
          pills(["C-band", "Ku-band", "Ka-band", "HTS", "LEO"])]),
    figure(img("teleport-security")), media_first=True)], tint=True))

# --- APStar alliance ------------------------------------------------------
def tl(year, title, body):
    return C([
        W("heading", {"title": year, "header_size": "div", "title_color": CTA,
                      "typography_typography": "custom", "typography_font_family": "Lexend",
                      "typography_font_size": px(12), "typography_font_weight": "700",
                      "typography_letter_spacing": px(1.4)}),
        h3(title, size=17), para(body, size=15)],
        content_width="full", width=px(100, "%"), flex_gap=gap(0, 4),
        border_border="solid", border_width=box(0, 0, 0, 2), border_color="#D7DEE6",
        padding=box(0, 0, 22, 20))

EL.append(section([split(
    half([eyebrow("The APStar alliance"),
          h2("Malaysian ground segment, regional space segment."),
          para("SGS is a strategic alliance partner under APStar Hong Kong &mdash; APT Satellite "
               "Holdings, an established regional satellite operator serving the Asia-Pacific. The "
               "relationship gives customers a direct route from a Malaysian gateway onto the "
               "APStar geostationary fleet, and from there to markets across the region."),
          para("It also underpins the SGS LEO programme with SPACESAIL, allowing hybrid GEO&ndash;LEO "
               "services to be designed, hosted and supported from the same site."),
          C([btn("Explore the fleet", "/our-services/#capacity", "maroon"),
             btn("Visit apstar.com", "https://www.apstar.com/", "ghost")],
            content_width="full", width=px(100, "%"), flex_direction="row", flex_gap=gap(12))]),
    half([tl("2011 &ndash; 2018", "Foundational research",
             "SPACESAIL research on key LEO technologies; company founded in 2018."),
          tl("2018 &ndash; 2019", "APStar-5C and APStar-6D enter service",
             "APStar-5C launched in the first half of 2018 at 138&deg;E; APStar-6D follows in 2019 "
             "at 134&deg;E with a Kuala Lumpur gateway beam."),
          tl("2021 &ndash; 2023", "LEO programme accelerates",
             "Test satellite batches launched; NDRC project approval, two ITU filings and inclusion "
             "in Shanghai's commercial space plan."),
          tl("2024 &ndash; present", "Constellation build-out",
             "90 commercial satellites on orbit, moving toward a 648-satellite target constellation."),
          tl("2026", "SGS expands its service portfolio",
             "Hybrid GEO&ndash;LEO connectivity, low-cost LEO IoT and managed satcom bandwidth "
             "packages added to the catalogue.")],
         flex_gap=gap(0, 0)))]))

# --- facility + gallery ---------------------------------------------------
GAL = [
    ("antenna-array", "Antenna array"), ("spacesail-radome", "SPACESAIL radome"),
    ("security-monitoring", "24/7 monitoring"), ("engineers-racks", "Engineering on site"),
    ("server-room-1", "Server room"), ("telco-room", "Telco room"),
    ("switchboard-1", "Main switchboard"), ("facility-1", "Site overview"),
    ("battery-room", "Battery room"), ("generator", "Standby generator"),
    ("office-team", "Office"), ("weather-station", "Weather station"),
    ("antenna-1", "Antenna farm"), ("spectrum-analyzer", "Spectrum analysis"),
]
EL.append(section([
    head_block("Our facility", "Inside the Rantau ground station.",
               "The SGS ground station (KL2) sits in the southern part of the Kuala Lumpur region "
               "&mdash; 68&nbsp;km and about 53 minutes' drive from KLIA, 80&nbsp;km from the "
               "metropolitan core. Antenna farm, data hall, power plant and operations are on one "
               "secured site."),
    grid([
        plain_card("Antennas", "C &middot; Ku &middot; Ka band",
                   "Antenna farm supporting geostationary and LEO tracking operations.", cols=4),
        plain_card("Connectivity", "Two fibre providers",
                   "Telekom Malaysia and Fiberail on site; 65&nbsp;km dark fibre to KL1 in full "
                   "redundancy.", cols=4),
        plain_card("Power", "Redundant plant",
                   "Utility feed, standby generator, battery plant and main switchboard rooms.",
                   cols=4),
        plain_card("Data hall", "Tier III class",
                   "Secure racks, environmental control and continuous monitoring.", cols=4),
    ], g=28),
    # core widget is "image-gallery" with a wp_gallery control; the Pro
    # "gallery" widget uses a different schema and renders empty here
    C([W("image-gallery", {
        "wp_gallery": [{"id": M[s]["id"], "url": M[s]["url"]} for s, _ in GAL if s in M],
        "gallery_columns": 4, "gallery_columns_tablet": 3, "gallery_columns_mobile": 2,
        "gallery_link": "file", "open_lightbox": "yes",
        "thumbnail_size": "medium_large",
        "image_spacing_custom": px(12),
        "image_border_radius": box(8, 8, 8, 8),
    })], content_width="boxed", padding=box(0, 24, 0, 24)),
    C([btn("Request a site visit", "/contact-us/", "maroon"),
       btn("Data centre &amp; colocation", "/our-services/#datacentre", "ghost")],
      content_width="boxed", flex_direction="row", flex_gap=gap(12),
      padding=box(0, 24, 0, 24)),
], anchor="facility"))

# --- supporting global networks (dark) ------------------------------------
EL.append(section([
    head_block("Regional platform", "Supporting global satellite networks from Malaysia.",
               "Strategically located in Malaysia, SGS provides a platform for satellite and "
               "telecommunications partners seeking to establish or expand their network presence "
               "in the region.", dark=True, center=True),
    grid([
        plain_card(None, "Satellite gateway deployments",
                   "Experience supporting operators bringing new gateway infrastructure into "
                   "service.", dark=True, cols=4),
        plain_card(None, "HTS infrastructure",
                   "Ground systems for High Throughput Satellite payloads and spot-beam "
                   "architectures.", dark=True, cols=4),
        plain_card(None, "LEO gateway systems",
                   "Tracking antenna and gateway support for low-earth-orbit constellations.",
                   dark=True, cols=4),
        plain_card(None, "Maritime VSAT",
                   "Connectivity projects for vessels and fleets operating across regional waters.",
                   dark=True, cols=4),
    ], g=28),
], dark=True))

EL.append(cta_band())

c, _ = wp.put_layout(PID, EL)
wp.set_page_template(PID, "elementor_header_footer")
print("about page %d -> %s, %d sections | cache %s" % (PID, c, len(EL), wp.clear_cache()))
