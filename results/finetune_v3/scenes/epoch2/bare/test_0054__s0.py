import bpy, bmesh, math, random
from mathutils import Vector
random.seed(967)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, em=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .8
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
grass, paving, granite, dark, pool, flame, path = col((.08, .15, .09)), col((.3, .3, .32)), col((.42, .4, .4)), col((.12, .12, .14)), col((.04, .16, .22), .6), col((1, .5, .12), 9), col((.5, .46, .4))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def ring(at, r, w, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def lamp(at, rgb, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5.5, radius2=12, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.05, .05)
    v.co.z -= 1.5
mk(bm, grass)
ring((0, 0, 0), 10.2, 1.4, .1, 10, paving)
# wide steps: three tiers rising toward the rings
for k, (r, h) in enumerate(((9.0, .3), (8.2, .6), (7.4, .9))): ring((0, 0, 0), r, 1.0, h, 10, paving)
# concentric stone rings, each carved with names as dark slots
for k, (r, h) in enumerate(((6.6, 1.1), (5.6, 1.4), (4.6, 1.7))):
    ring((0, 0, .9), r, .75, h, 10, granite)
    for i in range(20):
        a = i * math.pi / 10 + k * .15
        blk((math.cos(a) * (r - .02), math.sin(a) * (r - .02), .9 + h * .35), (.3, .12, .22), dark, (0, 0, a + math.pi / 2))
# central pool and flame
ring((0, 0, .9), 3.6, .5, .5, 10, granite); ring((0, 0, 1.2), 3.1, .4, .1, 10, pool)
ring((0, 0, 1.2), 1.2, .5, .6, 8, dark); ring((0, 0, 1.8), .55, .3, 1.0, 6, flame, .05)
lamp((0, 0, 3.0), (1, .5, .12), 1400)
# quiet paths between the rings and around the pool, stepping stones
for k in range(10):
    a = k * math.pi / 5 + .3
    for r in (5.0, 3.9, 2.4): blk((math.cos(a) * r, math.sin(a) * r, .9), (.7, .6, .06), path, (0, 0, a))
for k in range(8):
    a = k * math.pi / 4
    blk((math.cos(a) * 9.8, math.sin(a) * 9.8, .1), (1.0, 1.0, .12), path, (0, 0, a))
# low benches and a few trees outside
for k in range(5):
    a = k * math.pi * 2 / 5 + .5
    blk((math.cos(a) * 10.8, math.sin(a) * 10.8, 0), (1.6, .5, .5), paving, (0, 0, a + math.pi / 2))
for k in range(7):
    a = k * math.pi * 2 / 7 + .3; r = random.uniform(10.2, 11.2)
    x, y = math.cos(a) * r, math.sin(a) * r
    ring((x, y, 0), .22, .18, 2.2, 5, col((.2, .13, .08)))
    for j in range(2):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.2 - j * .35)
        for v in bm.verts: v.co *= random.uniform(.85, 1.1)
        mk(bm, col((.06, .17, .1)), (x, y, 2.4 + j * .8))
# a small sign post on the steps
blk((4.4, -4.2, .9), (.1, .1, 1.4), dark); blk((4.4, -4.2, 1.9), (.8, .08, .5), path)
for rgb, w, at in (((.6, .75, 1), 4.5, (-22, -12, 8)), ((.9, .55, .4), 2, (20, 18, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1)); co.location = t + Vector((6, -50, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
