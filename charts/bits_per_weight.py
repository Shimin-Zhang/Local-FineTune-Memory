"""Figure: what one weight costs, in bits, in each format inside the GGUF file we ran, next to BF16 as released.

Five columns on one floating base (BF16 a little apart, then Q5_K, IQ4_XS, Q6_K, Q4_K by share of weights). Height
= bits per weight at one scale (UNITS_PER_BIT), built from 1-bit slabs with a thin slit between them; the fractional
top (each weight's share of the scales stored once per block of 256 weights) is a light-blue slab of exactly that
height. A quiet glowing line marks the average over the whole model. Behind, small and out of focus (camera depth
of field), the card from the VRAM figure. Data: charts/data/weights_formats.json, entry "ours"; F32 is left out.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/bits_per_weight.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/bits_per_weight_draft.png] [--no-render]
"""
import argparse, json, math, os, sys, time
import bpy
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="900x600")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=os.path.join(HERE, "out", "bits_per_weight_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "bits_per_weight.layout.json"))
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))

data = json.load(open(os.path.join(HERE, "data", "weights_formats.json")))
O = data["ours"]
card_data = json.load(open(os.path.join(HERE, "data", "vram_gguf_3000.json")))

# ---------------------------------------------------------------- the numbers
# Whole bits each format stores per weight (llama.cpp block layouts, 256 weights per block); the rest of its
# bits per weight (8 x bytes / params, from the file's tensor table) is its share of the block's scales.
WHOLE = {"Q5_K": 5, "IQ4_XS": 4, "Q6_K": 6, "Q4_K": 4}
EXPECT_FRAC = {"Q5_K": 0.5, "IQ4_XS": 0.25, "Q6_K": 0.5625, "Q4_K": 0.5}
EXPECT_SUB = {"Q5_K": "69% of weights", "IQ4_XS": "21% of weights", "Q6_K": "5% of weights", "Q4_K": "5% of weights"}
cols = [{"type": "BF16", "bits": 16.0, "whole": 16, "frac": 0.0, "ref": True, "sub": "as released"}]
for t in sorted((t for t in O["types"] if t["type"] != "F32"), key=lambda t: -t["params"]):   # F32 left out
    bits = 8 * t["bytes"] / t["params"]
    share = t["params"] / O["text_params"]
    c = {"type": t["type"], "bits": bits, "whole": WHOLE[t["type"]], "frac": bits - WHOLE[t["type"]], "ref": False,
         "share": share, "sub": f"{share * 100:.0f}% of weights", "params": t["params"], "bytes": t["bytes"]}
    assert abs(c["frac"] - EXPECT_FRAC[c["type"]]) < 1e-9, c
    assert c["sub"] == EXPECT_SUB[c["type"]], c
    cols.append(c)
assert [c["type"] for c in cols] == ["BF16", "Q5_K", "IQ4_XS", "Q6_K", "Q4_K"]
AVG = 8 * O["bytes"] / O["text_params"]
assert f"{AVG:.2f}" == "5.24"


def bits_text(b):
    return f"{round(b, 2):g} bits"


# ---------------------------------------------------------------- scale and look
UNITS_PER_BIT = 1.0                  # height: 1 Blender unit = 1 bit per weight
COL_W, COL_D = 4.2, 4.2              # column footprint
GAP, REF_GAP = 2.2, 3.6              # between our columns; BF16 stands a little further apart
SLIT = 0.16                          # cut from the top of every slab except a column's last, so the top is exact
C = {"ref": "#8e8fa3", "ours": kit.COLOURS["weights"], "scales": "#9ec5f4", "avg": kit.LOOK["limit"]}
AVG_GLOW = 0.75                      # the average line: quiet, like the VRAM figure's limit rim
AVG_LINE = 0.0026                    # its thickness, fraction of the picture's width
ELEVATION, AZIMUTH, LENS = 26.4, 6.8, 80.0   # as the approved WebGL page's camera, through the series' long lens
REGION = (0.035, 0.80, 0.05, 0.86)   # where the row and its labels go (x0, x1, y0, y1); the card sits to its upper right
CARD_SCREEN = (0.865, 0.72, 0.32)    # the card's centre (x, y) and height on screen, as fractions
CARD_DEPTH = 2.4                     # the card's distance, in multiples of the focus distance
CARD_BLUR = 0.014                    # its blur circle, fraction of the picture's width
EM, SUB = kit.EM, kit.SUB_EM

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
rx, ry = W_PX, H_PX

