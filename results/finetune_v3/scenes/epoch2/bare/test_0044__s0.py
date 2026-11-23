import bpy, bmesh, random, math
from mathutils import Vector
random.seed(668)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, em=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
def spawn(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return spawn(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0.0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return spawn(bm, m, at, rot)
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return spawn(bm, m)
def lamp(kind, at, col, w, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
earth, rock, gravel, gravel2, gravel3 = pigment((.16, .13, .09)), pigment((.2, .18, .17)), pigment((.42, .38, .32)), pigment((.3, .27, .24)), pigment((.5, .46, .4))
water, hull, steel, belt, orange, cabin = pigment((.04, .12, .15)), pigment((.7, .1, .05)), pigment((.2, .22, .25)), pigment((.05, .05, .06)), pigment((.9, .4, .05)), pigment((.8, .75, .6))
flood, lampm, headl = pigment((.03, .1, .14), .6), pigment((1, .8, .4), 14), pigment((1, .95, .8), 25)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .2)))
    v.co.z -= 1.5
spawn(bm, earth)
# flooded pit behind: sunken dark water with a rough rim of rock
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6.2, radius2=6.2, depth=.3)
for v in bm.verts: v.co += Vector((random.uniform(-.4, .4), random.uniform(-.4, .4), 0)); v.co.y *= .8
spawn(bm, flood, (-2, 6.5, .1))
for i in range(11):
    a = i * .57 + .2; cone((-2 + 6.6 * math.cos(a), 6.5 + 5 * math.sin(a), 0), random.uniform(.6, 1.1), random.uniform(.7, 1.4), 5, rock, .3)
# graded heaps: coarse, medium, fine, in different sizes
for (x, y, r, h, m) in ((6.5, 2.5, 3.2, 2.6, gravel3), (2.5, 1.5, 2.4, 1.9, gravel), (6.5, -2.5, 1.9, 1.4, gravel2), (-3.5, -3, 1.6, 1.1, gravel3)):
    cone((x, y, 0), r, h, 8, m, .15)
    for i in range(6):
        a = i * 1.05; cone((x + r * .6 * math.cos(a), y + r * .6 * math.sin(a), h * .35), .35, .5, 5, rock, .1)
# floating dredger: hull, deck, cabin, boom arm, suction pipe into the pit, floating
dx, dy = 2.5, 6.0
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 5.2, v.co.y * 2.4, (v.co.z + .5) * 1.0))
    if v.co.x > 0: v.co.y *= .3
spawn(bm, hull, (dx, dy, .05))
blk((dx - .6, dy, 1.0), (3.4, 1.8, .25), steel)
blk((dx - 1.4, dy, 1.25), (1.6, 1.4, 1.2), cabin); blk((dx - 1.4, dy, 2.45), (1.8, 1.6, .2), orange)
blk((dx - 1.4, dy - .72, 1.8), (1.2, .06, .5), lampm)
cone((dx + .6, dy, 1.25), .5, 1.5, 6, orange, .35)
rod((dx + 1.4, dy, 2.2), (dx - 2.6, dy + 1.4, 4.6), .22, steel); rod((dx - 2.6, dy + 1.4, 4.6), (dx - 3.6, dy + 2.2, 1.2), .2, steel)
rod((dx - 3.6, dy + 2.2, 1.2), (dx - 3.4, dy + 3.4, .1), .35, orange)
cone((dx - 3.4, dy + 3.4, .1), .5, .3, 6, orange, .3)
cone((dx + 1.8, dy - .5, 1.25), .12, .8, 5, steel, .12); blk((dx + 1.8, dy - .5, 2.0), (.5, .5, .2), headl)
lamp("POINT", (dx + 1.8, dy - .9, 2.2), (1, .9, .7), 500); lamp("POINT", (dx - 1.4, dy - 1.2, 1.9), (1, .8, .4), 250)
# conveyor: inclined belt on trestles from the dredger to the sorting plant
a, b = Vector((dx - .5, dy - 1.2, 1.4)), Vector((-2.5, -.5, 3.2))
rod(a, b, .7, belt)
for t in (.2, .5, .8):
    p = a.lerp(b, t)
    for s in (-.4, .4): rod((p.x, p.y + s, 0), (p.x, p.y + s, p.z - .2), .12, steel)
# sorting plant: two trommel drums with screens, a hopper, a conveyor discharge
px, py = -5.5, -1.5
blk((px, py, 0), (4.2, 3.2, .5), steel)
for k, (y, r) in enumerate(((-.8, .6), (.8, .45))):
    cone((px, py + y, 1.4), r, 3.4, 8, orange, r, (0, math.pi / 2, 0)).location = (px - 1.7, py + y, 1.4)
    for s in (-1.2, 1.2): blk((px + s, py + y - r, .5), (.2, .2, .9), steel)
blk((px + 2.0, py, .5), (1.0, 2.4, .9), steel)
cone((px + 2.0, py, 1.4), .6, 1.0, 6, steel, .3)
blk((px - 1.8, py - 1.7, .5), (.6, .6, .6), lampm); lamp("POINT", (px - 1.8, py - 2.2, 1.2), (1, .8, .4), 300)
# lamp posts and a small haul road of raked gravel
for (x, y) in ((-8, -5), (9, -5), (0, -6.5)):
    rod((x, y, 0), (x, y, 3.4), .14, steel); blk((x, y, 3.4), (.7, .5, .4), headl)
    lamp("POINT", (x, y, 3.8), (1, .85, .5), 220)
for i in range(8): blk((-1 + i * .5, -5 + math.sin(i) * .6, 0), (1.2, 2.2, .06), gravel2, (0, 0, math.sin(i) * .2))
lamp("SUN", (-26, -14, 8), (.55, .65, 1), 4.5, (0, 0, 1)); lamp("SUN", (22, 22, 10), (1, .5, .25), 2.2, (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 1.2)); co.location = t + Vector((6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
