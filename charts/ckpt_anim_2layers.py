"""Animation: what gradient checkpointing does during one training step, shown on 2 layers and the loss.

Side by side: left without checkpointing, right with it. Each side: layer 1, layer 2 and the loss as a short column;
beside each layer, what it keeps for the backward pass as a bar at one shared MiB scale (BAR_MIB_PER_UNIT): a layer's
internals 2,193 MiB, its input 29.3 MiB (true 75:1); a gauge shows what the two layers keep for the backward pass.
Left: forward through layer 1 then 2, each leaving its full block; loss; backward through layer 2 then 1, each block
freed after use. Right: forward keeps only each layer's input (the internals are computed, used and dropped); loss;
backward: layer 2's internals are recomputed from its input, backprop through it (its adapter's gradients and the
gradient for layer 1's output), freed; then layer 1. The right side takes longer: its recompute steps.
Data: results/saved_activations.json (a linear-attention layer: 2,193.2 MiB kept, 29.3 MiB input).

One build serves the storyboard and the video: state(side, seconds) sets every frame of the timeline.
~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/ckpt_anim.py -- \
    --frames storyboard                                  # 8 key frames at 480x270 + charts/out/ckpt_anim_storyboard.png
    --frames 0,240,480 [--size 1920x1080 --samples 64]   # any frames
    --frames all --size 1920x1080 --samples 64           # every frame of the video (then ffmpeg -> MP4)
"""
import argparse, json, math, os, sys, time
import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--frames", default="storyboard")
ap.add_argument("--size", default="480x270")
ap.add_argument("--samples", type=int, default=16)
ap.add_argument("--outdir", default=os.path.join(HERE, "out", "ckpt_anim"))
ap.add_argument("--sheet", default=os.path.join(HERE, "out", "ckpt_anim_storyboard.png"))
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX

# ---------------------------------------------------------------- data
sa = json.load(open(os.path.join(ROOT, "results", "saved_activations.json")))
lin = next(L for L in sa["layers"] if L["layer_type"] == "linear_attention")
KEPT, INPUT = lin["total_mib"], lin["layer_input_mib"]
assert (KEPT, INPUT) == (2193.2, 29.3)
ck = json.load(open(os.path.join(HERE, "data", "checkpointing_3000.json")))
BILL = {r["key"]: next(L["gib"] for L in r["lines"] if L["key"] == "activations") for r in ck["rows"]}   # 64 layers

# ---------------------------------------------------------------- timeline (seconds); the right side is slower
FPS = 30
INTRO, FWD, LOSS, BWD, REC, FREE, OUTRO = 1.5, 2.0, 1.5, 2.4, 2.0, 0.6, 2.5
T_FWD0 = INTRO
T_LOSS0 = T_FWD0 + 2 * FWD
T_BWD0 = T_LOSS0 + LOSS


def steps(side):
    """[(start, end, phase, layer)] for one side, in order."""
    out = [(0, INTRO, "intro", None), (T_FWD0, T_FWD0 + FWD, "forward", 1), (T_FWD0 + FWD, T_LOSS0, "forward", 2),
           (T_LOSS0, T_BWD0, "loss", None)]
    t = T_BWD0
    for layer in (2, 1):
        if side == "right":
            out.append((t, t + REC, "recompute", layer))
            t += REC
        out += [(t, t + BWD, "backward", layer), (t + BWD, t + BWD + FREE, "free", layer)]
        t += BWD + FREE
    out.append((t, t + 99, "done", None))
    return out


T_END = steps("right")[-1][0] + OUTRO
N_FRAMES = int(round(T_END * FPS))


