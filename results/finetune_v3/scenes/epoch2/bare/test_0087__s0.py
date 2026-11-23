import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1711)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
paints = {}
def dye(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    paints[name] = m
for k, v in dict(moss=(.08, .16, .08), moss2=(.12, .2, .1), flag=(.25, .27, .26), flag2=(.18, .2, .2), granite=(.3, .3, .32),
                 water=(.08, .2, .25), plank=(.3, .17, .08), timber=(.2, .1, .06), roof=(.1, .13, .15),
                 cap=(.22, .24, .24), leaf=(.05, .2, .1), bark=(.15, .1, .08)).items(): dye(k, v)
dye("lamp", (1, .6, .2), 14); dye("rain", (.7, .85, 1), 2.5); dye("stone", (.35, .38, .38))
def add(bm, key, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(key); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(key, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(paints[key]); return o
def box(key, at, s, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * f, v.co.y * s[1] * f, (v.co.z + .5) * s[2]))
    return add(bm, key, at, rot)
def post(key, at, r, h, n=5, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, key, at, rot)
def rock(key, at, r, sq=(1, 1, .7)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.85, 1.15)
    return add(bm, key, at)
def glow(at, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = (1, .6, .2); L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
add(bm, "moss")
# stream across the front, with a plank bridge
box("water", (0, -6.5, .05), (24, 3.2, .1))
for i in range(14):
    box("plank", (-2.6 + i * .4, -6.5, .15), (.34, 2.2, .12), rot=(0, 0, random.uniform(-.04, .04)))
for sy in (-1, 1):
    for sx in (-2.7, 2.7):
        post("timber", (sx, -6.5 + sy * 1.1, 0), .1, 1.3, 5)
    box("timber", (0, -6.5 + sy * 1.1, .95), (6, .12, .12))
# the path: stone slabs climbing to the gate
for i in range(11):
    box("flag" if i % 2 else "flag2", (random.uniform(-.2, .2), -4.5 + i * 1.7, 0), (2.4, 1.5, .12 + i * .03), rot=(0, 0, random.uniform(-.06, .06)))
for i in range(5):
    box("flag2", (random.uniform(-.2, .2), 14.5 + i * 1.7, 0), (2.4, 1.5, .12 + i * .03))
# stone lanterns either side of the path
def lantern(x, y, s):
    post("granite", (x, y, 0), .5 * s, .3 * s, 6)
    post("granite", (x, y, .3 * s), .16 * s, 1.1 * s, 6)
    box("granite", (x, y, 1.4 * s), (.8 * s, .8 * s, .12 * s))
    box("lamp", (x, y, 1.55 * s), (.5 * s, .5 * s, .55 * s))
    post("cap", (x, y, 2.1 * s), .75 * s, .5 * s, 6, .1 * s)
    post("cap", (x, y, 2.6 * s), .12 * s, .2 * s, 5)
    glow((x, y, 1.9 * s), 140)
for y in (-2.5, 2.5, 7.5, 12.5):
    lantern(-3.2, y, 1.0); lantern(3.2, y, 1.0)
# the wooden gate with a tiled roof
for sx in (-1, 1):
    post("timber", (sx * 2.4, 13.5, 0), .3, 4.2, 6)
    box("timber", (sx * 2.4, 13.5, 0), (1.0, 1.0, .3))
box("timber", (0, 13.5, 3.9), (7, .3, .3)); box("timber", (0, 13.5, 3.0), (5, .2, .2)); box("timber", (0, 13.5, 1.0), (5, .2, .2))
box("roof", (0, 13.5, 4.2), (8.6, 2.6, .35), top=.8)
for sy in (-1, 1):
    box("roof", (0, 13.5 + sy * 1.3, 4.2), (8.6, .3, .3))
    for sx in (-1, 1): box("roof", (sx * 4.2, 13.5 + sy * 1.3, 4.5), (.3, .3, .3))
for i in range(5): box("roof", (-3.2 + i * 1.6, 13.5, 4.55), (.2, 2.4, .15))
# shrine hall behind the gate
box("timber", (0, 20, 0), (7, 4, 2.8), top=.98)
box("roof", (0, 20, 2.8), (9.2, 6, .4), top=.8)
box("lamp", (0, 17.95, .5), (1.2, .1, 1.8)); glow((0, 17, 1.5), 300)
for sx in (-1, 1): post("timber", (sx * 2.2, 17.8, 0), .15, 2.6, 5)
# mossy boulders, trees
for i in range(18):
    a = random.uniform(0, 6.28); r = random.uniform(9, 12.5)
    rock("stone" if i % 2 else "moss2", (math.cos(a) * r, math.sin(a) * r * .95, .1), random.uniform(.5, 1.2))
for x, y in ((-8, 6), (8.5, 8), (-9, 14), (9, 15), (-7, -2), (7, -1)):
    post("bark", (x, y, 0), .35, 2.4, 5, .25)
    for j in range(3): rock("leaf", (x + random.uniform(-.6, .6), y + random.uniform(-.6, .6), 2.6 + j * .7), 1.6 - j * .4, (1, 1, .8))
# light rain
for i in range(70):
    x, y, z = random.uniform(-12, 12), random.uniform(-12, 12), random.uniform(2, 12)
    box("rain", (x, y, z), (.04, .04, 1.3), rot=(0, .2, 0))
for key, w, p, c in (("a", 4, (-24, -12, 9), (.6, .8, 1)), ("b", 2.2, (16, 20, 10), (.5, .9, .7))):
    L = bpy.data.lights.new(key, "SUN"); L.energy = w; L.color = c
    o = bpy.data.objects.new(key, L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("rain"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .03, .035, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 85; cm.clip_end = 400
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
aim = Vector((0, 5, 3)); co.location = aim + Vector((22, -56, 36))
co.rotation_euler = (aim - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
