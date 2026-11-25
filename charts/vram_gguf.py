"""Figure: how the RTX 4090's 24 GiB is used when you just run Qwen3.8-27B (GGUF) in llama.cpp, 3,000 tokens.

One box = the whole card, layers stacked inside to scale (kit.UNITS_PER_MIB), free space left empty, the card's
limit as a glowing rim. Numbers come from charts/data/vram_gguf_3000.json unchanged.

~/.local/bin/blender -b --factory-startup --python-exit-code 1 -P charts/vram_gguf.py -- \
    [--size 900x600] [--samples 32] [--out charts/out/vram_gguf_3000_draft.png] [--no-render]
"""
import argparse, json, os, sys, time
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--size", default="900x600")
ap.add_argument("--samples", type=int, default=32)
ap.add_argument("--out", default=os.path.join(HERE, "out", "vram_gguf_3000_draft.png"))
ap.add_argument("--layout", default=os.path.join(HERE, "out", "vram_gguf_3000.layout.json"))
ap.add_argument("--data", default=os.path.join(HERE, "data", "vram_gguf_3000.json"))
ap.add_argument("--no-render", action="store_true")
ap.add_argument("--variant", default="open", choices=["glass", "open"],
                help="glass: the free headroom as smoked glass with a lid; open: cut-away front, two dark back walls")
ap.add_argument("--look", default="draft2", choices=["draft2", "draft1"],
                help="draft2: clear lid, quiet warm-grey rim; draft1: open top, loud white rim (the first draft)")
args = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
W, H = (int(v) for v in args.size.split("x"))

data = json.load(open(args.data))
layers = data["layers_bottom_to_top"]
card_mib = data["card_total_mib"]

# ---- the look of this figure
ELEVATION, AZIMUTH, LENS = 26.0, 38.0, 80.0
SIDE = {"free": "L", "weights": "L", "driver": "L", "limit": "R", "working": "R", "context": "R"}

scene = kit.reset()
kit.render_settings(scene, W, H, args.samples, denoise=True)
kit.world(scene)
direction = kit.view_direction(ELEVATION, AZIMUTH)

# ---- volumes
mats = {
    "driver": kit.material("driver", kit.COLOURS["driver"], emit=0.10, rough=0.85, spec=0.12),
    "weights": kit.material("weights", kit.COLOURS["weights"], emit=0.10, rough=0.85, spec=0.12),
    "context": kit.glow_material("context", kit.COLOURS["context"], 1.35),
    "working": kit.material("working", kit.COLOURS["working"], emit=0.12, rough=0.85, spec=0.12),
}
stack = kit.stack_layers(layers, mats)                 # "free" has no material: it stays empty
box_h = kit.layer_height(card_mib)
free = next(s for s in stack if s["key"] == "free")
if args.variant == "glass":
    walls = kit.glass_headroom(free["z0"], box_h)
else:
    walls = kit.back_walls(box_h, direction)
volumes = [s["obj"] for s in stack if s["obj"]] + walls

# ---- base, from the bounding box of what stands on it
lo, hi = kit.world_bbox(volumes)
base, base_info = kit.floating_base(lo, hi)

# ---- labels (one per layer, plus the limit), anchored on the box's left / right outline
left_c, near_c, right_c = kit.silhouette_corners(direction)
labels = []
for s in stack:
    text = f"{next(L['label'] for L in layers if L['key'] == s['key'])} {s['mib'] / kit.MIB_PER_GIB:.1f} GiB"
    side = SIDE[s["key"]]
    c = left_c if side == "L" else right_c
    sub = data["weights_on_card"]["label_lines"] if s["key"] == "weights" else None   # quantization mix, as in the data
    labels.append(kit.Label(s["key"], text, (c.x, c.y, (s["z0"] + s["z1"]) / 2), side, sub=sub))
labels.append(kit.Label("limit", "RTX 4090: 24 GiB", (right_c.x, right_c.y, box_h), "R"))

# ---- camera from the bounding box of everything (labels included, at their fixed on-screen size)
cam = kit.make_camera(scene, LENS)
lay = kit.frame_scene(scene, cam, volumes + base, direction, labels)

# ---- what is sized on screen: the frame of the box, the limit rim, labels and leaders
dist = (cam.matrix_world.translation - Vector((0, 0, box_h / 2))).length
fw, _ = kit.frame_size(scene, cam, dist)
strut, rim = kit.STRUT * fw, kit.RIM * fw
if args.look == "draft1":
    frame = kit.box_frame(box_h, strut, 0.0045 * fw, rim_strength=4.0, rim_colour="#fff6e8")
    rim = 0.0045 * fw
else:
    frame = kit.box_frame(box_h, strut, rim)
    frame += kit.clear_lid(box_h)
