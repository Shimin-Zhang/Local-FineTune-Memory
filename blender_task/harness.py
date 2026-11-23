"""Runs inside Blender: execute one script, then render what is in the scene and write a report.

blender --background --factory-startup --python harness.py -- <script.py> <out base> <report.json> [legacy-colour] [own-view] [only-own-view] [no-render]
                                                              [size=384] [samples=48] [denoise]

The scene starts as Blender's default (cube, light, camera). The render always uses a camera and sun added here,
so pictures are comparable across scripts. Two pictures are written, <out base>.v0.png and .v1.png, from opposite
sides, because scripts disagree about which side is the front. A single large flat object (a floor) is left out of
the framing so it does not shrink the subject. With "legacy-colour", a colour set only through diffuse_color is
copied onto the shader, which is how such a script looked in Blender before version 5. With "own-view" a third
picture, <out base>.v2.png, is rendered first with nothing added: the script's own lights and background, and its
own camera if it set one up (otherwise the first of the two fixed views). With "no-render" only the report is
written. The report also says where the script's camera and lights point and where the built objects are. Never run this outside the sandbox (run_sandboxed.py): the script it executes is model-written.
"""
import bpy, sys, json, math, traceback
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
script_path, png_base, report_path = ARGS[:3]
LEGACY_COLOUR = "legacy-colour" in ARGS[3:]
OWN_VIEW, NO_RENDER = "own-view" in ARGS[3:], "no-render" in ARGS[3:]
ONLY_OWN = "only-own-view" in ARGS[3:]                   # with own-view: skip the two fixed views (for review pictures)
OPT = dict(x.split("=") for x in ARGS[3:] if "=" in x)   # size=<pixels> samples=<n>, for a cleaner picture than the quick default
SIZE, SAMPLES, DENOISE = int(OPT.get("size", 384)), int(OPT.get("samples", 48)), "denoise" in ARGS[3:]
_c0 = bpy.context.scene.camera  # the camera of a new file, to tell later whether the script set up its own
CAM0 = (_c0.name, [v for row in _c0.matrix_world for v in row]) if _c0 else None
rep = {"blender": bpy.app.version_string, "error": None, "error_line": None}
for _o in bpy.data.objects:                               # mark what a new file starts with, to tell later whether it is still there
    _o["_was_there_at_start"] = 1


def save():
    json.dump(rep, open(report_path, "w"), indent=1)


save()  # so a hard crash or timeout still leaves a report
code = open(script_path).read()
try:
    exec(compile(code, "script.py", "exec"), {"__name__": "__main__"})
except BaseException as e:  # includes SystemExit from scripts that call sys.exit()
    rep["error"] = f"{type(e).__name__}: {str(e).strip()[:300]}"
    tb = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == "script.py"]
    if tb:
        rep["error_line"] = code.splitlines()[tb[-1].lineno - 1].strip()[:200] if tb[-1].lineno <= len(code.splitlines()) else None
save()

scene = bpy.context.scene
try:
    if bpy.context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
except Exception:
    pass
bpy.context.view_layer.update()
RENDERABLE = {"MESH", "CURVE", "SURFACE", "META", "FONT"}
objs = [o for o in scene.objects if o.type in RENDERABLE and not o.hide_render]
rep["n_renderable_objects"] = len(objs)
rep["object_types"] = {t: sum(o.type == t for o in scene.objects) for t in sorted({o.type for o in scene.objects})}
rep["default_cube_still_there"] = any(o.name == "Cube" and o.type == "MESH" for o in scene.objects)   # by name: also true of a new cube
rep["starting_objects_left"] = sorted(o.type for o in scene.objects if o.get("_was_there_at_start"))      # exact: the marked ones

# materials: will the colour show in a render?
DEFAULT = (0.8, 0.8, 0.8)
close = lambda a, b: all(abs(x - y) < 1e-3 for x, y in zip(a, b))
mats, seen, no_mat = [], set(), 0
for o in objs:
    slots = [s.material for s in getattr(o, "material_slots", []) if s.material]
    if not slots:
        no_mat += 1
    for m in slots:
        if m.name in seen:
            continue
        seen.add(m.name)
        info = {"name": m.name, "diffuse_color": [round(c, 3) for c in m.diffuse_color[:3]], "n_nodes": 0,
                "principled_base_color": None, "base_color_linked": False, "node_types": []}
        if m.node_tree:
            info["n_nodes"] = len(m.node_tree.nodes)
            info["node_types"] = sorted(n.type for n in m.node_tree.nodes)
            p = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if p:
                inp = next((i for i in p.inputs if i.identifier == "Base Color"), None)
                if inp:
                    info["principled_base_color"] = [round(c, 3) for c in inp.default_value[:3]]
                    info["base_color_linked"] = inp.is_linked
        untouched_nodes = (info["principled_base_color"] is not None and close(info["principled_base_color"], DEFAULT)
                           and not info["base_color_linked"] and info["n_nodes"] <= 2)
        info["colour_set_only_for_viewport"] = (not close(info["diffuse_color"], DEFAULT)) and untouched_nodes
        if LEGACY_COLOUR and info["colour_set_only_for_viewport"]:
            p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            next(i for i in p.inputs if i.identifier == "Base Color").default_value = tuple(m.diffuse_color)
            info["colour_restored_by_harness"] = True
        mats.append(info)
