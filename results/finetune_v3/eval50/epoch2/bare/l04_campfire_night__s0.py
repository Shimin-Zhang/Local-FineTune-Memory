import bpy, bmesh, math, random
from mathutils import Vector
random.seed(497)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def stuff(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
moss, soil, pine, bark, rockm, log, iron, ember, flame, flame2 = (stuff((.04, .1, .05)), stuff((.07, .05, .04)), stuff((.03, .12, .08)), stuff((.14, .08, .05)),
    stuff((.16, .15, .17)), stuff((.2, .12, .07)), stuff((.04, .04, .05), 0, .4), stuff((1, .2, .02), 10), stuff((1, .5, .08), 16), stuff((1, .85, .2), 22))
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, d, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * k, v.co.y * d[1] * k, (v.co.z + .5) * d[2]))
    return put(bm, m, at, (0, 0, rz))
def rod(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return put(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at)
def pebble(at, r, m, sq=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.8, 1.2), v.co.y * random.uniform(.8, 1.2), v.co.z * sq))
    return put(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: mossy forest floor, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=10, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
put(bm, moss)
for i in range(7): blk((random.uniform(-1, 1), random.uniform(-1, 1), .0), (random.uniform(2, 3.4), random.uniform(2, 3), .08), soil, random.random() * 3)
# fire pit: ring of stones, logs, flames
for i in range(9):
    a = i * math.tau / 9; pebble((math.cos(a) * 1.6, math.sin(a) * 1.6, .1), random.uniform(.4, .6), rockm, .7)
for i in range(5):
    a = i * 1.25; rod((math.cos(a) * 1.1, math.sin(a) * 1.1, .35), (math.cos(a + math.pi) * .2, math.sin(a + math.pi) * .2, .6), .16, log)
cone((0, 0, .3), 1.0, .15, 7, ember, .8)
for i, (dx, dy, h, r, m) in enumerate(((0, 0, 2.6, .9, flame), (.4, .2, 1.8, .6, flame2), (-.4, -.1, 1.9, .6, flame2), (.1, -.4, 1.4, .45, flame))):
    cone((dx, dy, .4), r, h, 6, m, .02)
lamp("POINT", (1, .45, .08), 1500, (0, 0, 1.4)); lamp("POINT", (1, .5, .1), 500, (0, 0, 3))
# grill pot on three legs over the flames
for i in range(3):
    a = i * math.tau / 3; rod((math.cos(a) * .75, math.sin(a) * .75, .5), (math.cos(a) * .15, math.sin(a) * .15, 1.9), .05, iron)
cone((0, 0, 1.9), .55, .45, 7, iron, .5)
# camp chairs and a log bench
for sx in (-1, 1):
    for sy in (-1, 1): rod((-3.6 + sx * .6, -2.2 + sy * .6, 0), (-3.6 + sx * .1, -2.2 + sy * .6, 1.1), .06, log)
    blk((-3.6, -2.2, 1.0), (1.3, 1.3, .15), bark); blk((-3.6, -1.55, 1.1), (1.3, .15, 1.0), bark)
rod((-1.5, -3.6, .55), (1.5, -3.6, .55), .28, log)
# lantern post and a pack
rod((4.2, -2.6, 0), (4.2, -2.6, 2.6), .08, log); blk((4.2, -2.6, 2.6), (.5, .5, .6), flame2, 0, .8)
lamp("POINT", (1, .6, .15), 250, (4.2, -2.6, 2.9))
blk((3.2, 1.2, 0), (1.2, .9, .8), bark, .4); blk((3.2, 1.2, .8), (1.0, .7, .1), log, .4)
# trees: dark pines ring the back and sides
for i, (x, y, s) in enumerate(((-8, 4, 1.3), (-5, 7.5, 1.5), (-1, 8.5, 1.4), (3, 8, 1.6), (7, 5.5, 1.3), (8.5, 1, 1.1), (-8.5, 0, 1.2), (-7, -5, 1.0), (6.5, -6.5, 1.0), (-3, -8, 1.1))):
    cone((x, y, 0), .3 * s, 1.6 * s, 5, bark, .25 * s)
    for k in range(3): cone((x, y, 1.2 * s + k * 1.4 * s), (2.1 - k * .55) * s, 2.0 * s, 7, pine, .1)
for i in range(12):
    x, y = random.uniform(-8, 8), random.uniform(-8, 8)
    if math.hypot(x, y) > 2.2 and math.hypot(x + 3.6, y + 2.2) > 2 and math.hypot(x - 4, y + 2.6) > 1.5: pebble((x, y, .1), random.uniform(.2, .5), rockm, .6)
lamp("SUN", (.3, .4, .9), 2.2, (-16, -12, 8), (0, 0, 1))
lamp("SUN", (.2, .3, .8), 1.4, (14, 16, 9), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.004, .008, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((14, -40, 25))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
