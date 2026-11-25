"""Figure: the naive bill for fully fine-tuning Qwen3.8-27B in BF16, against the 24 GiB card.

Variant a: the five lines stacked as one tower on the card's footprint, rising out of the card's box, to scale
(kit.UNITS_PER_MIB: 1 unit of height = 1 GiB). Variant b: the same bill poured, in order, into a row of 24 GiB card
boxes (ours solid, the rest ghosted). Numbers: charts/data/train_bill_bf16_3000.json, used as given.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/train_bill.py -- \
    [--variant a|b] [--size 900x600] [--samples 32] [--out ...] [--layout ...] [--no-render]
"""
import argparse, json, math, os, re, sys, time
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--variant", default="a", choices=["a", "b"])
ap.add_argument("--size", default="900x600")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=None)
ap.add_argument("--layout", default=None)
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--footnote", action="store_true", help="draw the 'calculated, not measured' footnote (drafts a and b)")
ap.add_argument("--no-sign", action="store_true", help="variant b without the '14 x RTX 4090' plaque (draft b)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W_PX, H_PX = (int(v) for v in args.size.split("x"))
out_png = args.out or os.path.join(HERE, "out", f"train_bill_draft_{args.variant}.png")
out_layout = args.layout or os.path.join(HERE, "out", f"train_bill_{args.variant}.layout.json")

data = json.load(open(os.path.join(HERE, "data", "train_bill_bf16_3000.json")))
lines = data["lines_bottom_to_top"]
card_gib = data["card_total_gib"]
GIB = kit.MIB_PER_GIB * kit.UNITS_PER_MIB          # units per GiB: 1.0


def label_parts(L):
    """Main text and optional dimmer second line, from the data's label."""
    m = re.match(r"(.*) \((AdamW.*)\)$", L["label"])
    name, sub = (m.group(1), [m.group(2)]) if m else (L["label"], None)
    value = f"≈ {round(L['gib']):.0f} GiB" if L.get("approximate") else f"{L['gib']:.1f} GiB"
    return f"{name} {value}", sub


TOTAL_TEXT = f"≈ {round(data['total_gib']):.0f} GiB, {round(data['times_the_card']):.0f}× the card"
LIMIT_TEXT = "RTX 4090: 24 GiB"
FOOT_TEXT = data["status"].split(":")[0]           # "calculated, not measured"
EXPECT = {"weights": "Qwen3.8-27B weights (BF16) 50.1 GiB", "gradients": "gradients 50.1 GiB",
          "optimizer": "optimizer state 100.2 GiB", "activations": "activations, 3,000 tokens ≈ 111 GiB",
          "loss": "loss, 3,000 tokens 9.4 GiB"}
for L in lines:
    assert label_parts(L)[0] == EXPECT[L["key"]], label_parts(L)
assert TOTAL_TEXT == "≈ 321 GiB, 13× the card" and FOOT_TEXT == "calculated, not measured"

ELEVATION, AZIMUTH, LENS = 26.0, 38.0, 80.0          # the VRAM figure's camera
scene = kit.reset()
kit.render_settings(scene, W_PX, H_PX, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)
mats = {L["key"]: kit.material(L["key"], kit.COLOURS[L["key"]], emit=0.10, rough=0.85, spec=0.12) for L in lines}
box_h = card_gib * GIB
ink2 = kit.glow_material("ink2", kit.LOOK["ink2"], 1.0)

if args.variant == "a":
    # ---- one tower on the card's footprint, starting inside the box
    stack = kit.stack_layers([{"key": L["key"], "mib": L["gib"] * kit.MIB_PER_GIB} for L in lines], mats)
    walls = kit.back_walls(box_h, direction)
    lo, hi = kit.world_bbox(walls)
    base, base_info = kit.floating_base(lo, hi)        # the card's own board, as in the VRAM figure
    volumes = [s["obj"] for s in stack] + walls
    left_c, near_c, right_c = kit.silhouette_corners(direction)
    labels = []
    for L, s in zip(lines, stack):
        text, sub = label_parts(L)
        labels.append(kit.Label(L["key"], text, (right_c.x, right_c.y, (s["z0"] + s["z1"]) / 2), "R", sub=sub))
    labels.append(kit.Label("limit", LIMIT_TEXT, (left_c.x, left_c.y, box_h), "L"))
    labels.append(kit.Label("total", TOTAL_TEXT, (left_c.x, left_c.y, stack[-1]["z1"]), "L"))
    cam = kit.make_camera(scene, LENS)
    lay = kit.frame_scene(scene, cam, volumes + base, direction, labels)
    d_box = kit.to_screen(scene, cam, (0, 0, box_h / 2)).z
    fw, _ = kit.frame_size(scene, cam, d_box)
    frame = kit.box_frame(box_h, kit.STRUT * fw, kit.RIM * fw)        # no lid: the bill comes out of the top
    kit.build_labels(scene, cam, labels, lay, lift=kit.RIM * fw)
    built = {L["key"]: s for L, s in zip(lines, stack)}
else:
    # ---- the bill poured, in order, into a row of card boxes: ours first (solid), the rest ghosted
    direction = kit.view_direction(ELEVATION, -AZIMUTH)          # mirrored, so box 1 (ours) is nearest and the row reads left to right
    GAP_B = 3.0
    n_boxes = math.ceil(sum(L["gib"] for L in lines) / card_gib - 1e-9)
    pitch = kit.FOOTPRINT[0] + GAP_B
    centres = [(k * pitch + kit.FOOTPRINT[0] / 2, 0.0) for k in range(n_boxes)]
    segs, c = [], 0.0                                          # (key, box, z0, z1) in the box's own height
    for L in lines:
        c0, c1 = c, c + L["gib"] * GIB
        for k in range(n_boxes):
            a0, a1 = max(c0, k * box_h), min(c1, (k + 1) * box_h)
            if a1 > a0 + 1e-9:
                segs.append((L["key"], k, a0 - k * box_h, a1 - k * box_h))
        c = c1
    seg_objs = {}
    a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
    for key, k, z0, z1 in segs:
        cx, cy = centres[k]
        ob = kit.cuboid(f"seg_{key}_{k}", (cx - a, cy - b, z0), (cx + a, cy + b, z1), mats[key])
        seg_objs.setdefault(key, []).append((k, z0, z1, ob))
    walls = kit.back_walls(box_h, direction, centre=centres[0])
    volumes = [o for v in seg_objs.values() for (_, _, _, o) in v] + walls
    lo, hi = kit.world_bbox(volumes)
    row_len = hi.x - lo.x
    base, base_info = kit.floating_base(lo, hi, margin=3.0 / row_len, dressing=False, drop=20.0, thickness=0.8)

    # a plaque on the base's front edge under the last boxes: how many cards the picture shows
    sign_objs, SIGN = [], None
    if not args.no_sign:
        n_cards = math.ceil(data["total_gib"] / card_gib)
        assert n_cards == n_boxes, (n_cards, n_boxes)
        SIGN = f"{n_cards} × RTX 4090"
        EM_SIGN, PAD_X, PAD_Y, BT, LIP = 4.2, 1.7, 1.25, 0.45, 0.35     # world units: the sign belongs to the scene
        txt, tw, th = kit.text_object("sign_text", SIGN, "CENTER", "CENTER")
        bw, bh = tw * EM_SIGN + 2 * PAD_X, th * EM_SIGN + 2 * PAD_Y
        Y0 = base_info["y"][0]
        x1 = centres[-1][0] + a
        x0 = x1 - bw
        z1 = base_info["top"] + LIP
        z0 = z1 - bh
        board = kit.cuboid("sign_board", (x0, Y0 - BT, z0), (x1, Y0, z1), kit.material("sign_board", "#323843", rough=0.75))
        fr = kit.material("sign_frame", "#5b636d", rough=0.5, spec=0.4)
        e, dz = 0.32, 0.08
        sign_objs = [board,
                     kit.cuboid("sign_frame_top", (x0, Y0 - BT - dz, z1 - e), (x1, Y0 - BT, z1), fr),
                     kit.cuboid("sign_frame_bottom", (x0, Y0 - BT - dz, z0), (x1, Y0 - BT, z0 + e), fr),
                     kit.cuboid("sign_frame_left", (x0, Y0 - BT - dz, z0 + e), (x0 + e, Y0 - BT, z1 - e), fr),
                     kit.cuboid("sign_frame_right", (x1 - e, Y0 - BT - dz, z0 + e), (x1, Y0 - BT, z1 - e), fr)]
        txt.data.size, txt.data.extrude = EM_SIGN, 0.12
        txt.location = ((x0 + x1) / 2, Y0 - BT - 0.12, (z0 + z1) / 2)
        txt.rotation_euler = (math.radians(90), 0, 0)               # in the board's plane, facing the front
        txt.data.materials.append(kit.material("sign_ink", "#dcdcdc", rough=0.6, emit=0.2, spec=0.3))
        txt.name = "sign_text"
    built = {key: {"objs": [o for (_, _, _, o) in v]} for key, v in seg_objs.items()}

    # labels: a line's label points at a box it fills completely (or at its only piece), from above; loss from the right
    def full_box(key):
        full = [(k, z0, z1) for (k, z0, z1, _) in seg_objs[key] if z1 - z0 > box_h - 1e-6]
        return full[len(full) // 2] if full else max(((k, z0, z1) for (k, z0, z1, _) in seg_objs[key]), key=lambda t: t[2] - t[1])
    left_c, near_c, right_c = kit.silhouette_corners(direction, centre=centres[0])
    labels = []
    for L in lines:
        text, sub = label_parts(L)
        k, z0, z1 = full_box(L["key"])
        if L["key"] == "loss":
            lc, nc, rc = kit.silhouette_corners(direction, centre=centres[k])
            labels.append(kit.Label(L["key"], text, (rc.x, rc.y, (z0 + z1) / 2), "R", sub=sub))
        else:
            labels.append(kit.Label(L["key"], text, (centres[k][0], centres[k][1], z1), "L", sub=sub))   # top face centre
    labels.append(kit.Label("limit", LIMIT_TEXT, (left_c.x, left_c.y, box_h), "L"))
    k_last = n_boxes - 1
    lc, nc, rc = kit.silhouette_corners(direction, centre=centres[k_last])
    labels.append(kit.Label("total", TOTAL_TEXT, (rc.x, rc.y, box_h), "R"))
    UP = {L["key"] for L in lines if L["key"] != "loss"}

    def place(cam):
        """Screen layout: 'up' labels end at the top of a vertical leader rising from their box; the others sit
        beside the row at their anchor's height. Returns a kit-style layout dict."""
        em_y = kit.EM * W_PX / H_PX
        lay = {}
        for lab in labels:
            p = kit.to_screen(scene, cam, lab.anchor)
            o = {"ax": p.x, "ay": p.y, "depth": p.z, "w": lab.w_em * kit.EM, "h": em_y, "below": 0.0}
            if lab.sub_obj:
                o["below"] = kit.SUB_GAP * em_y + lab.sub_h_em * kit.SUB_EM * W_PX / H_PX
                o["w"] = max(o["w"], lab.sub_w_em * kit.SUB_EM)
            lay[lab.key] = o
        ups = sorted([l for l in labels if l.key in UP], key=lambda l: lay[l.key]["ax"])
        top_row = kit.to_screen(scene, cam, (centres[-1][0], centres[-1][1] + b, box_h)).y
        y_prev = None
        for lab in ups:                                         # a staircase: each label above the last one's line
            o = lay[lab.key]
            y = max(o["ay"] + 2.2 * em_y, (y_prev + 1.9 * em_y + o["below"]) if y_prev is not None else -1)
            o["y"] = y
            o["x"] = o["ax"] - 0.5 * kit.EM                     # right-aligned, ending just left of its leader
            o["route"] = [(o["ax"], o["ay"]), (o["ax"], y + 0.35 * em_y)]
            o["x0"], o["x1"] = o["x"] - o["w"], o["x"]
            o["sub_y"] = y - o["h"] / 2 - kit.SUB_GAP * em_y
            y_prev = y
        for lab in labels:
            if lab.key in UP:
                continue
            o = lay[lab.key]
            sgn = -1 if lab.side == "L" else 1
            o["y"] = o["ay"]
            if lab.key == "total":
                o["y"] = o["ay"] + 2.4 * em_y
            o["x"] = o["ax"] + sgn * 2.2 * kit.EM
            end = o["x"] - sgn * 0.45 * kit.EM
            o["route"] = [(o["ax"], o["ay"]), (end, o["y"])] if abs(o["y"] - o["ay"]) < 0.002 else \
                [(o["ax"], o["ay"]), (o["ax"] + sgn * 0.8 * kit.EM, o["ay"]), (o["ax"] + sgn * 1.4 * kit.EM, o["y"]), (end, o["y"])]
            o["x0"], o["x1"] = (o["x"] - o["w"], o["x"]) if lab.side == "L" else (o["x"], o["x"] + o["w"])
            o["sub_y"] = o["y"] - o["h"] / 2 - kit.SUB_GAP * em_y
        return lay

    cam = kit.make_camera(scene, LENS)
    pts = kit.mesh_points(volumes + base + sign_objs)
    target, dist = (lo + hi) / 2, 2.0 * row_len
    for _ in range(14):
        kit.aim(cam, target, dist, direction)
        sp = [kit.to_screen(scene, cam, p) for p in pts]
        gx0, gx1, gy0, gy1 = min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)
        lay = place(cam)
        x0 = min([gx0] + [o["x0"] for o in lay.values()]); x1 = max([gx1] + [o["x1"] for o in lay.values()])
        y0 = min([gy0] + [o["y"] - o["h"] / 2 - o["below"] for o in lay.values()]); y1 = max([gy1] + [o["y"] + o["h"] / 2 for o in lay.values()])
        gw, gh = gx1 - gx0, gy1 - gy0
        z = min((0.90 - ((x1 - x0) - gw)) / gw, (0.86 - ((y1 - y0) - gh)) / gh)
        fw_, fh_ = kit.frame_size(scene, cam, dist)
        R = cam.matrix_world.to_3x3() @ Vector((1, 0, 0)); U = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
        target = target + R * ((x0 + x1) / 2 - 0.5) * fw_ + U * ((y0 + y1) / 2 - 0.5) * fh_
        if abs(z - 1) < 0.001 and abs((x0 + x1) / 2 - 0.5) < 0.001 and abs((y0 + y1) / 2 - 0.5) < 0.001:
            break
        dist /= z
    kit.aim(cam, target, dist, direction)
    lay = place(cam)
    d_box = kit.to_screen(scene, cam, (centres[0][0], 0, box_h / 2)).z
    fw, _ = kit.frame_size(scene, cam, d_box)
    frame = kit.box_frame(box_h, kit.STRUT * fw, kit.RIM * fw, centre=centres[0])      # ours: the real card
    ghost = kit.material("ghost", "#4d535c", rough=0.6, spec=0.2)
    s_, r_ = kit.STRUT * fw * 0.8 / 2, kit.STRUT * fw * 0.8 / 2
    for k in range(1, n_boxes):                                 # the others: dim outlines, no walls, no glow
        for i, p in enumerate(kit.box_corners(centre=centres[k])):
            kit.cuboid(f"ghost_{k}_strut_{i}", (p.x - s_, p.y - s_, 0), (p.x + s_, p.y + s_, box_h), ghost)
        cx, cy = centres[k]
        for nm, lo_, hi_ in (("-y", (cx - a - r_, cy - b - r_, box_h - r_), (cx + a + r_, cy - b + r_, box_h + r_)),
                             ("+y", (cx - a - r_, cy + b - r_, box_h - r_), (cx + a + r_, cy + b + r_, box_h + r_)),
                             ("-x", (cx - a - r_, cy - b + r_, box_h - r_), (cx - a + r_, cy + b - r_, box_h + r_)),
                             ("+x", (cx + a - r_, cy - b + r_, box_h - r_), (cx + a + r_, cy + b - r_, box_h + r_))):
            kit.cuboid(f"ghost_{k}_top_{nm}", lo_, hi_, ghost)
    kit.build_labels(scene, cam, labels, lay, lift=kit.RIM * fw)
    left_c, near_c = left_c, near_c

# ---- footnote, bottom left (only with --footnote; removed from draft b2 on)
if args.footnote:
    foot, fw_em, _ = kit.text_object("txt_foot", FOOT_TEXT, "LEFT", "BOTTOM_BASELINE")
    kit.place_on_screen(scene, cam, foot, 0.03, 0.035, d_box, kit.SUB_EM, ink2)

if args.variant == "a":
    kit.stage_lights(direction, key=3.1, rim=2.0, key_el=12, rim_turn=125)
else:                                                  # mirrored with the camera: key from its right, rim from behind-left
    kit.stage_lights(direction, key=3.1, rim=2.0, key_turn=-60, key_el=12, rim_turn=-125)

# ---- checks and layout
scene.frame_set(scene.frame_start)
heights = []
for L in lines:
    s = built[L["key"]]
    if args.variant == "a":
        h = kit.object_height(s["obj"])
        z = [round(s["z0"], 4), round(s["z1"], 4)]
    else:                                              # the line's pieces, box by box, added up
        h = sum(kit.object_height(o) for o in s["objs"])
        z = [[int(o.name.split("_")[-1]) + 1, round(kit.object_height(o), 4)] for o in s["objs"]]
    heights.append({"key": L["key"], "gib": L["gib"], "height_units": round(h, 6), "units_per_gib": h / L["gib"],
                    ("z" if args.variant == "a" else "pieces_box_height"): z})
rim_obj = next(o for o in frame if o.name == "rim_-y")
rlo, rhi = kit.world_bbox([rim_obj])
foot_rect = [0.03, 0.03 + fw_em * kit.SUB_EM, 0.035 - 0.004, 0.035 + 0.74 * kit.SUB_EM * W_PX / H_PX] if args.footnote else None
sign_check = None
if args.variant == "b" and sign_objs:
    sp = [kit.to_screen(scene, cam, p) for p in kit.mesh_points(sign_objs)]
    sr = [min(p.x for p in sp), max(p.x for p in sp), min(p.y for p in sp), max(p.y for p in sp)]
    on_labels = [k for k, o in lay.items() if sr[0] < o["x1"] and o["x0"] < sr[1]
                 and sr[2] < o["y"] + o["h"] / 2 and o["y"] - o["h"] / 2 - o.get("below", 0) < sr[3]]
    dg = bpy.context.evaluated_depsgraph_get()
    origin = cam.matrix_world.translation
    boxes_hidden = []
    for k, (cx, cy) in enumerate(centres):                 # rays to the bottom of every box's two visible faces
        for f in (0.1, 0.5, 0.9):
            for p in (Vector((cx - a + f * 2 * a, cy - b, 0.15)), Vector((cx - a, cy - b + f * 2 * b, 0.15))):
                v = p - origin
                hit, _, _, _, ob, _ = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.999)
                if hit and ob.name.startswith("sign"):
                    boxes_hidden.append(k + 1)
    sign_check = {"text": SIGN, "screen_rect": [round(v, 4) for v in sr], "inside_picture": 0.01 < sr[0] and sr[1] < 0.99 and 0.01 < sr[2] and sr[3] < 0.99,
                  "overlaps_labels": on_labels, "boxes_hidden": sorted(set(boxes_hidden)),
                  "letter_height_px_at_1200": round((kit.to_screen(scene, cam, (0, base_info["y"][0], 0.5 * EM_SIGN)).y
                                                    - kit.to_screen(scene, cam, (0, base_info["y"][0], 0)).y) * 1200 / 1.5 * 0.72, 1)}
