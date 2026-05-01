# Real or AI?

A browser game: can you tell a real photo from an AI-generated image?

**Play it here:** https://danhammo6.github.io/realOrAi

## Layout

```
.                         ← GitHub Pages root (site is served from here)
├── index.html            ← game entry point
├── styles.css
├── game.js
├── images.js             ← image manifest (hand-edited + auto-managed block)
├── manifest.webmanifest
├── icons/                ← PWA / iOS home-screen icons
├── images/
│   ├── real/             ← real photos & artworks (Wikimedia Commons)
│   └── ai/               ← AI-generated images (legacy + Z-Image batch)
│
├── tools/                ← not served by Pages, ignored by browser
│   ├── generate.py       ← drives ComfyUI to produce AI images
│   ├── prompts.json      ← prompt library (slug, workflow, aspect, caption)
│   ├── seeds.json        ← last seed used per slug (monotonically increments)
│   ├── workflows/        ← ComfyUI API workflow JSONs (realism + art)
│   ├── download_commons.py ← helper to add more real photos from Commons
│   └── make_icons.py     ← regenerates the icon PNGs
│
└── notes/                ← design notes for future iterations
    ├── NOTES.md          ← tells we've spotted, difficulty-bucket idea
    ├── PROMPT_GUIDE.md   ← what works (and what doesn't) for Z-Image prompts
    └── CREDITS.md        ← image / code attribution
```

## Run locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy

GitHub Pages serves the repo root. Push to `main` and it's live — no build step.

## Add more real photos

Edit `tools/download_commons.py` (there's a `CANDIDATES` list at the top), then:

```bash
cd tools
uv venv .venv && source .venv/bin/activate
uv pip install --python .venv Pillow websocket-client
python download_commons.py
```

Then add corresponding entries to `images.js`.

## Generate more AI images

1. Add prompts to `tools/prompts.json`.
2. Make sure your ComfyUI server is reachable (defaults to `192.168.33.101:8188` — override with `--server`).
3. Run:

    ```bash
    cd tools
    source .venv/bin/activate
    python generate.py                      # all missing
    python generate.py --only ai_food_ramen # single prompt
    python generate.py --force              # regenerate
    ```

`generate.py` rewrites the `// === AI auto-generated ===` block in `images.js` to match what's on disk — your hand-edited entries outside that block are preserved.

See `notes/PROMPT_GUIDE.md` for what we've learned writing Z-Image prompts.

## Regenerate icons

```bash
cd tools
source .venv/bin/activate
python make_icons.py
```

Only needed if you change the icon design — the PNGs are committed.
