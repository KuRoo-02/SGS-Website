"""Render the live WordPress site in headless Chromium and report problems.

    python verify.py                 # all known pages, desktop
    python verify.py news contact    # just those
    python verify.py --shots         # also write screenshots

Checks per page: HTTP status, console errors, broken images, horizontal
overflow, Elementor placeholder leakage, heading text.
"""
import sys, os, json
from playwright.sync_api import sync_playwright

BASE = "https://satcomgateway.com"
PAGES = {
    "home":     "/",
    "about":    "/about-us/",
    "services": "/our-services/",
    "news":     "/news-events/",
    "contact":  "/contact-us/",
}
WIDTHS = [(1440, "desktop"), (820, "tablet"), (390, "mobile")]
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "shots")

PROBE = """() => {
  const de = document.documentElement;
  const over = [...document.querySelectorAll('body *')].filter(el => {
    const r = el.getBoundingClientRect();
    return r.width > 0 && (r.right > de.clientWidth + 2 || r.left < -2);
  }).slice(0, 6).map(el => el.tagName.toLowerCase() + '.' + (el.className || '').toString().slice(0, 60));
  const imgs = [...document.images];
  return {
    docW: de.scrollWidth, viewW: de.clientWidth,
    overflow: over,
    broken: imgs.filter(i => i.complete && i.naturalWidth === 0).map(i => i.currentSrc || i.src),
    placeholder: imgs.filter(i => /placeholder\\.png/.test(i.src)).length,
    h1: [...document.querySelectorAll('h1')].map(h => h.textContent.trim()),
    posts: document.querySelectorAll('.elementor-widget-posts article').length,
    forms: document.querySelectorAll('form.elementor-form').length,
    nothingFound: /can't find what you're looking for/i.test(document.body.innerText),
  };
}"""


def run(names, shots, widths):
    bad = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name in names:
            # bare paths are accepted too; Git Bash mangles a leading slash
            # into a Windows path, so don't require one
            url = BASE + PAGES[name] if name in PAGES else \
                BASE + "/" + name.lstrip("/")
            for w, label in widths:
                pg = b.new_page(viewport={"width": w, "height": 1000})
                errs = []
                pg.on("console", lambda m: m.type == "error" and errs.append(m.text[:140]))
                pg.on("pageerror", lambda e: errs.append("JS: " + str(e)[:140]))
                r = pg.goto(url, wait_until="load", timeout=90000)
                pg.wait_for_timeout(1600)
                d = pg.evaluate(PROBE)
                flags = []
                if not r or r.status != 200:
                    flags.append("HTTP %s" % (r.status if r else "?"))
                if d["docW"] > d["viewW"] + 2:
                    flags.append("overflow %dpx" % (d["docW"] - d["viewW"]))
                if d["broken"]:
                    flags.append("%d broken img" % len(d["broken"]))
                if d["placeholder"]:
                    flags.append("%d placeholder" % d["placeholder"])
                if errs:
                    flags.append("%d console err" % len(errs))
                bad += len(flags)
                print("  %-9s %-8s %s" % (name, label, "OK" if not flags else " | ".join(flags)))
                if label == "desktop":
                    print("             h1=%s posts=%d forms=%d nothingFound=%s"
                          % (d["h1"][:1], d["posts"], d["forms"], d["nothingFound"]))
                    for o in d["overflow"]:
                        print("             over: %s" % o)
                    for e in errs[:3]:
                        print("             err: %s" % e)
                if shots:
                    os.makedirs(SHOTS, exist_ok=True)
                    pg.screenshot(path=os.path.join(SHOTS, "%s-%s.png" % (name, label)),
                                  full_page=True)
                pg.close()
        b.close()
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    shots = "--shots" in sys.argv
    widths = WIDTHS if "--responsive" in sys.argv else WIDTHS[:1]
    names = args or list(PAGES)
    n = run(names, shots, widths)
    print("\n%s" % ("clean" if not n else "%d flag(s)" % n))
