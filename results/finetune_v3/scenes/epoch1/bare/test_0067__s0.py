import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1749)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
P = {}
def tone(k, rgb, e=0, r=.9):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = e
    P[k] = m
for k, c in (("bank", (.1, .22, .08)), ("grass", (.14, .26, .1)), ("water", (.05, .2, .28)), ("thatch", (.45, .32, .12)), ("thatch2", (.32, .22, .09)),
             ("plank", (.3, .2, .12)), ("post", (.15, .1, .07)), ("reed", (.35, .3, .12)), ("trunk", (.15, .1, .07)), ("leaf", (.1, .22, .1)), ("swan", (.9, .9, .85)),
             ("beak", (.7, .3, .05)), ("stone", (.3, .3, .32)), ("nest", (.4, .32, .18))): tone(k, c)
tone("lake", (.05, .22, .3), r=.2); tone("window", (1, .65, .25), 7); tone("lantern", (1, .75, .3), 14)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(P[k]); return o
def blk(at, s, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, k, at, rot)
def rnd(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at, rot)
def gable(at, w, d, h, k):
    bm = bmesh.new(); p = [bm.verts.new(c) for c in ((-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0), (0, -d / 2, h), (0, d / 2, h))]
    for f in ((0, 1, 4), (2, 3, 5), (0, 4, 5, 3), (1, 2, 5, 4), (0, 3, 2, 1)): bm.faces.new([p[i] for i in f])
    return mk(bm, k, at)
def orb(at, r, k, s=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    return mk(bm, k, at)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# island base: grassy mound over a rough keel, lake around it
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=4, radius2=12.5, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
mk(bm, "water")
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=11.5, radius2=7.5, depth=1.4)
for v in bm.verts: v.co += Vector((random.uniform(-.5, .5), random.uniform(-.5, .5), 0)); v.co.z += .7
mk(bm, "bank")
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6.5, radius2=4.5, depth=.5)
for v in bm.verts: v.co += Vector((random.uniform(-.3, .3), random.uniform(-.3, .3), 0)); v.co.z += .25
mk(bm, "grass")
# swan house on stilts: four posts, deck, walls, thatched roof, door, windows, lantern
for sx in (-1, 1):
    for sy in (-1, 1): rnd((-2 + sx * 2.3, 3.5 + sy * 2.0, 0), .22, 3.2, 5, "post")
blk((-2, 3.5, 3.2), (6.4, 5.4, .3), "plank")
blk((-2, 3.5, 3.5), (4.8, 4.0, 2.6), "plank")
gable((-2, 3.5, 6.1), 6.6, 5.2, 2.2, "thatch"); gable((-2, 3.5, 6.1), 5.2, 4.4, 2.9, "thatch2")
for i in range(5): blk((-2, 3.5 - 2.0 + i * 1.0, 6.15), (6.4, .12, .12), "thatch2")
blk((-2, 1.45, 3.5), (1.2, .12, 2.0), "post")
for sx in (-1, 1): blk((-2 + sx * 1.7, 1.45, 4.6), (.9, .12, .9), "window")
lamp("POINT", (1, .65, .25), 300, (-2, .5, 4.5))
blk((-2, 3.5, 3.5), (.3, .3, .5), "post")
rnd((-2, 1.3, 4.0), .3, .5, 6, "lantern"); rnd((-2, 1.3, 4.5), .4, .2, 6, "post", .1); lamp("POINT", (1, .75, .3), 160, (-2, 1.3, 4.2))
for i in range(8): blk((-2, 1.0 - i * .5, 3.2 - i * .35), (1.8, .5, .12), "plank")
# feeding jetty out into the lake with a post, a bucket and a lantern
blk((0, -2.5, .5), (1.6, 9.0, .25), "plank")
for i in range(5):
    for sx in (-.7, .7): rnd((sx, 1.8 - i * 1.8, 0), .12, .6, 5, "post")
rnd((.9, -6.5, .75), .12, 2.0, 5, "post"); rnd((.9, -6.5, 2.7), .35, .3, 6, "lantern"); lamp("POINT", (1, .75, .3), 150, (.9, -6.5, 2.8))
blk((-.5, 1.0, .75), (.5, .5, .5), "plank")
# swan nest on a small bank, with two swans
rnd((5.5, -1.5, .6), 1.2, .4, 8, "grass"); rnd((5.5, -1.5, 1.0), .9, .3, 8, "nest", .7)
for a in (0, 1):
    x, y = 5.5 + a * .5 - .25, -1.5
    orb((x, y, 1.6), .5, "swan", (1.3, .9, .8)); blk((x + .5, y, 2.0), (.3, .22, 1.0), "swan", (0, -.3, 0)); orb((x + .75, y, 3.0), .22, "swan")
    blk((x + 1.0, y, 2.9), (.4, .12, .12), "beak")
# swan house signboard: two posts, a board, a painted swan and a post lantern
blk((-6.5, -2.5, .6), (.2, .2, 3.4), "post"); blk((-4.2, -2.5, .6), (.2, .2, 3.4), "post")
blk((-5.3, -2.5, 2.6), (2.8, .15, 1.4), "plank"); blk((-5.3, -2.6, 3.0), (2.0, .06, .5), "swan"); blk((-5.3, -2.6, 2.8), (.8, .06, .1), "beak")
rnd((-3.8, -3.5, 0), .1, 2.8, 5, "post"); rnd((-3.8, -3.5, 2.8), .3, .4, 6, "lantern"); lamp("POINT", (1, .75, .3), 120, (-3.8, -3.5, 3.0))
# reeds, boulders, a tree and a bench
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(6.8, 10.5)
    if abs(a - 4.7) < .4: continue
    rnd((math.cos(a) * r, math.sin(a) * r, .3), .1, random.uniform(1.2, 2.4), 4, "reed", .02)
for i in range(5):
    a = random.uniform(0, 6.28); r = random.uniform(7.5, 10.5)
    if abs(a - 4.7) < .4: continue
    orb((math.cos(a) * r, math.sin(a) * r, .6), random.uniform(.5, 1.0), "stone", (1, 1, .7))
rnd((6.5, 5.5, .6), .35, 3.5, 5, "trunk", .25)
for k in range(3): orb((6.5 + random.uniform(-1, 1), 5.5 + random.uniform(-1, 1), 4.5 + k * .6), 1.6 - k * .3, "leaf")
blk((-6.5, 5.5, 1.0), (2.0, .6, .15), "plank"); blk((-6.5, 5.9, 1.1), (2.0, .1, .8), "plank")
for sx in (-.8, .8): blk((-6.5 + sx, 5.5, .6), (.15, .5, .4), "post")
lamp("SUN", (1, .5, .35), 5, (-22, -14, 7), (0, 0, 2)); lamp("SUN", (.3, .6, .8), 2.5, (18, 20, 10), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((8, -56, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
