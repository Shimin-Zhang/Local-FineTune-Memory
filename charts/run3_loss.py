"""Figure: run 3's loss curve (Qwen3.8-27B QLoRA on the 2,000 diorama scenes, two passes, one scene per update).

An ordinary line chart as a diorama piece: an upright chart board on the series' floating circuit-board base, seen
head-on (a slight downward tilt shows the base). Held-out loss is a red tube with a low-poly marker at each of its
9 evaluations; training loss (smoothed) is a thinner blue tube, drawn only where its centered window is full (the
shrinking window at either end is not the run's loss: it starts below the untuned value and rises at the end). Both tubes are built along the camera's rays, so
their depth in front of the board never moves them on screen: the curve projects exactly onto the chart's axes.
A thin glowing post marks the start of pass 2; a faint sheet fills the pass-2 gap between seen and unseen scenes.
Every number comes from charts/data/run3_loss.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/run3_loss.py -- \
    [--size 2400x1600] [--samples 256] [--out charts/out/run3_loss.png] [--no-render] [--device gpu|cpu]
"""
import argparse, json, math, os, re, sys, time
import bpy, bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="2400x1600")
ap.add_argument("--samples", type=int, default=256)
ap.add_argument("--out", default=os.path.join(HERE, "out", "run3_loss.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "run3_loss.layout.json"))
ap.add_argument("--data", default=os.path.join(HERE, "data", "run3_loss.json"))
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--device", default="gpu", choices=["gpu", "cpu"], help="gpu: Cycles on CUDA (OptiX fails on this driver)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))

# ---------------------------------------------------------------- data
data = json.load(open(args.data))
held = [tuple(p) for p in data["held_out"]["points"]]
train_all = [tuple(p) for p in data["train_smoothed"]["points"]]
samples = [tuple(p) for p in data["train_samples"]["points"]]
WIN = int(re.search(r"mean of (\d+) logged samples", data["train_smoothed"]["note"]).group(1))   # 25
HALF = (WIN - 1) // 2
gaps = [b[0] - a[0] for a, b in zip(samples, samples[1:])]
SPACING = max(set(gaps), key=gaps.count)                                                       # 10 steps
assert [p[0] for p in samples] == [p[0] for p in train_all], "smoothed and raw samples are not on the same steps"
full = range(HALF, len(samples) - HALF)                   # indices whose centered window holds all WIN samples
assert max(abs(sum(v for _, v in samples[i - HALF:i + HALF + 1]) / WIN - train_all[i][1]) for i in full) < 6e-4
train = train_all[full.start:full.stop]                   # steps HALF*SPACING .. end - HALF*SPACING (120 .. 3,880)
assert abs(train[0][0] - HALF * SPACING) <= SPACING and abs(train[-1][0] - (train_all[-1][0] - HALF * SPACING)) <= SPACING
passes = data["passes"]
story = data["story"]
STEP_MAX = passes[-1]["steps"][1]
P2 = passes[1]["steps"][0]
PASS_LEN = passes[0]["steps"][1] - passes[0]["steps"][0]
seen_txt = re.search(r"training\s*~\s*([0-9.]+)", story["pass2_gap"]).group(1)     # "0.33"
p2_means = [m[2] for m in data["train_means_500"] if m[0] >= P2]
assert abs(float(seen_txt) - sum(p2_means) / len(p2_means)) < 0.006, (seen_txt, p2_means)
assert held[0][0] == 0 and held[-1][0] == STEP_MAX and abs(held[0][1] - story["untuned"]) < 5e-4
assert abs(dict(held)[500] - story["after_500"]) < 5e-4 and abs(held[-1][1] - story["end_pass2"]) < 5e-4

# ---------------------------------------------------------------- chart geometry, in Blender units
Y_LO, Y_HI, Y_STEP = 0.30, 0.65, 0.10      # loss axis (a line chart: it need not start at 0)
X_TICK = 1000
PLOT_W, PLOT_H = 40.0, 22.0
Z_AXIS = 3.3                                # the x axis, above the board's foot (tick labels go under it)
ML, MR, MT = 3.6, 6.2, 2.7                  # board margins: y tick labels / line-end labels / pass labels
XU = PLOT_W / STEP_MAX
ZU = PLOT_H / (Y_HI - Y_LO)
assert all(Y_LO < v < Y_HI for _, v in held + train)


