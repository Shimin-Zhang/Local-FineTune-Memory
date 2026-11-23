import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1824)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(rgb, em=0, rough=.8):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
oak, oak2, red, white, steam, coal, brass, dark = (paint(c, rough=r) for c, r in (((.22, .12, .07), .7), ((.16, .08, .05), .7), ((.62, .05, .05), .25), ((.8, .78, .72), .5), ((.9, .95, 1), 1.2, .9), ((.03, .03, .03), .9), ((.6, .4, .1), .3), ((.04, .03, .03), .9)))
def piece(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def drum(r1, r2, h, n=8, jit=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts:
        v.co.z += h / 2
        if jit: v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit)))
    return bm
def rod(a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return bm
def lump(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return piece(bm, m, at, rot)
def puff(at, r, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r); return piece(bm, m, at)
def glow(at, rgb, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# floating oak slab
bm = drum(4.5, 9, 2.4, 9, .35)
for v in bm.verts:
    if v.co.z < 0: v.co.z += random.uniform(-.5, .3)
piece(bm, oak2, (0, 0, -1.2))
for i in range(5): lump((0, -3.6 + i * 1.8, 0), (9.2, 1.7, .12), oak if i % 2 else oak2)
# the mug: red body, white rim, white handle, dark coffee
piece(drum(2.0, 1.7, 3.6, 8), red, (0, 0, .12)); piece(drum(1.85, 1.85, .25, 8), white, (0, 0, 3.72))
piece(drum(1.65, 1.65, .12, 8), coal, (0, 0, 3.6)); piece(drum(1.9, 1.9, .3, 8), white, (0, 0, .0))
for i in range(5):
    a = i * 2 * math.pi / 5 + .3; p = Vector((2.0 * math.cos(a), 2.0 * math.sin(a), 2.6))
    q = Vector((2.0 * math.cos(a + 2 * math.pi / 5 + .3), 2.0 * math.sin(a + 2 * math.pi / 5 + .3), 2.6)); piece(rod(p, q, .3), white)
for i in range(5):
    a = i * 2 * math.pi / 5; piece(rod((2.0 * math.cos(a), 2.0 * math.sin(a), 3.4), (2.0 * math.cos(a + 1.256), 2.0 * math.sin(a + 1.256), 3.4), .12), white)
for i in range(7):
    a = -1.2 + i * .4; p = Vector((2.1 * math.cos(a), 2.1 * math.sin(a), 1.2 + 1.2 * math.sin(a + 1.2) * .9 + .5))
    q = Vector((2.1 * math.cos(a + .4), 2.1 * math.sin(a + .4), 1.2 + 1.2 * math.sin(a + 1.6) * .9 + .5)); piece(rod(p, q, .35), white)
# steam: glowing puffs rising in a spiral
for i in range(7):
    t = i / 6; a = i * 1.1; puff((1.2 * math.cos(a) * t, 1.2 * math.sin(a) * t, 4.4 + i * .9), .45 + .1 * i, steam)
glow((0, 0, 6.5), (1, .95, .8), 900)
# a brass spoon, a saucer with crumbs, a book and a candle
piece(drum(3.0, 2.6, .3, 8), white, (5.2, -1.5, 0)); piece(drum(2.4, 2.4, .08, 8), red, (5.2, -1.5, .3))
lump((6.6, -3.4, 0), (.9, .25, .12), brass, (0, 0, .5)); lump((6.9, -3.3, .12), (.5, .4, .1), brass, (0, 0, .5))
lump((-5.5, 2.5, 0), (3.2, 2.2, .3), red, (0, 0, .4)); lump((-5.5, 2.5, .3), (3.0, 2.0, .3), white, (0, 0, .4)); lump((-5.4, 2.5, .6), (2.8, 1.8, .25), oak2, (0, 0, .4))
piece(drum(.3, .3, 1.2, 6), white, (-4.8, -3.6, 0)); piece(drum(.2, .05, .5, 5), brass, (-4.8, -3.6, 1.2)); piece(drum(.1, .02, .4, 4), steam, (-4.8, -3.6, 1.7)); glow((-4.8, -3.6, 2.2), (1, .7, .3), 160)
for i in range(4): lump((random.uniform(-1, 3), random.uniform(-4, 0), 0), (.25, .2, .15), white, (0, 0, i))
# lights: warm key from the left, cool rim from behind
for c, w, p in (((1, .72, .45), 5, (-16, -12, 10)), ((.4, .6, 1), 2.2, (14, 16, 8))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .015, .02, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((8, -34, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
