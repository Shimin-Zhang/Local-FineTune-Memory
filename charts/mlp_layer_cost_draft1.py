"""Figure: one MLP layer of Qwen3.8-27B in training memory, fully trained (BF16) vs QLoRA, plus the low-rank idea.

Bottom: the memory. Two bars on one floating base, both starting on the same line, length to scale in MiB
(MIB_PER_UNIT): fully trained = weights | gradients | optimizer state; QLoRA = frozen 4-bit weights + the adapter.
The adapter piece has the low-rank shape (A narrowing to the rank-16 neck, B widening), at its true length; its
three memory parts are stripes through its depth in the same three colours (each adapter matrix holds its weights,
their gradients and the optimizer state). A magnified copy of it sits beside the bar.
Top: the idea, not to scale: the frozen matrix W and the adapter (A, B) in the same shape and colours.
Data: charts/data/mlp_layer_cost.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/mlp_layer_cost.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/mlp_layer_cost_draft.png] [--no-render]
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
ap.add_argument("--out", default=os.path.join(HERE, "out", "mlp_layer_cost_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "mlp_layer_cost.layout.json"))
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX

data = json.load(open(os.path.join(HERE, "data", "mlp_layer_cost.json")))
full, qlora = data["rows"]
layer = data["layer"]
LR = data["low_rank"]
q_frozen = next(p for p in qlora["parts"] if p.get("frozen"))
q_adapter = [p for p in qlora["parts"] if not p.get("frozen")]
ad_mib = sum(p["mib"] for p in q_adapter)
assert abs(ad_mib - qlora["adapter_total_mib"]) < 0.02 and abs(sum(p["mib"] for p in full["parts"]) - full["total_mib"]) < 1e-6


def mib(x):
    return f"{x:,.0f}" if x >= 100 else f"{x:.1f}"


SHORT = {"weights": "weights", "gradients": "gradients", "optimizer": "optimizer state"}
TXT = {
    "full_head": f"{full['label']}  {mib(full['total_mib'])} MiB",
    "q_head": f"{qlora['label']}  {mib(qlora['total_mib'])} MiB",
    "frozen": f"{q_frozen['label']} {mib(q_frozen['mib'])} MiB",
    "adapter": f"adapter {ad_mib:.1f} MiB ({layer['adapter_weights'] / 1e6:.2f}M weights, {layer['adapter_share_pct']:.1f}%)",
    "count": f"one MLP layer: {layer['weights'] / 1e6:.1f}M weights",
    "W": f"W, frozen ({LR['W'][0]:,} × {LR['W'][1]:,})",
    "A": f"A ({LR['A'][0]} × {LR['A'][1]:,})",
    "B": f"B ({LR['B'][0]:,} × {LR['B'][1]})",
    "rank": f"rank {layer['adapter_rank']}",
}
for p in full["parts"]:
    TXT[f"seg_{p['line']}"] = f"{SHORT[p['line']]} {mib(p['mib'])} MiB"
assert TXT["full_head"] == "fully trained (BF16)  2,040 MiB" and TXT["q_head"] == "QLoRA  148 MiB"
assert TXT["frozen"] == "frozen 4-bit weights 132 MiB", TXT["frozen"]
assert TXT["adapter"] == "adapter 16.5 MiB (1.08M weights, 0.4%)", TXT["adapter"]
assert TXT["count"] == "one MLP layer: 267.4M weights"

# ---------------------------------------------------------------- scale and look
MIB_PER_UNIT = 20.0                  # bar length: 1 unit = 20 MiB
BAR_H, BAR_D = 2.0, 4.0              # bar cross-section
Y_BACK = 20.0                        # the fully trained bar, behind; the QLoRA bar at y = 0
A_FRAC = LR["A"][1] / LR["B"][0]     # A's wide end (5,120) against B's (17,408)
NECK = 0.07                          # the rank-16 neck, as a fraction of B's end (16 / 17,408 would be invisible)
AB_ASPECT = 1.6                      # the adapter shape everywhere: length = 1.6 x the height of B's end
K_CALLOUT = 12.0                     # the magnified copy: x12
CALL_D = 6.0                         # its depth (and the idea's)
IDEA_H = 17.0                        # the idea: W's height = B's end (both 17,408)
ELEVATION, AZIMUTH, LENS = 26.0, -12.0, 80.0
C = {k: kit.COLOURS[k] for k in ("weights", "gradients", "optimizer", "frozen")}
LINE_OF = {"adapter_weights": "weights", "adapter_gradients": "gradients", "adapter_optimizer": "optimizer"}
STRIPES = [(LINE_OF[p["line"]], p["mib"] / ad_mib) for p in q_adapter]   # front to back through the adapter's depth

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
mats = {k: kit.material(f"m_{k}", v, emit=0.10, rough=0.85, spec=0.12) for k, v in C.items()}


def adapter_shape(name, x0, L, H, zc, yc, D):
    """The low-rank shape: A tapers from A_FRAC*H to the neck over L/2, B widens from the neck to H; the three
    memory parts as stripes through the depth. Returns its objects."""
    obs, y = [], yc - D / 2
    for line, f in STRIPES:
        y1 = y + f * D
        obs.append(kit.taper_prism(f"{name}_A_{line}", x0, x0 + L / 2, A_FRAC * H, NECK * H, zc, y, y1, mats[line]))
        obs.append(kit.taper_prism(f"{name}_B_{line}", x0 + L / 2, x0 + L, NECK * H, H, zc, y, y1, mats[line]))
        y = y1
    return obs


# ---------------------------------------------------------------- the memory rows
rows = []
x = 0.0
for p in full["parts"]:
    L = p["mib"] / MIB_PER_UNIT
    rows.append(kit.cuboid(f"full_{p['line']}", (x, Y_BACK - BAR_D / 2, 0), (x + L, Y_BACK + BAR_D / 2, BAR_H), mats[p["line"]]))
    x += L
full_len = x
fz_len = q_frozen["mib"] / MIB_PER_UNIT
rows.append(kit.cuboid("q_frozen", (0, -BAR_D / 2, 0), (fz_len, BAR_D / 2, BAR_H), mats["frozen"]))
ad_len = ad_mib / MIB_PER_UNIT
ad_h = ad_len / AB_ASPECT                             # true length (its MiB); the shape sets its height
sliver = adapter_shape("q_adapter", fz_len, ad_len, ad_h, BAR_H / 2, 0.0, BAR_D)
rows += sliver
q_len = fz_len + ad_len
# the magnified copy, floating a little in front of the QLoRA row and to its right
cx0, cyc = q_len + 10.0, -3.0
c_len, c_h = ad_len * K_CALLOUT, ad_h * K_CALLOUT
c_zc = c_h / 2 + 0.8
callout = adapter_shape("callout", cx0, c_len, c_h, c_zc, cyc, CALL_D)
lo, hi = kit.world_bbox(rows + callout)
lo.z = 0.0
base, base_info = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), dressing=False, drop=10.0, thickness=0.6)

# ---------------------------------------------------------------- the idea, behind and above: not to scale
IDEA_Y, IDEA_Z = Y_BACK + 34.0, 20.0
w_w = IDEA_H * A_FRAC                                 # W is 17,408 x 5,120: the same aspect as the adapter's ends
idea_x0 = full_len * 0.30
idea = [kit.cuboid("idea_W", (idea_x0, IDEA_Y - CALL_D / 2, IDEA_Z), (idea_x0 + w_w, IDEA_Y + CALL_D / 2, IDEA_Z + IDEA_H), mats["frozen"])]
ab_x0 = idea_x0 + w_w + 6.0
ab_len = IDEA_H * AB_ASPECT                           # the same shape as the piece in the row
idea += adapter_shape("idea_AB", ab_x0, ab_len, IDEA_H, IDEA_Z + IDEA_H / 2, IDEA_Y, CALL_D)
ilo, ihi = kit.world_bbox(idea)
idea_base, idea_info = kit.floating_base(Vector((ilo.x, ilo.y, IDEA_Z)), ihi, margin=0.12, dressing=False, drop=7.0, thickness=0.6)

# ---------------------------------------------------------------- text
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
lead = kit.glow_material("lead", kit.LOOK["leader"], 1.0)
T = {}


def text(key, size, mat, ax="CENTER", ay="BOTTOM_BASELINE"):
    ob, w, h = kit.text_object(f"txt_{key}", TXT[key], ax, ay)
    T[key] = {"ob": ob, "w_em": w, "size": size, "mat": mat, "align": ax}


for p in full["parts"]:
    text(f"seg_{p['line']}", kit.EM, ink)
text("full_head", kit.EM, ink, "RIGHT", "CENTER")
text("q_head", kit.EM, ink, "RIGHT", "CENTER")
text("count", kit.SUB_EM, ink2, "RIGHT", "CENTER")
text("frozen", kit.EM, ink, "CENTER")
text("adapter", 1.15 * kit.EM, ink, "LEFT", "CENTER")
text("W", kit.SUB_EM, ink, "CENTER")
text("A", kit.SUB_EM, ink, "RIGHT")
text("B", kit.SUB_EM, ink, "LEFT")
text("rank", kit.SUB_EM, ink, "CENTER")


def scr(p):
    return kit.to_screen(scene, cam, p)


def layout():
    em_y = kit.EM * rx / ry
    pos = {}
    x = 0.0
    for p in full["parts"]:                                         # centred over each segment of the full bar
        L = p["mib"] / MIB_PER_UNIT
        s = scr((x + L / 2, Y_BACK + BAR_D / 2, BAR_H))
        pos[f"seg_{p['line']}"] = (s.x, s.y + 0.55 * em_y)
        x += L
    for key, y in (("full_head", Y_BACK), ("q_head", 0.0)):         # row heads, left of the bars' common start
        s = scr((0, y - BAR_D / 2, BAR_H / 2))
        pos[key] = (s.x - 1.2 * kit.EM, s.y)
    s = scr((0, Y_BACK - BAR_D / 2, BAR_H / 2))
    pos["count"] = (s.x - 1.2 * kit.EM, s.y + 2.1 * em_y)
    s = scr((fz_len / 2, -BAR_D / 2, 0))
    pos["frozen"] = (s.x, s.y - 1.5 * em_y)
    s0 = scr((cx0 + c_len, cyc - CALL_D / 2, c_zc))
    pos["adapter"] = (s0.x + 1.6 * kit.EM, s0.y)
    sw = scr((idea_x0 + w_w / 2, IDEA_Y + CALL_D / 2, IDEA_Z + IDEA_H))
    pos["W"] = (sw.x, sw.y + 0.6 * em_y)
    neck_x = ab_x0 + ab_len / 2
    sn = scr((neck_x, IDEA_Y - CALL_D / 2, IDEA_Z))                # A's label ends left of the neck, B's starts right of it
    pos["A"] = (sn.x - 0.5 * kit.EM, sn.y - 1.4 * em_y)
    pos["B"] = (sn.x + 0.5 * kit.EM, sn.y - 1.4 * em_y)
    st = scr((neck_x, IDEA_Y - CALL_D / 2, IDEA_Z + IDEA_H / 2 + NECK * IDEA_H / 2))
    pos["rank"] = (st.x, st.y + 1.2 * em_y)
    rects = {}
    for k, t in T.items():
        x, y = pos[k]
        w, hy = t["w_em"] * t["size"], t["size"] * rx / ry
        x0 = x - w / 2 if t["align"] == "CENTER" else (x - w if t["align"] == "RIGHT" else x)
        if k in ("full_head", "q_head", "count", "adapter"):
            rects[k] = [x0, x0 + w, y - 0.5 * hy, y + 0.5 * hy]
        else:
            rects[k] = [x0, x0 + w, y - 0.24 * hy, y + 0.74 * hy]
        t["x"], t["y"] = x, y
    return rects


# ---------------------------------------------------------------- camera: everything in frame
cam = kit.make_camera(scene, LENS)
geo = rows + callout + base + idea + idea_base
pts = kit.mesh_points(geo)
lo_all = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi_all = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
target, dist = (lo_all + hi_all) / 2, 1.6 * (hi_all - lo_all).length
for _ in range(16):
    kit.aim(cam, target, dist, direction)
    sp = [scr(p) for p in pts]
    gx0, gx1, gy0, gy1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    rr = list(layout().values())
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
rects = layout()
d_text = scr((0, base_info["y"][0], 0)).z - 1.0            # in front of the base's front edge
for k, t in T.items():
    kit.place_on_screen(scene, cam, t["ob"], t["x"], t["y"], d_text, t["size"], t["mat"])

# zoom guides: from the sliver's ends to the magnified copy's ends
fw, _ = kit.frame_size(scene, cam, d_text)
rad = kit.LINE * fw / 2
for z_s, z_c in ((BAR_H / 2 + ad_h / 2, c_zc + c_h / 2), (BAR_H / 2 - ad_h / 2, c_zc - c_h / 2)):
    p0 = Vector((q_len, -BAR_D / 2, z_s))
    p1 = Vector((cx0, cyc - CALL_D / 2, z_c))
    kit.polyline(f"zoom_{z_s}", [p0, p1], rad, lead)
kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-50, key_el=14, rim_turn=-125)

# ---------------------------------------------------------------- checks and layout
names = list(rects)
overlaps = [[p, q] for i, p in enumerate(names) for q in names[i + 1:]
            if rects[p][0] < rects[q][1] and rects[q][0] < rects[p][1] and rects[p][2] < rects[q][3] and rects[q][2] < rects[p][3]]
inside = all(0.01 < r[0] and r[1] < 0.99 and 0.01 < r[2] and r[3] < 0.99 for r in rects.values())
dg = bpy.context.evaluated_depsgraph_get()
origin = cam.matrix_world.translation
hidden = set()
for n, r in rects.items():
    for fx in (0.05, 0.5, 0.95):
        for fy in (0.25, 0.75):
            p = kit.to_world(scene, cam, r[0] + fx * (r[1] - r[0]), r[2] + fy * (r[3] - r[2]), d_text)
            v = p - origin
            hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(("txt_", "zoom_")):
                hidden.add((n, ob.name))
lens_out = {}
for nm, parts, L0 in (("full", full["parts"], 0.0),):
    x = 0.0
    for p in parts:
        ob = bpy.data.objects[f"full_{p['line']}"]
        lo_, hi_ = kit.world_bbox([ob])
        lens_out[f"full_{p['line']}"] = {"mib": p["mib"], "length_units": round(hi_.x - lo_.x, 5), "mib_per_unit": p["mib"] / (hi_.x - lo_.x)}
lo_, hi_ = kit.world_bbox([bpy.data.objects["q_frozen"]])
lens_out["qlora_frozen"] = {"mib": q_frozen["mib"], "length_units": round(hi_.x - lo_.x, 5), "mib_per_unit": q_frozen["mib"] / (hi_.x - lo_.x)}
lo_, hi_ = kit.world_bbox(sliver)
lens_out["qlora_adapter"] = {"mib": ad_mib, "length_units": round(hi_.x - lo_.x, 5), "mib_per_unit": ad_mib / (hi_.x - lo_.x),
                             "stripes_front_to_back": [[l, round(f, 4)] for l, f in STRIPES]}
layout_json = {
    "figure": "mlp_layer_cost", "scale": {"mib_per_unit_length": MIB_PER_UNIT, "bar_cross_section": [BAR_H, BAR_D],
                                          "callout_magnification": K_CALLOUT, "idea": "not to scale"},
    "lengths": lens_out,
    "max_deviation_mib_per_unit": max(abs(v["mib_per_unit"] - MIB_PER_UNIT) for v in lens_out.values()),
    "totals": {"full_units": round(full_len, 4), "qlora_units": round(q_len, 4), "ratio": round(full_len / q_len, 2),
               "adapter_share_of_qlora_row": round(ad_len / q_len, 4)},
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rects.items()},
    "text_overlaps": overlaps, "text_hidden": sorted(hidden), "text_inside_picture": inside,
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout_json)
print("LAYOUT", json.dumps({k: layout_json[k] for k in ("max_deviation_mib_per_unit", "totals", "text_overlaps", "text_hidden", "text_inside_picture")}))

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout_json["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout_json)
    print("RENDER", round(secs, 1), "s")