# ---------------------------------------------------------------- the columns
mats = {"ref": kit.material("bf16", C["ref"], emit=0.10, rough=0.85, spec=0.12),
        "ours": kit.material("ours", C["ours"], emit=0.10, rough=0.85, spec=0.12),
        "scales": kit.material("scales", C["scales"], emit=0.08, rough=0.85, spec=0.12)}
xs, x = [], 0.0
for i in range(len(cols)):
    xs.append(x)
    x += COL_W + (REF_GAP if i == 0 else GAP)
row_len = xs[-1] + COL_W
col_objs = []
for i, c in enumerate(cols):
    pieces = [(b, b + 1, "bit") for b in range(c["whole"])] + ([(c["whole"], c["bits"], "scales")] if c["frac"] > 0 else [])
    c["pieces"], c["objs"] = [], []
    for k, (z0, z1, kind) in enumerate(pieces):
        last = k == len(pieces) - 1
        top = z1 if last else z1 - SLIT
        m = mats["scales"] if kind == "scales" else mats["ref" if c["ref"] else "ours"]
        ob = kit.cuboid(f"col_{c['type']}_{kind}_{k}", (xs[i], -COL_D / 2, z0 * UNITS_PER_BIT),
                        (xs[i] + COL_W, COL_D / 2, top * UNITS_PER_BIT), m)
        c["objs"].append(ob)
        c["pieces"].append({"kind": kind, "cell": [z0, z1], "slab_z": [z0 * UNITS_PER_BIT, top * UNITS_PER_BIT]})
    col_objs += c["objs"]
    c["xc"] = xs[i] + COL_W / 2

lo, hi = kit.world_bbox(col_objs)
pad = 2.6
base, base_info = kit.floating_base(lo, hi, margin=pad / row_len, dressing=False, drop=7.0, thickness=0.6)
y_front = base_info["y"][0]
geo = col_objs + base

# ---------------------------------------------------------------- text (measured once at size 1, placed after the camera)
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
T = []          # every text item: dict(ob, w_em, size, mat, align, kind...)


def text(name, body, size, mat, align_x="CENTER", align_y="BOTTOM_BASELINE"):
    ob, w, h = kit.text_object(f"txt_{name}", body, align_x, align_y)
    t = {"name": name, "body": body, "ob": ob, "w_em": w, "size": size, "mat": mat, "align_x": align_x}
    T.append(t)
    return t


for c in cols:
    c["t_bits"] = text(f"bits_{c['type']}", bits_text(c["bits"]), EM, ink)
    c["t_name"] = text(f"name_{c['type']}", c["type"], EM, ink)
    c["t_sub"] = text(f"sub_{c['type']}", c["sub"], SUB, ink2)
t_avg = text("avg", f"average {AVG:.2f} bits", EM, ink, "LEFT")
t_avg2 = text("avg_sub", "over the whole model", SUB, ink2, "LEFT")
LEGEND = [("ref", "as released"), ("ours", "in the file we ran"), ("scales", "scales (stored once per block of 256 weights)")]
t_leg = [text(f"legend_{k}", s, SUB, ink, "LEFT", "CENTER") for k, s in LEGEND]
avg_x0, avg_x1 = xs[1] - 0.6 * GAP, row_len + 0.6 * GAP
avg_y = -COL_D / 2 - 0.35


