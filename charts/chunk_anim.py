"""Animation: what the chunked loss does in practice, side by side with the stock loss (Qwen3.8-27B, 3,000 tokens).

Each side lies on its own floating base: the final hidden states H (3,000 x 5,120), the output layer W (5,120 x 248,320)
as a ribbon behind the score table's footprint (3,000 x 248,320), a slot for the gradient on H (3,000 x 5,120), the loss
and a gauge. Widths are to scale: 1 unit = 5,120 columns, so the table is 48.5 units wide and H 1; rows run front to
back on their own scale (3,000 rows = D units), row 0 at the back. Heights are bytes per entry (ZB units per byte), so
a BF16 table is 2 bytes tall and the stack of the score table's copies is about 13 bytes tall.
Left (stock): logits = H x W for all rows at once, an FP32 log-softmax on top (kept for backward), the loss, the
gradient table on top (peak), the gradient contracts with W back to 3,000 x 5,120 on H, the tables are freed, the
gradient goes down into the model. Right (chunked): an empty gradient buffer beside H; for each slice of 128 rows
(24 slices, the last 56 rows): its 128 x V strip of the same copies, loss, gradient, the strip's gradient x W written
into the buffer's rows, the strip discarded; when the buffer is full it goes down into the model.

Timing: one compute clock drives both sides (units below, the stock loss = 2.65 units; the chunked loss costs 3% more,
spread over its slices, as measured on the 27B step). The first slice plays in slow motion so its phases can be read;
both sides slow down together, so the two step timers always agree until the left is done.
Data: charts/data/chunked_loss_3000.json.

One build serves the storyboard and the video: state(side, seconds) sets every frame of the timeline.
~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/chunk_anim.py -- \
    --frames storyboard                                  # 8 key frames at 640x360 + charts/out/chunk_anim_storyboard.png
    --frames 0,240,480 [--size 1920x1080 --samples 64]   # any frames
    --frames all|queue --size 1920x1080 --samples 64     # every frame of the video (then ffmpeg -> MP4)
"""
import argparse, json, math, os, sys, time
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--frames", default="storyboard")
ap.add_argument("--size", default="640x360")
ap.add_argument("--samples", type=int, default=16)
ap.add_argument("--outdir", default=os.path.join(HERE, "out", "chunk_anim"))
ap.add_argument("--sheet", default=os.path.join(HERE, "out", "chunk_anim_storyboard.png"))
ap.add_argument("--device", default="gpu", choices=["gpu", "cpu"], help="gpu: CUDA, falls back to CPU")
ap.add_argument("--threads", type=int, default=0, help="CPU threads for this process (0 = all)")
ap.add_argument("--denoise-gpu", action="store_true", help="run OpenImageDenoise on the GPU")
ap.add_argument("--tag", default=None, help="name for this process's log (frames_<tag>.json)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX

# ---------------------------------------------------------------- data
dat = json.load(open(os.path.join(HERE, "data", "chunked_loss_3000.json")))
sh, mem = dat["shapes"], dat["memory"]
N_TOK, D_MODEL, VOCAB, CHUNK = sh["N_tokens"], sh["d_model"], sh["V_vocab"], sh["chunk_c"]
SLICE_ROWS = [(r, min(r + CHUNK, N_TOK)) for r in range(0, N_TOK, CHUNK)]
N_SLICES = len(SLICE_ROWS)
assert (N_TOK, D_MODEL, VOCAB, CHUNK, N_SLICES) == (3000, 5120, 248320, 128, sh["slices"])
WIDEN = VOCAB / D_MODEL                                  # 48.5
SLAB_GIB = mem["hidden_states_mib"] / 1024.0           # H, and the gradient on H: 29.3 MiB each
assert mem["hidden_states_mib"] == mem["gradient_buffer_mib"] == 29.3
PEAK_STOCK = mem["stock_peak_gib"]                       # 9.4 GiB, measured
SLICE_GIB = mem["chunked_slice_gib"]                     # 0.39 GiB: one 128-row slice in the same copies
GIB = 2.0 ** 30
# bytes per entry of the score table's copies: BF16 logits 2, FP32 log-softmax 4, the gradient tables the rest, so
# that the stock peak (H + tables + the gradient on H) is the measured 9.4 GiB and one full slice is 0.39 GiB
BYTES = {"left": [2.0, 4.0, (PEAK_STOCK - 2 * SLAB_GIB) * GIB / (N_TOK * VOCAB) - 6.0],
         "right": [2.0, 4.0, SLICE_GIB * GIB / (CHUNK * VOCAB) - 6.0]}
BAND_NAMES = ("logits (BF16)", "log-softmax (FP32)", "gradient")


def band_gib(side, rows):
    return [rows * VOCAB * b / GIB for b in BYTES[side]]


# ---------------------------------------------------------------- timeline, driven by one compute clock
FPS = 30
UNITS = {"logits": 1.0, "softmax": 0.25, "loss": 0.15, "gradient": 0.25, "collapse": 1.0}   # schematic shares
ORDER = ("logits", "softmax", "loss", "gradient", "collapse")
CHUNK_COST = 1.03                                        # measured: the 27B step is about 3% slower chunked
L_TOTAL = sum(UNITS.values())
R_TOTAL = L_TOTAL * CHUNK_COST
SPU = 6.3                                                # seconds of video per compute unit at normal speed
INTRO = 2.0
SLOW = {"logits": 1.5, "softmax": 1.0, "loss": 0.9, "gradient": 0.9, "collapse": 1.5}       # slice 1, slow motion
SLOW_DISCARD = 0.7
FREE_T, DISCARD_T, SINK_T, OUTRO = 0.7, 0.3, 1.3, 3.0


def phase_list(side):
    """[(c0, c1, slice index or None, phase)] on the compute clock."""
    out, c = [], 0.0
    if side == "left":
        for ph in ORDER:
            out.append((c, c + UNITS[ph], None, ph))
            c += UNITS[ph]
        return out
    for k, (r0, r1) in enumerate(SLICE_ROWS):
        for ph in ORDER:
            u = UNITS[ph] * (r1 - r0) / N_TOK * CHUNK_COST
            out.append((c, c + u, k, ph))
            c += u
    return out


PH = {s: phase_list(s) for s in ("left", "right")}
C_S1 = next(c1 for (c0, c1, k, ph) in PH["right"] if k == 0 and ph == "collapse")
SEGS = [(0.0, INTRO, 0.0, 0.0, "intro")]                 # (tau0, tau1, c0, c1, kind): the clock is linear inside each
_t = INTRO
for (c0, c1, k, ph) in PH["right"]:
    if k == 0:
        SEGS.append((_t, _t + SLOW[ph], c0, c1, "slow"))
        _t += SLOW[ph]
SEGS.append((_t, _t + SLOW_DISCARD, C_S1, C_S1, "slow_discard"))
_t += SLOW_DISCARD
SEGS.append((_t, _t + (R_TOTAL - C_S1) * SPU, C_S1, R_TOTAL, "normal"))
T_NORMAL0 = _t
T_END_C = {"left": T_NORMAL0 + (L_TOTAL - C_S1) * SPU, "right": SEGS[-1][1]}
POST = {"left": [("free", FREE_T), ("sink", SINK_T)], "right": [("discard", DISCARD_T), ("sink", SINK_T)]}
T_DONE = {s: T_END_C[s] + sum(d for _, d in POST[s]) for s in POST}
T_END = max(T_DONE.values()) + OUTRO
N_FRAMES = int(round(T_END * FPS))


def clock(tau):
    for (t0, t1, c0, c1, kind) in SEGS:
        if tau < t1:
            return c0 + (c1 - c0) * max(0.0, (tau - t0) / (t1 - t0)), kind
    return R_TOTAL, "after"


def clamp01(x):
    return max(0.0, min(1.0, x))


def tau_at(c):
    """Screen time at which the compute clock reaches c."""
    for (t0, t1, c0, c1, kind) in SEGS:
        if c1 > c0 and c0 <= c <= c1:
            return t0 + (c - c0) / (c1 - c0) * (t1 - t0)
    return SEGS[-1][1]


ALLOC_T = 0.3                  # a table is allocated whole when its phase starts: it appears within this many seconds


def grown(tau, c0, c1):
    """0..1: how far a table allocated at compute c0 has appeared (fast: allocation, not computation)."""
    ta, tb = tau_at(c0), tau_at(c1)
    return clamp01((tau - ta) / max(1e-6, min(ALLOC_T, 0.5 * (tb - ta)))) if tau >= ta else 0.0


def state(side, tau):
    """What exists on one side at screen time tau. Memory is counted when it is allocated, not as it is computed."""
    c, kind = clock(tau)
    total = L_TOTAL if side == "left" else R_TOTAL
    st = {"bands": [0.0, 0.0, 0.0], "loss": 0.0, "ghost": None, "slot_alloc": 0.0, "slot_solid": False,
          "rows_done": 0, "sink": 0.0, "slice": None, "phase": None, "post": None, "c": min(c, total), "speed": kind}
    if side == "right":
        st["slot_alloc"] = 1.0                           # the buffer is allocated up front (empty)
    if kind == "intro":
        st["phase"] = "intro"
    elif c < total or (side == "right" and kind == "slow_discard"):
        if side == "right" and kind == "slow_discard":
            f = (tau - next(s_[0] for s_ in SEGS if s_[4] == "slow_discard")) / SLOW_DISCARD
            st.update(slice=0, phase="discard", loss=1.0, rows_done=SLICE_ROWS[0][1])
            st["bands"] = [1.0 - clamp01(f / 0.4)] * 3
            return finish(side, st)
        cur = next((p for p in PH[side] if p[0] <= c < p[1]), PH[side][-1])
        k = cur[2]
        st["slice"], st["phase"] = k, cur[3]
        prog, grow = {}, {}
        for (c0, c1, kk, ph) in PH[side]:
            if kk == k:
                prog[ph] = clamp01((c - c0) / (c1 - c0))
                grow[ph] = grown(tau, c0, c1) if c >= c0 else 0.0
        st["bands"] = [grow["logits"], grow["softmax"], grow["gradient"]]
        st["loss"] = grow["loss"] if (side == "left" or k == 0) else 1.0
        if side == "left":
            st["slot_alloc"] = grow["collapse"]          # the gradient on H: allocated, then filled by gradient x W
        else:
            st["rows_done"] = SLICE_ROWS[k][0]
        if 0.0 < prog["collapse"] < 1.0:
            st["ghost"] = prog["collapse"]
    else:                                                # compute done: free / discard, then down into the model
        st["loss"] = 1.0
        st["rows_done"] = N_TOK
        if side == "left":
            st["slot_alloc"], st["slot_solid"] = 1.0, True
        t = T_END_C[side]
        st["phase"] = "done"
        for name, d in POST[side]:
            if tau < t + d:
                f = (tau - t) / d
                st["phase"], st["post"] = name, f
                break
            t += d
        if st["phase"] in ("free", "discard"):
            st["bands"] = [1.0 - clamp01(st["post"] / 0.4)] * 3      # freeing is quick
            st["slice"] = N_SLICES - 1 if side == "right" else None
        elif st["phase"] == "sink":
            st["sink"] = st["post"]
        elif st["phase"] == "done":
            st["sink"] = 1.0
    return finish(side, st)


def finish(side, st):
    rows = N_TOK if side == "left" else (SLICE_ROWS[st["slice"]][1] - SLICE_ROWS[st["slice"]][0] if st["slice"] is not None else 0)
    g = band_gib(side, rows)
    slot = SLAB_GIB * st["slot_alloc"] * (1.0 - st["sink"])
    st["gib"] = SLAB_GIB + slot + sum(f * x for f, x in zip(st["bands"], g))
    return st


def timer(side, tau):
    return state(side, tau)["c"] / L_TOTAL


PEAK = {s: max(state(s, k / FPS)["gib"] for k in range(N_FRAMES)) for s in ("left", "right")}

# ---------------------------------------------------------------- scene
D = 36.0                       # 3,000 rows, front to back (rows are not to scale with widths)
ZB = 0.38                      # height per byte of each entry
SLAB_Z = 2 * ZB                # BF16: H, W, the gradient on H
SLOT_X0, H_X0, TX0 = 0.0, 1.45, 3.4
TX1 = TX0 + WIDEN              # the table: 48.5 units wide (H: 1)
W_Y0 = D / 2 + 1.0             # W lies behind the table: 5,120 deep (1 unit) x 248,320 wide
GAUGE_PER_GIB = 1.6
SIDE_DX = TX1 + 9.5
ELEVATION, AZIMUTH, LENS = 36.0, -2.0, 135.0


def row_y(r):
    return D / 2 - r / N_TOK * D


scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
DEVICE = "CPU"
if args.device == "gpu":                              # same samples and the same OpenImageDenoise; CPU if no GPU works
    prefs = bpy.context.preferences.addons["cycles"].preferences
    keep = (scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples, scene.cycles.use_denoising)
    for dev_type in ("CUDA",):                        # OptiX does not compile on this driver (565.77)
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            devs = [d for d in prefs.devices if d.type == dev_type]
            if not devs:
                continue
            for d in prefs.devices:
                d.use = d.type == dev_type
            scene.cycles.device = "GPU"
            scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples = 16, 16, 1
            scene.cycles.use_denoising = False
            probe_cam = bpy.data.objects.new("gpu_probe_cam", bpy.data.cameras.new("gpu_probe_cam"))
            scene.collection.objects.link(probe_cam)
            scene.camera = probe_cam
            try:
                bpy.ops.render.render(write_still=False)      # proves the kernels load on this driver
            finally:
                scene.camera = None
                bpy.data.objects.remove(probe_cam, do_unlink=True)
            DEVICE = f"{dev_type}: " + ", ".join(d.name for d in devs)
            break
        except Exception as e:
            print("GPU", dev_type, "failed:", str(e)[:160])
    scene.render.resolution_x, scene.render.resolution_y, scene.cycles.samples, scene.cycles.use_denoising = keep
    if DEVICE == "CPU":
        prefs.compute_device_type = "NONE"
        scene.cycles.device = "CPU"
print("DEVICE", DEVICE)
if args.threads > 0:
    scene.render.threads_mode = "FIXED"
    scene.render.threads = args.threads
if args.denoise_gpu:
    scene.cycles.denoising_use_gpu = True
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
h_m = kit.material("m_hidden", kit.COLOURS["activations"], emit=0.12, rough=0.85, spec=0.12)
w_m = kit.material("m_weights", kit.COLOURS["frozen"], emit=0.10, rough=0.85, spec=0.12)
band_m = [kit.material("m_logits", "#bdb6f5", emit=0.14, rough=0.85, spec=0.12),      # forward copies: violet tints
          kit.material("m_logsoftmax", "#6357cf", emit=0.18, rough=0.85, spec=0.12),
          kit.material("m_gradtable", kit.COLOURS["gradients"], emit=0.12, rough=0.85, spec=0.12)]
grad_m = kit.material("m_grad", kit.COLOURS["gradients"], emit=0.14, rough=0.85, spec=0.12)
empty_m = kit.veil_material("m_empty", 0.22, kit.hex_lin(kit.COLOURS["gradients"]))     # the allocated, empty buffer
ghost_m = kit.material("m_ghost", kit.COLOURS["gradients"], emit=0.35, rough=0.85, spec=0.12)   # the gradient on its way to H
loss_m = kit.material("m_loss", kit.COLOURS["loss"], emit=0.15, rough=0.85, spec=0.12)
gauge_m = kit.material("m_gauge", "#e9e9e9", emit=0.10, rough=0.8, spec=0.1)
frame_m = kit.material("m_frame", "#4d535c", rough=0.6, spec=0.2)
floor_m = kit.material("m_floor", "#262b33", rough=0.8, spec=0.1)
glow = kit.glow_material("marker", kit.LOOK["limit"], 1.6)


def unit_box(name, mat, shadow=True):
    ob = kit.cuboid(name, (0, 0, 0), (1, 1, 1), mat)
    if not shadow:
        kit.no_shadow(ob)
    return ob


def set_box(ob, x0, x1, y0, y1, z0, z1):
    ob.location = (min(x0, x1), min(y0, y1), min(z0, z1))
    ob.scale = (max(abs(x1 - x0), 1e-4), max(abs(y1 - y0), 1e-4), max(abs(z1 - z0), 1e-4))


def set_frame(obs, x0, x1, y0, y1, z0, z1, t=0.16):
    set_box(obs[0], x0 - t, x1 + t, y0 - t, y0, z0, z1)
    set_box(obs[1], x0 - t, x1 + t, y1, y1 + t, z0, z1)
    set_box(obs[2], x0 - t, x0, y0, y1, z0, z1)
    set_box(obs[3], x1, x1 + t, y0, y1, z0, z1)


SIDES = {}
for si, side in enumerate(("left", "right")):
    X0 = si * SIDE_DX
    S = {"X0": X0}
    S["H"] = kit.cuboid(f"{side}_H", (X0 + H_X0, -D / 2, 0), (X0 + H_X0 + 1, D / 2, SLAB_Z), h_m)
    S["W"] = kit.cuboid(f"{side}_W", (X0 + TX0, W_Y0, 0), (X0 + TX1, W_Y0 + 1.0, SLAB_Z), w_m)
    S["floor"] = kit.cuboid(f"{side}_floor", (X0 + TX0, -D / 2, 0), (X0 + TX1, D / 2, 0.03), floor_m)   # the table's footprint
    S["outline"] = [unit_box(f"{side}_outline{k}", frame_m) for k in range(4)]
    set_frame(S["outline"], X0 + TX0, X0 + TX1, -D / 2, D / 2, 0.0, 0.08, t=0.12)
    S["bands"] = [unit_box(f"{side}_band{k}", band_m[k]) for k in range(3)]
    S["slot"] = unit_box(f"{side}_slot", grad_m)          # the gradient on H (left) / the buffer's filled rows (right)
    S["empty"] = unit_box(f"{side}_empty", empty_m, shadow=False)
    S["ghost"] = unit_box(f"{side}_ghost", ghost_m, shadow=False)
    S["loss"] = kit.cuboid(f"{side}_loss", (0, 0, 0), (1.3, 1.3, 1.3), loss_m)
    S["loss_at"] = (X0 + TX1 + 2.2, -D / 2 + 0.4)
    gx0, gx1, gy0, gy1 = X0 + TX1 + 1.8, X0 + TX1 + 4.8, D / 2 - 3.0, D / 2      # the gauge stands at the back right
    S["gauge"] = unit_box(f"{side}_gauge", gauge_m)
    S["g"] = (gx0, gx1, gy0, gy1)
    top = PEAK["left"] * GAUGE_PER_GIB
    for k, (x, y) in enumerate(((gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1))):
        kit.cuboid(f"{side}_gpost{k}", (x - 0.06, y - 0.06, 0), (x + 0.06, y + 0.06, top), frame_m)
    S["marker"] = [unit_box(f"{side}_marker{k}", glow, shadow=False) for k in range(4)]
    objs = [S["H"], S["W"], S["floor"]]
    lo, hi = kit.world_bbox(objs)
    lo.z, lo.x, hi.x = 0.0, lo.x - 0.6, X0 + TX1 + 5.0
    S["base"], S["base_info"] = kit.floating_base(lo, hi, margin=2.2 / (hi.x - lo.x), seed=31 + si, dressing=False, drop=6.0, thickness=0.8)
    SIDES[side] = S

# ---------------------------------------------------------------- text (fixed places; bodies change per frame)
EM_A = 0.024 if W_PX <= 800 else 0.019
SUB_A = 0.019 if W_PX <= 800 else 0.0150
LAB_A = SUB_A * 0.88
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
ink3 = kit.glow_material("ink3", "#5e5f6b", 1.0)        # phase words not yet / no longer active
ink_h = kit.glow_material("ink_h", kit.COLOURS["activations"], 1.0)     # object labels in their object's colour
ink_w = kit.glow_material("ink_w", kit.COLOURS["frozen"], 1.0)
ink_g = kit.glow_material("ink_g", kit.COLOURS["gradients"], 1.0)
ink_l = kit.glow_material("ink_l", kit.COLOURS["loss"], 1.0)
T = {}


def text(key, body, size, mat, ax="LEFT", ay="BOTTOM_BASELINE"):
    ob, w, _ = kit.text_object(f"txt_{key}", body, ax, ay)
    T[key] = {"ob": ob, "size": size, "mat": mat, "w": w}


WORDS = {"left": ["logits", "softmax", "loss", "gradient", "collapse", "free"],
         "right": ["logits", "softmax", "loss", "gradient", "write rows", "discard"]}
PHASE_IDX = {"logits": 0, "softmax": 1, "loss": 2, "gradient": 3, "collapse": 4, "free": 5, "discard": 5}
for side, title in (("left", "stock loss"), ("right", "chunked loss")):
    text(f"title_{side}", title, EM_A, ink2)
    text(f"phase_{side}", "", EM_A, ink)
    text(f"gauge_{side}", "", SUB_A, ink, "RIGHT")
    text(f"timer_{side}", "step time 0.00×", SUB_A, ink)
    for i, w in enumerate(WORDS[side]):
        text(f"w{i}_{side}", w, SUB_A, ink3)
    text(f"H_{side}", "H  3,000 × 5,120", LAB_A, ink_h)
    text(f"W_{side}", "W, output layer  5,120 × 248,320", LAB_A, ink_w)
    text(f"slot_{side}", "gradient on H  3,000 × 5,120" if side == "left" else "gradient buffer  3,000 × 5,120", LAB_A, ink_g)
    text(f"table_{side}", "scores  3,000 × 248,320" if side == "left" else
         "scores: 128 rows at a time (24 slices)", LAB_A, ink2, "RIGHT")
    text(f"loss_{side}", "loss", LAB_A, ink_l, "CENTER")
text("timer_note", "measured: 3% slower on the 27B", SUB_A * 0.8, ink2)
text("caption", "", SUB_A, ink, "CENTER")
text("note", "score table : hidden states = 248,320 : 5,120 per token (48×)", SUB_A * 0.8, ink2, "CENTER")

cam = kit.make_camera(scene, LENS)
pts = []
for S in SIDES.values():
    pts += kit.mesh_points([S["H"], S["W"], S["floor"]] + S["base"])
    gx0, gx1, gy0, gy1 = S["g"]
    pts += [Vector((x, y, z)) for x in (gx0, gx1) for y in (gy0, gy1) for z in (0, PEAK["left"] * GAUGE_PER_GIB)]
    pts += [Vector((S["X0"] + x, y, z)) for x in (TX0, TX1) for y in (-D / 2, D / 2) for z in (0, sum(BYTES["left"]) * ZB)]
target, dist = sum(pts, Vector()) / len(pts), 300.0
for _ in range(16):                                   # geometry in the middle of the frame; room above and below for text
    kit.aim(cam, target, dist, direction)
    sp = [kit.to_screen(scene, cam, p) for p in pts]
    x0, x1, y0, y1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    z = min(0.93 / (x1 - x0), 0.52 / (y1 - y0))
    fw_, fh_ = kit.frame_size(scene, cam, dist)
    Rv = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    Uv = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    target = target + Rv * ((x0 + x1) / 2 - 0.5) * fw_ + Uv * ((y0 + y1) / 2 - 0.50) * fh_
    if abs(z - 1) < 0.002:
        break
    dist /= z
kit.aim(cam, target, dist, direction)
d_text = kit.to_screen(scene, cam, (SIDE_DX / 2, -D / 2 - 8, 0)).z
em_y, sub_y = EM_A * rx / ry, SUB_A * rx / ry
sp = [kit.to_screen(scene, cam, p) for p in pts]
top_geo, bot_geo = max(p.y for p in sp), min(p.y for p in sp)


def put(key, sx, sy):
    kit.place_on_screen(scene, cam, T[key]["ob"], sx, sy, d_text, T[key]["size"], T[key]["mat"])


for side, S in SIDES.items():
    X0 = S["X0"]
    px0 = kit.to_screen(scene, cam, (X0 + SLOT_X0, -D / 2, 0)).x
    put(f"title_{side}", px0, top_geo + 3.75 * em_y)
    put(f"phase_{side}", px0, top_geo + 2.6 * em_y)
    sx = px0
    for i in range(len(WORDS[side])):                  # the phase words in a row; the active one lit
        put(f"w{i}_{side}", sx, top_geo + 1.6 * em_y)
        sx += (T[f"w{i}_{side}"]["w"] + 0.9) * SUB_A
    gx0, gx1, gy0, gy1 = S["g"]
    gt = kit.to_screen(scene, cam, (gx1, gy0, PEAK["left"] * GAUGE_PER_GIB))
    put(f"gauge_{side}", gt.x + 0.004, gt.y + 0.5 * sub_y)
    p = kit.to_screen(scene, cam, (X0 + TX0, W_Y0 + 1.0, SLAB_Z))       # W: above the ribbon's left end
    put(f"W_{side}", p.x, p.y + 0.6 * sub_y)
    front = kit.to_screen(scene, cam, (X0 + SLOT_X0, -D / 2 - S["base_info"]["margin"], 0))   # the base's front edge
    put(f"H_{side}", px0, front.y - 1.15 * sub_y)                      # H and the gradient: under their front ends
    put(f"slot_{side}", px0, front.y - 2.15 * sub_y)
    p = kit.to_screen(scene, cam, (X0 + TX1, -D / 2 - S["base_info"]["margin"], 0))
    put(f"table_{side}", p.x, p.y - 1.15 * sub_y)                     # same line as H, at the table's right end
    lx, ly = S["loss_at"]
    p = kit.to_screen(scene, cam, (lx + 0.65, ly + 0.65, 1.3))
    put(f"loss_{side}", p.x, p.y + 0.4 * sub_y)
fronts = [kit.to_screen(scene, cam, (S["X0"] + x, -D / 2 - S["base_info"]["margin"], 0)).y for S in SIDES.values() for x in (SLOT_X0, TX1)]
TIMER_Y = min(bot_geo, min(fronts) - 2.15 * sub_y) - 1.05 * em_y      # one line for both timers, under every label
for side, S in SIDES.items():
    px0 = kit.to_screen(scene, cam, (S["X0"] + SLOT_X0, -D / 2, 0)).x
    put(f"timer_{side}", px0, TIMER_Y)
    if side == "right":
        put("timer_note", px0, TIMER_Y - 0.95 * sub_y)
put("caption", 0.5, max(0.075, TIMER_Y - 2.3 * sub_y))
put("note", 0.5, 0.022)
kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)


