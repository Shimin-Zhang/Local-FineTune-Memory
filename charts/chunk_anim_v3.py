"""Animation v3 (the video): what the chunked loss does in practice, stock loss above, chunked loss below
(Qwen3.8-27B, one 3,000-token step), timed by the measured time of the loss alone. v2 (charts/chunk_anim_v2.py) made
the approved storyboard; v1 is charts/chunk_anim.py.

Tokens run left to right along one line (3,000 positions, the token axis on its own scale). Features run up, at the
true ratio: each token's hidden state is a short column (5,120: H, a low band along the line) and its score row a
column 48.5x taller (248,320). The score table's copies are layers stacked toward the camera, their depth set by bytes
per entry (BF16 logits 2, FP32 log-softmax 4, the gradient the rest of the measured peak), so volume is memory.
W, the output layer (5,120 x 248,320), is a slim panel at the left end. In front of H runs dL/dH, the gradient on H
(3,000 x 5,120, H's height).
Stock (above): the whole wall of score columns rises over all 3,000 tokens at once (logits), the FP32 log-softmax
layer in front (kept for backward), the loss, the gradient layer in front (peak); gradient x W collapses every
column back down to H's height (dL/dH); the walls fade out (freed); the gradient goes down into the model.
Chunked (below): the gradient buffer is allocated empty; a 128-token window moves left to right (24 slices, the last
56 tokens): its 128 columns rise in the same layers, loss, gradient, they collapse to H's height and are written
into the buffer's 128 positions, the columns are dropped; then the next window. The full buffer goes into the model.

Timing: one clock in milliseconds of the loss alone, measured on the RTX 4090 with the 27B's shapes
(data speed.loss_only: stock 136.7 ms, chunked 192.3 ms), runs both rows at the same ms per second of screen, so the
chunked row visibly ends later. Inside each row the phases keep schematic shares (UNITS), scaled to the row's
measured total; the chunked row's extra time is spread over its slices. The whole training step is only about 3%
slower (the loss is a small part of it); a note on screen says so. Memory counts when a table is allocated (it
appears whole within ALLOC_T), not as it is computed.
Data: charts/data/chunked_loss_3000.json.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/chunk_anim_v3.py -- \
    --frames key                                         # a few key frames at 1920x1080 for a look
    --frames 0,90,180 [--size 1920x1080 --samples 64]    # any frames
    --frames all|queue                                   # every frame of the video (then ffmpeg -> MP4)
"""
import argparse, json, math, os, sys, time
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--frames", default="key")
ap.add_argument("--size", default="1920x1080")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--outdir", default=os.path.join(HERE, "out", "chunk_anim_v3"))
ap.add_argument("--sheet", default=os.path.join(HERE, "out", "chunk_anim_storyboard_v3.png"))
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


# ---------------------------------------------------------------- timeline, driven by one clock in measured milliseconds
FPS = 30
LOSS_MS = dat["speed"]["loss_only"]                      # the loss alone on the 4090, 27B shapes
L_MS, R_MS = LOSS_MS["stock_ms"], LOSS_MS["chunked_ms"]  # 136.7, 192.3
UNITS = {"logits": 1.0, "softmax": 0.25, "loss": 0.15, "gradient": 0.25, "collapse": 1.0}   # schematic shares
ORDER = ("logits", "softmax", "loss", "gradient", "collapse")
CHUNK_COST = R_MS / L_MS                                 # measured ratio, 1.41: spread over the chunked row's slices
assert abs(CHUNK_COST - LOSS_MS["ratio"]) < 0.005
MS_PER_UNIT = L_MS / sum(UNITS.values())                 # each row's phases scaled to its measured total
L_TOTAL = L_MS                                           # the clock runs in ms
R_TOTAL = R_MS
MS_PER_S = 32.0                                          # ms of loss per second of screen: about 7.7 frames per slice
INTRO = 0.5
FREE_T, DISCARD_T, SINK_T, OUTRO = 0.4, 0.2, 0.6, 1.5


def phase_list(side):
    """[(c0, c1, slice index or None, phase)] on the clock, in ms."""
    out, c = [], 0.0
    if side == "left":
        for ph in ORDER:
            u = UNITS[ph] * MS_PER_UNIT
            out.append((c, c + u, None, ph))
            c += u
        return out
    for k, (r0, r1) in enumerate(SLICE_ROWS):
        for ph in ORDER:
            u = UNITS[ph] * MS_PER_UNIT * (r1 - r0) / N_TOK * CHUNK_COST
            out.append((c, c + u, k, ph))
            c += u
    return out