def layout():
    """Picture positions of every text item for the current camera: baseline (x, y) and its rectangle."""
    em_y, sub_y = EM * rx / ry, SUB * rx / ry
    for c in cols:
        top_back = kit.to_screen(scene, cam, (c["xc"], COL_D / 2, c["bits"] * UNITS_PER_BIT))
        tb = c["t_bits"]
        tb["x"], tb["y"] = top_back.x, top_back.y + 0.45 * em_y
        line = kit.to_screen(scene, cam, (c["xc"], avg_y, AVG * UNITS_PER_BIT)).y
        if not c["ref"] and c["bits"] < AVG:          # keep a short column's label clear above the average line
            tb["y"] = max(tb["y"], line + 0.62 * em_y)
        edge = kit.to_screen(scene, cam, (c["xc"], y_front, base_info["top"] - base_info["thickness"]))
        tn, ts = c["t_name"], c["t_sub"]
        tn["x"], tn["y"] = edge.x, edge.y - 0.55 * em_y - 0.72 * em_y
        ts["x"], ts["y"] = edge.x, tn["y"] - 0.30 * em_y - 0.95 * sub_y
    end = kit.to_screen(scene, cam, (avg_x1, avg_y, AVG * UNITS_PER_BIT))
    t_avg["x"], t_avg["y"] = end.x + 0.6 * EM, end.y - 0.36 * em_y
    t_avg2["x"], t_avg2["y"] = t_avg["x"], t_avg["y"] - 0.30 * em_y - 0.95 * sub_y
    xl, yl = 0.03, 0.955
    for (k, _), t in zip(LEGEND, t_leg):
        t["swatch_x"] = xl + 0.425 * SUB
        t["x"], t["y"] = xl + 1.3 * SUB, yl
        xl = t["x"] + t["w_em"] * SUB + 1.6 * SUB
    for t in T:
        w = t["w_em"] * t["size"]
        hy = t["size"] * rx / ry
        x0 = t["x"] - w / 2 if t["align_x"] == "CENTER" else t["x"]
        if t["name"].startswith("legend"):
            x0 = t["swatch_x"] - 0.425 * t["size"]
            t["rect"] = [x0, t["x"] + w, t["y"] - 0.5 * hy, t["y"] + 0.5 * hy]
        else:
            t["rect"] = [x0, x0 + w, t["y"] - 0.24 * hy, t["y"] + 0.74 * hy]


# ---------------------------------------------------------------- camera: the row and its labels fill REGION
cam = kit.make_camera(scene, LENS)
pts = kit.mesh_points(geo)
target = (lo + hi) / 2
dist = 2.5 * row_len
rx0, rx1, ry0, ry1 = REGION
fill = 0.97
for _ in range(14):
    kit.aim(cam, target, dist, direction)
    sp = [kit.to_screen(scene, cam, p) for p in pts]
    gx0, gx1, gy0, gy1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    layout()
    rects = [t["rect"] for t in T if not t["name"].startswith("legend")]
    x0, x1 = min([gx0] + [r[0] for r in rects]), max([gx1] + [r[1] for r in rects])
    y0, y1 = min([gy0] + [r[2] for r in rects]), max([gy1] + [r[3] for r in rects])
    gw, gh = gx1 - gx0, gy1 - gy0
    ox, oy = (x1 - x0) - gw, (y1 - y0) - gh
    z = min((fill * (rx1 - rx0) - ox) / gw, (fill * (ry1 - ry0) - oy) / gh)
    fw, fh = kit.frame_size(scene, cam, dist)
    R = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    U = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    target = target + R * ((x0 + x1) / 2 - (rx0 + rx1) / 2) * fw + U * ((y0 + y1) / 2 - (ry0 + ry1) / 2) * fh
    if abs(z - 1) < 0.001 and abs((x0 + x1) / 2 - (rx0 + rx1) / 2) < 0.001 and abs((y0 + y1) / 2 - (ry0 + ry1) / 2) < 0.001:
        break
    dist /= z
kit.aim(cam, target, dist, direction)
layout()

