# SGS — Photo Shot List

Written for: whoever takes the replacement photos at the Rantau site.

The site currently uses the 18 photos supplied in `Materials/Facility Photos/`.
Four of them no longer reflect the facility, and one shot does not exist yet.
**These cannot be fixed by editing — the equipment in question was installed after
the existing photos were taken.** New photographs are required.

---

## What needs reshooting

### 1. Antenna view — platform 2  ·  REPLACE
Two antennas have since been added on platform 2 (one **Ku-band**, one **C-band**).
The current photos predate them.

| | |
|---|---|
| Replaces | `antenna-1.jpg`, `antenna-2.jpg` |
| Used on | Home hero section, About gallery, News post images |
| Shot | Wide view showing **platform 2 with all antennas**, so the new Ku-band and C-band dishes are clearly part of the group |
| Orientation | **Landscape**, 4:3 |
| Note | `antenna-2.jpg` is the featured image on the lead news article, so it wants to be the strongest of the set |

### 2. Telco room  ·  REPLACE
Two additional racks have been installed.

| | |
|---|---|
| Replaces | `telco-room.jpg` |
| Used on | Services §03, About gallery, News post image |
| Shot | Down the aisle so the **full rack line including the two new racks** is visible |
| Orientation | **Landscape**, 4:3 |

### 3. Server room  ·  REPLACE
Two Navalista racks have been added.

| | |
|---|---|
| Replaces | `server-room-1.jpg` |
| Used on | Home, Services §05, About gallery |
| Shot | Aisle view including the **two new Navalista racks** |
| Orientation | **Landscape**, 4:3 |

### 4. Rooftop — SPACESAIL antenna  ·  NEW
No rooftop photo exists in the supplied materials.

| | |
|---|---|
| New file | `rooftop-spacesail.jpg` |
| Would be used on | About gallery, and the SPACESAIL/LEO card on Services §02 |
| Shot | The **SPACESAIL antenna on the roof**, ideally with sky behind it. A second wider frame showing it in context with the rooftop would also be useful |
| Orientation | **Landscape**, 4:3 |
| Why it matters | LEO/SPACESAIL is a headline capability across the site and currently has **no photograph at all** — every LEO mention uses a GEO dish instead |

---

## Shooting notes

Matching the existing set keeps the site visually consistent:

- **Landscape, 4:3** for everything except where noted. The site crops to 4:3 and 16:10;
  portrait shots get cropped hard and lose their subject.
- **Minimum 2000px on the long edge.** Originals were 1500–1950px; the site serves
  1400px wide. More resolution is fine, less is not.
- **Overcast or golden hour** for exteriors. The existing hero was shot near sunset and
  it is the strongest image on the site — worth repeating.
- **Lights on, doors open** for interiors. The current interior shots are evenly lit and
  that is why they work.
- **Keep the camera level.** Converging verticals are obvious on a web page.
- Shoot **two or three frames per subject** at slightly different angles so there is a
  choice at layout time.
- **No people in frame** unless SGS wants that, which changes consent and privacy handling.

---

## How to drop them in

Replacements are a file swap — no code changes needed, provided the filenames match.

1. Save the new images over the existing ones in `Website/assets/img/`:
   `antenna-1.jpg` · `antenna-2.jpg` · `telco-room.jpg` · `server-room-1.jpg`
2. Resize to 1400px on the long edge, JPEG quality ~80 (matches the current set;
   the originals were ~900KB, the optimised versions ~150–260KB)
3. For the new rooftop photo, send it over and it gets added to the About gallery
   and the SPACESAIL card — that one does need a small markup change
4. Redeploy: `powershell -ExecutionPolicy Bypass -File .\deploy.ps1`

The deploy script cache-busts CSS and JS, but **not images** — they keep their
filenames. After swapping photos, hard-refresh (Ctrl+F5) or purge the Cloudflare
cache, or the old images will keep serving from the edge for up to 30 days.

---

## Also unused

`facility-4.jpg` and `switchboard-2.jpg` are optimised and in the repo but not placed
on any page. They are available if any of the above needs a stand-in.
