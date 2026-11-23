import bpy, bmesh, math, random
from mathutils import Vector
random.seed(689)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, em=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
soil, soil2, hedge, mint, cham, lemon = col((.22, .13, .08)), col((.16, .1, .07)), col((.08, .2, .1)), col((.2, .45, .25)), col((.55, .5, .4)), col((.35, .5, .2))
wood, wood2, pot, steam, bee, wing = col((.3, .2, .12)), col((.2, .13, .08)), col((.5, .22, .12)), col((.8, .85, .9), 1.2), col((.9, .6, .05)), col((.7, .8, .95), .5)
tile, tin, bulb, water = col((.4, .15, .1)), col((.35, .4, .45)), col((1, .75, .3), 14), col((.05, .15, .2))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def post(at, r, h, m, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def clump(at, r, m, sq=(1, 1, .8)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.88, 1.12)
    return mk(bm, m, at)
def line(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def glim(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("g", kind); l.color, l.energy = c, w
    o = bpy.data.objects.new("g", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# garden plot base: soil, rough underneath
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=12, depth=3.6)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    v.co.z -= 1.8
mk(bm, soil)
# three fenced beds with rows of plants, each a different herb
for k, (x, y, m, bloom) in enumerate(((-5, 3, mint, None), (0.5, 3, cham, col((.9, .85, .2))), (6, 3, lemon, col((.8, .3, .2))))):
    slab((x, y, 0), (4.6, 3.4, .4), wood2)
    for sx in (-1, 1):
        for sy in (-1, 1): post((x + sx * 2.3, y + sy * 1.7, 0), .1, 1.1, wood)
    for sy in (-1, 1): line((x - 2.3, y + sy * 1.7, 1.0), (x + 2.3, y + sy * 1.7, 1.0), .08, wood)
    for sx in (-1, 1): line((x + sx * 2.3, y - 1.7, 1.0), (x + sx * 2.3, y + 1.7, 1.0), .08, wood)
    for r in range(4):
        for c in range(3):
            px, py = x - 1.5 + c * 1.5 + random.uniform(-.15, .15), y - 1.0 + r * .65
            clump((px, py, .75), .38, m, (1, 1, .8))
            if bloom and (r + c) % 2 == 0: clump((px, py, 1.1), .14, bloom)
# drying racks under the eave of a small shed on the right
sx0, sy0 = 8.5, -2.5
slab((sx0, sy0, 0), (4.4, 3.4, 2.6), wood2)
for sx in (-1, 1):
    for sy in (-1, 1): post((sx0 + sx * 2.1, sy0 + sy * 1.6, 0), .12, 2.6, wood)
slab((sx0, sy0, 2.6), (5.4, 4.2, .25), tile, (-.25, 0, 0))
slab((sx0 - 2.35, sy0, 0), (.1, 3.2, 2.6), wood)
for i in range(4):
    z = .8 + i * .5
    line((sx0 - 2.2, sy0 - 1.2, z), (sx0 - 2.2, sy0 + 1.2, z), .06, wood)
    for j in range(6):
        clump((sx0 - 2.2, sy0 - 1.0 + j * .4, z + .22), .16, (mint, cham, lemon, cham)[i % 4], (1, 1, 1.4))
slab((sx0 + .5, sy0 - 1.6, 0), (1.6, .1, 1.2), wood2)
post((sx0 - 2.1, sy0, 2.3), .1, .3, wood, 5)
post((sx0 - 2.1, sy0, 1.9), .22, .35, bulb, 6)
glim("POINT", (1, .75, .3), 400, (sx0 - 2.6, sy0, 1.9))
# barrel table with a big teapot, cups, and steam
post((-1, -4.5, 0), 1.0, 1.4, wood, 8); post((-1, -4.5, 1.4), 1.05, .15, wood2, 8)
post((-1, -4.5, 1.55), .55, .8, tin, 8, .45); post((-1, -4.5, 2.35), .5, .1, tin, 8)
post((-1, -4.5, 2.45), .22, .12, tin, 6)
line((-1.3, -4.5, 2.0), (-1.9, -4.5, 2.3), .12, tin); line((-1.9, -4.5, 2.3), (-2.0, -4.5, 1.9), .09, tin)
line((-1.0, -4.5, 2.1), (-.4, -4.5, 2.2), .09, tin); slab((-.4, -4.5, 2.15), (.2, .2, .1), tin)
for i in range(3): post((-1.6 + i * .6, -4.0, 1.55), .12, .2, pot, 6)
for i in range(4): clump((-1.0 + .15 * i, -4.5, 2.8 + i * .45), .16 + .05 * i, steam)
# bees circling the beds
for i in range(7):
    x, y, z = random.uniform(-7, 4), random.uniform(0, 5), random.uniform(1.6, 2.8)
    clump((x, y, z), .17, bee, (1.5, 1, 1)); clump((x - .1, y, z + .15), .1, wing, (1, 1, .8))
# hedge along the back and left, stepping stones, watering can
for i in range(9): clump((-8 + i * 2, 6.4, .9), 1.2, hedge, (1.3, 1, .8))
for i in range(5): clump((-8.5, -1 + i * 1.6, .8), 1.0, hedge, (1, 1.2, .9))
for i in range(5): slab((-4 + i * 2.2, -1.2, 0), (.9, .6, .08), soil2, (0, 0, i))
post((-8, -5, 0), .3, .7, tin, 6); line((-7.7, -5, .6), (-6.6, -5, .9), .1, tin)
# warm golden hour from the left, cool rim from behind
glim("SUN", (1, .65, .35), 5.5, (-24, -14, 9), (0, 0, 1)); glim("SUN", (.4, .6, 1), 2.2, (20, 24, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .025, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.2)); co.location = t + Vector((6, -50, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
