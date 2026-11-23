import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1682)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(c, glow=0, r=.8):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if glow: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = glow
    return m
oak, oak2, floor, plaster, wall2, vase, petal, candle, brass, cloth, leaf, rug, rug2 = (paint((.3, .17, .08)), paint((.22, .12, .06)), paint((.16, .11, .08)), paint((.28, .25, .22)), paint((.2, .17, .16)),
    paint((.1, .45, .25), .6, .3), paint((.9, .5, .6)), paint((1, .65, .25), 14), paint((.6, .4, .12), 0, .4), paint((.5, .1, .12)), paint((.1, .3, .12)), paint((.45, .12, .1)), paint((.12, .22, .3)))
def piece(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return piece(bm, m, at, (0, 0, rz))
def vase_(at, r0, r1, h, n, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r0, radius2=r1, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return piece(bm, m, at, rot)
def stick(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return piece(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def flame(at, w):
    L = bpy.data.lights.new("f", "POINT"); L.color = (1, .6, .22); L.energy = w
    o = bpy.data.objects.new("f", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=10.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .3)))
piece(bm, floor)
for i in range(8): slab((0, -8 + i * 2.2, 0), (21, 2.2, .06), floor if i % 2 else oak2)
slab((0, -.5, 0), (12, 9, .12), rug); slab((0, -.5, .12), (10.5, 7.5, .06), rug2); slab((0, -.5, .18), (8.5, 5.5, .05), rug)
slab((0, 7.5, 0), (21, .6, 9), plaster); slab((-10.2, 0, 0), (.6, 15.6, 9), wall2)
for i in range(3): slab((-8 + i * 8, 7.1, 0), (3.4, .3, 8.2), plaster)
slab((-9.9, -2.5, 2.4), (.2, 3.4, 3.6), paint((.08, .05, .04))); slab((-9.9, -2.5, 2.6), (.3, 3, 3.2), paint((.04, .03, .03)))
slab((-9.9, -2.5, 4.2), (.3, 3, .15), oak2)
# the table: plank top, four tapered legs, a stretcher frame, a turned apron
for i in range(6): slab((0, -2.2 + i * .88, 3.2), (7.4, .84, .3), oak if i % 2 else oak2)
slab((0, 0, 2.9), (7, 5.6, .35), oak2, 0, .96)
for sx in (-1, 1):
    for sy in (-1, 1):
        vase_((sx * 3.2, sy * 2.2, 0), .4, .28, 3.0, 6, oak); vase_((sx * 3.2, sy * 2.2, .5), .5, .5, .25, 6, oak2); vase_((sx * 3.2, sy * 2.2, 2.6), .5, .5, .25, 6, oak2)
for sy in (-1, 1): slab((0, sy * 2.2, .8), (6.4, .2, .25), oak2)
for sx in (-1, 1): slab((sx * 3.2, 0, .8), (.2, 4.4, .25), oak2)
# the green vase: a faceted body, a neck and a rim, with a bouquet of flowers
vase_((0, 0, 3.5), .75, .5, .9, 8, vase); vase_((0, 0, 4.4), .5, .3, .5, 8, vase); vase_((0, 0, 4.9), .38, .38, .12, 8, vase)
vase_((0, 0, 3.9), .62, .62, .12, 8, paint((.06, .3, .16), 0, .3))
for i in range(7):
    a = i * 2.4; x, y = .3 * math.cos(a), .3 * math.sin(a)
    stick((x * .5, y * .5, 5.0), (x * 1.6, y * 1.6, 6.6), .05, leaf, 4)
    for k in range(5):
        b = k * 1.26
        slab((x * 1.6 + .22 * math.cos(b), y * 1.6 + .22 * math.sin(b), 6.6), (.2, .12, .1), petal if i % 2 else paint((.95, .75, .3)), b)
# a candlestick with a lit candle, a cloth and a bowl on the table
vase_((2.2, 1.4, 3.5), .35, .25, .2, 6, brass); vase_((2.2, 1.4, 3.7), .12, .12, .8, 6, paint((.8, .75, .6))); vase_((2.2, 1.4, 4.5), .09, .02, .25, 5, candle)
flame((2.2, 1.4, 4.9), 500)
slab((-2, -1.2, 3.5), (2.6, 1.8, .12), cloth, .3); slab((-2, -1.2, 3.62), (2.2, 1.4, .08), cloth, .3, .9)
vase_((-2.2, 1.2, 3.5), .5, .3, .3, 7, paint((.5, .5, .55), 0, .3))
slab((-7.5, -2, 0), (2.4, 2.4, .9), oak2, .4, .8); slab((-7.5, -2, .9), (2, 2, .15), cloth, .4)
slab((6, -3, 0), (1.4, 1.4, 1.5), oak, .2, .7)
slab((-9.4, 3, 6), (.2, 1.8, 2.2), paint((.1, .15, .3))); slab((-9.4, 3, 6.3), (.25, 1.2, 1.4), paint((.8, .5, .15)))
flame((-8.6, 3, 6.8), 200)
for col, w, p in (((1, .65, .35), 5, (-26, -20, 12)), ((.4, .55, 1), 2.4, (24, 22, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((10, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
