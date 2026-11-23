import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(887)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def tone(c, e=0, r=.85):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
oak, oak2, red, white, cream, steel, steam, leaf, berry, plate, band = (tone((.28, .17, .09)), tone((.2, .12, .06)), tone((.75, .07, .06), r=.3), tone((.85, .85, .82), r=.35),
    tone((.8, .72, .55)), tone((.5, .52, .55), r=.3), tone((.8, .85, .9), 1.2), tone((.1, .3, .1)), tone((.5, .08, .1)), tone((.6, .6, .62)), tone((.9, .6, .1)))
def put(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cup(p, r1, r2, h, n, m, top=True):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=top, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, p)
def bar(a, b, t, m):
    a, b = V(a), V(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ V((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return put(bm, m)
def orb(p, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return put(bm, m, p)
def lite(kind, p, c, w, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=4.5, radius2=8, depth=2.2)
for v in bm.verts:
    v.co.z -= 1.1
    if v.co.z < -1: v.co += V((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.2, .2)))
put(bm, oak2)
for i in range(8):
    a = i * .785 + .39; bar((math.cos(a) * 7.4, math.sin(a) * 7.4, 0), (math.cos(a) * 7.4, math.sin(a) * 7.4, .25), .35, oak)
# a big mug on a plate: body, rim, band, white handle, coffee
cup((0, 0, .1), 3.0, 3.0, .15, 10, plate)
cup((0, 0, .25), 2.2, 2.45, 3.6, 10, red)
cup((0, 0, 3.85), 2.45, 2.45, .25, 10, red); cup((0, 0, 4.0), 2.2, 2.2, .1, 10, cream)
cup((0, 0, 1.0), 2.35, 2.35, .5, 10, band)
for k in range(10):
    a = k * .628 + .31; orb((math.cos(a) * 2.38, math.sin(a) * 2.38, 1.25), .17, white, .6)
for k in range(12):
    a = k * .5236; bar((math.cos(a) * 3.0, math.sin(a) * 3.0, 3.9), (math.cos(a) * 3.0, math.sin(a) * 3.0, 4.1), .22, white)
for k in range(7):
    a = -math.pi * .5 + (k - 3) * .38
    bar((2.45 * math.cos(a - .1), 2.45 * math.sin(a - .1), 3.0), (2.45 * math.cos(a + .1), 2.45 * math.sin(a + .1), 3.0), .55, white)
for k in range(7):
    a = -math.pi * .5 + (k - 3) * .22
    bar((3.0 * math.cos(a - .06), 3.0 * math.sin(a - .06), 3.0), (3.0 * math.cos(a + .06), 3.0 * math.sin(a + .06), 3.0), .3, white)
for k in range(5):
    a = k * 1.25; bar((2.3 * math.cos(a), 2.3 * math.sin(a), 3.4), (2.3 * math.cos(a), 2.3 * math.sin(a), 3.8), .12, band)
lite("POINT", (0, 0, 4.7), (1, .7, .35), 300)
# steam rising from the mug
for k in range(5): orb((.2 * math.sin(k * 1.5), .1 * k, 5.0 + k * .9), .35 + .1 * k, steam, 1.2)
# a teapot, a small cup, a spoon and a leafy sprig on the table
cup((-4.6, -1.5, .1), 1.1, 1.1, .1, 8, plate); cup((-4.6, -1.5, .2), 1.0, .7, 1.0, 8, white); cup((-4.6, -1.5, 1.2), .7, .35, .5, 8, white)
bar((-3.9, -1.5, .8), (-2.9, -1.5, 1.4), .16, white); bar((-5.3, -1.5, .9), (-5.9, -1.5, 1.5), .16, white); orb((-4.6, -1.5, 1.75), .15, band)
cup((3.6, -2.4, .1), .8, .8, .1, 8, plate); cup((3.6, -2.4, .2), .5, .6, .8, 8, white); cup((3.6, -2.4, 1.0), .45, .45, .06, 8, cream)
bar((1.5, -3.6, .12), (2.2, -4.0, .12), .12, steel); orb((2.4, -4.1, .12), .22, steel, .5)
bar((-1.2, 3.6, .1), (-1.8, 4.2, .1), .08, leaf); orb((-2.0, 4.3, .12), .2, leaf, .6); orb((-.9, 3.5, .12), .17, leaf, .6)
# a small red-and-white cake with a candle, and a berry bowl
cup((4.2, 3.2, .1), 1.0, 1.0, .1, 8, plate); cup((4.2, 3.2, .2), .8, .8, .8, 8, red); cup((4.2, 3.2, 1.0), .82, .82, .12, 8, cream)
cup((4.2, 3.2, 1.12), .06, .06, .7, 5, white); cup((4.2, 3.2, 1.82), .12, .02, .22, 5, tone((1, .65, .15), 20))
lite("POINT", (4.2, 3.2, 2.4), (1, .6, .2), 160)
cup((-4.2, 3.0, .1), 1.0, 1.0, .1, 8, plate); cup((-4.2, 3.0, .2), .9, .6, .5, 8, steel)
for k in range(5): orb((-4.2 + .3 * math.cos(k * 1.3), 3.0 + .3 * math.sin(k * 1.3), .75), .22, berry, .9)
lite("SUN", (-14, -10, 7), (1, .62, .35), 4.5, (0, 0, 1)); lite("SUN", (12, 14, 8), (.45, .55, 1), 2.2, (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .012, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = V((0, 0, 2.4)); co.location = t + V((9, -33, 21))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
