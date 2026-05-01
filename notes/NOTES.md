# Real or AI? — Project Notes

Working notes for future iterations. Update as you learn more.

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
