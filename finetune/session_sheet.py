"""Pictures of agent-loop sessions (blender_task/agent_loop.py) from several sources, side by side.

Usage: python finetune/session_sheet.py <items.json> <out dir> --side "Name=<dir>" [--side ...] [--tile 512] [--rows 10] [--title T]
Writes <out>/finals_<n>.png: one row per request, one column per source, the scene as each session left it (final.png),
with its numbers under it. Writes <out>/first_and_end_<n>.png: per source the picture after the first run that ended
without an error, beside the scene at the end, to show what the later runs added. Writes <out>/strips/<id>.png: for each source a row of the pictures the model was shown,
one per run, so the session can be followed; a red frame marks a run that ended in an error. And
<out>/session_summary.json with the numbers per source.
"""
import argparse, json, os, statistics
import matplotlib
from PIL import Image, ImageDraw, ImageFont

F = os.path.join(matplotlib.get_data_path(), "fonts/ttf/")
INK, MUTED, BAD, GOOD, PAPER, EMPTY = (25, 28, 33), (95, 102, 112), (176, 38, 38), (30, 110, 60), (250, 250, 248), (232, 232, 228)
ap = argparse.ArgumentParser()
ap.add_argument("items"); ap.add_argument("out"); ap.add_argument("--side", action="append", required=True)
ap.add_argument("--tile", type=int, default=512); ap.add_argument("--rows", type=int, default=10); ap.add_argument("--title", default="")
ap.add_argument("--strip-tile", type=int, default=224); ap.add_argument("--pair-tile", type=int, default=384)
a = ap.parse_args()
sides = [x.split("=", 1) for x in a.side]
items = json.load(open(a.items))
if isinstance(items, dict):
    items = [it for group in items.values() for it in group]
os.makedirs(os.path.join(a.out, "strips"), exist_ok=True)
fb, fs, ft = ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 15), ImageFont.truetype(F + "DejaVuSans.ttf", 12), ImageFont.truetype(F + "DejaVuSans-Bold.ttf", 20)


def load(d, pid):
    p = os.path.join(d, pid, "session.json")
    return json.load(open(p)) if os.path.exists(p) else None


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        if d.textlength((cur + " " + w).strip(), font=font) > width and cur:
            lines.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return lines + [cur]


PAD, GAP, HEAD, CAP, STRIP = 16, 8, 78, 36, 36
W = PAD * 2 + len(sides) * a.tile + (len(sides) - 1) * GAP
rowh = CAP + a.tile + STRIP + 10
for g in range(0, len(items), a.rows):
    part = items[g:g + a.rows]
    sheet = Image.new("RGB", (W, HEAD + len(part) * rowh + PAD), PAPER)
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 12), a.title or "Sessions", font=ft, fill=INK)
    for k, (name, _) in enumerate(sides):
        d.text((PAD + k * (a.tile + GAP), 50), name, font=fb, fill=INK)
    for r, it in enumerate(part):
        y = HEAD + r * rowh
        for j, line in enumerate(wrap(d, f"{it.get('film', it['id'])}.  {it['prompt']}", fs, W - 2 * PAD)[:2]):
            d.text((PAD, y + j * 15), line, font=fs, fill=MUTED)
        for k, (name, sd) in enumerate(sides):
            x, s = PAD + k * (a.tile + GAP), load(sd, it["id"])
            png = os.path.join(sd, it["id"], "final.png")
            if s is None:
                lines, colour = ["no session"], BAD
            else:
                lines = [f"{s['runs']} runs, {s['runs_with_error']} with an error; {s['final_objects'] or 0} objects, {s['final_lights'] or 0} lights"
                         + ("" if s.get("final_own_camera") else "; no camera of its own (default view)"),
                         f"{s['tokens_written']:,} tokens written in {s['minutes']:.0f} min; ended: {s['stop']}"]
                colour = GOOD if s["final_objects"] else BAD
            if os.path.exists(png):
                sheet.paste(Image.open(png).convert("RGB").resize((a.tile, a.tile), Image.LANCZOS), (x, y + CAP))
            else:
                d.rectangle((x, y + CAP, x + a.tile - 1, y + CAP + a.tile - 1), fill=EMPTY)
            for j, text in enumerate(lines):
                while d.textlength(text, font=fs) > a.tile and len(text) > 8:
                    text = text[:-2]
                d.text((x, y + CAP + a.tile + 3 + j * 15), text, font=fs, fill=colour if j == 0 else MUTED)
    out = os.path.join(a.out, f"finals_{g // a.rows + 1}.png")
    sheet.save(out)
    print("wrote", out, sheet.size)



def first_ok(s):                                           # the first run that ended without an error, or None
    return next((t for t in (s["turn_list"] if s else []) if t.get("run") and not t["run"]["error"] and t["run"]["process"] == "exit 0"), None)


