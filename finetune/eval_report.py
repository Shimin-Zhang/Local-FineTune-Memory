"""Compare two sets of model-written Blender scripts for the same requests: numbers and side-by-side pictures.

Usage: python finetune/eval_report.py <prompts.json> <out dir> --a "Before=<dir>" --b "After=<dir>" [--seeds 0,1,2]
           [--extra "Name=<dir>" ...]    more sides, for the numbers only (the sheets show --a and --b)
Each <dir> holds <id>__s<seed>.py, .png and .report.json as written by generate.py and run_sandboxed.py --own-view
(the picture is three views side by side: the script's own lighting and camera, then two fixed views under the same
sun), with generation.jsonl one level up. Where the camera and lights point is read from the report; for reports written
before the harness recorded that, from a report of the same name in <dir>_geometry if there is one (the same scripts
run again with --no-render).

Writes <out>/eval_summary.json and, per group of requests, <out>/sheet_<group>.png: one row per request, the first
seed's picture from each side, and under it what happened for every seed.
"""
import argparse, collections, json, os
import matplotlib
from PIL import Image, ImageDraw, ImageFont
from checks import ran, objects_made, own_view_blank, camera_misses_scene, aimed_lights, starting_cube_left

F = os.path.join(matplotlib.get_data_path(), "fonts/ttf/")
INK, MUTED, BAD, WARN, GOOD, PAPER, LINE = (25, 28, 33), (95, 102, 112), (176, 38, 38), (150, 96, 0), (30, 110, 60), (250, 250, 248), (214, 216, 220)
ap = argparse.ArgumentParser()
ap.add_argument("prompts"); ap.add_argument("out"); ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
ap.add_argument("--seeds", default="0,1,2"); ap.add_argument("--title", default=""); ap.add_argument("--extra", action="append", default=[])
a = ap.parse_args()
seeds = [int(s) for s in a.seeds.split(",")]
sides = [tuple(x.split("=", 1)) for x in (a.a, a.b)]
all_sides = sides + [tuple(x.split("=", 1)) for x in a.extra]
groups = json.load(open(a.prompts))
os.makedirs(a.out, exist_ok=True)
PATTERN = lambda t: t.startswith("TEX_") and t not in ("TEX_COORD", "TEX_IMAGE", "TEX_ENVIRONMENT")
RELIEF = {"BUMP", "DISPLACEMENT", "NORMAL_MAP"}


def read(d, pid, seed):
    """What one script did, or None if it was never generated."""
    base = os.path.join(d, f"{pid}__s{seed}")
    if not os.path.exists(base + ".py"):
        return None
    rep = json.load(open(base + ".report.json")) if os.path.exists(base + ".report.json") else {}
    mats = rep.get("materials", [])
    types = [t for m in mats for t in m.get("node_types", [])]
    lights = rep.get("lights", [])
    default_light = [l for l in lights if l["type"] == "POINT" and abs(l["energy"] - 1000) < 1 and abs(l["location"][0] - 4.08) < 0.02]
    ok = ran(rep)
    geo, again = rep, os.path.join(d.rstrip("/") + "_geometry", f"{pid}__s{seed}.report.json")
    if ("scene_center" not in rep or "starting_objects_left" not in rep) and os.path.exists(again):
        geo = json.load(open(again))
        if "starting_objects_left" in geo:                 # the exact mark of the starting cube, from the later run
            rep = dict(rep, starting_objects_left=geo["starting_objects_left"])
    made = objects_made(rep)
    own = bool(ok and made and rep.get("script_set_camera"))
    blank = own_view_blank(base + ".png") if own and os.path.exists(base + ".png") else None
    away = camera_misses_scene(geo) if own and ran(geo) else None
    aimed, astray = aimed_lights(geo) if ok and made and ran(geo) else (0, 0)
    return {"ran": ok, "timeout": rep.get("process") == "timeout", "error": (rep.get("error") or "")[:160], "error_line": rep.get("error_line"),
            "objects": made if ok else 0, "built": bool(ok and made),
            "materials": len(mats), "most_nodes": max([m.get("n_nodes", 0) for m in mats], default=0),
            "pattern": any(PATTERN(t) for t in types), "relief": any(t in RELIEF for t in types),
            "colour_lost": bool(rep.get("materials_viewport_only")), "lights": len(lights) - len(default_light),
            "own_camera": bool(rep.get("script_set_camera")), "camera_sees_nothing": blank, "camera_points_away": away,
            "starting_cube_left": bool(ok and starting_cube_left(rep)),
            "aimed_lights": aimed, "aimed_lights_astray": astray, "depth_of_field": bool(rep.get("depth_of_field")),
            "lines": len(open(base + ".py").read().strip().splitlines()), "image": base + ".png" if os.path.exists(base + ".png") else None}


