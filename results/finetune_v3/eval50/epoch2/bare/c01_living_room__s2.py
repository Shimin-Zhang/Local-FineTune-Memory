import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1339)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(r, g, b, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .8
    if glow: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = glow
    return m
oak, oak2, plaster, plaster2 = dye(.3, .2, .12), dye(.22, .14, .08), dye(.32, .26, .24), dye(.24, .2, .22)
teal, teal2, cream, wood = dye(.1, .32, .34), dye(.06, .22, .24), dye(.55, .5, .4), dye(.35, .2, .1)
rugA, rugB, rugC, shade = dye(.4, .12, .1), dye(.5, .38, .2), dye(.12, .2, .3), dye(1, .65, .3, 22)
lampg, win, plant, book1 = dye(1, .6, .25, 16), dye(.5, .65, 1, 6), dye(.1, .3, .12), dye(.6, .15, .12)
book2, book3, black = dye(.1, .3, .5), dye(.7, .6, .15), dye(.03, .03, .04)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, m, at, rot)
def post(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at)
def blob(at, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.9, 1.1); v.co.z *= sq
    return put(bm, m, at)
def glow(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=9.2, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.2, .2)))
put(bm, oak2)
for i in range(9): slab((-8 + i * 2, 0, 0), (1.96, 12, .12), oak if i % 2 else oak2)
# two walls: back with a window, left with a bookshelf
slab((0, 6.2, 0), (18, .6, 7), plaster); slab((-9, 0, 0), (.6, 12.4, 7), plaster2)
slab((3.4, 5.8, 2.0), (4.6, .3, 3.6), win); slab((3.4, 5.6, 3.8), (4.8, .3, .25), cream); slab((3.4, 5.6, 3.8), (.2, .3, 3.6), cream)
slab((3.4, 5.4, 1.9), (5.2, 1.0, .25), cream)
slab((-8.6, 0, 0), (.9, 6, 5.2), wood)
for k in range(4):
    slab((-8.1, 0, 1.0 + k * 1.2), (.7, 5.6, .15), oak)
    for j in range(6):
        if (k + j) % 3: slab((-8.1, -2.2 + j * .9, 1.15 + k * 1.2), (.5, .6, .7 + .1 * ((j * k) % 3)), (book1, book2, book3, cream)[(j + k) % 4], (0, 0, 0))
# rug, sofa, cushions, coffee table with books and a vase
for r, m in ((4.6, rugC), (3.6, rugA), (2.6, rugB), (1.6, rugA)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=r, depth=.06)
    put(bm, m, (0, -1, .12 + r * .01))
slab((0, 2.2, .5), (7, 2.4, .9), teal); slab((0, 3.5, 1.4), (7, .5, 1.6), teal2)
for sx in (-1, 1): slab((sx * 3.5, 2.2, 1.4), (.5, 2.4, 1.0), teal2)
for i in range(3): slab((-2.1 + i * 2.1, 2.2, 1.4), (1.9, 2.0, .5), teal)
for i, c in enumerate((cream, book2, book1)):
    slab((-2 + i * 2, 2.0, 1.9), (1.4, 1.2, .55), c, (0, 0, .15 * (i - 1)))
slab((0, -1.2, .12), (3.4, 1.8, .15), wood); slab((0, -1.2, .75), (3.0, 1.5, .12), oak)
for sx in (-1, 1):
    for sy in (-1, 1): slab((sx * 1.4, -1.2 + sy * .6, .12), (.14, .14, .65), black)
slab((-.6, -1.2, .87), (1.0, .7, .12), book1, (0, 0, .2)); slab((-.6, -1.2, .99), (.9, .6, .1), book3, (0, 0, .5))
post((.8, -1.2, .87), .22, .5, 6, cream, .12); post((.8, -1.2, 1.37), .1, .1, 6, black)
# floor lamp, side table with a lamp, plant, framed art
post((-5.6, 3.2, .12), .4, .15, 8, black); post((-5.6, 3.2, .27), .08, 3.6, 5, black)
post((-5.6, 3.2, 3.8), .6, 1.0, 8, shade, .45); post((-5.6, 3.2, 4.0), .35, .3, 6, lampg)
glow("POINT", (1, .6, .25), 700, (-5.6, 3.2, 4.2))
slab((5.4, 3.2, .12), (1.4, 1.4, .9), wood); post((5.4, 3.2, 1.02), .2, .6, 6, lampg, .1); post((5.4, 3.2, 1.62), .35, .5, 6, shade, .25)
glow("POINT", (1, .6, .25), 250, (5.4, 3.2, 2.0))
post((7.6, 4.6, .12), .5, .8, 7, book1, .4)
for k in range(6):
    a = k * 1.05; post((7.6 + math.cos(a) * .2, 4.6 + math.sin(a) * .2, .9), .08, 1.5, 4, plant, .02).rotation_euler = (math.sin(a) * .5, -math.cos(a) * .5, 0)
for i, x in enumerate((-5.5, -3.8, -2.1)):
    slab((x, 5.8, 2.6), (1.4, .12, 1.8), wood); slab((x, 5.7, 2.9), (1.0, .06, 1.2), (book2, rugA, book1)[i])
slab((-1.2, 5.8, 3.6), (2.0, .12, 1.4), wood); slab((-1.2, 5.7, 3.8), (1.6, .06, 1.0), cream)
glow("POINT", (.5, .65, 1), 500, (3.4, 4.8, 3.8))
glow("SUN", (1, .55, .3), 5, (22, -20, 9), (0, 0, 1.5)); glow("SUN", (.35, .45, 1), 2, (-14, 20, 10), (0, 0, 1.5))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((16, -40, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
