"""Figure: two naive full fine-tune bills on one base. Back row: the BF16 bill (14 cards). Front row: a thought
experiment, every number training stores at the GGUF's 5.24 bits except the loss (5 cards).

One floating base, both rows starting on the same line, each a row of 24 GiB card boxes filled in order with its
bill (1 unit = 1 GiB, the VRAM figure's box). Our card (first box) solid with its rim, the others ghosted. A
signboard at each row's end gives the card count (ceil(total / card), from the data) and the total. Row 1's labels
on its far side (above), row 2's on its near side (below). Data: charts/data/train_bill_bf16_3000.json and
train_bill_q4_3000.json, used as given.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/train_bill_pair.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/train_bill_pair_draft.png] [--no-render]
"""
import argparse, json, math, os, re, sys, time
import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="900x600")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=os.path.join(HERE, "out", "train_bill_pair_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "train_bill_pair.layout.json"))
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX
GIB = kit.MIB_PER_GIB * kit.UNITS_PER_MIB          # units per GiB: 1.0


def half_up(x):
    return int(math.floor(x + 0.5))


ROWS = [
    {"id": "bf16", "data": "train_bill_bf16_3000.json", "side": "far",
     "title": ["Full fine-tune in BF16 (as released)"], "keep_sub": True},
    {"id": "q4", "data": "train_bill_q4_3000.json", "side": "near",
     "title": ["Pretend: training entirely in the GGUF's 4-bit format", "5.24 bits per number; the loss kept in full precision"],
     "keep_sub": False},                            # AdamW's note is given once, on row 1
]
for R in ROWS:
    R["d"] = json.load(open(os.path.join(HERE, "data", R["data"])))
    R["lines"] = R["d"]["lines_bottom_to_top"]
    R["card"] = R["d"]["card_total_gib"]
    R["n"] = math.ceil(R["d"]["total_gib"] / R["card"])                     # cards, from the data
    R["sign"] = [f"{R['n']} × RTX 4090", f"≈ {half_up(R['d']['total_gib'])} GiB"]
assert [R["n"] for R in ROWS] == [14, 5] and ROWS[0]["card"] == ROWS[1]["card"]
assert [L["key"] for L in ROWS[0]["lines"]] == [L["key"] for L in ROWS[1]["lines"]]
assert [R["sign"] for R in ROWS] == [["14 × RTX 4090", "≈ 332 GiB"], ["5 × RTX 4090", "≈ 115 GiB"]]   # v2 data
card_gib = ROWS[0]["card"]
box_h = card_gib * GIB


def label_parts(L, keep_sub=True):
    m = re.match(r"(.*) \((AdamW.*)\)$", L["label"])
    name, sub = (m.group(1), [m.group(2)]) if m else (L["label"], None)
    value = f"≈ {half_up(L['gib'])} GiB" if L.get("approximate") else f"{L['gib']:.1f} GiB"
    return f"{name} {value}", (sub if keep_sub else None)


EXPECT = {"bf16": ["Qwen3.8-27B weights (BF16) 50.1 GiB", "gradients 50.1 GiB", "optimizer state 100.2 GiB",
                   "activations, 3,000 tokens ≈ 122 GiB", "loss, 3,000 tokens 9.4 GiB"],
          "q4": ["Qwen3.8-27B weights (Q4 GGUF) 16.4 GiB", "gradients 16.4 GiB", "optimizer state 32.8 GiB",
                 "activations, 3,000 tokens ≈ 40 GiB", "loss, 3,000 tokens 9.4 GiB"]}
for R in ROWS:
    assert [label_parts(L)[0] for L in R["lines"]] == EXPECT[R["id"]], [label_parts(L)[0] for L in R["lines"]]

ELEVATION, AZIMUTH, LENS = 30.0, -16.0, 80.0         # nearly level rows, so their lengths compare directly
PITCH = kit.FOOTPRINT[0] + 3.0
SIGN_EM, SIGN_EM2 = 6.4, 4.8                          # sign letters, world units (the sign is part of the scene)
a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
direction = kit.view_direction(ELEVATION, AZIMUTH)
# back row far enough behind that its boxes clear the front row's tops on screen (same x): with "away" = depth
# along the view, screen height ~ cos(el) z + sin(el) away
away_y = -direction.y / math.hypot(direction.x, direction.y)
Y_BACK = 2 * b + (box_h * math.cos(math.radians(ELEVATION)) + 1.5) / (math.sin(math.radians(ELEVATION)) * away_y)
ROWS[0]["y"], ROWS[1]["y"] = Y_BACK, 0.0

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
mats = {L["key"]: kit.material(L["key"], kit.COLOURS[L["key"]], emit=0.10, rough=0.85, spec=0.12) for L in ROWS[0]["lines"]}
ghost = kit.material("ghost", "#4d535c", rough=0.6, spec=0.2)
ink_sign = kit.material("sign_ink", "#dcdcdc", rough=0.6, emit=0.2, spec=0.3)
ink_sign2 = kit.material("sign_ink2", "#a9a9a9", rough=0.6, emit=0.2, spec=0.3)
volumes = []
for R in ROWS:
    R["centres"] = [(k * PITCH + a, R["y"]) for k in range(R["n"])]
    R["segs"], c = [], 0.0
    for L in R["lines"]:
        c0, c1 = c, c + L["gib"] * GIB
        for k in range(R["n"]):
            a0, a1 = max(c0, k * box_h), min(c1, (k + 1) * box_h)
            if a1 > a0 + 1e-9:
                cx, cy = R["centres"][k]
                ob = kit.cuboid(f"{R['id']}_seg_{L['key']}_{k}", (cx - a, cy - b, a0 - k * box_h), (cx + a, cy + b, a1 - k * box_h), mats[L["key"]])
                R["segs"].append({"key": L["key"], "box": k, "z0": a0 - k * box_h, "z1": a1 - k * box_h, "obj": ob})
                volumes.append(ob)
        c = c1
    walls = kit.back_walls(box_h, direction, centre=R["centres"][0])
    for w in walls:
        w.name = f"{R['id']}_{w.name}"
    volumes += walls
    # signboard on a post past the row's last box (row 2: one slot further, leaving room for its loss leader)
    t1, w1, _ = kit.text_object(f"{R['id']}_sign_text", R["sign"][0], "CENTER", "CENTER")
    t2, w2, _ = kit.text_object(f"{R['id']}_sign_text2", R["sign"][1], "CENTER", "CENTER")
    bw = max(w1 * SIGN_EM, w2 * SIGN_EM2) + 3.2
    bh = 0.75 * SIGN_EM + 0.75 * SIGN_EM2 + 0.45 * SIGN_EM + 2.4
    post_h = 3.0
    sx = (R["n"] - 1) * PITCH + 2 * a + (3.0 if R["side"] == "far" else 9.0) + bw / 2
    R["sign_centre"] = Vector((sx, R["y"] - 1.0, post_h + bh / 2))
    bm = kit.material(f"{R['id']}_sign_board", "#323843", rough=0.75)
    fr = kit.material(f"{R['id']}_sign_frame", "#5b636d", rough=0.5, spec=0.4)
    e = 0.32
    parts = [kit.cuboid(f"{R['id']}_sign_board", (-bw / 2, -0.25, -bh / 2), (bw / 2, 0.25, bh / 2), bm),
             kit.cuboid(f"{R['id']}_sign_ft", (-bw / 2, -0.33, bh / 2 - e), (bw / 2, -0.25, bh / 2), fr),
             kit.cuboid(f"{R['id']}_sign_fb", (-bw / 2, -0.33, -bh / 2), (bw / 2, -0.25, -bh / 2 + e), fr),
             kit.cuboid(f"{R['id']}_sign_fl", (-bw / 2, -0.33, -bh / 2 + e), (-bw / 2 + e, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{R['id']}_sign_fr", (bw / 2 - e, -0.33, -bh / 2 + e), (bw / 2, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{R['id']}_sign_post", (-0.45, -0.2, -bh / 2 - post_h), (0.45, 0.2, -bh / 2), fr)]
    rot = Euler((0, 0, math.radians(AZIMUTH)))                 # turned to face the camera
    for p in parts:
        p.location, p.rotation_euler = R["sign_centre"], rot
    gap_l = 0.45 * SIGN_EM
    for t, em, mat, dz in ((t1, SIGN_EM, ink_sign, (0.75 * SIGN_EM2 + gap_l) / 2),
                           (t2, SIGN_EM2, ink_sign2, -(0.75 * SIGN_EM + gap_l) / 2)):
        t.data.size, t.data.extrude = em, 0.1
        off = Vector((0, -0.25 - 0.1, dz))
        off.rotate(rot)
        t.location = R["sign_centre"] + off
        t.rotation_euler = (math.radians(90), 0, math.radians(AZIMUTH))
        t.data.materials.append(mat)
    R["sign_objs"], R["sign_texts"] = parts, [t1, t2]
    volumes += parts

lo, hi = kit.world_bbox(volumes)
lo.z = 0.0
base, base_info = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), dressing=False, drop=14.0, thickness=0.8)

