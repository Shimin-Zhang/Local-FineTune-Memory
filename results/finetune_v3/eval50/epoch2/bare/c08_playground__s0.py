import bpy, bmesh, random, math
from mathutils import Vector
random.seed(503)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(c, e=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .8
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
turf, path, wood, red, blue, yellow, sand, rubber, leaf1, leaf2, trunk, iron = (col(c) for c in (
    (.08, .2, .1), (.25, .2, .15), (.3, .18, .1), (.7, .1, .08), (.1, .3, .6), (.8, .6, .08), (.55, .42, .25), (.07, .07, .09), (.1, .3, .1), (.2, .38, .08), (.2, .13, .08), (.1, .1, .12)))
lamp, lamp2, bulb = col((.3, .6, 1), 14), col((1, .5, .15), 14), col((1, .85, .5), 16)
def mk(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(p, s, m, r=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, p, r)
def rod(p, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, p, rot)
def ball(p, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, m, p)
def glow(p, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
# base: round grass slab, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=13, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
mk(bm, turf)
for i in range(7): box((-2 + i * .6, -9.5 + i * 2.8, 0), (2.6, 1.6, .08), path, (0, 0, .2))
# slide: platform, ladder, chute with side rails, support legs
box((-6, 3, 3.6), (3.4, 3.2, .3), wood)
for sx in (-1, 1):
    box((-6 + sx * 1.7, 3, 0), (.3, 2.8, 3.6), wood); box((-6 + sx * 1.7, 4.6, 3.6), (.3, .3, 1.2), red)
    for k in range(4): box((-6 + sx * 1.7, 3, .5 + k * .9), (.3, 2.2, .12), iron)
box((-6, 4.6, 4.9), (3.4, .2, .2), red); box((-6, 1.4, 4.9), (3.4, .2, .2), red)
box((-6, 1.4, 4.9), (.2, 3.4, .2), red)
for i in range(6):
    t = i / 5
    box((-6, 3.6 - t * 5.2, 3.6 - t * 3.6 + .1), (2.0, 1.15, .15), yellow, (0, .66, 0)).location.z = 3.6 - t * 3.6
    for sx in (-1, 1): box((-6 + sx * 1.05, 3.6 - t * 5.2, 3.6 - t * 3.6 + .2), (.12, 1.1, .5), yellow, (0, .66, 0))
# swing set: A-frame legs, top bar, two seats with chains
for sy in (-1, 1):
    for sx in (-1, 1): rod((2 + sx * 3.2, 2 + sy * 1.0, 0), .16, 5.2, 5, iron, rot=(sy * .15, 0, 0))
box((2, 2, 5.0), (7.0, .3, .3), iron)
for sx in (-1.5, 1.5):
    for k in range(2): rod((2 + sx + (k - .5) * .35, 2, 4.9), .03, 3.2, 4, iron)
    box((2 + sx, 2, 1.6), (1.0, .15, .15), red if sx < 0 else blue)
# sandbox: four boards, sand inside, bucket and spade
for (x, y, w, d) in ((6.5, -2, 3.6, .3), (6.5, .2, 3.6, .3), ((4.7, -1, .3, 1.6), (8.3, -1, .3, 1.6))):
    box((x, y, 0), (w, d, .7), wood)
box((6.5, -.9, .1), (3.2, 2.2, .5), sand)
rod((6.0, -1.2, .6), .3, .5, 7, red, .22); rod((7.2, -.6, .6), .06, 1.2, 4, yellow, rot=(0, .2, 0)); box((7.4, -.6, 1.7), (.4, .06, .3), yellow)
# seesaw: pivot post and a long board
rod((-1, -4.5, 0), .25, 1.0, 6, iron, .15); box((-1, -4.5, 1.0), (4.2, .6, .2), blue, (0, .06, 0))
# lamp posts with glowing heads
for (x, y) in ((-9, -5), (9.5, 4)):
    rod((x, y, 0), .12, 5.5, 5, iron); box((x, y, 5.5), (.9, .9, .9), bulb); glow((x, y, 5.6), (1, .8, .5), 450)
# trees, bushes, fence
for (x, y, s) in ((-10, 6, 1.2), (10, 8, 1.0), (-3, 9.5, 1.1)):
    rod((x, y, 0), .3 * s, 2.2 * s, 5, trunk); ball((x, y, 3.4 * s), 1.8 * s, leaf1, .9); ball((x + .8, y, 4.4 * s), 1.2 * s, leaf2, .9)
for i in range(6): ball((-9 + i * .1, 8.5 - i * .2, .5), .6 + (i % 2) * .2, leaf2, .7)
for i in range(11): box((-10 + i * 2, 10.2, 0), (.2, .2, 1.4), wood); 
box((0, 10.2, 1.0), (20, .12, .12), wood)
# night: cool moonlight from the left, warm rim from behind right
for c, e, p in (((.55, .65, 1), 4.5, (-26, -12, 12)), ((1, .6, .3), 2.2, (22, 22, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((6, -54, 31))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
