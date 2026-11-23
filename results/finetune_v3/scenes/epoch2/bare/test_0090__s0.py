import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1274)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
T = {}
def paint(name, rgb, em=0, metal=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    T[name] = m
for k, v in dict(sand=(.42, .28, .14), road=(.3, .24, .17), white=(.5, .48, .42), rust=(.38, .15, .06), rust2=(.25, .1, .05), steel=(.3, .32, .3), rock=(.3, .2, .13),
                 cactus=(.1, .25, .1), roof=(.4, .12, .08), glass=(.1, .2, .25), wood=(.3, .18, .1), pipe=(.15, .15, .16)).items(): paint(k, v)
paint("neon", (1, .05, .1), em=18); paint("sign", (1, .55, .1), em=10); paint("heat", (1, .85, .5), em=2)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("t"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("t", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(T[m]); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def can(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def pebble(at, r, m, sq=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return mk(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# dusty ground: a flat slab with a rough underside, and a dirt road across the front
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 2
mk(bm, "sand")
slab((0, -7.2, .02), (26, 3.2, .1), "road"); slab((0, -7.2, .12), (26, .25, .02), "white")
for i in range(7): slab((-11 + i * 3.6, -7.2, .13), (1.6, .15, .02), "rust2")
# the steel water tank: eight legs, cross braces, a fat drum with bands, a conical roof and a ladder
tx, ty = -3.5, 4.5
for i in range(8):
    a = i * math.pi / 4 + math.pi / 8
    px, py = tx + 3.2 * math.cos(a), ty + 3.2 * math.sin(a)
    strut((px, py, 0), (px * .85 + tx * .15, py * .85 + ty * .15, 6.2), .28, "rust2")
    strut((px, py, 1.2), (tx + 2.0 * math.cos(a), ty + 2.0 * math.sin(a), 2.6), .12, "rust")
    strut((px, py, 2.6), (tx + 1.6 * math.cos(a), ty + 1.6 * math.sin(a), 4.0), .12, "rust")
for i in range(8):
    a, b = i * math.pi / 4 + math.pi / 8, (i + 1) * math.pi / 4 + math.pi / 8
    for z in (1.2, 2.6, 4.0):
        r = 3.2 - z * .25
        strut((tx + r * math.cos(a), ty + r * math.sin(a), z), (tx + r * math.cos(b), ty + r * math.sin(b), z), .12, "rust")
can((tx, ty, 6.2), 3.4, 4.2, 8, "steel", 3.4)
for z in (6.4, 7.8, 9.2, 10.3): can((tx, ty, z), 3.5, .18, 8, "rust2")
can((tx, ty, 10.4), 3.6, 1.6, 8, "rust", .3)
can((tx, ty, 12.0), .35, .8, 6, "rust2")
for k in range(10):
    z = .5 + k * .62
    slab((tx + 3.3 - z * .15, ty - 1.2, z), (.1, .5, .1), "rust")
strut((tx + 3.3, ty - 1.45, .5), (tx + 2.7, ty - 1.45, 6.7), .08, "rust"); strut((tx + 3.3, ty - .95, .5), (tx + 2.7, ty - .95, 6.7), .08, "rust")
strut((tx - 3.0, ty, 6.4), (tx - 6.5, ty, 1.2), .22, "pipe"); strut((tx - 6.5, ty, 1.2), (tx - 6.5, ty - 1.8, 1.2), .22, "pipe")
# the windmill pump: a lattice tower, a wheel of thin blades, a tail vane and a pipe to a trough
wx, wy = 6.5, 4.5
for i in range(4):
    a = i * math.pi / 2 + math.pi / 4
    strut((wx + 1.5 * math.cos(a), wy + 1.5 * math.sin(a), 0), (wx + .5 * math.cos(a), wy + .5 * math.sin(a), 8.0), .14, "rust2")
for z in (1.5, 3.5, 5.5):
    r = 1.5 - z * .125
    for i in range(4):
        a, b = i * math.pi / 2 + math.pi / 4, (i + 1) * math.pi / 2 + math.pi / 4
        strut((wx + r * math.cos(a), wy + r * math.sin(a), z), (wx + r * math.cos(b), wy + r * math.sin(b), z), .09, "rust")
can((wx, wy, 8.0), .25, .6, 6, "steel")
for k in range(12):
    a = k * math.pi / 6
    strut((wx, wy, 8.6), (wx + 2.6 * math.cos(a), wy + 2.6 * math.sin(a), 8.6), .13, "steel")
    strut((wx + 2.6 * math.cos(a), wy + 2.6 * math.sin(a), 8.6), (wx + 2.6 * math.cos(a + .26), wy + 2.6 * math.sin(a + .26), 8.6), .3, "rust")
strut((wx, wy, 8.6), (wx + 3.8, wy, 7.0), .12, "rust2"); slab((wx + 4.2, wy, 6.2), (.1, 1.8, .9), "rust")
strut((wx, wy, 7.0), (wx - 1.5, wy - 3.0, 1.2), .12, "pipe"); slab((wx - 2.0, wy - 3.6, .0), (1.8, 1.0, .5), "wood")
# a small town along the road: a white shop with a neon sign, a gas pump and a hitching post
slab((4, -4.2, 0), (5.0, 3.4, 2.6), "white"); slab((4, -4.2, 2.6), (5.4, 3.8, .25), "roof")
slab((4, -5.95, .8), (1.2, .1, 1.4), "glass"); slab((1.6, -5.95, .6), (.1, .1, 1.6), "glass"); slab((6.4, -5.95, .6), (.1, .1, 1.6), "glass")
slab((4, -6.1, 3.0), (2.4, .15, .9), "neon"); slab((4, -6.2, 3.1), (2.0, .1, .6), "sign")
slab((-1.5, -4.5, 0), (1.0, 1.0, 1.6), "rust"); slab((-1.5, -4.5, 1.6), (1.2, 1.2, .15), "white"); slab((-1.5, -5.05, 1.0), (.6, .05, .5), "sign")
for x in (8.5, 9.2): strut((x, -5.2, 0), (x, -5.2, 1.4), .12, "wood")
strut((8.3, -5.2, 1.2), (9.4, -5.2, 1.2), .1, "wood")
for i in range(5): pebble((random.uniform(-11, 11), random.uniform(1, 11), .1), random.uniform(.4, 1.0), "rock", .6)
for x, y in ((-9, 8), (1, 9.5), (10, 8.5), (-8, -2)):
    can((x, y, 0), .35, 2.0, 6, "cactus", .3); can((x + .6, y, .8), .22, 1.0, 6, "cactus", .2); strut((x + .2, y, 1.0), (x + .6, y, 1.0), .12, "cactus")
lamp("POINT", (1, .05, .1), 900, (4, -7.2, 3.2)); lamp("POINT", (1, .55, .1), 500, (-1.5, -6.0, 1.4))
lamp("SUN", (1, .82, .5), 8.5, (24, -10, 30), (0, 0, 3)); lamp("SUN", (1, .5, .25), 2.5, (-24, 22, 10), (0, 0, 3))
w = bpy.data.worlds.new("heat"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .02, .01, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 5)); co.location = t + Vector((-6, -66, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