rep["materials"] = mats
rep["objects_without_material"] = no_mat
rep["materials_viewport_only"] = sum(m["colour_set_only_for_viewport"] for m in mats)
AXIS = lambda o, v: [round(c, 4) for c in (o.matrix_world.to_3x3() @ Vector(v)).normalized()]  # a local axis in world space
rep["lights"] = [{"type": o.data.type, "energy": round(o.data.energy, 2), "color": [round(c, 3) for c in o.data.color],
                  "location": [round(c, 2) for c in o.matrix_world.translation], "direction": AXIS(o, (0, 0, -1)),
                  "spot_size": round(o.data.spot_size, 4) if o.data.type == "SPOT" else None}
                 for o in scene.objects if o.type == "LIGHT" and not o.hide_render]
sc = scene.camera
try:
    untouched = sc is not None and CAM0 is not None and sc.name == CAM0[0] and all(abs(a - b) < 1e-5 for a, b in zip([v for row in sc.matrix_world for v in row], CAM0[1]))
except ReferenceError:
    untouched = False
rep["script_set_camera"] = sc is not None and not untouched
rep["depth_of_field"] = bool(sc is not None and sc.type == "CAMERA" and sc.data.dof.use_dof)
# where the script's own camera is and where it points, to tell later whether it looks at what was built
rep["camera"] = ({"location": [round(c, 4) for c in sc.matrix_world.translation], "direction": AXIS(sc, (0, 0, -1)), "up": AXIS(sc, (0, 1, 0)),
                  "angle": round(sc.data.angle, 4) if sc.type == "CAMERA" else None} if rep["script_set_camera"] else None)

# frame everything, except one dominant flat object (a floor or ground plane)
def box(os_):
    pts = [o.matrix_world @ Vector(c) for o in os_ for c in o.bound_box]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


framed = objs
if len(objs) >= 3:
    dims = {o.name: (box([o])[1] - box([o])[0]) for o in objs}
    big = max(objs, key=lambda o: dims[o.name].length)
    d = dims[big.name]
    rest = [o for o in objs if o is not big]
    rlo, rhi = box(rest)
    if min(d) < 0.05 * max(d) and d.length > 1.8 * (rhi - rlo).length:
        framed = rest
        rep["left_out_of_framing"] = big.name
lo, hi = box(framed) if framed else (Vector((-1, -1, -1)), Vector((1, 1, 1)))
center, radius = (lo + hi) / 2, max((hi - lo).length / 2, 1e-3)
rep["bbox_size"] = [round(v, 3) for v in (hi - lo)]
rep["scene_center"], rep["scene_radius"] = [round(v, 4) for v in center], round(radius, 4)   # of what is framed
save()
if NO_RENDER:
    raise SystemExit(0)
cam_data = bpy.data.cameras.new("EvalCam")
cam = bpy.data.objects.new("EvalCam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
dist = radius / math.sin(cam_data.angle / 2) * 1.1
cam_data.clip_start, cam_data.clip_end = max(dist / 1000, 1e-4), dist * 10 + radius * 10
VIEWS = [Vector((1.0, -1.25, 0.8)), Vector((-1.0, 1.25, 0.8))]

try:
    scene.render.engine = "CYCLES"
except TypeError:
    pass
rep["render_engine"] = scene.render.engine
if scene.render.engine == "CYCLES":
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = DENOISE
scene.render.resolution_x = scene.render.resolution_y = SIZE
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.image_settings.file_format = "PNG"
try:
    scene.view_settings.view_transform = "Standard"  # keeps saturated colours saturated
except TypeError:
    pass
scene.frame_set(scene.frame_start)
rep["rendered"] = 0


def shoot(path):
    scene.render.filepath = path
    try:
        bpy.ops.render.render(write_still=True)
        rep["rendered"] += 1
    except Exception as e:
        rep["render_error"] = f"{type(e).__name__}: {str(e)[:300]}"


def aim(direction):
    cam.location = center + direction.normalized() * dist
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()


if OWN_VIEW:  # first, with nothing added: the script's lights and background, and its camera if it set one up
    if rep["script_set_camera"]:
        scene.camera = sc
    else:
        aim(VIEWS[0])
    shoot(f"{png_base}.v2.png")
    scene.camera = cam
    if ONLY_OWN:
        save()
        raise SystemExit(0)

sun = bpy.data.objects.new("EvalSun", bpy.data.lights.new("EvalSun", "SUN"))
sun.data.energy = 2.5
scene.collection.objects.link(sun)
if scene.world is None:
    scene.world = bpy.data.worlds.new("EvalWorld")
w = scene.world
try:
    w.use_nodes = True
except Exception:
    pass
bg = next((n for n in w.node_tree.nodes if n.type == "BACKGROUND"), None) if w.node_tree else None
if bg and not bg.inputs[0].is_linked:
    bg.inputs[0].default_value = (0.55, 0.6, 0.7, 1.0)
    bg.inputs[1].default_value = 0.6
for k, direction in enumerate(VIEWS):
    aim(direction)
    sun.rotation_euler = (math.radians(50), 0, math.radians(35 if k == 0 else 215))  # keep the visible side lit
    shoot(f"{png_base}.v{k}.png")
save()
