"""On-page SEO, structured data and analytics for the SGS site.

Everything here is delivered through Elementor Pro's Custom Code snippets
(post type elementor_snippet), which inject raw HTML into <head> and accept
the same display conditions as Theme Builder templates. That is what makes
per-page meta possible without a plugin: one snippet per page, scoped to it.

Why not an SEO plugin: Rank Math installs fine over REST but stays dormant
until its setup wizard is run in wp-admin, and it registers neither a REST
namespace nor REST-exposed post meta, so none of it can be configured or
populated from here. A half-configured SEO plugin on a live client site is
worse than none, so it was removed. If SGS later want to edit titles and
descriptions themselves, run the Rank Math wizard and these snippets come
out -- they are deliberately easy to find and delete under Elementor >
Custom Code.

Analytics is wired but inert until the IDs exist: add GA4_ID and/or
GSC_VERIFICATION to .env.deploy and re-run. Nothing is emitted otherwise,
because a placeholder measurement ID silently reports to nobody.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP

SITE = "https://satcomgateway.com"
NAME = "Satcom Gateway Services"
LEGAL = "Satcom Gateway Services Sdn Bhd"
TAGLINE = "Satellite teleport and data centre, Malaysia"
EMAIL = "info@satcomgs.com"
PHONE = "+60 6-694 4990"

wp = WP()
M = wp.media_map()
P = wp.page_map()


def og(slug):
    m = M.get("sgs-og-" + slug)
    return m["url"] if m else M["sgs-og-home"]["url"]


# --------------------------------------------------------------------------
# Page copy. Descriptions are written to stand on their own in a result
# listing: what SGS is, where it is, and what can be bought.
# --------------------------------------------------------------------------
PAGES = [
    dict(slug="home", path="/", page="home",
         ogtitle="Carrier-neutral satellite teleport in Malaysia",
         desc="Carrier-neutral satellite teleport and Tier III data centre in Rantau, "
              "Malaysia. GEO and LEO gateway hosting, capacity leasing, backhaul and "
              "colocation.",
         crumbs=[]),
    dict(slug="about", path="/about-us/", page="about-us",
         ogtitle="About SGS - licensed satellite ground infrastructure",
         desc="MCMC-licensed satellite teleport and data centre in Rantau, Negeri "
              "Sembilan, and a strategic alliance partner of APT Satellite (APStar).",
         crumbs=[("About Us", "/about-us/")]),
    dict(slug="services", path="/our-services/", page="our-services",
         ogtitle="Teleport, gateway hosting, capacity and colocation",
         desc="Gateway hosting, satellite capacity leasing across APStar and SPACESAIL, "
              "broadband, backhaul, mobility and data centre colocation from Malaysia.",
         crumbs=[("Our Services", "/our-services/")]),
    dict(slug="news", path="/news-events/", page="news-events",
         ogtitle="SGS news and events",
         desc="Announcements, technical updates and events from Satcom Gateway Services, "
              "Malaysia's carrier-neutral satellite teleport and data centre operator.",
         crumbs=[("News & Events", "/news-events/")]),
    dict(slug="contact", path="/contact-us/", page="contact-us",
         ogtitle="Contact Satcom Gateway Services",
         desc="Contact SGS about gateway hosting, satellite capacity, backhaul or "
              "colocation at the Rantau ground station. %s, %s." % (EMAIL, PHONE),
         crumbs=[("Contact Us", "/contact-us/")]),
]


LIMITS = {"desc": 158, "ogtitle": 70}
for _p in PAGES:
    for _k, _max in LIMITS.items():
        if len(_p[_k]) > _max:
            raise SystemExit("%s %s is %d chars, limit %d: %s"
                             % (_p["slug"], _k, len(_p[_k]), _max, _p[_k]))


def esc(s):
    return (s.replace("&", "&amp;").replace('"', "&quot;")
             .replace("<", "&lt;").replace(">", "&gt;"))


def ld(obj):
    return ('<script type="application/ld+json">%s</script>'
            % json.dumps(obj, ensure_ascii=False, separators=(",", ":")))


# --------------------------------------------------------------------------
# Snippet plumbing
# --------------------------------------------------------------------------
def upsert(slug, title, code, conditions, priority=10):
    """Create or update a Custom Code snippet and scope it.

    _elementor_location only accepts elementor_head / elementor_body_start /
    elementor_body_end, and conditions go through Elementor's own route --
    writing _elementor_conditions meta leaves the snippet unscoped.
    """
    payload = {"title": title, "slug": slug, "status": "publish",
               "meta": {"_elementor_code": code,
                        "_elementor_location": "elementor_head",
                        "_elementor_priority": priority}}
    c, found = wp.call("/wp-json/wp/v2/elementor_snippet?slug=%s&status=any" % slug)
    if found:
        sid = found[0]["id"]
        c, _ = wp.call("/wp-json/wp/v2/elementor_snippet/%d" % sid, "POST", payload)
        action = "updated"
    else:
        c, b = wp.call("/wp-json/wp/v2/elementor_snippet", "POST", payload)
        sid, action = (b or {}).get("id"), "created"
    cc, _ = wp.call("/wp-json/elementor/v1/site-editor/templates-conditions/%d" % sid,
                    "POST", {"conditions": conditions})
    print("  %-26s %s id=%-4s %s  conditions=%s" % (slug, action, sid, c, cc))
    return sid


def drop(slug):
    c, found = wp.call("/wp-json/wp/v2/elementor_snippet?slug=%s&status=any" % slug)
    for f in (found or []):
        wp.call("/wp-json/wp/v2/elementor_snippet/%d?force=true" % f["id"], "DELETE")
        print("  %-26s removed id=%s" % (slug, f["id"]))


# --------------------------------------------------------------------------
# 1. Site identity
# --------------------------------------------------------------------------
c, st = wp.call("/wp-json/wp/v2/settings", "POST",
                {"title": NAME, "description": TAGLINE})
print("settings -> %s | %s - %s" % (c, NAME, TAGLINE))

# --------------------------------------------------------------------------
# 2. Site-wide: organisation identity and the bits every page shares
# --------------------------------------------------------------------------
ORG = {
    "@context": "https://schema.org",
    "@graph": [
        {"@type": "Organization",
         "@id": SITE + "/#organization",
         "name": LEGAL,
         "legalName": LEGAL,
         "alternateName": "SGS",
         "url": SITE + "/",
         "logo": {"@type": "ImageObject", "@id": SITE + "/#logo",
                  "url": M["sgs-logo"]["url"], "caption": LEGAL},
         "image": {"@id": SITE + "/#logo"},
         "description": "Carrier-neutral satellite teleport, gateway hosting and data "
                        "centre operator in Rantau, Negeri Sembilan, Malaysia.",
         "email": EMAIL,
         "telephone": PHONE,
         "address": {"@type": "PostalAddress",
                     "streetAddress": "Lot 23126, Jalan Kuala Sawah, Batu 10 Kampung Ribu",
                     "addressLocality": "Rantau",
                     "addressRegion": "Negeri Sembilan",
                     "postalCode": "71200",
                     "addressCountry": "MY"},
         "location": {"@type": "Place",
                      "name": "SGS Ground Station (KL2)",
                      "geo": {"@type": "GeoCoordinates",
                              "latitude": 2.609896, "longitude": 101.957879}},
         "areaServed": {"@type": "Place", "name": "Asia-Pacific"},
         "contactPoint": [{"@type": "ContactPoint", "contactType": "sales",
                           "email": EMAIL, "telephone": PHONE,
                           "availableLanguage": ["en", "ms"]}]},
        {"@type": "WebSite",
         "@id": SITE + "/#website",
         "url": SITE + "/",
         "name": NAME,
         "description": TAGLINE,
         "publisher": {"@id": SITE + "/#organization"},
         "inLanguage": "en-MY"},
    ],
}

site_head = "\n".join([
    "<!-- SGS: site-wide head. Managed in Elementor > Custom Code. -->",
    '<meta name="theme-color" content="#24000B">',
    '<meta property="og:site_name" content="%s">' % esc(LEGAL),
    '<meta property="og:locale" content="en_MY">',
    '<meta name="twitter:card" content="summary_large_image">',
    ld(ORG),
])
print("\nsite-wide:")
upsert("sgs-seo-site", "SGS SEO - site wide", site_head,
       [{"type": "include", "name": "general", "sub_name": "", "sub_id": ""}], priority=5)

# --------------------------------------------------------------------------
# 3. Per page: description, social card, breadcrumb trail
# --------------------------------------------------------------------------
print("\nper page:")
for p in PAGES:
    url = SITE + p["path"]
    tags = [
        "<!-- SGS: %s. Managed in Elementor > Custom Code. -->" % p["slug"],
        '<meta name="description" content="%s">' % esc(p["desc"]),
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="%s">' % esc(p["ogtitle"]),
        '<meta property="og:description" content="%s">' % esc(p["desc"]),
        '<meta property="og:url" content="%s">' % url,
        '<meta property="og:image" content="%s">' % og(p["slug"]),
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:title" content="%s">' % esc(p["ogtitle"]),
        '<meta name="twitter:description" content="%s">' % esc(p["desc"]),
        '<meta name="twitter:image" content="%s">' % og(p["slug"]),
    ]
    if p["crumbs"]:
        items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"}]
        for i, (label, href) in enumerate(p["crumbs"], start=2):
            items.append({"@type": "ListItem", "position": i, "name": label,
                          "item": SITE + href})
        tags.append(ld({"@context": "https://schema.org",
                        "@type": "BreadcrumbList", "itemListElement": items}))
    upsert("sgs-seo-" + p["slug"], "SGS SEO - %s" % p["slug"], "\n".join(tags),
           [{"type": "include", "name": "singular", "sub_name": "page",
             "sub_id": P[p["page"]]}])

# Articles: no per-post copy exists to inject, but they should still share as
# an article with a branded image rather than as a bare link. Scrapers fall
# back to <title>, which WordPress already sets per post.
upsert("sgs-seo-post", "SGS SEO - articles", "\n".join([
    "<!-- SGS: article defaults. Managed in Elementor > Custom Code. -->",
    '<meta property="og:type" content="article">',
    '<meta property="og:image" content="%s">' % og("news"),
    '<meta property="og:image:width" content="1200">',
    '<meta property="og:image:height" content="630">',
    '<meta name="twitter:image" content="%s">' % og("news"),
]), [{"type": "include", "name": "singular", "sub_name": "post", "sub_id": ""}])

# --------------------------------------------------------------------------
# 4. Analytics -- only if the IDs are actually configured
# --------------------------------------------------------------------------
print("\nanalytics:")
ga = wp.env.get("GA4_ID", "").strip()
gsc = wp.env.get("GSC_VERIFICATION", "").strip()

if ga or gsc:
    bits = ["<!-- SGS: analytics. Managed in Elementor > Custom Code. -->"]
    if gsc:
        bits.append('<meta name="google-site-verification" content="%s">' % esc(gsc))
    if ga:
        bits += [
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>' % ga,
            "<script>window.dataLayer=window.dataLayer||[];"
            "function gtag(){dataLayer.push(arguments);}gtag('js',new Date());"
            "gtag('config','%s');</script>" % ga,
        ]
    upsert("sgs-analytics", "SGS analytics", "\n".join(bits),
           [{"type": "include", "name": "general", "sub_name": "", "sub_id": ""}],
           priority=1)
    print("    GA4=%s  GSC=%s" % (ga or "-", "set" if gsc else "-"))
else:
    drop("sgs-analytics")
    print("    skipped: add GA4_ID and/or GSC_VERIFICATION to .env.deploy and re-run")

print("\ncache cleared:", wp.clear_cache())