PH = {s: phase_list(s) for s in ("left", "right")}
assert abs(PH["left"][-1][1] - L_MS) < 1e-6 and abs(PH["right"][-1][1] - R_MS) < 1e-6
SEGS = [(0.0, INTRO, 0.0, 0.0, "intro"), (INTRO, INTRO + R_MS / MS_PER_S, 0.0, R_MS, "normal")]   # (tau0, tau1, c0, c1, kind)
T_NORMAL0 = INTRO
T_END_C = {"left": INTRO + L_MS / MS_PER_S, "right": INTRO + R_MS / MS_PER_S}
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


ALLOC_T = 0.2                  # a table is allocated whole when its phase starts: it appears within this many seconds


def grown(tau, c0, c1):
    """0..1: how far a table allocated at compute c0 has appeared (fast: allocation, not computation)."""
    ta, tb = tau_at(c0), tau_at(c1)
    return clamp01((tau - ta) / max(1e-6, min(ALLOC_T, 0.5 * (tb - ta)))) if tau >= ta else 0.0


def state(side, tau):
    """What exists on one side at screen time tau. Memory is counted when it is allocated, not as it is computed."""
    c, kind = clock(tau)
    total = L_TOTAL if side == "left" else R_TOTAL
    st = {"bands": [0.0, 0.0, 0.0], "loss": 0.0, "loss_outline": False, "ghost": None, "slot_alloc": 0.0, "slot_solid": False,
          "rows_done": 0, "sink": 0.0, "slice": None, "phase": None, "post": None, "c": min(c, total), "speed": kind}
    if side == "right":
        st["slot_alloc"] = 1.0                           # the buffer is allocated up front (empty)
    if kind == "intro":
        st["phase"] = "intro"
    elif c < total:
        cur = next((p for p in PH[side] if p[0] <= c < p[1]), PH[side][-1])
        k = cur[2]
        st["slice"], st["phase"] = k, cur[3]
        prog, grow = {}, {}
        for (c0, c1, kk, ph) in PH[side]:
            if kk == k:
                prog[ph] = clamp01((c - c0) / (c1 - c0))
                grow[ph] = grown(tau, c0, c1) if c >= c0 else 0.0
        st["bands"] = [grow["logits"], grow["softmax"], grow["gradient"]]
        if side == "left":                              # stock: the whole loss at once, in its loss phase
            st["loss"] = grow["loss"]
            st["loss_outline"] = st["loss"] > 0
        else:                                            # chunked: a running sum, total += loss of each slice
            r0, r1 = SLICE_ROWS[k]
            st["loss"] = (r0 + (r1 - r0) * prog["loss"]) / N_TOK
            st["loss_outline"] = k > 0 or prog["loss"] > 0
        if side == "left":
            st["slot_alloc"] = grow["collapse"]          # the gradient on H: allocated, then filled by gradient x W
        else:
            st["rows_done"] = SLICE_ROWS[k][0]
        if 0.0 < prog["collapse"] < 1.0:
            st["ghost"] = prog["collapse"]
    else:                                                # compute done: free / discard, then down into the model
        st["loss"], st["loss_outline"] = 1.0, True
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
        if st["phase"] in ("free", "discard"):          # freed: the walls fade out at full height (height = features)
            st["bands"] = [1.0 - st["post"]] * 3
            st["fading"] = True
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
    """Milliseconds of the loss done by time tau (the stock row stops at 136.7, the chunked at 192.3)."""
    return state(side, tau)["c"]


PEAK = {s: max(state(s, k / FPS)["gib"] for k in range(N_FRAMES)) for s in ("left", "right")}

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
GIB_SERIES = {s: [state(s, k / FPS)["gib"] for k in range(N_FRAMES)] for s in ("left", "right")}

# ---------------------------------------------------------------- scene: stock above (state key "left"), chunked below ("right")
HD = 0.40                      # a hidden state's column: 5,120 features
VH = HD * WIDEN                # a score column: 248,320 features, 48.5x as tall
YB = 0.5                       # depth per byte of each entry: the copies stand one in front of the other
LAYER_GAP = 0.35               # a small gap between copies, so each reads as its own wall
LAYER_F = {}                   # per case: the depth range (from the back, toward the camera) of each copy
for s_ in BYTES:
    f_, LAYER_F[s_] = 0.0, []
    for b_ in BYTES[s_]:
        LAYER_F[s_].append((f_, f_ + b_ * YB))
        f_ += b_ * YB + LAYER_GAP