def state(side, tau):
    """Per layer: kept block fraction (0..1), input slab held, transient internals fraction; the active step."""
    blk = {1: 0.0, 2: 0.0}
    inp = {1: False, 2: False}
    transient = {1: 0.0, 2: 0.0}
    active = None
    for (t0, t1, ph, layer) in steps(side):
        if tau < t0:
            break
        f = min(1.0, (tau - t0) / (t1 - t0)) if t1 > t0 else 1.0
        if tau < t1 and ph != "done":
            active = (ph, layer, f)
        if ph == "forward":
            if side == "left":
                blk[layer] = min(1.0, f / 0.7)
            else:
                transient[layer] = min(1.0, f / 0.6) if f < 0.85 else 0.0     # computed, used, then dropped
                inp[layer] = f >= 0.15
        elif ph == "recompute":
            blk[layer] = min(1.0, f / 0.9)
        elif ph == "free":
            blk[layer] = max(0.0, 1.0 - f)
            if side == "right":
                inp[layer] = f < 0.5
    # what is kept for the backward pass: kept or rebuilt internals and saved inputs; the right side's forward
    # internals are computed and dropped at once (shown translucent), so they do not count
    held = sum(blk[l] * KEPT + (INPUT if inp[l] else 0.0) for l in (1, 2))
    return {"blk": blk, "inp": inp, "transient": transient, "active": active, "held": held}


def phase_label(side, st):
    if st["active"] is None:
        return "done" if st is not None else ""
    ph, layer, _ = st["active"]
    return {"intro": "", "forward": f"forward ↑ layer {layer}", "loss": "loss", "recompute": f"recompute layer {layer}",
            "backward": f"backward ↓ layer {layer}", "free": f"free layer {layer}", "done": "done"}[ph]


PEAK = {s: max(state(s, k / FPS)["held"] for k in range(N_FRAMES)) for s in ("left", "right")}

# ---------------------------------------------------------------- scene
BAR_MIB_PER_UNIT = 75.0              # kept internals and input, one shared scale: 1 unit = 75 MiB
GAUGE_MIB_PER_UNIT = 250.0           # the gauge: 1 unit of height = 250 MiB
PLATE_W, PLATE_D, PLATE_T, STEP = 8.0, 6.0, 0.8, 7.0
SIDE_DX = 56.0
ELEVATION, AZIMUTH, LENS = 22.0, -10.0, 80.0
scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
act_m = kit.material("m_acts", kit.COLOURS["activations"], emit=0.12, rough=0.85, spec=0.12)
re_m = kit.material("m_recompute", "#bdb6f5", emit=0.35, rough=0.85, spec=0.12)        # rebuilt: a lighter, lit violet
in_m = kit.material("m_input", "#6357cf", emit=0.30, rough=0.85, spec=0.12)            # an input slab: the darker step
ghost_m = kit.veil_material("m_transient", 0.35, kit.hex_lin(kit.COLOURS["activations"]))   # computed, not kept
plate_m = kit.material("m_plate", "#5b636d", rough=0.7, spec=0.2)
loss_m = kit.material("m_loss", kit.COLOURS["loss"], emit=0.12, rough=0.85, spec=0.12)
gauge_m = kit.material("m_gauge", kit.COLOURS["activations"], emit=0.15, rough=0.8, spec=0.1)
frame_m = kit.material("m_frame", "#4d535c", rough=0.6, spec=0.2)
glow = kit.glow_material("marker", kit.LOOK["limit"], 1.6)
SIDES = {}
for si, side in enumerate(("left", "right")):
    X0 = si * SIDE_DX
    S = {"X0": X0, "plates": {}, "blk": {}, "re": {}, "inp": {}, "tr": {}}
    bx = X0 + PLATE_W + 0.4
    for layer in (1, 2):
        z = (layer - 1) * STEP
        S["plates"][layer] = kit.cuboid(f"{side}_layer{layer}", (X0, -PLATE_D / 2, z), (X0 + PLATE_W, PLATE_D / 2, z + PLATE_T), plate_m)
        L = KEPT / BAR_MIB_PER_UNIT
        for key, m in (("blk", act_m), ("re", re_m), ("tr", ghost_m)):
            ob = kit.cuboid(f"{side}_{key}{layer}", (0, -PLATE_D / 2, 0), (L, PLATE_D / 2, PLATE_T), m)
            ob.location = (bx, 0, z)
            S[key][layer] = ob
        S["inp"][layer] = kit.cuboid(f"{side}_inp{layer}", (bx, -PLATE_D / 2, z), (bx + INPUT / BAR_MIB_PER_UNIT, PLATE_D / 2, z + PLATE_T), in_m)
        kit.no_shadow(S["tr"][layer])
    S["plates"]["loss"] = kit.cuboid(f"{side}_loss", (X0, -PLATE_D / 2, 2 * STEP), (X0 + PLATE_W, PLATE_D / 2, 2 * STEP + PLATE_T), loss_m)
    # gauge: held activations of the two layers, with its full-scale outline (the left's peak)
    gx = bx + KEPT / BAR_MIB_PER_UNIT + 5.0           # the gauge stands at the end of the bars
    S["gauge"] = kit.cuboid(f"{side}_gauge", (gx - 1.2, -1.2, 0), (gx + 1.2, 1.2, 1.0), gauge_m)
    S["gx"] = gx
    top = PEAK["left"] / GAUGE_MIB_PER_UNIT
    for k, (dx, dy) in enumerate(((-1.2, -1.2), (1.2, -1.2), (1.2, 1.2), (-1.2, 1.2))):
        kit.cuboid(f"{side}_gpost{k}", (gx + dx - 0.06, dy - 0.06, 0), (gx + dx + 0.06, dy + 0.06, top), frame_m)
    S["marker"] = []
    for k, (lo_, hi_) in enumerate((((-0.2, -PLATE_D / 2 - 0.2), (PLATE_W + 0.2, -PLATE_D / 2)),
                                     ((-0.2, PLATE_D / 2), (PLATE_W + 0.2, PLATE_D / 2 + 0.2)),
                                     ((-0.2, -PLATE_D / 2), (0.0, PLATE_D / 2)),
                                     ((PLATE_W, -PLATE_D / 2), (PLATE_W + 0.2, PLATE_D / 2)))):
        ob = kit.cuboid(f"{side}_marker{k}", (X0 + lo_[0], lo_[1], -0.12), (X0 + hi_[0], hi_[1], PLATE_T + 0.12), glow)
        kit.no_shadow(ob)
        S["marker"].append(ob)
    objs = list(S["plates"].values()) + list(S["blk"].values()) + [S["gauge"]]
    lo, hi = kit.world_bbox(objs)
    lo.z, lo.x = 0.0, lo.x - 1.0
    S["base"], S["base_info"] = kit.floating_base(lo, hi, margin=2.5 / (hi.x - lo.x), seed=21 + si, dressing=False, drop=6.0, thickness=0.6)
    SIDES[side] = S

