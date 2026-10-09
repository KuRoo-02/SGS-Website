"""
Shared helpers for building the SGS site in Elementor over the REST API.

Elementor 4.x registers its document meta with show_in_rest, so layouts,
kit settings and Theme Builder conditions can all be written directly.
The one catch is that Elementor caches generated CSS per post and a REST
meta write does NOT invalidate it — so every write is followed by
DELETE /elementor/v1/cache, which is what makes this loop work at all.

    from wpb import WP, eid, px, box
    wp = WP()
    wp.put_layout(page_id, [container, ...])
    wp.clear_cache()
"""
import base64, io, json, os, re, ssl, sys, uuid
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
ENV = os.path.join(os.path.dirname(SITE), ".env.deploy")


def eid():
    """Elementor element ids are 7 hex chars."""
    return uuid.uuid4().hex[:7]


def px(n, unit="px"):
    return {"unit": unit, "size": n, "sizes": []}


def box(t, r, b, l, unit="px", linked=False):
    return {"unit": unit, "top": str(t), "right": str(r), "bottom": str(b),
            "left": str(l), "isLinked": linked}


def gap(col, row=None):
    row = col if row is None else row
    return {"unit": "px", "size": col, "column": str(col), "row": str(row)}


# Global colour slugs defined by the kit, referenced as globals so a later
# palette change propagates instead of leaving hard-coded hex behind.
def gcolor(slug):
    return "globals/colors?id=%s" % slug


def gtypo(slug):
    return "globals/typography?id=%s" % slug


class WP:
    def __init__(self):
        env = {}
        if not os.path.exists(ENV):
            sys.exit("Missing %s" % ENV)
        for line in io.open(ENV, encoding="utf-8"):
            m = re.match(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$', line)
            if m:
                env[m.group(1)] = m.group(2).strip('"')
        for k in ("WP_URL", "WP_USER", "WP_APP_PASSWORD"):
            if not env.get(k):
                sys.exit("Missing %s in .env.deploy" % k)
        self.url = env["WP_URL"].rstrip("/")
        self.auth = "Basic " + base64.b64encode(
            ("%s:%s" % (env["WP_USER"], env["WP_APP_PASSWORD"])).encode()).decode()
        self.ctx = ssl.create_default_context()

    def call(self, path, method="GET", data=None, timeout=90):
        r = urllib.request.Request(self.url + path, method=method,
            headers={"User-Agent": "sgs-build", "Authorization": self.auth,
                     "Accept": "application/json"})
        if data is not None:
            r.add_header("Content-Type", "application/json")
            r.data = json.dumps(data).encode()
        try:
            with urllib.request.urlopen(r, timeout=timeout, context=self.ctx) as x:
                t = x.read().decode()
                return x.status, (json.loads(t) if t.strip() else None)
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode())
            except Exception:
                return e.code, None
        except Exception as e:
            return None, str(e)

    # -- cache -------------------------------------------------------------
    def clear_cache(self):
        """Without this, a REST write shows stale CSS. Always call after writing."""
        c, _ = self.call("/wp-json/elementor/v1/cache", "DELETE")
        return c == 200

    # -- lookups -----------------------------------------------------------
    def media_map(self):
        out, page = {}, 1
        while True:
            c, batch = self.call("/wp-json/wp/v2/media?per_page=100&page=%d" % page)
            if c != 200 or not batch:
                break
            for m in batch:
                out[m["slug"]] = {"id": m["id"], "url": m["source_url"]}
            if len(batch) < 100:
                break
            page += 1
        return out

    def page_map(self):
        c, items = self.call("/wp-json/wp/v2/pages?per_page=100&status=any")
        return {p["slug"]: p["id"] for p in (items or [])}

    def menu_id(self, name="Primary"):
        c, menus = self.call("/wp-json/wp/v2/menus?per_page=50")
        for m in (menus or []):
            if m.get("name") == name or m.get("slug") == name.lower():
                return m["id"]
        return None

    def kit_id(self):
        c, items = self.call(
            "/wp-json/wp/v2/elementor_library?per_page=100&status=any&context=edit")
        for i in (items or []):
            if (i.get("meta") or {}).get("_elementor_template_type") == "kit":
                return i["id"]
        return None

    # -- writing -----------------------------------------------------------
    def put_layout(self, post_id, elements, post_type="pages"):
        """Write Elementor layout JSON onto an existing post/page."""
        return self.call("/wp-json/wp/v2/%s/%d" % (post_type, post_id), "POST", {
            "meta": {
                "_elementor_data": json.dumps(elements),
                "_elementor_edit_mode": "builder",
            }})

    def upsert_template(self, title, slug, tmpl_type, elements, conditions=None):
        """Create or update a Theme Builder template (header/footer/single/...).

        conditions use Elementor's own syntax, e.g. ["include/general"].
        """
        c, found = self.call(
            "/wp-json/wp/v2/elementor_library?slug=%s&status=any&context=edit" % slug)
        payload = {
            "title": title, "slug": slug, "status": "publish",
            "meta": {
                "_elementor_data": json.dumps(elements),
                "_elementor_edit_mode": "builder",
                "_elementor_template_type": tmpl_type,
            }}
        if conditions is not None:
            payload["meta"]["_elementor_conditions"] = conditions
        if found:
            tid = found[0]["id"]
            c, b = self.call("/wp-json/wp/v2/elementor_library/%d" % tid, "POST", payload)
            return c, tid, "updated"
        c, b = self.call("/wp-json/wp/v2/elementor_library", "POST", payload)
        return c, (b or {}).get("id"), "created"

    def set_conditions(self, template_id, conditions=("general",)):
        """Activate a Theme Builder template.

        Writing _elementor_conditions meta alone is NOT enough: Elementor keeps
        a separate conditions index, and the template stays isActive=false. It
        must go through Elementor's own route, and that route rejects the
        string shorthand ("include/general" -> HTTP 500). It wants the parsed
        object form.
        """
        norm = []
        for cnd in conditions:
            if isinstance(cnd, dict):
                base = {"type": "include", "name": "general", "sub_name": "", "sub_id": ""}
                base.update(cnd)
                norm.append(base)
            else:
                norm.append({"type": "include", "name": cnd,
                             "sub_name": "", "sub_id": ""})
        payload = {"conditions": norm}
        return self.call(
            "/wp-json/elementor/v1/site-editor/templates-conditions/%d" % template_id,
            "POST", payload)

    def template_state(self):
        """What Elementor itself thinks is registered and active."""
        c, d = self.call("/wp-json/elementor/v1/site-editor/templates")
        return {t["id"]: {"type": t["type"], "title": t["title"],
                          "active": t["isActive"], "conditions": t["conditions"]}
                for t in (d or [])}

    def set_page_template(self, post_id, template="elementor_canvas"):
        """elementor_canvas = no theme header/footer; elementor_header_footer =
        full width with them."""
        return self.call("/wp-json/wp/v2/pages/%d" % post_id, "POST",
                          {"template": template})
