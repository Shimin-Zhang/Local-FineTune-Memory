import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1071)
sc = bpy.context.scene
paints = {m.name: m for m in bpy.data.materials}
def paint(name, rgb, glow=0):
    if name in paints: return
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .8
    if glow:
        n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    paints[name] = m
for k, c, g in [("road", (.03, .035, .05), 0), ("puddle", (.02, .04, .07), 0), ("sidewalk", (.1, .1, .13), 0), ("stone", (.16, .15, .16), 0),
        ("brick", (.2, .07, .06), 0), ("brick2", (.13, .09, .11), 0), ("iron", (.02, .02, .03), 0), ("coat", (.08, .08, .12), 0),
        ("skin", (.55, .35, .26), 0), ("umbrella", (.6, .04, .07), 0), ("window", (1, .72, .35), 7), ("neon", (1, .1, .5), 14), ("neon2", (.1, .8, 1), 12),
        ("lamp", (1, .8, .45), 25), ("car", (.35, .05, .05), 0), ("tyre", (.02, .02, .02), 0), ("gold", (.7, .5, .1), 3), ("rain", (.5, .6, .9), 1.5)]:
    paint(k, c, g)
def mk(bm, key, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(key); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(key, me); o.location = loc; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(paints[key]); return o
def box(key, loc, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, key, loc, rot)
def bar(key, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, key)
def cyl(key, loc, r, h, n=6, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, key, loc, rot)
def ball(key, loc, r, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, key, loc)
def glow(col, w, loc):
    L = bpy.data.lights.new("g", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = loc; sc.collection.objects.link(o)
# floating base: wet road slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 28, v.co.y * 18, v.co.z * 2.4 - 1.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
mk(bm, "road", (0, 0, 0))
for x, y, rx, ry in [(-3, -4, 3, 1.6), (4, -6, 2.2, 1.2), (0, 2.5, 2.5, 1.0), (-8, -7, 1.5, 1.0), (8, 0, 1.8, 1.0)]:
    cyl("puddle", (x, y, .02), 1, .04, 8).scale = (rx, ry, 1)
# sidewalk, kerb and gutter along the back
box("sidewalk", (0, 5.5, 0), (28, 7, .5)); box("stone", (0, 1.8, 0), (28, .5, .35))
# four shopfronts: lit windows, neon signs, doors, fire escape, roof vents
for i, (x, w, key) in enumerate([(-9.5, 6, "brick"), (-3, 6, "brick2"), (3.5, 6, "brick"), (10, 5, "brick2")]):
    box(key, (x, 7.2, 0), (w, 3.2, 8.5)); box("stone", (x, 5.55, 0), (w, .15, .8))
    for j in range(2):
        box("window", (x - w / 4 + j * w / 2, 5.5, 1.0), (w / 2 - .5, .1, 2.6)); box("iron", (x - w / 4 + j * w / 2, 5.4, 1.0), (.15, .1, 2.7))
    box("iron", (x, 5.4, 3.6), (w - .3, .1, .12)); box("iron", (x, 5.4, 1.0), (w - .3, .1, .12))
    box("neon" if i % 2 else "neon2", (x, 5.4, 4.4), (w - 1.2, .12, .5))
    box("iron", (x + w / 2 - .9, 5.5, .0), (1.2, .1, 2.4)); box("lamp", (x + w / 2 - .9, 5.4, 1.0), (.6, .08, .8))
    glow((1, .72, .35), 260, (x, 3.5, 2.4))
    box("stone", (x, 7.2, 8.5), (w + .3, 3.5, .35))
    for k in range(3): box("iron", (x - w / 3 + k * w / 3, 7.2, 9.0), (.8, 2.4, 1.2))
for z in (1.5, 3.5, 5.5): box("iron", (-3, 5.2, z), (3.2, .12, .1))
for x in (-4.5, -3, -1.5): bar("iron", (x, 5.2, 1.4), (x, 5.2, 5.7), .08)
# the lamp post with arm and hanging lamp
px, py = -1.5, -1.0
cyl("iron", (px, py, 0), .35, 8.0, 6, .22); cyl("iron", (px, py, 0), .5, .4, 6)
bar("iron", (px, py, 8.0), (px + 2.4, py, 8.4), .2); bar("iron", (px + 2.4, py, 8.4), (px + 2.4, py, 7.9), .08)
cyl("lamp", (px + 2.4, py, 7.2), .55, .7, 6, .3); cyl("iron", (px + 2.4, py, 7.9), .35, .1, 6)
glow((1, .8, .45), 900, (px + 2.4, py - .5, 7.6))
# the swinging man: arm raised to the wire, torso, trailing legs, umbrella in the other hand
mx, my, mz = px + 1.0, py - 1.2, 5.2
bar("coat", (px, py, 8.0), (mx, my, mz + 1.6), .22)
bar("coat", (mx, my, mz + 1.6), (mx + .2, my - .3, mz + 2.3), .22)
bar("coat", (mx, my, mz + 1.6), (mx - 1.2, my - .2, mz + .2), .3)
bar("skin", (mx - 1.2, my - .2, mz + .2), (mx - 1.9, my - .3, mz + .1), .2)
ball("skin", (mx - 2.1, my - .3, mz + .1), .3)
bar("coat", (mx - 1.2, my - .2, mz), (mx - 1.6, my - .6, mz - 1.6), .22)
bar("coat", (mx - 1.2, my - .2, mz), (mx - .6, my - .1, mz - 1.7), .22)
bar("iron", (mx - 1.6, my - .6, mz - 1.6), (mx - 1.6, my - .6, mz - 1.9), .3)
bar("iron", (mx - .6, my - .1, mz - 1.7), (mx - .6, my - .1, mz - 2.0), .3)
bar("iron", (mx - 1.2, my - .2, mz + 1.2), (mx - 2.4, my - 1.0, mz - 1.2), .07)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.1, radius2=1.5, depth=.9)
for v in bm.verts: v.co.z -= .45
mk(bm, "umbrella", (mx - 2.4, my - 1.0, mz - 1.2))
# parked car with glowing windshield and wheels, hydrant, a manhole cover, bins
box("car", (7.5, -5.5, .4), (4.2, 1.9, .9)); box("car", (7.5, -5.5, 1.3), (2.2, 1.6, .7)); box("window", (7.5, -5.5, 1.5), (2.0, 1.7, .4))
for sx in (-1.4, 1.4):
    for sy in (-1.0, 1.0): cyl("tyre", (7.5 + sx, -5.5 + sy * .95, .4), .45, .3, 8, rot=(1.57, 0, 0))
cyl("car", (11.5, 1.5, 0), .35, .9, 6, .3); cyl("iron", (11.5, 1.5, .9), .1, .3, 5)
cyl("iron", (-6, -3, .02), .8, .06, 8)
for bx in (-11, -10): cyl("iron", (bx, 3.2, .5), .3, .8, 6)
# night rain: thin pale streaks slanting down over the whole street
for i in range(70):
    x, y, z = random.uniform(-13, 13), random.uniform(-8, 10), random.uniform(2, 14)
    bar("rain", (x, y, z), (x + .5, y + .15, z - 1.6), .035)
# lights: cold blue key from the left, magenta neon rim from behind
for col, e, p in [((.45, .55, 1), 4.5, (-30, -22, 12)), ((.9, .25, .7), 2.2, (24, 28, 14))]:
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 4)); co.location = t + Vector((-16, -66, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
