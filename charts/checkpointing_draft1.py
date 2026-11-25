"""Figure: gradient checkpointing on top of QLoRA, left (all activations kept) vs right (+ checkpointing).

Each side: a floating diorama with (back) the training bill as a row of 24 GiB card boxes in the fig-3 style
(1 unit = 1 GiB, the VRAM figure's box; our card solid with its rim, the others ghosted; a signboard with the card
count and total), and (front) the model as a stack of 64 thin layer plates (a locator, not to scale) with layer 33
highlighted, zoomed into a bar of what layer 33 keeps for the backward pass, at one MiB scale shared by both sides
(DETAIL_MIB_PER_UNIT): left 2,193 MiB in four groups, right only the layer's input. Data: charts/data/checkpointing_3000.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/checkpointing.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/checkpointing_draft.png] [--no-render]
"""
import argparse, json, math, os, sys, time
import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="900x600")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=os.path.join(HERE, "out", "checkpointing_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "checkpointing.layout.json"))
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX
GIB = kit.MIB_PER_GIB * kit.UNITS_PER_MIB          # bills: 1 unit = 1 GiB


def half_up(x, nd=0):
    f = 10 ** nd
    return math.floor(x * f + 0.5) / f


data = json.load(open(os.path.join(HERE, "data", "checkpointing_3000.json")))
card_gib = data["card_total_gib"]
box_h = card_gib * GIB
ML = data["middle_layer"]
kept = ML["kept_without_checkpointing_mib"]
kept_ck = ML["kept_with_checkpointing_mib"]
assert abs(sum(kept.values()) - ML["kept_without_checkpointing_total_mib"]) < 0.2

SIDES = [
    {"row": data["rows"][0], "title": ["QLoRA, all activations kept"], "approx_acts": True},
    {"row": data["rows"][1], "title": ["QLoRA + gradient checkpointing", "every layer's forward pass runs twice: 19–26% slower"],
     "approx_acts": False},
]
for S in SIDES:
    R = S["row"]
    S["id"] = R["key"]
    S["n"] = math.ceil(R["total_gib"] / card_gib)
    S["sign"] = [f"{S['n']} × RTX 4090", f"≈ {half_up(R['total_gib']):.0f} GiB"]
    S["lines"] = {L["key"]: L for L in R["lines"]}
assert [S["sign"] for S in SIDES] == [["7 × RTX 4090", "≈ 149 GiB"], ["2 × RTX 4090", "≈ 32 GiB"]]


def gib_text(L, approx):
    v = L["gib"]
    return f"≈ {half_up(v):.0f} GiB" if approx else f"{half_up(v, 1):.1f} GiB"


for S in SIDES:
    Ls = S["lines"]
    S["text"] = {"weights": f"{Ls['weights']['label']} {gib_text(Ls['weights'], False)}",
                 "adapter": f"{Ls['adapter']['label']} {gib_text(Ls['adapter'], False)}",
                 "activations": f"{Ls['activations']['label']} {gib_text(Ls['activations'], S['approx_acts'])}",
                 "loss": f"{Ls['loss']['label']} {gib_text(Ls['loss'], False)}"}
assert SIDES[0]["text"]["activations"] == "activations, 3,000 tokens ≈ 122 GiB"
assert SIDES[1]["text"]["activations"] == "activations, 3,000 tokens 4.5 GiB"
assert SIDES[0]["text"]["weights"] == "frozen 4-bit weights 16.5 GiB" and SIDES[0]["text"]["adapter"] == "adapter 1.2 GiB"
ratio_layer = ML["kept_without_checkpointing_total_mib"] / sum(kept_ck.values())
DETAIL_TXT = {
    "left_head": f"layer 33 keeps {ML['kept_without_checkpointing_total_mib']:,.0f} MiB for the backward pass",
    "right_head": f"layer 33 keeps only its input: {sum(kept_ck.values()):.1f} MiB, {half_up(ratio_layer):.0f}× less",
    "right_note": ["its insides are recomputed in the backward pass,", "one layer at a time"],
    "tower": "layer 33 of 64",
}
for k, v in kept.items():
    DETAIL_TXT[f"seg_{k}"] = f"{k} {half_up(v):,.0f} MiB"
assert DETAIL_TXT["left_head"] == "layer 33 keeps 2,193 MiB for the backward pass"
assert DETAIL_TXT["right_head"] == "layer 33 keeps only its input: 29.3 MiB, 75× less"

# ---------------------------------------------------------------- scale and look
PITCH = kit.FOOTPRINT[0] + 3.0
DETAIL_MIB_PER_UNIT = 40.0           # the layer detail: 1 unit of bar length = 40 MiB, both sides
BAR_H, BAR_D = 2.5, 4.0              # its cross-section
Y_BILL = 56.0                        # the bill row behind; tower and detail bar at y = 0
PLATE, PLATE_T, PLATE_GAP = 7.0, 0.16, 0.08
TOWER_X0 = -12.0
DETAIL_X0 = 0.0
SIDE_GAP = 166.0                     # the right diorama sits this far along the camera's screen-right
ELEVATION, AZIMUTH, LENS = 30.0, -14.0, 80.0   # as the train-bill pair: nearly level rows
C = {k: kit.COLOURS[k] for k in ("weights", "gradients", "optimizer", "activations", "loss", "frozen")}
TINTS = ["#6357cf", "#9085e9", "#bdb6f5", "#e2defc"]  # layer 33's four groups, dark to light (validated ramp)
direction = kit.view_direction(ELEVATION, AZIMUTH)
a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
RIGHT = Vector((-direction.y, direction.x, 0)).normalized()

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
mats = {k: kit.material(f"m_{k}", v, emit=0.10, rough=0.85, spec=0.12) for k, v in C.items()}
tint_m = [kit.material(f"m_tint{i}", t, emit=0.10, rough=0.85, spec=0.12) for i, t in enumerate(TINTS)]
plate_m = kit.material("m_plate", "#4b525c", rough=0.7, spec=0.2)
plate33_m = kit.material("m_plate33", C["activations"], emit=0.35, rough=0.7, spec=0.2)
ghost = kit.material("ghost", "#4d535c", rough=0.6, spec=0.2)
ink_sign = kit.material("sign_ink", "#dcdcdc", rough=0.6, emit=0.2, spec=0.3)
ink_sign2 = kit.material("sign_ink2", "#a9a9a9", rough=0.6, emit=0.2, spec=0.3)
SIGN_EM, SIGN_EM2 = 8.4, 6.6           # larger than fig 3: this scene is zoomed out further

# ---------------------------------------------------------------- build each side
for si, S in enumerate(SIDES):
    X0, Y0 = si * SIDE_GAP * RIGHT.x, si * SIDE_GAP * RIGHT.y
    S["X0"], S["Y0"] = X0, Y0
    Ls = S["lines"]
    pour = [("weights", "frozen", Ls["weights"]["gib"])]
    ad = Ls["adapter"]["gib"]
    pour += [("adapter_w", "weights", ad / 4), ("adapter_g", "gradients", ad / 4), ("adapter_o", "optimizer", ad / 2)]   # 1:1:2 by length
    pour += [("activations", "activations", Ls["activations"]["gib"]), ("loss", "loss", Ls["loss"]["gib"])]
    S["centres"] = [(X0 + k * PITCH + a, Y0 + Y_BILL) for k in range(S["n"])]
    S["segs"], S["objs"], c = [], [], 0.0
    for key, col, g in pour:
        c0, c1 = c, c + g * GIB
        for k in range(S["n"]):
            a0, a1 = max(c0, k * box_h), min(c1, (k + 1) * box_h)
            if a1 > a0 + 1e-9:
                cx, cy = S["centres"][k]
                ob = kit.cuboid(f"{S['id']}_seg_{key}_{k}", (cx - a, cy - b, a0 - k * box_h), (cx + a, cy + b, a1 - k * box_h), mats[col])
                S["segs"].append({"key": key, "box": k, "z0": a0 - k * box_h, "z1": a1 - k * box_h, "obj": ob})
                S["objs"].append(ob)
        c = c1
    for w in kit.back_walls(box_h, direction, centre=S["centres"][0]):
        w.name = f"{S['id']}_{w.name}"
        S["objs"].append(w)
    # signboard past the last box
    t1, w1, _ = kit.text_object(f"{S['id']}_sign_text", S["sign"][0], "CENTER", "CENTER")
    t2, w2, _ = kit.text_object(f"{S['id']}_sign_text2", S["sign"][1], "CENTER", "CENTER")
    bw = max(w1 * SIGN_EM, w2 * SIGN_EM2) + 3.2
    bh = 0.75 * SIGN_EM + 0.75 * SIGN_EM2 + 0.45 * SIGN_EM + 2.4
    sx = X0 + (S["n"] - 1) * PITCH + 2 * a + 3.0 + bw / 2
    centre = Vector((sx, Y0 + Y_BILL - 1.0, 3.0 + bh / 2))
    bm = kit.material(f"{S['id']}_sign_board", "#323843", rough=0.75)
    fr = kit.material(f"{S['id']}_sign_frame", "#5b636d", rough=0.5, spec=0.4)
    e = 0.32
    parts = [kit.cuboid(f"{S['id']}_sign_board", (-bw / 2, -0.25, -bh / 2), (bw / 2, 0.25, bh / 2), bm),
             kit.cuboid(f"{S['id']}_sign_ft", (-bw / 2, -0.33, bh / 2 - e), (bw / 2, -0.25, bh / 2), fr),
             kit.cuboid(f"{S['id']}_sign_fb", (-bw / 2, -0.33, -bh / 2), (bw / 2, -0.25, -bh / 2 + e), fr),
             kit.cuboid(f"{S['id']}_sign_fl", (-bw / 2, -0.33, -bh / 2 + e), (-bw / 2 + e, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{S['id']}_sign_fr", (bw / 2 - e, -0.33, -bh / 2 + e), (bw / 2, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{S['id']}_sign_post", (-0.45, -0.2, -bh / 2 - 3.0), (0.45, 0.2, -bh / 2), fr)]
    rot = Euler((0, 0, math.radians(AZIMUTH)))
    for p in parts:
        p.location, p.rotation_euler = centre, rot
    gap_l = 0.45 * SIGN_EM
    for t, em, m, dz in ((t1, SIGN_EM, ink_sign, (0.75 * SIGN_EM2 + gap_l) / 2), (t2, SIGN_EM2, ink_sign2, -(0.75 * SIGN_EM + gap_l) / 2)):
        t.data.size, t.data.extrude = em, 0.1
        off = Vector((0, -0.35, dz))
        off.rotate(rot)
        t.location = centre + off
        t.rotation_euler = (math.radians(90), 0, math.radians(AZIMUTH))
        t.data.materials.append(m)
    S["sign_objs"], S["sign_texts"] = parts, [t1, t2]
    S["objs"] += parts
    # the model: 64 thin plates, layer 33 highlighted (a locator, not to scale)
    S["plates"] = []
    for i in range(64):
        z = i * (PLATE_T + PLATE_GAP)
        m = plate33_m if i == 32 else plate_m
        S["plates"].append(kit.cuboid(f"{S['id']}_plate_{i + 1}", (X0 + TOWER_X0, Y0 - PLATE / 2, z), (X0 + TOWER_X0 + PLATE, Y0 + PLATE / 2, z + PLATE_T), m))
    S["z33"] = 32 * (PLATE_T + PLATE_GAP) + PLATE_T / 2
    S["objs"] += S["plates"]
    # layer 33's kept memory, at the shared MiB scale
    S["detail"], x = [], X0 + DETAIL_X0
    groups = list(kept.items()) if si == 0 else list(kept_ck.items())
    for gi, (name, mib) in enumerate(groups):
        L = mib / DETAIL_MIB_PER_UNIT
        m = tint_m[gi] if si == 0 else tint_m[1]
        ob = kit.cuboid(f"{S['id']}_detail_{gi}", (x, Y0 - BAR_D / 2, 0), (x + L, Y0 + BAR_D / 2, BAR_H), m)
        S["detail"].append({"name": name, "mib": mib, "x0": x, "x1": x + L, "obj": ob})
        x += L
    S["objs"] += [d["obj"] for d in S["detail"]]

for S in SIDES:                                       # each diorama's base fits its own content
    lo, hi = kit.world_bbox([o for o in S["objs"]])
    lo.z = 0.0
    S["base"], S["base_info"] = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), seed=11 + 7 * SIDES.index(S), dressing=False, drop=12.0, thickness=0.8)

