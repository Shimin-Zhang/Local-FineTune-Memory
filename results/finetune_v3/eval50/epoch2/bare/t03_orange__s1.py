import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(658)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def mat(c, e=0, r=.8):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
wood, wood2, peel, peel2, peel3, stem, leaf, leaf2, fruit, glow = (
    mat((.22, .12, .06)), mat((.15, .08, .045)), mat((.85, .32, .03)), mat((.7, .24, .03)), mat((.9, .4, .05)),
    mat((.18, .13, .06)), mat((.1, .35, .08)), mat((.18, .45, .1)), mat((.5, .08, .04)), mat((1, .55, .15), 6))
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    o.data.materials.append(m); sc.collection.objects.link(o); return o
def ball(r, at, m, sq=(1, 1, 1), jit=0, sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts:
        v.co = V((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) + V((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit)))
    return put(bm, m, at)
def tube(r, r2, h, n, at, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at, rot)
def stick(a, b, t, m):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ V((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return put(bm, m)
def shine(at, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = (1, .55, .15); L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# wooden board on a tapered rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4.5, radius2=9.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.3, .2)))
    v.co.z -= 1.5
put(bm, wood2)
tube(9.2, 9.2, .5, 9, (0, 0, -.25), wood)
for i in range(3): tube(9.2 - i * .3, 9.2 - i * .3, .06, 9, (0, 0, .25 + i * .02), wood2 if i % 2 else wood)
# the orange: a faceted, dimpled skin made of many small overlapping bumps
R = 4.0
for i in range(46):
    th, ph = random.uniform(0, 6.28), random.acos(random.uniform(-1, 1))
    n = V((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph))); p = n * R
    ball(random.uniform(.55, .85), p * .98, (peel, peel2, peel3)[i % 3], jit=.04, sub=1)
for i in range(24):
    th, ph = random.uniform(0, 6.28), random.acos(random.uniform(-1, 1))
    n = V((math.sin(ph) * math.cos(th), math.sin(ph) * math.sin(th), math.cos(ph))); p = n * R
    ball(.22, p * 1.0, peel2, jit=.02, sub=1)
# stem nub and a single small leaf on a short stalk
tube(.35, .25, .8, 6, (0, 0, R - .1), stem)
stick((0, 0, R + .4), (.6, .1, R + 1.1), .12, stem)
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
for v in bm.verts: v.co = V((v.co.x * 1.1, v.co.y * .22, v.co.z * .55))
put(bm, leaf, (1.5, .1, R + 1.5), (0, .25, .2))
stick((.6, .1, R + 1.1), (2.4, .2, R + 1.7), .05, leaf2)
# a cut half orange showing segments, with a glowing juice inside
hx, hy = -5.6, -1.6
tube(2.7, 2.7, 1.3, 10, (hx, hy, .25), peel3)
tube(2.4, 2.4, .1, 10, (hx, hy, 1.55), peel)
tube(2.0, 2.0, .1, 10, (hx, hy, 1.6), glow)
for k in range(8):
    a = k * math.pi / 4
    stick((hx, hy, 1.7), (hx + math.cos(a) * 1.9, hy + math.sin(a) * 1.9, 1.7), .12, peel)
shine((hx, hy, 2.6), 450)
# small fruit and a few leaves on the board
for i, (x, y) in enumerate(((6.0, -3.0), (6.8, -1.2), (4.8, -4.4))):
    ball(.8, (x, y, .8), fruit, (1, 1, .85), .05)
for x, y, a in ((-3.5, 4.2, .3), (4.2, 4.8, -.5), (0, 6.2, .1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.8)
    for v in bm.verts: v.co = V((v.co.x * 1.2, v.co.y * .2, v.co.z * .5))
    put(bm, leaf2, (x, y, .4), (0, 0, a))
# lights: warm key from the left, cool rim from behind right
for c, w, p in (((1, .6, .3), 5, (-26, -14, 10)), ((.3, .5, 1), 2, (20, 22, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (V((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
aim = V((0, 0, 3)); co.location = aim + V((8, -42, 26))
co.rotation_euler = (aim - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
