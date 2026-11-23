import bpy, bmesh, random, math
from mathutils import Vector
random.seed(501)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
moss, pine, stone, bark, flame, core, log, cloth, iron, rock = (tint(c) for c in (
    (.07, .13, .06), (.04, .1, .06), (.25, .24, .24), (.17, .1, .06), (1, .3, .03, ), (1, .75, .2), (.3, .17, .09), (.45, .12, .08), (.08, .08, .09), (.12, .12, .13)))
flame = tint((1, .3, .03), 14); core = tint((1, .75, .2), 22)
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    o.data.materials.append(m); sc.collection.objects.link(o); return o
def cone(at, r1, r2, h, n, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, at, rot)
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mesh(bm, m, at, rot)
def pebble(at, r, m, flat=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= flat
    return mesh(bm, m, at)
def log(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return mesh(bm, m)
def spark(kind, rgb, w, at, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5.5, radius2=9.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .3)))
mesh(bm, moss)
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(2.5, 8)
    pebble((math.cos(a) * r, math.sin(a) * r, 0), random.uniform(.5, 1.1), moss if i % 2 else rock, .3)
for i in range(10):
    a = i * math.pi / 5 + .2; pebble((math.cos(a) * 1.5, math.sin(a) * 1.5, 0), .4, stone, .7)
for i in range(4):
    a = i * math.pi / 2 + .4; log((math.cos(a) * 1.2, math.sin(a) * 1.2, .15), (math.cos(a + math.pi) * 1.0, math.sin(a + math.pi) * 1.0, .55), .17, log)
cone((0, 0, .3), .9, .1, 1.7, 6, flame, (0, 0, .5)); cone((.3, .2, .3), .5, .05, 1.2, 5, core, (0, 0, 2)); cone((-.4, -.2, .3), .45, .05, 1.0, 5, core, (0, 0, 4))
for i in range(3):
    a = i * 2.1 + .7; log((math.cos(a) * 1.9, math.sin(a) * 1.9, .15), (math.cos(a) * .8, math.sin(a) * .8, .5), .22, log)
for i in range(3):
    a = i * 2.1 + 1.8; log((math.cos(a) * 2.0, math.sin(a) * 2.0, .15), (math.cos(a) * .7, math.sin(a) * .7, .5), .22, log)
for i, (x, y) in enumerate(((-3.4, -2.6), (3.4, -2.8), (0, 3.8))):
    log((x, y, 0), (x, y, .5), .2, bark); log((x, y, .5), (x, y, 1.5), .15, bark)
    cone((x, y, 1.5), 1.1, .05, 2.6, 6, pine)
    cone((x, y, .1), .55, .55, .12, 6, cloth if i != 1 else log)
slab((-3.4, -2.6, .5), (.9, .9, .1), cloth); slab((3.4, -2.8, .5), (.9, .9, .1), log); slab((0, 3.8, .5), (.9, .9, .1), cloth)
slab((3.4, -2.8, .62), (.5, .5, .1), iron); slab((-3.4, -2.6, .62), (.4, .3, .12), iron)
log((.3, .2, .6), (.3, .2, 1.2), .06, iron); slab((.3, .2, 1.2), (.15, .15, .1), iron)
for x, y, h in ((-6.5, 5, 5.5), (-4.5, 7, 6.5), (5.5, 6.5, 6), (7.5, 3, 5), (-8, 0, 4.5), (8, -2.5, 4)):
    cone((x, y, 0), .3, .3, 1.2, 5, bark)
    for k in range(3): cone((x, y, 1.0 + k * 1.5), 1.9 - k * .5, .1, 2.2, 6, pine)
for i in range(5):
    pebble((random.uniform(-9, 9), random.uniform(-9, -3), 0), random.uniform(.3, .6), rock, .8)
spark("POINT", (1, .45, .08), 2200, (0, 0, 1.2)); spark("POINT", (1, .6, .15), 700, (0, 0, 2.8))
spark("SUN", (.35, .5, .9), .8, (-24, -12, 8), (0, 0, 1)); spark("SUN", (.4, .35, .8), .5, (20, 20, 9), (0, 0, 1))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((7, -40, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