def X(step):
    return step * XU


def Z(loss):
    return Z_AXIS + (loss - Y_LO) * ZU


BX0, BX1 = -ML, PLOT_W + MR                 # what the base must carry: the plot and its labels
BZ1 = Z_AXIS + PLOT_H + MT                  # the title's baseline, above the plot
FRONT = -0.06                               # the chart plane (text, axes); data geometry is placed along rays from it

# depths (y) along the camera's rays: the frame behind, the data in front of it
Y_GRID, Y_VEIL, Y_POST = 0.0, -0.10, -0.24
Y_HELD, Y_TRAIN = -0.70, -1.40
R_HELD, R_TRAIN, R_MARK = 0.15, 0.10, 0.40
D_FRONT, D_BACK = 4.5, 2.5                  # the base reaches this far in front of / behind the chart plane

ELEVATION, AZIMUTH, LENS = 10.0, 0.0, 80.0
C = {"held": kit.COLOURS["loss"], "train": "#3987e5"}       # the series' loss red; the weights-blue step for training

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
DEVICE = "CPU"
if args.device == "gpu":
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    devs = [d for d in prefs.devices if d.type == "CUDA"]
    if not devs:
        raise SystemExit("no CUDA device")
    for d in prefs.devices:
        d.use = d.type == "CUDA"
    scene.cycles.device = "GPU"
    DEVICE = "CUDA: " + ", ".join(d.name for d in devs)
print("DEVICE", DEVICE)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)

# ---------------------------------------------------------------- the frame of the chart, standing on the base
# The loss axis is a post standing on the base (the series' strut grey), just left of step 0; the step axis and the
# gridlines are thin rods held by it, in the chart plane. Nothing stands behind the curve: it reads against the dark
# background. The gridlines are built after the text, so they can stop short where a label crosses them.
m_post = kit.material("axis_post", kit.LOOK["frame"], rough=0.5, spec=0.5)
m_axis = kit.material("axis", "#7a828d", rough=0.5, spec=0.3, emit=0.20)
m_grid = kit.material("grid", "#3d4450", rough=0.6, spec=0.2, emit=0.25)
pw, aw, gw = 0.16, 0.05, 0.028                 # post half-width, axis rod half-width, gridline half-width
X_POST = -0.75                                 # the post's right face: clear of the first marker and the "0" label
y_ticks = [round(Y_LO + k * Y_STEP, 2) for k in range(int((Y_HI - Y_LO) / Y_STEP + 1e-9) + 1)]
x_ticks = list(range(0, STEP_MAX + 1, X_TICK))
frame = [kit.cuboid("axis_post", (X_POST - 2 * pw, Y_GRID, 0.0), (X_POST, Y_GRID + 2 * pw, Z(Y_HI) + 0.4), m_post),
         kit.cuboid("axis_x", (X_POST, Y_GRID, Z_AXIS - aw), (PLOT_W + 0.4, Y_GRID + 2 * aw, Z_AXIS + aw), m_axis)]
for v in y_ticks:
    frame.append(kit.cuboid(f"ytick_{v:.2f}", (X_POST - 2 * pw - 0.4, Y_GRID, Z(v) - aw), (X_POST - 2 * pw, Y_GRID + 2 * aw, Z(v) + aw), m_axis))
for s in x_ticks:
    frame.append(kit.cuboid(f"xtick_{s}", (X(s) - aw, Y_GRID, Z_AXIS - 0.4), (X(s) + aw, Y_GRID + 2 * aw, Z_AXIS), m_axis))
lo, hi = Vector((BX0, -D_FRONT, 0.0)), Vector((BX1, D_BACK, 0.0))
base, base_info = kit.floating_base(lo, hi, margin=1.2 / (hi.x - lo.x), seed=11, dressing=False, drop=4.5, thickness=0.7)
geo = frame + base

