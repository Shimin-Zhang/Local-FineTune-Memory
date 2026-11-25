"""The post's three picture sheets, each pair with the request it was built from printed under it.

python charts/post_prompt_sheets.py
    -> charts/out/pairs10_prompts.png   the ten held-out scenes of post_pairs10.py (same seed, same ten), untuned | fine-tuned
       charts/out/film_gbu_prompt.png   The Good, the Bad and the Ugly, untuned | fine-tuned (the post's opening picture)
       charts/out/films10_prompts.png   nine film scenes picked at random, then Ghostbusters (which the post's text names)
       charts/out/prompt_sheets.json    what was picked and the text printed

post_pairs10.py (the sheet without requests) is left as it was. Picks are made with a fixed seed and no look at the
pictures. The nine films are drawn from the 18 that are neither The Good, the Bad and the Ugly (already the opening
picture) nor Ghostbusters (added on purpose, last).

A held-out scene's request is printed whole. A film session's first message was the request printed here followed by
one fixed sentence, the same for every film and both models ("Be detailed: build every part of the scene, and keep
adding and refining detail for as long as you can."); that sentence is left off the sheet.

Held-out pairs: the left view (the script's own camera and lights) of the three-view picture run_sandboxed.py made;
the untuned side is the reply the outline counts (the re-written one where the first was cut off at 4,096 tokens);
a script that raised an error is tagged. Film pairs: each session's final picture.
"""
import glob, json, os, random

from PIL import Image, ImageDraw, ImageFont

V = "results/finetune_v3/scenes"
M = "results/finetune_v3/movies"
OUT = "charts/out"
SEED, TILE = 0, 384
BG, INK, SOFT, TAG = (14, 14, 22), (222, 222, 230), (198, 198, 210), (232, 96, 80)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FIXED_FILM_SENTENCE = " Be detailed: build every part of the scene, and keep adding and refining detail for as long as you can."


def font(px):
    return ImageFont.truetype(FONT, px)


def wrap(draw, text, f, width):
    lines, cur = [], ""
    for w in text.split():
        trial = (cur + " " + w).strip()
        if cur and draw.textlength(trial, font=f) > width:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    return lines + [cur]


def pair_sheet(pairs, tile, head_px, cap_px, cols=2, inner=6):
    """pairs: [{"left": Image, "right": Image, "left_ok": bool, "right_ok": bool, "request": str}].
    Each pair is two tiles side by side with its request under them; `cols` pairs to a row."""
    IN, BETWEEN, TOP, EDGE = inner, 34, round(head_px * 2.1), 18
    CAP_TOP, CAP_BOTTOM, LEAD = round(cap_px * 0.45), round(cap_px * 1.0), round(cap_px * 1.32)
    pair_w = 2 * tile + IN
    W = EDGE * 2 + cols * pair_w + (cols - 1) * BETWEEN
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    head, cap, small = font(head_px), font(cap_px), font(round(head_px * 0.77))
    for p in pairs:
        p["lines"] = wrap(probe, "“" + p["request"] + "”", cap, pair_w - 4)
    rows = [pairs[i:i + cols] for i in range(0, len(pairs), cols)]
    row_h = [tile + CAP_TOP + max(len(p["lines"]) for p in row) * LEAD + CAP_BOTTOM for row in rows]
    H = TOP + sum(row_h) - CAP_BOTTOM + EDGE
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)
    for c in range(min(cols, len(pairs))):
        x0 = EDGE + c * (pair_w + BETWEEN)
        for k, label in enumerate(("untuned", "fine-tuned")):
            x = x0 + k * (tile + IN)
            d.text((x + (tile - d.textlength(label, font=head)) / 2, round(head_px * 0.55)), label, font=head, fill=INK)
    y = TOP
    for row, h in zip(rows, row_h):
        for c, p in enumerate(row):
            x0 = EDGE + c * (pair_w + BETWEEN)
            for k, (im, ok) in enumerate(((p["left"], p["left_ok"]), (p["right"], p["right_ok"]))):
                x = x0 + k * (tile + IN)
                sheet.paste(im if im.size == (tile, tile) else im.resize((tile, tile), Image.LANCZOS), (x, y))
                if not ok:
                    label = "script error"
                    tw = d.textlength(label, font=small)
                    d.rectangle((x + 8, y + 8, x + 8 + tw + 14, y + 8 + round(head_px * 1.2)), fill=TAG)
                    d.text((x + 15, y + 8 + round(head_px * 0.14)), label, font=small, fill=(255, 255, 255))
            for j, line in enumerate(p["lines"]):
                d.text((x0 + 2, y + tile + CAP_TOP + j * LEAD), line, font=cap, fill=SOFT)
        y += h
    return sheet


