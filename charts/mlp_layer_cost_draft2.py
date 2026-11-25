"""Figure: one MLP layer of Qwen3.8-27B in training memory, fully trained (BF16) vs QLoRA, plus the low-rank idea.
(Draft 2. Draft 1 is reproducible with charts/mlp_layer_cost_draft1.py.)

Bottom, the memory: two bars on one floating base, starting on the same line, length to scale in MiB
(MIB_PER_UNIT): fully trained = weights | gradients | optimizer state; QLoRA = frozen 4-bit weights + the adapter,
a tiny bow-tie (the low-rank shape) at its true length. A magnified copy of the bow-tie sits in front. The bow-tie is
built from four equal slices with slits (weights, gradients, 2 x optimizer state: the adapter's 1 : 1 : 2), the same
object in all three places.
Top, the idea (not to scale): the frozen matrix W as a big solid slab in its 17,408 x 5,120 aspect, and in front of it
the adapter as a thin bow-tie beside it: A's wide end = W's 5,120 side, narrowing to the rank-16 neck, B widening
to W's 17,408 side. Data: charts/data/mlp_layer_cost.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/mlp_layer_cost.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/mlp_layer_cost_draft2.png] [--no-render]
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
ap.add_argument("--out", default=os.path.join(HERE, "out", "mlp_layer_cost_draft2.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "mlp_layer_cost_draft2.layout.json"))
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
    "q_sum": f"= {q_frozen['label']} {mib(q_frozen['mib'])} + adapter {ad_mib:.1f}",
    "adapter2": "4 equal slices: weights, gradients, 2 × optimizer state",
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
assert TXT["q_sum"] == "= frozen 4-bit weights 132 + adapter 16.5" and TXT["adapter"] == "adapter 16.5 MiB (1.08M weights, 0.4%)"
assert TXT["count"] == "one MLP layer: 267.4M weights"


# ---------------------------------------------------------------- scale and look
MIB_PER_UNIT = 20.0                  # bar length: 1 unit = 20 MiB
BAR_H, BAR_D = 2.0, 4.0              # bar cross-section
Y_BACK = 16.0                        # the fully trained bar, behind; the QLoRA bar at y = 0
DIM_OFF = BAR_D / 2 + 1.1            # each row's dimension line (its whole length = its total) runs this far in front
A_FRAC = LR["A"][1] / LR["B"][0]     # A's wide end (5,120) against B's (17,408)
NECK = 0.05                          # the rank-16 neck, a fraction of B's end (16 / 17,408 would be invisible)
BT_ASPECT = 0.4                      # the bow-tie everywhere: length = 0.4 x B's end
K_CALLOUT = 8.0                      # the magnified copy (also used in a text line, so defined before TXT)
W_X, W_Y, W_Z = 34.0, 10.0, 5.0      # the idea's W: 17,408 x 5,120 lying flat, a solid slab, twice A/B's stack
ELEVATION, AZIMUTH, LENS = 26.0, -12.0, 80.0
C = {k: kit.COLOURS[k] for k in ("weights", "gradients", "optimizer", "frozen", "adapter")}
LINE_OF = {"adapter_weights": "weights", "adapter_gradients": "gradients", "adapter_optimizer": "optimizer"}

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
mats = {k: kit.material(f"m_{k}", v, emit=0.45 if k == "adapter" else 0.10, rough=0.85, spec=0.12) for k, v in C.items()}
# (the adapter's flat sheets face up, where the low key light barely reaches: a self-lit share keeps them green)


def bowtie(name, along, s0, L, w_b, c, z0, layers, top=None, slit=0.0):
    """A flat bow-tie lying on z0: A from width A_FRAC*w_b at s0 to the neck at s0+L/2, B to w_b at s0+L.
    along 'x': length along +x, widths along y about c; 'y': length along +y, widths along x about c.
    layers: [(material, thickness)] stacked upward with `slit` between them. Returns its objects."""
    obs, z = [], z0
    for i, (m, t) in enumerate(layers):
        last = i == len(layers) - 1
        top_m = top or m
        for part, (sa, sb, wa, wb) in (("A", (s0, s0 + L / 2, A_FRAC * w_b, NECK * w_b)), ("B", (s0 + L / 2, s0 + L, NECK * w_b, w_b))):
            if along == "x":
                q = [(sa, c - wa / 2), (sb, c - wb / 2), (sb, c + wb / 2), (sa, c + wa / 2)]
            else:
                q = [(c + wa / 2, sa), (c + wb / 2, sb), (c - wb / 2, sb), (c - wa / 2, sa)]
            v = [(x, y, z) for x, y in q] + [(x, y, z + t) for x, y in q]
            f = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
            ob = kit.mesh_object(f"{name}_{part}_{i}", v, f, [m, top_m], [0, 1 if last else 0, 0, 0, 0, 0])
            obs.append(ob)
        z += t + slit
    return obs


# the adapter's memory is weights : gradients : optimizer state = 1 : 1 : 2, so the bow-tie is four equal slices,
# bottom to top in the order the fully trained row reads left to right; the reader counts slices
SLICE_UNIT = sorted(p["mib"] for p in q_adapter)[0]
SLICES = []
for p in q_adapter:
    n = round(p["mib"] / SLICE_UNIT)
    assert abs(n * SLICE_UNIT - p["mib"]) < 0.02 * p["mib"], (p, SLICE_UNIT)
    SLICES += [LINE_OF[p["line"]]] * n
assert SLICES == ["weights", "gradients", "optimizer", "optimizer"], SLICES


def sliced(t):
    return [(mats[line], t) for line in SLICES]


# ---------------------------------------------------------------- the memory rows
rows, x = [], 0.0
for p in full["parts"]:
    L = p["mib"] / MIB_PER_UNIT
    rows.append(kit.cuboid(f"full_{p['line']}", (x, Y_BACK - BAR_D / 2, 0), (x + L, Y_BACK + BAR_D / 2, BAR_H), mats[p["line"]]))
    x += L
full_len = x
fz_len = q_frozen["mib"] / MIB_PER_UNIT
rows.append(kit.cuboid("q_frozen", (0, -BAR_D / 2, 0), (fz_len, BAR_D / 2, BAR_H), mats["frozen"]))
ad_len = ad_mib / MIB_PER_UNIT                        # the adapter's true length (its MiB)
ad_w = ad_len / BT_ASPECT
ROW_SLIT = 0.12
sliver = bowtie("q_adapter", "x", fz_len, ad_len, ad_w, 0.0, 0.0, sliced((BAR_H - 3 * ROW_SLIT) / 4), slit=ROW_SLIT)   # as tall as the bar
rows += sliver
q_len = fz_len + ad_len
# the magnified copy: in front of the rows, to the right, clear of the QLoRA row
c_len, c_w = ad_len * K_CALLOUT, ad_w * K_CALLOUT
cx0, cyc = 34.0, -c_w / 2 - 8.0
callout = bowtie("callout", "x", cx0, c_len, c_w, cyc, 0.0, sliced(0.9), slit=0.3)
lo, hi = kit.world_bbox(rows + callout)
lo.z = 0.0
base, base_info = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), dressing=False, drop=10.0, thickness=0.6)

# ---------------------------------------------------------------- the idea, behind and above: not to scale
IDEA_Y, IDEA_Z = Y_BACK + 40.0, 24.0
idea_x0 = full_len * 0.33
wy0 = IDEA_Y
idea = [kit.cuboid("idea_W", (idea_x0, wy0, IDEA_Z), (idea_x0 + W_X, wy0 + W_Y, IDEA_Z + W_Z), mats["frozen"])]
tile = kit.material("m_frozen_tile", kit.COLOURS["frozen"], emit=0.14, rough=0.85, spec=0.12)
nx, ny, gap = 17, 5, 0.14                             # a 17 x 5 grid of 1,024 x 1,024 blocks: clearly a matrix
for i in range(nx):
    for j in range(ny):
        tx0, ty0 = idea_x0 + i * W_X / nx + gap / 2, wy0 + j * W_Y / ny + gap / 2
        idea.append(kit.cuboid(f"idea_W_tile_{i}_{j}", (tx0, ty0, IDEA_Z + W_Z), (tx0 + W_X / nx - gap, ty0 + W_Y / ny - gap, IDEA_Z + W_Z + 0.08), tile))
bt_len = BT_ASPECT * W_X                              # B's wide end = W's 17,408 side, the same bow-tie shape
bt_x0 = idea_x0 + W_X + 0.8                           # A's wide end (= W's 5,120 side) against W's right edge
idea += bowtie("idea_AB", "x", bt_x0, bt_len, W_X, wy0 + W_Y / 2, IDEA_Z, sliced(0.5), slit=0.18)
ilo, ihi = kit.world_bbox(idea)
idea_base, idea_info = kit.floating_base(Vector((ilo.x, ilo.y, IDEA_Z)), ihi, margin=0.08, dressing=False, drop=7.0, thickness=0.6)

# ---------------------------------------------------------------- text
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
lead = kit.glow_material("lead", kit.LOOK["leader"], 1.0)
T = {}


def text(key, size, mat, ax="CENTER", ay="BOTTOM_BASELINE"):
    ob, w, h = kit.text_object(f"txt_{key}", TXT[key], ax, ay)
    T[key] = {"ob": ob, "w_em": w, "size": size, "mat": mat, "align": ax, "valign": ay}


for p in full["parts"]:
    text(f"seg_{p['line']}", kit.EM, ink)
text("full_head", kit.EM, ink, "RIGHT", "CENTER")
text("q_head", kit.EM, ink, "RIGHT", "CENTER")
text("count", kit.SUB_EM, ink2, "RIGHT", "CENTER")
text("q_sum", kit.SUB_EM, ink2, "RIGHT", "CENTER")
text("adapter", 1.15 * kit.EM, ink, "LEFT", "CENTER")
text("adapter2", kit.SUB_EM, ink2, "LEFT", "CENTER")
text("W", kit.SUB_EM, ink, "RIGHT", "CENTER")
text("A", kit.SUB_EM, ink, "CENTER", "CENTER")
text("B", kit.SUB_EM, ink, "LEFT", "CENTER")
text("rank", kit.SUB_EM, ink, "CENTER", "CENTER")


def scr(p):
    return kit.to_screen(scene, cam, p)


def layout():
    em_y = kit.EM * rx / ry
    pos = {}
    x = 0.0
    for p in full["parts"]:
        L = p["mib"] / MIB_PER_UNIT
        s = scr((x + L / 2, Y_BACK + BAR_D / 2, BAR_H))
        pos[f"seg_{p['line']}"] = (s.x, s.y + 0.55 * em_y)
        x += L
    for key, y in (("full_head", Y_BACK), ("q_head", 0.0)):     # at the start of the row's dimension line
        s = scr((0, y - DIM_OFF, 0))
        pos[key] = (s.x - 1.0 * kit.EM, s.y + (0.45 * em_y if key == "q_head" else 0.0))
    pos["q_sum"] = (pos["q_head"][0], pos["q_head"][1] - 1.05 * em_y)
    pos["count"] = (pos["full_head"][0], pos["full_head"][1] + 1.6 * em_y)
    s = scr((cx0 + c_len, cyc, 2.0))
    pos["adapter"] = (s.x + 1.4 * kit.EM, s.y + 0.45 * em_y)
    pos["adapter2"] = (pos["adapter"][0], pos["adapter"][1] - 1.2 * em_y)
    s = scr((idea_x0, wy0 + W_Y / 2, IDEA_Z + W_Z / 2))              # W: left of the slab
    pos["W"] = (s.x - 1.0 * kit.EM, s.y)
    cy = wy0 + W_Y / 2
    s = scr((bt_x0 + bt_len / 4, cy - A_FRAC * W_X / 2, IDEA_Z))     # A: in front of its front edge
    pos["A"] = (s.x, s.y - 1.3 * em_y)
    s = scr((bt_x0 + bt_len, cy, IDEA_Z))                            # B: right of its wide end
    pos["B"] = (s.x + 1.0 * kit.EM, s.y)
    s = scr((bt_x0 + bt_len / 2, cy + NECK * W_X / 2, IDEA_Z))       # rank: just behind the neck
    pos["rank"] = (s.x, s.y + 1.0 * em_y)
    rects = {}
    for k, t in T.items():
        x, y = pos[k]
        w, hy = t["w_em"] * t["size"], t["size"] * rx / ry
        x0 = x - w / 2 if t["align"] == "CENTER" else (x - w if t["align"] == "RIGHT" else x)
        rects[k] = [x0, x0 + w, y - 0.5 * hy, y + 0.5 * hy] if t["valign"] == "CENTER" else [x0, x0 + w, y - 0.24 * hy, y + 0.74 * hy]
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
d_text = scr((0, base_info["y"][0], 0)).z - 1.0
for k, t in T.items():
    kit.place_on_screen(scene, cam, t["ob"], t["x"], t["y"], d_text, t["size"], t["mat"])

# zoom guides: from the sliver's two ends to the magnified copy's two ends, low along the base
fw, _ = kit.frame_size(scene, cam, d_text)
rad = kit.LINE * fw / 2
for nm, p0, p1 in (("a", (fz_len, -A_FRAC * ad_w / 2, 0.05), (cx0, cyc - A_FRAC * c_w / 2, 0.05)),
                   ("b", (q_len, ad_w / 2, 0.05), (cx0 + c_len, cyc + c_w / 2, 0.05))):
    kit.polyline(f"zoom_{nm}", [Vector(p0), Vector(p1)], rad, lead)
for nm, y, L in (("full", Y_BACK, full_len), ("qlora", 0.0, q_len)):   # the row total spans the whole row
    yd = y - DIM_OFF
    kit.polyline(f"zoom_dim_{nm}", [Vector((0, yd, 0.05)), Vector((L, yd, 0.05))], rad, lead)
    for xe in (0.0, L):
        kit.polyline(f"zoom_dim_{nm}_{xe:.0f}", [Vector((xe, yd - 0.55, 0.05)), Vector((xe, yd + 0.55, 0.05))], rad, lead)
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
for p in full["parts"]:
    lo_, hi_ = kit.world_bbox([bpy.data.objects[f"full_{p['line']}"]])
    lens_out[f"full_{p['line']}"] = {"mib": p["mib"], "length_units": round(hi_.x - lo_.x, 5), "mib_per_unit": p["mib"] / (hi_.x - lo_.x)}
lo_, hi_ = kit.world_bbox([bpy.data.objects["q_frozen"]])
lens_out["qlora_frozen"] = {"mib": q_frozen["mib"], "length_units": round(hi_.x - lo_.x, 5), "mib_per_unit": q_frozen["mib"] / (hi_.x - lo_.x)}
lo_, hi_ = kit.world_bbox(sliver)
lens_out["qlora_adapter"] = {"mib": ad_mib, "length_units": round(hi_.x - lo_.x, 5), "mib_per_unit": ad_mib / (hi_.x - lo_.x)}
lo_w, hi_w = kit.world_bbox([idea[0]])
ab = [o for o in idea if o.name.startswith("idea_AB")]
lo_b, hi_b = kit.world_bbox(ab)
layout_json = {
    "figure": "mlp_layer_cost", "draft": 2,
    "scale": {"mib_per_unit_length": MIB_PER_UNIT, "bar_cross_section": [BAR_H, BAR_D], "callout_magnification": K_CALLOUT,
              "idea": "not to scale"},
    "lengths": lens_out,
    "max_deviation_mib_per_unit": max(abs(v["mib_per_unit"] - MIB_PER_UNIT) for v in lens_out.values()),
    "totals": {"full_units": round(full_len, 4), "qlora_units": round(q_len, 4), "ratio": round(full_len / q_len, 2)},
    "idea": {"W_slab": [W_X, W_Y, W_Z], "W_volume": round(W_X * W_Y * W_Z, 1),
             "AB_sheet_extent": [round(hi_b.x - lo_b.x, 3), round(hi_b.y - lo_b.y, 3), round(hi_b.z - lo_b.z, 3)],
             "AB_volume": round(4 * 0.5 * (W_X * (1 + NECK) / 2 + W_X * (A_FRAC + NECK) / 2) * bt_len / 2, 1)},
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rects.items()},
    "text_overlaps": overlaps, "text_hidden": sorted(hidden), "text_inside_picture": inside,
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout_json)
print("LAYOUT", json.dumps({k: layout_json[k] for k in ("max_deviation_mib_per_unit", "totals", "idea", "text_overlaps", "text_hidden", "text_inside_picture")}))

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout_json["draft_render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout_json)
    print("RENDER", round(secs, 1), "s")