Q = a.pair_tile                                            # what the loop added: first run that worked, beside the final scene
W2 = PAD * 2 + len(sides) * (2 * Q + 4) + (len(sides) - 1) * 20
rowh2 = CAP + Q + 24
for g in range(0, len(items), a.rows):
    part = items[g:g + a.rows]
    sheet = Image.new("RGB", (W2, HEAD + len(part) * rowh2 + PAD), PAPER)
    d = ImageDraw.Draw(sheet)
    d.text((PAD, 12), (a.title or "Sessions") + ": first run that worked, and the scene at the end", font=ft, fill=INK)
    for k, (name, _) in enumerate(sides):
        d.text((PAD + k * (2 * Q + 24), 50), name, font=fb, fill=INK)
    for r, it in enumerate(part):
        y = HEAD + r * rowh2
        for j, line in enumerate(wrap(d, f"{it.get('film', it['id'])}.  {it['prompt']}", fs, W2 - 2 * PAD)[:2]):
            d.text((PAD, y + j * 15), line, font=fs, fill=MUTED)
        for k, (name, sd) in enumerate(sides):
            x, s = PAD + k * (2 * Q + 24), load(sd, it["id"])
            t = first_ok(s)
            cells = [(os.path.join(sd, it["id"], "steps", f"step_{t['turn']:02d}.png") if t else None,
                      f"run {s['turn_list'].index(t) + 1 if t else '-'}: {t['run']['n_objects'] or 0} objects" if t else "no run without an error"),
                     (os.path.join(sd, it["id"], "final.png"), f"end, after {s['runs']} runs: {s['final_objects'] or 0} objects" if s else "no session")]
            for c, (png, text) in enumerate(cells):
                cx = x + c * (Q + 4)
                if png and os.path.exists(png):
                    sheet.paste(Image.open(png).convert("RGB").resize((Q, Q), Image.LANCZOS), (cx, y + CAP))
                else:
                    d.rectangle((cx, y + CAP, cx + Q - 1, y + CAP + Q - 1), fill=EMPTY)
                d.text((cx, y + CAP + Q + 3), text, font=fs, fill=MUTED)
    out = os.path.join(a.out, f"first_and_end_{g // a.rows + 1}.png")
    sheet.save(out)
    print("wrote", out, sheet.size)

T = a.strip_tile
for it in items:                                           # the pictures the model was shown, run by run
    rows = []
    for name, sd in sides:
        s = load(sd, it["id"])
        rows.append((name, s, [t for t in (s["turn_list"] if s else []) if t.get("run")]))
    n = max((len(r[2]) for r in rows), default=0)
    if not n:
        continue
    strip = Image.new("RGB", (PAD * 2 + n * (T + 4), 56 + len(rows) * (T + 44)), PAPER)
    d = ImageDraw.Draw(strip)
    d.text((PAD, 10), f"{it.get('film', it['id'])}: the scene after each run", font=fb, fill=INK)
    d.text((PAD, 32), it["prompt"][:int(strip.width / 6.5)], font=fs, fill=MUTED)
    for j, (name, s, runs) in enumerate(rows):
        y = 56 + j * (T + 44)
        d.text((PAD, y), name, font=fb, fill=INK)
        for k, t in enumerate(runs):
            x, png = PAD + k * (T + 4), os.path.join(dict(sides)[name], it["id"], "steps", f"step_{t['turn']:02d}.png")
            bad = bool(t["run"]["error"]) or t["run"]["process"] != "exit 0"
            if os.path.exists(png):
                strip.paste(Image.open(png).convert("RGB").resize((T, T), Image.LANCZOS), (x, y + 20))
            else:
                d.rectangle((x, y + 20, x + T - 1, y + 20 + T - 1), fill=EMPTY)
            if bad:
                d.rectangle((x, y + 20, x + T - 1, y + 20 + T - 1), outline=BAD, width=3)
            d.text((x + 2, y + 22 + T), f"{t['turn']}: {t['run']['n_objects'] or 0} obj" + (" (error)" if bad else ""), font=fs, fill=BAD if bad else MUTED)
    strip.save(os.path.join(a.out, "strips", it["id"] + ".png"))
print("wrote", len(items), "strips to", os.path.join(a.out, "strips"))

summary = {}
for name, sd in sides:
    ss = [s for s in (load(sd, it["id"]) for it in items) if s]
    if ss:
        summary[name] = {"sessions": len(ss), "with_a_final_picture": sum(bool(s["final_picture"]) and bool(s["final_objects"]) for s in ss),
                         "median_runs": statistics.median(s["runs"] for s in ss), "runs": sum(s["runs"] for s in ss),
                         "runs_with_error": sum(s["runs_with_error"] for s in ss), "median_final_objects": statistics.median(s["final_objects"] or 0 for s in ss),
                         "with_own_camera": sum(bool(s.get("final_own_camera")) for s in ss), "median_tokens_written": statistics.median(s["tokens_written"] for s in ss),
                         "total_minutes": round(sum(s["minutes"] for s in ss), 1), "stops": {k: sum(s["stop"] == k for s in ss) for k in sorted({s["stop"] for s in ss})}}
json.dump(summary, open(os.path.join(a.out, "session_summary.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
