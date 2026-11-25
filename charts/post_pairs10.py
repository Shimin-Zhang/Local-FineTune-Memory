"""Ten random held-out scenes, untuned vs fine-tuned (run 3, two passes), as one sheet for the blog post.

python charts/post_pairs10.py            -> charts/out/pairs10.png + charts/out/pairs10.json

Picks 10 of the 100 held-out requests with a fixed seed, with no look at the pictures. Each pair is the left view
(the script's own camera and lights) of the three-view picture run_sandboxed.py made. The untuned side is the reply
the outline counts: the re-written reply where the first one was cut off at 4,096 tokens. A script that raised an
error is tagged; its picture shows whatever the scene held when the error hit.
"""
import glob, json, os, random

from PIL import Image, ImageDraw, ImageFont

V = "results/finetune_v3/scenes"
SEED, N, TILE = 0, 10, 384
BG, INK, TAG = (14, 14, 22), (222, 222, 230), (232, 96, 80)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

ids = sorted({os.path.basename(p).split("__")[0] for p in glob.glob(f"{V}/epoch2/bare/test_*__s0.py")})
long_ids = {os.path.basename(p).split("__")[0] for p in glob.glob(f"{V}/before_long/bare/test_*__s0.py")}
picked = sorted(random.Random(SEED).sample(ids, N))
requests = {}
for batch in json.load(open("blender_task/prompts_scenes100.json")).values():
    for it in batch:
        requests[it["id"]] = it["prompt"]


def side(folder, i):
    base = f"{V}/{folder}/bare/{i}__s0"
    rep = json.load(open(base + ".report.json"))
    own = Image.open(base + ".png").convert("RGB").crop((0, 0, TILE, TILE))
    return own, rep.get("error") is None


head = ImageFont.truetype(FONT, 22)
small = ImageFont.truetype(FONT, 17)
IN, BETWEEN, ROW, TOP, EDGE = 6, 34, 14, 46, 18
pair_w = 2 * TILE + IN
W = EDGE * 2 + 2 * pair_w + BETWEEN
rows = N // 2
H = TOP + rows * TILE + (rows - 1) * ROW + EDGE
sheet = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(sheet)
for col in range(2):
    x0 = EDGE + col * (pair_w + BETWEEN)
    for k, label in enumerate(("untuned", "fine-tuned")):
        x = x0 + k * (TILE + IN)
        tw = draw.textlength(label, font=head)
        draw.text((x + (TILE - tw) / 2, 12), label, font=head, fill=INK)

record = []
for n, i in enumerate(picked):
    col, row = n % 2, n // 2
    x0 = EDGE + col * (pair_w + BETWEEN)
    y = TOP + row * (TILE + ROW)
    row_rec = {"id": i, "request": requests[i]}
    for k, folder in enumerate((("before_long" if i in long_ids else "before"), "epoch2")):
        im, ok = side(folder, i)
        x = x0 + k * (TILE + IN)
        sheet.paste(im, (x, y))
        if not ok:
            label = "script error"
            tw = draw.textlength(label, font=small)
            draw.rectangle((x + 8, y + 8, x + 8 + tw + 14, y + 8 + 26), fill=TAG)
            draw.text((x + 15, y + 11), label, font=small, fill=(255, 255, 255))
        row_rec["untuned_ran" if k == 0 else "tuned_ran"] = ok
    record.append(row_rec)

os.makedirs("charts/out", exist_ok=True)
sheet.save("charts/out/pairs10.png")
json.dump({"seed": SEED, "of": len(ids), "picked": record}, open("charts/out/pairs10.json", "w"), indent=1)
print("charts/out/pairs10.png", sheet.size)
for r in record:
    print(f"  {r['id']}  untuned {'ran' if r['untuned_ran'] else 'ERROR'}  tuned {'ran' if r['tuned_ran'] else 'ERROR'}  {r['request'][:70]}")