# ---------------------------------------------------------------- labels
# Lines the two bills share (frozen weights, adapter) are labelled once, on the left; the right labels what differs.
labels, kinds = [], {}


def add(key, text, anchor, kind, S, side="R", sub=None, extra=None):
    labels.append(kit.Label(key, text, anchor, side, sub=sub))
    kinds[key] = (kind, S, extra)


for S in SIDES:
    segs, sid = S["segs"], S["id"]
    front = lambda s: (S["centres"][s["box"]][0], S["centres"][s["box"]][1] - b)
    w0 = next(s for s in segs if s["key"] == "weights")
    adl = [s for s in segs if s["key"].startswith("adapter")]
    acts = [s for s in segs if s["key"] == "activations"]
    full = [s for s in acts if s["z1"] - s["z0"] > box_h - 1e-6]
    loss_last = [s for s in segs if s["key"] == "loss" and s["box"] == S["n"] - 1][0]
    if S is SIDES[0]:                                  # left of our card
        lc, _, _ = kit.silhouette_corners(direction, centre=S["centres"][0])
        add(f"{sid}_weights", S["text"]["weights"], (lc.x, lc.y, (w0["z0"] + w0["z1"]) / 2), "left", S, side="L")
        add(f"{sid}_adapter", S["text"]["adapter"], (lc.x, lc.y, (adl[0]["z0"] + adl[-1]["z1"]) / 2), "left", S, side="L")
    if full:
        s0 = full[len(full) // 2]
        add(f"{sid}_activations", S["text"]["activations"], (*S["centres"][s0["box"]], s0["z1"]), "up", S, side="L")
    else:
        add(f"{sid}_activations", S["text"]["activations"], (*front(acts[0]), (acts[0]["z0"] + acts[0]["z1"]) / 2), "below_bill", S, extra=("side", acts[0]))
    if S is SIDES[0]:                                  # loss is the same on both sides: labelled once
        add(f"{sid}_loss", S["text"]["loss"], (*S["centres"][loss_last["box"]], loss_last["z1"]), "up", S, side="L")
    if S is SIDES[0]:
        add(f"{sid}_tower", DETAIL_TXT["tower"], (S["X0"] + TOWER_X0, S["Y0"] - PLATE / 2, S["z33"]), "tower", S, side="L")
        for gi, d in enumerate(S["detail"]):
            add(f"{sid}_seg{gi}", DETAIL_TXT[f"seg_{d['name']}"], ((d["x0"] + d["x1"]) / 2, S["Y0"] - BAR_D / 2, BAR_H / 2), "down", S)
        add(f"{sid}_head", DETAIL_TXT["left_head"], (S["X0"] + DETAIL_X0, S["Y0"] - BAR_D / 2, 0.0), "head", S)
    else:
        d = S["detail"][0]
        add(f"{sid}_head", DETAIL_TXT["right_head"], ((d["x0"] + d["x1"]) / 2, S["Y0"] - BAR_D / 2, BAR_H / 2), "head", S, sub=DETAIL_TXT["right_note"])
titles = []
for S in SIDES:
    objs, ws = [], []
    for j, line in enumerate(S["title"]):
        t, w, _ = kit.text_object(f"txt_title{j}_{S['id']}", line, "LEFT", "BOTTOM_BASELINE")
        objs.append(t)
        ws.append(w)
    titles.append({"side": S, "objs": objs, "w": ws})


def place(cam):
    em_y, sub_y = kit.EM * rx / ry, kit.SUB_EM * rx / ry
    lay = {}
    for lab in labels:
        p = kit.to_screen(scene, cam, lab.anchor)
        o = {"ax": p.x, "ay": p.y, "depth": p.z, "w": lab.w_em * kit.EM, "h": em_y, "below": 0.0}
        if lab.sub_obj:
            o["below"] = kit.SUB_GAP * em_y + lab.sub_h_em * kit.SUB_EM * rx / ry
            o["w"] = max(o["w"], lab.sub_w_em * kit.SUB_EM)
        lay[lab.key] = o
    for S in SIDES:
        mine = [l for l in labels if kinds[l.key][1] is S]
        # above the bill row: right-aligned flags rising to the right
        placed = []
        for l in sorted([l for l in mine if kinds[l.key][0] == "up"], key=lambda l: lay[l.key]["ax"]):
            o = lay[l.key]
            o["x"] = o["ax"] - 0.5 * kit.EM
            o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
            y = o["ay"] + 2.0 * em_y
            for q in placed:
                if q["x0"] - 1.5 * kit.EM < o["x1"] and o["x0"] < q["x1"] + 1.5 * kit.EM:
                    y = max(y, q["y"] + 1.9 * em_y + o["below"])
            o["y"], o["route"] = y, [(o["ax"], o["ay"]), (o["ax"], y + 0.35 * em_y)]
            placed.append(o)
        # left of our card: fanned, right-aligned in one column
        lefts = sorted([l for l in mine if kinds[l.key][0] == "left"], key=lambda l: -lay[l.key]["ay"])
        ys = [lay[l.key]["ay"] for l in lefts]
        for _ in range(200):
            for i in range(len(ys) - 1):
                if ys[i] - ys[i + 1] < 1.6 * em_y:
                    dd = (1.6 * em_y - (ys[i] - ys[i + 1])) / 2
                    ys[i] += dd
                    ys[i + 1] -= dd
        for l, y in zip(lefts, ys):
            o = lay[l.key]
            o["y"], o["x"] = y, o["ax"] - 2.2 * kit.EM
            o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
            end = o["x"] + 0.45 * kit.EM
            o["route"] = ([(o["ax"], o["ay"]), (o["ax"] - 0.8 * kit.EM, o["ay"]), (o["ax"] - 1.4 * kit.EM, y), (end, y)]
                          if abs(y - o["ay"]) > 0.002 else [(o["ax"], o["ay"]), (end, y)])
        # below the bill row: left-aligned flags, the rightmost leader highest
        bl = []
        for l in mine:
            kind, _, extra = kinds[l.key]
            if kind != "below_bill":
                continue
            mode, sg = extra
            o = lay[l.key]
            cx, cy = S["centres"][sg["box"]]
            o["lx"] = kit.to_screen(scene, cam, (cx + a + 1.5, cy - b, l.anchor.z)).x if mode == "side" else o["ax"]
            o["edge"] = kit.to_screen(scene, cam, (cx, cy - b, 0.0)).y
            bl.append((l, mode))
        bl.sort(key=lambda t: -lay[t[0].key]["lx"])
        y_prev = None
        near_depth = kit.to_screen(scene, cam, (S["X0"], S["base_info"]["y"][0], 0.0)).z - 2.0
        for l, mode in bl:
            o = lay[l.key]
            o["depth"] = near_depth                        # in front of the base, so nothing covers the text
            y = o["edge"] - 1.3 * em_y if y_prev is None else min(o["edge"] - 1.3 * em_y, y_prev - 1.75 * em_y)
            o["route"] = ([(o["ax"], o["ay"]), (o["lx"], o["ay"]), (o["lx"], y + 0.3 * em_y)] if mode == "side"
                          else [(o["ax"], o["ay"]), (o["ax"], y + 0.3 * em_y)])
            o["y"], o["x"] = y, o["lx"] + 0.45 * kit.EM
            o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
            y_prev = y
        # tower: left of the plates
        for l in [l for l in mine if kinds[l.key][0] == "tower"]:
            o = lay[l.key]
            o["y"], o["x"] = o["ay"], o["ax"] - 2.0 * kit.EM
            o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
            o["route"] = [(o["ax"], o["ay"]), (o["x"] + 0.45 * kit.EM, o["y"])]
        # below the detail bar: left-aligned flags, the rightmost highest
        downs = sorted([l for l in mine if kinds[l.key][0] == "down"], key=lambda l: -lay[l.key]["ax"])
        y_prev = None
        for l in downs:
            o = lay[l.key]
            edge = kit.to_screen(scene, cam, (lay[l.key]["ax"] and l.anchor.x, S["base_info"]["y"][0], S["base_info"]["top"] - S["base_info"]["thickness"])).y
            y = edge - 1.2 * em_y if y_prev is None else min(edge - 1.2 * em_y, y_prev - 1.75 * em_y)
            o["y"], o["x"] = y, o["ax"] + 0.45 * kit.EM
            o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
            o["route"] = [(o["ax"], o["ay"]), (o["ax"], y + 0.3 * em_y)]
            y_prev = y
        # the detail's caption: under its labels (left) or under the bar with a leader up to it (right)
        for l in [l for l in mine if kinds[l.key][0] == "head"]:
            o = lay[l.key]
            bar_x0 = kit.to_screen(scene, cam, (S["X0"] + DETAIL_X0, S["Y0"] - BAR_D / 2, 0.0)).x
            edge = kit.to_screen(scene, cam, (S["X0"] + DETAIL_X0, S["base_info"]["y"][0], S["base_info"]["top"] - S["base_info"]["thickness"])).y
            o["y"] = (y_prev - 1.9 * em_y) if (S is SIDES[0] and y_prev is not None) else edge - 1.3 * em_y
            o["x"] = bar_x0 if S is SIDES[0] else o["ax"] + 0.45 * kit.EM
            o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
            o["route"] = ([(o["ax"], o["ay"]), (o["ax"], o["ay"] + 0.001)] if S is SIDES[0]
                          else [(o["ax"], o["ay"]), (o["ax"], o["y"] + 0.3 * em_y)])
    for o in lay.values():
        o["sub_y"] = o["y"] - o["h"] / 2 - kit.SUB_GAP * em_y
    tl = []
    geo_top = max(kit.to_screen(scene, cam, (cx + dx, cy + dy, box_h)).y for S in SIDES for cx, cy in S["centres"]
                  for dx in (-a, a) for dy in (-b, b))
    top = max([o["y"] + o["h"] / 2 for o in lay.values()] + [geo_top])
    for t in titles:
        S = t["side"]
        mine = [lay[l.key] for l in labels if kinds[l.key][1] is S]
        gx = min(kit.to_screen(scene, cam, (cx - a, cy - b, 0)).x for cx, cy in S["centres"])
        x0 = min([o["x0"] for o in mine] + [gx])
        ys = [top + 1.2 * em_y]
        if len(t["w"]) > 1:
            ys = [top + 1.2 * em_y + 1.05 * sub_y + 0.3 * em_y, top + 1.2 * em_y]
        w = max([t["w"][0] * kit.EM] + [x * kit.SUB_EM for x in t["w"][1:]])
        tl.append({"t": t, "x": x0, "y": ys, "rect": [x0, x0 + w, ys[-1] - 0.25 * (sub_y if len(ys) > 1 else em_y), ys[0] + 0.74 * em_y]})
    return lay, tl


def rects(lay, tl):
    out = {k: [o["x0"], o["x1"], o["y"] - o["h"] / 2 - o["below"], o["y"] + o["h"] / 2] for k, o in lay.items()}
    for t in tl:
        out[f"title_{t['t']['side']['id']}"] = t["rect"]
    return out


# ---------------------------------------------------------------- camera
cam = kit.make_camera(scene, LENS)
geo = [o for S in SIDES for o in S["objs"] + S["base"]]
pts = kit.mesh_points(geo)
lo_all = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi_all = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
target, dist = (lo_all + hi_all) / 2, 1.6 * (hi_all - lo_all).length
for _ in range(16):
    kit.aim(cam, target, dist, direction)
    sp = [kit.to_screen(scene, cam, p) for p in pts]
    gx0, gx1, gy0, gy1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    lay, tl = place(cam)
    rr = list(rects(lay, tl).values())
    x0, x1 = min([gx0] + [r[0] for r in rr]), max([gx1] + [r[1] for r in rr])
    y0, y1 = min([gy0] + [r[2] for r in rr]), max([gy1] + [r[3] for r in rr])
    gw, gh = gx1 - gx0, gy1 - gy0
    z = min((0.94 - ((x1 - x0) - gw)) / gw, (0.92 - ((y1 - y0) - gh)) / gh)
    fw_, fh_ = kit.frame_size(scene, cam, dist)
    Rv = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    Uv = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    target = target + Rv * ((x0 + x1) / 2 - 0.5) * fw_ + Uv * ((y0 + y1) / 2 - 0.5) * fh_
    if abs(z - 1) < 0.001 and abs((x0 + x1) / 2 - 0.5) < 0.001 and abs((y0 + y1) / 2 - 0.5) < 0.001:
        break
    dist /= z
kit.aim(cam, target, dist, direction)
lay, tl = place(cam)

# ---------------------------------------------------------------- frames, zoom lines, text
d_box = kit.to_screen(scene, cam, (SIDES[0]["centres"][0][0], SIDES[0]["centres"][0][1], box_h / 2)).z
fw, _ = kit.frame_size(scene, cam, d_box)
s_ = kit.STRUT * fw * 0.8 / 2
lead = kit.glow_material("lead", kit.LOOK["leader"], 1.0)
for S in SIDES:
    objs = kit.box_frame(box_h, kit.STRUT * fw, kit.RIM * fw, centre=S["centres"][0])
    for k in range(1, S["n"]):
        cx, cy = S["centres"][k]
        for i, p in enumerate(kit.box_corners(centre=(cx, cy))):
            objs.append(kit.cuboid(f"ghost_{k}_{i}", (p.x - s_, p.y - s_, 0), (p.x + s_, p.y + s_, box_h), ghost))
        for nm, l_, h_ in (("-y", (cx - a - s_, cy - b - s_, box_h - s_), (cx + a + s_, cy - b + s_, box_h + s_)),
                           ("+y", (cx - a - s_, cy + b - s_, box_h - s_), (cx + a + s_, cy + b + s_, box_h + s_)),
                           ("-x", (cx - a - s_, cy - b + s_, box_h - s_), (cx - a + s_, cy + b - s_, box_h + s_)),
                           ("+x", (cx + a - s_, cy - b + s_, box_h - s_), (cx + a + s_, cy + b - s_, box_h + s_))):
            objs.append(kit.cuboid(f"ghost_{k}_top{nm}", l_, h_, ghost))
    for ob in objs:
        ob.name = f"{S['id']}_{ob.name}"
    # zoom: from plate 33's front-right edge to the detail bar's start
    z33 = S["z33"]
    xd = S["X0"] + DETAIL_X0
    for nm, z_from, z_to in (("top", z33 + PLATE_T / 2, BAR_H), ("bot", z33 - PLATE_T / 2, 0.0)):
        kit.polyline(f"zoom_{S['id']}_{nm}", [Vector((S["X0"] + TOWER_X0 + PLATE, S["Y0"] - PLATE / 2, z_from)), Vector((xd, S["Y0"] - BAR_D / 2, z_to))],
                     kit.LINE * fw / 2, lead)
bpy.context.view_layer.update()
kit.build_labels(scene, cam, labels, lay, lift=kit.RIM * fw)
ink, ink2 = kit.glow_material("ink_t", kit.LOOK["ink"], 1.0), kit.glow_material("ink2_t", kit.LOOK["ink2"], 1.0)
d_text = kit.to_screen(scene, cam, (SIDES[0]["X0"], SIDES[0]["base_info"]["y"][0], 0)).z - 2.0
for t in tl:
    for j, ob in enumerate(t["t"]["objs"]):
        kit.place_on_screen(scene, cam, ob, t["x"], t["y"][j], d_text, kit.EM if j == 0 else kit.SUB_EM, ink if j == 0 else ink2)
kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)   # as fig 3