layout = {
    "figure": "train_bill", "variant": args.variant,
    "scale": {"units_per_gib": GIB, "footprint_units": list(kit.FOOTPRINT)},
    "card": {"gib": card_gib, "box_height_units": box_h, "limit_rim_centre_z": (rlo.z + rhi.z) / 2},
    "lines_bottom_to_top": heights,
    "max_deviation_units_per_gib": max(abs(h["units_per_gib"] - 1.0) for h in heights),
    "total": {"gib_data": data["total_gib"], "sum_of_lines_units": round(sum(h["height_units"] for h in heights), 4),
              "label": TOTAL_TEXT},
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS,
               "distance": round(cam.matrix_world.translation.length, 2)},
    "labels": {k: {"text": next(l.text for l in labels if l.key == k), "side": next(l.side for l in labels if l.key == k),
                   "anchor_y": round(o["ay"], 4), "label_y": round(o["y"], 4), "x0": round(o["x0"], 4), "x1": round(o["x1"], 4)}
               for k, o in lay.items()},
    "label_overlaps": kit.label_overlaps(lay),
    "label_occlusions": kit.occlusion_check(scene, cam, labels, lay),
    "labels_inside_picture": all(0 < o["x0"] and o["x1"] < 1 for o in lay.values()),
    "footnote_rect": [round(v, 4) for v in foot_rect] if foot_rect else None,
    "footnote_clear": all(not (foot_rect[0] < o["x1"] and o["x0"] < foot_rect[1] and foot_rect[2] < o["y"] + o["h"] / 2
                               and o["y"] - o["h"] / 2 - o.get("below", 0) < foot_rect[3]) for o in lay.values()) if foot_rect else None,
    "sign": sign_check,
}
os.makedirs(os.path.dirname(out_layout), exist_ok=True)
kit.write_json(out_layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_gib", "label_overlaps", "label_occlusions",
                                                 "labels_inside_picture", "footnote_clear", "sign")}))
print("HEIGHTS", [(h["key"], h["gib"], h["height_units"]) for h in heights], layout["total"])

if not args.no_render:
    scene.render.filepath = out_png
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    lf = (left_c + near_c) / 2
    if args.variant == "a":
        pts = {f"{h['key']}_left_face": Vector((lf.x, lf.y, sum(h["z"]) / 2)) for h in heights}
    else:
        pts = {}
        for key, v in seg_objs.items():
            k, z0, z1, _ = max(v, key=lambda t: t[2] - t[1])
            pts[f"{key}_front_box{k + 1}"] = Vector((centres[k][0], -kit.FOOTPRINT[1] / 2, (z0 + z1) / 2))
    layout["draft_render"] = {"png": out_png, "size": [W_PX, H_PX], "samples": args.samples, "seconds": round(secs, 1),
                              "colours": kit.sample_colours(out_png, scene, cam, pts),
                              "targets": {L["key"]: kit.COLOURS[L["key"]] for L in lines}}
    kit.write_json(out_layout, layout)
    print("RENDER", round(secs, 1), "s", json.dumps(layout["draft_render"]["colours"]))