# ---------------------------------------------------------------- labels
far, near = ROWS
labels, kinds = [], {}
FAR_LEFT_ALIGNED = set()                              # far-side flags that run right from their leader
for R in ROWS:
    for L in R["lines"]:
        text, sub = label_parts(L, R["keep_sub"])
        segs = [s for s in R["segs"] if s["key"] == L["key"]]
        key = f"{R['id']}_{L['key']}"
        if R["side"] == "far":                                       # from above: a box the line fills, else its piece
            full = [s for s in segs if s["z1"] - s["z0"] > box_h - 1e-6]
            s = segs[0] if L["key"] == "weights" else (full[-1] if full else max(segs, key=lambda s: s["z1"] - s["z0"]))
            cx, cy = R["centres"][s["box"]]
            labels.append(kit.Label(key, text, (cx, cy, s["z1"]), "R" if L["key"] == "weights" else "L", sub=sub))
            kinds[key] = ("far_first" if L["key"] == "weights" else "far", s["box"])
            FAR_LEFT_ALIGNED.add(key) if L["key"] in ("weights", "gradients") else None
        else:                                                        # from below: a piece standing on the box floor
            ground = [s for s in segs if s["z0"] < 1e-6]
            s = ground[0] if ground else segs[0]
            cx, cy = R["centres"][s["box"]]
            labels.append(kit.Label(key, text, (cx, cy - b, (s["z0"] + s["z1"]) / 2), "R", sub=sub))
            kinds[key] = ("near" if ground else "near_side", s["box"])
