"""Audit the live site for tablet/phone problems that an overflow check misses.

    python audit_responsive.py            # all pages, tablet + phone
    python audit_responsive.py contact    # one page

The thing overflow alone will not catch: an Elementor container defaults to
flex-wrap:nowrap, so a two-column row whose children are set to width:100%
on mobile does not stack -- the children just shrink to share the row. The
page stays inside the viewport and looks fine to a width check while reading
as two 160px columns on a phone. SQUEEZED is that case.
"""
import sys, os, json
from playwright.sync_api import sync_playwright

BASE = "https://satcomgateway.com"
PAGES = {"home": "/", "about": "/about-us/", "services": "/our-services/",
         "news": "/news-events/", "contact": "/contact-us/"}
WIDTHS = [(820, "tablet", 300), (390, "phone", 240)]

PROBE = r"""(minChild) => {
  const vw = document.documentElement.clientWidth;
  const vis = el => {
    const s = getComputedStyle(el);
    if (s.display === 'none' || s.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const tag = el => {
    const c = (typeof el.className === 'string' ? el.className : '').trim()
      .split(/\s+/).filter(x => /^(elementor-widget-|sgs-|e-con)/.test(x)).slice(0, 2).join('.');
    return el.tagName.toLowerCase() + (c ? '.' + c : '') +
      (el.dataset.id ? '#' + el.dataset.id : '');
  };
  const out = {vw, squeezed: [], taps: [], tiny: [], wide: [], upscaled: [], nowrap: []};

  // Column layouts that should have stacked but only shrank. Two traps here:
  // a BOXED container puts the flex row on its .e-con-inner child rather than
  // on itself, and align-items:center gives siblings different tops while
  // still sitting side by side -- so judge by x, not by y. Restricted to rows
  // whose children are containers, since an icon-plus-text row is also a
  // narrow flex row and is meant to stay side by side.
  document.querySelectorAll('.e-con, .e-con-inner').forEach(el => {
    if (!vis(el)) return;
    // footer link columns are meant to be narrow; the main-content threshold
    // does not apply to them
    if (el.closest('[data-elementor-type="footer"]')) return;
    const s = getComputedStyle(el);
    if (s.display !== 'flex' || !s.flexDirection.startsWith('row')) return;
    const kids = [...el.children].filter(vis);
    if (kids.length < 2 || !kids.every(k => k.classList.contains('e-con'))) return;
    const boxes = kids.map(k => k.getBoundingClientRect());
    const lefts = boxes.map(b => Math.round(b.left));
    if (Math.max(...lefts) - Math.min(...lefts) < 20) return;   // stacked
    const w = boxes.map(b => Math.round(b.width));
    if (Math.min(...w) < minChild)
      out.squeezed.push((el.dataset.id || (el.parentElement || {}).dataset?.id || '?') +
        ' wrap=' + s.flexWrap + ' kids=[' + w.join(',') + '] "' +
        el.innerText.trim().split('\n')[0].slice(0, 32) + '"');
  });

  // interactive things too small to hit
  document.querySelectorAll('a,button,select,input,textarea,.elementor-menu-toggle')
    .forEach(el => {
      if (!vis(el)) return;
      if (getComputedStyle(el).display === 'inline') return;
      // the theme's skip link is deliberately 1px until focused, and a
      // checkbox's real target is its <label for>, not the box itself
      if (el.classList.contains('skip-link')) return;
      if (el.type === 'checkbox' && el.id &&
          document.querySelector('label[for="' + el.id + '"]')) return;
      const r = el.getBoundingClientRect();
      if (r.height < 40)
        out.taps.push(tag(el) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height) +
                      ' "' + el.textContent.trim().slice(0, 22) + '"');
    });

  // body copy below 14px
  document.querySelectorAll('p,li,td,th,span,div,a').forEach(el => {
    if (!vis(el)) return;
    const txt = [...el.childNodes].filter(n => n.nodeType === 3)
      .map(n => n.textContent.trim()).join('');
    if (txt.length < 12) return;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < 14) out.tiny.push(tag(el) + ' ' + fs + 'px "' + txt.slice(0, 26) + '"');
  });

  // anything physically wider than the viewport
  document.querySelectorAll('table,img,iframe,pre,.elementor-widget-html').forEach(el => {
    if (!vis(el)) return;
    const r = el.getBoundingClientRect();
    if (r.width > vw + 1) out.wide.push(tag(el) + ' w=' + Math.round(r.width));
  });

  // scroll containers that silently clip
  document.querySelectorAll('*').forEach(el => {
    if (!vis(el)) return;
    if (el.scrollWidth > el.clientWidth + 2 && el.clientWidth > 0) {
      const s = getComputedStyle(el);
      if (s.overflowX === 'hidden' || s.overflowX === 'clip')
        out.nowrap.push(tag(el) + ' clips ' + (el.scrollWidth - el.clientWidth) + 'px');
    }
  });

  // images rendered much larger than their source
  [...document.images].forEach(i => {
    if (!vis(i) || !i.naturalWidth) return;
    const r = i.getBoundingClientRect();
    if (r.width > i.naturalWidth * 1.5 && r.width > 120)
      out.upscaled.push(i.src.split('/').pop() + ' ' + i.naturalWidth +
                        ' -> ' + Math.round(r.width));
  });
  return out;
}"""


def uniq(xs, n):
    seen, out = set(), []
    for x in xs:
        k = x.split(" ")[0]
        if k in seen:
            continue
        seen.add(k)
        out.append(x)
        if len(out) >= n:
            break
    return out


def run(names):
    total = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for name in names:
            path = PAGES.get(name, "/" + name.lstrip("/"))
            for w, label, minchild in WIDTHS:
                pg = b.new_page(viewport={"width": w, "height": 900},
                                device_scale_factor=2, is_mobile=(w < 600),
                                has_touch=(w < 600))
                pg.goto(BASE + path, wait_until="load", timeout=90000)
                pg.wait_for_timeout(1800)
                d = pg.evaluate(PROBE, minchild)
                n = sum(len(d[k]) for k in ("squeezed", "taps", "tiny", "wide", "nowrap", "upscaled"))
                total += n
                print("\n  %-9s %-7s  %s" % (name, label, "clean" if not n else "%d issue(s)" % n))
                for k, cap in (("squeezed", 6), ("wide", 4), ("nowrap", 4),
                               ("tiny", 4), ("taps", 6), ("upscaled", 3)):
                    for x in uniq(d[k], cap):
                        print("      %-9s %s" % (k.upper(), x))
                    if len(d[k]) > cap:
                        print("      %-9s ... and %d more" % (k.upper(), len(d[k]) - cap))
                pg.close()
        b.close()
    return total


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = run(args or list(PAGES))
    print("\n%s" % ("clean" if not n else "%d issue(s) total" % n))