FW = max(LAYER_F[s_][-1][1] for s_ in BYTES)            # the wall's full depth
SLAB_F = 2 * YB                                          # BF16: H, W, the gradient on H
FH0 = FW + 0.75                                          # H: a low band in front of the wall
FG0 = FH0 + SLAB_F + 0.7                                 # the gradient on H: in front of H
W_X0 = -1.9                                              # W: a slim panel at the left end, 5,120 wide, 248,320 tall
ELEVATION, AZIMUTH, LENS = 28.0, -3.0, 135.0
BASE_T, BASE_DROP = 0.45, 0.9
LX = 80.0                      # 3,000 tokens, left to right (the token axis has its own scale; solved below to fill the width)


def tok_x(t):
    return t / N_TOK * LX


def Y(f):                                                # depth toward the camera -> world y
    return -f


def case_pts(zo, lx):
    xs = (W_X0 - 0.9, lx + 3.3)
    ys = (Y(-0.9), Y(FG0 + SLAB_F + 0.9))
    zs = (zo - BASE_T - BASE_DROP, zo + VH)
    return [Vector((x, y, z)) for x in xs for y in ys for z in zs]


direction = kit.view_direction(ELEVATION, AZIMUTH)
cam = kit.make_camera(scene, LENS)
EM_A, SUB_A, LAB_A = 0.019, 0.0140, 0.0118
em_y, sub_y = EM_A * rx / ry, SUB_A * rx / ry

# ---------------------------------------------------------------- text objects first: the left panel's width sets where the geometry starts
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
ink3 = kit.glow_material("ink3", "#5e5f6b", 1.0)        # phase words not active
inks = {"h": kit.glow_material("ink_h", kit.COLOURS["activations"], 1.0), "w": kit.glow_material("ink_w", kit.COLOURS["frozen"], 1.0),
        "l0": kit.glow_material("ink_l0", "#bdb6f5", 1.0), "l1": kit.glow_material("ink_l1", "#6357cf", 1.0),
        "g": kit.glow_material("ink_g", kit.COLOURS["gradients"], 1.0), "loss": kit.glow_material("ink_loss", kit.COLOURS["loss"], 1.0)}
T = {}


def text(key, body, size, mat, ax="LEFT", ay="BOTTOM_BASELINE"):
    ob, w, _ = kit.text_object(f"txt_{key}", body, ax, ay)
    T[key] = {"ob": ob, "size": size, "mat": mat, "w": w}


def bar(name, colour):
    """A flat bar anchored at its left middle (for the memory meters)."""
    ob = kit.mesh_object(name, [(0, -0.5, 0), (1, -0.5, 0), (1, 0.5, 0), (0, 0.5, 0)], [(0, 1, 2, 3)],
                         [kit.glow_material(name, colour, 1.0)])
    kit.no_shadow(ob)
    return ob


WORDS = {"left": ["logits", "softmax", "loss", "gradient", "collapse", "free"],
         "right": ["logits", "softmax", "loss", "gradient", "write rows", "discard"]}
PHASE_IDX = {"logits": 0, "softmax": 1, "loss": 2, "gradient": 3, "collapse": 4, "free": 5, "discard": 5}
LEGEND = [("H  3,000 × 5,120", "h"), ("W  5,120 × 248,320", "w"), ("score columns, 248,320 each:", None),
          ("logits BF16", "l0"), ("log-softmax FP32", "l1"), ("gradient", "g"),
          ("dL/dH  3,000 × 5,120", "g"), ("loss", "loss")]
METER = {}
for side, title in (("left", "stock loss"), ("right", "chunked loss")):
    text(f"title_{side}", title, EM_A, ink2)
    text(f"phase_{side}", "slice 24 of 24 · 128 tokens", SUB_A, ink)
    text(f"gauge_{side}", "loss memory: 0.45 GiB", SUB_A, ink)
    text(f"timer_{side}", "loss time 192 ms (1.41×)", SUB_A, ink)
    for i, w in enumerate(WORDS[side]):
        text(f"w{i}_{side}", w, SUB_A, ink3)
    METER[side] = {"bg": bar(f"meter_bg_{side}", "#2a2e38"), "fill": bar(f"meter_fill_{side}", "#e9e9e9"),
                   "peak": bar(f"meter_peak_{side}", "#b2b2b2")}
for i, (body, key) in enumerate(LEGEND):
    text(f"lg{i}", body, LAB_A, inks[key] if key else ink2)
