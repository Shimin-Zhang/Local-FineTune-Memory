"""Web versions of the post's figures and animations, written into the personal site.

python charts/post_web_assets.py <site>/public/images/journal/<slug>

Each still is saved as WebP at several widths (so the page can offer the browser a choice); each animation as
its 1080p H.264 MP4 (stream copy) plus a poster frame. Re-run after a figure changes; it overwrites.
Also writes og.jpg, the 1200x630 social card: the opening film pair without its request.
Prints one line per file and a manifest (manifest.json in the output folder) with widths and heights.
"""
import json, os, subprocess, sys

from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
C = "charts/out"
WIDTHS = (800, 1200, 1600)   # the post column is 800 CSS px wide: 1x, phone 3x, 2x


STILLS = {
    "vram-gguf": f"{C}/vram_gguf_3000.png",
    "bits-per-weight": f"{C}/bits_per_weight.png",
    "train-bill-pair": f"{C}/train_bill_pair.png",
    "qlora-stair": f"{C}/qlora_stair.png",
    "mlp-layer-cost": f"{C}/mlp_layer_cost.png",
    "checkpointing": f"{C}/checkpointing.png",
    "single-gpu": f"{C}/single_gpu.png",
    "run3-loss": f"{C}/run3_loss.png",
    "pairs10": f"{C}/pairs10_prompts.png",                    # the three sheets with requests: post_prompt_sheets.py
    "films10": f"{C}/films10_prompts.png",
    "sonnet-example-airship-hangar": "results/synth_v1/show/train_b94/train_0048.png",
    "good-bad-ugly-before-after": f"{C}/film_gbu_prompt.png",
}
VIDEOS = {
    "ckpt-anim": (f"{C}/ckpt_anim.mp4", f"{C}/ckpt_anim_poster.png"),
    "chunk-anim": (f"{C}/chunk_anim.mp4", f"{C}/chunk_anim_poster.png"),
}

manifest = {"stills": {}, "videos": {}}
for name, src in STILLS.items():
    im = Image.open(src).convert("RGB")
    widths = sorted({w for w in WIDTHS if w < im.width} | {min(im.width, WIDTHS[-1])})
    entry = []
    for w in widths:
        h = round(im.height * w / im.width)
        path = os.path.join(OUT, f"{name}-{w}.webp")
        im.resize((w, h), Image.LANCZOS).save(path, "WEBP", quality=84, method=6)
        entry.append({"file": os.path.basename(path), "width": w, "height": h, "kb": round(os.path.getsize(path) / 1024)})
        print(f"{entry[-1]['file']:48s} {w}x{h}  {entry[-1]['kb']} KB")
    manifest["stills"][name] = entry

for name, (mp4, poster) in VIDEOS.items():
    entry = {}
    # The renders are already small H.264 files (under 2 MB at 1080p), and the ffmpeg on this machine has no x264
    # encoder, so the video stream is copied as it is, with the index moved to the front for streaming.
    path = os.path.join(OUT, f"{name}-1080.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-c", "copy", "-an",
                    "-movflags", "+faststart", path], check=True)
    entry["1080"] = {"file": os.path.basename(path), "kb": round(os.path.getsize(path) / 1024)}
    print(f"{entry['1080']['file']:48s} 1080p  {entry['1080']['kb']} KB")
    p = Image.open(poster).convert("RGB").resize((1280, 720), Image.LANCZOS)
    ppath = os.path.join(OUT, f"{name}-poster.webp")
    p.save(ppath, "WEBP", quality=82, method=6)
    entry["poster"] = {"file": os.path.basename(ppath), "kb": round(os.path.getsize(ppath) / 1024)}
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                         capture_output=True, text=True).stdout.strip()
    entry["seconds"] = round(float(dur), 1)
    print(f"{entry['poster']['file']:48s} poster  {entry['poster']['kb']} KB   ({entry['seconds']} s)")
    manifest["videos"][name] = entry

# The social card: the two final pictures of the opening film pair, a label over each, at the size link previews use.
OG_W, OG_H, OG_TILE, OG_GAP, OG_TOP = 1200, 630, 558, 12, 54
card = Image.new("RGB", (OG_W, OG_H), (14, 14, 22))
d = ImageDraw.Draw(card)
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
for k, (side, label) in enumerate((("untuned", "untuned"), ("tuned", "fine-tuned"))):
    im = Image.open(f"results/finetune_v3/movies/{side}/film_19_good_bad_ugly/final.png").convert("RGB")
    x = (OG_W - 2 * OG_TILE - OG_GAP) // 2 + k * (OG_TILE + OG_GAP)
    card.paste(im.resize((OG_TILE, OG_TILE), Image.LANCZOS), (x, OG_TOP))
    d.text((x + (OG_TILE - d.textlength(label, font=f)) / 2, 10), label, font=f, fill=(222, 222, 230))
card.save(os.path.join(OUT, "og.jpg"), "JPEG", quality=88, optimize=True)
manifest["og"] = {"file": "og.jpg", "size": [OG_W, OG_H], "kb": round(os.path.getsize(os.path.join(OUT, "og.jpg")) / 1024)}
print(f"{'og.jpg':48s} {OG_W}x{OG_H}  {manifest['og']['kb']} KB")

json.dump(manifest, open(f"{C}/post_web_manifest.json", "w"), indent=1)
total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print(f"{len(os.listdir(OUT))} files, {total / 2**20:.1f} MiB in {OUT}")
