# Real or AI? — Project Notes

Working notes for future iterations. Update as you learn more.

## Current state (as of end-of-session May 2026)

**Game**: Live at https://danhammo6.github.io/realOrAi — single-page static site, playable in browser and installable as a PWA on iOS/iPadOS via Safari → "Add to Home Screen".

**Image library**: 198 total, all normalized to max-dim 1280 px, JPEG quality 85, progressive.
- **102 AI images**:
  - 86 generated locally via ComfyUI + Z-Image (Aitrepreneur's v2 workflow variants in `tools/workflows/`)
  - 16 legacy images sourced from Wikimedia Commons AI-generated categories (kept for stylistic variety — DALL-E, Copilot, FLUX, Firefly, Recraft, etc.)
- **96 real images** from Wikimedia Commons, covering:
  - Nature (landscapes, wildlife, birds, insects, macro, astronomy)
  - Food, architecture, vehicles, sports, people/candid, street, markets
  - Classical art (Van Gogh, Monet, Klimt, Vermeer, Bosch, Botticelli, Bruegel, Leonardo, Hokusai, Kirchner)
  - Vintage historical photography (Lange, Hine, Kodachrome family, "Migrant Mother", "Powerhouse Mechanic")
  - Interiors, hands-at-work, sculpture, urbex, weather, reflections

**Game mechanics**
- 12 rounds per session, balanced 6 AI / 6 real via `pickUnseen()` filters in `game.js`
- Seen-image tracking in localStorage (`realOrAi.seen.v1`) — cycles cleanly per-pool when exhausted
- "Reset progress" link on start screen
- Score + feedback caption after each guess; final-screen message by percentage

## Working agreement for this project

Things we've consistently done and that should continue:
- **Parity**: every change on the AI side should have a matching change on the real side (category mix, dimensions, file format, filesize). Asymmetry is a tell.
- **Prompts live in `tools/prompts.json`**, one source of truth. `generate.py` reads it, rewrites the manifest block in `images.js` to match what's on disk.
- **Tools output is reproducible**: seeds persist per-slug in `tools/seeds.json` and monotonically increment on regen; the workflow JSONs are committed; the prompts are committed.
- **Manifest hygiene**: never hand-edit the `// === AI auto-generated ===` block. Everything else in `images.js` is hand-edited. The downloader doesn't auto-sync the manifest — it needs an append step (see "Known loose ends").
- **Image normalization**: anything new goes through `img_utils.shrink_to_jpeg()`. Both `generate.py` and `download_commons.py` already do this.

## Where to pick up next session

### Suggested order of work

1. **Play several rounds and capture tells.** We currently have ~86 new Z-Image images that haven't been battle-tested. Write the slug + the tell into the "Prompt refinements" table below as you find them.
2. **Refine the worst-offender prompts** (re-run with `python generate.py --force --only <slug>`).
3. **Implement difficulty selector** if the game is still feeling too uniform.
4. **Try Ernie or Klein** for model-diversity (see "Models to try next" section).

### Known loose ends
- `download_commons.py` and `download_batch2.py` don't auto-sync `images.js`. After a download run, the real entries need to be manually appended (see the ad-hoc inline Python we used at end-of-session for the pattern — it's straightforward).
- `seeds.json` has entries only for the current prompt slugs; any new slug just gets a fresh random seed on first run.
- `notes/` contains `NOTES.md` (this), `PROMPT_GUIDE.md`, and `CREDITS.md`. Keep `CREDITS.md` updated if you add more attribution-required images.
- The 4.5 MB average ComfyUI PNG → 300-ish KB progressive JPEG compression is happy. No reason to tweak unless image quality feels degraded.

### File map (from memory, to save a re-read)

```
realOrAi/                       GitHub Pages root
├── index.html, styles.css, game.js, images.js, manifest.webmanifest, icons/
├── images/real/  (96 jpg)
├── images/ai/    (102 jpg)
├── tools/
│   ├── generate.py             ← ComfyUI batch runner
│   ├── prompts.json            ← 85 prompts (35 batch1 + 50 batch2)
│   ├── seeds.json              ← per-slug seed state
│   ├── img_utils.py            ← shrink_to_jpeg(), shared constants
│   ├── download_commons.py     ← generic Commons downloader w/ normalize
│   ├── download_batch2.py      ← the curated 50-image real-photo run (kept as reference)
│   ├── download_batch2b.py     ← verified-filename follow-up after batch2's 404s
│   ├── make_icons.py           ← regenerates PWA icons
│   ├── normalize_images.py     ← one-shot resize/recompress existing files
│   ├── workflows/              ← comfy_realism_workflow_api.json, comfy_art_workflow_api.json
│   └── .venv/                  ← gitignored; recreate with `uv venv .venv && uv pip install --python .venv websocket-client Pillow`
└── notes/  NOTES.md, PROMPT_GUIDE.md, CREDITS.md
```

### Quick-start checklist for next session