# ---------------------------------------------------------------- checks and layout
rr = rects(lay, tl)
names = list(rr)
overlaps = [[p, q] for i, p in enumerate(names) for q in names[i + 1:]
            if rr[p][0] < rr[q][1] and rr[q][0] < rr[p][1] and rr[p][2] < rr[q][3] and rr[q][2] < rr[p][3]]
leader_cross = set()
for k, o in lay.items():
    for (x0_, y0_), (x1_, y1_) in zip(o["route"], o["route"][1:]):
        for f in [i / 40 for i in range(1, 40)]:
            x_, y_ = x0_ + f * (x1_ - x0_), y0_ + f * (y1_ - y0_)
            for n, r in rr.items():
                if n != k and r[0] < x_ < r[1] and r[2] < y_ < r[3]:
                    leader_cross.add((k, n))
inside = all(0.01 < r[0] and r[1] < 0.99 and 0.01 < r[2] and r[3] < 0.99 for r in rr.values())
dg = bpy.context.evaluated_depsgraph_get()
origin = cam.matrix_world.translation
hidden = set()
for n, r in rr.items():
    for fx in (0.05, 0.5, 0.95):
        for fy in (0.25, 0.75):
            p = kit.to_world(scene, cam, r[0] + fx * (r[1] - r[0]), r[2] + fy * (r[3] - r[2]), lay[n]["depth"] - kit.RIM * fw if n in lay else d_text)
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(("label_", "leader_", "dot_", "txt_")):
                hidden.add((n, ob.name))
