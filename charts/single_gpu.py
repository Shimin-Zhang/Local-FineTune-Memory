"""Figure: the one-card bill. The next panel after fig 5 (charts/checkpointing.py), in its layout: left the stack fig 5
ended on (QLoRA + gradient checkpointing, 2 cards), right the same with the chunked loss and the fast kernels: one card,
with its empty headroom as smoked glass (the VRAM figure's free space), and run 3's measured peak as a thin line.
1 unit = 1 GiB of height on the 10 x 10 footprint; card boxes of 24 GiB; sign boards lit by a shadowless twin of the key.
Data: charts/data/single_gpu_3000.json (every number on the figure comes from it).

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/single_gpu.py -- \
    [--size 2400x1600] [--samples 64] [--out charts/out/single_gpu.png] [--no-render]
"""
import argparse, json, math, os, sys, time
import bpy
from mathutils import Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="2400x1600")
ap.add_argument("--samples", type=int, default=256)              # as fig 5's final
ap.add_argument("--out", default=os.path.join(HERE, "out", "single_gpu.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "single_gpu.layout.json"))
ap.add_argument("--no-render", action="store_true")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
rx, ry = W_PX, H_PX
GIB = kit.MIB_PER_GIB * kit.UNITS_PER_MIB


def half_up(x, nd=0):
    f = 10 ** nd
    return math.floor(x * f + 0.5) / f


def gib(v):
    """A memory amount as on the bills: one decimal, two below 1 GiB."""
    return f"{half_up(v, 1):.1f}" if v >= 0.995 else f"{half_up(v, 2):.2f}"


data = json.load(open(os.path.join(HERE, "data", "single_gpu_3000.json")))
card_gib = data["card_total_gib"]
box_h = card_gib * GIB
MEAS = data["measured"]
SIDES = [{"row": data["rows"][0], "title": "QLoRA + gradient checkpointing"},
         {"row": data["rows"][1], "title": "+ chunked loss + fast kernels"}]
SHORT = {"activations": "activations, fast kernels", "loss": "loss, chunked"}   # the right side: the trick's name
WHOLE = {L["key"]: L for L in data["whole_card_right"]["lines_bottom_to_top"]}   # driver, training, runtime, free
for S, sign in zip(SIDES, (data["signs"]["left"], data["signs"]["right"])):
    R = S["row"]
    S["id"], S["n"] = R["key"], math.ceil(R["total_gib"] / card_gib)
    S["sign"] = [f"{S['n']} × RTX 4090", sign]
    S["lines"] = {L["key"]: L for L in R["lines"]}
    if S["n"] == 1:                                   # the one card as fig 1 fills it: the driver under, runtime over
        S["lines"]["driver"] = WHOLE["driver"]
        S["lines"]["runtime"] = WHOLE["runtime"]
    S["floor"] = S["lines"]["driver"]["gib"] * GIB if "driver" in S["lines"] else 0.0   # where the bill starts
    S["top"] = sum(L["gib"] for L in S["lines"].values()) * GIB    # the stack's top (all cards together)
    S["text"] = {}
    for k, L in S["lines"].items():
        if "was_gib" in L:                                         # what shrank: the trick, before -> after
            S["text"][k] = f"{SHORT[k]} {gib(L['was_gib'])} → {gib(L['gib'])} GiB"
        else:
            S["text"][k] = f"{L['label']} {gib(L['gib'])} GiB"
    S["labelled"] = ([k for k in ("weights", "adapter", "activations", "loss")] if S["n"] > 1 else
                     [k for k in S["lines"] if "was_gib" in S["lines"][k] or k in ("driver", "runtime")])
L_, R_ = SIDES
assert [S["n"] for S in SIDES] == [2, 1] and [S["sign"][1] for S in SIDES] == ["≈ 32 GiB", "≈ 22 GiB"]
FREE = card_gib - R_["top"] / GIB
assert abs(FREE - WHOLE["free"]["gib"]) < 0.01 and abs(sum(L["gib"] for L in R_["row"]["lines"]) - WHOLE["training"]["gib"]) < 0.01
HEAD_TEXT = f"free ≈ {gib(WHOLE['free']['gib'])} GiB"                 # fig 1's word; ≈: 1.43 computed, 1.52 with run 3's peak
MEAS_TEXT = f"{MEAS['label']}: {gib(MEAS['peak_gib'])} GiB"

PITCH = kit.FOOTPRINT[0] + 3.0
BASE_GAP = 4.0                       # between the two floating bases (fig 5 kept 150 units between origins, for 7 cards)
SIGN_CLEAR = {1: 7.0}                # room between a lone card and its sign: the headroom bracket and a leader run there
ELEVATION, AZIMUTH, LENS = 22.0, -14.0, 80.0          # fig 5: 28; lower, so the one card's headroom is seen from the side
BRACKET = (2.2, 2.9)                 # the free space's dimension bracket: ticks from / vertical at, out of the front-right edge
SIGN_EM, SIGN_EM2 = 7.4, 5.6
SIGN_POST = 1.0                      # fig 5: 3.0; lower here, so the headroom's label fits beside its bracket above the sign
C = {k: kit.COLOURS[k] for k in ("weights", "gradients", "optimizer", "activations", "loss", "frozen")}
direction = kit.view_direction(ELEVATION, AZIMUTH)
a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
RIGHT = Vector((-direction.y, direction.x, 0)).normalized()

scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
mats = {k: kit.material(f"m_{k}", v, emit=0.10, rough=0.85, spec=0.12) for k, v in C.items()}
mats["driver"] = kit.material("m_driver", kit.COLOURS["driver"], emit=0.10, rough=0.85, spec=0.12)      # as fig 1
mats["working"] = kit.material("m_working", kit.COLOURS["working"], emit=0.12, rough=0.85, spec=0.12)
ghost = kit.material("ghost", "#4d535c", rough=0.6, spec=0.2)
ink_sign = kit.glow_material("sign_ink", kit.LOOK["ink"], 1.0)

SIDE_GAP = 0.0
for si, S in enumerate(SIDES):
    if si == 1:                                       # the right diorama just clear of the left one's base
        left_reach = max(p.dot(RIGHT) for p in kit.mesh_points(SIDES[0]["objs"] + SIDES[0]["base"]))
        SIDE_GAP = left_reach + BASE_GAP + 3.0 * RIGHT.x + (b + 3.0) * abs(RIGHT.y) + 1.0
    X0, Y0 = si * SIDE_GAP * RIGHT.x, si * SIDE_GAP * RIGHT.y
    S["X0"], S["Y0"] = X0, Y0
    Ls = S["lines"]
    ad = Ls["adapter"]["gib"]
    pour = [("weights", "frozen", Ls["weights"]["gib"]), ("adapter_w", "weights", ad / 4), ("adapter_g", "gradients", ad / 4),
            ("adapter_o", "optimizer", ad / 2), ("activations", "activations", Ls["activations"]["gib"]), ("loss", "loss", Ls["loss"]["gib"])]
    if "driver" in Ls:
        pour = [("driver", "driver", Ls["driver"]["gib"])] + pour + [("runtime", "working", Ls["runtime"]["gib"])]
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
    top_in_last = S["top"] - (S["n"] - 1) * box_h
    empty_top = S["n"] == 1 and top_in_last < box_h - 1e-6
    # the one card's back walls stop at the stack: above it the card is empty, open to the night behind it
    for w in kit.back_walls(top_in_last if empty_top else box_h, direction, centre=S["centres"][0]):
        w.name = f"{S['id']}_{w.name}"
        S["objs"].append(w)
    if empty_top:                                     # the headroom: nearly clear, a faint sheet so it reads as card
        S["glass"] = kit.glass_headroom(top_in_last, box_h, centre=S["centres"][0], mat=kit.veil_material("headroom_veil", 0.035))
        for ob in S["glass"]:
            kit.no_shadow(ob)
        S["objs"] += S["glass"]
    t1, w1, _ = kit.text_object(f"{S['id']}_sign_text", S["sign"][0], "CENTER", "CENTER")
    t2, w2, _ = kit.text_object(f"{S['id']}_sign_text2", S["sign"][1], "CENTER", "CENTER")
    bw = max(w1 * SIGN_EM, w2 * SIGN_EM2) + 3.2
    bh = 0.75 * SIGN_EM + 0.75 * SIGN_EM2 + 0.45 * SIGN_EM + 2.4
    sx = X0 + (S["n"] - 1) * PITCH + 2 * a + SIGN_CLEAR.get(S["n"], 3.0) + bw / 2
    centre = Vector((sx, Y0 - 1.0, SIGN_POST + bh / 2))
    S["sign_box"] = (centre, bw, bh)
    bm = kit.material(f"{S['id']}_sign_board", "#323843", rough=0.75)
    fr = kit.material(f"{S['id']}_sign_frame", "#5b636d", rough=0.5, spec=0.4)
    e = 0.32
    parts = [kit.cuboid(f"{S['id']}_sign_board", (-bw / 2, -0.25, -bh / 2), (bw / 2, 0.25, bh / 2), bm),
             kit.cuboid(f"{S['id']}_sign_ft", (-bw / 2, -0.33, bh / 2 - e), (bw / 2, -0.25, bh / 2), fr),
             kit.cuboid(f"{S['id']}_sign_fb", (-bw / 2, -0.33, -bh / 2), (bw / 2, -0.25, -bh / 2 + e), fr),
             kit.cuboid(f"{S['id']}_sign_fl", (-bw / 2, -0.33, -bh / 2 + e), (-bw / 2 + e, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{S['id']}_sign_fr", (bw / 2 - e, -0.33, -bh / 2 + e), (bw / 2, -0.25, bh / 2 - e), fr),
             kit.cuboid(f"{S['id']}_sign_post", (-0.45, -0.2, -bh / 2 - SIGN_POST), (0.45, 0.2, -bh / 2), fr)]
    rot = Euler((0, 0, math.radians(AZIMUTH)))
    for p in parts:
        p.location, p.rotation_euler = centre, rot
    gap_l = 0.45 * SIGN_EM
    for t, em, dz in ((t1, SIGN_EM, (0.75 * SIGN_EM2 + gap_l) / 2), (t2, SIGN_EM2, -(0.75 * SIGN_EM + gap_l) / 2)):
        t.data.size, t.data.extrude = em, 0.1
        off = Vector((0, -0.35, dz))
        off.rotate(rot)
        t.location = centre + off
        t.rotation_euler = (math.radians(90), 0, math.radians(AZIMUTH))
        t.data.materials.append(ink_sign)
    S["sign_objs"] = parts
    S["sign_texts"] = [t1, t2]
    S["objs"] += parts
    lo, hi = kit.world_bbox(S["objs"])
    lo.z = 0.0
    S["base"], S["base_info"] = kit.floating_base(lo, hi, margin=3.0 / (hi.x - lo.x), seed=11 + 7 * si, dressing=False, drop=12.0, thickness=0.8)

# ---------------------------------------------------------------- labels
# Each side's own lines under its row, as in fig 5. The right card labels only what changed (the trick, before -> after),
# the loss leader leaves its right edge, the activations leader its back-left edge; run 3's measured peak is a tick
# out of its back-left edge, labelled on its left; the headroom has a bracket on its right, labelled beside it.
labels, kinds = [], {}
for S in SIDES:
    segs, sid = S["segs"], S["id"]
    w0 = next(s for s in segs if s["key"] == "weights")
    adl = [s for s in segs if s["key"].startswith("adapter")]
    acts = [s for s in segs if s["key"] == "activations"]
    loss = [s for s in segs if s["key"] == "loss"]
    stagger = S["n"] == 1

    def add(key, s, z, mode):
        if key not in S["labelled"]:
            return
        cx, cy = S["centres"][s["box"]]
        if mode == "side" and stagger:                # the one card: loss and runtime out of its right side, activations
            mode = {"loss": "sside", "runtime": "rface"}.get(key, "lback")   # out of its back-left edge
        anchor = {"sside": (cx + a, cy - b, z), "rface": (cx + a - 2.8, cy - b, z), "lback": (cx - a, cy + b, z)}.get(mode, (cx, cy - b, z))
        labels.append(kit.Label(f"{sid}_{key}", S["text"][key], anchor, "R"))
        kinds[f"{sid}_{key}"] = (S, mode, s)

    add("weights", w0, (w0["z0"] + w0["z1"]) / 2, "ground")
    add("adapter", adl[0], (adl[0]["z0"] + adl[-1]["z1"]) / 2, "side")
    ga = [s for s in acts if s["z0"] < 1e-6]
    sa = (ga[0] if ga else acts[0])
    add("activations", sa, (sa["z0"] + sa["z1"]) / 2, "ground" if ga else "side")
    gl = [s for s in loss if s["z0"] < 1e-6]
    sl = gl[-1] if gl else loss[-1]
    add("loss", sl, (sl["z0"] + sl["z1"]) / 2, "ground" if gl else "side")
    for key in ("driver", "runtime"):
        sg = next((s for s in segs if s["key"] == key), None)
        if sg:
            add(key, sg, (sg["z0"] + sg["z1"]) / 2, "ground" if sg["z0"] < 1e-6 else "side")
cxR, cyR = R_["centres"][0]
Z_MEAS = R_["floor"] + MEAS["peak_gib"] * GIB         # from the card's floor, as the stack: on top of the driver's share
Z_HEAD = (R_["top"] + box_h) / 2
TICK = 1.6                                            # run 3's measured peak: a tick out of the card's back-left edge
labels.append(kit.Label("one_card_meas", MEAS_TEXT, (cxR - a - TICK, cyR + b, Z_MEAS), "L"))
kinds["one_card_meas"] = (R_, "left", None)
labels.append(kit.Label("one_card_head", HEAD_TEXT, (cxR + a + BRACKET[1], cyR - b, Z_HEAD), "R"))
kinds["one_card_head"] = (R_, "right", None)
titles = []
for S in SIDES:
    t, w, _ = kit.text_object(f"txt_title_{S['id']}", S["title"], "LEFT", "BOTTOM_BASELINE")
    titles.append({"side": S, "obj": t, "w": w})


def place(cam):
    em_y = kit.EM * rx / ry
    lay = {}
    for lab in labels:
        p = kit.to_screen(scene, cam, lab.anchor)
        lay[lab.key] = {"ax": p.x, "ay": p.y, "depth": p.z, "w": lab.w_em * kit.EM, "h": em_y, "below": 0.0}
    for S in SIDES:
        near_depth = kit.to_screen(scene, cam, (S["X0"], S["base_info"]["y"][0], 0.0)).z - 2.0
        mine = []
        for lab in labels:
            S_, mode, s = kinds[lab.key]
            if S_ is not S or mode in ("left", "right"):
                continue
            o = lay[lab.key]
            cx, cy = S["centres"][s["box"]]
            if mode == "side":
                o["lx"] = kit.to_screen(scene, cam, (cx + a + 1.5, cy - b, lab.anchor.z)).x
            elif mode == "sside":                     # short stubs, inside the bracket: loss nearer, runtime (higher) further
                o["lx"] = kit.to_screen(scene, cam, (cx + a + 0.7, cy - b, lab.anchor.z)).x
            elif mode == "rface":
                o["lx"] = kit.to_screen(scene, cam, (cx + a + 1.5, cy - b, lab.anchor.z)).x
            elif mode == "lback":
                o["lx"] = kit.to_screen(scene, cam, (cx - a - 1.3, cy + b, lab.anchor.z)).x
            else:
                o["lx"] = o["ax"]
            o["edge"] = kit.to_screen(scene, cam, (cx, S["base_info"]["y"][0], S["base_info"]["top"] - S["base_info"]["thickness"])).y
            o["depth"] = min(near_depth, o["depth"] - 1.5)  # in front of the card where the anchor sits on its face
            mine.append((lab, mode))
        mine.sort(key=lambda t: -lay[t[0].key]["lx"])            # the rightmost leader highest, each further left lower
        y_prev = None
        for lab, mode in mine:
            o = lay[lab.key]
            y = o["edge"] - 1.5 * em_y if y_prev is None else min(o["edge"] - 1.5 * em_y, y_prev - 1.75 * em_y)
            o["route"] = ([(o["ax"], o["ay"]), (o["lx"], o["ay"]), (o["lx"], y + 0.3 * em_y)] if mode in ("side", "sside", "rface", "lback")
                          else [(o["ax"], o["ay"]), (o["ax"], y + 0.3 * em_y)])
            o["y"], o["x"] = y, o["lx"] + 0.45 * kit.EM
            o["x0"], o["x1"] = o["x"], o["x"] + o["w"]
            y_prev = y
    # run 3's measured peak: to the card's left (right-aligned), kept above the left sign; the headroom: beside its
    # bracket on the card's right, kept above the right sign
    near_depth = kit.to_screen(scene, cam, (R_["X0"], R_["base_info"]["y"][0], 0.0)).z - 2.0

    def sign_rect(S):
        centre, bw, bh = S["sign_box"]
        sp_ = [kit.to_screen(scene, cam, centre + Vector((dx, 0, dz))) for dx in (-bw / 2, bw / 2) for dz in (-bh / 2, bh / 2)]
        return min(p.x for p in sp_), max(p.x for p in sp_), max(p.y for p in sp_)
    om, oh = lay["one_card_meas"], lay["one_card_head"]
    lx0, lx1, ltop = sign_rect(L_)
    col = om["ax"] - 2.2 * kit.EM                                # its right edge
    ym = max(om["ay"], ltop + 1.0 * em_y) if (col - om["w"] < lx1 and col > lx0) else om["ay"]
    stub, end = 0.8 * kit.EM, col + 0.45 * kit.EM
    p1 = (om["ax"] - stub, om["ay"])
    p2x = p1[0] - min(abs(ym - om["ay"]) * ry / rx, (p1[0] - end) * 0.8)
    om["route"] = [(om["ax"], om["ay"]), p1, (p2x, ym), (end, ym)] if abs(ym - om["ay"]) > 0.002 else [(om["ax"], om["ay"]), (end, om["ay"])]
    om["x"], om["y"], om["depth"], om["x0"], om["x1"] = col, ym, near_depth, col - om["w"], col
    rx0, rx1, rtop = sign_rect(R_)
    xh = oh["ax"] + 0.6 * kit.EM                                 # its left edge, close beside the bracket
    yh = max(oh["ay"], rtop + 0.55 * em_y) if (xh < rx1 and xh + oh["w"] > rx0) else oh["ay"]   # its baseline clear of the sign
    oh["beside"] = abs(yh - oh["ay"]) < 0.4 * em_y              # still beside its bracket: a dimension, no leader
    oh["route"] = [(oh["ax"], oh["ay"]), (xh - 0.35 * kit.EM, oh["ay"])] if oh["beside"] else \
        [(oh["ax"], oh["ay"]), (oh["ax"] + 0.3 * kit.EM, oh["ay"]), (oh["ax"] + 0.3 * kit.EM, yh), (xh - 0.35 * kit.EM, yh)]
    oh["x"], oh["y"], oh["depth"], oh["x0"], oh["x1"] = xh, yh, near_depth, xh, xh + oh["w"]
    for o in lay.values():
        o["sub_y"] = o["y"] - o["h"] / 2 - kit.SUB_GAP * em_y
    tl = []
    geo_top = max(kit.to_screen(scene, cam, (cx + dx, cy + dy, box_h)).y for S in SIDES for cx, cy in S["centres"] for dx in (-a, a) for dy in (-b, b))
    for t in titles:
        S = t["side"]
        gx = min(kit.to_screen(scene, cam, (cx - a, cy - b, 0)).x for cx, cy in S["centres"])
        y = geo_top + 1.4 * em_y
        w = t["w"] * kit.EM
        for o in (oh, om):                            # above the right card's labels if they share a column
            if gx < o["x1"] and o["x0"] < gx + w:
                y = max(y, o["y"] + 1.6 * em_y)
        tl.append({"t": t, "x": gx, "y": y, "rect": [gx, gx + w, y - 0.25 * em_y, y + 0.74 * em_y]})
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
# run 3's measured peak: a thin bright tick at its height, out of the card's back-left edge (not across the faces,
# where it would cover the 0.45 GiB loss slab it sits in)
mline = kit.glow_material("measured_line", kit.LOOK["ink"], 1.0)
t_ = kit.LINE * fw * 1.4 / 2
s0 = kit.STRUT * fw / 2
ob = kit.cuboid("measured_tick", (cxR - a - TICK, cyR + b - t_, Z_MEAS - t_), (cxR - a - s0, cyR + b + t_, Z_MEAS + t_), mline)
kit.no_shadow(ob)
meas_objs = [ob]
# the empty headroom: the card's four edges drawn bright from the stack's top up to the rim
rimm = kit.glow_material("headroom_edges", kit.LOOK["limit"], kit.RIM_GLOW * 2.0)
r_ = kit.STRUT * fw * 0.62                            # a little wider than the struts, so the faces don't coincide
for i, p in enumerate(kit.box_corners(centre=(cxR, cyR))):
    kit.no_shadow(kit.cuboid(f"headroom_edge_{i}", (p.x - r_, p.y - r_, R_["top"]), (p.x + r_, p.y + r_, box_h), rimm))
# ... and its height as a dimension bracket beside the card's front-right edge, labelled to its right
br = kit.glow_material("bracket", kit.LOOK["leader"], 1.0)
bx_in, bx_out, by = cxR + a + BRACKET[0], cxR + a + BRACKET[1], cyR - b
for nm, l_, h_ in (("v", (bx_out - t_, by - t_, R_["top"]), (bx_out + t_, by + t_, box_h)),
                   ("lo", (bx_in, by - t_, R_["top"] - t_), (bx_out + t_, by + t_, R_["top"] + t_)),
                   ("hi", (bx_in, by - t_, box_h - t_), (bx_out + t_, by + t_, box_h + t_))):
    kit.no_shadow(kit.cuboid(f"headroom_bracket_{nm}", l_, h_, br))
bpy.context.view_layer.update()
kit.build_labels(scene, cam, labels, lay, lift=0.0)
if lay["one_card_head"]["beside"]:                    # beside its bracket: a dimension, no leader
    for nm in ("leader_one_card_head", "dot_one_card_head"):
        bpy.data.objects.remove(bpy.data.objects[nm], do_unlink=True)
ink = kit.glow_material("ink_t", kit.LOOK["ink"], 1.0)
d_text = kit.to_screen(scene, cam, (SIDES[0]["X0"], SIDES[0]["base_info"]["y"][0], 0)).z - 2.0
for t in tl:
    kit.place_on_screen(scene, cam, t["t"]["obj"], t["x"], t["y"], d_text, kit.EM, ink)
key_ob, rim_ob = kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)   # as fig 5
# fig 5: light linking; the key lights everything but the two signs, a shadowless twin of the key lights only the signs
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
try:
    twin.use_shadow = False
except AttributeError:
    pass
try:
    twin.cycles.cast_shadow = False
except AttributeError:
    pass
sign_key = bpy.data.objects.new("sign_key", twin)
scene.collection.objects.link(sign_key)
sign_key.rotation_euler = key_ob.rotation_euler.copy()
sign_key.light_linking.receiver_collection = by_twin
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
    for nm, obs in (("row", [s["obj"] for s in S["segs"]] + S.get("glass", [])), ("sign", S["sign_objs"])):
        sp = [kit.to_screen(scene, cam, p) for p in kit.mesh_points(obs)]
        geo_rects[f"{S['id']}_{nm}"] = [min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)]
text_on_geo = [[n, g] for n, r in rr.items() for g, q in geo_rects.items() if r[0] < q[1] and q[0] < r[1] and r[2] < q[3] and q[2] < r[3]]
sides_out = []
for S in SIDES:
    lines_out = {}
    for key in [k for k in ("driver", "weights", "adapter", "activations", "loss", "runtime") if k in S["lines"]]:
        h = sum(kit.object_height(s["obj"]) for s in S["segs"] if s["key"] == key or (key == "adapter" and s["key"].startswith("adapter")))
        lines_out[key] = {"gib": S["lines"][key]["gib"], "height_units": round(h, 6), "units_per_gib": h / S["lines"][key]["gib"]}
    sides_out.append({"side": S["id"], "cards": S["n"], "sign": S["sign"], "total_gib_data": S["row"]["total_gib"],
                      "stack_top_units": round(S["top"], 4), "lines": lines_out, "labels": [S["text"][k] for k in S["labelled"]]})
gl = R_["glass"][0]
glo, ghi = kit.world_bbox([gl])
mlo, mhi = kit.world_bbox(meas_objs)
layout = {
    "figure": "single_gpu", "scales": {"bills_units_per_gib": GIB},
    "sides": sides_out,
    "headroom": {"glass_z": [round(glo.z, 4), round(ghi.z, 4)], "gib": round((ghi.z - glo.z) / GIB, 4), "label": HEAD_TEXT},
    "measured_line": {"z_centre": round((mlo.z + mhi.z) / 2, 4), "gib": MEAS["peak_gib"], "label": MEAS_TEXT,
                      "below_loss_top_units": round(R_["top"] - R_["lines"]["runtime"]["gib"] * GIB - (mlo.z + mhi.z) / 2, 4)},
    "max_deviation_units_per_gib": max(abs(v["units_per_gib"] - 1.0) for s in sides_out for v in s["lines"].values()),
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS, "distance": round(dist, 2)},
    "text_rects": {k: [round(v, 4) for v in r] for k, r in rr.items()},
    "text_overlaps": overlaps, "leaders_crossing_text": sorted(leader_cross), "text_hidden": sorted(hidden),
    "text_inside_picture": inside, "text_on_geometry": text_on_geo,
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_gib", "headroom", "measured_line", "text_overlaps",
                                                 "leaders_crossing_text", "text_hidden", "text_inside_picture", "text_on_geometry")}))
print("SIDES", [(s["side"], s["cards"], s["stack_top_units"], s["labels"]) for s in sides_out])

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    layout["render"] = {"png": args.out, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1)}
    kit.write_json(args.layout, layout)
    print("RENDER", round(secs, 1), "s")
