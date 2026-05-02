#!/usr/bin/env python3
"""
Batch-generate AI images for the Real or AI? game using ComfyUI.

Reads prompts.json, picks the matching workflow (realism/art), patches in
the prompt text, negative prompt, aspect ratio, and a fresh random seed,
then queues it through the ComfyUI WebSocket API and downloads the result
into ../realOrAi/images/ai/<slug>.png.

Setup (one-time):
    cd tools
    uv venv .venv
    uv pip install --python .venv websocket-client Pillow

Run:
    source .venv/bin/activate
    python generate.py                      # generate all missing
    python generate.py --only ai_food_ramen # single prompt
    python generate.py --force              # regenerate even if exists
    python generate.py --server 192.168.33.101:8188

On each run, rewrites the marker block in ../images.js so it matches every
prompt whose .jpg currently exists — safe across --only / --force / partial runs:
    // === AI auto-generated (do not hand-edit this block) ===
    // === end AI auto-generated ===
"""
import argparse
import copy
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

try:
    import websocket  # websocket-client
except ImportError:
    sys.stderr.write("Missing dependency. Run: uv pip install --python .venv websocket-client Pillow\n")
    sys.exit(1)

from img_utils import shrink_to_jpeg  # noqa: E402

HERE = Path(__file__).parent.resolve()
REPO = HERE.parent
WORKFLOWS = {
    "realism": HERE / "workflows" / "comfy_realism_workflow_api.json",
    "art":     HERE / "workflows" / "comfy_art_workflow_api.json",
}
PROMPTS_FILE = HERE / "prompts.json"
SEEDS_FILE = HERE / "seeds.json"
OUTPUT_DIR = REPO / "images" / "ai"
IMAGES_JS = REPO / "images.js"

# Workflow node IDs (confirmed identical across the v2 realism/art workflows)
NODE_POSITIVE_PROMPT = "133"
NODE_NEGATIVE_PROMPT = "132"
NODE_LATENT = "130"
NODE_SEED = "509"          # RandomNoise.noise_seed
SEED_KEY = "noise_seed"

# Aspect ratios -> (width, height). Kept close to ~2 MP, multiples of 64.
# Matches the "1920x1088" budget of the supplied workflow (≈2.1 MP).
ASPECTS = {
    "1:1":  (1472, 1472),
    "3:2":  (1792, 1216),  # landscape
    "2:3":  (1216, 1792),  # portrait
    "16:9": (1920, 1088),  # as provided
    "9:16": (1088, 1920),
    "4:3":  (1664, 1280),
    "3:4":  (1280, 1664),
}


def load_seeds():
    if SEEDS_FILE.exists():
        try:
            return json.loads(SEEDS_FILE.read_text())
        except Exception:
            pass
    return {}


def save_seeds(seeds):
    SEEDS_FILE.write_text(json.dumps(seeds, indent=2, sort_keys=True) + "\n")


def next_seed_for(slug, seeds):
    """Monotonically increment this slug's seed; initialize from random if unseen."""
    prev = seeds.get(slug)
    seed = (prev + 1) if isinstance(prev, int) else random.randint(1, 2**31 - 1)
    seeds[slug] = seed
    return seed


def patch_workflow(base, prompt_item, seed):
    wf = copy.deepcopy(base)
    wf[NODE_POSITIVE_PROMPT]["inputs"]["text"] = prompt_item["positive"]
    wf[NODE_NEGATIVE_PROMPT]["inputs"]["text"] = prompt_item.get("negative", "watermark")
    w, h = ASPECTS[prompt_item.get("aspect", "3:2")]
    wf[NODE_LATENT]["inputs"]["width"] = w
    wf[NODE_LATENT]["inputs"]["height"] = h
    wf[NODE_SEED]["inputs"][SEED_KEY] = seed
    return wf