NOTE_A = SUB_A * 0.8
text("timer_note", "the loss alone, measured on the 4090", NOTE_A, ink2)
text("timer_note2", "the whole training step: about 3% slower", NOTE_A, ink2)
text("caption", "", SUB_A, ink, "CENTER")
text("note", "score table : hidden states = 248,320 : 5,120 per token (48×)", SUB_A * 0.8, ink2, "CENTER")
WORD_GAP = 0.8
PANEL_W = max([T[f"phase_{s_}"]["w"] * SUB_A for s_ in WORDS] + [T[k_]["w"] * NOTE_A for k_ in ("timer_note", "timer_note2")] +
              [T[f"timer_{s_}"]["w"] * SUB_A for s_ in WORDS] +
              [sum(T[f"w{i}_{s_}"]["w"] + WORD_GAP for i in r) * SUB_A for s_ in WORDS for r in ((0, 1, 2), (3, 4, 5))])
X_P = 0.025                                              # the left panel: title, phase, words, memory, timer
X_G0, X_G1 = X_P + PANEL_W + 0.02, 0.978                 # the geometry fills the rest of the width
ML = PANEL_W                                             # the meter's full length = 9.4 GiB
TOP_LIM = 0.985
BOT_LIM = 0.022 + 4.0 * sub_y                            # legend, caption and footer under the lower case
GAP_NEED = 0.04


def fit(zt, lx):
    """Frame both cases (upper one at height zt) into the geometry area; returns (gap between cases, width used)."""
    pts = case_pts(0.0, lx) + case_pts(zt, lx)
    target, dist = sum(pts, Vector()) / len(pts), 600.0
    for _ in range(40):
        kit.aim(cam, target, dist, direction)
        sp = [kit.to_screen(scene, cam, p) for p in pts]
        x0, x1, y0, y1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
        z = min((X_G1 - X_G0) / (x1 - x0), (TOP_LIM - BOT_LIM) / (y1 - y0))
        fw_, fh_ = kit.frame_size(scene, cam, dist)
        Rv = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
        Uv = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
        target = target + Rv * ((x0 + x1) / 2 - (X_G0 + X_G1) / 2) * fw_ + Uv * ((y0 + y1) / 2 - (TOP_LIM + BOT_LIM) / 2) * fh_
        if abs(z - 1) < 0.0005:
            break
        dist /= z
    kit.aim(cam, target, dist, direction)
    lo = [kit.to_screen(scene, cam, p) for p in case_pts(0.0, lx)]
    up = [kit.to_screen(scene, cam, p) for p in case_pts(zt, lx)]
    return min(p.y for p in up) - max(p.y for p in lo), max(p.x for p in lo + up) - min(p.x for p in lo + up)


Z_TOP = VH + 8.0
for _ in range(30):                                      # solve the upper case's height (gap) and the token axis (width)
    g0, wd = fit(Z_TOP, LX)
    slope = (fit(Z_TOP + 1.0, LX)[0] - g0) / 1.0
    Z_TOP -= (g0 - GAP_NEED) / slope
    LX *= ((X_G1 - X_G0) / wd) ** 0.8
    if abs(g0 - GAP_NEED) < 0.0005 and abs(wd - (X_G1 - X_G0)) < 0.0015:
        break
fit(Z_TOP, LX)
print("Z_TOP", round(Z_TOP, 2), "LX", round(LX, 2), "PANEL_W", round(PANEL_W, 3))

h_m = kit.material("m_hidden", kit.COLOURS["activations"], emit=0.12, rough=0.85, spec=0.12)
w_m = kit.material("m_weights", kit.COLOURS["frozen"], emit=0.10, rough=0.85, spec=0.12)
LAYER_COL = ["#bdb6f5", "#6357cf", kit.COLOURS["gradients"]]      # BF16 logits, FP32 log-softmax, gradient
band_m = {s_: [kit.material(f"m_logits_{s_}", LAYER_COL[0], emit=0.14, rough=0.85, spec=0.12),     # per case: each fades alone
               kit.material(f"m_logsoftmax_{s_}", LAYER_COL[1], emit=0.18, rough=0.85, spec=0.12),
               kit.material(f"m_gradtable_{s_}", LAYER_COL[2], emit=0.12, rough=0.85, spec=0.12)] for s_ in ("left", "right")}


def set_alpha(m, a):
    next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED").inputs["Alpha"].default_value = a