# ---------------------------------------------------------------- camera: level and raised, framed with lens shift
# A level camera keeps the chart plane parallel to the picture: no keystone, verticals stay vertical, one scale for
# x and one for y everywhere on the plot. It sits above the chart (as if tilted ELEVATION degrees down at its middle)
# so the base's top shows, and the lens shift brings the scene back to the middle of the picture.
cam = kit.make_camera(scene, LENS)
cam.rotation_euler = (math.radians(90), 0.0, 0.0)
rx, ry = W_PX, H_PX
em_y = kit.EM * rx / ry
pts = kit.mesh_points(geo)
lo_all = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
hi_all = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
cx, zc = (lo_all.x + hi_all.x) / 2, Z((Y_LO + Y_HI) / 2)
dist, shift = 2.0 * (hi_all - lo_all).length, 0.0
FILL_W, FILL_H = 0.92, 0.88
for _ in range(60):
    cam.location = (cx, FRONT - dist, zc + dist * math.tan(math.radians(ELEVATION)))
    cam.data.shift_y = shift
    cam.data.clip_start, cam.data.clip_end = dist / 1000.0, dist * 10.0
    bpy.context.view_layer.update()
    sp = [kit.to_screen(scene, cam, p) for p in pts]
    gx0, gx1, gy0, gy1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    top = kit.to_screen(scene, cam, (BX0, FRONT, BZ1)).y + 1.0 * em_y                   # the title above the plot
    x0, x1, y0, y1 = gx0, gx1, gy0, max(gy1, top)
    gw_, gh_ = gx1 - gx0, gy1 - gy0
    z = min(FILL_W / gw_, (FILL_H - ((y1 - y0) - gh_)) / gh_)
    fw_, fh_ = kit.frame_size(scene, cam, dist)
    cx += ((x0 + x1) / 2 - 0.5) * fw_
    shift += ((y0 + y1) / 2 - 0.5) * fh_ / fw_
    if abs(z - 1) < 1e-4 and abs((x0 + x1) / 2 - 0.5) < 1e-4 and abs((y0 + y1) / 2 - 0.5) < 1e-4:
        break
    dist /= z
CAM = cam.matrix_world.translation.copy()
D_BOARD = kit.to_screen(scene, cam, (PLOT_W / 2, FRONT, Z(0.45))).z
FW, _ = kit.frame_size(scene, cam, D_BOARD)                       # picture width in units at the chart plane
EMU, SUBU = kit.EM * FW, kit.SUB_EM * FW                          # text sizes in units
view_el = math.degrees(math.atan2(CAM.z - zc, FRONT - CAM.y))
print("CAMERA dist", round(dist, 2), "shift_y", round(shift, 4), "view elevation at the plot's middle", round(view_el, 2),
      "units per picture width", round(FW, 2), "px per unit", round(rx / FW, 1))


def on_ray(x, z, yq):
    """The point at depth yq (y) on the camera's ray through the chart point (x, FRONT, z), and its scale."""
    P = Vector((x, FRONT, z))
    t = (yq - CAM.y) / (P.y - CAM.y)
    return CAM + (P - CAM) * t, t


# ---------------------------------------------------------------- the data, as tubes and markers
m_held = kit.material("held_out", C["held"], emit=0.18, rough=0.6, spec=0.3)
m_mark = kit.material("held_out_marker", C["held"], emit=0.30, rough=0.5, spec=0.4)
m_train = kit.material("training", C["train"], emit=0.18, rough=0.6, spec=0.3)


def tube(name, points, yq, radius, mat):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp_ = cu.splines.new("POLY")
    sp_.points.add(len(points) - 1)
    ts = []
    for p, (s, v) in zip(sp_.points, points):
        q, t = on_ray(X(s), Z(v), yq)
        p.co = (q.x, q.y, q.z, 1.0)
        ts.append(t)
    sp_.use_smooth = False
    cu.bevel_depth = radius * sum(ts) / len(ts)          # same thickness on screen as at the board
    cu.bevel_resolution = 1
    cu.use_fill_caps = True
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    scene.collection.objects.link(ob)
    return ob


data_objs = [tube("line_held_out", held, Y_HELD, R_HELD, m_held), tube("line_training", train, Y_TRAIN, R_TRAIN, m_train)]
for i, (s, v) in enumerate(held):
    q, t = on_ray(X(s), Z(v), Y_HELD)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=R_MARK * t)
    me = bpy.data.meshes.new(f"marker_{s}")
    bm.to_mesh(me)
    bm.free()
    me.materials.append(m_mark)
    for poly in me.polygons:
        poly.use_smooth = False
    ob = bpy.data.objects.new(f"marker_{s}", me)
    ob.location = q
    ob.rotation_euler = (0.0, 0.0, math.radians(18 + 7 * i))     # vary the facets a little
    scene.collection.objects.link(ob)
    data_objs.append(ob)
