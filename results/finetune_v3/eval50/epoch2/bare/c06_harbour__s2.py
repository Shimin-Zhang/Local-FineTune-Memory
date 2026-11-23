import bpy, bmesh, random, math
from mathutils import Vector
random.seed(828)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, em=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .85
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
sea, shore, plank, post = dye((.03, .12, .17)), dye((.17, .14, .1)), dye((.3, .2, .12)), dye((.15, .1, .07))
white, red, hull1, hull2 = dye((.7, .68, .62)), dye((.6, .08, .06)), dye((.1, .3, .4)), dye((.5, .2, .1))
crate, crate2, rope, glass = dye((.4, .28, .15)), dye((.25, .2, .14)), dye((.5, .42, .25)), dye((1, .75, .3), 14)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def line(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def hull(at, L, W, m, tilt=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = 1 if v.co.z < 0 else .55
        v.co = Vector((v.co.x * L * k + (.7 * L if v.co.x > 0 and v.co.z > 0 else 0), v.co.y * W * k, v.co.z * 1.0 + (.5 if v.co.z > 0 else 0)))
    return make(bm, m, at, (0, 0, tilt))
# water slab with a rough tapered underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
    v.co.z -= 2
make(bm, sea)
# shore at the back with a stepped edge
blk((0, 8.2, -.1), (16, 5, 1.0), shore)
for i in range(5): blk((-7 + i * 3.5, 5.3, -.1), (3.4, .8, .6 + (i % 2) * .2), shore)
# pier running out into the water, planks on piles
for i in range(18):
    blk((-1.8, 4.8 - i * .72, .15), (3.2, .66, .22), plank if i % 2 else post)
for i in range(6):
    for s in (-1, 1): cyl((s * 1.5, 4.2 - i * 2.4, -.4), .17, 1.2, 5, post)
for i in range(8): cyl((1.6, 4.6 - i * .9, .37), .07, 1.0, 4, rope)
# two boats: a blue fishing boat tied to the pier, a red dinghy beside it
hull((-5.5, -1.5, -.1), 6.0, 2.2, hull1, .15)
blk((-5.8, -1.5, .75), 1.6, 1.4, white, (.15, 0, .15)); blk((-5.8, -1.5, 1.9), 1.8, 1.6, red, (.15, 0, .15))
line((-4.2, -1.3, .8), (-3.0, -1.1, 3.2), .1, post); line((-7.5, -1.8, .8), (-8.2, -2.0, 2.6), .08, post)
hull((2.5, -4.5, -.1), 3.6, 1.6, hull2, -.5)
for i in range(3): blk((2.5, -4.5, .5 + i * .0), (3.0 - i * .5, 1.2 - i * .3, .1), white, (0, 0, -.5))
# lighthouse on the headland: white tower, red band, lantern with a strong glow
cyl((7.5, 7.5, .8), 2.2, 1.2, 8, shore, 1.8)
cyl((7.5, 7.5, 2.0), 1.5, 6.0, 8, white, 1.0)
cyl((7.5, 7.5, 5.0), 1.2, 1.2, 8, red, 1.1)
cyl((7.5, 7.5, 6.4), 1.0, 1.4, 8, glass, .9)
cyl((7.5, 7.5, 7.8), 1.4, 1.0, 8, red, .1)
blk((6.3, 6.4, 2.6), (.5, .5, 1.0), post)
for i in range(5): cyl((7.5 + math.cos(i * 1.26) * 2.0, 7.5 + math.sin(i * 1.26) * 2.0, .8), .3, .6, 5, white, .25)
# crates, barrels, net and a lamp post at the pier head
for i, (x, y, z, t) in enumerate(((-4, 6.5, .8, .3), (-2.6, 6.8, .8, -.2), (-3.4, 6.6, 1.6, .6), (-.5, 7.2, .8, .1), (1.2, 6.6, .8, .5), (-4.2, 3.0, .37, .2), (-.6, 2.2, .37, -.4))):
    blk((x, y, z), (1.1, 1.1, .9), crate if i % 2 else crate2, (0, 0, t))
for i in range(3): cyl((4.2 + i * .9, 6.8 - i * .3, .8), .45, 1.0, 7, post, .4)
cyl((-1.6, 4.8, .37), .09, 2.6, 5, post); cyl((-1.6, 4.8, 2.9), .3, .4, 6, glass)
line((-1.6, 4.8, 2.9), (-1.6, 4.8, 3.3), .06, rope)
for i in range(6): blk((-6 + i * .5, 8.2 - (i % 2) * .3, 1.0), (.1, .1, .1), rope)
for i in range(10): blk((random.uniform(-9, 9), random.uniform(-9, 3), -.05), (.6, .4, .12), dye((.25, .3, .3)), (0, 0, random.uniform(0, 3)))
def beam(kind, at, col, e, aim=None):
    L = bpy.data.lights.new("b", kind); L.color, L.energy = col, e
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
beam("SUN", (-24, -14, 8), (.55, .65, 1), 4.5, (0, 0, 1))
beam("SUN", (20, 22, 12), (1, .5, .3), 2.2, (0, 0, 1))
beam("POINT", (7.5, 7.5, 7.2), (1, .75, .3), 1800); beam("POINT", (-1.6, 4.8, 2.9), (1, .7, .3), 200)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((12, -50, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
