import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1134)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def dye(k, c, e=0, a=1.0, r=.8):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r; n.inputs["Alpha"].default_value = a
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    M[k] = m
dye("desk", (.17, .09, .06)); dye("brass", (.55, .38, .12), 0, 1, .35); dye("crystal", (.3, .55, 1), .6, .35, .05)
dye("mist", (.5, .3, 1), 2.5, .5); dye("mist2", (.2, .8, 1), 2.5, .45); dye("book", (.35, .05, .12)); dye("book2", (.08, .12, .3))
dye("candle", (1, .6, .2), 20); dye("cloth", (.2, .06, .22)); dye("gold", (.8, .6, .15), 0, 1, .3)
def mk(bm, k, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def ball(p, r, k, s=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    return mk(bm, k, p)
def rod(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, k)
def ring(p, r, n, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=.12)
    return mk(bm, k, p, rot)
def glim(p, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
# round table top, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=4, radius2=9.5, depth=2.6)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    v.co.z -= 1.3
mk(bm, "desk")
ring((0, 0, .02), 9.55, 10, "gold")
# brass stand: foot, stem, three claws cradling the ball
ring((0, 0, .1), 3.4, 8, "brass"); ring((0, 0, .2), 2.9, 8, "brass")
rod((0, 0, .2), (0, 0, 2.4), .7, "brass")
for k in range(3):
    a = k * 2.094 + .5
    rod((0, 0, 2.3), (math.cos(a) * 3.2, math.sin(a) * 3.2, 3.6), .45, "brass")
    ball((math.cos(a) * 3.2, math.sin(a) * 3.2, 3.5), .4, "brass")
# the crystal ball and its swirling mist
ball((0, 0, 5.6), 3.4, "crystal")
for i in range(30):
    a = i * .6; r = 2.6 - i * .055; z = 5.6 + (i - 15) * .17 * math.cos(i * .5)
    ball((math.cos(a) * r, math.sin(a) * r, z), .55 - i * .008, "mist" if i % 2 else "mist2")
ball((0, 0, 5.6), .8, "mist")
glim((0, 0, 5.6), (.5, .4, 1), 1400)
# a cloth runner, open grimoire, a candle in a holder, ink pot, a small crystal
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts: v.co = Vector((v.co.x * 1.6, v.co.y * 8, v.co.z * .08))
mk(bm, "cloth", (0, 0, .06))
for s in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * 1.9, v.co.y * 2.6, v.co.z * .12))
    mk(bm, "book" if s < 0 else "book2", (-3.2 + s * 1.0, -4.2, .25), (0, 0, s * .2))
ball((4.2, -3.5, .3), .7, "brass"); ball((4.2, -3.5, 1.0), .35, "candle")
glim((4.2, -3.5, 1.4), (1, .6, .2), 250)
ball((-5, 4.5, .5), .5, "book2"); ball((-3.9, 4.8, .4), .3, "mist2", (1, 1, .6))
# moonlight from the left, violet rim from behind right
for c, e, p in (((.55, .65, 1), 4.5, (-26, -12, 11)), ((.7, .3, 1), 2.2, (22, 24, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .01, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.8)); co.location = t + Vector((8, -46, 27))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
