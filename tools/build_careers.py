"""Build the SGS Careers page.

Follows the shape of APStar's career-development page -- intro, how to
apply, then the vacancies -- but the openings are an accordion rather than
one long stack of text, so a visitor sees every role at a glance and opens
only the one they want.

NOTE: the single opening below is placeholder content. It reads as a real
vacancy on a live, public site, so it should be replaced with a genuine one
or removed before SGS start promoting the page -- otherwise it will attract
real applications for a job that does not exist.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap
from sgs import *

wp = WP(); M = wp.media_map(); P = wp.page_map()
TO = "info@satcomgs.com"


def img(s):
    m = M.get(s, {})
    return {"id": m.get("id"), "url": m.get("url")}


# --------------------------------------------------------------------------
# page + menu entry
# --------------------------------------------------------------------------
if "careers" in P:
    PID = P["careers"]
    print("careers page exists -> %d" % PID)
else:
    c, b = wp.call("/wp-json/wp/v2/pages", "POST",
                   {"title": "Careers", "slug": "careers", "status": "publish",
                    "template": "elementor_header_footer"})
    PID = b["id"]
    print("careers page created -> %d (%s)" % (PID, c))

MID = wp.menu_id("Primary")
c, items = wp.call("/wp-json/wp/v2/menu-items?menus=%d&per_page=50" % MID)
have = {i["title"]["rendered"]: i for i in (items or [])}
if "Careers" not in have:
    # sits between the newsroom and Contact, the way APStar files it
    c, b = wp.call("/wp-json/wp/v2/menu-items", "POST",
                   {"title": "Careers", "menus": MID, "status": "publish",
                    "type": "post_type", "object": "page", "object_id": PID,
                    "menu_order": 5})
    print("menu item created -> %s" % c)
    contact = have.get("Contact Us")
    if contact:
        wp.call("/wp-json/wp/v2/menu-items/%d" % contact["id"], "POST",
                {"menu_order": 6})
        print("  Contact Us moved to order 6")
else:
    print("menu item exists -> %d" % have["Careers"]["id"])


# --------------------------------------------------------------------------
# openings
# --------------------------------------------------------------------------
LINK = ("color:#3FC8F5;font-weight:600;text-decoration:none;"
        "border-bottom:1px solid rgba(63,200,245,.45);padding-bottom:1px;")
META = ("margin:0 0 18px;padding:10px 14px;background:rgba(255,255,255,.06);border-radius:8px;"
        "font-size:14.5px;color:#E9EDF6;")
H = "margin:22px 0 8px;font-family:Lexend,sans-serif;font-size:14px;font-weight:700;color:#E9EDF6;"
UL = "margin:0;padding-left:20px;line-height:1.7;"


def opening(title, meta, responsibilities, requirements):
    subject = "Application%20%E2%80%94%20" + title.replace(" ", "%20")
    html = ['<p style="%s"><strong>%s</strong></p>' % (META, meta),
            '<p style="%s">Responsibilities</p><ul style="%s">%s</ul>'
            % (H, UL, "".join("<li>%s</li>" % r for r in responsibilities)),
            '<p style="%s">Requirements</p><ul style="%s">%s</ul>'
            % (H, UL, "".join("<li>%s</li>" % r for r in requirements)),
            '<p style="margin:22px 0 0;"><a style="%s" href="mailto:%s?subject=%s">'
            'Email us your resume for this role &rarr;</a></p>' % (LINK, TO, subject)]
    return {"_id": eid(), "tab_title": title, "tab_content": "".join(html)}


OPENINGS = [opening(
    "Teleport Operations Engineer",
    "SGS Ground Station (KL2), Rantau, Negeri Sembilan &nbsp;&middot;&nbsp; "
    "Full time &nbsp;&middot;&nbsp; Shift duty required",
    ["Operate and monitor antenna, RF and baseband systems across the C-band, Ku-band "
     "and Ka-band chains.",
     "Carry out carrier monitoring and link verification, and investigate interference "
     "using spectrum analysis.",
     "Perform first-line fault isolation across the RF chain, satellite modems and "
     "terrestrial links, escalating to vendors and customers where required.",
     "Support the installation, integration and commissioning of hosted gateway "
     "equipment on the antenna farm.",
     "Maintain operational logs for power, environmental and site-access systems.",
     "Contribute to 24/7 monitored teleport operations on a shift roster."],
    ["Diploma or Degree in Electronics, Telecommunications or Electrical Engineering.",
     "Two or more years in satellite teleport, VSAT, broadcast or ground-segment "
     "operations.",
     "Working knowledge of RF chains, satellite modems, spectrum analysers and link "
     "budgets.",
     "Able to work a shift roster, including nights and weekends.",
     "Based in, or able to relocate to, Negeri Sembilan.",
     "Written and spoken English and Bahasa Malaysia."])]


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------
EL = [page_hero(
    'Home &nbsp;/&nbsp; Careers', "Careers", "Build the ground segment with us.",
    "SGS operates a carrier-neutral satellite teleport and data centre in Rantau, "
    "Negeri Sembilan. The people here keep antennas tracking, carriers clean and a "
    "Tier III-class data hall running for operators across the Asia-Pacific.")]

# --- career opportunities -------------------------------------------------
EL.append(section([split(
    half([eyebrow("Career opportunities"),
          h2("Work where the satellite meets the ground.", size=34),
          para("Satellite communications is a small industry built on a narrow set of "
               "skills, and those skills are learned on operating infrastructure rather "
               "than in a classroom. SGS runs its own antenna farm, RF chain, power plant "
               "and data hall, which means the engineers here work across all of it."),
          para("We look for people who want hands-on responsibility for infrastructure "
               "that other networks depend on &mdash; and who would rather understand a "
               "whole system than one layer of it."),
          ticks(["Training on live GEO and LEO gateway operations",
                 "Exposure across RF, IP, power and data centre disciplines",
                 "A regulated operator working to MCMC licence conditions"])]),
    figure(img("engineers-racks"),
           "Engineering on site &mdash; the SGS team at the equipment racks."))]))

# --- why join (dark) ------------------------------------------------------
EL.append(section([
    head_block("Why SGS", "A small team on serious infrastructure.", dark=True,
               center=True),
    grid([
        plain_card(None, "Real infrastructure",
                   "C-band, Ku-band and Ka-band antennas, a SPACESAIL LEO gateway and a "
                   "Tier III-class data hall &mdash; all on one secured site.",
                   dark=True, cols=4),
        plain_card(None, "Breadth, not narrowness",
                   "GEO and LEO, RF through to IP, teleport operations through to "
                   "colocation. Small teams see the whole path.", dark=True, cols=4),
        plain_card(None, "A regulated operator",
                   "MCMC individual licences as NFP and NSP, plus ASP(C) registration "
                   "&mdash; work held to standards that matter.", dark=True, cols=4),
        plain_card(None, "Regional reach",
                   "A strategic alliance partner of APT Satellite (APStar), supporting "
                   "operators across the Asia-Pacific.", dark=True, cols=4),
    ], g=28),
], dark=True))

# --- job openings ---------------------------------------------------------
EL.append(section([
    head_block("Job openings", "Current vacancies.",
               "Select a role to see the responsibilities and requirements in full. "
               "If nothing listed fits but you believe you would strengthen the team, "
               "write to us anyway.", center=True),
    C([W("accordion", {
        "tabs": OPENINGS,
        "selected_icon": ico("plus"), "selected_active_icon": ico("minus"),
        "title_color": INK, "tab_active_color": CYAN,
        "content_color": MUTED,
        "border_color": BORDER,
        "title_typography_typography": "custom",
        "title_typography_font_family": "Lexend",
        "title_typography_font_size": px(17.5),
        "title_typography_font_weight": "600",
    })], content_width="boxed", padding=box(0, 24, 0, 24),
       width=px(900), max_width=px(900)),
], anchor="openings"))

# --- how to apply (dark closer, in place of the gateway CTA) --------------
def detail(label, html, dark=True):
    return C([W("heading", {
                  "title": label, "header_size": "div", "title_color": CYAN,
                  "typography_typography": "custom", "typography_font_family": "Lexend",
                  "typography_font_size": px(11.5), "typography_font_weight": "700",
                  "typography_letter_spacing": px(1.4),
                  "typography_text_transform": "uppercase"}),
              para(html, dark=dark, size=15)],
             content_width="full", **colw(3), flex_gap=gap(0, 5))


EL.append(C([
    C([C([eyebrow("How to apply", dark=True),
          h2("Email us your resume.", dark=True, size=38),
          para("Send your CV with a short note about the role that interests you. "
               "Applications are read by the people you would be working with, and we "
               "reply to everyone we shortlist.", dark=True)],
         content_width="full", width=px(58, "%"), width_tablet=px(100, "%"),
         flex_gap=gap(0, 12)),
       C([btn("Email us your resume",
              "mailto:%s?subject=Job%%20application%%20%%E2%%80%%94%%20SGS" % TO,
              "primary"),
          btn("See open roles", "#openings", "ghost-light")],
         content_width="full", width=px(42, "%"), width_tablet=px(100, "%"),
         flex_direction="row", flex_wrap="wrap", flex_gap=gap(12), **BTN_STACK,
         flex_justify_content="flex-end", flex_justify_content_tablet="flex-start")],
      content_width="boxed", flex_direction="row", flex_align_items="center",
      flex_gap=gap(48), padding=box(0, 24, 0, 24), **STACK_TABLET),

    C([detail("Email", '<a href="mailto:%s" style="color:#FFFFFF;">%s</a>' % (TO, TO)),
       detail("HR Department",
              "Satcom Gateway Services Sdn Bhd<br>Lot 23126, Jalan Kuala Sawah,<br>"
              "Batu 10 Kampung Ribu,<br>71200 Rantau, Negeri Sembilan, Malaysia"),
       detail("Privacy",
              "Personal information collected through applications is used for "
              "recruitment purposes only.")],
      content_width="boxed", flex_direction="row", flex_wrap="wrap",
      flex_align_items="flex-start", flex_gap=gap(32),
      padding=box(44, 24, 0, 24), margin=box(36, 0, 0, 0),
      border_border="solid", border_width=box(1, 0, 0, 0), border_color="#FFFFFF24"),
],
    content_width="full",
    padding=box(84, 0, 84, 0), padding_mobile=box(56, 0, 56, 0),
    background_background="gradient", background_color="#340010",
    background_color_b=SPACE_D,
    background_gradient_angle={"unit": "deg", "size": 120}))

c, _ = wp.put_layout(PID, EL)
wp.set_page_template(PID, "elementor_header_footer")
print("careers page %d -> %s, %d sections | cache %s"
      % (PID, c, len(EL), wp.clear_cache()))