def fmt_gib(x):
    return f"{x:.1f} GiB" if x >= 0.995 else f"{x:.2f} GiB"


def apply(frame):
    tau = frame / FPS
    sts = {}
    for side, S in SIDES.items():
        st = state(side, tau)
        sts[side] = st
        X0 = S["X0"]
        # the score table's copies: the whole table (left) or the current slice's strip (right)
        if side == "left":
            ya, yb = -D / 2, D / 2
        elif st["slice"] is not None:
            r0, r1 = SLICE_ROWS[st["slice"]]
            ya, yb = row_y(r1), row_y(r0)
        z = 0.03
        for k, ob in enumerate(S["bands"]):
            h = BYTES[side][k] * ZB * st["bands"][k]
            ob.hide_render = h < 1e-3 or (side == "right" and st["slice"] is None)
            if not ob.hide_render:
                set_box(ob, X0 + TX0, X0 + TX1, ya, yb, z, z + h)
            z += h                                     # bands fill in order, so a band starts on a full one
        top_grad = (0.03 + sum(BYTES[side][:2]) * ZB, 0.03 + sum(BYTES[side]) * ZB)
        # the gradient on H: left fills its slot during the collapse; right fills the buffer's rows slice by slice
        sink = st["sink"] * (SLAB_Z + 0.9)
        if side == "left":                             # allocated (clear) during the collapse, solid once written
            a = st["slot_alloc"]
            S["slot"].hide_render = not st["slot_solid"] or st["sink"] >= 1.0
            set_box(S["slot"], X0 + SLOT_X0, X0 + SLOT_X0 + 1, -D / 2, D / 2, -sink, SLAB_Z - sink)
            S["empty"].hide_render = st["slot_solid"] or a < 1e-3
            set_box(S["empty"], X0 + SLOT_X0, X0 + SLOT_X0 + 1, -D / 2, D / 2, 0.0, SLAB_Z * max(a, 1e-3))
            gya, gyb = -D / 2, D / 2
        else:
            rows = st["rows_done"]
            S["slot"].hide_render = rows == 0 or st["sink"] >= 1.0
            set_box(S["slot"], X0 + SLOT_X0, X0 + SLOT_X0 + 1, row_y(rows), D / 2, -sink, SLAB_Z - sink)
            S["empty"].hide_render = st["sink"] >= 1.0 or rows >= N_TOK
            set_box(S["empty"], X0 + SLOT_X0, X0 + SLOT_X0 + 1, -D / 2, row_y(rows), -sink, SLAB_Z - sink)
            gya, gyb = (ya, yb) if st["slice"] is not None else (-D / 2, D / 2)
        g = st["ghost"]
        S["ghost"].hide_render = g is None
        if g is not None:                              # the gradient x W, contracted to 5,120 wide, flies to its rows
            s = g * g * (3 - 2 * g)
            ax0, ax1, az0, az1 = X0 + TX0, X0 + TX1, top_grad[0], top_grad[1]
            bx0, bx1, bz0, bz1 = X0 + SLOT_X0, X0 + SLOT_X0 + 1, 0.0, SLAB_Z
            lift = math.sin(math.pi * s) * (top_grad[1] + 1.5)      # up and over the strip, then down
            set_box(S["ghost"], ax0 + (bx0 - ax0) * s, ax1 + (bx1 - ax1) * s, gya, gyb,
                    az0 + (bz0 - az0) * s + lift, az1 + (bz1 - az1) * s + lift)
        # loss: a small cube that appears once
        lx, ly = S["loss_at"]
        S["loss"].hide_render = st["loss"] <= 1e-3
        S["loss"].location = (lx, ly, 0)
        S["loss"].scale = (1, 1, max(st["loss"], 1e-3))
        T[f"loss_{side}"]["ob"].hide_render = st["loss"] < 0.5
        T[f"slot_{side}"]["ob"].hide_render = side == "left" and (st["slot_alloc"] <= 0 or st["sink"] >= 1.0)
        # marker: the rows of H in use (logits), or the rows of the gradient being written (collapse)
        ph = st["phase"]
        mk = None
        if ph == "logits":
            mk = (X0 + H_X0, X0 + H_X0 + 1, ya, yb)
        elif ph == "collapse" and g is not None:
            mk = (X0 + SLOT_X0, X0 + SLOT_X0 + 1, gya, gyb)
        for ob in S["marker"]:
            ob.hide_render = mk is None
        if mk is not None:
            set_frame(S["marker"], mk[0], mk[1], mk[2], mk[3], -0.05, SLAB_Z + 0.1, t=0.14)
        # gauge
        gx0, gx1, gy0, gy1 = S["g"]
        set_box(S["gauge"], gx0, gx1, gy0, gy1, 0, st["gib"] * GAUGE_PER_GIB)
        done = tau >= T_END_C[side]
        T[f"gauge_{side}"]["ob"].data.body = f"loss memory: {fmt_gib(st['gib'])}" + (f"  (peak {fmt_gib(PEAK[side])})" if done else "")
        slow = st["speed"] in ("slow", "slow_discard")
        T[f"timer_{side}"]["ob"].data.body = f"step time {timer(side, tau):.2f}×" + ("   slow motion" if slow else "")
        # phase line and phase words
        if ph == "intro":
            line = ""
        elif ph in ("sink",):
            line = "gradient ↓ into the model"
        elif ph == "done":
            line = "done"
        elif side == "left":
            line = "free the tables" if ph == "free" else "all 3,000 tokens at once"
        else:
            k = st["slice"]
            r0, r1 = SLICE_ROWS[k]
            line = f"slice {k + 1} of {N_SLICES} · {r1 - r0} tokens"
        T[f"phase_{side}"]["ob"].data.body = line
        act = PHASE_IDX.get(ph)
        for i in range(len(WORDS[side])):
            ob = T[f"w{i}_{side}"]["ob"]
            ob.data.materials[0] = ink if i == act else ink3
    T["caption"]["ob"].data.body = caption(tau, sts)
    bpy.context.view_layer.update()
    return sts


