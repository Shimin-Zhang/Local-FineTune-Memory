"""Runs inside Blender (sandboxed): one step of a session that keeps its scene from step to step.

blender --background --factory-startup --disable-autoexec [<state.blend>] --python session_step.py --
        <step.py, or - for none> <out.png> <result.json> <state.blend> [size=512] [samples=48]

Blender opens the scene as the last step left it (a new file at the first step: cube, light, camera). This runs the
step's code in a fresh namespace, as a live Blender behind a "run this Python" tool would: the scene is kept between
steps, Python variables are not. Whatever ran before an error stays in the scene. Then the scene is saved back to
<state.blend>, what happened is written to <result.json>, and the scene is rendered to <out.png>: through its own
camera, with its own lights and background, if a camera was set up; otherwise from a fixed view. What the render
changes (engine, size, the fixed camera) is not saved. With "-" for the step nothing is run or saved; the scene is
only rendered (a larger final picture). Never run this outside the sandbox (agent_loop.py): the code is model-written.
"""
import bpy, sys, os, io, json, math, traceback, contextlib
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:]
step_path, png_path, result_path, state_path = ARGS[:4]
OPT = dict(x.split("=") for x in ARGS[4:] if "=" in x)
SIZE, SAMPLES = int(OPT.get("size", 512)), int(OPT.get("samples", 48))
KEEP = state_path + ".keep.json"                          # data with no user that was kept alive across the save
rep = {"blender": bpy.app.version_string, "error": None, "error_line": None, "printed": "", "state_saved": None}


def save():
    json.dump(rep, open(result_path, "w"), indent=1)


save()                                                     # so a hard crash or a timeout still leaves a result
first = not bpy.data.filepath
if first:                                                  # mark what a new file starts with
    for o in bpy.data.objects:
        o["_was_there_at_start"] = 1
        if o.type == "CAMERA":
            o["_start_matrix"] = [v for row in o.matrix_world for v in row]
elif os.path.exists(KEEP):                                 # a live session keeps unused data; saving drops it, so it was pinned
    for attr, name in json.load(open(KEEP)):
        d = getattr(bpy.data, attr, None)
        if d is not None and d.get(name) is not None:
            d[name].use_fake_user = False

if step_path != "-":
    code, out = open(step_path).read(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out):               # what the code prints; warnings (stderr) are left out
            exec(compile(code, "script.py", "exec"), {"__name__": "__main__"})
    except BaseException as e:                             # includes SystemExit from code that calls sys.exit()
        rep["error"] = f"{type(e).__name__}: {str(e).strip()[:300]}"
        tb = [f for f in traceback.extract_tb(e.__traceback__) if f.filename == "script.py"]
        line = tb[-1].lineno if tb else getattr(e, "lineno", None)
        if line and line <= len(code.splitlines()):
            rep["error_line"] = code.splitlines()[line - 1].strip()[:200]
    rep["printed"] = out.getvalue()[-600:]
    save()
    try:
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
    except Exception:
        pass
    try:                                                   # save the scene for the next step
        kept = []
        for attr in ("objects", "meshes", "curves", "materials", "lights", "cameras", "collections", "node_groups", "worlds", "textures", "images"):
            for d in getattr(bpy.data, attr, []):
                if d.users == 0 and not d.use_fake_user:
                    d.use_fake_user = True
                    kept.append([attr, d.name])
        bpy.ops.wm.save_as_mainfile(filepath=state_path + ".new.blend", copy=True, check_existing=False)
        os.replace(state_path + ".new.blend", state_path)
        json.dump(kept, open(KEEP, "w"))
        rep["state_saved"] = True
    except Exception as e:
        rep["state_saved"] = False
        rep["save_error"] = f"{type(e).__name__}: {str(e)[:300]}"
    save()

scene = bpy.context.scene
try:
    bpy.context.view_layer.update()
except Exception:
    pass
RENDERABLE = {"MESH", "CURVE", "SURFACE", "META", "FONT"}
objs = [o for o in scene.objects if o.type in RENDERABLE and not o.hide_render]
rep["n_objects"] = len(objs)
rep["n_lights"] = sum(o.type == "LIGHT" and not o.hide_render for o in scene.objects)
rep["n_materials"] = len({s.material.name for o in objs for s in getattr(o, "material_slots", []) if s.material})
rep["starting_objects_left"] = sorted(o.type for o in scene.objects if o.get("_was_there_at_start"))
sc = scene.camera
try:
    m0 = sc.get("_start_matrix") if sc is not None else None
    untouched = m0 is not None and all(abs(a - b) < 1e-5 for a, b in zip([v for row in sc.matrix_world for v in row], m0))
except ReferenceError:
    sc, untouched = None, False
rep["own_camera"] = sc is not None and not untouched
save()


def box(os_):
    pts = [o.matrix_world @ Vector(c) for o in os_ for c in o.bound_box]
    return (Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)]))


if not rep["own_camera"]:                                  # the fixed view: everything in frame, except one dominant flat object (a ground plane)
    framed = objs
    if len(objs) >= 3:
        dims = {o.name: (box([o])[1] - box([o])[0]) for o in objs}
        big = max(objs, key=lambda o: dims[o.name].length)
        rest = [o for o in objs if o is not big]
        rlo, rhi = box(rest)
        if min(dims[big.name]) < 0.05 * max(dims[big.name]) and dims[big.name].length > 1.8 * (rhi - rlo).length:
            framed = rest
    lo, hi = box(framed) if framed else (Vector((-1, -1, -1)), Vector((1, 1, 1)))
    center, radius = (lo + hi) / 2, max((hi - lo).length / 2, 1e-3)
    cam_data = bpy.data.cameras.new("ViewCam")
    cam = bpy.data.objects.new("ViewCam", cam_data)
    scene.collection.objects.link(cam)
    dist = radius / math.sin(cam_data.angle / 2) * 1.1
    cam_data.clip_start, cam_data.clip_end = max(dist / 1000, 1e-4), dist * 10 + radius * 10
    cam.location = center + Vector((1.0, -1.25, 0.8)).normalized() * dist
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
try:
    scene.render.engine = "CYCLES"
except TypeError:
    pass
if scene.render.engine == "CYCLES":
    scene.cycles.device = "CPU"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
scene.render.resolution_x = scene.render.resolution_y = SIZE
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.render.use_border = False
scene.render.image_settings.file_format = "PNG"
try:
    scene.view_settings.view_transform = "Standard"       # as in every other picture of this project
except TypeError:
    pass
try:
    scene.frame_set(scene.frame_start)
    scene.render.filepath = png_path
    bpy.ops.render.render(write_still=True)
    rep["rendered"] = os.path.exists(png_path)
except Exception as e:
    rep["rendered"] = False
    rep["render_error"] = f"{type(e).__name__}: {str(e)[:300]}"
save()