grad_m = kit.material("m_grad", kit.COLOURS["gradients"], emit=0.14, rough=0.85, spec=0.12)
empty_m = kit.veil_material("m_empty", 0.07, kit.hex_lin(kit.COLOURS["gradients"]))     # dL/dH allocated, still empty: a ghost
ghost_m = kit.material("m_ghost", kit.COLOURS["gradients"], emit=0.9, rough=0.85, spec=0.12)   # gradient x W, on its way
loss_m = kit.material("m_loss", kit.COLOURS["loss"], emit=0.15, rough=0.85, spec=0.12)
frame_m = kit.material("m_frame", "#59606b", rough=0.6, spec=0.2)
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
    ZO = Z_TOP if side == "left" else 0.0
    S = {"ZO": ZO}
    S["W"] = kit.cuboid(f"{side}_W", (W_X0, Y(SLAB_F), ZO), (W_X0 + HD, Y(0), ZO + VH), w_m)
    S["H"] = kit.cuboid(f"{side}_H", (0, Y(FH0 + SLAB_F), ZO), (LX, Y(FH0), ZO + HD), h_m)
    S["floor"] = kit.cuboid(f"{side}_floor", (0, Y(FW), ZO), (LX, Y(0), ZO + 0.02), floor_m)      # the wall's footprint
    e, yf = 0.07, Y(FW) - 0.1                          # the full wall's edges: where the whole table would stand
    for k, (lo_, hi_) in enumerate((((-e, yf - e, ZO), (e, yf, ZO + VH)), ((LX - e, yf - e, ZO), (LX + e, yf, ZO + VH)),
                                     ((-e, yf - e, ZO + VH - e), (LX + e, yf, ZO + VH)),
                                     ((-e, yf, ZO + VH - e), (e, Y(0), ZO + VH)), ((LX - e, yf, ZO + VH - e), (LX + e, Y(0), ZO + VH)),
                                     ((-e, Y(0) - e, ZO + VH - e), (LX + e, Y(0), ZO + VH)))):
        kit.no_shadow(kit.cuboid(f"{side}_edge{k}", lo_, hi_, frame_m))
    S["layers"] = [unit_box(f"{side}_layer{k}", band_m[side][k]) for k in range(3)]
    S["slot"] = unit_box(f"{side}_slot", grad_m)
    S["empty"] = unit_box(f"{side}_empty", empty_m, shadow=False)
    S["ghost"] = unit_box(f"{side}_ghost", ghost_m, shadow=False)
    LS = 1.8                                             # the loss square's size
    S["loss"] = kit.cuboid(f"{side}_loss", (0, 0, 0), (LS, LS, LS), loss_m)
    S["loss_at"] = (LX + 0.8, Y(1.0), ZO)
    lx_, ly_, lz_ = S["loss_at"]                         # the loss square's outline: the running sum fills it
    x0_, x1_, y0_, y1_, z0_, z1_, t_ = lx_, lx_ + LS, ly_ - LS, ly_, lz_, lz_ + LS, 0.08
    S["loss_edges"] = []
    for (ax, ay, az) in [(a_, b_, None) for a_ in (x0_, x1_) for b_ in (y0_, y1_)]:      # 4 vertical edges
        S["loss_edges"].append(kit.cuboid(f"{side}_lossv{len(S['loss_edges'])}", (ax - t_ / 2, ay - t_ / 2, z0_), (ax + t_ / 2, ay + t_ / 2, z1_), loss_m))
    for zz in (z0_, z1_):                                # top and bottom squares
        for (lo_, hi_) in (((x0_ - t_ / 2, y0_ - t_ / 2), (x1_ + t_ / 2, y0_ + t_ / 2)), ((x0_ - t_ / 2, y1_ - t_ / 2), (x1_ + t_ / 2, y1_ + t_ / 2)),
                           ((x0_ - t_ / 2, y0_ - t_ / 2), (x0_ + t_ / 2, y1_ + t_ / 2)), ((x1_ - t_ / 2, y0_ - t_ / 2), (x1_ + t_ / 2, y1_ + t_ / 2))):
            S["loss_edges"].append(kit.cuboid(f"{side}_lossh{len(S['loss_edges'])}", (lo_[0], lo_[1], zz - t_ / 2), (hi_[0], hi_[1], zz + t_ / 2), loss_m))
    for ob_ in S["loss_edges"]:
        kit.no_shadow(ob_)
    S["marker"] = [unit_box(f"{side}_marker{k}", glow, shadow=False) for k in range(4)]
    lo, hi = Vector((W_X0 - 0.3, Y(FG0 + SLAB_F), ZO)), Vector((LX + 2.6, Y(0), ZO))
    S["base"], S["base_info"] = kit.floating_base(lo, hi, margin=0.7 / (hi.x - lo.x), seed=41 + si, dressing=False,
                                                  drop=BASE_DROP, thickness=BASE_T)
    SIDES[side] = S
kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=18, rim_turn=-125)

# ---------------------------------------------------------------- placing the text and the meters
d_text = kit.to_screen(scene, cam, (LX / 2, Y(FG0 + 12), Z_TOP / 2)).z
FW_TEXT = kit.frame_size(scene, cam, d_text)[0]


def put(key, sx, sy):
    kit.place_on_screen(scene, cam, T[key]["ob"], sx, sy, d_text, T[key]["size"], T[key]["mat"])


def put_bar(ob, sx, sy, length, thick, depth_add=0.0):
    ob.location = kit.to_world(scene, cam, sx, sy, d_text + depth_add)
    ob.rotation_euler = cam.matrix_world.to_quaternion().to_euler()
    fw = kit.frame_size(scene, cam, d_text + depth_add)[0]
    ob.scale = (max(length, 1e-5) * fw, thick * fw, 1.0)


EXT = {}
for side, S in SIDES.items():
    sp = [kit.to_screen(scene, cam, p) for p in case_pts(S["ZO"], LX)]
    EXT[side] = {"b": min(p.y for p in sp), "t": max(p.y for p in sp)}
for side in ("left", "right"):                           # the left panel, top down from the case's top
    y = EXT[side]["t"] - 0.75 * em_y
    put(f"title_{side}", X_P, y)
    y -= 1.25 * em_y
    put(f"phase_{side}", X_P, y)
    y -= 0.4 * sub_y
    for row in ((0, 1, 2), (3, 4, 5)):
        y -= 1.4 * sub_y if row[0] == 0 else 1.15 * sub_y
        sx = X_P
        for i in row:
            put(f"w{i}_{side}", sx, y)
            sx += (T[f"w{i}_{side}"]["w"] + WORD_GAP) * SUB_A
    y -= 1.6 * sub_y
    put(f"gauge_{side}", X_P, y)
    y -= 0.75 * sub_y
    m = METER[side]
    put_bar(m["bg"], X_P, y, ML, 0.0085, 0.4)
    put_bar(m["fill"], X_P, y, 0.0, 0.0085, 0.0)
    put_bar(m["peak"], X_P, y, 0.0012, 0.016, -0.2)
    EXT[side]["meter_y"] = y
    y -= 1.55 * sub_y
    put(f"timer_{side}", X_P, y)
    if side == "right":                                  # the timers are the loss alone; the step barely changes
        y -= 1.05 * sub_y
        put("timer_note", X_P, y)
        y -= 0.85 * sub_y
        put("timer_note2", X_P, y)
X_M = X_P
widths = [(T[f"lg{i}"]["w"] + (0.6 if LEGEND[i][1] is None else 1.5)) * LAB_A for i in range(len(LEGEND))]
sx, ly = (X_G0 + X_G1) / 2 - (sum(widths) - 1.5 * LAB_A) / 2, EXT["right"]["b"] - 1.2 * sub_y
for i, w_ in enumerate(widths):                          # one legend for both cases, under the lower one
    put(f"lg{i}", sx, ly)
    sx += w_
put("caption", 0.5, ly - 1.55 * sub_y)
put("note", 0.5, 0.022)


def fmt_gib(x):
    return f"{x:.1f} GiB" if x >= 0.995 else f"{x:.2f} GiB"


def lerp_box(a, b, u):
    return [p + (q - p) * u for p, q in zip(a, b)]


