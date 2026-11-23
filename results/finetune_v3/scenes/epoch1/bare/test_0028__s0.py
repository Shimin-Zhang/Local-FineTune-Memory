import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1959)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
P = {}
def dye(k, c, e=0, r=.9):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    P[k] = m
for k, c in (("turf", (.1, .26, .09)), ("turf2", (.08, .2, .08)), ("plank", (.42, .26, .13)), ("plank2", (.3, .18, .09)), ("slide", (.8, .12, .1)),
             ("slide2", (.9, .65, .1)), ("mattA", (.75, .1, .12)), ("mattB", (.1, .35, .7)), ("hoop1", (.9, .75, .1)), ("hoop2", (.9, .3, .1)), ("hoop3", (.2, .6, .6)),
             ("canvas", (.7, .6, .45)), ("canvas2", (.25, .3, .5)), ("pine", (.06, .2, .12)), ("trunk", (.2, .12, .07)), ("steel", (.3, .32, .36)), ("lamp", (1, .65, .2))):
    dye(k, c)
dye("bulb", (1, .6, .15), 14); dye("lampglow", (1, .65, .2), 10)
def mesh(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(P[k]); return o
def blk(at, s, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mesh(bm, k, at, rot)
def col(at, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, k, at)
def tube(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mesh(bm, k)
def bulb(at, r, k):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    return mesh(bm, k, at)
def light(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()

# lawn base, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .2)))
    else: v.co.z += random.uniform(-.08, .08)
    v.co.z -= 1.7
mesh(bm, "turf")
# the tower: four legs, cross braces, two decks, railings, a roofed top deck
for sx in (-1, 1):
    for sy in (-1, 1): col((sx * 2.4, sy * 2.4, 0), .3, 11.5, 5, "plank2")
for z in (2.2, 4.4, 6.6, 8.8):
    for sx, sy, dx, dy in ((0, 0, 1, 0), (0, 0, 0, 1)):
        blk((0, 0, z), (4.8, .15, .15) if dx else (.15, 4.8, .15), "plank2")
for z, w in ((2.6, 6.4), (6.0, 5.6)):
    blk((0, 0, z - .35), (w, w, .35), "plank")
    for i in range(7):
        blk((-w / 2 + .3 + i * (w - .6) / 6, -w / 2 + .2, z + .15), (.12, .12, 1.0), "plank2")
    for sx in (-1, 1): blk((sx * (w / 2 - .2), 0, z + 1.0), (.12, w - .4, .12), "plank2"); blk((0, sx * (w / 2 - .2), z + 1.0), (w - .4, .12, .12), "plank2")
blk((0, 0, 11.5), (4.2, 4.2, .3), "plank")
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.6, radius2=.3, depth=1.6)
for v in bm.verts: v.co.z += .8
mesh(bm, "mattA", (0, 0, 11.8), (0, 0, math.pi / 4))
# spiral slide: a red and yellow ribbon of boards winding down the outside
prev = None
for i in range(46):
    t = i / 45; a = 4.2 - t * 7.4; r = 3.4 + t * 1.0; z = 10.2 - t * 9.6
    p = Vector((math.cos(a) * r, math.sin(a) * r, z))
    if prev: tube(prev, p, .55, "slide" if i % 2 else "slide2")
    prev = p
    if i % 5 == 0:
        tube(p, p + Vector((math.cos(a) * 1.0, math.sin(a) * 1.0, 0)), .2, "steel")
# mats at the base of the slide
for i, k in enumerate(("mattA", "mattB", "mattA")): blk((math.cos(4.2 - 7.4) * 4.6 + i * 1.0, math.sin(4.2 - 7.4) * 4.6, 0), (1.2, 2.4, .25), k, (0, 0, 4.2 - 7.4 + 1.57))
blk((0, -5.6, 0), (3.4, 1.8, .25), "mattB")
# hoop-la stall: striped canopy on four posts, hoops on a rack, a prize shelf
for sx in (-1, 1):
    for sy in (-1, 1): col((8 + sx * 2.2, -3 + sy * 1.8, 0), .12, 3.2, 5, "plank2")
blk((8, -3, 3.2), (5.4, 4.6, .2), "canvas")
for i in range(6): blk((8 - 2.4 + i * .9, -3, 3.4), (.45, 4.4, .12), "canvas2")
for i in range(5):
    for k in range(2): col((6.6 + i * .7, -1.0, 1.0 + k * .35), .45, .08, 8, ("hoop1", "hoop2", "hoop3")[(i + k) % 3])
blk((8, -4.3, .8), (5, .6, .12), "plank")
for i in range(4): bulb((6.6 + i * 1.1, -4.3, 1.2), .3, ("hoop1", "mattA", "hoop3", "mattB")[i])
# string lights up the tower and around the stall
for i in range(10):
    z = 1.5 + i * 1.1; a = i * 1.3
    bulb((math.cos(a) * 3.1, math.sin(a) * 3.1, z), .14, "bulb")
for i in range(8): bulb((8 - 2.4 + i * .68, -5.4, 3.1), .1, "bulb")
light("POINT", (1, .6, .2), 700, (0, -3, 5)); light("POINT", (1, .6, .2), 500, (8, -5, 2.5))
# a few pines and a bench
for x, y, h in ((-10, 4, 5), (-8, 8, 6), (10, 6, 5.5), (-11, -2, 4.5), (12, -1, 4)):
    col((x, y, 0), .3, 1.2, 5, "trunk")
    for j in range(3): col((x, y, 1.2 + j * h * .22), 1.9 - j * .5, h * .35, 6, "pine", .1)
blk((-5.5, -6, 0), (2.6, .8, .6), "plank"); blk((-5.5, -6.4, .6), (2.6, .15, .5), "plank2")
light("SUN", (1, .5, .3), 5, (-26, -14, 8), (0, 0, 2)); light("SUN", (.3, .5, .9), 2.2, (24, 22, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .05, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((1, 0, 4)); co.location = t + Vector((8, -54, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