for ob in data_objs:              # the curve casts no shadow: on the gridlines behind it a shadow reads as a break
    ob.visible_shadow = False


def interp(series, s):
    for (s0, v0), (s1, v1) in zip(series, series[1:]):
        if s0 <= s <= s1:
            return v0 + (v1 - v0) * (s - s0) / (s1 - s0)
    raise ValueError(s)


# the pass-2 gap: a faint sheet between the two lines (held-out above, training below), on the board
gap_steps = [s for s, _ in train if s >= P2]
assert all(interp(held, s) > v for s, v in train if s >= P2), "training is not below held-out all through pass 2"
vs = []
for s in gap_steps:
    vs += [on_ray(X(s), Z(interp(train, s)), Y_VEIL)[0], on_ray(X(s), Z(interp(held, s)), Y_VEIL)[0]]
faces = [(2 * k, 2 * k + 2, 2 * k + 3, 2 * k + 1) for k in range(len(gap_steps) - 1)]
veil = kit.mesh_object("gap_veil", vs, faces, [kit.veil_material("gap_veil", 0.028)])
kit.no_shadow(veil)

# the pass divider: a thin glowing post at the start of pass 2, standing on the x axis
post_top = Z(Y_HI) + 0.55 * MT
pq0, _ = on_ray(X(P2), Z_AXIS, Y_POST)
post = kit.cuboid("pass_divider", (pq0.x - 0.07, Y_POST - 0.06, Z_AXIS), (pq0.x + 0.07, Y_POST + 0.06, post_top),
                  kit.glow_material("pass_divider", kit.LOOK["limit"], kit.RIM_GLOW))
post.visible_shadow = False
data_objs.append(post)

# ---------------------------------------------------------------- text: printed on the board (and the title above it)
ink = kit.glow_material("ink", kit.LOOK["ink"], 1.0)
ink2 = kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
lead = kit.glow_material("leader", kit.LOOK["leader"], 1.0)
texts = {}


def text(key, body, x, z, size, mat, ax="LEFT", ay="CENTER"):
    ob, w, h = kit.text_object(f"txt_{key}", body, ax, ay)
    ob.data.size = size
    ob.location = (x, FRONT, z)
    ob.rotation_euler = (math.radians(90), 0.0, 0.0)
    ob.data.materials.append(mat)
    kit.no_shadow(ob)
    texts[key] = ob
    return ob


fmt3 = lambda v: f"{v:.3f}"
words = {2: "two", 3: "three"}
text("title", f"Run 3: loss over {words.get(len(passes), len(passes))} passes of {PASS_LEN:,} scenes",
     BX0, BZ1, EMU, ink, "LEFT", "BOTTOM_BASELINE")
for v in y_ticks:
    text(f"y_{v:.2f}", f"{v:.2f}", X_POST - 2 * pw - 0.75, Z(v), SUBU, ink2, "RIGHT", "CENTER")
for s in x_ticks:
    text(f"x_{s}", f"{s:,}", X(s), Z_AXIS - 0.6 - 0.5 * SUBU, SUBU, ink2, "CENTER", "CENTER")
x_last = texts[f"x_{x_ticks[-1]}"]
bpy.context.view_layer.update()
text("x_unit", "steps", X(x_ticks[-1]) + x_last.dimensions.x / 2 + 0.3 * SUBU, Z_AXIS - 0.6 - 0.5 * SUBU, SUBU, ink2,
     "LEFT", "CENTER")
pass_z = Z(Y_HI) + 0.42 * MT
text("pass1", f"pass {passes[0]['pass']}", X(P2) - 0.55, pass_z, EMU, ink2, "RIGHT", "CENTER")
text("pass2", f"pass {passes[1]['pass']}", X(P2) + 0.55, pass_z, EMU, ink2, "LEFT", "CENTER")
# line names at their ends
text("end_held", "held-out", X(STEP_MAX) + R_MARK + 0.55, Z(held[-1][1]), EMU, ink, "LEFT", "CENTER")
text("end_train", "training", X(train[-1][0]) + R_TRAIN + 0.55, Z(train[-1][1]), EMU, ink, "LEFT", "CENTER")
# story numbers
text("untuned", f"untuned {fmt3(story['untuned'])}", X(0) + R_MARK + 0.5, Z(held[0][1]), EMU, ink, "LEFT", "CENTER")
s500, v500 = next(p for p in held if p[0] == 500)
lab500_z = Z(v500) - R_MARK - 1.9
text("at500", f"{fmt3(story['after_500'])} by step {s500:,}", X(s500) - 0.25 * EMU, lab500_z, EMU, ink, "LEFT", "CENTER")
leader = kit.polyline("leader_500", [(X(s500), FRONT - 0.02, Z(v500) - R_MARK - 0.1),
                                     (X(s500), FRONT - 0.02, lab500_z + 0.62 * EMU)], kit.LINE * FW / 2, lead)
