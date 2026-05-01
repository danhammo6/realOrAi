#!/usr/bin/env python3
"""
Download real-photo images from Wikimedia Commons into ../images/real/.

Edit the CANDIDATES list below (file title on Commons + local slug + caption),
then run. The script uses the Commons API with User-Agent and rate-limit
backoff, and skips files it's already downloaded.

Commons categories that have yielded good variety:
  Category:Featured_pictures_of_animals
  Category:Featured_pictures_of_landscapes
  Category:Featured_pictures_of_food
  Category:Featured_pictures_of_people
  Category:Featured_pictures_of_architecture
  Category:Quality_images_of_birds
  Category:Quality_images_of_insects
  Category:Quality_images_of_astronomy

To find more candidates, use the API directly:
  https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers \
    &cmtitle=Category:<name>&cmlimit=50&cmtype=file&format=json

For classical art, these category names work:
  Category:Paintings_by_<artist>
  Category:Featured_pictures_of_paintings

All images fetched this way are under free licenses (public domain / CC).

Usage:
    source .venv/bin/activate   # if not already
    python download_commons.py
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent.resolve()
OUT = HERE.parent / "images" / "real"

# (Commons filename, local slug, caption) — edit to taste
CANDIDATES = [
    # ("File:Cute Hedgehog.jpg", "hedgehog", "Real photo — hedgehog"),
]


def get_url(title):
    qs = urllib.parse.urlencode({
        "action": "query", "titles": title,
        "prop": "imageinfo", "iiprop": "url|size",
        "iiurlwidth": "1024",
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


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "realOrAi-game/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


def ext_from_url(url):
    m = re.search(r"\.([a-zA-Z0-9]+)(?:/|$|\?)", url.split("/")[-1])
    return ("." + m.group(1).lower()) if m else ".jpg"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not CANDIDATES:
        print("Edit CANDIDATES at the top of this file, then re-run.")
        return

    for title, slug, caption in CANDIDATES:
        # Skip if already present under any common extension
        existing = next(
            (OUT / f"{slug}{e}" for e in (".jpg", ".jpeg", ".png", ".webp")
             if (OUT / f"{slug}{e}").exists() and (OUT / f"{slug}{e}").stat().st_size > 5000),
            None,
        )
        if existing:
            print(f"  SKIP {existing.name}")
            continue

        for attempt in range(6):
            try:
                u = get_url(title)
                if not u:
                    print(f"  [NO-URL] {title}")
                    break
                ext = ext_from_url(u)
                if ext not in (".jpg", ".jpeg", ".png", ".webp"):
                    ext = ".jpg"
                dest = OUT / f"{slug}{ext}"
                size = download(u, dest)
                print(f"  OK {dest.name} ({size//1024} KB)  |  {caption}")
                time.sleep(2.5)
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = 8 * (attempt + 1)
                    print(f"  429 on {slug}, wait {wait}s")
                    time.sleep(wait)
                else:
                    print(f"  [ERR] {title}: {e}")
                    break
            except Exception as e:
                print(f"  [ERR] {title}: {e}")
                break
        time.sleep(1)


if __name__ == "__main__":
    main()
