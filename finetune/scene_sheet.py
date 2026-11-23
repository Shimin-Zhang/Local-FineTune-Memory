"""Side-by-side pictures of the same requests from several sources: one row per request, one column per source.

Usage: python finetune/scene_sheet.py <prompts.json> <out dir> --side "Name=<dir>[,<dir>...]" [--side ...] [--seed 0] [--tile 384]
prompts.json is a dict of groups of {"id", "prompt"}; one sheet per group is written, <out>/scenes_<n>.png, and
<out>/scene_summary.json with the counts per source. Each <dir> holds <id>__s<seed>.py (or <id>.py), its .report.json
and its .png as written by run_sandboxed.py --own-view. The tile is the view through the script's own camera with its
own lights (the left third of that picture); under it, what happened. A source may name several folders (the reference
scenes are spread over their batches).
"""
import argparse, json, os
import matplotlib
from PIL import Image, ImageDraw, ImageFont
from checks import ran, objects_made, starting_cube_left, own_view_blank, camera_misses_scene, own_view_edge_share

F = os.path.join(matplotlib.get_data_path(), "fonts/ttf/")
INK, MUTED, BAD, WARN, GOOD, PAPER, EMPTY = (25, 28, 33), (95, 102, 112), (176, 38, 38), (150, 96, 0), (30, 110, 60), (250, 250, 248), (232, 232, 228)
ap = argparse.ArgumentParser()
ap.add_argument("prompts"); ap.add_argument("out"); ap.add_argument("--side", action="append", required=True)
ap.add_argument("--seed", type=int, default=0); ap.add_argument("--tile", type=int, default=384); ap.add_argument("--title", default="")
a = ap.parse_args()
sides = [(n, d.split(",")) for n, d in (x.split("=", 1) for x in a.side)]
groups = json.load(open(a.prompts))
os.makedirs(a.out, exist_ok=True)
fb, fs, ft = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 15), ImageFont.truetype(F + "DejaVuSans.ttf", 12), ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 20)


def find(dirs, pid):
    for d in dirs:
        for base in (os.path.join(d, f"{pid}__s{a.seed}"), os.path.join(d, pid)):
            if os.path.exists(base + ".py"):
                return base
    return None


def look(dirs, pid):
    """(the own-view tile or None, a line of text, its colour, a one-word outcome)"""
    base = find(dirs, pid)
    if base is None:
        return None, "no reply", BAD, "missing"
    rep = json.load(open(base + ".report.json")) if os.path.exists(base + ".report.json") else {}
    if not ran(rep):
        why = "timed out" if rep.get("process") == "timeout" else (rep.get("error") or rep.get("process") or "not run")
        return None, "error: " + why[:52], BAD, "error"
    made = objects_made(rep)
    if not made or not os.path.exists(base + ".png"):
        return None, "ran, built nothing", BAD, "nothing built"
    im = Image.open(base + ".png").convert("RGB")
    views = 3 if im.width > 2 * im.height else 1
    tile = im.crop((0, 0, (im.width - 4 * (views - 1)) // views, im.height)).resize((a.tile, a.tile), Image.LANCZOS)
    notes, colour, outcome = [], GOOD, "picture"
    if not rep.get("script_set_camera"):
        notes.append("no camera of its own (fixed view)"); colour, outcome = WARN, "no own camera"
    elif own_view_blank(base + ".png") or camera_misses_scene(rep):
        notes.append("its camera shows nothing"); colour, outcome = BAD, "camera shows nothing"
    elif views == 3 and own_view_edge_share(base + ".png") >= 0.15:
        notes.append("cut off by the frame"); colour, outcome = WARN, "cut off"
    if starting_cube_left(rep):
        notes.append("starting cube left in")
    return tile, f"{made} objects" + ("; " + "; ".join(notes) if notes else ""), colour, outcome


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        if d.textlength((cur + " " + w).strip(), font=font) > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


PAD, GAP, HEAD, CAP, STRIP = 16, 8, 78, 36, 20
W = PAD * 2 + len(sides) * a.tile + (len(sides) - 1) * GAP
summary = {n: {} for n, _ in sides}
for g, (group, items) in enumerate(groups.items(), 1):
    rowh = CAP + a.tile + STRIP + 10
    sheet = Image.new("RGB", (W, HEAD + len(items) * rowh + PAD), PAPER)
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 12), (a.title + ": " if a.title else "") + group, font=ft, fill=INK)
    for k, (name, _) in enumerate(sides):
        d.text((PAD + k * (a.tile + GAP), 50), name, font=fb, fill=INK)
    for r, it in enumerate(items):
        y = HEAD + r * rowh
        for j, line in enumerate(wrap(d, f"{it['id']}  {it['prompt']}", fs, W - 2 * PAD)[:2]):
            d.text((PAD, y + j * 15), line, font=fs, fill=MUTED)
        for k, (name, dirs) in enumerate(sides):
            x = PAD + k * (a.tile + GAP)
            tile, text, colour, outcome = look(dirs, it["id"])
            summary[name][outcome] = summary[name].get(outcome, 0) + 1
            if tile is None:
                d.rectangle((x, y + CAP, x + a.tile - 1, y + CAP + a.tile - 1), fill=EMPTY)
            else:
                sheet.paste(tile, (x, y + CAP))
            while d.textlength(text, font=fs) > a.tile and len(text) > 8:
                text = text[:-2]
            d.text((x, y + CAP + a.tile + 3), text, font=fs, fill=colour)
    sheet.save(os.path.join(a.out, f"scenes_{g}.png"))
    print("wrote", os.path.join(a.out, f"scenes_{g}.png"), sheet.size)
json.dump(summary, open(os.path.join(a.out, "scene_summary.json"), "w"), indent=1)
print(json.dumps(summary))
