"""WCAG AA contrast audit against the live site.

Flips a theme and you flip every contrast ratio with it, so this walks every
visible run of text, resolves what is actually painted behind it (climbing
ancestors until something opaque turns up, and compositing the translucent
layers on the way) and reports anything under the AA threshold: 4.5:1 for
body copy, 3:1 for large text.

Text over a photograph cannot be judged this way -- the backdrop is pixels,
not a colour -- so those are listed separately to look at by eye.
"""
import sys, os
from playwright.sync_api import sync_playwright

BASE = "https://satcomgateway.com"
PAGES = {"home": "/", "about": "/about-us/", "services": "/our-services/",
         "news": "/news-events/", "careers": "/careers/", "contact": "/contact-us/"}

PROBE = r"""() => {
  const parse = c => {
    const m = c.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map(x => parseFloat(x));
    return {r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1};
  };
  const over = (fg, bg) => ({            // composite fg (with alpha) onto bg
    r: fg.r * fg.a + bg.r * (1 - fg.a),
    g: fg.g * fg.a + bg.g * (1 - fg.a),
    b: fg.b * fg.a + bg.b * (1 - fg.a), a: 1});
  const lum = c => {
    const f = v => { v /= 255; return v <= .03928 ? v / 12.92
                                                  : Math.pow((v + .055) / 1.055, 2.4); };
    return .2126 * f(c.r) + .7152 * f(c.g) + .0722 * f(c.b);
  };
  const ratio = (a, b) => {
    const l1 = lum(a), l2 = lum(b);
    return (Math.max(l1, l2) + .05) / (Math.min(l1, l2) + .05);
  };

  const out = {fails: [], overPhoto: 0, checked: 0};
  const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  let n;
  while ((n = walk.nextNode())) {
    const t = n.textContent.trim();
    if (t.length < 3) continue;
    const el = n.parentElement;
    if (!el || seen.has(el)) continue;
    seen.add(el);
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity === 0) continue;
    const box = el.getBoundingClientRect();
    if (!box.width || !box.height) continue;

    const fg = parse(cs.color);
    if (!fg) continue;

    // resolve the painted backdrop, compositing translucent layers
    let layers = [], p = el, photo = false;
    while (p) {
      const s = getComputedStyle(p);
      if (s.backgroundImage && s.backgroundImage !== 'none') {
        if (/url\(/.test(s.backgroundImage)) { photo = true; break; }
      }
      const bg = parse(s.backgroundColor);
      if (bg && bg.a > 0) { layers.push(bg); if (bg.a === 1) break; }
      p = p.parentElement;
    }
    if (photo) { out.overPhoto++; continue; }
    if (!layers.length) continue;
    let base = layers.pop();
    while (layers.length) base = over(layers.pop(), base);

    const size = parseFloat(cs.fontSize);
    const bold = parseInt(cs.fontWeight, 10) >= 700;
    const large = size >= 24 || (size >= 18.66 && bold);
    const need = large ? 3 : 4.5;
    const got = ratio(over(fg, base), base);
    out.checked++;
    if (got < need - 0.01) {
      out.fails.push({
        txt: t.slice(0, 44), got: +got.toFixed(2), need,
        color: cs.color, size: Math.round(size),
        tag: el.tagName.toLowerCase(),
      });
    }
  }
  return out;
}"""


def run(names):
    bad = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name in names:
            pg = b.new_page(viewport={"width": 1440, "height": 1000})
            pg.add_init_script("try{sessionStorage.setItem('sgs-seen','1')}catch(e){}")
            pg.goto(BASE + PAGES[name], wait_until="load", timeout=90000)
            pg.wait_for_timeout(1800)
            d = pg.evaluate(PROBE)
            bad += len(d["fails"])
            print("\n  %-9s %d checked, %d over photos, %s"
                  % (name, d["checked"], d["overPhoto"],
                     "all pass" if not d["fails"] else "%d FAIL" % len(d["fails"])))
            seen = set()
            for f in d["fails"]:
                k = (f["color"], f["size"])
                if k in seen:
                    continue
                seen.add(k)
                print("      %5.2f:1 (need %.1f)  %-7s %2dpx %-18s %s"
                      % (f["got"], f["need"], f["tag"], f["size"], f["color"], f["txt"]))
            pg.close()
        b.close()
    return bad


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = run(args or list(PAGES))
    print("\n%s" % ("contrast clean" if not n else "%d failing run(s)" % n))