def caption(tau, sts):
    L, R = sts["left"], sts["right"]
    if tau < INTRO:
        return "The loss of one 3,000-token step: hidden states H are 5,120 wide; scores, 248,320 wide."
    if tau < T_NORMAL0:
        return {"logits": "Slow motion. Right: scores for the first 128 tokens only (their rows of H × W).",
                "softmax": "Right: softmax, loss and gradient for those 128 rows only.",
                "loss": "Right: softmax, loss and gradient for those 128 rows only.",
                "gradient": "Right: softmax, loss and gradient for those 128 rows only.",
                "collapse": "Right: the strip's gradient × W is 128 × 5,120; it goes into the buffer's rows.",
                "discard": "Right discards the strip; next slice."}[R["phase"]]
    if L["phase"] == "logits":
        return "Left builds the whole score table at once: 3,000 × 248,320."
    if L["phase"] == "softmax":
        return "Left: an FP32 log-softmax of the whole table, kept for the backward pass."
    if L["phase"] == "loss":
        return "Same loss on both sides: each token's loss needs only its own row."
    if L["phase"] == "gradient":
        return f"Left: the gradient table goes on top: up to {fmt_gib(PEAK['left'])} at once."
    if L["phase"] == "collapse":
        return "Left: gradient × W gives the gradient on H, 3,000 × 5,120."
    if L["phase"] == "free" or R["phase"] not in ("sink", "done"):
        return "Left frees its tables; the right finishes its last slices."
    if L["phase"] == "sink" or R["phase"] == "sink":
        return "Each side sends one 3,000 × 5,120 gradient down into the model."
    return (f"Same loss, same gradient (within 0.04%); peak {fmt_gib(PEAK['left'])} vs {fmt_gib(PEAK['right'])}.")


