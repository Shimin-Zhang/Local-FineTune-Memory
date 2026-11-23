import bpy, bmesh, math, random
from mathutils import Vector
random.seed(596)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, em=0):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
moss, bark, plank, rope, frond, mist, lamp, soil, leaf2 = (hue(c) for c in (
    (.05, .15, .06), (.22, .13, .08), (.38, .22, .11), (.4, .33, .2), (.04, .2, .08), (.55, .65, .7), (.9, .65, .25), (.06, .05, .04), (.08, .26, .1)))
lampm = hue((1, .6, .2), 14)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, d, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return add(bm, m, at, rot)
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return add(bm, m)
def trunk(at, r, h, m, lean=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=r, radius2=r * .7, depth=h)
    for v in bm.verts: v.co.z += h / 2; v.co.x += lean * v.co.z
    return add(bm, m, at)
def puff(at, r, m, sq=.5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return add(bm, m, at)
def frond(at, m, s=1):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=.9 * s, radius2=.05, depth=3.2 * s)
    for v in bm.verts: v.co.z -= 1.6 * s; v.co.x += random.uniform(-.2, .2)
    return add(bm, m, at, (random.uniform(-.6, -.3), random.uniform(-.4, .4), random.uniform(0, 6)))
def lit(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color, l.energy = c, w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# forest floor: mossy slab, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4, radius2=9.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.3, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
add(bm, moss)
for i in range(10): puff((random.uniform(-7, 7), random.uniform(-7, 7), 0), random.uniform(.4, .9), soil, .35)
# four giant trunks with buttress roots and spiral ladders
trees = ((-5, 3, 6.5, 1.0), (5, 4, 7.0, 1.0), (-6, -4, 5.5, 1.0), (6, -4, 6.0, 1.0))
for i, (x, y, h, r) in enumerate(trees):
    trunk((x, y, 0), r, h, bark, lean=random.uniform(-.15, .15))
    for k in range(4):
        a = k * 1.57 + i
        rod((x + math.cos(a) * r * .9, y + math.sin(a) * r * .9, 0), (x + math.cos(a) * r * 2.0, y + math.sin(a) * r * 2.0, .1), .3, bark)
    for k in range(int(h * 1.1)):
        a = k * .9 + i * 2
        px, py = x + math.cos(a) * (r + .15), y + math.sin(a) * (r + .15)
        rod((px, py, k * .7), (px, py, k * .7 + .9), .12, rope)
    for k in range(4):
        a = k * 1.57 + i
        rod((x + math.cos(a) * (r + .1), y + math.sin(a) * (r + .1), .8 + k * 1.7), (x + math.cos(a) * (r + .1), y + math.sin(a) * (r + .1), .8 + k * 1.7 + .1), .1, plank)
    for k in range(6):
        a = k * 1.05 + i
        frond((x + math.cos(a) * r * 1.2, y + math.sin(a) * r * 1.2, h + random.uniform(-.5, .5)), frond if k % 2 else leaf2, random.uniform(1.0, 1.4))
    for k in range(3):
        a = k * 2.1 + i * 3
        frond((x + math.cos(a) * r * 1.8, y + math.sin(a) * r * 1.8, h - 2.5 - k * .8), frond, random.uniform(.8, 1.2))
# canopy platforms and rope bridges
def deck(x, y, z, w, d):
    box((x, y, z), (w, d, .25), plank)
    for s in (-1, 1):
        box((x, y + s * d * .45, z + .25), (w, .1, .7), plank)
        for k in range(5): rod((x - w * .4 + k * w * .2, y + s * d * .45, z + .25), (x - w * .4 + k * w * .2, y + s * d * .45, z + .95), .06, plank)
def bridge(a, b, z):
    a, b = Vector(a), Vector(b); n = 8
    for i in range(n):
        t = i / (n - 1); p = a.lerp(b, t); sag = z - .5 * math.sin(math.pi * t)
        box((p.x, p.y, sag), (.7, .8, .1), plank, (0, 0, math.atan2(b.y - a.y, b.x - a.x)))
        for s in (-1, 1):
            q = p + Vector((-math.sin(math.atan2(b.y - a.y, b.x - a.x)) * .4 * s, math.cos(math.atan2(b.y - a.y, b.x - a.x)) * .4 * s, 0))
            rod(q, q + Vector((0, 0, .8)), .05, plank)
            if i: rod(p + Vector((-math.sin(math.atan2(b.y - a.y, b.x - a.x)) * .4 * s, math.cos(math.atan2(b.y - a.y, b.x - a.x)) * .4 * s, .8)), q + Vector((0, 0, .8)), .04, rope)
    for s in (-1, 1): rod(a + Vector((0, s * .4, .8)), b + Vector((0, s * .4, .8)), .04, rope)
deck(-5, 3, 3.4, 2.6, 2.6); deck(5, 4, 4.2, 2.6, 2.6); deck(-6, -4, 3.0, 2.6, 2.6); deck(6, -4, 3.6, 2.6, 2.6); deck(0, 0, 4.8, 3.0, 3.0)
bridge((-5, 3, 0), (0, 0, 0), 3.4); bridge((5, 4, 0), (0, 0, 0), 4.2); bridge((-6, -4, 0), (0, 0, 0), 3.0); bridge((6, -4, 0), (0, 0, 0), 3.6)
for x, y in ((-5, 3), (5, 4), (-6, -4), (6, -4), (0, 0)):
    box((x + 1.0, y - 1.0, 3.4 if x else 4.8), (.3, .3, .9), lampm); box((x + 1.0, y - 1.0, 4.3 if x else 5.7), (.5, .5, .3), lampm)
    lit("POINT", (1, .6, .2), 450, (x + 1.0, y - 1.2, 3.9 if x else 5.2))
lit("POINT", (1, .6, .2), 800, (0, -1.4, 5.4))
# mist drifting at the top, ferns and logs below
for i in range(11):
    puff((random.uniform(-7, 7), random.uniform(-6, 6), random.uniform(7, 9)), random.uniform(1.0, 1.8), mist, .35)
for i in range(14):
    x, y = random.uniform(-7.5, 7.5), random.uniform(-7, 7)
    if math.hypot(x, y) < 3 or any(math.hypot(x - tx, y - ty) < 2 for tx, ty, _, _ in trees): continue
    frond((x, y, 0), frond, random.uniform(.5, .9)); frond((x, y, 0), leaf2, random.uniform(.4, .7)).rotation_euler.z += 1.5
for x, y in ((-2, 0), (2, -1)): trunk((x, y, .1), .35, 2.5, bark, lean=1.4)
lit("SUN", (.55, .9, .7), 4, (-22, -14, 10), (0, 0, 3)); lit("SUN", (.5, .4, .9), 2.2, (18, 18, 14), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .02, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4)); co.location = t + Vector((18, -46, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