def apply(frame):
    tau = frame / FPS
    sts = {}
    for side, S in SIDES.items():
        st = state(side, tau)
        sts[side] = st
        ZO = S["ZO"]
        if side == "left":
            xa, xb = 0.0, LX
        elif st["slice"] is not None:
            r0, r1 = SLICE_ROWS[st["slice"]]
            xa, xb = tok_x(r0), tok_x(r1)
        else:
            xa, xb = 0.0, LX
        # the score columns' copies: the whole wall (stock) or the window's 128 columns (chunked)
        fading = st.get("fading", False)                 # freed walls fade out at full height: height is features only
        for k, ob in enumerate(S["layers"]):
            f0, f1 = LAYER_F[side][k]
            frac = st["bands"][k]
            h = VH * (1.0 if fading else frac)
            set_alpha(band_m[side][k], frac if fading else 1.0)
            ob.hide_render = frac < 1e-3 or (side == "right" and st["slice"] is None)
            if not ob.hide_render:
                set_box(ob, xa, xb, Y(f1), Y(f0), ZO, ZO + h)
        # the gradient on H: stock allocates it at the collapse and it is solid once written; chunked fills it window by window
        sink = st["sink"] * (HD + BASE_T + 0.2)
        gy0, gy1 = Y(FG0 + SLAB_F), Y(FG0)
        if side == "left":
            a = st["slot_alloc"]
            S["slot"].hide_render = not st["slot_solid"] or st["sink"] >= 1.0
            set_box(S["slot"], 0, LX, gy0, gy1, ZO - sink, ZO + HD - sink)
            S["empty"].hide_render = st["slot_solid"] or a < 1e-3
            set_box(S["empty"], 0, LX, gy0, gy1, ZO, ZO + HD * max(a, 1e-3))
        else:
            xr = tok_x(st["rows_done"])
            S["slot"].hide_render = st["rows_done"] == 0 or st["sink"] >= 1.0
            set_box(S["slot"], 0, xr, gy0, gy1, ZO - sink, ZO + HD - sink)
            S["empty"].hide_render = st["sink"] >= 1.0 or st["rows_done"] >= N_TOK
            set_box(S["empty"], xr, LX, gy0, gy1, ZO - sink, ZO + HD - sink)
        # gradient x W: a bright copy leaves the gradient layer, collapses down to H's height, hops over H into place
        g = st["ghost"]
        S["ghost"].hide_render = g is None
        if g is not None:
            gf0, gf1 = LAYER_F[side][2]
            B0, B1 = (gf0, gf1, 0.0, VH), (gf1 + 0.15, gf1 + 0.55, 0.0, VH)
            B2, B3 = (gf1 + 0.15, gf1 + 0.55, 0.0, HD), (FG0, FG0 + SLAB_F, 0.0, HD)
            s = g * g * (3 - 2 * g)
            lift = 0.0
            if s < 0.15:
                b = lerp_box(B0, B1, s / 0.15)
            elif s < 0.75:
                b = lerp_box(B1, B2, (s - 0.15) / 0.6)
            else:
                u = (s - 0.75) / 0.25
                b = lerp_box(B2, B3, u)
                lift = math.sin(math.pi * u) * 0.9
            set_box(S["ghost"], xa, xb, Y(b[1]), Y(b[0]), ZO + b[2] + lift, ZO + b[3] + lift)
        lx, ly, lz = S["loss_at"]
        S["loss"].hide_render = st["loss"] <= 1e-3
        for ob_ in S["loss_edges"]:
            ob_.hide_render = not st["loss_outline"]
        S["loss"].location = (lx, ly - LS, lz)
        S["loss"].scale = (1, 1, max(st["loss"], 1e-3))
        # marker: the window of H in use (logits), or the window of the gradient being written (collapse)
        ph = st["phase"]
        mk = None
        if ph == "logits":
            mk = (Y(FH0 + SLAB_F), Y(FH0))
        elif ph == "collapse" and g is not None:
            mk = (gy0, gy1)
        for ob in S["marker"]:
            ob.hide_render = mk is None
        if mk is not None:
            set_frame(S["marker"], xa, xb, mk[0], mk[1], ZO - 0.05, ZO + HD + 0.06, t=0.18)
        # header: phase, words, memory, timer
        if ph == "intro":
            line = ""
        elif ph == "sink":
            line = "dL/dH ↓ into the model"
        elif ph == "done":
            line = "done"
        elif side == "left":
            line = "free the walls" if ph == "free" else "all 3,000 tokens at once"
        else:
            r0, r1 = SLICE_ROWS[st["slice"]]
            line = f"slice {st['slice'] + 1} of {N_SLICES} · {r1 - r0} tokens"
        T[f"phase_{side}"]["ob"].data.body = line
        act = PHASE_IDX.get(ph)
        for i in range(len(WORDS[side])):
            T[f"w{i}_{side}"]["ob"].data.materials[0] = ink if i == act else ink3
        T[f"gauge_{side}"]["ob"].data.body = f"loss memory: {fmt_gib(st['gib'])}"
        ms = timer(side, tau)
        T[f"timer_{side}"]["ob"].data.body = f"loss time {ms:.0f} ms" + (
            f" ({R_MS / L_MS:.2f}×)" if side == "right" and tau >= T_END_C["right"] else "")
        m, my = METER[side], EXT[side]["meter_y"]
        put_bar(m["fill"], X_M, my, ML * st["gib"] / PEAK_STOCK, 0.0085, 0.0)
        pk = max(GIB_SERIES[side][:frame + 1])
        put_bar(m["peak"], X_M + ML * pk / PEAK_STOCK - 0.0006, my, 0.0012, 0.016, -0.2)
    T["caption"]["ob"].data.body = caption(tau, sts)
    bpy.context.view_layer.update()
    return sts


