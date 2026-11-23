import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1234)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def dye(name, rgb, em=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, c in (("sawdust", (.35, .24, .12)), ("canvas", (.55, .45, .3)), ("canvas2", (.4, .3, .2)), ("timber", (.22, .13, .07)), ("brass", (.7, .5, .12)),
             ("iron", (.06, .06, .07)), ("red", (.45, .08, .06)), ("green", (.1, .25, .15)), ("cream", (.6, .55, .4)), ("water", (.1, .3, .4)), ("dark", (.03, .02, .02))):
    dye(k, c)
dye("lantern", (1, .6, .2), 12); dye("fire", (1, .45, .1), 10); dye("gramo", (1, .75, .3), 6)
def make(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def box(at, d, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return make(bm, k, at, (0, 0, rz))
def drum(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, k, at, rot)
def beam(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, k)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
def chair(x, y, rz, k):
    c, s = math.cos(rz), math.sin(rz)
    at = lambda dx, dy, z: (x + dx * c - dy * s, y + dx * s + dy * c, z)
    for sx in (-1, 1):
        for sy in (-1, 1): beam(at(sx * .35, sy * .3, 0), at(sx * .35, sy * .3, .55), .06, "timber")
    box(at(0, 0, .5), (.8, .8, .08), k, rz); box(at(0, -.4, .55), (.8, .08, .7), k, rz)
# sawdust floor, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=13, depth=4)
for v in bm.verts:
    v.co.x *= 1.25
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.2, .3)))
    v.co.z -= 2
make(bm, "sawdust")
# the long dining tent: two pitched halves with a ridge, open at the ends
for sx in (-1, 1):
    for sy in (-1, 1): drum((sx * 10.5, sy * 3.4, 0), .16, 4.0, 5, "timber")
    beam((sx * 10.5, -3.4, 4.0), (sx * 10.5, 0, 5.4), .12, "timber"); beam((sx * 10.5, 3.4, 4.0), (sx * 10.5, 0, 5.4), .12, "timber")
    for sy in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
        for v in bm.verts: v.co = Vector((v.co.x * 21.4, v.co.y * 3.9, v.co.z * .08))
        make(bm, "canvas" if sy > 0 else "canvas2", (0, sy * 1.7, 4.7), (0, -sy * .55, 0))
beam((0, 0, 5.4), (0, 0, 5.4), .01, "timber"); beam((-10.6, 0, 5.4), (10.6, 0, 5.4), .2, "timber")
# long trestle table with cloth, plates, cups and candles
box((0, 0, 1.0), (12, 1.4, .12), "cream"); box((0, 0, .9), (12.2, 1.6, .1), "timber")
for x in (-5, 0, 5):
    for sy in (-.6, .6): beam((x, sy, 0), (x, sy, .9), .1, "timber")
for i in range(7):
    for sy in (-.85, .85):
        drum((-5 + i * 1.7, sy, 1.12), .22, .04, 7, "cream"); drum((-5 + i * 1.7, sy, 1.16), .1, .12, 5, "red" if i % 2 else "green")
for x in (-3, 0, 3): drum((x, 0, 1.12), .06, .3, 5, "lantern")
# lanterns hanging from the ridge, glowing
for x in (-6, -2, 2, 6):
    beam((x, 0, 5.3), (x, 0, 4.4), .03, "iron"); drum((x, 0, 3.9), .22, .5, 6, "lantern", .26); drum((x, 0, 4.4), .3, .12, 6, "brass", .05)
    glow((x, 0, 4.0), (1, .6, .2), 260)
# folding chairs round the table
for i in range(7):
    chair(-5.5 + i * 1.8, -2.0, 0, "red" if i % 2 else "green"); chair(-5.5 + i * 1.8, 2.0, math.pi, "green" if i % 2 else "red")
# gramophone on a side table with a big horn
drum((-8.5, 2.4, 0), .55, .9, 7, "timber"); drum((-8.5, 2.4, .9), .5, .12, 8, "brass")
drum((-8.5, 2.4, 1.0), .12, .5, 5, "brass", .45); beam((-8.5, 2.4, 1.5), (-7.6, 2.9, 2.2), .06, "brass"); drum((-7.5, 2.9, 2.1), .1, .1, 5, "gramo")
glow((-7.6, 2.9, 2.2), (1, .75, .3), 120)
# bath tub on legs with water and a basin
for sx in (-1, 1):
    for sy in (-1, 1): box((-3 + sx * .8, 7 + sy * .5, 0), (.16, .16, .5), "timber")
box((-3, 7, .5), (2.0, 1.3, .7), "cream"); box((-3, 7, 1.15), (1.7, 1.0, .08), "water")
drum((-1.5, 6.5, 0), .3, .5, 7, "brass"); beam((-1.5, 6.5, .5), (-2.0, 6.8, 1.0), .05, "brass")
# firewood, crates, a rope and a campfire
for i in range(6): beam((9, 7 + (i % 3) * .3, .15 + (i // 3) * .3), (11, 7 + (i % 3) * .3, .15 + (i // 3) * .3), .22, "timber")
box((7.5, -6.5, 0), (1.2, 1.0, .8), "timber"); box((8.8, -6.2, 0), (.9, .9, .6), "timber", .3)
for i in range(7):
    a = i * 6.283 / 7; drum((2 + math.cos(a) * .7, 7 + math.sin(a) * .7, 0), .22, .3, 5, "iron", .15)
drum((2, 7, .1), .4, .6, 5, "fire", .05); glow((2, 7, 1.0), (1, .45, .1), 500)
for i in range(4): box((-9 + i * .9, -7.5, 0), (.5, .5, .5 + (i % 2) * .2), "cream" if i % 2 else "red", i * .3)
# dusk: amber key low from the right, indigo rim from the back-left
for c, w, p in (((1, .55, .25), 5, (24, -14, 9)), ((.3, .4, .9), 2, (-20, 22, 10))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("sun", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dusk"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .012, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 2.5)); co.location = t + Vector((6, -60, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
