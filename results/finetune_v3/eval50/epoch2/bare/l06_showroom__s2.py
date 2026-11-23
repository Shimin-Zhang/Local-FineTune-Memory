import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1555)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(c, e=0, r=.5, mt=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r; n.inputs["Metallic"].default_value = mt
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
tileA, tileB, red, glass, chrome, rubber, white, under = paint((.04, .045, .06), 0, .08), paint((.07, .08, .1), 0, .08), paint((.6, .03, .04), 0, .25, .3), paint((.02, .03, .05), 0, .05), paint((.7, .72, .75), 0, .3, .6), paint((.02, .02, .02)), paint((.9, .9, .92)), paint((.3, .8, 1), 12)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); me.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    return make(bm, m, at, rot)
def bar(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def shine(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 22, v.co.y * 16, v.co.z * 1.6))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z * 1.5 - random.uniform(0, 1.5)))
make(bm, tileA, (0, 0, -.8))
for i in range(11):
    for j in range(8): slab((-10 + i * 2, -7 + j * 2, 0), (1.96, 1.96, .06), tileA if (i + j) % 2 else tileB)
# the car: wedge body, cabin, glass, nose and tail lights, wheels, spoiler
slab((0, 0, .75), (6.2, 2.5, .9), red); slab((0, 0, 1.6), (6.2, 2.5, .12), red)
slab((.3, 0, 1.7), (3.0, 2.1, .85), red, (0, 0, 0))
slab((.3, 0, 2.0), (2.5, 1.9, .6), glass)
slab((-3.3, 0, 1.0), (.9, 2.3, .5), red, (0, -.12, 0)); slab((3.3, 0, 1.0), (.9, 2.3, .45), red, (0, .12, 0))
slab((-3.9, 0, 1.15), (.12, 1.8, .25), white); slab((3.9, 0, 1.15), (.12, 1.8, .2), red)
slab((0, 0, .62), (6.3, 2.55, .15), under)
for x in (-2.0, 2.0):
    for y in (-1.25, 1.25):
        drum((x, y, .75), .75, .5, 10, rubber, rot=(math.pi / 2, 0, 0)).location.y = y - (.25 if y > 0 else -.25)
        drum((x, y - (.25 if y > 0 else -.25), .75), .4, .55, 8, chrome, rot=(math.pi / 2, 0, 0))
bar((-1.4, -1.2, 2.3), (-1.4, 1.2, 2.3), .1, chrome)
# long soft lights overhead on a frame, and a cyan rim
for y in (-3.5, 0, 3.5):
    slab((0, y, 7.2), (10, .5, .35), white)
    for x in (-5, 5): bar((x, y, 0), (x, y, 7.2), .12, chrome)
    bar((-5, y, 7.2), (5, y, 7.2), .12, chrome)
for x in (-5, 5): bar((x, -3.5, 7.2), (x, 3.5, 7.2), .12, chrome)
shine("POINT", (.9, .95, 1), 2200, (0, -3.5, 6.5)); shine("POINT", (.9, .95, 1), 2200, (0, 0, 6.5)); shine("POINT", (.9, .95, 1), 2200, (0, 3.5, 6.5))
# back wall with a glowing strip and side panels
slab((0, 8, 0), (22, .6, 8), tileB); slab((-11, 0, 0), (.6, 16, 8), tileB)
slab((0, 7.6, 1.2), (14, .15, .5), under)
for i in range(5): slab((-8 + i * 4, 7.6, 3.5), (1.8, .15, 3.0), glass)
shine("POINT", (.3, .8, 1), 1200, (0, 6.5, 2.5))
# pedestal spotlights on the floor and a few showroom props
for x, y in ((-8, -5), (8, -5), (-8, 5), (8, 5)): drum((x, y, 0), .5, .5, 6, chrome); drum((x, y, .5), .35, .2, 6, white)
slab((-8, 0, 0), (2, 1.2, 1.2), tileA); slab((-8, 0, 1.2), (1.6, .9, .5), chrome)
shine("SUN", (.75, .85, 1), 4.5, (-24, -20, 12), (0, 0, 1)); shine("SUN", (1, .5, .6), 2.2, (22, 22, 10), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .012, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((14, -50, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