# ---------------------------------------------------------------- frames
def storyboard_secs():
    seg = {s[4]: s for s in SEGS}
    slow = [s for s in SEGS if s[4] == "slow"]          # logits, softmax, loss, gradient, collapse of slice 1
    def at_c(c):                                       # screen time at compute c (normal speed)
        return T_NORMAL0 + (c - C_S1) * SPU
    lp = {ph: (c0, c1) for (c0, c1, _, ph) in PH["left"]}
    return [1.2,
            slow[0][0] + 0.8 * (slow[0][1] - slow[0][0]),             # slice 1: logits
            slow[3][1] - 0.05,                                         # slice 1: gradient done, strip full
            slow[4][0] + 0.55 * (slow[4][1] - slow[4][0]),             # slice 1: write rows
            at_c(lp["softmax"][0] + 0.7 * UNITS["softmax"]),           # left: softmax
            at_c(lp["gradient"][0] + 0.75 * UNITS["gradient"]),       # left: the gradient table on top
            at_c(lp["collapse"][0] + 0.5 * UNITS["collapse"]),         # left: collapse
            T_END - 0.5]


if args.frames == "storyboard":
    secs = storyboard_secs()
    frames = [int(round(s * FPS)) for s in secs]
elif args.frames in ("all", "queue"):
    frames = list(range(N_FRAMES))
