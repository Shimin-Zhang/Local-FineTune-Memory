import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1352)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def mat(r, g, b, e=0, ro=.8):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = ro
    if e: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = e
    return m
wall, floor, wood, dark = mat(.12, .1, .2), mat(.2, .14, .1), mat(.3, .18, .1), mat(.04, .04, .05)
steel, screen, key, mug = mat(.4, .42, .46, 0, .4), mat(.1, .4, .8, 3), mat(.5, .5, .55), mat(.8, .15, .1)
lamp, warm, leaf, pot = mat(1, .75, .35, 25), mat(1, .65, .25, 6), mat(.1, .35, .15), mat(.5, .2, .12)
book1, book2, book3 = mat(.6, .1, .1), mat(.1, .3, .5), mat(.7, .6, .2)
def make(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(p, s, m, r=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, p, r)
def cyl(p, r, h, n, m, r2=None, r_=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, p, r_)
def lite(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab with a rough underside, and two walls
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=10, depth=2.6)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.3
make(bm, floor)
cube((0, 5.6, 0), (13, .5, 6.2), wall); cube((-6.2, 0, 0), (.5, 11.5, 6.2), wall)
cube((0, 5.3, 0), (13, .2, .4), wood); cube((-5.9, 0, 0), (.2, 11.5, .4), wood)
# the desk: top, two trestle legs, a back rail and a drawer unit
cube((0, 0, 2.2), (11, 4.2, .3), wood)
for x in (-4.8, 4.8):
    cube((x, -1.7, 0), (.35, .3, 2.2), dark); cube((x, 1.7, 0), (.35, .3, 2.2), dark)
cube((0, 1.9, 2.5), (11, .15, .5), dark)
cube((3.5, -.5, 0), (3.2, 3.0, 2.2), wood); cube((3.5, -2.05, 1.0), (2.6, .1, .8), dark)
for k in range(2): cube((3.5, -2.15, 1.4 - k * .9), (.5, .1, .1), steel)
# monitor on a stand, with a glowing screen and a base bar
cube((-1, .8, 2.5), (1.2, .8, .2), steel); cube((-1, .8, 2.7), (.3, .3, 1.2), steel)
cube((-1, .6, 3.9), (5.2, .25, 3.0), dark); cube((-1, .45, 4.1), (4.8, .1, 2.6), screen)
cube((-1, .4, 3.8), (4.8, .1, .12), mat(.2, .9, 1, 4))
# keyboard: a slab with rows of keys, a mouse, and a notebook
cube((-1, -1.0, 2.5), (4.2, 1.4, .15), dark)
for r in range(4):
    for c in range(12): cube((-2.8 + c * .32, -1.35 + r * .32, 2.65), (.26, .24, .08), key if (r + c) % 3 else mat(.7, .3, .1))
cyl((2.0, -1.0, 2.5), .35, .25, 8, key, .3, (0, 0, .5))
cube((-3.8, -1.0, 2.5), (1.5, 1.0, .1), book1, (0, 0, .3))
# mug with a handle and a steam curl, plus a desk lamp on an arm
cyl((1.5, .9, 2.5), .4, .8, 8, mug); cyl((1.5, .9, 3.25), .33, .06, 8, warm)
cube((1.95, .9, 2.8), (.15, .15, .4), mug)
cube((1.5, .9, 3.4), (.2, .2, .2), mug)
cube((-4.6, 1.0, 2.5), (1.2, 1.2, .2), steel)
cube((-4.6, 1.0, 2.7), (.15, .15, 1.8), steel, (0, 0, 0)); cube((-4.2, .6, 4.4), (1.4, .15, .15), steel, (0, .5, 0))
cube((-3.4, .1, 4.0), (.8, .8, .6), lamp, (.4, 0, 0)); lite("POINT", (1, .7, .3), 900, (-3.4, -.3, 3.9))
# shelf on the back wall with books, a plant and a small frame
cube((-1, 4.9, 4.0), (8, .8, .2), wood)
for i, c in enumerate((book1, book2, book3, book1, book2)): cube((-4 + i * .55, 4.9, 4.2), (.4, .3, 1.0 + (i % 3) * .15), c)
cyl((3, 4.9, 4.2), .5, .6, 7, pot); cyl((3, 4.9, 4.8), .6, .1, 7, leaf, .1)
cube((1.0, 4.9, 4.2), (1.2, .1, .9), dark); cube((1.0, 4.8, 4.35), (.9, .05, .6), warm)
# a chair pulled up to the desk, and a rug under it
cube((0, -3.2, .1), (5, 4, .1), mat(.35, .1, .15))
cube((0, -2.8, .8), (1.8, 1.6, .2), dark); cube((0, -3.6, 1.0), (1.8, .2, 1.8), dark)
cyl((0, -2.8, 0), .12, .8, 6, steel); cyl((0, -2.8, 0), .7, .1, 8, steel, .1)
# a soft lamp on the floor beside the desk
cyl((-6, -4, 0), .5, 2.8, 6, dark, .3); cyl((-6, -4, 2.8), .5, .6, 6, warm, .3)
lite("POINT", (1, .65, .25), 300, (-6, -4, 3.2))
lite("SUN", (.4, .5, 1), 3, (22, -14, 10), (0, 0, 2)); lite("SUN", (.9, .3, .6), 2, (-20, 20, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .01, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.8)); co.location = t + Vector((14, -38, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
