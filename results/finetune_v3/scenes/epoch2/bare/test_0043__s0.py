import bpy, bmesh, math, random
from mathutils import Vector
random.seed(802)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, em=0):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
moss, soil, leaf, leaf2, leaf3, trunk, bark, stone, toad, rope, cloth1, cloth2, bloom = (
    hue((.06, .15, .06)), hue((.12, .09, .06)), hue((.05, .3, .1)), hue((.1, .38, .12)), hue((.04, .22, .09)), hue((.2, .13, .09)), hue((.12, .08, .06)),
    hue((.45, .45, .42)), hue((.3, .45, .15)), hue((.5, .4, .25)), hue((.6, .2, .15)), hue((.15, .3, .5)), hue((1, .85, .4), 14))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def stalk(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r * .6, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return mk(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def leafy(at, r, m, sq=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mk(bm, m, at)
def glim(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# forest-floor base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
mk(bm, moss)
# wide-leaf bed: a dark soil patch ringed by big leaves
slab((-3.5, -1.5, 0), (7.5, 5.5, .25), soil, (0, 0, .2), .95)
for i in range(26):
    a = i * 2.4; r = random.uniform(2.2, 4.2)
    p = Vector((-3.5 + r * math.cos(a) * 1.1, -1.5 + r * math.sin(a) * .85, .2))
    h = random.uniform(1.0, 1.8)
    stalk(p, p + Vector((.1, .1, h)), .12, leaf3, 4)
    for k in range(3):
        b = a + k * 2.1 + random.uniform(-.3, .3)
        tip = p + Vector((math.cos(b) * 1.6, math.sin(b) * 1.6, h + random.uniform(.2, .8)))
        stalk(p + Vector((0, 0, h * .6)), tip, .5, (leaf, leaf2, leaf)[(i + k) % 3], 4)
        leafy(tip, .55, (leaf, leaf2, leaf3)[(i + k) % 3], .3)
# stepping-stone path winding from the front to the hammock
for i in range(9):
    t = i / 8; x = 1.5 + 3.5 * math.sin(t * 3) + 2 * t; y = -9 + t * 9.5
    slab((x, y, 0), (1.5, 1.1, .25), stone, (0, 0, i), .8)
# stone toad on a plinth by the path
slab((.2, -3.5, 0), (1.5, 1.2, .5), stone, (0, 0, .3), .8)
leafy((.2, -3.5, .9), .75, toad, .8)
for s in (-1, 1): leafy((.2 + s * .35, -3.9, 1.4), .22, toad, 1); leafy((.2 + s * .3, -3.1, 1.5), .2, toad, 1)
slab((.2, -4.0, 1.0), (.7, .1, .1), bark, (0, 0, 0))
# two old trees with buttress roots, canopy and hanging moss
for tx, ty, h in ((-8, 4, 8.5), (7.5, 6, 9)):
    stalk((tx, ty, 0), (tx + .6, ty, h), 1.1, trunk, 6)
    for k in range(5):
        a = k * 1.26; slab((tx + math.cos(a) * 1.2, ty + math.sin(a) * 1.2, 0), (1.4, .5, 1.6), bark, (0, 0, a + 1.57), .3)
    for k in range(5):
        a = k * 1.3; leafy((tx + math.cos(a) * 3.2, ty + math.sin(a) * 3.2, h + 1 + random.uniform(-.5, .8)), 2.4, (leaf, leaf2)[k % 2], .6)
    leafy((tx, ty, h + 2.5), 3, leaf2, .6)
    for k in range(4): stalk((tx + math.cos(k * 1.7) * 3, ty + math.sin(k * 1.7) * 3, h + .5), (tx + math.cos(k * 1.7) * 3, ty + math.sin(k * 1.7) * 3, h - 1.2), .06, leaf3, 3)
# hammock between the two trees, sagging in the middle
for sx, sy in ((-8, 3.2), (7.5, 5.2)):
    stalk((sx, sy, 0), (sx + .6, sy, 4.2), .15, bark, 4)
for i in range(11):
    t = i / 10; p = Vector((-8 + t * 15.5, 3.2 + t * 2, 4.2 - 1.6 * math.sin(t * math.pi)))
    if i: slab((p + prev) / 2, (1.8, 1.3, .12), cloth1 if i % 2 else cloth2, (0, 0, .12))
    prev = p
# glowing mushrooms and a lantern post by the path
for i, (x, y) in enumerate(((2.5, -5.5), (4.2, 1.5), (1.0, 4.5), (-1, -7))):
    stalk((x, y, 0), (x, y, .7), .08, stone, 4); leafy((x, y, .8), .4, bloom, .7)
    glim((x, y, 1.2), (1, .85, .4), 90)
stalk((3.8, -1.5, 0), (3.8, -1.5, 2.4), .1, bark, 5); leafy((3.8, -1.5, 2.6), .35, bloom, 1); glim((3.8, -1.5, 2.6), (1, .8, .4), 350)
for i in range(14):
    x, y = random.uniform(-11, 11), random.uniform(-10, 10)
    if math.hypot(x, y) < 11 and abs(x + 3.5) + abs(y + 1.5) > 4.5 and not (2 < x < 5 and -6 < y < 3): leafy((x, y, .1), random.uniform(.25, .5), (leaf, leaf2, leaf3)[i % 3], .6)
for c, w, p in (((.9, .85, .5), 4.5, (-24, -14, 14)), ((.4, .7, .8), 2.2, (22, 20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .03, .025, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 3.5)); co.location = tg + Vector((6, -52, 30))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
