"""Port the draft's orbital preloader into WordPress.

Two Custom Code snippets, because order of injection matters:

  head        the CSS, so the overlay is already styled when the markup
              arrives. Put the CSS with the markup at body_start instead and
              the page flashes unstyled for a frame.
  body_start  the markup, which must land before any page content paints.

The sequence itself is the draft's, unchanged: orbits draw in, satellites
start tracking, signal waves answer, the status line advances, the link
locks. Pure CSS and SVG -- the only JS is the dismiss timer.

Two differences from the draft, both deliberate:
  - It shows once per session. A 5s hold on every page view would be
    punishing; sessionStorage means it greets a visitor and then stays out
    of the way.
  - It never runs inside the Elementor editor, which would otherwise make
    the page unopenable for five seconds on every edit.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wpb import WP

wp = WP()
M = wp.media_map()
LOGO = M["sgs-logo-light"]["url"]

CYAN, GREEN, EASE = "#00B0EC", "#7EBF41", "cubic-bezier(.22,.61,.36,1)"
DURATION = "5s"          # change this one value; everything rescales

CSS = """
<style id="sgs-preloader-css">
.sgs-pl{
  --pl-dur:%(dur)s;
  position:fixed;inset:0;z-index:99999;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:30px;
  background:
    radial-gradient(900px 600px at 50%% 42%%, rgba(0,176,236,.10), transparent 62%%),
    radial-gradient(700px 500px at 78%% 78%%, rgba(126,191,65,.07), transparent 60%%),
    linear-gradient(160deg,#0D1124 0%%,#05070E 100%%);
  /* fires even if the JS never runs; sits past the JS ceiling so the script
     normally wins. This is the net, not the mechanism. */
  animation:sgs-pl-out .55s %(ease)s 6.6s forwards;
}
.sgs-pl.is-done{animation:sgs-pl-out .55s %(ease)s forwards;}
@keyframes sgs-pl-out{to{opacity:0;visibility:hidden;pointer-events:none;}}

.sgs-pl__stage{position:relative;width:min(320px,76vw);aspect-ratio:1;display:grid;place-items:center;}
.sgs-pl__sys{position:absolute;inset:0;width:100%%;height:100%%;overflow:visible;}

/* the whole system drifts, so nothing looks locked to the grid */
.sgs-pl__rot{transform-origin:160px 160px;animation:sgs-pl-drift 38s linear infinite;}
@keyframes sgs-pl-drift{to{transform:rotate(360deg);}}

.sgs-pl__orbit{transform-origin:160px 160px;transform:rotate(var(--tilt));}
.sgs-pl__path,.sgs-pl__sat{fill:none;vector-effect:non-scaling-stroke;}

/* pathLength="100" normalises every ellipse, so dash values are percentages
   and the same timings hold whatever the radii */
.sgs-pl__path{
  stroke:rgba(120,200,255,.22);stroke-width:1;
  stroke-dasharray:100 100;stroke-dashoffset:100;
  animation:sgs-pl-draw 1.1s %(ease)s forwards;
  animation-delay:calc(.25s + var(--i) * .18s);
}
@keyframes sgs-pl-draw{to{stroke-dashoffset:0;}}

/* a short bright dash travelling the ring reads as a satellite on track;
   riding the path itself means no transform maths to get wrong */
.sgs-pl__sat{
  stroke:%(cyan)s;stroke-width:2.4;stroke-linecap:round;
  stroke-dasharray:7 93;stroke-dashoffset:100;opacity:0;
  filter:drop-shadow(0 0 6px rgba(0,176,236,.95));
  animation:sgs-pl-track calc(2.6s + var(--i) * .7s) linear infinite,
            sgs-pl-fade .6s ease forwards;
  animation-delay:calc(1s + var(--i) * .22s),calc(1s + var(--i) * .22s);
}
@keyframes sgs-pl-track{to{stroke-dashoffset:0;}}
@keyframes sgs-pl-fade{to{opacity:1;}}

.sgs-pl__wave{
  fill:none;stroke:%(cyan)s;stroke-width:1.3;transform-origin:160px 160px;opacity:0;
  animation:sgs-pl-wave 2.6s %(ease)s infinite;animation-delay:.9s;
}
@keyframes sgs-pl-wave{
  0%%{transform:scale(.4);opacity:0;}
  12%%{opacity:.85;}
  100%%{transform:scale(3.5);opacity:0;}
}

.sgs-pl__logo{
  position:relative;z-index:2;width:108px;height:auto;opacity:0;transform:scale(.86);
  animation:sgs-pl-logo-in .9s %(ease)s .1s forwards,
            sgs-pl-breathe 3.2s ease-in-out 1s infinite;
}
@keyframes sgs-pl-logo-in{to{opacity:1;transform:scale(1);}}
@keyframes sgs-pl-breathe{
  0%%,100%%{filter:drop-shadow(0 0 0 rgba(0,176,236,0));}
  50%%{filter:drop-shadow(0 0 16px rgba(0,176,236,.55));}
}

.sgs-pl__text{
  position:relative;height:1.2em;min-width:230px;text-align:center;
  font-family:Lexend,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  font-size:.6875rem;font-weight:600;letter-spacing:.22em;text-transform:uppercase;
  color:rgba(255,255,255,.62);
}
.sgs-pl__text span{position:absolute;inset:0;opacity:0;animation-duration:var(--pl-dur);
  animation-timing-function:linear;animation-fill-mode:forwards;}
.sgs-pl__text span:nth-child(1){animation-name:sgs-pl-s1;}
.sgs-pl__text span:nth-child(2){animation-name:sgs-pl-s2;}
.sgs-pl__text span:nth-child(3){animation-name:sgs-pl-s3;color:%(green)s;}
@keyframes sgs-pl-s1{0%%,2%%{opacity:0;}8%%,30%%{opacity:1;}36%%,100%%{opacity:0;}}
@keyframes sgs-pl-s2{0%%,36%%{opacity:0;}42%%,64%%{opacity:1;}70%%,100%%{opacity:0;}}
@keyframes sgs-pl-s3{0%%,70%%{opacity:0;}76%%,100%%{opacity:1;}}

/* lock flash, timed to land with "Link established" */
.sgs-pl__stage::after{
  content:"";position:absolute;inset:0;border-radius:50%%;
  border:1px solid %(green)s;opacity:0;transform:scale(.75);
  animation:sgs-pl-lock .9s %(ease)s forwards;
  animation-delay:calc(var(--pl-dur) * .76);
}
@keyframes sgs-pl-lock{
  0%%{opacity:0;transform:scale(.75);}
  35%%{opacity:.85;}
  100%%{opacity:0;transform:scale(1.12);}
}

.sgs-pl__bar{width:230px;height:2px;background:rgba(255,255,255,.13);border-radius:2px;overflow:hidden;}
.sgs-pl__bar::after{
  content:"";display:block;width:100%%;height:100%%;border-radius:2px;
  background:linear-gradient(90deg,#00769F,%(cyan)s);
  box-shadow:0 0 8px rgba(0,176,236,.55);
  transform-origin:left center;transform:scaleX(0);
  /* linear: a timed bar should finish exactly when the wait does, rather
     than race to 95%% and then look stuck */
  animation:sgs-pl-fill var(--pl-dur) linear forwards;
}
@keyframes sgs-pl-fill{from{transform:scaleX(0);}to{transform:scaleX(1);}}

/* nothing animates, nothing blocks */
@media (prefers-reduced-motion:reduce){.sgs-pl{display:none !important;}}
</style>
""" % dict(dur=DURATION, ease=EASE, cyan=CYAN, green=GREEN)


MARKUP = """
<div class="sgs-pl" id="sgs-pl" role="presentation" aria-hidden="true">
  <div class="sgs-pl__stage">
    <svg class="sgs-pl__sys" viewBox="0 0 320 320" aria-hidden="true">
      <g class="sgs-pl__rot">
        <g class="sgs-pl__orbit" style="--tilt:-24deg;--i:0">
          <ellipse class="sgs-pl__path" cx="160" cy="160" rx="132" ry="46" pathLength="100"/>
          <ellipse class="sgs-pl__sat"  cx="160" cy="160" rx="132" ry="46" pathLength="100"/>
        </g>
        <g class="sgs-pl__orbit" style="--tilt:38deg;--i:1">
          <ellipse class="sgs-pl__path" cx="160" cy="160" rx="116" ry="58" pathLength="100"/>
          <ellipse class="sgs-pl__sat"  cx="160" cy="160" rx="116" ry="58" pathLength="100"/>
        </g>
        <g class="sgs-pl__orbit" style="--tilt:84deg;--i:2">
          <ellipse class="sgs-pl__path" cx="160" cy="160" rx="140" ry="36" pathLength="100"/>
          <ellipse class="sgs-pl__sat"  cx="160" cy="160" rx="140" ry="36" pathLength="100"/>
        </g>
      </g>
      <circle class="sgs-pl__wave" cx="160" cy="160" r="30"/>
      <circle class="sgs-pl__wave" cx="160" cy="160" r="30" style="animation-delay:2.2s"/>
    </svg>
    <img class="sgs-pl__logo" src="%(logo)s" alt="" width="693" height="418" fetchpriority="high">
  </div>
  <div class="sgs-pl__text">
    <span>Acquiring signal</span>
    <span>Establishing uplink</span>
    <span>Link established</span>
  </div>
  <div class="sgs-pl__bar"></div>
</div>
<script>
(function(){
  var el = document.getElementById('sgs-pl');
  if (!el) return;
  var kill = function(){ if (el.parentNode) el.parentNode.removeChild(el); };

  // Never inside the Elementor editor: a 5s overlay on every edit would make
  // the page feel broken to whoever is maintaining it.
  if (window.top !== window.self || /elementor-preview=/.test(location.search)
      || document.body.classList.contains('elementor-editor-active')) { kill(); return; }

  var reduce = window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var seen = false;
  try { seen = sessionStorage.getItem('sgs-seen') === '1'; } catch (e) {}
  if (seen || reduce) { kill(); return; }

  // Duration is read back off the CSS so it lives in exactly one place.
  var MIN = 5000;
  try {
    var raw = getComputedStyle(el).getPropertyValue('--pl-dur').trim();
    var n = parseFloat(raw);
    if (!isNaN(n) && n > 0) MIN = raw.indexOf('ms') > -1 ? n : n * 1000;
  } catch (e) {}
  var MAX = MIN + 1200;             // hard ceiling, whatever the network does
  var start = Date.now(), gone = false;

  function dismiss(){
    if (gone) return;
    gone = true;
    try { sessionStorage.setItem('sgs-seen', '1'); } catch (e) {}
    el.classList.add('is-done');
    setTimeout(kill, 600);
  }
  function ready(){ setTimeout(dismiss, Math.max(0, MIN - (Date.now() - start))); }

  if (document.readyState === 'complete') ready();
  else window.addEventListener('load', ready);
  setTimeout(dismiss, MAX);
})();
</script>
""" % dict(logo=LOGO)


def upsert(slug, title, code, location, priority):
    payload = {"title": title, "slug": slug, "status": "publish",
               "meta": {"_elementor_code": code,
                        "_elementor_location": location,
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
                    "POST", {"conditions": [{"type": "include", "name": "general",
                                             "sub_name": "", "sub_id": ""}]})
    print("  %-22s %s id=%-4s %s  conditions=%s" % (slug, action, sid, c, cc))


upsert("sgs-preloader-css", "SGS preloader - styles", CSS, "elementor_head", 2)
upsert("sgs-preloader", "SGS preloader", MARKUP, "elementor_body_start", 2)
print("cache cleared:", wp.clear_cache())