# ---------------------------------------------------------------- text (fixed places; bodies change per frame)
EM_A = 0.031 if W_PX <= 640 else 0.022
SUB_A = 0.025 if W_PX <= 640 else 0.017
ink, ink2 = kit.glow_material("ink", kit.LOOK["ink"], 1.0), kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)
T = {}


def text(key, body, size, mat, ax="LEFT", ay="BOTTOM_BASELINE"):
    ob, _, _ = kit.text_object(f"txt_{key}", body, ax, ay)
    T[key] = {"ob": ob, "size": size, "mat": mat}


for side, title in (("left", "without checkpointing"), ("right", "with gradient checkpointing")):
    text(f"title_{side}", title, EM_A, ink2)
    text(f"phase_{side}", "", EM_A, ink)
    text(f"held_{side}", "", SUB_A, ink, "RIGHT")
    for key, label in (("l1", "layer 1"), ("l2", "layer 2"), ("loss", "loss")):
        text(f"{key}_{side}", label, SUB_A, ink2, "RIGHT", "CENTER")
text("inp_note", f"input {INPUT:.0f} MiB", SUB_A * 0.85, ink2, "LEFT", "CENTER")
text("caption", "", SUB_A, ink, "CENTER")
text("note", f"bars to one scale: a layer's internals {KEPT:,.0f} MiB, its input {INPUT:.1f} MiB", SUB_A * 0.8, ink2, "CENTER")

cam = kit.make_camera(scene, LENS)
pts = []
for S in SIDES.values():
    pts += kit.mesh_points(list(S["plates"].values()) + S["base"])
    pts += [S["blk"][l].matrix_world @ Vector(c) for l in (1, 2) for c in S["blk"][l].bound_box]
    pts += [Vector((S["gx"] + dx, dy, z)) for dx in (-1.2, 1.2) for dy in (-1.2, 1.2) for z in (0, PEAK["left"] / GAUGE_MIB_PER_UNIT)]