# ---------------------------------------------------------------- what is sized on screen: the average line, the text
focus_pt = Vector((xs[1] + (row_len - xs[1]) / 2, -COL_D / 2, 3.0 * UNITS_PER_BIT))
d_focus = kit.to_screen(scene, cam, focus_pt).z
fw_focus, _ = kit.frame_size(scene, cam, d_focus)
th = AVG_LINE * fw_focus
avg_line = kit.cuboid("avg_line", (avg_x0, avg_y - th / 2, AVG * UNITS_PER_BIT - th / 2),
                      (avg_x1, avg_y + th / 2, AVG * UNITS_PER_BIT + th / 2), kit.glow_material("avg", C["avg"], AVG_GLOW))
kit.no_shadow(avg_line)
d_text = kit.to_screen(scene, cam, (row_len / 2, y_front, base_info["top"])).z - 1.0     # in front of the base's edge
for t in T:
    kit.place_on_screen(scene, cam, t["ob"], t["x"], t["y"], d_text, t["size"], t["mat"])
swatches = []
for (k, _), t in zip(LEGEND, t_leg):
    sw = kit.swatch_object(f"swatch_{k}", C[k])
    kit.place_on_screen(scene, cam, sw, t["swatch_x"], t["y"], d_text, 0.85 * SUB)
    swatches.append(sw)

# ---------------------------------------------------------------- the card from the last picture, far behind, out of focus
card = kit.build_card(card_data, kit.view_direction(26.0, 38.0))
clo, chi = kit.world_bbox(card)
c_mid = (clo + chi) / 2
holder = bpy.data.objects.new("card", None)
scene.collection.objects.link(holder)
for ob in card:
    ob.parent = holder
d_card = CARD_DEPTH * d_focus
s, csx, csy, ch = 1.0, CARD_SCREEN[0], CARD_SCREEN[1], CARD_SCREEN[2]
aim_x, aim_y = csx, csy
for _ in range(6):
    centre = kit.to_world(scene, cam, aim_x, aim_y, d_card)
    to_cam = cam.matrix_world.translation - centre
    phi = math.atan2(to_cam.x, -to_cam.y)                      # azimuth the card is seen from
    rot = Matrix.Rotation(phi - math.radians(38.0), 4, "Z")     # so it shows the face it showed in its own picture
    holder.matrix_world = Matrix.Translation(centre) @ rot @ Matrix.Scale(s, 4) @ Matrix.Translation(-c_mid)
    bpy.context.view_layer.update()
    sp = [kit.to_screen(scene, cam, p) for p in kit.mesh_points([o for o in card if o.type == "MESH"])]
    bx0, bx1, by0, by1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    s *= ch / (by1 - by0)
    aim_x += csx - (bx0 + bx1) / 2
    aim_y += csy - (by0 + by1) / 2
card_rect = [bx0, bx1, by0, by1]

# depth of field: the columns sharp, the card blurred by CARD_BLUR of the picture's width
cam.data.dof.use_dof = True
cam.data.dof.focus_distance = d_focus
f_m = LENS / 1000.0
blur_m = CARD_BLUR * cam.data.sensor_width / 1000.0              # blur circle on the sensor, metres
aperture = blur_m * d_card * (d_focus - f_m) / (f_m * (d_card - d_focus))
cam.data.dof.aperture_fstop = f_m / aperture
cam.data.clip_end = d_card * 3

# ---------------------------------------------------------------- light
kit.stage_lights(direction, key=3.5, rim=2.0, key_turn=30, key_el=14, rim_turn=130)

# ---------------------------------------------------------------- checks and layout
rects = {t["name"]: t["rect"] for t in T}
names = list(rects)
overlaps = [[a, b] for i, a in enumerate(names) for b in names[i + 1:]
            if rects[a][0] < rects[b][1] and rects[b][0] < rects[a][1] and rects[a][2] < rects[b][3] and rects[b][2] < rects[a][3]]
