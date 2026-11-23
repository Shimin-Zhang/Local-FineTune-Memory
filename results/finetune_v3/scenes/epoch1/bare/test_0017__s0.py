import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1644)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, glow=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
grass, grass2, ashlar, ashlar2, roof, roof2, earth, wood, iron, window = (tone(c) for c in (
    (.1, .2, .08), (.07, .14, .07), (.42, .38, .3), (.32, .29, .24), (.2, .1, .1), (.15, .12, .13), (.22, .15, .1), (.25, .15, .08), (.06, .06, .07), (1, .7, .25)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, d, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * k, v.co.y * d[1] * k, (v.co.z + .5) * d[2]))
    return mk(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0.0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def glow(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14.5, depth=4)
for v in bm.verts:
    v.co.x *= 1.05; v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
mk(bm, grass)
cone((0, 0, 0), 14.3, .06, 10, grass2)
# the round church: drum, conical roof, lantern, door, windows, buttresses
cone((0, 0, .1), 3.4, 4.2, 12, ashlar); cone((0, 0, 4.3), 3.5, .35, 12, ashlar2, 3.5)
cone((0, 0, 4.6), 3.7, 3.8, 12, roof, .5)
cone((0, 0, 8.4), .8, 1.2, 8, ashlar, .6); cone((0, 0, 9.6), .95, 1.5, 8, roof2, .05)
box((0, 0, 9.6), (.1, .1, 1.6), iron); box((0, 0, 10.5), (.5, .1, .1), iron)
box((0, -3.5, .1), 1.5, 1.2, 3.2, wood); box((0, -3.4, 3.3), 1.1, .8, 3.2, ashlar2)
for i in range(8):
    a = i * math.pi / 4 + math.pi / 8
    box((3.2 * math.cos(a), 3.2 * math.sin(a), 1.6), (.5, .15, 1.5), window, (0, 0, a + math.pi / 2))
    box((3.7 * math.cos(a), 3.7 * math.sin(a), .1), (.8, .8, 2.4), ashlar2, (0, 0, a + math.pi / 2), .8)
glow("POINT", (1, .7, .25), 300, (0, -4.5, 2.0))
# the chancel: small rectangular nave, pitched roof, apse, door, windows
box((0, 7.2, .1), 3.4, 5.2, 3.2, ashlar)
bm = bmesh.new(); p = [bm.verts.new(c) for c in ((-1.9, -3.1, 0), (1.9, -3.1, 0), (1.9, 3.1, 0), (-1.9, 3.1, 0), (-1.9, 0, 1.8), (1.9, 0, 1.8))]
for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 1, 2, 3)): bm.faces.new([p[i] for i in f])
mk(bm, roof, (0, 7.2, 3.3))
cone((0, 10.2, .1), 1.7, 2.6, 8, ashlar); cone((0, 10.2, 2.7), 1.8, 1.6, 8, roof, .1)
box((0, 4.4, .1), 1.1, .2, 2.6, wood); box((0, 4.4, 2.9), .8, .2, 1.2, window)
for sx in (-1, 1):
    for y in (6.0, 8.4): box((sx * 1.72, y, 1.3), (.15, .5, 1.3), window, (0, 0, 0))
glow("POINT", (1, .7, .25), 200, (0, 3.8, 2.0))
# ring of low stone buildings around the church, one left out for the gate
for i in range(13):
    a = math.radians(25 + i * 25.3); r = 10.0
    x, y = r * math.cos(a), r * math.sin(a)
    if i == 11: continue
    box((x, y, .1), 3.6, 2.6, 2.2 + random.uniform(-.2, .3), ashlar if i % 2 else ashlar2, .95, (0, 0, a + math.pi / 2))
    bm = bmesh.new(); q = [bm.verts.new(c) for c in ((-2.0, -1.5, 0), (2.0, -1.5, 0), (2.0, 1.5, 0), (-2.0, 1.5, 0), (-2.0, 0, 1.1), (2.0, 0, 1.1))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 1, 2, 3)): bm.faces.new([q[i] for i in f])
    mk(bm, roof2 if i % 2 else roof, (x, y, 2.3 + random.uniform(-.2, .3)), (0, 0, a + math.pi / 2))
    dx, dy = math.cos(a), math.sin(a)
    box((x - dx * 1.2, y - dy * 1.2, 1.0), (.7, .12, .8), window, (0, 0, a + math.pi / 2))
    box((x + dx * 1.2, y + dy * 1.2, .1), (.7, .12, 1.3), wood, (0, 0, a + math.pi / 2))
    if i % 3 == 0: glow("POINT", (1, .7, .25), 140, (x - dx * 1.7, y - dy * 1.7, 1.4))
# the gate: two stone piers, lintel, iron bars, a lamp
for sx in (-1, 1):
    box((sx * 2.4, -10.4, .1), 1.2, 1.4, 3.0, ashlar, .9); box((sx * 2.4, -10.4, 3.1), 1.5, 1.7, .3, ashlar2)
box((0, -10.4, 2.6), 4.8, 1.0, .45, ashlar)
for i in range(9): box((-1.9 + i * .48, -10.4, .1), (.1, .1, 2.6), iron)
box((0, -10.4, 1.0), 4.0, .1, .1, iron)
box((0, -10.4, 3.4), (.5, .5, .5), window); glow("POINT", (1, .7, .25), 400, (0, -10.4, 3.6))
# path, steps and a few trees
box((0, -7.0, .05), 1.6, 5.6, .05, earth)
for k in range(3): box((0, -3.6 + k * .3, .05), 1.8, .3, .12 + k * .12, ashlar2)
for x, y in ((-11, 3), (11, 4), (-9, -7), (9, -7)):
    cone((x, y, 0), .25, 1.6, 5, wood, .2); cone((x, y, 1.2), 1.5, 2.4, 6, grass2, .1); cone((x, y, 2.8), 1.0, 1.8, 6, grass2, .05)
glow("SUN", (1, .72, .45), 5, (-28, -20, 12), (0, 0, 2)); glow("SUN", (.4, .5, .9), 2.2, (24, 28, 14), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((-10, -52, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