# the pass-2 gap, above the held-out line in pass 2
gap_x = X((P2 + STEP_MAX) / 2)
gap_top = max(interp(held, s) for s in gap_steps)
text("gap", f"seen ≈ {seen_txt} vs unseen {fmt3(story['end_pass2'])}", gap_x, Z(gap_top) + R_MARK + 0.75 * EMU, EMU, ink,
     "CENTER", "CENTER")
bpy.context.view_layer.update()

# gridlines, from the post to the end of the plot, cut where a label crosses them
grid, knock_x, knock_z = [], 0.45 * EMU, 0.35 * EMU
holes_by_v = {}
for v in y_ticks:
    if v <= Y_LO:
        continue
    holes = []
    for k, ob in texts.items():
        tlo, thi = kit.world_bbox([ob])
        if tlo.z - knock_z < Z(v) + gw and Z(v) - gw < thi.z + knock_z:
            holes.append((tlo.x - knock_x, thi.x + knock_x))
    holes_by_v[v] = holes
    segs, xa = [], X_POST
    for h0, h1 in sorted(holes):
        if h0 > xa:
            segs.append((xa, min(h0, PLOT_W)))
        xa = max(xa, h1)
    if xa < PLOT_W:
        segs.append((xa, PLOT_W))
    for j, (g0, g1) in enumerate(segs):
        if g1 - g0 > 0.05:
            grid.append(kit.cuboid(f"grid_{v:.2f}_{j}", (g0, Y_GRID + 0.02, Z(v) - gw), (g1, Y_GRID + 0.02 + 2 * gw, Z(v) + gw), m_grid))

# ---------------------------------------------------------------- lights: as the other figures (low key from the left-front, rim behind-right)
kit.stage_lights(direction, key=3.1, rim=2.0, key_el=12, rim_turn=125)

# ---------------------------------------------------------------- checks
def screen_rect(ob, pad=0.0):
    lo_, hi_ = kit.world_bbox([ob])
    cs = [kit.to_screen(scene, cam, (x, y, z)) for x in (lo_.x, hi_.x) for y in (lo_.y, hi_.y) for z in (lo_.z, hi_.z)]
    return [min(c.x for c in cs) - pad, max(c.x for c in cs) + pad, min(c.y for c in cs) - pad, max(c.y for c in cs) + pad]


rects = {k: screen_rect(o) for k, o in texts.items()}
names = list(rects)
overlaps = [[p, q] for i, p in enumerate(names) for q in names[i + 1:]
            if rects[p][0] < rects[q][1] and rects[q][0] < rects[p][1] and rects[p][2] < rects[q][3] and rects[q][2] < rects[p][3]]
# text against the lines and markers (sampled on screen, padded by the tube's radius on screen)
px_per_unit = rx / FW
line_pts = [(kit.to_screen(scene, cam, on_ray(X(s), Z(interp(held, s)), Y_HELD)[0]), R_HELD) for s in range(0, STEP_MAX + 1, 5)]
line_pts += [(kit.to_screen(scene, cam, on_ray(X(s), Z(v), Y_TRAIN)[0]), R_TRAIN) for s, v in train]
line_pts += [(kit.to_screen(scene, cam, on_ray(X(s), Z(v), Y_HELD)[0]), R_MARK) for s, v in held]
text_on_lines = set()
for k, r in rects.items():
    for p, rad in line_pts:
        pr = rad / FW * 1.0
        if r[0] - pr < p.x < r[1] + pr and r[2] - pr * rx / ry < p.y < r[3] + pr * rx / ry:
            text_on_lines.add(k)
inside_picture = all(0.01 < r[0] and r[1] < 0.99 and 0.01 < r[2] and r[3] < 0.99 for r in rects.values())
frame_rects = {o.name: screen_rect(o) for o in frame + grid + [post]}
text_on_frame = [[k, n] for k, r in rects.items() for n, q in frame_rects.items()
                 if r[0] < q[1] and q[0] < r[1] and r[2] < q[3] and q[2] < r[3]]