lc0, _, _ = kit.silhouette_corners(direction, centre=far["centres"][0])
labels.append(kit.Label("limit", "RTX 4090: 24 GiB", (lc0.x, lc0.y, box_h), "L"))
kinds["limit"] = ("left", 0)
titles = []
for i, R in enumerate(ROWS):
    t, w, _ = kit.text_object(f"txt_title_{R['id']}", R["title"][0], "LEFT", "BOTTOM_BASELINE")
    objs, ws = [t], [w]
    if len(R["title"]) > 1:
        t2, w2, _ = kit.text_object(f"txt_title2_{R['id']}", R["title"][1], "LEFT", "BOTTOM_BASELINE")
        objs.append(t2)
        ws.append(w2)
    titles.append({"row": R, "objs": objs, "w": ws})


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
    # far side: flags rising to the right, each above every placed flag it overlaps (right-aligned, except the
    # first lines', which run right from their leader so they stay clear of the leaders to their left)
    ups = sorted([l for l in labels if kinds[l.key][0] == "far"], key=lambda l: lay[l.key]["ax"])
    placed = []
    for lab in ups:
        o = lay[lab.key]
        if lab.key in FAR_LEFT_ALIGNED:
            o["x"] = o["ax"] + 0.5 * kit.EM
            o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
        else:
            o["x"] = o["ax"] - 0.5 * kit.EM
            o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
        y = o["ay"] + 2.0 * em_y
        for q in placed:
            if q["x0"] < o["x1"] and o["x0"] < q["x1"]:
                y = max(y, q["y"] + 1.9 * em_y + o["below"])
        o["y"] = y
        o["route"] = [(o["ax"], o["ay"]), (o["ax"], y + 0.35 * em_y)]
        placed.append(o)
    first = next(l for l in labels if kinds[l.key][0] == "far_first")
    o = lay[first.key]
    o["x"] = o["ax"] + 0.5 * kit.EM
    o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
    y = o["ay"] + 2.0 * em_y
    for lab in ups:
        q = lay[lab.key]
        if q["x0"] < o["x1"] and o["x0"] < q["x1"]:
            y = max(y, q["y"] + 1.9 * em_y)
    o["y"], o["route"] = y, [(o["ax"], o["ay"]), (o["ax"], y + 0.35 * em_y)]
    # near side: left-aligned flags under the base, the rightmost highest, each further left one step lower
    downs = sorted([l for l in labels if kinds[l.key][0] in ("near", "near_side")], key=lambda l: -kinds[l.key][1] - (0.5 if kinds[l.key][0] == "near_side" else 0))
    y_prev = None
    for lab in downs:
        o = lay[lab.key]
        k = kinds[lab.key][1]
        cx, cy = near["centres"][k]
        edge = kit.to_screen(scene, cam, (cx, base_info["y"][0], base_info["top"] - base_info["thickness"])).y
        y = edge - 1.25 * em_y
        if y_prev is not None:
            y = min(y, y_prev - 1.9 * em_y - o["below"])
        if kinds[lab.key][0] == "near_side":                       # out past the box's right edge, then down
            px = kit.to_screen(scene, cam, (cx + a + 2.2, cy - b, lab.anchor.z)).x
            o["route"] = [(o["ax"], o["ay"]), (px, o["ay"]), (px, y + 0.3 * em_y)]
            lx = px
        else:
            o["route"] = [(o["ax"], o["ay"]), (o["ax"], y + 0.3 * em_y)]
            lx = o["ax"]
        o["y"], o["x"] = y, lx + 0.45 * kit.EM
        o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
        y_prev = y
    # limit: left of row 1's card
    o = lay["limit"]
    o["y"], o["x"] = o["ay"], o["ax"] - 2.2 * kit.EM
    o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
    o["route"] = [(o["ax"], o["ay"]), (o["x"] + 0.45 * kit.EM, o["y"])]
    for o in lay.values():
        o["sub_y"] = o["y"] - o["h"] / 2 - kit.SUB_GAP * em_y
    # titles: row 1 above everything at the top left, row 2 below everything at the bottom left
    tl = []
    top_y = max(o["y"] + o["h"] / 2 for k, o in lay.items() if kinds[k][0] in ("far", "far_first"))
    bot_y = min(o["y"] - o["h"] / 2 - o["below"] for k, o in lay.items() if kinds[k][0] in ("near", "near_side"))
    x_left = min(o["x0"] for o in lay.values())
    for t in titles:
        R = t["row"]
        w = max([t["w"][0] * kit.EM] + ([t["w"][1] * kit.SUB_EM] if len(t["w"]) > 1 else []))
        if R["side"] == "far":
            y1 = top_y + 0.9 * em_y
            ys = [y1]
            rect = [x_left, x_left + w, y1 - 0.25 * em_y, y1 + 0.74 * em_y]
        else:
            y1 = bot_y - 1.15 * em_y
            ys = [y1, y1 - 0.30 * em_y - 0.95 * sub_y]
            rect = [x_left, x_left + w, ys[-1] - 0.25 * sub_y, y1 + 0.74 * em_y]
        tl.append({"t": t, "x": x_left, "y": ys, "rect": rect})
    return lay, tl