class ComfyClient:
    def __init__(self, server):
        self.server = server
        self.client_id = str(uuid.uuid4())

    def queue_prompt(self, prompt, prompt_id):
        data = json.dumps({
            "prompt": prompt,
            "client_id": self.client_id,
            "prompt_id": prompt_id,
        }).encode("utf-8")
        req = urllib.request.Request(f"http://{self.server}/prompt", data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    def view(self, filename, subfolder, ftype):
        qs = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": ftype})
        with urllib.request.urlopen(f"http://{self.server}/view?{qs}", timeout=60) as r:
            return r.read()

    def history(self, prompt_id):
        with urllib.request.urlopen(f"http://{self.server}/history/{prompt_id}", timeout=30) as r:
            return json.loads(r.read())

    def generate(self, prompt):
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server}/ws?clientId={self.client_id}", timeout=30)
        try:
            prompt_id = str(uuid.uuid4())
            self.queue_prompt(prompt, prompt_id)
            while True:
                msg = ws.recv()
                if not isinstance(msg, str):
                    continue
                data = json.loads(msg)
                if data.get("type") == "executing":
                    d = data["data"]
                    if d.get("node") is None and d.get("prompt_id") == prompt_id:
                        break
                if data.get("type") == "execution_error":
                    raise RuntimeError(f"Comfy error: {data.get('data')}")
        finally:
            ws.close()

        hist = self.history(prompt_id).get(prompt_id, {})
        for _node_id, output in hist.get("outputs", {}).items():
            for img in output.get("images", []) or []:
                return self.view(img["filename"], img.get("subfolder", ""), img.get("type", "output"))
        raise RuntimeError("No image in history output")


IMAGES_JS_START = "  // === AI auto-generated (do not hand-edit this block) ==="
IMAGES_JS_END   = "  // === end AI auto-generated ==="


def update_images_js(all_prompts):
    """Rewrite the auto-generated block to reflect every prompt whose .jpg
    currently exists on disk. `all_prompts` = full list from prompts.json.
    This keeps the manifest in sync regardless of --only / --force / partial runs.
    """
    if not IMAGES_JS.exists():
        print(f"  (no {IMAGES_JS} — skipping manifest update)")
        return

    text = IMAGES_JS.read_text()
    present = [p for p in all_prompts if (OUTPUT_DIR / f"{p['slug']}.jpg").exists()]
    lines = [
        f'  {{ src: "images/ai/{p["slug"]}.jpg", isAI: true, alt: "{p["slug"]}", caption: "{p["caption"]}" }},'
        for p in present
    ]
    block = "\n".join([IMAGES_JS_START, *lines, IMAGES_JS_END])

    if IMAGES_JS_START in text and IMAGES_JS_END in text:
        pre, _, rest = text.partition(IMAGES_JS_START)
        _, _, post = rest.partition(IMAGES_JS_END)
        text = pre + block + post
    else:
        # Insert before the closing `];`
        idx = text.rfind("];")
        if idx < 0:
            print("  (couldn't find closing ']; ' — appending)")
            text += "\n" + block + "\n"
        else:
            text = text[:idx] + "\n" + block + "\n" + text[idx:]

    IMAGES_JS.write_text(text)
    print(f"  updated {IMAGES_JS.name} with {len(present)} entries")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=os.environ.get("COMFY_SERVER", "192.168.33.101:8188"))
    ap.add_argument("--prompts", default=str(PROMPTS_FILE))
    ap.add_argument("--only", help="Run a single prompt by slug")
    ap.add_argument("--force", action="store_true", help="Regenerate even if output exists")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(args.prompts) as f:
        prompts = json.load(f)
    if args.only:
        prompts = [p for p in prompts if p["slug"] == args.only]
        if not prompts:
            print(f"No prompt with slug {args.only!r}")
            sys.exit(1)

    workflows = {k: json.load(open(v)) for k, v in WORKFLOWS.items()}
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    client = ComfyClient(args.server)
    seeds = load_seeds()

    generated = []
    for p in prompts:
        dest = OUTPUT_DIR / f"{p['slug']}.jpg"
        if dest.exists() and not args.force:
            print(f"SKIP {p['slug']} (already exists)")
            generated.append(p)
            continue

        seed = next_seed_for(p["slug"], seeds)
        wf = patch_workflow(workflows[p["workflow"]], p, seed)
        if args.dry_run:
            print(f"DRY  {p['slug']} ({p['workflow']}, {p.get('aspect','3:2')}, seed={seed})")
            continue

        print(f"GEN  {p['slug']} ({p['workflow']}, {p.get('aspect','3:2')}, seed={seed})...", flush=True)
        t0 = time.time()
        try:
            raw = client.generate(wf)
            jpg = shrink_to_jpeg(raw)
            dest.write_bytes(jpg)
            save_seeds(seeds)   # persist after each successful gen
            print(f"  OK {dest.name} ({len(raw)//1024} KB -> {len(jpg)//1024} KB, {time.time()-t0:.1f}s)")
            generated.append(p)
        except Exception as e:
            print(f"  ERR {p['slug']}: {e}")

    if not args.dry_run:
        # Always rewrite from what's actually on disk, using the full prompt
        # list (not just this run's generated items) so --only / partial runs
        # don't wipe earlier entries.
        with open(args.prompts) as f:
            all_prompts = json.load(f)
        update_images_js(all_prompts)


if __name__ == "__main__":
    main()