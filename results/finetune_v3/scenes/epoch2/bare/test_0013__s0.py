import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1058)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def paint(name, rgb, glow=0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .8
    n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    n.inputs["Alpha"].default_value = alpha
    M[name] = m
for k, v in dict(cliff=(.22, .2, .24), cliff2=(.14, .13, .17), steel=(.28, .3, .34), steel2=(.15, .16, .2), rock=(.3, .27, .27),
                 red=(.6, .08, .06), bench=(.45, .25, .12), white=(.7, .7, .75), cloud=(.55, .6, .75), cloud2=(.4, .45, .65)).items(): paint(k, v)
paint("glass", (.3, .8, 1), glow=1.5, alpha=.35); paint("lamp", (1, .6, .2), glow=25); paint("sign", (1, .5, .1), glow=12)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("w"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("w", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(M[m]); return o
def bar(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def block(m, at, s, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def spike(m, at, r1, r2, h, n=5, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def puff(m, at, r, sq=.55):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.9, 1.2), v.co.y * random.uniform(.9, 1.2), v.co.z * sq))
    return make(bm, m, at)
def shine(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# cliff mass: a sheer rock wall at the back, a ledge at the front, and a deep ragged underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
make(bm, "cliff2")
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 20, v.co.y * 10, (v.co.z + .5) * 9))
    if v.co.z > 4: v.co.y += random.uniform(-.6, .6); v.co.x += random.uniform(-.8, .8)
make(bm, "cliff", (0, 7.5, -4.5))
for i in range(8):
    spike("rock", (-9 + i * 2.6 + random.uniform(-.5, .5), 2.4 + random.uniform(-.4, .4), -4.5), random.uniform(.8, 1.4), .2, random.uniform(1.5, 3), 5)
for i in range(5): block("rock", (random.uniform(-8, 8), random.uniform(2.5, 3.5), 0), (random.uniform(.8, 1.6), random.uniform(.8, 1.4), random.uniform(.4, .9)), rot=(0, 0, random.uniform(0, 3)))
# the glass walkway: frame beams, glowing glass panels, steel railing
for i in range(7):
    x = 1.0 + i * 1.5
    block("steel2", (x, -4.5, 0), (1.5, 3.4, .2)); block("glass", (x, -4.5, .2), (1.4, 3.2, .15))
for x in (1.0, 10.0): block("steel", (x, -4.5, 0), (.3, 3.4, .3))
for y in (-6.1, -2.9): block("steel", (5.5, y, 0), (9.3, .3, .3))
for i in range(11):
    x = 1.2 + i * .9
    for y in (-6.1, -2.9): bar("steel", (x, y, .3), (x, y, 1.6), .08)
for y in (-6.1, -2.9): bar("steel", (1.2, y, 1.6), (10.8, y, 1.6), .12); bar("steel", (1.2, y, 1.0), (10.8, y, 1.0), .07)
for x in (1.2, 10.8): bar("steel", (x, -6.1, .3), (x, -2.9, 1.6), .1)
for x in (3.0, 6.5, 9.5):
    for y in (-6.1, -2.9):
        bar("steel2", (x, y, 1.6), (x, y, 2.6), .1); block("lamp", (x, y, 2.6), (.4, .4, .4))
        shine("POINT", (1, .6, .2), 160, (x, y - .4, 2.9))
block("steel", (10.8, -4.5, .3), (.3, .3, .3))
# ticket gate on the ledge: two posts, arms, booth and sign
for y in (-6.6, -2.4):
    block("red", (0.0, y, 0), (.5, .5, 1.5), top=.8); block("white", (0.0, y, 1.5), (.7, .7, .25))
    bar("white", (.0, y, 1.1), (.6, y, 1.1), .1)
block("steel2", (-3.0, -5.0, 0), (2.4, 2.0, 2.4)); block("sign", (-3.0, -3.95, 1.2), (1.8, .1, .8))
block("steel", (-3.0, -5.0, 2.4), (2.8, 2.4, .25)); block("lamp", (-3.0, -5.0, 2.65), (1.2, 1.2, .15))
shine("POINT", (1, .5, .1), 250, (-3.0, -4.0, 3.2))
block("steel2", (6.5, -3.4, .3), (1.8, .6, .45)); block("bench", (6.5, -3.4, .75), (1.9, .5, .12))
for i in range(3): block("bench", (3.8 + i * .9, -5.4, .3), (.5, .5, .4))
# sea of cloud below: layered banks, some drifting out over the void
for i in range(16):
    x, y = random.uniform(-11, 11), random.uniform(-11, 6)
    if x * x + y * y > 160: continue
    puff("cloud" if i % 2 else "cloud2", (x, y, -7.2 + random.uniform(-.5, .5)), random.uniform(2.0, 3.4))
for i in range(5): puff("cloud", (random.uniform(-6, 6), random.uniform(-9, -5), -6.2), random.uniform(1.6, 2.2))
for i in range(4): puff("cloud2", (random.uniform(-9, 9), random.uniform(3, 7), -5.5), random.uniform(1.2, 2.0))
# dusk: rose key from the left, cold violet rim from behind the cloud
shine("SUN", (1, .5, .4), 5, (-26, -20, 11), (0, 0, 0)); shine("SUN", (.4, .5, 1), 2.2, (24, 24, 10), (0, 0, 0))
w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .05, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((1, -1, 0)); co.location = t + Vector((16, -62, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
