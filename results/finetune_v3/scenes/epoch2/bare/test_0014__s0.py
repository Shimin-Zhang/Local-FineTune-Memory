import bpy, bmesh, random, math
from mathutils import Vector
random.seed(349)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def flat(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("f"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
sand, sea, road, curb, post, timber, roofm, white, red, lampm, pebble, weed = (
    flat((.22, .2, .17)), flat((.04, .12, .17), rough=.1), flat((.2, .2, .22)), flat((.35, .35, .36)), flat((.1, .1, .12)), flat((.3, .2, .12)), flat((.3, .1, .1)), flat((.7, .7, .68)),
    flat((.8, .1, .08)), flat((1, .7, .25), 16), flat((.25, .24, .24)), flat((.1, .2, .1)))
def solid(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return solid(bm, m, at, rot)
def stick(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return solid(bm, m)
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return solid(bm, m, at, rot)
def mound(at, r, m, sq=.4):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return solid(bm, m, at)
def beam(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.7
solid(bm, sand)
slab((-6.5, 0, 0), (9, 22, .25), sea); slab((12.5, 0, 0), (3, 22, .25), sea)
for i in range(14): mound((-11 + random.uniform(-1, 1), random.uniform(-10, 10), .1), random.uniform(.5, 1.1), pebble, .5)
# the causeway: kerbed paving, a little below the tide level, so the water laps over it
for i in range(14):
    x = -11 + i * 1.5
    slab((x, 0, 0), (1.5, 3.6, .3), road if i % 2 else curb, (0, 0, 0))
    for s in (-1, 1): slab((x, s * 2.1, 0), (1.5, .35, .55), curb)
slab((-2.5, 0, .28), (7, 3.6, .06), sea); slab((5.5, 0, .28), (3, 3.6, .06), sea)
for i in range(18):
    x, y = random.uniform(-9, 8), random.choice((-1, 1)) * random.uniform(1.0, 1.8)
    slab((x, y, .3), (.5, .3, .03), sea, (0, 0, random.uniform(0, 3)))
# marker poles along the kerb: white with a red band and a lamp on the last few
for i in range(11):
    x = -10 + i * 2.0; s = -1 if i % 2 else 1
    stick((x, s * 2.5, 0), (x, s * 2.5, 2.4), .16, white); stick((x, s * 2.5, 1.6), (x, s * 2.5, 2.1), .2, red)
    if i >= 7:
        drum((x, s * 2.5, 2.4), .22, .35, 6, lampm); beam("POINT", (1, .7, .25), 160, (x, s * 2.5, 2.9))
# the island: shingle mound with a refuge hut on stilts and a ladder
mound((7.5, 0, 0), 4.5, pebble, .35); mound((7.5, 0, .1), 3.2, sand, .3)
for sx in (-1, 1):
    for sy in (-1, 1): stick((7.5 + sx * 1.5, sy * 1.2, 0), (7.5 + sx * 1.5, sy * 1.2, 2.4), .22, timber)
slab((7.5, 0, 2.4), (4, 3.2, .25), timber)
slab((7.5, 0, 2.65), (3.2, 2.6, 2.0), white); slab((7.5, -1.32, 3.0), (1.0, .1, .8), lampm)
drum((7.5, 0, 4.65), 2.8, 1.4, 4, roofm, .3, (0, 0, math.pi / 4)).scale = (1.0, .8, 1)
for i in range(7): slab((6.0, -.6, .3 + i * .35), (.1, .9, .1), timber)
stick((6.0, -.2, 0), (6.0, -.2, 2.7), .1, timber); stick((6.0, -1.0, 0), (6.0, -1.0, 2.7), .1, timber)
beam("POINT", (1, .7, .25), 400, (7.5, -2.2, 3.4))
for i in range(5): mound((7.5 + random.uniform(-2.5, 2.5), random.uniform(-3, 3), .2), random.uniform(.3, .6), weed, .8)
# a stranded boat turned upside down, and a crab pot or two
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 3.2, v.co.y * 1.3, v.co.z * .8))
    if v.co.x > 0: v.co.y *= .3
    if v.co.z > 0: v.co.y *= .6
solid(bm, timber, (-9, -5.5, .4), (0, 0, .4)); slab((-9, -5.5, .8), (3, .1, .1), timber, (0, 0, .4))
for x, y in ((-4, 5), (-1, 6.2)): drum((x, y, 0), .45, .6, 7, red, .4); stick((x, y, .6), (x, y, 1.1), .06, post)
beam("SUN", (1, .55, .35), 5, (-26, -10, 8), (0, 0, 1)); beam("SUN", (.3, .6, .8), 2.2, (22, 18, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .03, .045, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((-6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