data_hidden = set()                                    # the bills' boxes and the detail bars must not be hidden
for S in SIDES:
    targets = [(f"{S['id']}_seg", f"{S['id']}:box{k + 1}", Vector((cx, cy - b, z))) for k, (cx, cy) in enumerate(S["centres"]) for z in (0.5, box_h / 2)]
    targets += [(f"{S['id']}_detail", f"{S['id']}:detail{gi}", Vector(((d["x0"] + d["x1"]) / 2, S["Y0"] - BAR_D / 2, BAR_H / 2))) for gi, d in enumerate(S["detail"])]
    for own, nm, p in targets:
        v = p - origin
        hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.999)
        if hit and not ob.name.startswith((own, "dot_", "leader_")):      # anchor dots sit on their own bars
            data_hidden.add((nm, ob.name))
sides_out = []
for S in SIDES:
    lines_out = {}
    for key in ("weights", "adapter", "activations", "loss"):
        h = sum(kit.object_height(s["obj"]) for s in S["segs"] if s["key"] == key or (key == "adapter" and s["key"].startswith("adapter")))
        lines_out[key] = {"gib": S["lines"][key]["gib"], "height_units": round(h, 6), "units_per_gib": h / S["lines"][key]["gib"]}
    adapter_parts = {k: round(sum(kit.object_height(s["obj"]) for s in S["segs"] if s["key"] == k), 5) for k in ("adapter_w", "adapter_g", "adapter_o")}
    det = [{"group": d["name"], "mib": d["mib"], "length_units": round(kit.world_bbox([d["obj"]])[1].x - kit.world_bbox([d["obj"]])[0].x, 5)} for d in S["detail"]]
    for d in det:
        d["mib_per_unit"] = d["mib"] / d["length_units"]
    sides_out.append({"side": S["id"], "cards": S["n"], "sign": S["sign"], "total_gib_data": S["row"]["total_gib"],
                      "sum_of_lines_units": round(sum(v["height_units"] for v in lines_out.values()), 4), "lines": lines_out,
                      "adapter_parts_units": adapter_parts, "detail": det, "detail_total_units": round(sum(d["length_units"] for d in det), 4)})
