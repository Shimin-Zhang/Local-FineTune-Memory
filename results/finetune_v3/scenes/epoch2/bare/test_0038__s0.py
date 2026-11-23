import bpy, bmesh, math, random
from mathutils import Vector
random.seed(635)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def bark(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("b"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
moss, loam, trunk, trunk2 = bark((.06, .17, .1)), bark((.12, .1, .08)), bark((.22, .17, .13)), bark((.16, .13, .11))
deck, plank, rope, leaf = bark((.3, .2, .12)), bark((.22, .15, .1)), bark((.55, .45, .3)), bark((.05, .22, .12))
leaf2, mist, fern, mossy = bark((.08, .3, .15)), bark((.5, .65, .75), .15, 1), bark((.1, .35, .15)), bark((.1, .3, .1))
lamp, flower, vine = bark((1, .6, .2), 20), bark((1, .2, .6), 12), bark((.1, .25, .1))
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def log(at, r, h, n, m, rot=(0, 0, 0), r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, rot)
def rope(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, m)
def blob(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return add(bm, m, at)
def lit(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# forest floor base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13.5, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 2
add(bm, moss)
# four huge trees
trees = [(-9, -5, 1.5, 11), (9, -6, 1.4, 12), (-10, 6, 1.6, 12.5), (9.5, 6.5, 1.5, 11.5)]
for i, (x, y, r, h) in enumerate(trees):
    log((x, y, 0), r * 1.5, 1.2, 7, trunk2, r2=r)
    log((x, y, 1), r, h - 1, 7, trunk if i % 2 == 0 else trunk2, r2=r * .6)
    for k in range(4):
        a = k * 1.6 + i
        log((x + math.cos(a) * r * .8, y + math.sin(a) * r * .8, 0), .5, 1.6, 5, trunk2, (.3 * math.cos(a), .3 * math.sin(a), 0))
    for z in (5, 7.5, 10):
        a = z + i
        box((x + math.cos(a) * r * .9, y + math.sin(a) * r * .9, z), (.7, .5, .5), mossy)
# canopy platforms on each tree
plats = [(-9, -5, 8.6), (9, -6, 9.2), (-10, 6, 9.8), (9.5, 6.5, 8.8)]
for i, (x, y, z) in enumerate(plats):
    log((x, y, z - .3), 2.5, .4, 8, deck)
    for k in range(8):
        a = k * math.pi / 4
        box((x + math.cos(a) * 2.3, y + math.sin(a) * 2.3, z + .1), (.15, .15, 1.1), plank)
    for k in range(8):
        a = k * math.pi / 4 + .39
        rope((x + math.cos(a) * 2.3, y + math.sin(a) * 2.3, z + 1.2), (x + math.cos(a + .785) * 2.3, y + math.sin(a + .785) * 2.3, z + 1.2), .1, rope)
    for k in range(3):
        a = k * 2.1 + i
        rope((x + math.cos(a) * 2.3, y + math.sin(a) * 2.3, z + 1.2), (x + math.cos(a) * 2.3, y + math.sin(a) * 2.3, z + .5), .08, rope)
    log((x, y, z + .1), .2, 1.0, 5, plank)
    box((x, y, z + 1.1), (.5, .5, .6), lamp)
    lit("POINT", (1, .6, .2), 700, (x, y, z + 1.6))
# rope bridges between platforms
for a, b in ((0, 1), (1, 3), (3, 2), (2, 0)):
    pa, pb = Vector(plats[a]), Vector(plats[b])
    for s in (-.7, .7):
        rope(pa + Vector((0, s, .5)), pb + Vector((0, s, .5)), .09, rope)
    for k in range(1, 13):
        t = k / 13; p = pa.lerp(pb, t) + Vector((0, 0, .5 - 1.2 * math.sin(t * math.pi)))
        box(p - Vector((0, .7, 0)), (1.0, .12, .12), plank)
    for k in range(1, 13):
        t = k / 13; p = pa.lerp(pb, t) + Vector((0, 0, .5 - 1.2 * math.sin(t * math.pi)))
        rope(p + Vector((0, .7, 0)), p + Vector((0, .7, 1.5)), .06, rope)
# spiral ladders up two trunks
for i, (x, y) in enumerate((9, -6), (-10, 6)):
    for k in range(26):
        a = k * .5 + i * 2
        r = 1.7 + i * .1
        p = Vector((x + math.cos(a) * r, y + math.sin(a) * r, .6 + k * .31))
        box(p - Vector((0, .25, 0)), (.15, .5, .12), plank, (0, 0, a + math.pi / 2))
        rope(p + Vector((math.cos(a) * .5, math.sin(a) * .5, 0)), p + Vector((math.cos(a) * .5, math.sin(a) * .5, 1.1)), .06, rope)
    for z in (4, 8):
        a = (z - .6) / .31 * .5 + i * 2
        rope((x + math.cos(a) * 1.7, y + math.sin(a) * 1.7, z), (x + math.cos(a) * 2.4, y + math.sin(a) * 2.4, z + .5), .08, rope)
# canopy crowns and mist at the top
for i, (x, y, r, h) in enumerate(trees):
    for k in range(5):
        a = k * 1.3 + i
        blob((x + math.cos(a) * r * 1.2, y + math.sin(a) * r * 1.2, h + random.uniform(-.5, 1)), random.uniform(2.4, 3.4), leaf if k % 2 else leaf2, .65)
    blob((x, y, h + 1.5), 3.6, leaf2, .6)
for k in range(10):
    a = random.uniform(0, 6.3); d = random.uniform(4, 11)
    blob((math.cos(a) * d, math.sin(a) * d, random.uniform(13, 15.5)), random.uniform(2, 3.5), mist, .25)
# ferns, flowers, vines on the ground
for k in range(26):
    a = random.uniform(0, 6.3); d = random.uniform(2, 12)
    if d > 11: continue
    p = (math.cos(a) * d, math.sin(a) * d)
    for j in range(3):
        log((p[0], p[1], 0), .15, random.uniform(.8, 1.5), 4, fern, (.6 * (j - 1), .3, j * 2.1), r2=.02)
for k in range(8):
    a = random.uniform(0, 6.3); d = random.uniform(3, 11)
    log((math.cos(a) * d, math.sin(a) * d, 0), .1, .5, 5, mossy); blob((math.cos(a) * d, math.sin(a) * d, .6), .25, flower, 1)
lit("SUN", (.55, .9, .6), 4, (-26, -14, 10), (0, 0, 6))
lit("SUN", (.3, .5, .9), 2.2, (24, 22, 14), (0, 0, 6))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .025, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 7)); co.location = t + Vector((16, -62, 42))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
