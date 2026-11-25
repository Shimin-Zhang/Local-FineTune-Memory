"""Shared pieces for the post's Blender figures: one scale, one palette, one look.

Every figure draws GPU memory as volume in the low-poly diorama look of synth/guide.md ("The look"): a box with
the fixed FOOTPRINT whose height is the memory, at one scale for the whole series (UNITS_PER_MIB: one Blender unit
of height is one GiB). Nothing here fixes the zoom. The base is sized from the bounding box of what was built,
the camera distance follows the guide's framing rule (whole scene in frame, spanning about 85-90%), and what must
stay legible at any zoom (labels, leader lines, the box's struts, the glowing limit rim) is sized as a fraction of
the picture's width, after the camera is placed.

Use from a figure script run by Blender:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import kit
Build order: volumes (layers, walls) -> base -> camera (frame_scene) -> frame and labels (sized on screen) -> lights.
"""
import bpy, bmesh, json, math, random
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

# ---------------------------------------------------------------- scale, fixed for the whole series
MIB_PER_GIB = 1024.0
UNITS_PER_MIB = 1.0 / MIB_PER_GIB    # height: 1 Blender unit = 1 GiB of memory over the fixed footprint
FOOTPRINT = (10.0, 10.0)             # x, y of every memory box; so 1 GiB = 100 cubic units of volume

# ---------------------------------------------------------------- palette, fixed for the whole series
COLOURS = {                          # dark-surface steps of a palette checked for colour-blind separation
    "weights": "#3987e5",
    "context": "#d95926",
    "working": "#199e70",
    "driver":  "#6b6b6b",            # someone else's memory: a neutral grey
    "gradients": "#c98500",          # the training bill; validated as a stack in this order with weights at the bottom
    "optimizer": "#d55181",
    "activations": "#9085e9",
    "loss": "#e66767",
    "adapter": "#008300",            # the palette's green dark step; validated next to weights, activations, loss
    "scales": "#9ec5f4",             # quantization scales (bits and bytes figures)
    "frozen": "#82bdf5",             # frozen (4-bit) weights: a paler step of the weights blue; validated against it
}
LOOK = {                             # the scene around the chart: neutrals only, so the memory colours stand out
    "background": (0.010, 0.010, 0.030),
    "ink": "#e9e9e9",                # label text
    "ink2": "#b2b2b2",               # secondary label lines: dimmer, still well clear of the background
    "leader": "#a9a9a9",             # leader lines and their dots
    "limit": "#ece4d6",              # the rim at the card's limit: a faint warm-grey glow, quieter than the layers
    "frame": "#5b636d",              # the box's vertical struts
    "wall": "#20252d",               # the box's two back walls
    "pcb": "#171b21", "pcb_edge": "#2b3039", "rock": "#4a4f58",
    "chip": "#101215", "metal": "#aab0b7",
}
# Screen-relative sizes, as fractions of the picture's width, so they hold at every zoom.
EM = 0.0165          # label text size (1,200 px wide picture -> about 20 px)
SUB_EM = 0.0135      # secondary label lines (1,200 px wide -> about 16 px)
SUB_GAP = 0.30       # gap between a label's main line and its secondary lines, in main-line ems
LINE = 0.0019        # leader line width
DOT = 0.0050         # leader end dot diameter
STRUT = 0.0030       # the box's vertical struts
RIM = 0.0032         # the limit rim, a touch thicker than the struts
RIM_GLOW = 0.5       # emission strength of the limit rim (draft 1 used 4.0 and "#fff6e8": too loud)
LID_VEIL = 0.018     # how much of the clear lid is a faint neutral sheet (0 = invisible)


# ---------------------------------------------------------------- basics
def hex_lin(h):
    """'#rrggbb' (sRGB) -> linear RGB, the space Blender's shader colours are in."""
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def _rgb(c):
    return hex_lin(c) if isinstance(c, str) else tuple(c)


def reset():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for d in list(coll):
            coll.remove(d)
    return bpy.context.scene


def material(name, colour, rough=0.7, emit=0.0, spec=0.35, metallic=0.0):
    """Flat colour, rough finish. emit > 0 adds a self-lit share of the same colour, which keeps a hue readable on
    the shadow side without a flat fill light."""
    m = bpy.data.materials.new(name)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgb = _rgb(colour)
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Emission Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*rgb, 1.0)
    return m


def glow_material(name, colour, strength):
    """Pure emission: reads as a light source, the same colour on every face."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    rgb = _rgb(colour)
    em.inputs["Color"].default_value = (*rgb, 1.0)
    em.inputs["Strength"].default_value = strength
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    m.diffuse_color = (*rgb, 1.0)
    return m


def glass_material(name, tint=(0.42, 0.46, 0.53), sheen=0.3, rough=0.08):
    """Smoked glass without refraction: a tinted see-through surface with a little Fresnel gloss on top."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (*tint, 1.0)
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = rough
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = sheen
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Fresnel"], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(gl.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (*tint, 0.3)
    return m