layout = {
    "figure": "checkpointing",
    "scales": {"bills_units_per_gib": GIB, "detail_mib_per_unit": DETAIL_MIB_PER_UNIT, "layer_plates": "64 plates, a locator, not to scale"},
    "sides": sides_out,
    "max_deviation_units_per_gib": max(abs(v["units_per_gib"] - 1.0) for s in sides_out for v in s["lines"].values()),
    "max_deviation_detail_mib_per_unit": max(abs(d["mib_per_unit"] - DETAIL_MIB_PER_UNIT) for s in sides_out for d in s["detail"]),
    "detail_ratio": round(sides_out[0]["detail_total_units"] / sides_out[1]["detail_total_units"], 2),
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rr.items()},
    "text_overlaps": overlaps, "leaders_crossing_text": sorted(leader_cross), "text_hidden": sorted(hidden),
    "text_inside_picture": inside, "data_hidden": sorted(data_hidden),
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_gib", "max_deviation_detail_mib_per_unit", "detail_ratio",
                                                 "text_overlaps", "leaders_crossing_text", "text_hidden", "text_inside_picture", "data_hidden")}))
print("SIDES", [(s["side"], s["cards"], s["sum_of_lines_units"], s["adapter_parts_units"], s["detail_total_units"]) for s in sides_out])

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout)
    print("RENDER", round(secs, 1), "s")