def tokens(d):
    out = {}
    path = os.path.join(os.path.dirname(os.path.abspath(d)), "generation.jsonl")
    if os.path.exists(path):
        for l in open(path):
            g = json.loads(l)
            out[g["file"]] = (g["usage"]["completion_tokens"], g["finish_reason"])
    return out


data = {name: {} for name, _ in all_sides}
for name, d in all_sides:
    tk = tokens(d)
    for g, items in groups.items():
        for it in items:
            for s in seeds:
                r = read(d, it["id"], s)
                if r is not None:
                    r["tokens"], r["finish"] = tk.get(f"{it['id']}__s{s}", (None, None))
                    data[name][(it["id"], s)] = r


def stats(rs):
    n = len(rs)
    if not n:
        return {"scripts": 0}
    done = [r for r in rs if r["ran"]]
    mean = lambda xs: round(sum(xs) / len(xs), 2) if xs else None
    return {"scripts": n, "ran_without_error": len(done), "built_at_least_one_object": sum(r["built"] for r in rs),
            "ran_but_built_nothing": sum(r["ran"] and not r["built"] for r in rs), "cut_off_by_token_limit": sum(r["finish"] == "length" for r in rs),
            "with_a_texture_pattern": sum(r["pattern"] for r in done), "with_surface_relief": sum(r["relief"] for r in done),
            "colour_lost": sum(r["colour_lost"] for r in done), "with_own_lights": sum(r["lights"] > 0 for r in done),
            "with_two_or_more_lights": sum(r["lights"] >= 2 for r in done), "with_own_camera": sum(r["own_camera"] for r in done),
            "starting_cube_left_in_the_scene": sum(r["starting_cube_left"] for r in done),
            "own_camera_on_a_built_scene": sum(r["camera_sees_nothing"] is not None for r in done),
            "of_which_own_view_is_blank": sum(bool(r["camera_sees_nothing"]) for r in done),
            "own_camera_with_known_direction": sum(r["camera_points_away"] is not None for r in done),
            "of_which_points_away_from_the_scene": sum(bool(r["camera_points_away"]) for r in done),
            "spot_and_area_lights": sum(r["aimed_lights"] for r in done),
            "of_which_point_away_from_the_scene": sum(r["aimed_lights_astray"] for r in done),
            "scripts_with_a_spot_or_area_light": sum(r["aimed_lights"] > 0 for r in done),
            "of_which_none_points_at_the_scene": sum(r["aimed_lights"] > 0 and r["aimed_lights_astray"] == r["aimed_lights"] for r in done),
            "mean_objects_when_ran": mean([r["objects"] for r in done]), "mean_nodes_in_richest_material": mean([r["most_nodes"] for r in done]),
            "mean_script_tokens": mean([r["tokens"] for r in rs if r["tokens"]]), "mean_script_lines": mean([r["lines"] for r in rs])}


summary = {"seeds": seeds, "sides": {}}
for name, _ in all_sides:
    summary["sides"][name] = {"all": stats(list(data[name].values()))}
    for g, items in groups.items():
        summary["sides"][name][g] = stats([data[name][(it["id"], s)] for it in items for s in seeds if (it["id"], s) in data[name]])
