"""Figure: what one weight costs in training, in bytes: fully trained (BF16), frozen in 4-bit, and an adapter weight.

The twin of bits_per_weight.py: columns on one floating base, height = bytes per weight (UNITS_PER_BYTE), built from
one-byte slabs with a thin slit between them, each byte in the colour of the bill line it belongs to; a sub-byte
part (the frozen weight's 0.5 + 0.017) is one slab of exactly its height. Data: charts/data/weight_cost_bytes.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/weight_cost.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/weight_cost_draft.png] [--no-render] [--inset]
"""
import argparse, json, math, os, sys, time
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="900x600")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=os.path.join(HERE, "out", "weight_cost_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "weight_cost.layout.json"))
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--inset", action="store_true", help="try the inset: one MLP matrix as a frozen slab with its adapter strips")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX

data = json.load(open(os.path.join(HERE, "data", "weight_cost_bytes.json")))
cols = data["columns"]
for c in cols:
    assert abs(sum(p["bytes"] for p in c["parts"]) - c["total_bytes"]) < 1e-9, c


def bytes_text(b):
    return f"{round(b, 2):g} bytes"


assert [bytes_text(c["total_bytes"]) for c in cols] == ["8 bytes", "0.52 bytes", "16 bytes"]

UNITS_PER_BYTE = 1.0                 # height: 1 Blender unit = 1 byte per weight
COL_W, COL_D, GAP = 4.2, 4.2, 3.4    # the bits figure's column footprint
SLIT = 0.16                          # cut from the top of every whole-byte slab except a column's last
COLOUR = {k: kit.COLOURS[k] for k in ("weights", "gradients", "optimizer", "scales")}
ELEVATION, AZIMUTH, LENS = 26.4, 6.8, 80.0   # the bits figure's camera
REGION = (0.035, 0.965, 0.05, 0.86)
EM, SUB = kit.EM, kit.SUB_EM

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
mats = {k: kit.material(f"m_{k}", v, emit=0.10 if k != "scales" else 0.08, rough=0.85, spec=0.12) for k, v in COLOUR.items()}

# ---------------------------------------------------------------- columns of byte slabs
xs = [i * (COL_W + GAP) for i in range(len(cols))]
row_len = xs[-1] + COL_W
col_objs = []
for i, c in enumerate(cols):
    slabs = []                                       # (line, bytes): whole bytes one by one, a fraction as one slab
    # scales go under the weight they belong to: on a sub-byte column the top face would otherwise show the
    # scales' colour for a part that is 3% of it
    for p in sorted(c["parts"], key=lambda p: p["line"] != "scales"):
        whole = int(p["bytes"] + 1e-9)
        if abs(p["bytes"] - whole) < 1e-9 and whole >= 1:
            slabs += [(p["line"], 1.0)] * whole
        else:
            slabs.append((p["line"], p["bytes"]))
    c["slabs"], c["objs"], z = [], [], 0.0
    for k, (line, h) in enumerate(slabs):
        last = k == len(slabs) - 1
        top = z + h - (SLIT if (h >= 1.0 and not last) else 0.0)
        ob = kit.cuboid(f"col_{c['key']}_{k}_{line}", (xs[i], -COL_D / 2, z * UNITS_PER_BYTE), (xs[i] + COL_W, COL_D / 2, top * UNITS_PER_BYTE), mats[line])
        c["objs"].append(ob)
        c["slabs"].append({"line": line, "bytes": h, "slab_z": [round(z, 4), round(top, 4)]})
        z += h
    c["xc"] = xs[i] + COL_W / 2
    col_objs += c["objs"]
inset_objs = []
if args.inset:                                       # area = weights (1 unit = 2,048 weights a side), height = bytes
    M = data["inset_matrix"]
    L = 2048.0
    ox, oy = -(M["rows"] / L) - 4.0, 0.0
    w_, d_ = M["rows"] / L, M["cols"] / L
    inset_objs.append(kit.cuboid("inset_frozen_w", (ox, oy - d_ / 2, 0), (ox + w_, oy + d_ / 2, 0.5), mats["weights"]))
    inset_objs.append(kit.cuboid("inset_frozen_s", (ox, oy - d_ / 2, 0.5), (ox + w_, oy + d_ / 2, 0.517), mats["scales"]))
    t = M["adapter"]["rank"] / L
    z = 0.0
    for line, h in (("weights", 4), ("gradients", 4), ("optimizer", 8)):
        inset_objs.append(kit.cuboid(f"inset_B_{line}", (ox, oy + d_ / 2, z), (ox + w_, oy + d_ / 2 + t, z + h), mats[line]))
        inset_objs.append(kit.cuboid(f"inset_A_{line}", (ox + w_, oy - d_ / 2, z), (ox + w_ + t, oy + d_ / 2, z + h), mats[line]))
        z += h
    col_objs += inset_objs
lo, hi = kit.world_bbox(col_objs)
lo.z = 0.0
pad = 2.6
base, base_info = kit.floating_base(lo, hi, margin=pad / (hi.x - lo.x), dressing=False, drop=6.0, thickness=0.6)
y_front = base_info["y"][0]
geo = col_objs + base

# ---------------------------------------------------------------- text
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
T = []


def text(name, body, size, mat, align_x="CENTER", align_y="BOTTOM_BASELINE"):
    ob, w, h = kit.text_object(f"txt_{name}", body, align_x, align_y)
    t = {"name": name, "body": body, "ob": ob, "w_em": w, "size": size, "mat": mat, "align_x": align_x}
    T.append(t)
    return t


for c in cols:
    c["t_top"] = text(f"top_{c['key']}", bytes_text(c["total_bytes"]), EM, ink)
    c["t_name"] = text(f"name_{c['key']}", c["label"], EM, ink)
    c["t_sub"] = text(f"sub_{c['key']}", c["sub"], SUB, ink2)
    c["t_count"] = text(f"count_{c['key']}", c["count"], SUB, ink)
LEGEND = [("weights", "weights"), ("gradients", "gradient"), ("optimizer", "optimizer state"), ("scales", "scales")]
t_leg = [text(f"legend_{k}", s, SUB, ink, "LEFT", "CENTER") for k, s in LEGEND]


def layout():
    em_y, sub_y = EM * rx / ry, SUB * rx / ry
    for c in cols:
        top_back = kit.to_screen(scene, cam, (c["xc"], COL_D / 2, c["total_bytes"] * UNITS_PER_BYTE))
        c["t_top"]["x"], c["t_top"]["y"] = top_back.x, top_back.y + 0.45 * em_y
        edge = kit.to_screen(scene, cam, (c["xc"], y_front, base_info["top"] - base_info["thickness"]))
        c["t_name"]["x"], c["t_name"]["y"] = edge.x, edge.y - 0.55 * em_y - 0.72 * em_y
        c["t_sub"]["x"], c["t_sub"]["y"] = edge.x, c["t_name"]["y"] - 0.30 * em_y - 0.95 * sub_y
        c["t_count"]["x"], c["t_count"]["y"] = edge.x, c["t_sub"]["y"] - 0.35 * sub_y - 0.95 * sub_y
    xl, yl = 0.03, 0.955
    for t in t_leg:
        t["swatch_x"] = xl + 0.425 * SUB
        t["x"], t["y"] = xl + 1.3 * SUB, yl
        xl = t["x"] + t["w_em"] * SUB + 1.6 * SUB
    for t in T:
        w, hy = t["w_em"] * t["size"], t["size"] * rx / ry
        x0 = t["x"] - w / 2 if t["align_x"] == "CENTER" else t["x"]
        if t["name"].startswith("legend"):
            t["rect"] = [t["swatch_x"] - 0.425 * t["size"], t["x"] + w, t["y"] - 0.5 * hy, t["y"] + 0.5 * hy]
        else:
            t["rect"] = [x0, x0 + w, t["y"] - 0.24 * hy, t["y"] + 0.74 * hy]


# ---------------------------------------------------------------- camera: the row and its text fill REGION
cam = kit.make_camera(scene, LENS)
pts = kit.mesh_points(geo)
target, dist = (lo + hi) / 2, 2.5 * row_len
rx0, rx1, ry0, ry1 = REGION
for _ in range(14):
    kit.aim(cam, target, dist, direction)
    sp = [kit.to_screen(scene, cam, p) for p in pts]
    gx0, gx1, gy0, gy1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    layout()
    rects = [t["rect"] for t in T if not t["name"].startswith("legend")]
    x0, x1 = min([gx0] + [r[0] for r in rects]), max([gx1] + [r[1] for r in rects])
    y0, y1 = min([gy0] + [r[2] for r in rects]), max([gy1] + [r[3] for r in rects])
    gw, gh = gx1 - gx0, gy1 - gy0
    z = min((0.97 * (rx1 - rx0) - ((x1 - x0) - gw)) / gw, (0.97 * (ry1 - ry0) - ((y1 - y0) - gh)) / gh)
    fw_, fh_ = kit.frame_size(scene, cam, dist)
    Rv = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    Uv = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    target = target + Rv * ((x0 + x1) / 2 - (rx0 + rx1) / 2) * fw_ + Uv * ((y0 + y1) / 2 - (ry0 + ry1) / 2) * fh_
    if abs(z - 1) < 0.001 and abs((x0 + x1) / 2 - (rx0 + rx1) / 2) < 0.001 and abs((y0 + y1) / 2 - (ry0 + ry1) / 2) < 0.001:
        break
    dist /= z
kit.aim(cam, target, dist, direction)
layout()
d_text = kit.to_screen(scene, cam, (row_len / 2, y_front, base_info["top"])).z - 1.0
for t in T:
    kit.place_on_screen(scene, cam, t["ob"], t["x"], t["y"], d_text, t["size"], t["mat"])
for (k, _), t in zip(LEGEND, t_leg):
    kit.place_on_screen(scene, cam, kit.swatch_object(f"swatch_{k}", COLOUR[k]), t["swatch_x"], t["y"], d_text, 0.85 * SUB)
kit.stage_lights(direction, key=3.5, rim=2.0, key_turn=30, key_el=14, rim_turn=130)   # as the bits figure

# ---------------------------------------------------------------- checks and layout
rects = {t["name"]: t["rect"] for t in T}
names = list(rects)
overlaps = [[p, q] for i, p in enumerate(names) for q in names[i + 1:]
            if rects[p][0] < rects[q][1] and rects[q][0] < rects[p][1] and rects[p][2] < rects[q][3] and rects[q][2] < rects[p][3]]
inside = all(0.01 < r[0] and r[1] < 0.99 and 0.01 < r[2] and r[3] < 0.99 for r in rects.values())
dg = bpy.context.evaluated_depsgraph_get()
origin = cam.matrix_world.translation
hidden = set()
for t in T:
    r = t["rect"]
    for fx in (0.05, 0.5, 0.95):
        for fy in (0.25, 0.75):
            p = kit.to_world(scene, cam, r[0] + fx * (r[1] - r[0]), r[2] + fy * (r[3] - r[2]), d_text)
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(("txt_", "swatch_")):
                hidden.add((t["name"], ob.name))
cols_out = []
for c in cols:
    lo_c, hi_c = kit.world_bbox(c["objs"])
    h = hi_c.z - lo_c.z
    cols_out.append({"key": c["key"], "bytes": c["total_bytes"], "height_units": round(h, 6), "units_per_byte": h / c["total_bytes"],
                     "labels": [c["t_top"]["body"], c["t_name"]["body"], c["t_sub"]["body"], c["t_count"]["body"]], "slabs": c["slabs"]})
layout_json = {
    "figure": "weight_cost", "scale": {"units_per_byte": UNITS_PER_BYTE, "slit_units": SLIT,
                                       "slit_rule": "cut from the top of every whole-byte slab except a column's last"},
    "columns": cols_out, "max_deviation_units_per_byte": max(abs(c["units_per_byte"] - UNITS_PER_BYTE) for c in cols_out),
    "ratios": {"adapter_vs_full_bytes": cols[2]["total_bytes"] / cols[0]["total_bytes"],
               "full_vs_frozen_bytes": round(cols[0]["total_bytes"] / cols[1]["total_bytes"], 2)},
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 3)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rects.items()},
    "text_overlaps": overlaps, "text_hidden": sorted(hidden), "text_inside_picture": inside,
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout_json)
print("LAYOUT", json.dumps({k: layout_json[k] for k in ("max_deviation_units_per_byte", "text_overlaps", "text_hidden", "text_inside_picture", "ratios")}))
print("HEIGHTS", [(c["key"], c["bytes"], c["height_units"]) for c in cols_out])

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout_json["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout_json)
    print("RENDER", round(secs, 1), "s")
