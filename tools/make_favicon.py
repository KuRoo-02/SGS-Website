"""Build a 512x512 site icon from the SGS logo and set it in WordPress.

WordPress crops the site icon square and renders it as small as 16px, so a
wide logo pasted straight in would be unreadable. This trims the logo to its
ink, scales it to fit a square with breathing room, and puts it on the brand
maroon so the mark still reads in a browser tab.
"""
import sys, os, io as _io, json, base64, mimetypes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from wpb import WP

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "assets", "img", "sgs-logo-light.png")
OUT = os.path.join(os.environ.get("TEMP", "."), "sgs-site-icon.png")
BG = (36, 0, 11, 255)          # MAROON_D, matches the header/footer
SIZE, PAD = 512, 58

im = Image.open(SRC).convert("RGBA")
im = im.crop(im.getbbox())      # trim transparent margin
box = SIZE - PAD * 2
scale = min(box / im.width, box / im.height)
im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
               Image.LANCZOS)

canvas = Image.new("RGBA", (SIZE, SIZE), BG)
canvas.alpha_composite(im, ((SIZE - im.width) // 2, (SIZE - im.height) // 2))
canvas.save(OUT, "PNG", optimize=True)
print("built %s (%dx%d, %d bytes)" % (OUT, SIZE, SIZE, os.path.getsize(OUT)))

wp = WP()
existing = wp.media_map().get("sgs-site-icon")
if existing:
    mid = existing["id"]
    print("reusing media %d" % mid)
else:
    import urllib.request, ssl
    data = open(OUT, "rb").read()
    r = urllib.request.Request(wp.url + "/wp-json/wp/v2/media", method="POST",
        headers={"Authorization": wp.auth, "Content-Type": "image/png",
                 "Content-Disposition": 'attachment; filename="sgs-site-icon.png"',
                 "User-Agent": "sgs-build"})
    r.data = data
    with urllib.request.urlopen(r, timeout=120, context=wp.ctx) as x:
        body = json.loads(x.read().decode())
    mid = body["id"]
    print("uploaded media %d -> %s" % (mid, body["source_url"]))
    wp.call("/wp-json/wp/v2/media/%d" % mid, "POST",
            {"alt_text": "Satcom Gateway Services", "title": "SGS site icon"})

c, s = wp.call("/wp-json/wp/v2/settings", "POST", {"site_icon": mid})
print("site_icon -> %s (now %s)" % (c, (s or {}).get("site_icon")))