def mesh_object(name, verts, faces, mats, face_mats=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    for m in mats:
        me.materials.append(m)
    for i, p in enumerate(me.polygons):
        p.use_smooth = False
        if face_mats:
            p.material_index = face_mats[i]
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def cuboid(name, lo, hi, mats, face_mats=None):
    """Axis-aligned box from corner lo to corner hi. Faces: bottom, top, -y, +x, +y, -x."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return mesh_object(name, v, f, mats if isinstance(mats, (list, tuple)) else [mats], face_mats)


def world_bbox(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in objs:
        ev = ob.evaluated_get(dg)
        pts += [ob.matrix_world @ Vector(c) for c in ev.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def no_shadow(ob):
    """For annotation (labels, leaders): seen by the camera, invisible to light."""
    for attr in ("visible_shadow", "visible_diffuse", "visible_glossy", "visible_transmission", "visible_volume_scatter"):
        try:
            setattr(ob, attr, False)
        except AttributeError:
            pass


# ---------------------------------------------------------------- render and world
def render_settings(scene, width, height, samples, denoise=True):
    """The project's render settings (blender_task/harness.py): Cycles on the CPU, Standard view transform, PNG."""
    try:
        scene.render.engine = "CYCLES"
    except TypeError:
        pass
    try:
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "NONE"
    except Exception:
        pass
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = denoise
    for attr, val in (("denoiser", "OPENIMAGEDENOISE"), ("denoising_use_gpu", False)):
        try:
            setattr(scene.cycles, attr, val)
        except (AttributeError, TypeError):
            pass
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    try:
        scene.view_settings.view_transform = "Standard"   # keeps saturated colours saturated
        scene.view_settings.look = "None"
    except TypeError:
        pass
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0


def world(scene, colour=None):
    w = bpy.data.worlds.new("World")
    scene.world = w
    bg = next(n for n in w.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (*(colour or LOOK["background"]), 1.0)
    bg.inputs["Strength"].default_value = 1.0
    return w


# ---------------------------------------------------------------- memory as volume
def layer_height(mib):
    return mib * UNITS_PER_MIB


def stack_layers(layers, mats, footprint=FOOTPRINT, centre=(0.0, 0.0), z0=0.0):
    """Stacks layers [{key, mib, ...}] bottom to top, each the full footprint and mib*UNITS_PER_MIB tall.
    A layer whose key has no material in mats is left empty (it still takes its height). Returns
    [{key, mib, z0, z1, obj}] with z read from the data, not rounded."""
    a, b = footprint[0] / 2, footprint[1] / 2
    cx, cy = centre
    out, z = [], z0
    for L in layers:
        h = layer_height(L["mib"])
        ob = None
        if L["key"] in mats:
            ob = cuboid(f"layer_{L['key']}", (cx - a, cy - b, z), (cx + a, cy + b, z + h), mats[L["key"]])
        out.append({"key": L["key"], "mib": L["mib"], "z0": z, "z1": z + h, "obj": ob})
        z += h
    return out


def far_sides(direction):
    """The two vertical sides of an axis-aligned box that face away from a camera looking from `direction`."""
    return ["-x" if direction.x > 0 else "+x", "-y" if direction.y > 0 else "+y"]


def back_walls(height, direction, footprint=FOOTPRINT, centre=(0.0, 0.0), thick=None, mat=None):
    """The box's two far walls (the front two are cut away so the camera sees in), just outside the footprint."""
    a, b = footprint[0] / 2, footprint[1] / 2
    cx, cy = centre
    t = thick or 0.01 * max(footprint)
    mat = mat or material("wall", LOOK["wall"], rough=0.45, spec=0.5)
    obs = []
    for s in far_sides(direction):
        if s == "-x":
            lo, hi = (cx - a - t, cy - b, 0), (cx - a, cy + b + t, height)
        elif s == "+x":
            lo, hi = (cx + a, cy - b - t, 0), (cx + a + t, cy + b, height)
        elif s == "-y":
            lo, hi = (cx - a - t, cy - b - t, 0), (cx + a, cy - b, height)
        else:
            lo, hi = (cx - a, cy + b, 0), (cx + a + t, cy + b + t, height)
        obs.append(cuboid(f"wall_{s}", lo, hi, mat))
    return obs


def glass_headroom(z0, z1, footprint=FOOTPRINT, centre=(0.0, 0.0), mat=None):
    """The empty part of the box, z0..z1, as a smoked-glass shell: four walls and the lid, no bottom (the top of
    the stack is its floor). Free memory reads as the container's empty headroom."""
    a, b = footprint[0] / 2, footprint[1] / 2
    cx, cy = centre
    v = [(cx - a, cy - b, z0), (cx + a, cy - b, z0), (cx + a, cy + b, z0), (cx - a, cy + b, z0),
         (cx - a, cy - b, z1), (cx + a, cy - b, z1), (cx + a, cy + b, z1), (cx - a, cy + b, z1)]
    f = [(4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    ob = mesh_object("free_glass", v, f, [mat or glass_material("glass")])
    return [ob]


def veil_material(name, veil, colour=(1.0, 1.0, 1.0)):
    """Clear: fully see-through with no tint or refraction, plus `veil` of a faint neutral sheet so it can be seen."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    tr.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*colour, 1.0)
    em.inputs["Strength"].default_value = 1.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.inputs[0].default_value = veil
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    m.diffuse_color = (*colour, veil)
    return m


def clear_lid(height, footprint=FOOTPRINT, centre=(0.0, 0.0), veil=None):
    """A clear lid exactly at the limit, closing the box: a faint neutral sheet (no tint, no refraction, casts no
    shadow). Its edge is the limit rim."""
    a, b = footprint[0] / 2, footprint[1] / 2
    cx, cy = centre
    veil = LID_VEIL if veil is None else veil
    lid = mesh_object("lid", [(cx - a, cy - b, height), (cx + a, cy - b, height), (cx + a, cy + b, height),
                              (cx - a, cy + b, height)], [(0, 1, 2, 3)], [veil_material("lid", veil)])
    no_shadow(lid)
    return [lid]


def box_corners(footprint=FOOTPRINT, centre=(0.0, 0.0)):
    a, b = footprint[0] / 2, footprint[1] / 2
    cx, cy = centre
    return [Vector((cx + sx * a, cy + sy * b, 0.0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def silhouette_corners(direction, footprint=FOOTPRINT, centre=(0.0, 0.0)):
    """(left, near, right) vertical box edges as seen from `direction` (xy positions at z=0)."""
    right = Vector((-direction.y, direction.x, 0.0)).normalized()   # camera's screen-right, for a level camera
    c = box_corners(footprint, centre)
    left_c = min(c, key=lambda p: p.dot(right))
    right_c = max(c, key=lambda p: p.dot(right))
    near_c = max(c, key=lambda p: p.dot(Vector((direction.x, direction.y, 0))))
    return left_c, near_c, right_c


def box_frame(height, width_units, rim_units, footprint=FOOTPRINT, centre=(0.0, 0.0), rim_strength=None,
              rim_colour=None):
    """Edge frame of the box: four vertical struts, and the top as a glowing rim exactly at `height` (the limit)."""
    a, b = footprint[0] / 2, footprint[1] / 2
    cx, cy = centre
    s, r = width_units / 2, rim_units / 2
    fm = material("frame", LOOK["frame"], rough=0.5, spec=0.5)
    rm = glow_material("limit_rim", rim_colour or LOOK["limit"], RIM_GLOW if rim_strength is None else rim_strength)
    obs = []
    for i, p in enumerate(box_corners(footprint, centre)):
        obs.append(cuboid(f"strut_{i}", (p.x - s, p.y - s, 0), (p.x + s, p.y + s, height - r), fm))
    obs.append(cuboid("rim_-y", (cx - a - r, cy - b - r, height - r), (cx + a + r, cy - b + r, height + r), rm))
    obs.append(cuboid("rim_+y", (cx - a - r, cy + b - r, height - r), (cx + a + r, cy + b + r, height + r), rm))
    obs.append(cuboid("rim_-x", (cx - a - r, cy - b + r, height - r), (cx - a + r, cy + b - r, height + r), rm))
    obs.append(cuboid("rim_+x", (cx + a - r, cy - b + r, height - r), (cx + a + r, cy + b - r, height + r), rm))
    for ob in obs[4:]:
        ob.visible_shadow = False
    return obs


# ---------------------------------------------------------------- the diorama base, sized from what stands on it
def floating_base(lo, hi, margin=0.2, seed=11, dressing=True, drop=None, thickness=None):
    """A floating slab of circuit board under the bounding box lo..hi (xy), a margin of `margin` x the larger
    side all round, with a tapered, rough low-poly underside. drop / thickness override the underside depth and
    the board thickness (by default proportional to the larger side, which suits a square base; a long row needs
    them set). Returns (objects, base_info)."""
    rnd = random.Random(seed)
    w, d = hi.x - lo.x, hi.y - lo.y
    big = max(w, d)
    m = margin * big
    X0, X1, Y0, Y1 = lo.x - m, hi.x + m, lo.y - m, hi.y + m
    top = lo.z
    t = thickness if thickness is not None else 0.035 * (big + 2 * m)       # board thickness
    if drop is None:
        drop = 0.55 * (big + 2 * m)                 # depth of the rough underside (deep enough to show below the board)
    obs = [cuboid("base_board", (X0, Y0, top - t), (X1, Y1, top),
                  [material("pcb", LOOK["pcb"], rough=0.6), material("pcb_edge", LOOK["pcb_edge"], rough=0.8)],
                  [1, 0, 1, 1, 1, 1])]
    # underside: rings of the outline, shrinking and jittered, closed at the bottom
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    hw, hd = (X1 - X0) / 2, (Y1 - Y0) / 2
    n_side = 3

    def outline(scale, jit, z, zj):
        pts = []
        for k in range(4 * n_side):
            side, f = divmod(k, n_side)
            u = -1 + 2 * f / n_side
            x, y = [(u, -1), (1, u), (-u, 1), (-1, -u)][side]
            jx, jy = rnd.uniform(-jit, jit), rnd.uniform(-jit, jit)
            pts.append(Vector((cx + (x * scale + jx) * hw, cy + (y * scale + jy) * hd, z + rnd.uniform(-zj, zj) * drop)))
        return pts

    rings = [outline(0.985, 0.0, top - t, 0.0),
             outline(0.90, 0.04, top - t - 0.25 * drop, 0.03),
             outline(0.64, 0.07, top - t - 0.60 * drop, 0.05),
             outline(0.28, 0.06, top - t - 0.88 * drop, 0.03)]
    verts = [p for r in rings for p in r] + [Vector((cx + rnd.uniform(-0.05, 0.05) * hw, cy, top - t - drop))]
    N = 4 * n_side
    faces = []
    for r in range(len(rings) - 1):
        for k in range(N):
            a0, a1 = r * N + k, r * N + (k + 1) % N
            b0, b1 = a0 + N, a1 + N
            faces += [(a0, b0, b1), (a0, b1, a1)]      # triangles: crisp facets
    tip = len(verts) - 1
    last = (len(rings) - 1) * N
    faces += [(last + k, tip, last + (k + 1) % N) for k in range(N)]
    obs.append(mesh_object("base_underside", verts, faces, [material("rock", LOOK["rock"], rough=0.9)]))
    info = {"x": (X0, X1), "y": (Y0, Y1), "top": top, "margin": m, "thickness": t, "drop": drop}
    if dressing:
        obs += pcb_dressing(info, lo, hi, rnd)
    return obs, info


def pcb_dressing(info, lo, hi, rnd):
    """Light 'graphics card' dressing on the board's margin: edge contacts, memory-chip packages, capacitors.
    All of it low (under 12% of the margin) so it hides nothing."""
    (X0, X1), (Y0, Y1), top, m = info["x"], info["y"], info["top"], info["margin"]
    chip, metal = material("chip", LOOK["chip"], rough=0.55), material("metal", LOOK["metal"], rough=0.35, spec=0.6)
    pad = material("pad", "#3a4049", rough=0.6)
    obs = []
    # edge contacts along the -y edge of the board, with the key notch
    L = X1 - X0
    n, fw, gap = 22, 0.020 * L, 0.012 * L
    x = X0 + 0.5 * (L - n * fw - (n - 1) * gap)
    for i in range(n):
        if i not in (7,):
            obs.append(cuboid(f"contact_{i}", (x, Y0 + 0.04 * m, top), (x + fw, Y0 + 0.40 * m, top + 0.012 * m), metal))
        x += fw + gap
    # memory packages on the +x margin
    for k, f in enumerate((0.22, 0.62)):
        cy = Y0 + f * (Y1 - Y0)
        c0 = (hi.x + 0.22 * m, cy - 0.30 * m, top)
        obs.append(cuboid(f"chip_{k}", c0, (hi.x + 0.72 * m, cy + 0.30 * m, top + 0.07 * m), chip))
        obs.append(cuboid(f"chip_pad_{k}", (c0[0] - 0.03 * m, c0[1] - 0.03 * m, top), (hi.x + 0.75 * m, cy + 0.33 * m, top + 0.01 * m), pad))
    # a row of capacitors on the +x margin, toward the back
    for k in range(4):
        cx, cy, r, h = hi.x + 0.86 * m, Y0 + (0.80 + 0.045 * k) * (Y1 - Y0), 0.055 * m, 0.11 * m
        verts = [Vector((cx + r * math.cos(2 * math.pi * j / 8), cy + r * math.sin(2 * math.pi * j / 8), top + z)) for z in (0, h) for j in range(8)]
        faces = [tuple(range(7, -1, -1)), tuple(range(8, 16))] + [(j, (j + 1) % 8, 8 + (j + 1) % 8, 8 + j) for j in range(8)]
        obs.append(mesh_object(f"cap_{k}", verts, faces, [metal]))
    # small parts on the -y margin, between the contacts and the box
    for k in range(5):
        px = lo.x + (0.12 + 0.18 * k) * (hi.x - lo.x)
        py = Y0 + 0.62 * m + rnd.uniform(-0.05, 0.05) * m
        obs.append(cuboid(f"smd_{k}", (px, py, top), (px + 0.16 * m, py + 0.09 * m, top + 0.04 * m), chip))
    return obs


# ---------------------------------------------------------------- camera
def view_direction(elevation_deg, azimuth_deg):
    """Unit vector from the scene toward the camera. Azimuth 0 = looking from -y; positive turns toward +x."""
    el, az = math.radians(elevation_deg), math.radians(azimuth_deg)
    return Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))


def make_camera(scene, lens):
    cd = bpy.data.cameras.new("Camera")
    cd.lens = lens
    cam = bpy.data.objects.new("Camera", cd)
    scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


def aim(cam, target, dist, direction):
    cam.location = target + direction.normalized() * dist
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_start = dist / 1000.0
    cam.data.clip_end = dist * 10.0
    bpy.context.view_layer.update()


def to_screen(scene, cam, p):
    """World point -> (x, y, depth); x, y in 0..1 of the picture from the bottom left."""
    return world_to_camera_view(scene, cam, Vector(p))


def frame_size(scene, cam, depth):
    """World width and height of the picture at this depth in front of the camera."""
    tr, br, bl, tl = cam.data.view_frame(scene=scene)
    k = depth / -tr.z
    return (tr.x - bl.x) * k, (tr.y - bl.y) * k


def to_world(scene, cam, sx, sy, depth):
    tr, br, bl, tl = cam.data.view_frame(scene=scene)
    k = depth / -tr.z
    local = Vector(((bl.x + (tr.x - bl.x) * sx) * k, (bl.y + (tr.y - bl.y) * sy) * k, -depth))
    return cam.matrix_world @ local


def mesh_points(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in objs:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        pts += [ob.matrix_world @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    return pts


def silhouette(scene, cam, objs, bins=900):
    """Left and right extent of the objects on screen, per horizontal band: (lo[], hi[], bins)."""
    rx, ry = scene.render.resolution_x, scene.render.resolution_y
    lo, hi = [None] * bins, [None] * bins
    dg = bpy.context.evaluated_depsgraph_get()
    for ob in objs:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        wp = [ob.matrix_world @ v.co for v in me.vertices]
        sp = [to_screen(scene, cam, p) for p in wp]
        for e in me.edges:
            i, j = e.vertices
            n = 2 + int(max(abs(sp[i].x - sp[j].x) * rx, abs(sp[i].y - sp[j].y) * ry))
            for k in range(n + 1):
                p = to_screen(scene, cam, wp[i].lerp(wp[j], k / n))
                b = int(p.y * bins)
                if 0 <= b < bins:
                    lo[b] = p.x if lo[b] is None else min(lo[b], p.x)
                    hi[b] = p.x if hi[b] is None else max(hi[b], p.x)
        ev.to_mesh_clear()
    return lo, hi, bins


def _band(sil, y0, y1):
    lo, hi, bins = sil
    xs_lo = [lo[b] for b in range(max(0, int(y0 * bins)), min(bins, int(y1 * bins) + 1)) if lo[b] is not None]
    xs_hi = [hi[b] for b in range(max(0, int(y0 * bins)), min(bins, int(y1 * bins) + 1)) if hi[b] is not None]
    return (min(xs_lo) if xs_lo else None), (max(xs_hi) if xs_hi else None)


# ---------------------------------------------------------------- labels with leaders
class Label:
    """Text beside the chart with a leader line to an anchor point. side 'L' or 'R'."""

    def __init__(self, key, text, anchor, side, sub=None):
        """sub: optional secondary lines, set under the main line in smaller, dimmer type."""
        self.key, self.text, self.anchor, self.side, self.sub = key, text, Vector(anchor), side, list(sub or [])
        cu = bpy.data.curves.new(f"label_{key}", "FONT")
        cu.body = text
        cu.align_x = "RIGHT" if side == "L" else "LEFT"
        cu.align_y = "CENTER"
        cu.size = 1.0
        cu.extrude = 0.0
        self.obj = bpy.data.objects.new(f"label_{key}", cu)
        bpy.context.scene.collection.objects.link(self.obj)
        bpy.context.view_layer.update()
        self.w_em = self.obj.dimensions.x            # width in ems
        self.h_em = self.obj.dimensions.y
        self.sub_obj, self.sub_w_em, self.sub_h_em = None, 0.0, 0.0
        if self.sub:
            cs = bpy.data.curves.new(f"label_{key}_sub", "FONT")
            cs.body = "\n".join(self.sub)
            cs.align_x = cu.align_x
            cs.align_y = "TOP"
            cs.size = 1.0
            cs.extrude = 0.0
            self.sub_obj = bpy.data.objects.new(f"label_{key}_sub", cs)
            bpy.context.scene.collection.objects.link(self.sub_obj)
            bpy.context.view_layer.update()
            self.sub_w_em, self.sub_h_em = self.sub_obj.dimensions.x, self.sub_obj.dimensions.y


def layout_labels(scene, cam, labels, sil, em=EM, gap_em=2.2, sep_em=1.75):
    """Screen layout: each label at its anchor's height, pushed apart where they would collide, in one column per
    side clear of the silhouette. Returns {key: dict(ax, ay, depth, x, y, w, h, route)} in picture fractions."""
    rx, ry = scene.render.resolution_x, scene.render.resolution_y
    em_y = em * rx / ry
    out = {}
    for lab in labels:
        a = to_screen(scene, cam, lab.anchor)
        o = {"ax": a.x, "ay": a.y, "depth": a.z, "y": a.y, "w": lab.w_em * em, "h": em_y, "below": 0.0}
        if lab.sub_obj:                                  # secondary lines hang under the main line
            o["below"] = SUB_GAP * em_y + lab.sub_h_em * SUB_EM * rx / ry
            o["w"] = max(o["w"], lab.sub_w_em * SUB_EM)
        out[lab.key] = o
    for side in ("L", "R"):
        labs = sorted([l for l in labels if l.side == side], key=lambda l: -out[l.key]["ay"])
        ys = [out[l.key]["ay"] for l in labs]
        for _ in range(500):
            moved = False
            for i in range(len(ys) - 1):
                sep = sep_em * em_y + out[labs[i].key]["below"]
                g = ys[i] - ys[i + 1]
                if g < sep - 1e-9:
                    ys[i] += (sep - g) / 2
                    ys[i + 1] -= (sep - g) / 2
                    moved = True
            if not moved:
                break
        col = None
        for l, y in zip(labs, ys):
            o = out[l.key]
            o["y"] = y
            xl, xh = _band(sil, min(y - o["below"], o["ay"]) - 0.6 * em_y, max(y, o["ay"]) + 0.6 * em_y)
            edge = (xl if side == "L" else xh)
            if edge is None:
                edge = o["ax"]
            edge = min(edge, o["ax"]) if side == "L" else max(edge, o["ax"])
            col = edge if col is None else (min(col, edge) if side == "L" else max(col, edge))
        for l in labs:
            o = out[l.key]
            sgn = -1 if side == "L" else 1
            o["x"] = col + sgn * gap_em * em            # label's inner edge
            pad, stub = 0.45 * em, 0.8 * em
            end = o["x"] - sgn * pad
            if abs(o["y"] - o["ay"]) < 0.002:
                o["route"] = [(o["ax"], o["ay"]), (end, o["ay"])]
                o["y"] = o["ay"]
            else:
                p1 = (o["ax"] + sgn * stub, o["ay"])
                p2x = p1[0] + sgn * min(abs(o["y"] - o["ay"]) * ry / rx * 1.0, abs(end - p1[0]) * 0.8)
                o["route"] = [(o["ax"], o["ay"]), p1, (p2x, o["y"]), (end, o["y"])]
            o["sub_y"] = o["y"] - o["h"] / 2 - SUB_GAP * em_y      # top of the secondary lines
            o["x0"] = o["x"] - o["w"] if side == "L" else o["x"]
            o["x1"] = o["x"] if side == "L" else o["x"] + o["w"]
    return out


def frame_scene(scene, cam, objs, direction, labels=(), fill=0.88, edge=0.035, iters=10):
    """Camera distance and aim from the bounding box of what was built (guide: whole scene in frame with a small
    margin, spanning about 85-90% of the width or height). Labels count as part of the scene; their size is fixed
    on screen, so only the geometry scales with distance. Returns the final label layout."""
    pts = mesh_points(objs)
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    target = (lo + hi) / 2
    fov = 2 * math.atan(cam.data.sensor_width / 2 / cam.data.lens)
    dist = (hi - lo).length / 2 / math.tan(fov / 2) * 1.2
    lay = {}
    for _ in range(iters):
        aim(cam, target, dist, direction)
        sp = [to_screen(scene, cam, p) for p in pts]
        gx0, gx1 = min(p.x for p in sp), max(p.x for p in sp)
        gy0, gy1 = min(p.y for p in sp), max(p.y for p in sp)
        x0, x1, y0, y1 = gx0, gx1, gy0, gy1
        if labels:
            sil = silhouette(scene, cam, objs)
            lay = layout_labels(scene, cam, labels, sil)
            for o in lay.values():
                x0, x1 = min(x0, o["x0"]), max(x1, o["x1"])
                y0, y1 = min(y0, o["y"] - o["h"] / 2 - o["below"]), max(y1, o["y"] + o["h"] / 2)
        gw, gh = gx1 - gx0, gy1 - gy0
        ox, oy = (x1 - x0) - gw, (y1 - y0) - gh                  # what the labels add, fixed on screen
        z = min((fill - ox) / gw, (fill - oy) / gh, (1 - 2 * edge - ox) / gw, (1 - 2 * edge - oy) / gh)
        fw, fh = frame_size(scene, cam, dist)
        R = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
        U = cam.matrix_world.to_3x3() @ Vector((0, 1, 0))
        target = target + R * ((x0 + x1) / 2 - 0.5) * fw + U * ((y0 + y1) / 2 - 0.5) * fh
        if abs(z - 1) < 0.002 and abs((x0 + x1) / 2 - 0.5) < 0.002 and abs((y0 + y1) / 2 - 0.5) < 0.002:
            break
        dist /= z
    aim(cam, target, dist, direction)
    if labels:
        lay = layout_labels(scene, cam, labels, silhouette(scene, cam, objs))
    return lay


def build_labels(scene, cam, labels, lay, em=EM, lift=0.0):
    """Text objects facing the camera, leader lines and anchor dots, from a layout_labels() layout. lift brings
    them that far toward the camera (in front of the struts they are anchored on) without moving them on screen."""
    ink = glow_material("ink", LOOK["ink"], 1.0)
    ink2 = glow_material("ink_secondary", LOOK["ink2"], 1.0)
    lead = glow_material("leader", LOOK["leader"], 1.0)
    rot = cam.matrix_world.to_quaternion()
    built = []
    for lab in labels:
        o = lay[lab.key]
        o["depth"] -= lift
        fw, _ = frame_size(scene, cam, o["depth"])
        ob = lab.obj
        ob.data.size = em * fw
        ob.location = to_world(scene, cam, o["x"], o["y"], o["depth"])
        ob.rotation_euler = rot.to_euler()
        ob.data.materials.clear()
        ob.data.materials.append(ink)
        no_shadow(ob)
        if lab.sub_obj:
            so = lab.sub_obj
            so.data.size = SUB_EM * fw
            so.location = to_world(scene, cam, o["x"], o["sub_y"], o["depth"])
            so.rotation_euler = rot.to_euler()
            so.data.materials.clear()
            so.data.materials.append(ink2)
            no_shadow(so)
            built.append(so)
        # leader
        cu = bpy.data.curves.new(f"leader_{lab.key}", "CURVE")
        cu.dimensions = "3D"
        sp = cu.splines.new("POLY")
        pts = [to_world(scene, cam, x, y, o["depth"]) for x, y in o["route"]]
        sp.points.add(len(pts) - 1)
        for p, c in zip(sp.points, pts):
            p.co = (c.x, c.y, c.z, 1.0)
        cu.bevel_depth = LINE * fw / 2
        cu.bevel_resolution = 1
        cu.materials.append(lead)
        lo = bpy.data.objects.new(f"leader_{lab.key}", cu)
        scene.collection.objects.link(lo)
        no_shadow(lo)
        # dot at the anchor
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=DOT * fw / 2)
        me = bpy.data.meshes.new(f"dot_{lab.key}")
        bm.to_mesh(me)
        bm.free()
        me.materials.append(lead)
        do = bpy.data.objects.new(f"dot_{lab.key}", me)
        do.location = pts[0]
        scene.collection.objects.link(do)
        no_shadow(do)
        built += [ob, lo, do]
    bpy.context.view_layer.update()
    return built


# ---------------------------------------------------------------- lights
def sun(name, direction_to_light, strength, colour=(1, 1, 1), angle_deg=2.0):
    ld = bpy.data.lights.new(name, "SUN")
    ld.energy = strength
    ld.color = colour
    ld.angle = math.radians(angle_deg)
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = (-direction_to_light.normalized()).to_track_quat("-Z", "Y").to_euler()
    return ob


def stage_lights(direction, key=3.2, rim=2.0, key_turn=60, key_el=20, rim_turn=140, rim_el=32):
    """One low key sun from the camera's left-front and a dimmer rim sun from behind on the right (guide).
    key_turn / rim_turn: degrees from the camera's horizontal direction toward its left / around behind."""
    dh = Vector((direction.x, direction.y, 0)).normalized()
    right = Vector((-dh.y, dh.x, 0))

    def d(turn, el, side):
        t = math.radians(turn)
        h = dh * math.cos(t) + side * right * math.sin(t)
        return Vector((h.x * math.cos(math.radians(el)), h.y * math.cos(math.radians(el)), math.sin(math.radians(el))))

    return [sun("key", d(key_turn, key_el, -1), key, (1.0, 0.97, 0.93)),
            sun("rim", d(rim_turn, rim_el, +1), rim, (0.72, 0.82, 1.0))]


def point_glow(name, location, colour, power, radius):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = power
    ld.color = _rgb(colour)
    ld.shadow_soft_size = radius
    ob = bpy.data.objects.new(name, ld)
    ob.location = location
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ---------------------------------------------------------------- checks and output
def occlusion_check(scene, cam, labels, lay, exclude_prefixes=("label_", "leader_", "dot_", "lid")):
    """Rays from the camera to points on each label and leader: anything else in the way is reported (the clear
    lid does not count)."""
    dg = bpy.context.evaluated_depsgraph_get()
    origin = cam.matrix_world.translation
    bad = []
    for lab in labels:
        o = lay[lab.key]
        samples = [(x, y) for x, y in o["route"]]
        for fx in (0.0, 0.5, 1.0):
            for fy in (-0.4, 0.0, 0.4):
                samples.append((o["x0"] + fx * (o["x1"] - o["x0"]), o["y"] + fy * o["h"]))
            if o["below"]:
                for fb in (0.3, 0.95):
                    samples.append((o["x0"] + fx * (o["x1"] - o["x0"]), o["y"] - o["h"] / 2 - fb * o["below"]))
        for sx, sy in samples:
            p = to_world(scene, cam, sx, sy, o["depth"])
            v = p - origin
            hit, loc, nor, idx, ob, mtx = scene.ray_cast(dg, origin, v.normalized(), distance=v.length * 0.995)
            if hit and not ob.name.startswith(exclude_prefixes):
                bad.append({"label": lab.key, "at": [round(sx, 3), round(sy, 3)], "hidden_by": ob.name})
    return bad


def label_overlaps(lay):
    keys, out = list(lay), []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = lay[a], lay[b]
            a_lo, a_hi = A["y"] - A["h"] / 2 - A.get("below", 0), A["y"] + A["h"] / 2
            b_lo, b_hi = B["y"] - B["h"] / 2 - B.get("below", 0), B["y"] + B["h"] / 2
            if A["x0"] < B["x1"] and B["x0"] < A["x1"] and a_lo < b_hi and b_lo < a_hi:
                out.append([a, b])
    return out


def object_height(ob):
    lo, hi = world_bbox([ob])
    return hi.z - lo.z


def sample_colours(png, scene, cam, points, r=2):
    """Average sRGB colour of the rendered picture around projected world points {name: point}."""
    img = bpy.data.images.load(png)
    w, h = img.size
    px = list(img.pixels)
    out = {}
    for name, p in points.items():
        s = to_screen(scene, cam, p)
        cx, cy = int(s.x * w), int(s.y * h)
        acc, n = [0.0, 0.0, 0.0], 0
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if 0 <= x < w and 0 <= y < h:
                    i = (y * w + x) * 4
                    for c in range(3):
                        acc[c] += px[i + c]
                    n += 1
        rgb = [a / max(n, 1) for a in acc]
        out[name] = {"px": [cx, h - 1 - cy], "hex": "#" + "".join(f"{int(round(min(1, max(0, c)) * 255)):02x}" for c in rgb)}
    bpy.data.images.remove(img)
    return out


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)


# ---------------------------------------------------------------- reuse: the card from the VRAM figure
def build_card(data, direction, strut=0.168, rim=0.180, glow_light=False):
    """The approved VRAM figure's card (vram_gguf.py, draft 4 build) without labels or camera: layers to scale,
    two back walls, struts, the quiet limit rim, the clear lid, the circuit-board base. Built at the origin in
    its own units (strut / rim default to the sizes of the approved 2400x1600 render). Returns its objects."""
    layers, card_mib = data["layers_bottom_to_top"], data["card_total_mib"]
    mats = {
        "driver": material("card_driver", COLOURS["driver"], emit=0.10, rough=0.85, spec=0.12),
        "weights": material("card_weights", COLOURS["weights"], emit=0.10, rough=0.85, spec=0.12),
        "context": glow_material("card_context", COLOURS["context"], 1.35),
        "working": material("card_working", COLOURS["working"], emit=0.12, rough=0.85, spec=0.12),
    }
    stack = stack_layers(layers, mats)
    box_h = layer_height(card_mib)
    walls = back_walls(box_h, direction)
    volumes = [s["obj"] for s in stack if s["obj"]] + walls
    lo, hi = world_bbox(volumes)
    base, _ = floating_base(lo, hi)
    obs = volumes + base + box_frame(box_h, strut, rim) + clear_lid(box_h)
    if glow_light:
        ctx = next(s for s in stack if s["key"] == "context")
        _, near_c, _ = silhouette_corners(direction)
        out_h = Vector((direction.x, direction.y, 0)).normalized()
        obs.append(point_glow("card_context_glow", near_c + out_h * 0.22 * FOOTPRINT[0]
                              + Vector((0, 0, (ctx["z0"] + ctx["z1"]) / 2)), COLOURS["context"], 120.0, 0.5))
    return obs


# ---------------------------------------------------------------- free-standing text (no leader)
def text_object(name, body, align_x="CENTER", align_y="CENTER"):
    """A flat text object of size 1 in the built-in font; returns (object, width, height) in ems."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.align_x, cu.align_y = align_x, align_y
    cu.size, cu.extrude = 1.0, 0.0
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    return ob, ob.dimensions.x, ob.dimensions.y


def place_on_screen(scene, cam, ob, sx, sy, depth, size_frac, mat=None):
    """Puts a camera-facing flat object (text, swatch) at picture position sx, sy (0..1 from the bottom left),
    at this depth, sized as a fraction of the picture's width."""
    fw, _ = frame_size(scene, cam, depth)
    if ob.type == "FONT":
        ob.data.size = size_frac * fw
    else:
        ob.scale = (size_frac * fw,) * 3
    ob.location = to_world(scene, cam, sx, sy, depth)
    ob.rotation_euler = cam.matrix_world.to_quaternion().to_euler()
    if mat is not None:
        ob.data.materials.clear()
        ob.data.materials.append(mat)
    no_shadow(ob)


def swatch_object(name, colour):
    """A unit square that shows `colour` exactly (emission 1, Standard view): for legends."""
    ob = mesh_object(name, [(-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.5, 0.5, 0)], [(0, 1, 2, 3)],
                     [glow_material(name, colour, 1.0)])
    no_shadow(ob)
    return ob


def polyline(name, pts, radius, mat):
    """A thin round line through world points (for zoom guides and other annotation), invisible to light."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (c[0], c[1], c[2], 1.0)
    cu.bevel_depth, cu.bevel_resolution = radius, 1
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    no_shadow(ob)
    return ob


def taper_prism(name, xa, xb, ha, hb, zc, y0, y1, mat):
    """A block from x=xa to x=xb whose height tapers linearly from ha to hb, centred on z=zc, between y0 and y1."""
    v = [(xa, y0, zc - ha / 2), (xb, y0, zc - hb / 2), (xb, y0, zc + hb / 2), (xa, y0, zc + ha / 2),
         (xa, y1, zc - ha / 2), (xb, y1, zc - hb / 2), (xb, y1, zc + hb / 2), (xa, y1, zc + ha / 2)]
    f = [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (3, 2, 6, 7), (0, 3, 7, 4), (1, 5, 6, 2)]
    return mesh_object(name, v, f, [mat])