target, dist = sum(pts, Vector()) / len(pts), 200.0
for _ in range(16):                                   # geometry in the middle of the frame; room above and below for text
    kit.aim(cam, target, dist, direction)
    sp = [kit.to_screen(scene, cam, p) for p in pts]
    x0, x1, y0, y1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
    z = min(0.86 / (x1 - x0), 0.60 / (y1 - y0))
    fw_, fh_ = kit.frame_size(scene, cam, dist)
    Rv = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    Uv = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
    target = target + Rv * ((x0 + x1) / 2 - 0.5) * fw_ + Uv * ((y0 + y1) / 2 - 0.47) * fh_
    if abs(z - 1) < 0.002:
        break
    dist /= z
kit.aim(cam, target, dist, direction)
d_text = kit.to_screen(scene, cam, (SIDE_DX / 2, -PLATE_D - 6, 0)).z
em_y, sub_y = EM_A * rx / ry, SUB_A * rx / ry
sp = [kit.to_screen(scene, cam, p) for p in pts]
top_geo, bot_geo = max(p.y for p in sp), min(p.y for p in sp)
for side, S in SIDES.items():
    px0 = kit.to_screen(scene, cam, (S["X0"], -PLATE_D / 2, 0)).x
    kit.place_on_screen(scene, cam, T[f"title_{side}"]["ob"], px0, top_geo + 2.75 * em_y, d_text, EM_A, ink2)
    kit.place_on_screen(scene, cam, T[f"phase_{side}"]["ob"], px0, top_geo + 1.6 * em_y, d_text, EM_A, ink)
    gt = kit.to_screen(scene, cam, (S["gx"] + 1.2, -1.2, PEAK["left"] / GAUGE_MIB_PER_UNIT))
    kit.place_on_screen(scene, cam, T[f"held_{side}"]["ob"], gt.x + 0.004, gt.y + 0.35 * sub_y, d_text, SUB_A, ink)
    for key, z in (("l1", PLATE_T / 2), ("l2", STEP + PLATE_T / 2), ("loss", 2 * STEP + PLATE_T / 2)):
        p = kit.to_screen(scene, cam, (S["X0"] - 0.3, -PLATE_D / 2, z))
        kit.place_on_screen(scene, cam, T[f"{key}_{side}"]["ob"], p.x, p.y, d_text, SUB_A, ink2)
ip = kit.to_screen(scene, cam, (SIDES["right"]["X0"] + PLATE_W + 0.4, -PLATE_D / 2, STEP + PLATE_T + 1.6))   # just above layer 2's slab
kit.place_on_screen(scene, cam, T["inp_note"]["ob"], ip.x, ip.y, d_text, SUB_A * 0.85, ink2)
kit.place_on_screen(scene, cam, T["caption"]["ob"], 0.5, max(0.075, bot_geo - 1.3 * sub_y), d_text, SUB_A, ink)
kit.place_on_screen(scene, cam, T["note"]["ob"], 0.5, 0.022, d_text, SUB_A * 0.8, ink2)
kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)


