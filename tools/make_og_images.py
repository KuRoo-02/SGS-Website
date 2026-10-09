"""Generate 1200x630 social share cards and upload them to WordPress.

Link previews are cropped to roughly 1.91:1 by Facebook, LinkedIn and X. The
facility photos are 4:3, so handing them over raw means each network crops
them differently and usually badly. These are cropped once, deliberately,
with a maroon scrim and the logo so a shared link still looks like SGS.
"""
import sys, os, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image
from wpb import WP

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(os.path.dirname(HERE), "assets", "img")
TMP = os.path.join(os.environ.get("TEMP", "."), "sgs-og")
W, H = 1200, 630

# page slug -> (source photo, vertical crop bias 0=top 1=bottom)
CARDS = {
    "home":     ("antenna-array", 0.42),
    "about":    ("facility-2", 0.45),
    "services": ("antenna-3", 0.40),
    "news":     ("teleport-security", 0.45),
    "contact":  ("facility-1", 0.50),
}


def card(src, bias):
    im = Image.open(os.path.join(IMG, src + ".jpg")).convert("RGB")
    # cover-crop to 1200x630
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    x = (im.width - W) // 2
    y = int((im.height - H) * bias)
    im = im.crop((x, y, x + W, y + H))

    # maroon scrim, strongest bottom-left where the logo sits
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = scrim.load()
    for yy in range(H):
        for xx in range(0, W, 4):
            t = (1 - xx / W) * 0.55 + (yy / H) * 0.65
            a = int(min(1.0, t) * 190)
            for dx in range(4):
                if xx + dx < W:
                    px[xx + dx, yy] = (36, 0, 11, a)
    out = Image.alpha_composite(im.convert("RGBA"), scrim)

    logo = Image.open(os.path.join(IMG, "sgs-logo-light.png")).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    lw = 210
    logo = logo.resize((lw, max(1, round(logo.height * lw / logo.width))), Image.LANCZOS)
    out.alpha_composite(logo, (56, H - logo.height - 48))
    return out.convert("RGB")


def main():
    os.makedirs(TMP, exist_ok=True)
    wp = WP()
    media = wp.media_map()
    result = {}
    for slug, (src, bias) in CARDS.items():
        name = "sgs-og-%s" % slug
        path = os.path.join(TMP, name + ".jpg")
        card(src, bias).save(path, "JPEG", quality=86, optimize=True, progressive=True)
        size = os.path.getsize(path)

        if name in media:
            result[slug] = media[name]
            print("  %-9s reuse  id=%s" % (slug, media[name]["id"]))
            continue
        r = urllib.request.Request(wp.url + "/wp-json/wp/v2/media", method="POST",
            headers={"Authorization": wp.auth, "Content-Type": "image/jpeg",
                     "Content-Disposition": 'attachment; filename="%s.jpg"' % name,
                     "User-Agent": "sgs-build"})
        r.data = open(path, "rb").read()
        with urllib.request.urlopen(r, timeout=180, context=wp.ctx) as x:
            body = json.loads(x.read().decode())
        wp.call("/wp-json/wp/v2/media/%d" % body["id"], "POST",
                {"alt_text": "Satcom Gateway Services ground station, Rantau, Malaysia"})
        result[slug] = {"id": body["id"], "url": body["source_url"]}
        print("  %-9s upload id=%s  %.0f KB" % (slug, body["id"], size / 1024.0))
    return result


if __name__ == "__main__":
    for k, v in main().items():
        print("%-9s %s" % (k, v["url"]))