else:
    frames = [int(f) for f in args.frames.split(",")]
os.makedirs(args.outdir, exist_ok=True)
log, t_all = [], time.time()
QUEUE = args.frames == "queue"                        # several processes share the frames: each claims one at a time
if QUEUE:
    os.makedirs(os.path.join(args.outdir, "claims"), exist_ok=True)
for f in frames:
    if QUEUE:
        try:
            fd = os.open(os.path.join(args.outdir, "claims", f"{f:04d}"), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, DEVICE.encode())
            os.close(fd)
        except FileExistsError:
            continue
    sts = apply(f)
    scene.render.filepath = os.path.join(args.outdir, f"frame_{f:04d}.png")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    log.append({"frame": f, "time_s": round(f / FPS, 2),
                "left": T["phase_left"]["ob"].data.body, "right": T["phase_right"]["ob"].data.body,
                "phase": [sts["left"]["phase"], sts["right"]["phase"]],
                "gib": [round(sts["left"]["gib"], 3), round(sts["right"]["gib"], 3)],
                "timer": [round(timer("left", f / FPS), 3), round(timer("right", f / FPS), 3)],
                "caption": T["caption"]["ob"].data.body, "seconds": round(time.time() - t0, 2)})
    print("FRAME", json.dumps(log[-1]))
