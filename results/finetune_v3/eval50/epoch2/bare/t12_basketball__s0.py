import bpy, bmesh, random, math
from mathutils import Vector
random.seed(869)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, em=0, rough=.7):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
court, court2, line, orange, black = hue((.22, .1, .05)), hue((.3, .15, .07)), hue((.7, .7, .65)), hue((.8, .25, .04), rough=.5), hue((.02, .02, .02), rough=.5)
rim, net, steel, hoopboard, glass = hue((.9, .15, .05)), hue((.75, .75, .7)), hue((.15, .15, .17), rough=.4), hue((.6, .6, .55)), hue((.25, .35, .4), rough=.1)
bulb, teal, cyan = hue((1, .75, .3), 10), hue((.1, .55, .55), 5), hue((.2, .6, 1), 5)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("b", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def ball(at, r, m, rot):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * 1.02, v.co.y, v.co.z)) * random.uniform(.98, 1.02)
    return put(bm, m, at, rot)
def bar(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return put(bm, m)
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    return put(bm, m, at, rot)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=4.5, radius2=10.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.3, .2)))
    v.co.z -= 1.5
put(bm, court)
for i in range(5): drum((0, 0, .02 + i * .015), 9.2 - i * 1.7, .02, 10, court2 if i % 2 else court)
for a in range(10):
    x, y = math.cos(a * .628) * 8.2, math.sin(a * .628) * 8.2
    bar((x * .98, y * .98, .03), (x * 1.02, y * 1.02, .03), .12, line)
for i in range(10):
    a, b = i * .628, (i + 1) * .628
    bar((math.cos(a) * 8.2, math.sin(a) * 8.2, .04), (math.cos(b) * 8.2, math.sin(b) * 8.2, .04), .12, line)
drum((0, 0, .02), 1.9, .03, 10, line); drum((0, 0, .03), 1.7, .03, 10, court)
# the hoop: pole, arm, backboard with glass, rim, net
bar((6.4, 0, 0), (6.4, 0, 4.2), .35, steel); bar((6.4, 0, 4.2), (4.4, 0, 4.9), .22, steel)
bar((4.4, 0, 1.4), (4.4, 0, 4.9), .12, steel)
drum((3.4, 0, 3.3), .08, 2.0, 4, steel).rotation_euler = (0, math.pi / 2, 0)
bar((2.9, 0, 2.0), (2.9, 0, 4.6), .25, hoopboard)
for s in (-1, 1): bar((2.9, s * 1.1, 2.2), (2.9, s * 1.1, 4.4), .1, steel)
bar((2.9, -1.1, 4.4), (2.9, 1.1, 4.4), .1, steel)
for s in (-1, 1): bar((2.9, s * .6, 3.6), (2.9, s * .6, 4.1), .06, hoopboard)
drum((2.3, 0, 3.0), .5, .12, 8, rim, rot=(0, math.pi / 2, 0))
for i in range(8):
    a, b = i * .785, (i + 1) * .785
    bar((2.3 + math.cos(a) * .5, math.sin(a) * .5, 3.0), (2.5 + math.cos(b) * .2, math.sin(b) * .2, 2.2), .04, net)
    bar((2.3 + math.cos(b) * .5, math.sin(b) * .5, 3.0), (2.5 + math.cos(a) * .2, math.sin(a) * .2, 2.2), .04, net)
# the ball, larger than life, with its seams
R = 3.6
ball((0, 0, R + .3), R, orange, (0, 0, 0))
def seam(fn, off, w):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=R + off)
    for v in bm.verts:
        if abs(fn(v.co) * 2 / R - .5) > w: v.co = Vector((10, 10, 10))
    return put(bm, black, (0, 0, R + .3))
seam(lambda c: c.x, .05, .025); seam(lambda c: c.z, .05, .025)
seam(lambda c: math.atan2(c.y, c.x) * 2 / math.pi, .05, .03)
seam(lambda c: math.atan2(c.z, c.x) * 2 / math.pi, .05, .03)
for i in range(260):
    a, b = random.uniform(0, 6.28), random.uniform(-1.2, 1.2)
    p = Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b))) * (R + .06)
    drum(p, .09, .05, 5, orange, rot=p.to_track_quat('Z', 'Y').to_euler())
# scoreboard on a stand and a few hoopside details
bar((-6.4, 0, 0), (-6.4, 0, 3.2), .3, steel); bar((-6.4, 0, 3.2), (-5.2, 0, 3.6), .2, steel)
bar((-4.8, 0, 2.6), (-4.8, 0, 4.0), .12, steel)
drum((-4.2, 0, 3.4), .06, 1.8, 4, steel).rotation_euler = (0, math.pi / 2, 0)
bar((-3.5, 0, 2.9), (-3.5, 0, 3.9), .2, steel)
drum((-3.2, 0, 3.4), .5, .1, 6, cyan, rot=(0, math.pi / 2, 0))
for i in range(4): bar((-3.0, -1.2 + i * .8, 3.4), (-3.0, -1.2 + i * .8, 3.6), .08, bulb)
for s in (-1, 1): bar((-1.5, s * 4.6, 0), (-1.5, s * 4.6, 5.2), .2, steel); bar((-1.5, s * 4.6, 5.2), (-1.5, s * 4.6, 5.9), .08, bulb)
lamp("POINT", (1, .7, .3), 900, (-1.5, -4.6, 5.9)); lamp("POINT", (1, .7, .3), 900, (-1.5, 4.6, 5.9)); lamp("POINT", (.2, .6, 1), 500, (-3, 0, 3.4))
lamp("SUN", (1, .65, .3), 5.5, (-20, -14, 10), (0, 0, 2)); lamp("SUN", (.3, .6, .9), 2.5, (16, 18, 9), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((-8, -46, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