errs = {name: collections.Counter(r["error"].split(":")[0] for r in data[name].values() if r["error"]) for name, _ in all_sides}
summary["error_types"] = {k: dict(v.most_common()) for k, v in errs.items()}
# per request: did more or fewer seeds run
moved = collections.Counter()
for g, items in groups.items():
    for it in items:
        x, y = [sum(data[n][(it["id"], s)]["ran"] for s in seeds if (it["id"], s) in data[n]) for n, _ in sides]
        moved["more seeds ran" if y > x else "fewer seeds ran" if y < x else "same"] += 1
summary["requests_by_change_in_seeds_that_ran"] = dict(moved)
json.dump(summary, open(os.path.join(a.out, "eval_summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))

# ------------------------------------------------------------------------------------------------------- sheets
VIEW, GAP, LABEL_W, PAD, HEAD, STRIP = 208, 3, 250, 12, 86, 62
PIC_W = VIEW * 3 + GAP * 2
f, fb, ft, fs = (ImageFont.truetype(F + n, z) for n, z in (("DejaVuSans.ttf", 14), ("DejaVuSans-Bold.ttf", 13), ("DejaVuSans-Bold.ttf", 18), ("DejaVuSans.ttf", 11)))


def wrap(d, text, font, width):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = word
    return lines + ([cur] if cur else [])


def line_for(r):
    if r is None:
        return "not generated", MUTED
    if r["timeout"]:
        return "timed out", BAD
    if not r["ran"]:
        return "error: " + r["error"][:58], BAD
    if not r["built"]:
        return "ran, but built no object", WARN
    bits = [f"{r['objects']} objects", f"{r['most_nodes']} nodes in richest material" + (" (pattern)" if r["pattern"] else ""), f"{r['lights']} lights"]
    return "ran: " + ", ".join(bits) + ("; colour lost" if r["colour_lost"] else "") + ("; own view blank" if r["camera_sees_nothing"] else ""), GOOD


for g, items in groups.items():
    W, ROW = PAD * 4 + LABEL_W + PIC_W * 2, VIEW + STRIP + PAD
    im = Image.new("RGB", (W, HEAD + ROW * len(items) + PAD), PAPER)
    d = ImageDraw.Draw(im)
    d.text((PAD, 10), (a.title + ": " if a.title else "") + g + " requests", font=ft, fill=INK)
    d.text((PAD, 36), f"Picture: seed {seeds[0]}. In each picture: the script's own lights and camera | fixed view, same sun | opposite side. "
                      f"Lines under it: seeds {', '.join(map(str, seeds))}.", font=fs, fill=MUTED)
    for j, (name, _) in enumerate(sides):
        d.text((PAD * (2 + j) + LABEL_W + PIC_W * j, HEAD - 22), name, font=fb, fill=INK)
    for i, it in enumerate(items):
        y = HEAD + i * ROW
        d.line([(PAD, y - PAD // 2), (W - PAD, y - PAD // 2)], fill=LINE)
        for k, line in enumerate(wrap(d, it["prompt"], f, LABEL_W)[:9]):
            d.text((PAD, y + 2 + k * 19), line, font=f, fill=INK)
        d.text((PAD, y + VIEW + STRIP - 18), it["id"], font=fs, fill=MUTED)
        for j, (name, _) in enumerate(sides):
            x = PAD * (2 + j) + LABEL_W + PIC_W * j
            r0 = data[name].get((it["id"], seeds[0]))
            if r0 and r0["image"]:
                pic = Image.open(r0["image"]).convert("RGB")
                pic = pic.resize((PIC_W, VIEW), Image.LANCZOS)
                im.paste(pic, (x, y))
            else:
                d.rectangle([x, y, x + PIC_W, y + VIEW], fill=(236, 236, 233))
                d.text((x + 12, y + VIEW // 2 - 8), "no picture" if r0 else "not generated", font=f, fill=MUTED)
            for k, s in enumerate(seeds):
                text, colour = line_for(data[name].get((it["id"], s)))
                d.text((x, y + VIEW + 4 + k * 17), f"seed {s}: {text}"[:104], font=fs, fill=colour)
    path = os.path.join(a.out, f"sheet_{g}.png")
    im.save(path)
    print("wrote", path, im.size)