def apply(frame):
    tau = frame / FPS
    sts = {}
    for side, S in SIDES.items():
        st = state(side, tau)
        sts[side] = st
        for layer in (1, 2):
            f = st["blk"][layer]
            keep_ob = S["blk"][layer] if side == "left" else S["re"][layer]
            other = S["re"][layer] if side == "left" else S["blk"][layer]
            other.hide_render = True
            keep_ob.hide_render = f <= 1e-3
            keep_ob.scale.x = max(f, 1e-3)
            tr = st["transient"][layer]
            S["tr"][layer].hide_render = tr <= 1e-3
            S["tr"][layer].scale.x = max(tr, 1e-3)
            S["inp"][layer].hide_render = not (side == "right" and st["inp"][layer])
        act = st["active"]
        on = act is not None and act[0] in ("forward", "recompute", "backward", "free", "loss")
        for ob in S["marker"]:
            ob.hide_render = not on
            if on:
                ob.location.z = 2 * STEP if act[0] == "loss" else (act[1] - 1) * STEP
        h = st["held"]
        S["gauge"].hide_render = h <= 1e-3
        S["gauge"].scale.z = max(h / GAUGE_MIB_PER_UNIT, 1e-4)
        T[f"held_{side}"]["ob"].data.body = f"kept for the backward pass: {h:,.0f} MiB"
        T[f"phase_{side}"]["ob"].data.body = phase_label(side, st) if act is not None else "done"
    T["inp_note"]["ob"].hide_render = not sts["right"]["inp"][2] or sts["right"]["blk"][2] > 1e-3   # not over the rebuilt bar
    T["caption"]["ob"].data.body = caption(frame / FPS, sts)
    bpy.context.view_layer.update()
    return sts


def caption(tau, sts):
    L, R = sts["left"]["active"], sts["right"]["active"]
    lp, rp = (L[0] if L else "done"), (R[0] if R else "done")
    n = (R or L or (None, None))[1]
    if lp == "intro":
        return "One training step: two layers, then the loss."
    if lp == rp == "forward":
        return f"Forward ↑ layer {n}: left keeps its internals, right only its input."
    if lp == rp == "loss":
        return f"Loss. Kept for backward: left {sts['left']['held']:,.0f} MiB, right {sts['right']['held']:,.0f} MiB."
    if rp == "recompute":
        return f"Right recomputes layer {n}'s internals from its input."
    if rp == "backward":
        return f"Backprop through layer {n}: adapter gradients, then onward." if n == 2 else \
            "Backprop through layer 1: its adapter's gradients."
    if rp == "free" or lp == "free":
        return "Each layer's internals are freed once its backward is done."
    if lp == rp == "done":
        return f"Peak {PEAK['left']:,.0f} vs {PEAK['right']:,.0f} MiB here; 64 layers: {BILL['qlora']:.0f} vs {BILL['ckpt']:.1f} GiB."
    return f"{tau:.1f} s"


# ---------------------------------------------------------------- frames
if args.frames == "storyboard":
    secs = [1.0, 2.8, 6.3, 8.4, 10.6, 12.2, 15.0, T_END - 0.6]   # intro, fwd, loss, recompute, bwd, recompute, bwd, end
    frames = [int(round(s * FPS)) for s in secs]
elif args.frames == "all":
    frames = list(range(N_FRAMES))
else:
    frames = [int(f) for f in args.frames.split(",")]
os.makedirs(args.outdir, exist_ok=True)
log, t_all = [], time.time()
for f in frames:
    sts = apply(f)
    scene.render.filepath = os.path.join(args.outdir, f"frame_{f:04d}.png")
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    log.append({"frame": f, "time_s": round(f / FPS, 2), "left": phase_label("left", sts["left"]) if sts["left"]["active"] else "done",
                "right": phase_label("right", sts["right"]) if sts["right"]["active"] else "done",
                "held_mib": [round(sts["left"]["held"], 1), round(sts["right"]["held"], 1)],
                "caption": T["caption"]["ob"].data.body, "seconds": round(time.time() - t0, 2)})
    print("FRAME", json.dumps(log[-1]))
info = {"fps": FPS, "length_s": round(T_END, 2), "frames_total": N_FRAMES, "size": [W_PX, H_PX], "samples": args.samples,
        "scales": {"bar_mib_per_unit": BAR_MIB_PER_UNIT, "gauge_mib_per_unit": GAUGE_MIB_PER_UNIT,
                   "bar_units": {"internals": round(KEPT / BAR_MIB_PER_UNIT, 3), "input": round(INPUT / BAR_MIB_PER_UNIT, 4)}},
        "timeline": {side: steps(side)[:-1] for side in ("left", "right")},
        "peaks_mib": PEAK, "bill_64_layers_gib": BILL, "rendered": log, "wall_seconds": round(time.time() - t_all, 1)}
kit.write_json(os.path.join(args.outdir, "frames.json"), info)

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