over_card = [n for n, r in rects.items() if r[0] < card_rect[1] and card_rect[0] < r[1] and r[2] < card_rect[3] and card_rect[2] < r[3]]
line_hits = []
for t in T:
    r = t["rect"]
    a = kit.to_screen(scene, cam, (avg_x0, avg_y, AVG * UNITS_PER_BIT))
    b = kit.to_screen(scene, cam, (avg_x1, avg_y, AVG * UNITS_PER_BIT))
    for k in range(41):
        q = a.lerp(b, k / 40)
        if r[0] < q.x < r[1] and r[2] - 0.004 < q.y < r[3] + 0.004:
            line_hits.append(t["name"])
            break
inside = all(0.01 < r[0] and r[1] < 0.99 and 0.01 < r[2] and r[3] < 0.99 for r in rects.values())
dg = bpy.context.evaluated_depsgraph_get()
origin = cam.matrix_world.translation
hidden = []
for t in T:
    r = t["rect"]
    for fx in (0.05, 0.5, 0.95):
        for fy in (0.25, 0.75):
            p = kit.to_world(scene, cam, r[0] + fx * (r[1] - r[0]), r[2] + fy * (r[3] - r[2]), d_text)
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(("txt_", "swatch_")):
                hidden.append([t["name"], ob.name])
columns_out = []
for c in cols:
    lo_c, hi_c = kit.world_bbox(c["objs"])
    h = hi_c.z - lo_c.z
    columns_out.append({"type": c["type"], "bits": c["bits"], "whole_bits": c["whole"], "scales_bits": c["frac"],
                        "share_of_weights": c.get("share"), "label_above": c["t_bits"]["body"],
                        "label_below": [c["t_name"]["body"], c["t_sub"]["body"]],
                        "height_units": round(h, 6), "units_per_bit": h / c["bits"], "pieces": c["pieces"]})
layout_json = {
    "figure": "bits_per_weight",
    "scale": {"units_per_bit": UNITS_PER_BIT, "means": "1 Blender unit of height = 1 bit per weight",
              "slit_units": SLIT, "slit_rule": "cut from the top of every slab except a column's last, so each slab "
              "starts at its bit boundary and the column's top is exactly its bits"},
    "columns": columns_out,
    "max_deviation_units_per_bit": max(abs(c["units_per_bit"] - UNITS_PER_BIT) for c in columns_out),
    "average": {"bits": AVG, "line_z_centre": AVG * UNITS_PER_BIT, "label": [t_avg["body"], t_avg2["body"]]},
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 3),
               "focus_distance": round(d_focus, 3), "fstop": round(cam.data.dof.aperture_fstop, 4)},
    "card": {"depth": round(d_card, 2), "scale": round(s, 4), "screen_rect": [round(v, 4) for v in card_rect],
             "blur_fraction_of_width": CARD_BLUR},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rects.items()},
    "text_overlaps": overlaps, "text_over_card": over_card, "text_on_average_line": line_hits, "text_hidden": hidden, "text_inside_picture": inside,
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout_json)
print("LAYOUT", json.dumps({k: layout_json[k] for k in ("max_deviation_units_per_bit", "text_overlaps", "text_over_card", "text_on_average_line",
                                                      "text_hidden", "text_inside_picture")}))
print("HEIGHTS", [(c["type"], c["bits"], c["height_units"]) for c in columns_out])

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    pts = {"bf16_front": Vector((cols[0]["xc"], -COL_D / 2, 7.5)), "bf16_left_side": Vector((xs[0], 0, 7.5)),
           "q5k_bit_front": Vector((cols[1]["xc"], -COL_D / 2, 2.4)), "q5k_scales_front": Vector((cols[1]["xc"], -COL_D / 2, 5.42)),
           "iq4_scales_front": Vector((cols[2]["xc"], -COL_D / 2, 4.12)), "q6k_scales_front": Vector((cols[3]["xc"], -COL_D / 2, 6.3)),
           "q5k_top": Vector((cols[1]["xc"], 0, 5.5))}
    layout_json["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1),
                                   "colours": kit.sample_colours(args.out, scene, cam, pts), "targets": C}
    kit.write_json(args.layout, layout_json)
    print("RENDER", round(secs, 1), "s", json.dumps(layout_json["draft_render"]["colours"]))
