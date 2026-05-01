# Prompt Guide — Z-Image for Real or AI?

Practical notes for writing prompts that fool people, learned across ~35 generations with Z-Image via ComfyUI.

## Goal

Every AI image should look like it came from the same camera roll as the real photos it sits next to. If a player can glance and say "that's got the AI look" without inspecting details, the prompt failed.

## What works

- **Specify camera language.** `"shot on 50mm f/1.8"`, `"85mm"`, `"wide-angle 14mm"`, `"telephoto compression"`. Forces a photographic frame of reference instead of "illustrative" defaults.
- **Specify lighting.** `"golden hour"`, `"soft overcast"`, `"harsh midday sun"`, `"window light from the left"`. AI defaults to flat, even lighting — real photos almost never look like that.
- **Specify film / sensor look.** `"Kodak Portra 400"`, `"medium format film"`, `"Fujifilm color look"`, `"slight film grain"`. Adds the imperfections that distinguish photos from renders.
- **Describe depth of field explicitly.** `"shallow depth of field"`, `"background completely out of focus"`, `"f/2 bokeh"`. The default AI image is too-sharp corner to corner.
- **Use concrete subjects.** `"a scarlet macaw on a mossy branch"` beats `"a colorful bird on a branch"`. Z-Image is strong enough to render named species / specific locations / named styles accurately.
- **Describe composition like a photographer.** `"shot from water level"`, `"45-degree angle"`, `"overhead"`, `"through the window"`. Gives the AI a reason to offset the subject from dead-center.

## What doesn't work (avoid these)

- `"stunning"`, `"masterpiece"`, `"hyperdetailed"`, `"8k"`, `"intricate"`, `"trending on artstation"` — all of these push the output toward the "AI look": over-sharpened, over-saturated, glossy.
- `"beautiful"`, `"perfect"` — same problem, triggers the showcase-render default.
- Bare generic prompts (`"a cat in a garden"`) — leave too much to the model's defaults.

## Text rendering

Z-Image is noticeably stronger at text than older models. Use it deliberately:

- **Works well**: 3–8 character all-caps signs, single words on neon, short painted signage.
- **Works OK with effort**: multi-line signage if you quote the exact text. `"a small chalkboard reads 'HEIRLOOM $4/lb'"`.
- **Still risky**: paragraphs, small-print (magazine covers, license plates, book spines). These often gibberish out even while the big text is perfect.

Add `"garbled text, gibberish letters, misspelled letters"` to the negative prompt whenever you use text — helps clean up secondary text the model adds on its own.

## Negatives that reliably help

A good default negative for realism prompts:
```
watermark, cartoon, illustration, oversaturated, hdr look, plastic skin, airbrushed, waxy, over-sharpened, garbled text
```

For art pastiches, invert:
```
watermark, photograph, photorealistic, 3d render, digital art, sharp digital edges
```

## Category-specific notes

- **Portraits**: prompt for specific ethnicities/ages/professions and always include texture words (`"clear skin texture and fine lines"`, `"weathered hands"`, `"freckles"`, `"flyaway hair"`). Airbrushed skin is the #1 portrait tell.
- **Food**: avoid top-down "food magazine" shots unless the real pool has them — most real food photos in our dataset are casual angles. Also avoid garnishes that look like they're holding on by magic (floating herb sprigs).
- **Wildlife**: always name the species (`"red fox"`, not `"a wild dog"`) and the lens (`"400mm telephoto"`). Wildlife photography has a very specific look that Z-Image reproduces well when pushed.
- **Art pastiches**: name the art movement and a structural technique — `"visible brushstrokes"`, `"broken color"`, `"impasto"`, `"canvas texture"`, `"aged varnish"`, `"cracked paint"`. The art workflow skips the sharpen+grain post-processing, which is correct for paintings.
- **Astronomy**: prompt for specific objects (`"Milky Way core"`, `"aurora borealis"`) and exposure language (`"long exposure"`, `"14mm wide-angle"`). AI is surprisingly good at night sky.

## Aspect ratios

Using 4 ratios mapped to ~2 MP, multiples of 64:

| Name  | Dimensions   | Typical use              |
|-------|--------------|--------------------------|
| 1:1   | 1472 × 1472  | Macro, food-overhead     |
| 3:2   | 1792 × 1216  | Most landscapes, streets |
| 2:3   | 1216 × 1792  | Portraits, tall subjects |
| 16:9  | 1920 × 1088  | Wide vistas, cinematic   |
| 4:3   | 1664 × 1280  | Classical painting mat   |
| 3:4   | 1280 × 1664  | Tall painting mat        |

Mix them in `prompts.json` so the deck doesn't have a "same-shape-every-time" tell.

## Seed handling

The generator picks a fresh seed per slug on first run and then increments on forced regens (stored in `tools/seeds.json`). If a specific seed produced a great image, commit `seeds.json` alongside `prompts.json` so it's reproducible later.
