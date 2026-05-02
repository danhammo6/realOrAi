#!/usr/bin/env python3
"""
Batch 2b: download the candidates that batch2 missed, using filenames
verified via Commons search API.
"""
import time
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request
import json

from img_utils import shrink_to_jpeg

HERE = Path(__file__).parent.resolve()
OUT = HERE.parent / "images" / "real"

# All titles below verified via the Commons search API.
CANDIDATES = [
    # Interiors
    ("File:NYC Public Library Research Room Jan 2006-1- 3.jpg", "nypl_reading_room",
     "Real photo — NYPL Rose Main Reading Room"),
    ("File:People studying in the Wolfson Reading Room of Manchester Central Library 03.jpg", "manchester_reading_room",
     "Real photo — Wolfson Reading Room, Manchester"),
    ("File:-2019-11-08 Inside Cafe Main, Church Street, Cromer.JPG", "cafe_cromer",
     "Real photo — Cafe Main interior, Cromer"),
    ("File:Modern dining area with stylish table and chairs in cozy interior design.jpg", "modern_dining",
     "Real photo — modern dining area interior"),

    # Hands
    ("File:Potter shaping clay on a traditional manual potter’s wheel in India 01.jpg", "potter_india",
     "Real photo — potter's hands at the wheel, India"),

    # Vintage
    ("File:Lange-MigrantMother02.jpg", "migrant_mother",
     "Real photo — 'Migrant Mother' (Dorothea Lange, 1936)"),
    ("File:Lewis Hine Power house mechanic working on steam pump.jpg", "powerhouse_mechanic",
     "Real photo — 'Powerhouse Mechanic' (Lewis Hine, 1920)"),
    ("File:Lewis Hine, Newsies smoking at Skeeter's Branch, St. Louis, 1910.jpg", "newsies_1910",
     "Real photo — newsboys St. Louis (Lewis Hine, 1910)"),
    ("File:We Can Do It!.jpg", "rosie_riveter",
     "Real poster — 'We Can Do It!' (1943)"),

    # Sculpture
    ("File:Le Penseur Musée Rodin Paris S.1295.jpg", "rodin_thinker",
     "Real photo — Rodin's 'The Thinker', Musée Rodin"),
    ("File:Chicago from under the Cloud Gate (9694666470).jpg", "cloud_gate",
     "Real photo — 'Cloud Gate' (Anish Kapoor), Chicago"),

    # Urbex
    ("File:Ferris wheel in Pripyat, Ukraine.jpg", "pripyat_ferris_wheel",
     "Real photo — abandoned Pripyat Ferris wheel"),
    ("File:Michigan Central Train Station Exterior 2010.jpg", "michigan_central",
     "Real photo — Michigan Central Station, 2010"),

    # Weather
    ("File:Foggy Muir Woods.jpg", "muir_fog",
     "Real photo — fog in Muir Woods"),

    # Reflections
    ("File:DFC 3503 A wet city street at night shopfronts and illuminated signs reflecting in puddles as cars and motorcycles pass by.jpg",
     "puddle_night", "Real photo — wet city street reflections at night"),

    # Kids
    ("File:Brighton Beach - children making a sandcastle(GN14525).jpg", "kids_sandcastle",
     "Real photo — kids making sandcastle, Brighton Beach"),
    ("File:A young child preparing to extinguish the candle of his first birthday - 1983-11-30.jpg", "kid_birthday_cake",
     "Real photo — child at first-birthday cake (1983)"),

    # Night
    ("File:Rainy night, rue de Turenne, Paris March 2020.jpg", "rainy_paris_night",
     "Real photo — rainy night on rue de Turenne, Paris"),

    # Markets
    ("File:Tsukiji Fish market and Tuna edit.jpg", "tsukiji_fish",
     "Real photo — Tsukiji fish market, Tokyo"),
    ("File:Flower Market @ Singel @ Amsterdam (16000748479).jpg", "amsterdam_flowers",
     "Real photo — Amsterdam Singel flower market"),

    # Wildlife
    ("File:Elephant dusting itself.jpg", "elephant_dusting",
     "Real photo — African elephant dusting itself"),

    # Macro
    ("File:Chanterelle in the forest.JPG", "chanterelle",
     "Real photo — chanterelle mushroom on forest floor"),

    # Art
    ("File:Book of Kells ChiRho Folio 34R.png", "kells_folio",
     "Real — Book of Kells, ChiRho folio (c. 800 AD)"),
    ("File:Kirchner Straßenszene 1280890.jpg", "kirchner_street",
     "Real — Kirchner, 'Straßenszene' (1913)"),
    ("File:Egrets from Quick Lessons in Simplified Drawing, Hokusai, 1823.jpg", "hokusai_egrets",
     "Real — Hokusai, egrets from 'Quick Lessons in Simplified Drawing' (1823)"),

    # Extras / variety
    ("File:Aurora borealis above Storfjorden and the Lyngen Alps in moonlight, 2012 March.jpg", "aurora_lyngen",
     "Real photo — aurora borealis, Lyngen Alps"),
    ("File:Marokko Wüste 01 (cropped).JPG", "morocco_dunes",
     "Real photo — Moroccan desert dunes"),
    ("File:Leon l gallet pocket watch movement 1879.jpg", "pocket_watch",
     "Real photo — Leon L Gallet pocket watch movement (1879)"),
    ("File:AnPing Street, Taipei (Shilin Night Market).jpg", "taipei_market",
     "Real photo — Shilin Night Market, Taipei"),
    ("File:Musician Mohamed Lamouri in Paris Metro line 2.jpg", "paris_musician",
     "Real photo — street musician in Paris metro"),
    ("File:Local Blacksmith forge blower2.jpg", "blacksmith_forge",
     "Real photo — local blacksmith forge"),
    ("File:Foggy mountain trail Montsoflo Switzerland.jpg", "foggy_trail_swiss",
     "Real photo — foggy mountain trail, Switzerland"),

    # Additional replacements for slugs used before that had guessed filenames
    ("File:The Thinker, Rodin.jpg", "rodin_thinker2",
     "Real photo — Rodin's 'The Thinker' (alternate angle)"),
    ("File:Guitarist plays the acoustic guitar.jpg", "guitarist_generic",
     "Real photo — guitarist hand on fretboard"),
]