base_x = [kit.to_screen(scene, cam, (base_info["x"][0], FRONT, 0)).x, kit.to_screen(scene, cam, (base_info["x"][1], FRONT, 0)).x]
text_beyond_base = [k for k, r in rects.items() if r[0] < base_x[0] or r[1] > base_x[1]]
# the curve's projection: chart point vs where the tube's centre lands on screen (must be the same)
proj_err = 0.0
for (s, v), yq in [(p, Y_HELD) for p in held] + [(p, Y_TRAIN) for p in train[::40]]:
    a_ = kit.to_screen(scene, cam, (X(s), FRONT, Z(v)))
    b_ = kit.to_screen(scene, cam, on_ray(X(s), Z(v), yq)[0])
    proj_err = max(proj_err, abs(a_.x - b_.x) * rx, abs(a_.y - b_.y) * ry)
# vertical scale on screen at the left and right of the plot (keystone check)
kz = []
for s in (0, STEP_MAX):
    y0_ = kit.to_screen(scene, cam, (X(s), FRONT, Z(Y_LO))).y
    y1_ = kit.to_screen(scene, cam, (X(s), FRONT, Z(Y_HI))).y
    kz.append((y1_ - y0_) * ry)
gap_px = {s: round((kit.to_screen(scene, cam, (X(s), FRONT, Z(interp(held, s)))).y
                    - kit.to_screen(scene, cam, (X(s), FRONT, Z(interp(train, s)))).y) * ry, 1) for s in (2500, 3000, 3500, train[-1][0])}
glo, ghi = kit.world_bbox([texts["gap"]])
under = [v for st, v in train if glo.x <= X(st) <= ghi.x]
p2_line = [v for st, v in train if st >= P2]
seen_check = {"label": seen_txt, "line_mean_under_label": round(sum(under) / len(under), 4),
              "label_span_steps": [round(glo.x / XU), round(ghi.x / XU)],
              "line_mean_pass2": round(sum(p2_line) / len(p2_line), 4), "line_end": list(train[-1])}
assert abs(seen_check["line_mean_under_label"] - float(seen_txt)) < 0.005 and abs(seen_check["line_mean_pass2"] - float(seen_txt)) < 0.005
assert abs(train[-1][1] - float(seen_txt)) < 0.005
layout = {
    "figure": "run3_loss", "data": os.path.relpath(args.data, os.path.dirname(HERE)),
    "axes": {"loss": [Y_LO, Y_HI], "loss_ticks": y_ticks, "steps": [0, STEP_MAX], "step_ticks": x_ticks},
    "colours": C, "device": DEVICE,
    "camera": {"level": True, "view_elevation_deg": round(view_el, 2), "shift_y": round(shift, 4), "lens_mm": LENS, "distance": round(dist, 2),
               "px_per_unit": round(px_per_unit, 2)},
    "plot_px": {"width": round((kit.to_screen(scene, cam, (PLOT_W, FRONT, Z_AXIS)).x - kit.to_screen(scene, cam, (0, FRONT, Z_AXIS)).x) * rx, 1),
                "height_left": round(kz[0], 1), "height_right": round(kz[1], 1)},
    "pass2_gap_px": gap_px,
    "training_line": {"window_samples": WIN, "sample_spacing_steps": SPACING, "drawn_steps": [train[0][0], train[-1][0]],
                      "points_drawn": len(train), "points_in_data": len(train_all)},
    "gap_fill_steps": [gap_steps[0], gap_steps[-1]], "seen_label_check": seen_check,
    "labels": {k: o.data.body for k, o in texts.items()},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rects.items()},
    "text_overlaps": overlaps, "text_on_lines": sorted(text_on_lines), "text_inside_picture": inside_picture,
    "text_on_frame": text_on_frame, "text_beyond_base": text_beyond_base, "curve_projection_error_px": round(proj_err, 3),
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("plot_px", "pass2_gap_px", "training_line", "gap_fill_steps", "seen_label_check", "text_overlaps", "text_on_lines",
                                                 "text_inside_picture", "text_on_frame", "text_beyond_base", "curve_projection_error_px")}))

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout["render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout)
    print("RENDER", round(secs, 1), "s")