def caption(tau, sts):
    """Few, long-lived captions: the whole video is under 10 s."""
    if tau < INTRO + PH["left"][3][1] / MS_PER_S:        # until the stock's gradient wall is done
        return "Stock: score columns for all 3,000 tokens at once. Chunked: 128 tokens at a time, 24 times."
    if tau < T_END_C["left"]:
        return "Both take each column back down to 5,120 (gradient × W): stock all at once, chunked per window."
    if tau < T_END_C["right"] + DISCARD_T:
        return f"Stock is done at {L_MS:.0f} ms; chunked is still going: the loss alone takes {R_MS / L_MS:.2f}× as long."
    return f"Same loss, same gradient (within 0.04%); peak {fmt_gib(PEAK['left'])} vs {fmt_gib(PEAK['right'])}."


# ---------------------------------------------------------------- frames
def key_secs():
    """Frames to look at before the full render (and for the contact sheet)."""
    lp = {ph: (c0, c1) for (c0, c1, _, ph) in PH["left"]}
    at = lambda c: INTRO + c / MS_PER_S                  # noqa: E731
    return {"intro": 0.3,
            "chunked slice 2, loss partly summed": INTRO + next(c1 for (c0, c1, k, ph) in PH["right"] if k == 1 and ph == "loss") / MS_PER_S + 0.02,
            "stock logits": at(0.5 * lp["logits"][1]),
            "stock softmax": at(lp["softmax"][0] + 0.7 * (lp["softmax"][1] - lp["softmax"][0])),
            "stock gradient (peak)": at(lp["gradient"][0] + 0.8 * (lp["gradient"][1] - lp["gradient"][0])),
            "stock collapse": at(lp["collapse"][0] + 0.45 * (lp["collapse"][1] - lp["collapse"][0])),
            "stock fading (free)": T_END_C["left"] + 0.5 * FREE_T,
            "stock holds, chunked finishing": T_END_C["right"] - 0.4,
            "final hold": T_END - 0.2}


KEY = key_secs()
if args.frames == "key":
    frames = sorted({min(N_FRAMES - 1, int(round(s_ * FPS))) for s_ in KEY.values()})
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
                "stock": T["phase_left"]["ob"].data.body, "chunked": T["phase_right"]["ob"].data.body,
                "phase": [sts["left"]["phase"], sts["right"]["phase"]],
                "gib": [round(sts["left"]["gib"], 3), round(sts["right"]["gib"], 3)],
                "timer": [round(timer("left", f / FPS), 3), round(timer("right", f / FPS), 3)],
                "caption": T["caption"]["ob"].data.body, "seconds": round(time.time() - t0, 2)})
    print("FRAME", json.dumps(log[-1]))
info = {"fps": FPS, "length_s": round(T_END, 2), "frames_total": N_FRAMES, "size": [W_PX, H_PX], "samples": args.samples,
        "device": DEVICE, "ms_per_second": MS_PER_S, "loss_ms": {"stock": L_MS, "chunked": R_MS}, "units": UNITS,
        "chunk_cost": CHUNK_COST, "key_frames": {k_: int(round(v_ * FPS)) for k_, v_ in KEY.items()},
        "timer_stops_frame": {s_: math.ceil(T_END_C[s_] * FPS - 1e-9) for s_ in T_END_C},
        "segments": SEGS, "compute_end_s": T_END_C, "done_s": T_DONE,
        "bytes_per_entry": BYTES, "band_gib_full": {"left": band_gib("left", N_TOK), "right": band_gib("right", CHUNK)},
        "scales": {"tokens_x_units": LX, "hidden_height_units": HD, "score_height_units": round(VH, 3),
                   "depth_per_byte": YB, "z_top": round(Z_TOP, 3), "meter_full_gib": PEAK_STOCK},
        "peaks_gib": PEAK, "rendered": log, "wall_seconds": round(time.time() - t_all, 1)}
kit.write_json(os.path.join(args.outdir, f"frames_{args.tag}.json" if args.tag else "frames.json"), info)