def rects(lay, tl):
    out = {k: [o["x0"], o["x1"], o["y"] - o["h"] / 2 - o["below"], o["y"] + o["h"] / 2] for k, o in lay.items()}
    for t in tl:
        out[f"title_{t['t']['row']['id']}"] = t["rect"]
    return out


# ---------------------------------------------------------------- camera: everything (geometry and text) in frame
cam = kit.make_camera(scene, LENS)
pts = kit.mesh_points(volumes + base)
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
    z = min((0.93 - ((x1 - x0) - gw)) / gw, (0.92 - ((y1 - y0) - gh)) / gh)
    fw_, fh_ = kit.frame_size(scene, cam, dist)
    Rv = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    Uv = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    target = target + Rv * ((x0 + x1) / 2 - 0.5) * fw_ + Uv * ((y0 + y1) / 2 - 0.5) * fh_
    if abs(z - 1) < 0.001 and abs((x0 + x1) / 2 - 0.5) < 0.001 and abs((y0 + y1) / 2 - 0.5) < 0.001:
        break
    dist /= z
kit.aim(cam, target, dist, direction)
lay, tl = place(cam)

# ---------------------------------------------------------------- what is sized on screen: frames, text
d_box = kit.to_screen(scene, cam, (near["centres"][0][0], 0, box_h / 2)).z
fw, _ = kit.frame_size(scene, cam, d_box)
for R in ROWS:
    objs = kit.box_frame(box_h, kit.STRUT * fw, kit.RIM * fw, centre=R["centres"][0])       # our card: frame and rim
    s_ = kit.STRUT * fw * 0.8 / 2
    for k in range(1, R["n"]):
        cx, cy = R["centres"][k]
        for i, p in enumerate(kit.box_corners(centre=(cx, cy))):
            objs.append(kit.cuboid(f"ghost_{k}_{i}", (p.x - s_, p.y - s_, 0), (p.x + s_, p.y + s_, box_h), ghost))
        for nm, l_, h_ in (("-y", (cx - a - s_, cy - b - s_, box_h - s_), (cx + a + s_, cy - b + s_, box_h + s_)),
                           ("+y", (cx - a - s_, cy + b - s_, box_h - s_), (cx + a + s_, cy + b + s_, box_h + s_)),
                           ("-x", (cx - a - s_, cy - b + s_, box_h - s_), (cx - a + s_, cy + b - s_, box_h + s_)),
                           ("+x", (cx + a - s_, cy - b + s_, box_h - s_), (cx + a + s_, cy + b - s_, box_h + s_))):
            objs.append(kit.cuboid(f"ghost_{k}_top{nm}", l_, h_, ghost))
    for ob in objs:
        ob.name = f"{R['id']}_{ob.name}"