def get_url(title):
    qs = urllib.parse.urlencode({
        "action": "query", "titles": title,
        "prop": "imageinfo", "iiprop": "url|size",
        "iiurlwidth": "1400",
        "format": "json",
    })
    req = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{qs}",
        headers={"User-Agent": "realOrAi-game/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    for p in d.get("query", {}).get("pages", {}).values():
        if "imageinfo" in p:
            ii = p["imageinfo"][0]
            return ii.get("thumburl") or ii.get("url")
    return None


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "realOrAi-game/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    misses = []
    for title, slug, caption in CANDIDATES:
        dest = OUT / f"{slug}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            print(f"  SKIP {dest.name}")
            continue

        for attempt in range(6):
            try:
                u = get_url(title)
                if not u:
                    print(f"  [NO-URL] {title}")
                    misses.append((title, slug))
                    break
                raw = download(u)
                jpg = shrink_to_jpeg(raw)
                dest.write_bytes(jpg)
                print(f"  OK {dest.name} ({len(raw)//1024}->{len(jpg)//1024} KB) | {caption}")
                time.sleep(2.5)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 8 * (attempt + 1)
                    print(f"  429 on {slug}, wait {wait}s")
                    time.sleep(wait)
                elif e.code == 404:
                    print(f"  [404] {title}")
                    misses.append((title, slug))
                    break
                else:
                    print(f"  [ERR] {title}: {e}")
                    break
            except Exception as e:
                print(f"  [ERR] {title}: {e}")
                break
        time.sleep(1)

    if misses:
        print(f"\n{len(misses)} still missing:")
        for t, s in misses:
            print(f"  - {s}  ({t})")


if __name__ == "__main__":
    main()
