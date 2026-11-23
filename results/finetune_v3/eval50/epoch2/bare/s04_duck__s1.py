import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(519)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def paint(c, glow=0, rough=.5):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = glow
    return m
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def ball(at, r, m, sq=(1, 1, 1), sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co = V((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return put(bm, m, at)
def tube(a, b, r, m, n=6):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r * .85, depth=d.length)
    for v in bm.verts: v.co = q @ V((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return put(bm, m)
def lamp(at, col, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
rubber, beak, eye, pond = paint((1, .68, .04), rough=.35), paint((1, .3, .05), rough=.3), paint((.02, .02, .02), rough=.1), paint((.04, .2, .3), rough=.05)
rim, tile1, tile2, bulb, toy = paint((.2, .8, 1), 3, .1), paint((.1, .3, .45), rough=.5), paint((.15, .4, .55), rough=.5), paint((1, .8, .3), 14), paint((.9, .1, .3), rough=.4)
# round bath-tub of pond water on a tiled deck
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=11, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    v.co.z -= 1.5
put(bm, tile1)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=9.2, radius2=9.2, depth=.5)
for v in bm.verts: v.co.z += .25
put(bm, pond)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=9.7, radius2=9.7, depth=.4)
for v in bm.verts: v.co.z += .6
put(bm, rim)
for i in range(10):
    a = i * math.tau / 10
    ball((math.cos(a) * 9.7, math.sin(a) * 9.7, .8), .45, bulb, (1.2, 1, .6))
lamp((0, 0, 1.3), (.3, .85, 1), 450)
for i in range(18):
    a, r = random.uniform(0, 6.28), random.uniform(0, 10)
    x, y = math.cos(a) * r, math.sin(a) * r
    if r > 8.5: continue
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = V((v.co.x * 1.7, v.co.y * 1.7, v.co.z * .15))
    put(bm, tile2 if (i + int(r)) % 2 else tile1, (x, y, .12), (0, 0, a))
# the duck: body, chest, head, beak, eyes, wings, tail, feet
ball((0, 0, 2.2), 3.2, rubber, (1.1, 1, .95))
ball((.9, -.7, 1.8), 2.0, rubber, (1, 1, .9))
ball((1.4, -.9, 5.4), 1.9, rubber, (1, 1, 1.05))
ball((2.5, -1.9, 5.1), .75, beak, (1.2, 1, .55))
for s in (-1, 1):
    ball((2.0, -1.9 + s * .9, 5.8), .28, eye)
    ball((.6, s * 2.6, 2.6), 1.5, rubber, (.25, 1, .8)); ball((-.4, s * 2.2, 2.8), 1.0, rubber, (.2, 1, .6))
ball((-3.3, 0, 3.2), 1.2, rubber, (1.1, .8, 1.2)); ball((-4.3, 0, 4.2), .8, rubber, (1, .6, 1))
for s in (-1, 1):
    ball((.6, s * 1.0, .5), .5, beak, (1.6, .5, .25))
# rubber ring and floating toys
for i in range(8):
    a = i * math.tau / 8
    ball((math.cos(a) * 5.4, math.sin(a) * 5.4, .6), .6, toy if i % 2 else rubber, (1.3, 1, .8))
ball((-6, 5, .9), .9, toy, (1, 1, .7)); ball((6.5, 4.5, .8), .6, rubber, (1, 1, .8))
# neon bulb sign and a little stool with a towel
for i in range(7):
    ball((-7 + i * 2.2, 8.2, 6.5 - abs(i - 3) * .8), .4, bulb)
lamp((-2, 7, 6), (1, .75, .3), 500)
ball((-7.5, -6, .8), 1.1, tile2, (1, 1, .5)); ball((-7.5, -6, 1.4), 1.3, tile2, (1, 1, .2))
ball((7, -6.5, .7), 1.2, paint((.8, .8, .85), rough=.8), (1.2, .8, .25))
for col, w, p in (((1, .55, .3), 5, (-24, -14, 9)), ((.2, .8, 1), 2.4, (22, 20, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (V((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tgt = V((0, 0, 3)); co.location = tgt + V((9, -46, 28))
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
