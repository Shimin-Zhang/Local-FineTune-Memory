"""Figure: the QLoRA step as a staircase, two training bills as rows of 24 GiB card boxes on one floating base.
Back row "naive: full fine-tune in BF16" (14 cards), front row "+ QLoRA" (7 cards); the memory QLoRA removes (the
gradients and the optimizer state of the frozen weights) is drawn after the front row's sign as outlines in those
lines' colours, to scale.

This is charts/bill_rows.py --option stair_a (which made the 900x600 draft, qlora_stair_a_draft.png, on the earlier
bills of 321 and 138 GiB) as its own file, checked against the current bills: activations counted on the 27B's own
shapes (about 122 GiB), so 332 GiB and 149 GiB. bill_rows.py is left as it was.
Data: charts/data/train_bill_bf16_3000.json and charts/data/train_bill_qlora_3000.json.

Each row: boxes filled in order with its bill (1 unit = 1 GiB, the VRAM figure's box), our card (first box) solid
with its rim, the others ghosted, a signboard with the card count (ceil(total / card), from the data) and the total.
The back row is labelled on its far side (above), the front row on its near side (below).

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/qlora_stair.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/qlora_stair_draft.png] [--layout ...] [--no-render]
The post's figure: --size 2400x1600 --samples 256 --out charts/out/qlora_stair.png
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
ap.add_argument("--out", default=None)
ap.add_argument("--layout", default=None)
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX
NAME = "qlora_stair"
out_png = args.out or os.path.join(HERE, "out", f"{NAME}_draft.png")
out_layout = args.layout or os.path.join(HERE, "out", f"{NAME}.layout.json")
GIB = kit.MIB_PER_GIB * kit.UNITS_PER_MIB          # units per GiB: 1.0


def half_up(x):
    return int(math.floor(x + 0.5))


ROWS = [   # back to front
    {"id": "bf16", "data": "train_bill_bf16_3000.json", "title": ["naive: full fine-tune in BF16"], "keep_sub": True},
    {"id": "qlora", "data": "train_bill_qlora_3000.json", "title": ["+ QLoRA: freeze the weights in 4-bit, train a rank-16 adapter"],
     "keep_sub": False, "show_removed": True},
]
ROWS[0]["side"], ROWS[-1]["side"] = "far", "near"
for R in ROWS:
    R["d"] = json.load(open(os.path.join(HERE, "data", R["data"])))
    R["lines"] = [L for L in R["d"]["lines_bottom_to_top"] if not L.get("removed")]
    R["removed"] = [L for L in R["d"]["lines_bottom_to_top"] if L.get("removed")] if R.get("show_removed") else []
    R["card"] = R["d"]["card_total_gib"]
    R["n"] = math.ceil(R["d"]["total_gib"] / R["card"])                     # cards, from the data
    assert R["n"] == math.ceil(sum(L["gib"] for L in R["lines"]) / R["card"] - 1e-9)
    R["sign"] = [f"{R['n']} × RTX 4090", f"≈ {half_up(R['d']['total_gib'])} GiB"]
assert [R["sign"] for R in ROWS] == [["14 × RTX 4090", "≈ 332 GiB"], ["7 × RTX 4090", "≈ 149 GiB"]]
card_gib = ROWS[0]["card"]
box_h = card_gib * GIB
SHORT = {}                                            # a line's short name, from the BF16 bill ("gradients", "optimizer state")


def label_parts(L, keep_sub=True):
    m = re.match(r"(.*) \((AdamW.*)\)$", L["label"])
    name, sub = (m.group(1), [m.group(2)]) if m else (L["label"], None)
    value = f"≈ {half_up(L['gib'])} GiB" if L.get("approximate") else f"{L['gib']:.1f} GiB"
    return f"{name} {value}", (sub if keep_sub else None)


for L in ROWS[0]["lines"]:
    SHORT[L["key"]] = re.match(r"(.*?)( \(AdamW.*\))?$", L["label"]).group(1)
EXPECT = {"bf16": ["Qwen3.8-27B weights (BF16) 50.1 GiB", "gradients 50.1 GiB", "optimizer state 100.2 GiB",
                   "activations, 3,000 tokens ≈ 122 GiB", "loss, 3,000 tokens 9.4 GiB"],
          "qlora": ["Qwen3.8-27B weights, frozen in 4-bit (NF4) 16.5 GiB", "adapter (79.7M weights): weights, gradients, AdamW 1.2 GiB",
                    "activations, 3,000 tokens ≈ 122 GiB", "loss, 3,000 tokens 9.4 GiB"]}
for R in ROWS:
    assert [label_parts(L)[0] for L in R["lines"]] == EXPECT[R["id"]], [label_parts(L)[0] for L in R["lines"]]
for R in ROWS:
    R["removed_text"] = {L["key"]: f"removed: {SHORT[L['key']]} {L['was_gib']:.1f} GiB" for L in R["removed"]}
assert ROWS[1]["removed_text"] == {"gradients": "removed: gradients 50.1 GiB", "optimizer": "removed: optimizer state 100.2 GiB"}

ELEVATION, AZIMUTH, LENS = 30.0, -16.0, 80.0         # as train_bill_pair
PITCH = kit.FOOTPRINT[0] + 3.0
SIGN_EM, SIGN_EM2 = 6.4, 4.8
a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
direction = kit.view_direction(ELEVATION, AZIMUTH)
away_y = -direction.y / math.hypot(direction.x, direction.y)
ROW_STEP = 2 * b + (box_h * math.cos(math.radians(ELEVATION)) + 1.5) / (math.sin(math.radians(ELEVATION)) * away_y)
for i, R in enumerate(ROWS):                          # back row furthest away; each row in front one step nearer
    R["y"] = (len(ROWS) - 1 - i) * ROW_STEP

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
keys = {L["key"] for R in ROWS for L in R["lines"] + R["removed"]}
mats = {k: kit.material(k, kit.COLOURS[k], emit=0.10, rough=0.85, spec=0.12) for k in keys}
ghost = kit.material("ghost", "#4d535c", rough=0.6, spec=0.2)
ink_sign = kit.material("sign_ink", "#dcdcdc", rough=0.6, emit=0.2, spec=0.3)
ink_sign2 = kit.material("sign_ink2", "#a9a9a9", rough=0.6, emit=0.2, spec=0.3)
volumes = []


def pour(lines, n_slots, x0, y, tag, gib_key="gib"):
    """Fill 24 GiB columns from x0 in order; returns segments {key, box, z0, z1, cx, cy}."""
    segs, c = [], 0.0
    for L in lines:
        c0, c1 = c, c + L[gib_key] * GIB
        for k in range(n_slots):
            a0, a1 = max(c0, k * box_h), min(c1, (k + 1) * box_h)
            if a1 > a0 + 1e-9:
                segs.append({"key": L["key"], "box": k, "z0": a0 - k * box_h, "z1": a1 - k * box_h,
                             "cx": x0 + k * PITCH + a, "cy": y, "tag": tag})
        c = c1
    return segs


for R in ROWS:
    R["centres"] = [(k * PITCH + a, R["y"]) for k in range(R["n"])]
    R["segs"] = pour(R["lines"], R["n"], 0.0, R["y"], "real")
    for s in R["segs"]:
        s["obj"] = kit.cuboid(f"{R['id']}_seg_{s['key']}_{s['box']}", (s["cx"] - a, s["cy"] - b, s["z0"]), (s["cx"] + a, s["cy"] + b, s["z1"]), mats[s["key"]])
        volumes.append(s["obj"])
    walls = kit.back_walls(box_h, direction, centre=R["centres"][0])
    for w in walls:
        w.name = f"{R['id']}_{w.name}"
    volumes += walls
    # signboard on a post past the row's last box
    t1, w1, _ = kit.text_object(f"{R['id']}_sign_text", R["sign"][0], "CENTER", "CENTER")
    t2, w2, _ = kit.text_object(f"{R['id']}_sign_text2", R["sign"][1], "CENTER", "CENTER")
    bw = max(w1 * SIGN_EM, w2 * SIGN_EM2) + 3.2
    bh = 0.75 * SIGN_EM + 0.75 * SIGN_EM2 + 0.45 * SIGN_EM + 2.4
    post_h = 3.0
    sx = (R["n"] - 1) * PITCH + 2 * a + (3.0 if R["side"] == "far" else 9.0) + bw / 2
    R["sign_centre"] = Vector((sx, R["y"] - 1.0, post_h + bh / 2))
    R["sign_right"] = sx + bw / 2
    bm = kit.material(f"{R['id']}_sign_board", "#323843", rough=0.75)
    fr = kit.material(f"{R['id']}_sign_frame", "#5b636d", rough=0.5, spec=0.4)
    e = 0.32
    parts = [kit.cuboid(f"{R['id']}_sign_board", (-bw / 2, -0.25, -bh / 2), (bw / 2, 0.25, bh / 2), bm),
             kit.cuboid(f"{R['id']}_sign_ft", (-bw / 2, -0.33, bh / 2 - e), (bw / 2, -0.25, bh / 2), fr),
             kit.cuboid(f"{R['id']}_sign_fb", (-bw / 2, -0.33, -bh / 2), (bw / 2, -0.25, -bh / 2 + e), fr),
             kit.cuboid(f"{R['id']}_sign_fl", (-bw / 2, -0.33, -bh / 2 + e), (-bw / 2 + e, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{R['id']}_sign_fr", (bw / 2 - e, -0.33, -bh / 2 + e), (bw / 2, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{R['id']}_sign_post", (-0.45, -0.2, -bh / 2 - post_h), (0.45, 0.2, -bh / 2), fr)]
    rot = Euler((0, 0, math.radians(AZIMUTH)))
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
    # removed lines: their memory, to scale, as outlines in their colours after the sign
    R["ghost_segs"] = []
    if R["removed"]:
        gx0 = R["sign_right"] + 4.0
        n_g = math.ceil(sum(L["was_gib"] for L in R["removed"]) / card_gib - 1e-9)
        R["ghost_segs"] = pour(R["removed"], n_g, gx0, R["y"], "removed", gib_key="was_gib")
        R["ghost_x1"] = gx0 + (n_g - 1) * PITCH + 2 * a

lo, hi = kit.world_bbox(volumes)
for R in ROWS:
    if R["ghost_segs"]:
        hi.x = max(hi.x, R["ghost_x1"])
lo.z = 0.0
base, base_info = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), dressing=False, drop=14.0, thickness=0.8)

# ---------------------------------------------------------------- labels
far, near = ROWS[0], ROWS[-1]
labels, kinds = [], {}
FAR_LEFT_ALIGNED = set()                              # far-side flags that run right from their leader
for R in ROWS:
    entries = [(L, label_parts(L, R["keep_sub"]), R["segs"]) for L in R["lines"]]
    entries += [(L, (R["removed_text"][L["key"]], None), R["ghost_segs"]) for L in R["removed"]]
    for L, (text, sub), pool in entries:
        segs = [s for s in pool if s["key"] == L["key"]]
        tag = segs[0]["tag"]
        key = f"{R['id']}_{tag}_{L['key']}"
        if R["side"] == "far":
            full = [s for s in segs if s["z1"] - s["z0"] > box_h - 1e-6]
            s = segs[0] if L["key"] == "weights" else (full[-1] if full else max(segs, key=lambda s: s["z1"] - s["z0"]))
            runs_right = L["key"] in ("weights", "gradients")      # text side must match the layout's alignment
            labels.append(kit.Label(key, text, (s["cx"], s["cy"], s["z1"]), "R" if runs_right else "L", sub=sub))
            kinds[key] = ("far_first" if L["key"] == "weights" else "far", s)
            if runs_right:
                FAR_LEFT_ALIGNED.add(key)
        else:
            ground = [s for s in segs if s["z0"] < 1e-6]
            full = [s for s in ground if s["z1"] - s["z0"] > box_h - 1e-6]
            s = (full[0] if full else ground[0]) if ground else max(segs, key=lambda s: s["z1"] - s["z0"])
            labels.append(kit.Label(key, text, (s["cx"], s["cy"] - b, (s["z0"] + s["z1"]) / 2), "R", sub=sub))
            kinds[key] = ("near" if ground else "near_side", s)
lc0, _, _ = kit.silhouette_corners(direction, centre=far["centres"][0])
labels.append(kit.Label("limit", "RTX 4090: 24 GiB", (lc0.x, lc0.y, box_h), "L"))
kinds["limit"] = ("left", None)
titles = []
for R in ROWS:
    objs, ws = [], []
    for j, line in enumerate(R["title"]):
        t, w, _ = kit.text_object(f"txt_title{j}_{R['id']}", line, "LEFT", "BOTTOM_BASELINE")
        objs.append(t)
        ws.append(w)
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
    # far side: flags rising to the right, each above every placed flag it overlaps
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
        for q in placed:                                       # flags closer than 1.5 em on a line read as one
            if q["x0"] - 1.5 * kit.EM < o["x1"] and o["x0"] < q["x1"] + 1.5 * kit.EM:
                y = max(y, q["y"] + 1.9 * em_y + o["below"])
        o["y"] = y
        o["route"] = [(o["ax"], o["ay"]), (o["ax"], y + 0.35 * em_y)]
        placed.append(o)
    first = next(l for l in labels if kinds[l.key][0] == "far_first")
    o = lay[first.key]
    o["x"] = o["ax"] + 0.5 * kit.EM
    o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
    y = o["ay"] + 2.0 * em_y
    for q in placed:
        if q["x0"] - 1.5 * kit.EM < o["x1"] and o["x0"] < q["x1"] + 1.5 * kit.EM:
            y = max(y, q["y"] + 1.9 * em_y)
    o["y"], o["route"] = y, [(o["ax"], o["ay"]), (o["ax"], y + 0.35 * em_y)]
    # near side: left-aligned flags under the base; the rightmost leader highest, each further left one step lower
    downs = []
    for lab in labels:
        kind, s = kinds[lab.key]
        if kind not in ("near", "near_side"):
            continue
        o = lay[lab.key]
        if kind == "near_side":                                    # out past the box's right edge, then down
            o["lx"] = kit.to_screen(scene, cam, (s["cx"] + a + 1.5, s["cy"] - b, lab.anchor.z)).x
        else:
            o["lx"] = o["ax"]
        o["edge"] = kit.to_screen(scene, cam, (s["cx"], base_info["y"][0], base_info["top"] - base_info["thickness"])).y
        downs.append((lab, kind))
    downs.sort(key=lambda t: -lay[t[0].key]["lx"])
    y_prev = None
    for lab, kind in downs:
        o = lay[lab.key]
        y = o["edge"] - 1.25 * em_y
        if y_prev is not None:
            y = min(y, y_prev - 1.9 * em_y - o["below"])
        o["route"] = ([(o["ax"], o["ay"]), (o["lx"], o["ay"]), (o["lx"], y + 0.3 * em_y)] if kind == "near_side"
                      else [(o["ax"], o["ay"]), (o["ax"], y + 0.3 * em_y)])
        o["y"], o["x"] = y, o["lx"] + 0.45 * kit.EM
        o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
        y_prev = y
    o = lay["limit"]
    o["y"], o["x"] = o["ay"], o["ax"] - 2.2 * kit.EM
    o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
    o["route"] = [(o["ax"], o["ay"]), (o["x"] + 0.45 * kit.EM, o["y"])]
    for o in lay.values():
        o["sub_y"] = o["y"] - o["h"] / 2 - kit.SUB_GAP * em_y
    tl = []
    top_y = max(o["y"] + o["h"] / 2 for k, o in lay.items() if kinds[k][0] in ("far", "far_first"))
    bot_y = min(o["y"] - o["h"] / 2 - o["below"] for k, o in lay.items() if kinds[k][0] in ("near", "near_side"))
    x_left = min(o["x0"] for o in lay.values())
    for t in titles:
        R = t["row"]
        w = max([t["w"][0] * kit.EM] + [x * kit.SUB_EM for x in t["w"][1:]])
        if R["side"] == "far":
            ys = [top_y + 0.9 * em_y]
            rect = [x_left, x_left + w, ys[0] - 0.25 * em_y, ys[0] + 0.74 * em_y]
        else:
            ys = [bot_y - 1.15 * em_y]
            for _ in t["w"][1:]:
                ys.append(ys[-1] - 0.30 * em_y - 0.95 * sub_y)
            rect = [x_left, x_left + w, ys[-1] - 0.25 * sub_y, ys[0] + 0.74 * em_y]
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
for R in ROWS:                                        # the removed outlines count too
    for s in R["ghost_segs"]:
        pts += [Vector((s["cx"] + sx_ * a, s["cy"] + sy_ * b, z)) for sx_ in (-1, 1) for sy_ in (-1, 1) for z in (s["z0"], s["z1"])]
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

# ---------------------------------------------------------------- what is sized on screen: frames, outlines, text
d_box = kit.to_screen(scene, cam, (near["centres"][0][0], near["y"], box_h / 2)).z
fw, _ = kit.frame_size(scene, cam, d_box)
s_ = kit.STRUT * fw * 0.8 / 2


def ring(name, cx, cy, z, mat, r=s_):
    return [kit.cuboid(f"{name}-y", (cx - a - r, cy - b - r, z - r), (cx + a + r, cy - b + r, z + r), mat),
            kit.cuboid(f"{name}+y", (cx - a - r, cy + b - r, z - r), (cx + a + r, cy + b + r, z + r), mat),
            kit.cuboid(f"{name}-x", (cx - a - r, cy - b + r, z - r), (cx - a + r, cy + b - r, z + r), mat),
            kit.cuboid(f"{name}+x", (cx + a - r, cy - b + r, z - r), (cx + a + r, cy + b - r, z + r), mat)]


for R in ROWS:
    objs = kit.box_frame(box_h, kit.STRUT * fw, kit.RIM * fw, centre=R["centres"][0])       # our card: frame and rim
    for k in range(1, R["n"]):
        cx, cy = R["centres"][k]
        for i, p in enumerate(kit.box_corners(centre=(cx, cy))):
            objs.append(kit.cuboid(f"ghost_{k}_{i}", (p.x - s_, p.y - s_, 0), (p.x + s_, p.y + s_, box_h), ghost))
        objs += ring(f"ghost_{k}_top", cx, cy, box_h, ghost)
    for ob in objs:
        ob.name = f"{R['id']}_{ob.name}"
    # removed memory: edges in the line's colour and a faint veil of it, no card frame
    by_slot = {}
    for s in R["ghost_segs"]:
        by_slot.setdefault(s["box"], []).append(s)
    for k, ss in by_slot.items():
        ss.sort(key=lambda s: s["z0"])
        for j, s in enumerate(ss):
            m = mats[s["key"]]
            veil = kit.veil_material(f"veil_{s['key']}", 0.07, kit.hex_lin(kit.COLOURS[s["key"]]))
            nm = f"{R['id']}_removed_{s['key']}_{k}"
            for i, p in enumerate(kit.box_corners(centre=(s["cx"], s["cy"]))):
                kit.cuboid(f"{nm}_edge_{i}", (p.x - s_, p.y - s_, s["z0"]), (p.x + s_, p.y + s_, s["z1"]), m)
            for ob in ring(f"{nm}_bottom", s["cx"], s["cy"], s["z0"] + (s_ if s["z0"] < 1e-6 else 0.0), m):
                pass
            if j == len(ss) - 1:
                ring(f"{nm}_top", s["cx"], s["cy"], s["z1"], m)
            v = kit.cuboid(f"{nm}_veil", (s["cx"] - a, s["cy"] - b, s["z0"]), (s["cx"] + a, s["cy"] + b, s["z1"]), veil)
            kit.no_shadow(v)
bpy.context.view_layer.update()
kit.build_labels(scene, cam, labels, lay, lift=kit.RIM * fw)
ink, ink2 = kit.glow_material("ink_t", kit.LOOK["ink"], 1.0), kit.glow_material("ink2_t", kit.LOOK["ink2"], 1.0)
d_text = kit.to_screen(scene, cam, (near["centres"][0][0], base_info["y"][0], 0)).z - 2.0
for t in tl:
    for j, ob in enumerate(t["t"]["objs"]):
        kit.place_on_screen(scene, cam, ob, t["x"], t["y"][j], d_text, kit.EM if j == 0 else kit.SUB_EM, ink if j == 0 else ink2)

kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)   # as train_bill_pair

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
            if hit and not ob.name.startswith(("label_", "leader_", "dot_", "txt_")) and "_veil" not in ob.name:
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
back_hidden = set()
for R in ROWS[:-1]:
    for k, (cx, cy) in enumerate(R["centres"]):
        for f in (0.1, 0.5, 0.9):
            p = Vector((cx - a + f * 2 * a, cy - b, 0.4))
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.999)
            if hit and not ob.name.startswith(R["id"]) and not ob.name.startswith(("base", "label_", "leader_", "dot_")):
                back_hidden.add(f"{R['id']}:{k + 1} by {ob.name}")
rows_out = []
for R in ROWS:
    lines_out = []
    for L in R["lines"]:
        h = sum(kit.object_height(s["obj"]) for s in R["segs"] if s["key"] == L["key"])
        lines_out.append({"key": L["key"], "gib": L["gib"], "height_units": round(h, 6), "units_per_gib": h / L["gib"],
                          "boxes": [s["box"] + 1 for s in R["segs"] if s["key"] == L["key"]]})
    removed_out = [{"key": L["key"], "was_gib": L["was_gib"], "height_units": round(sum(s["z1"] - s["z0"] for s in R["ghost_segs"] if s["key"] == L["key"]), 6),
                    "label": R["removed_text"][L["key"]]} for L in R["removed"]]
    last = max(s["z1"] for s in R["segs"] if s["box"] == R["n"] - 1)
    rows_out.append({"row": R["id"], "cards": R["n"], "total_gib_data": R["d"]["total_gib"],
                     "sum_of_lines_units": round(sum(x["height_units"] for x in lines_out), 4),
                     "last_box_fill": round(last / box_h, 4), "lines": lines_out, "removed": removed_out,
                     "sign": R["sign"], "title": R["title"]})
layout = {
    "figure": NAME, "from": "bill_rows.py --option stair_a", "scale": {"units_per_gib": GIB, "footprint_units": list(kit.FOOTPRINT), "box_height": box_h},
    "rows_back_to_front": rows_out,
    "max_deviation_units_per_gib": max(abs(x["units_per_gib"] - 1.0) for r in rows_out for x in r["lines"]),
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2), "row_step_y": round(ROW_STEP, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rr.items()},
    "text_overlaps": overlaps, "leaders_crossing_text": sorted(leader_cross), "text_hidden": sorted(hidden),
    "text_inside_picture": inside, "signs": signs, "back_rows_hidden": sorted(back_hidden),
}
os.makedirs(os.path.dirname(out_layout), exist_ok=True)
kit.write_json(out_layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_gib", "text_overlaps", "leaders_crossing_text",
                                                 "text_hidden", "text_inside_picture", "back_rows_hidden")}))
print("SIGNS", json.dumps({k: (v["cap_height_px_at_1200"], v["boxes_hidden"], v["overlaps_text"], v["inside_picture"]) for k, v in signs.items()}))
print("ROWS", [(r["row"], r["cards"], r["sum_of_lines_units"], r["last_box_fill"], [(x["key"], x["height_units"]) for x in r["lines"]],
                [(x["key"], x["height_units"]) for x in r["removed"]]) for r in rows_out])

if not args.no_render:
    scene.render.filepath = out_png
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout["draft_render"] = {"png": out_png, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(out_layout, layout)
    print("RENDER", round(secs, 1), "s")