kit.build_labels(scene, cam, labels, lay, lift=rim)

# ---- light: low key from the left-front, rim from behind-right, the context slab's glow spilling out
kit.stage_lights(direction, key=3.1, rim=2.0, key_el=12, rim_turn=125)
ctx = next(s for s in stack if s["key"] == "context")
out_h = Vector((direction.x, direction.y, 0)).normalized()
kit.point_glow("context_glow", near_c + out_h * 0.22 * kit.FOOTPRINT[0] + Vector((0, 0, (ctx["z0"] + ctx["z1"]) / 2)),
               kit.COLOURS["context"], power=120.0, radius=0.5)

# ---- layout check: heights read back from the built objects
scene.frame_set(scene.frame_start)
bpy_layers = []
for s in stack:
    if s["obj"]:
        h = kit.object_height(s["obj"])
        src = "object"
    else:                                              # free: the gap between the top layer and the rim
        top_of_layers = max(kit.world_bbox([t["obj"]])[1].z for t in stack if t["obj"])
        h = box_h - top_of_layers
        src = "box height minus the top of the built layers"
    bpy_layers.append({"key": s["key"], "mib": s["mib"], "height_units": round(h, 6),
                       "units_per_mib": h / s["mib"], "height_source": src,
                       "share_of_card": round(s["mib"] / card_mib, 5)})
rim_obj = next(o for o in frame if o.name == "rim_-y")
rim_lo, rim_hi = kit.world_bbox([rim_obj])
layout = {
    "figure": "vram_gguf_3000", "variant": args.variant, "look": args.look,
    "scale": {"units_per_mib": kit.UNITS_PER_MIB, "means": "1 Blender unit of height = 1 GiB (1,024 MiB)",
              "footprint_units": list(kit.FOOTPRINT)},
    "card": {"mib": card_mib, "box_height_units": box_h, "limit_rim_centre_z": (rim_lo.z + rim_hi.z) / 2,
             "units_per_mib": box_h / card_mib},
    "layers_bottom_to_top": bpy_layers,
    "max_deviation_units_per_mib": max(abs(L["units_per_mib"] - kit.UNITS_PER_MIB) for L in bpy_layers),
    "base": {k: (list(v) if isinstance(v, tuple) else v) for k, v in base_info.items()},
    "camera": {"elevation_deg": ELEVATION, "azimuth_deg": AZIMUTH, "lens_mm": LENS,
               "distance": round((cam.matrix_world.translation - Vector((0, 0, 0))).length, 3)},
    "labels": {k: {"text": next(l.text for l in labels if l.key == k), "side": next(l.side for l in labels if l.key == k),
                   "anchor_y": round(o["ay"], 4), "label_y": round(o["y"], 4), "x0": round(o["x0"], 4), "x1": round(o["x1"], 4),
                   **({"sub_lines": next(l.sub for l in labels if l.key == k), "sub_bottom_y": round(o["y"] - o["h"] / 2 - o["below"], 4)}
                      if o["below"] else {})}
               for k, o in lay.items()},
    "label_overlaps": kit.label_overlaps(lay),
    "label_occlusions": kit.occlusion_check(scene, cam, labels, lay),
    "labels_inside_picture": all(0 < o["x0"] and o["x1"] < 1 for o in lay.values()),
}
os.makedirs(os.path.dirname(args.layout), exist_ok=True)
kit.write_json(args.layout, layout)
print("LAYOUT", json.dumps({k: layout[k] for k in ("max_deviation_units_per_mib", "label_overlaps", "label_occlusions",
                                                 "labels_inside_picture")}))

if not args.no_render:
    scene.render.filepath = args.out
    t0 = time.time()
    import bpy
    bpy.ops.render.render(write_still=True)
    secs = time.time() - t0
    # colour check: the middle of each layer on the lit (left) and shaded (right) visible face
    a, b = kit.FOOTPRINT[0] / 2, kit.FOOTPRINT[1] / 2
    pts = {}
    lf = (left_c + near_c) / 2                         # middle of the left visible face (xy)
    rf = (right_c + near_c) / 2
    for s in stack:
        if s["obj"]:
            z = (s["z0"] + s["z1"]) / 2
            pts[f"{s['key']}_left_face"] = Vector((lf.x, lf.y, z))
            pts[f"{s['key']}_right_face"] = Vector((rf.x, rf.y, z))
    layout["draft_render"] = {"png": args.out, "size": [W, H], "samples": args.samples, "seconds": round(secs, 1),
                              "colours": kit.sample_colours(args.out, scene, cam, pts),
                              "targets": {k: v for k, v in kit.COLOURS.items()}}
    kit.write_json(args.layout, layout)
    print("RENDER", round(secs, 1), "s", json.dumps(layout["draft_render"]["colours"]))