bpy.context.view_layer.update()
kit.build_labels(scene, cam, labels, lay, lift=kit.RIM * fw)
ink, ink2 = kit.glow_material("ink_t", kit.LOOK["ink"], 1.0), kit.glow_material("ink2_t", kit.LOOK["ink2"], 1.0)
d_text = kit.to_screen(scene, cam, (near["centres"][0][0], base_info["y"][0], 0)).z - 2.0
for t in tl:
    kit.place_on_screen(scene, cam, t["t"]["objs"][0], t["x"], t["y"][0], d_text, kit.EM, ink)
    if len(t["t"]["objs"]) > 1:
        kit.place_on_screen(scene, cam, t["t"]["objs"][1], t["x"], t["y"][1], d_text, kit.SUB_EM, ink2)

kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)   # key from the camera's right, as draft b

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
            sxy = (r[0] + fx * (r[1] - r[0]), r[2] + fy * (r[3] - r[2]))
            p = kit.to_world(scene, cam, sxy[0], sxy[1], lay[n]["depth"] if n in lay else d_text)
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(("label_", "leader_", "dot_", "txt_")):
                hidden.add((n, ob.name))
signs = {}
for R in ROWS:
    sp = [kit.to_screen(scene, cam, p) for p in kit.mesh_points(R["sign_objs"])]
    sr = [min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)]
    t = R["sign_texts"][0]
    p0 = kit.to_screen(scene, cam, t.matrix_world.translation)
    p1 = kit.to_screen(scene, cam, t.matrix_world.translation + Vector((0, 0, 0.72 * SIGN_EM)))
    boxes_hidden = set()
    for RR in ROWS:
        for k, (cx, cy) in enumerate(RR["centres"]):
            for f in (0.1, 0.5, 0.9):
                for z in (0.3, box_h / 2, box_h - 0.3):
                    p = Vector((cx - a + f * 2 * a, cy - b, z))
                    v = p - origin
                    hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.999)
                    if hit and "sign" in ob.name:
                        boxes_hidden.add(f"{RR['id']}:{k + 1}")
    signs[R["id"]] = {"text": R["sign"], "screen_rect": [round(v, 4) for v in sr],
                      "inside_picture": 0.01 < sr[0] and sr[1] < 0.99 and 0.01 < sr[2] and sr[3] < 0.99,
                      "overlaps_text": [n for n, r in rr.items() if r[0] < sr[1] and sr[0] < r[1] and r[2] < sr[3] and sr[2] < r[3]],
                      "boxes_hidden": sorted(boxes_hidden), "cap_height_px_at_1200": round((p1.y - p0.y) * 800, 1)}