1. `cd` to the project directory
2. Make sure ComfyUI server is reachable: `curl -sSI http://127.0.0.1:8188/` (override server with `--server HOST:PORT` or `COMFY_SERVER` env var)
3. Activate venv: `source tools/.venv/bin/activate` (or recreate if lost)
4. Edit `tools/prompts.json` (add entries) and/or `tools/download_commons.py` (add to `CANDIDATES` list)
5. Run `python tools/generate.py` or `python tools/download_commons.py`
6. Don't forget to manually append new real entries to `images.js` if you downloaded new photos (AI entries auto-sync)
7. Smoke-test locally with `python3 -m http.server 8000`, commit, push — Pages auto-deploys

---


## Tells we've spotted in Z-Image output

These are cues that give away AI images; fixing them (via prompt or negative) makes the game harder.

### Confirmed across multiple images
- **Repeating patterns are *not* repeating.** Printed napkins, wallpaper, fabric. Real manufactured cloth has a stamped/woven repeat; AI tends to draw every element freehand-unique. Fix: explicitly prompt `"small repeating floral motif"` or pick `"plain linen"`.
- **Orphaned stickers / labels.** Chopsticks served with a tiny rectangular label still attached; wine bottles with vague label blobs. Fix: add `"no packaging, no labels"` to positive, or `"stickers, labels, wrappers"` to negative.
- **Too-regular wood grain.** Table surfaces look like cheap laminate — perfectly parallel stripes. Real wood has knots, varied grain direction, board seams. Fix: `"varied wood grain with knots and imperfections"`, or pick a different surface (stone, metal, cloth).

### v1 → v2 ramen regeneration cleared these
- **Mismatched egg yolks.** v1 had two halves of the same egg rendered differently. Z-Image v2 workflow fixed this without prompt change — seems to be a workflow/sampler improvement, not a prompt issue.

### Known-hard classes we haven't stress-tested yet
- **Hands.** Every prompt that includes a person should be reviewed for finger count / joint bending.
- **Text in the background.** When we ask for big hero text (signs, neon), Z-Image nails it. Incidental background text (magazine covers, license plates) is usually the weakest link.
- **Reflections.** Mirror reflections, wet-pavement reflections often break physics.

## Difficulty bucket idea (not implemented)

Rough plan for when we want to add a difficulty selector:

Tag each image in `images.js` with `difficulty: "easy" | "medium" | "hard"`, store the player's choice in localStorage, and filter the deck accordingly.

Approximate buckets today:
- **Easy AI side**: the 17 legacy Commons AI images (stylized DALL-E / Copilot illustrations).
- **Medium AI side**: the 26 Z-Image realism images (current batch).
- **Hard AI side**: Z-Image art pastiches (Renaissance, Van Gogh imitations, Dutch still life). Need to be paired with challenging real photos — weird-lighting, surreal-but-real shots — so the bucket isn't just "it's always AI."

The real side needs tiering too. "Hard" real photos are ones that genuinely look AI-ish (amateur shots with odd lighting, macro extremes, cosmic / surreal subjects) — otherwise a hard AI next to an obvious Featured Picture is trivially resolved.

### Auto-calibration (v3 idea)
Track per-image wrong-guess rate in localStorage. Images that fool the player most often get promoted to the "hard" pool on the next session. Images that are guessed correctly every time get demoted to "easy." No manual tagging needed once we have enough play data.

## Prompt refinements to try next pass

Specific slugs with known tells:

| Slug | Tell | Proposed fix |
|------|------|--------------|
| `ai_food_ramen` | napkin has unique florals (not a repeat) | change to `"plain linen runner"` |
| `ai_food_ramen` | chopsticks have a dangling label | add `"no labels"` to positive; `"stickers, wrappers"` to negative |
| `ai_food_ramen` | wood grain too regular | pick `"stone surface"` or prompt `"weathered oak with knots"` |

When making these changes, just edit `tools/prompts.json` and re-run `python generate.py --force --only ai_food_ramen`. The seed auto-increments from `tools/seeds.json`, so forced regens aren't tempted to rerun the same latent.

## Models to try next

Currently all Z-Image batch images come from one model. Regenerating variety from other models reduces the chance the game becomes solvable by recognizing a single model's visual fingerprint (the "Z-Image look").

- **Ernie** (Baidu) — worth trying for photorealism diversity. Different training data, different tells.
- **Klein** — worth A/B-ing against Z-Image on the same prompts to see which categories it handles better.

Implementation hint: the workflow JSON drives everything, so adding a new model is mostly: new workflow file in `tools/workflows/`, add a `workflow: "ernie"` option to `tools/prompts.json` entries, and extend the `WORKFLOWS` dict in `tools/generate.py`. No other code changes needed.

## Future feature ideas

- **Difficulty selector** on the start screen (see above).
- **Per-image stats** — "you got this one wrong 3 out of 4 times" displayed in the feedback panel.
- **"Why I was wrong" hints** — after a miss, show a short sentence about the tell we expected you to spot (e.g. "watch for repeating patterns in decorative cloth").
- **Share your score** — link to a fixed permutation that a friend can try.
- **Mix ratio per round** — some rounds 70% real / 30% AI, others the inverse, so the player can't default to "guess AI if unsure."