record = {}

# ---------------------------------------------------------------- the ten held-out scenes (as post_pairs10.py)
ids = sorted({os.path.basename(p).split("__")[0] for p in glob.glob(f"{V}/epoch2/bare/test_*__s0.py")})
long_ids = {os.path.basename(p).split("__")[0] for p in glob.glob(f"{V}/before_long/bare/test_*__s0.py")}
picked = sorted(random.Random(SEED).sample(ids, 10))
assert picked == [r["id"] for r in json.load(open(f"{OUT}/pairs10.json"))["picked"]], "not the ten of post_pairs10.py"
requests = {it["id"]: it["prompt"] for batch in json.load(open("blender_task/prompts_scenes100.json")).values() for it in batch}


def scene_side(folder, i):
    base = f"{V}/{folder}/bare/{i}__s0"
    rep = json.load(open(base + ".report.json"))
    return Image.open(base + ".png").convert("RGB").crop((0, 0, TILE, TILE)), rep.get("error") is None


pairs = []
for i in picked:
    left, left_ok = scene_side("before_long" if i in long_ids else "before", i)
    right, right_ok = scene_side("epoch2", i)
    pairs.append({"id": i, "left": left, "right": right, "left_ok": left_ok, "right_ok": right_ok, "request": requests[i]})
sheet = pair_sheet(pairs, TILE, head_px=27, cap_px=27)
sheet.save(f"{OUT}/pairs10_prompts.png")
record["pairs10_prompts"] = {"size": sheet.size, "seed": SEED, "of": len(ids),
                             "pairs": [{k: p[k] for k in ("id", "request", "left_ok", "right_ok")} | {"lines": len(p["lines"])} for p in pairs]}

# ---------------------------------------------------------------- film scenes
films = {it["id"]: it["prompt"] for batch in json.load(open("blender_task/prompts_movies20.json")).values() for it in batch}
for f, text in films.items():                      # the printed request is the session's first message less the fixed sentence
    for side in ("untuned", "tuned"):
        assert json.load(open(f"{M}/{side}/{f}/session.json"))["prompt"] == text + FIXED_FILM_SENTENCE, (f, side)


def film_pair(f):
    return {"id": f, "left": Image.open(f"{M}/untuned/{f}/final.png").convert("RGB"),
            "right": Image.open(f"{M}/tuned/{f}/final.png").convert("RGB"), "left_ok": True, "right_ok": True, "request": films[f]}


GBU, GHOST = "film_19_good_bad_ugly", "film_18_ghostbusters"
one = [film_pair(GBU)]
sheet = pair_sheet(one, 768, head_px=29, cap_px=29, cols=1, inner=12)
sheet.save(f"{OUT}/film_gbu_prompt.png")
record["film_gbu_prompt"] = {"size": sheet.size, "pairs": [{"id": GBU, "request": films[GBU], "lines": len(one[0]["lines"])}]}

pool = sorted(f for f in films if f not in (GBU, GHOST))
nine = sorted(random.Random(SEED).sample(pool, 9))
ten = [film_pair(f) for f in nine + [GHOST]]
sheet = pair_sheet(ten, TILE, head_px=27, cap_px=27)
sheet.save(f"{OUT}/films10_prompts.png")
record["films10_prompts"] = {"size": sheet.size, "seed": SEED, "drawn_from": len(pool), "added_on_purpose": GHOST,
                             "left_off_every_request": FIXED_FILM_SENTENCE.strip(),
                             "pairs": [{"id": p["id"], "request": p["request"], "lines": len(p["lines"])} for p in ten]}

json.dump(record, open(f"{OUT}/prompt_sheets.json", "w"), indent=1)
for name, r in record.items():
    print(f"{OUT}/{name}.png", r["size"], [(p["id"], p["lines"]) for p in r["pairs"]])
