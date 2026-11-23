import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(427)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
floor, floor2, clay, clay2, soil = pigment((.22, .17, .15)), pigment((.15, .12, .11)), pigment((.55, .22, .12)), pigment((.4, .16, .09)), pigment((.1, .07, .05))
pad, pad2, spine, bloom, bloom2 = pigment((.12, .3, .15)), pigment((.2, .38, .18)), pigment((.8, .8, .7)), pigment((.9, .2, .35), 2), pigment((.9, .5, .25), 2)
lamp, frame, leaf, leaf2 = pigment((1, .65, .3), 14), pigment((.06, .06, .07)), pigment((.1, .3, .12)), pigment((.2, .4, .15))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("x"); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new("x", me); o.location, o.rotation_euler = at, rot; sc.collection.objects.link(o); return o
def block(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = V((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mesh(bm, m, at, rot)
def pot(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, at)
def pad(at, r, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r, radius2=r * .95, depth=h)
    for v in bm.verts: v.co.z += h / 2; v.co += V((random.uniform(-.03, .03), random.uniform(-.03, .03), 0))
    return mesh(bm, m, at, rot)
def lamp(kind, at, col, w, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = col, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab of two tones, rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = V((v.co.x * 18, v.co.y * 18, v.co.z * 3 - 1.5))
    if v.co.z < 0: v.co = V((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
mesh(bm, floor2)
for i in range(6):
    for j in range(6): block((-7.5 + i * 3, -7.5 + j * 3, 0), (2.9, 2.9, .12), floor if (i + j) % 2 else floor2)
# shelf with brackets
block((0, 2, 2.6), (11, 4.2, .35), frame); block((0, 2, 2.3), (10.4, 3.8, .1), clay2)
for sx in (-4, 4): block((sx, .3, 1.0), (.3, .2, 1.6), frame)
# terracotta pot: tapered body, rim, soil, drainage shadow
pot((0, 2, 2.95), 2.0, 2.6, 8, clay, 1.55); pot((0, 2, 5.5), 2.05, .45, 8, clay2, 2.05); pot((0, 2, 5.9), 1.7, .15, 8, soil)
# saguaro: trunk, two arms with elbows, ribs of spines, flowers on top
pad((0, 2, 5.9), 1.0, 6.2, pad)
for sx, z0 in ((-1, 8.0), (1, 9.0)):
    pad((sx * 1.9, 2, z0), .6, 2.0, pad2, (0, math.pi / 2, 0)); pad((sx * 2.7, 2, z0 + 1.0), .6, 2.6, pad, (0, 0, 0))
for k in range(18):
    a = random.uniform(0, 6.28); z = 6.5 + random.uniform(0, 5.2); r = 1.02
    block((math.cos(a) * r, 2 + math.sin(a) * r, z), (.06, .06, .45), spine, (0, 0, 0))
for k in range(5):
    a = k * 1.25; block((math.cos(a) * .5, 2 + math.sin(a) * .5, 12.0), (.4, .4, .5), bloom if k % 2 else bloom2, (0, 0, a))
lamp("POINT", (0, 1, 12.4), (1, .3, .45), 220)
# second pot with a prickly ball and a lamp on the shelf
pot((3.8, 2.5, 2.95), .9, 1.4, 7, clay2, .7)
for k in range(8):
    a = k * .8; pad((3.8 + math.cos(a) * .35, 2.5 + math.sin(a) * .35, 4.3 + (k % 2) * .3), .45, .8, pad2)
for sx in (-4.2,):
    block((sx, 2.5, 2.95), (.15, .15, 2.6), frame); block((sx, 2.5, 5.5), (1.0, 1.0, .8), lamp, top=.7)
    lamp("POINT", (sx, 2.5, 5.6), (1, .65, .3), 600)
# monstera on the floor: pot, stem, split leaves
pot((-5.5, -2, 0), 1.3, 1.8, 7, clay, 1.0)
for k in range(6):
    a = k * 1.05; block((-5.5 + math.cos(a) * .5, -2 + math.sin(a) * .5, 1.8), (.1, .1, 2.2 + (k % 3) * .4), pad2, (math.sin(a) * .4, -math.cos(a) * .4, 0))
    block((-5.5 + math.cos(a) * 1.7, -2 + math.sin(a) * 1.7, 3.8 + (k % 3) * .4), (1.6, 1.3, .1), leaf if k % 2 else leaf2, (0, 0, a))
# watering can, a leaning book stack and a small succulent on the floor
block((5.5, -3, 0), (1.2, 1.0, 1.0), clay2); block((6.2, -3, .3), (1.2, .12, .12), clay, (0, 0, 0)); block((6.7, -3, .8), (.2, .2, .8), clay)
for k, c in enumerate((bloom, pad2, clay)): block((-1.5 + k * .05, -5, k * .35), (2.0, 1.4, .3), c, (0, 0, .1 * k))
pot((-2.5, -5.5, 0), .45, .6, 6, clay, .35); pad((-2.5, -5.5, .6), .35, .5, pad2)
# warm evening light: low amber key, teal rim
lamp("SUN", (-22, -14, 11), (1, .6, .3), 5, (0, 0, 4)); lamp("SUN", (20, 20, 12), (.3, .7, .8), 2, (0, 0, 4))
w = bpy.data.worlds.new("eve"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .012, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); t = V((0, 1, 5.5)); co.location = t + V((16, -54, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
