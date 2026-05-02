#!/usr/bin/env python3
"""
Batch 2: download 50 more real photos from Wikimedia Commons, covering the
same new categories as prompts_batch2.json so the AI and real pools mirror
each other (no category-level tell).

Run from tools/ with the venv active:
    python download_batch2.py
"""
import time
from pathlib import Path

from img_utils import shrink_to_jpeg
import urllib.error
import urllib.parse
import urllib.request
import json

HERE = Path(__file__).parent.resolve()
OUT = HERE.parent / "images" / "real"

# (title, slug, caption) — all under free Commons licenses
CANDIDATES = [
    # --- Interior scenes ---
    ("File:Gustavsbergs porslinsmuseum - modernt koksinterior 01.jpg", "kitchen_modern", "Real photo — modern kitchen interior"),
    ("File:Chetham's Library Reading Room 1.jpg", "chethams_library", "Real photo — Chetham's Library Reading Room, Manchester"),
    ("File:Caffe Florian interior.jpg", "cafe_florian", "Real photo — Caffè Florian interior, Venice"),
    ("File:Alt-Berliner Zimmer in einer Mietskaserne um 1900 (Heimatmuseum Hellersdorf).jpg", "berlin_room_1900", "Real photo — recreated 1900s Berlin tenement room"),

    # --- Hands / people doing things ---
    ("File:Kneading bread dough.jpg", "baker_hands_dough", "Real photo — hands kneading bread dough"),
    ("File:Potter at work - potter's wheel Kayseri 02.jpg", "potter_kayseri", "Real photo — potter's hands at the wheel, Kayseri"),
    ("File:Classical guitar left hand.jpg", "guitar_left_hand", "Real photo — classical guitarist's fretting hand"),

    # --- Vintage / historical photography ---
    ("File:Migrant Mother by Dorothea Lange restored.jpg", "migrant_mother", "Real photo — 'Migrant Mother' (Dorothea Lange, 1936)"),
    ("File:Powerhouse Mechanic by Lewis Hine, 1920 - restoration.jpg", "powerhouse_mechanic", "Real photo — 'Powerhouse Mechanic' (Lewis Hine, 1920)"),
    ("File:Newsies at Skeeter's Branch, Jefferson near Franklin. They were all smoking. St. Louis, Missouri.jpg", "newsies_1910", "Real photo — newsboys St. Louis (Lewis Hine, 1910)"),
    ("File:Flappers.jpg", "flappers_1920s", "Real photo — flappers in the 1920s"),
    ("File:Rosie the Riveter (Vultee) edit1.jpg", "rosie_riveter", "Real photo — WWII-era factory worker"),

    # --- Sculpture ---
    ("File:David von Michelangelo.jpg", "david_michelangelo", "Real photo — Michelangelo's David"),
    ("File:'The Thinker', Auguste Rodin.jpg", "rodin_thinker", "Real photo — Rodin's 'The Thinker'"),
    ("File:Cloud Gate 3 (ST).jpg", "cloud_gate", "Real photo — 'Cloud Gate' (Anish Kapoor), Chicago"),
    ("File:Great Buddha of Kamakura.jpg", "buddha_kamakura", "Real photo — Great Buddha of Kamakura"),

    # --- Abandoned / urbex ---
    ("File:Chernobyl Pripyat amusement park.jpg", "pripyat_park", "Real photo — Pripyat abandoned amusement park"),
    ("File:Abandoned Hospital.jpg", "abandoned_hospital", "Real photo — abandoned hospital"),
    ("File:Detroit Michigan Central Station 2009.jpg", "michigan_central", "Real photo — abandoned Michigan Central Station"),

    # --- Weather / dramatic skies ---
    ("File:Lightning over Oradea Romania 3.jpg", "lightning_oradea", "Real photo — lightning over Oradea, Romania"),
    ("File:Muir Woods National Monument - Fog.jpg", "muir_fog", "Real photo — fog in Muir Woods"),
    ("File:Storm on Tyrrhenian Sea.jpg", "storm_tyrrhenian", "Real photo — storm on Tyrrhenian Sea"),
    ("File:Nor'easter blizzard Times Square.jpg", "nor_easter_ny", "Real photo — nor'easter blizzard in New York"),

    # --- Reflections ---
    ("File:Puddle reflection rainy night.jpg", "puddle_night", "Real photo — puddle reflecting neon at night"),
    ("File:Taj Mahal reflection on Yamuna river, Agra.jpg", "taj_reflection", "Real photo — Taj Mahal reflected in Yamuna river"),
    ("File:Lake Bled.jpg", "lake_bled", "Real photo — Lake Bled reflection"),

    # --- Kids candid ---
    ("File:Children building a sandcastle at Saltburn-by-the-Sea (6187604170).jpg", "kids_sandcastle", "Real photo — kids building a sandcastle"),
    ("File:Boy playing football.jpg", "boy_football", "Real photo — boy playing football"),
    ("File:Kid blowing candles on birthday cake.jpg", "kid_birthday_cake", "Real photo — kid blowing out birthday candles"),

    # --- Night ---
    ("File:Rainy night street in Lyon.jpg", "lyon_rainy_night", "Real photo — rainy night street in Lyon"),
    ("File:Campfire 4213.jpg", "campfire", "Real photo — campfire at night"),

    # --- Markets ---
    ("File:Tsukiji fish market japan.jpg", "tsukiji_fish", "Real photo — Tsukiji fish market, Tokyo"),
    ("File:Amsterdamflowermarket1.jpg", "amsterdam_flowers", "Real photo — Amsterdam flower market"),

    # --- Environmental portraits ---
    ("File:Old man portrait Japan woodcarver.jpg", "woodcarver_japan", "Real photo — Japanese woodcarver portrait"),
    ("File:Nurse portrait.jpg", "nurse_portrait", "Real photo — nurse environmental portrait"),

    # --- More wildlife ---
    ("File:Octopus2.jpg", "octopus_reef", "Real photo — reef octopus"),
    ("File:African Elephant in Serengeti National Park.jpg", "elephant_savannah", "Real photo — African elephant in Serengeti"),

    # --- Macro ---
    ("File:Cantharellus cibarius bavaria.jpg", "chanterelle_mushroom", "Real photo — chanterelle mushrooms"),

    # --- Art ---
    ("File:Hokusai Crane.jpg", "hokusai_crane", "Real — Hokusai crane sketch (Japanese ink)"),
    ("File:Book of Kells, Folio 292r, Incipit to John.jpg", "kells_folio", "Real — Book of Kells illuminated manuscript"),
    ("File:Ernst Ludwig Kirchner - Die Strasse.jpg", "kirchner_street", "Real — Kirchner expressionist painting"),
    ("File:Picasso - Girl with a Mandolin, 1910.jpg", "picasso_mandolin", "Real — Picasso cubist painting (1910)"),

    # --- Extra variety to pad out ---
    ("File:Venetian lace work.jpg", "venetian_lace", "Real photo — Venetian lacework macro"),
    ("File:Aurora borealis near Svolvær.jpg", "aurora_svolvaer", "Real photo — aurora borealis, Svolvær"),
    ("File:Desert dunes Sahara.jpg", "sahara_dunes", "Real photo — Sahara desert dunes"),
    ("File:Old pocket watch mechanism macro.jpg", "pocket_watch", "Real photo — pocket watch mechanism macro"),
    ("File:Night market Taipei.jpg", "taipei_market", "Real photo — Taipei night market"),
    ("File:Street musician Paris metro.jpg", "paris_musician", "Real photo — street musician in Paris metro"),
    ("File:Blacksmith at work forge.jpg", "blacksmith_forge", "Real photo — blacksmith at the forge"),
    ("File:Foggy mountain trail hiker.jpg", "foggy_hiker", "Real photo — hiker on foggy mountain trail"),
]


def get_url(title):
    qs = urllib.parse.urlencode({
        "action": "query", "titles": title,
        "prop": "imageinfo", "iiprop": "url|size",
        "iiurlwidth": "1400",  # request slightly larger so shrink_to_jpeg picks the sharpest downscale
        "format": "json",
    })
    req = urllib.request.Request(
        f"https://commons.wikimedia.org/w/api.php?{qs}",
        headers={"User-Agent": "realOrAi-game/1.0 (personal project)"},
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
        print(f"\n{len(misses)} candidates failed to resolve. Will need to pick alternates for:")
        for t, s in misses:
            print(f"  - {s}  ({t})")


if __name__ == "__main__":
    main()
