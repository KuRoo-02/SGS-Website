"""Build the SGS Contact Us page, including the live Elementor Pro form.

The form delivers to info@satcomgs.com and sets Reply-To from the submitted
email address, so SGS can answer straight out of the notification. Submissions
are also kept in Elementor > Submissions as a fallback if mail ever bounces.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP, eid, px, box, gap
from sgs import *

wp = WP(); M = wp.media_map(); P = wp.page_map()
PID = P["contact-us"]
def img(s): m = M.get(s, {}); return {"id": m.get("id"), "url": m.get("url")}

TO    = "info@satcomgs.com"
PHONE = "+60 6-694 4990"
TEL   = "tel:+6066944990"

EL = [page_hero(
    'Home &nbsp;/&nbsp; Contact Us', "Get in touch", "Let's talk about your network.",
    "Whether you need gateway hosting, satellite capacity, backhaul or colocation, tell us "
    "what you are trying to connect and our team will come back with a scoped response.")]


# ===========================================================================
# Enquiry form + contact details
# ===========================================================================
def field(fid, label, ftype="text", width="100", required=False, **extra):
    f = {"_id": eid(), "custom_id": fid, "field_type": ftype,
         "field_label": label, "width": width}
    if required:
        f["required"] = "true"
    f.update(extra)
    return f


TOPICS = "\n".join([
    # Elementor's select ignores `placeholder`. An empty first choice is written
    # with its "label|value" syntax -- a blank value is what makes `required`
    # actually bite, instead of the first real topic counting as an answer.
    "Please select…|",
    "Teleport & gateway hosting",
    "Satellite capacity leasing",
    "Satellite broadband / enterprise network",
    "Satellite backhaul",
    "Satellite mobility (maritime / aero)",
    "Data centre & colocation",
    "Technical & ground-segment services",
    "Site visit request",
    "General enquiry",
])

FORM = W("form", {
    "form_name": "SGS Enquiry",
    "form_fields": [
        field("name", "Full name", width="50", required=True,
              placeholder="Your name"),
        field("company", "Company / organisation", width="50",
              placeholder="Company name"),
        field("email", "Work email", "email", width="50", required=True,
              placeholder="you@company.com"),
        field("phone", "Phone", "tel", width="50",
              placeholder="Including country code"),
        field("topic", "What can we help with?", "select", required=True,
              field_options=TOPICS),
        field("message", "Tell us about your requirement", "textarea", required=True,
              rows=6,
              placeholder="The more technical detail you can share, the more precise our "
                          "response will be."),
        field("consent", "", "acceptance", required=True,
              acceptance_text="I consent to SGS storing and processing the details above in "
                              "order to respond to this enquiry."),
    ],

    # --- delivery ---
    "submit_actions": ["email"],
    "email_to": TO,
    "email_subject": "Website enquiry — satcomgateway.com",
    "email_content": "[all-fields]",
    "email_from": "wordpress@satcomgateway.com",
    "email_from_name": "SGS Website",
    "email_reply_to": '[field id="email"]',
    "email_content_type": "html",

    # --- messages ---
    "success_message": "Thank you — your enquiry has reached the SGS team. "
                       "We aim to respond within one business day.",
    "error_message": "Something went wrong. Please email %s directly." % TO,
    "required_field_message": "This field is required.",

    # --- layout + styling ---
    "button_text": "Send enquiry",
    "button_size": "md",
    "button_background_color": CTA,
    "button_text_color": "#FFFFFF",
    "button_background_color_hover": CTA_H,
    "button_border_radius": box(8, 8, 8, 8),
    "button_text_padding": box(16, 30, 16, 30),
    "button_typography_typography": "custom",
    "button_typography_font_family": "Lexend",
    "button_typography_font_size": px(15),
    "button_typography_font_weight": "600",

    "mark_required": "yes",
    "label_spacing": px(7),
    "label_color": TEXT,
    "label_typography_typography": "custom",
    "label_typography_font_family": "Lexend",
    "label_typography_font_size": px(13.5),
    "label_typography_font_weight": "600",

    "field_text_color": TEXT,
    "field_background_color": "#FFFFFF",
    "field_border_color": "#C9D1D9",
    "field_border_width": box(1, 1, 1, 1, linked=True),
    "field_border_radius": box(8, 8, 8, 8),
    "field_typography_typography": "custom",
    "field_typography_font_size": px(15),
    "row_gap": px(18),
    "column_gap": px(18),
})


def detail(label, html):
    return C([W("heading", {
                  "title": label, "header_size": "div", "title_color": SUBTLE,
                  "typography_typography": "custom", "typography_font_family": "Lexend",
                  "typography_font_size": px(11.5), "typography_font_weight": "700",
                  "typography_letter_spacing": px(1.4),
                  "typography_text_transform": "uppercase"}),
              para(html, size=15.5, color=TEXT)],
             content_width="full", width=px(100, "%"), flex_gap=gap(0, 4))


EL.append(section([
    C([
        # --- form ---
        half([eyebrow("Send us an enquiry"),
              h2("Tell us what you need to connect.", size=30),
              para("Fields marked <strong>*</strong> are required. We aim to respond within "
                   "one business day.", size=15.5),
              FORM],
             width=px(58, "%"), width_tablet=px(100, "%"), flex_gap=gap(0, 16)),

        # --- details ---
        half([C([eyebrow("Contact details"),
                 h3("Prefer to reach us directly?", size=20),
                 detail("Office &amp; ground station",
                        "Satcom Gateway Services Sdn Bhd<br>Lot 23126, Jalan Kuala Sawah,<br>"
                        "Batu 10 Kampung Ribu,<br>71200 Rantau, Negeri Sembilan,<br>Malaysia"),
                 detail("Email", '<a href="mailto:%s">%s</a>' % (TO, TO)),
                 detail("Telephone", '<a href="%s">%s</a>' % (TEL, PHONE)),
                 detail("Business hours",
                        "Monday &ndash; Friday, 09:00 &ndash; 17:00 (MYT)<br>"
                        "Teleport operations monitored 24 / 7"),
                 C([btn("Click to call", TEL, "primary"),
                    btn("Email us", "mailto:%s" % TO, "ghost")],
                   content_width="full", width=px(100, "%"), flex_direction="row",
                   flex_wrap="wrap", flex_gap=gap(12))],
                content_width="full", width=px(100, "%"), flex_gap=gap(0, 16),
                background_background="classic", background_color=TINT,
                border_border="solid", border_width=box(1, 1, 1, 1, linked=True),
                border_color=BORDER, border_radius=box(14, 14, 14, 14),
                padding=box(32, 30, 32, 30))],
             width=px(42, "%"), width_tablet=px(100, "%"))],
      content_width="boxed", flex_direction="row", flex_align_items="flex-start",
      flex_gap=gap(48), padding=box(0, 24, 0, 24)),
]))


# ===========================================================================
# Finding us
# ===========================================================================
FACTS = [("Site reference", "SGS Ground Station (KL2)"),
         ("Coordinates", "2.609896&deg; N, 101.957879&deg; E"),
         ("Distance from KLIA", "68&nbsp;km &middot; approx. 53 minutes"),
         ("Distance from KL metro", "80&nbsp;km &middot; approx. 73 minutes"),
         ("Fibre providers on site", "Telekom Malaysia, Fiberail")]

TABLE = ('<table style="width:100%;border-collapse:collapse;font-size:15px;">'
         "<tbody>" + "".join(
    '<tr%s><th style="text-align:left;padding:13px 16px;color:#545C66;font-weight:600;'
    'font-size:13px;letter-spacing:.03em;text-transform:uppercase;border-bottom:1px solid '
    '#E1E6EB;width:46%%;">%s</th><td style="padding:13px 16px;color:#15191E;'
    'border-bottom:1px solid #E1E6EB;">%s</td></tr>'
    % (' style="background:#F7F9FB;"' if i % 2 else "", k, v)
    for i, (k, v) in enumerate(FACTS)) + "</tbody></table>")

EL.append(section([split(
    half([eyebrow("Finding us"),
          h2("Ground station KL2, Rantau.", size=32),
          para("The station sits in the southern part of the Kuala Lumpur region &mdash; "
               "68&nbsp;km and roughly 53 minutes' drive from Kuala Lumpur International "
               "Airport, and 80&nbsp;km (about 73 minutes) from the metropolitan area."),
          W("html", {"html": TABLE}),
          para("Site visits are by appointment. Please contact us in advance so we can "
               "arrange access and an engineering escort.", size=14.5, color=SUBTLE)],
         flex_gap=gap(0, 14)),
    half([W("google_maps", {
              "address": "2.609896,101.957879",
              "zoom": {"unit": "px", "size": 13, "sizes": []},
              "height": {"unit": "px", "size": 460, "sizes": []},
              "border_radius": box(14, 14, 14, 14)}),
          para("SGS Ground Station (KL2) &mdash; Rantau, Negeri Sembilan, Malaysia.",
               size=14, color=SUBTLE)],
         flex_gap=gap(0, 10)),
    align="flex-start")], tint=True))


# ===========================================================================
# Routing your enquiry
# ===========================================================================
EL.append(section([
    head_block("Routing your enquiry", "Not sure who to ask for?", dark=True, center=True),
    grid([
        plain_card(None, "Gateway &amp; capacity",
                   "Hosting an antenna, leasing GEO or LEO capacity, or planning a hybrid "
                   "architecture.", dark=True, cols=3),
        plain_card(None, "Colocation &amp; interconnection",
                   "Rack space, power, cross-connects and carrier hand-off at the Rantau "
                   "data hall.", dark=True, cols=3),
        plain_card(None, "Technical &amp; site services",
                   "Installation, commissioning, maintenance, remote hands and site visit "
                   "requests.", dark=True, cols=3),
    ]),
], dark=True))

EL.append(cta_band())

c, _ = wp.put_layout(PID, EL)
wp.set_page_template(PID, "elementor_header_footer")
print("contact page %d -> %s, %d sections | cache %s"
      % (PID, c, len(EL), wp.clear_cache()))
