"""Figure (v2): gradient checkpointing on top of QLoRA, as two bills: left all activations kept (7 cards), right with
checkpointing (2 cards). Fig-3 style: rows of 24 GiB card boxes (1 unit = 1 GiB, the VRAM figure's box), our card
solid with its rim, the others ghosted, a signboard with the card count and total; each side labels its own lines.
(Draft 1, with the 64-layer stacks and the layer-33 detail, is reproducible with charts/checkpointing_draft1.py.)
Data: charts/data/checkpointing_3000.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/checkpointing.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/checkpointing_v2_draft.png] [--no-render]
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
ap.add_argument("--out", default=os.path.join(HERE, "out", "checkpointing_v5_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "checkpointing_v5_draft.layout.json"))
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--no-sign-light", action="store_true", help="v4: the signs lit by the key itself (its shadow can cross them)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX
GIB = kit.MIB_PER_GIB * kit.UNITS_PER_MIB


def half_up(x, nd=0):
    f = 10 ** nd
    return math.floor(x * f + 0.5) / f


data = json.load(open(os.path.join(HERE, "data", "checkpointing_3000.json")))
card_gib = data["card_total_gib"]
box_h = card_gib * GIB
SIDES = [
    {"row": data["rows"][0], "title": ["QLoRA, all activations kept"], "approx_acts": True},
    {"row": data["rows"][1], "title": ["QLoRA + gradient checkpointing", "every layer's forward pass runs twice: 19–26% slower"],
     "approx_acts": False},
]


def gib_text(v, approx):
    return f"≈ {half_up(v):.0f} GiB" if approx else f"{half_up(v, 1):.1f} GiB"


for S in SIDES:
    R = S["row"]
    S["id"], S["n"] = R["key"], math.ceil(R["total_gib"] / card_gib)
    S["sign"] = [f"{S['n']} × RTX 4090", f"≈ {half_up(R['total_gib']):.0f} GiB"]
    S["lines"] = {L["key"]: L for L in R["lines"]}
    S["text"] = {k: f"{L['label']} {gib_text(L['gib'], S['approx_acts'] and k == 'activations')}" for k, L in S["lines"].items()}
assert [S["sign"] for S in SIDES] == [["7 × RTX 4090", "≈ 149 GiB"], ["2 × RTX 4090", "≈ 32 GiB"]]
assert SIDES[0]["text"]["activations"] == "activations, 3,000 tokens ≈ 122 GiB"
assert SIDES[1]["text"]["activations"] == "activations, 3,000 tokens 4.5 GiB"

PITCH = kit.FOOTPRINT[0] + 3.0
SIDE_GAP = 150.0                     # the right diorama, along the camera's screen-right
ELEVATION, AZIMUTH, LENS = 28.0, -14.0, 80.0
SIGN_EM, SIGN_EM2 = 7.4, 5.6
C = {k: kit.COLOURS[k] for k in ("weights", "gradients", "optimizer", "activations", "loss", "frozen")}
direction = kit.view_direction(ELEVATION, AZIMUTH)
a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
RIGHT = Vector((-direction.y, direction.x, 0)).normalized()

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
mats = {k: kit.material(f"m_{k}", v, emit=0.10, rough=0.85, spec=0.12) for k, v in C.items()}
ghost = kit.material("ghost", "#4d535c", rough=0.6, spec=0.2)
# v3: the signs' lettering is self-lit in the figure's two text inks. With a lit ink, the low key light from the right
# made the right diorama's card throw its shadow across the left sign's lower line (v2: "≈ 149 GiB" read dark).
ink_sign = kit.glow_material("sign_ink", kit.LOOK["ink"], 1.0)
ink_sign2 = ink_sign                                  # v4: the total in the same bright primary ink as the count line

for si, S in enumerate(SIDES):
    X0, Y0 = si * SIDE_GAP * RIGHT.x, si * SIDE_GAP * RIGHT.y
    S["X0"], S["Y0"] = X0, Y0
    Ls = S["lines"]
    ad = Ls["adapter"]["gib"]
    pour = [("weights", "frozen", Ls["weights"]["gib"]), ("adapter_w", "weights", ad / 4), ("adapter_g", "gradients", ad / 4),
            ("adapter_o", "optimizer", ad / 2), ("activations", "activations", Ls["activations"]["gib"]), ("loss", "loss", Ls["loss"]["gib"])]
    S["centres"] = [(X0 + k * PITCH + a, Y0) for k in range(S["n"])]
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
    t1, w1, _ = kit.text_object(f"{S['id']}_sign_text", S["sign"][0], "CENTER", "CENTER")
    t2, w2, _ = kit.text_object(f"{S['id']}_sign_text2", S["sign"][1], "CENTER", "CENTER")
    bw = max(w1 * SIGN_EM, w2 * SIGN_EM2) + 3.2
    bh = 0.75 * SIGN_EM + 0.75 * SIGN_EM2 + 0.45 * SIGN_EM + 2.4
    sx = X0 + (S["n"] - 1) * PITCH + 2 * a + 3.0 + bw / 2
    centre = Vector((sx, Y0 - 1.0, 3.0 + bh / 2))
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
    S["sign_objs"] = parts
    S["sign_texts"] = [t1, t2]
    S["objs"] += parts
    lo, hi = kit.world_bbox(S["objs"])
    lo.z = 0.0
    S["base"], S["base_info"] = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), seed=11 + 7 * si, dressing=False, drop=12.0, thickness=0.8)

# ---------------------------------------------------------------- labels: each side's own lines, under its row
labels, kinds = [], {}
for S in SIDES:
    segs, sid = S["segs"], S["id"]
    w0 = next(s for s in segs if s["key"] == "weights")
    adl = [s for s in segs if s["key"].startswith("adapter")]
    acts = [s for s in segs if s["key"] == "activations"]
    loss = [s for s in segs if s["key"] == "loss"]

    def add(key, s, z, mode):
        cx, cy = S["centres"][s["box"]]
        labels.append(kit.Label(f"{sid}_{key}", S["text"][key], (cx, cy - b, z), "R"))
        kinds[f"{sid}_{key}"] = (S, mode, s)

    add("weights", w0, (w0["z0"] + w0["z1"]) / 2, "ground")
    add("adapter", adl[0], (adl[0]["z0"] + adl[-1]["z1"]) / 2, "side")
    ga = [s for s in acts if s["z0"] < 1e-6]
    sa = (ga[0] if ga else acts[0])
    add("activations", sa, (sa["z0"] + sa["z1"]) / 2, "ground" if ga else "side")
    gl = [s for s in loss if s["z0"] < 1e-6]
    sl = gl[-1] if gl else loss[-1]
    add("loss", sl, (sl["z0"] + sl["z1"]) / 2, "ground" if gl else "side")
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
        lay[lab.key] = {"ax": p.x, "ay": p.y, "depth": p.z, "w": lab.w_em * kit.EM, "h": em_y, "below": 0.0}
    for S in SIDES:
        near_depth = kit.to_screen(scene, cam, (S["X0"], S["base_info"]["y"][0], 0.0)).z - 2.0
        mine = []
        for lab in labels:
            S_, mode, s = kinds[lab.key]
            if S_ is not S:
                continue
            o = lay[lab.key]
            cx, cy = S["centres"][s["box"]]
            o["lx"] = kit.to_screen(scene, cam, (cx + a + 1.5, cy - b, lab.anchor.z)).x if mode == "side" else o["ax"]
            o["edge"] = kit.to_screen(scene, cam, (cx, S["base_info"]["y"][0], S["base_info"]["top"] - S["base_info"]["thickness"])).y
            o["depth"] = near_depth
            mine.append((lab, mode))
        mine.sort(key=lambda t: -lay[t[0].key]["lx"])            # the rightmost leader highest, each further left lower
        y_prev = None
        for lab, mode in mine:
            o = lay[lab.key]
            y = o["edge"] - 1.5 * em_y if y_prev is None else min(o["edge"] - 1.5 * em_y, y_prev - 1.75 * em_y)
            o["route"] = ([(o["ax"], o["ay"]), (o["lx"], o["ay"]), (o["lx"], y + 0.3 * em_y)] if mode == "side"
                          else [(o["ax"], o["ay"]), (o["ax"], y + 0.3 * em_y)])
            o["y"], o["x"] = y, o["lx"] + 0.45 * kit.EM
            o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
            y_prev = y
    for o in lay.values():
        o["sub_y"] = o["y"] - o["h"] / 2 - kit.SUB_GAP * em_y
    tl = []
    geo_top = max(kit.to_screen(scene, cam, (cx + dx, cy + dy, box_h)).y for S in SIDES for cx, cy in S["centres"] for dx in (-a, a) for dy in (-b, b))
    for t in titles:
        S = t["side"]
        gx = min(kit.to_screen(scene, cam, (cx - a, cy - b, 0)).x for cx, cy in S["centres"])
        ys = [geo_top + 1.4 * em_y]
        if len(t["w"]) > 1:
            ys = [geo_top + 1.4 * em_y + 1.05 * sub_y + 0.3 * em_y, geo_top + 1.4 * em_y]
        w = max([t["w"][0] * kit.EM] + [x * kit.SUB_EM for x in t["w"][1:]])
        tl.append({"t": t, "x": gx, "y": ys, "rect": [gx, gx + w, ys[-1] - 0.25 * (sub_y if len(ys) > 1 else em_y), ys[0] + 0.74 * em_y]})
    return lay, tl


def rects(lay, tl):
    out = {k: [o["x0"], o["x1"], o["y"] - o["h"] / 2, o["y"] + o["h"] / 2] for k, o in lay.items()}
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
d_box = kit.to_screen(scene, cam, (SIDES[0]["centres"][0][0], SIDES[0]["centres"][0][1], box_h / 2)).z
fw, _ = kit.frame_size(scene, cam, d_box)
s_ = kit.STRUT * fw * 0.8 / 2
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
bpy.context.view_layer.update()
kit.build_labels(scene, cam, labels, lay, lift=0.0)
ink, ink2 = kit.glow_material("ink_t", kit.LOOK["ink"], 1.0), kit.glow_material("ink2_t", kit.LOOK["ink2"], 1.0)
d_text = kit.to_screen(scene, cam, (SIDES[0]["X0"], SIDES[0]["base_info"]["y"][0], 0)).z - 2.0
for t in tl:
    for j, ob in enumerate(t["t"]["objs"]):
        kit.place_on_screen(scene, cam, ob, t["x"], t["y"][j], d_text, kit.EM if j == 0 else kit.SUB_EM, ink if j == 0 else ink2)
key_ob, rim_ob = kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)   # as fig 3
# v5: the low key light made the right card's shadow fall across the left sign (a dark band behind "≈ 149 GiB").
# Light linking: the key lights everything but the two signs; a twin of the key, shadows off, lights only the signs,
# so both boards are lit the same way and no shadow crosses them.
if not args.no_sign_light:
    # two collections, because a collection's link states are shared by every light that uses it
    not_key = bpy.data.collections.new("signs_not_lit_by_key")
    by_twin = bpy.data.collections.new("signs_lit_by_twin")
    for c in (not_key, by_twin):
        scene.collection.children.link(c)
        for S in SIDES:
            for ob in S["sign_objs"] + S["sign_texts"]:
                c.objects.link(ob)
    key_ob.light_linking.receiver_collection = not_key
    for co in not_key.collection_objects:
        co.light_linking.link_state = "EXCLUDE"
    twin = key_ob.data.copy()
    twin.name = "sign_key"
    for attr, val in (("use_shadow", False),):
        try:
            setattr(twin, attr, val)
        except AttributeError:
            pass
    try:
        twin.cycles.cast_shadow = False
    except AttributeError:
        pass
    sign_key = bpy.data.objects.new("sign_key", twin)
    scene.collection.objects.link(sign_key)
    sign_key.rotation_euler = key_ob.rotation_euler.copy()
    sign_key.light_linking.receiver_collection = by_twin      # only the signs (INCLUDE, the default state)
    for co in by_twin.collection_objects:
        co.light_linking.link_state = "INCLUDE"

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
            p = kit.to_world(scene, cam, r[0] + fx * (r[1] - r[0]), r[2] + fy * (r[3] - r[2]), lay[n]["depth"] if n in lay else d_text)
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(("label_", "leader_", "dot_", "txt_")):
                hidden.add((n, ob.name))
geo_rects = {}                                        # boxes and signs on screen: no text on them
for S in SIDES:
    for nm, obs in (("row", [s["obj"] for s in S["segs"]]), ("sign", S["sign_objs"])):
        sp = [kit.to_screen(scene, cam, p) for p in kit.mesh_points(obs)]
        geo_rects[f"{S['id']}_{nm}"] = [min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)]
text_on_geo = [[n, g] for n, r in rr.items() for g, q in geo_rects.items() if r[0] < q[1] and q[0] < r[1] and r[2] < q[3] and q[2] < r[3]]
sides_out = []
for S in SIDES:
    lines_out = {}
    for key in ("weights", "adapter", "activations", "loss"):
        h = sum(kit.object_height(s["obj"]) for s in S["segs"] if s["key"] == key or (key == "adapter" and s["key"].startswith("adapter")))
        lines_out[key] = {"gib": S["lines"][key]["gib"], "height_units": round(h, 6), "units_per_gib": h / S["lines"][key]["gib"]}
    box_px = (geo_rects[f"{S['id']}_row"][1] - geo_rects[f"{S['id']}_row"][0]) * rx / S["n"]
    sides_out.append({"side": S["id"], "cards": S["n"], "sign": S["sign"], "total_gib_data": S["row"]["total_gib"],
                      "sum_of_lines_units": round(sum(v["height_units"] for v in lines_out.values()), 4), "lines": lines_out,
                      "labels": [S["text"][k] for k in ("weights", "adapter", "activations", "loss")], "box_pitch_px": round(box_px, 1)})
layout = {
    "figure": "checkpointing", "version": 2, "scales": {"bills_units_per_gib": GIB},
    "sides": sides_out,
    "max_deviation_units_per_gib": max(abs(v["units_per_gib"] - 1.0) for s in sides_out for v in s["lines"].values()),
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rr.items()},
    "text_overlaps": overlaps, "leaders_crossing_text": sorted(leader_cross), "text_hidden": sorted(hidden),
    "text_inside_picture": inside, "text_on_geometry": text_on_geo,
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_gib", "text_overlaps", "leaders_crossing_text",
                                                 "text_hidden", "text_inside_picture", "text_on_geometry")}))
print("SIDES", [(s["side"], s["cards"], s["sum_of_lines_units"], s["box_pitch_px"]) for s in sides_out])

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout)
    print("RENDER", round(secs, 1), "s")