info = {"fps": FPS, "length_s": round(T_END, 2), "frames_total": N_FRAMES, "size": [W_PX, H_PX], "samples": args.samples,
        "device": DEVICE, "seconds_per_compute_unit": SPU, "units": UNITS, "chunk_cost": CHUNK_COST,
        "segments": SEGS, "compute_end_s": T_END_C, "done_s": T_DONE,
        "bytes_per_entry": BYTES, "band_gib_full": {"left": band_gib("left", N_TOK), "right": band_gib("right", CHUNK)},
        "scales": {"width_units": {"d": 1.0, "V": WIDEN}, "rows_depth_units": D, "z_per_byte": ZB, "gauge_units_per_gib": GAUGE_PER_GIB},
        "peaks_gib": PEAK, "rendered": log, "wall_seconds": round(time.time() - t_all, 1)}
kit.write_json(os.path.join(args.outdir, f"frames_{args.tag}.json" if args.tag else "frames.json"), info)

if args.frames == "storyboard":                       # contact sheet: 2 across, 4 down
    gap = 6
    sheet = np.full(((H_PX + gap) * 4 + gap, (W_PX + gap) * 2 + gap, 4), [0.05, 0.05, 0.09, 1.0], dtype=np.float32)
    for k, f in enumerate(frames):
        img = bpy.data.images.load(os.path.join(args.outdir, f"frame_{f:04d}.png"))
        px = np.array(img.pixels[:], dtype=np.float32).reshape(H_PX, W_PX, 4)        # rows bottom-up
        r, c = k // 2, k % 2
        y0 = sheet.shape[0] - (r + 1) * (H_PX + gap)
        x0 = gap + c * (W_PX + gap)
        sheet[y0:y0 + H_PX, x0:x0 + W_PX] = px
        bpy.data.images.remove(img)
    out = bpy.data.images.new("sheet", sheet.shape[1], sheet.shape[0], alpha=False)
    out.pixels[:] = sheet.ravel()
    out.filepath_raw = args.sheet
    out.file_format = "PNG"
    out.save()
    print("SHEET", args.sheet, sheet.shape[1], "x", sheet.shape[0])