# the back row must not be hidden by the front row: rays to the bottom of its boxes' fronts
back_hidden = set()
for k, (cx, cy) in enumerate(far["centres"]):
    for f in (0.1, 0.5, 0.9):
        p = Vector((cx - a + f * 2 * a, cy - b, 0.4))
        v = p - origin
        hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.999)
        if hit and ob.name.startswith("q4_"):
            back_hidden.add(k + 1)
rows_out = []
for R in ROWS:
    lines_out = []
    for L in R["lines"]:
        h = sum(kit.object_height(s["obj"]) for s in R["segs"] if s["key"] == L["key"])
        lines_out.append({"key": L["key"], "gib": L["gib"], "height_units": round(h, 6), "units_per_gib": h / L["gib"],
                          "boxes": [s["box"] + 1 for s in R["segs"] if s["key"] == L["key"]]})
    last = max(s["z1"] for s in R["segs"] if s["box"] == R["n"] - 1)
    rows_out.append({"row": R["id"], "cards": R["n"], "total_gib_data": R["d"]["total_gib"],
                     "sum_of_lines_units": round(sum(x["height_units"] for x in lines_out), 4),
                     "last_box_fill": round(last / box_h, 4), "lines": lines_out, "sign": R["sign"], "title": R["title"]})
layout = {
    "figure": "train_bill_pair", "scale": {"units_per_gib": GIB, "footprint_units": list(kit.FOOTPRINT), "box_height": box_h},
    "rows": rows_out,
    "max_deviation_units_per_gib": max(abs(x["units_per_gib"] - 1.0) for r in rows_out for x in r["lines"]),
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2),
               "back_row_y": round(Y_BACK, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rr.items()},
    "text_overlaps": overlaps, "leaders_crossing_text": sorted(leader_cross), "text_hidden": sorted(hidden),
    "text_inside_picture": inside, "signs": signs, "back_row_boxes_hidden_by_front_row": sorted(back_hidden),
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_gib", "text_overlaps", "leaders_crossing_text",
                                                 "text_hidden", "text_inside_picture", "signs", "back_row_boxes_hidden_by_front_row")}))
print("ROWS", [(r["row"], r["cards"], r["sum_of_lines_units"], r["last_box_fill"], [(x["key"], x["height_units"]) for x in r["lines"]]) for r in rows_out])

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout)
    print("RENDER", round(secs, 1), "s")
