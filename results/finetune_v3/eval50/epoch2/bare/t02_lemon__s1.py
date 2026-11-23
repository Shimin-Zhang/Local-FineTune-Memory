import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(557)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def col(c, e=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .8
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
LEMON, BUMP, NUB, STEM, LEAF, RIND, WOOD, CREAM, GLOW, JUICE, DARK = col((.8, .62, .05)), col((.9, .72, .1)), col((.55, .42, .04)), col((.2, .12, .06)), col((.12, .32, .08)), col((.7, .55, .08)), col((.25, .15, .08)), col((.75, .7, .55)), col((1, .85, .3), 6), col((.9, .7, .1), 1.5), col((.04, .03, .02))
def make(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blob(r, m, p, sub=1, jit=0, stretch=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co = V((v.co.x * stretch[0], v.co.y * stretch[1], v.co.z * stretch[2])) * random.uniform(1 - jit, 1 + jit)
    return make(bm, m, p)
def stem(r1, r2, h, n, m, p, r=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, p, r)
def lit(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# round wooden table-top on a floating slab
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4, radius2=9.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.3, .2)))
    v.co.z -= 1.5
make(bm, WOOD)
# the lemon: a bumpy icosphere stretched along x, with a nub at each end
big = blob(3.0, LEMON, (0, 0, 3.6), 2, .035, (1.25, 1, .95))
for s in (-1, 1): blob(.55, LEMON, (s * 3.75, 0, 3.6), 2, .06, (1, 1, 1))
# dimpled surface: little raised bumps and tiny pores, clustered on the top half
for i in range(150):
    t = random.uniform(0, 6.28); u = random.uniform(-.9, 1.0)
    d = V((math.cos(t) * math.sqrt(1 - u ** 2), math.sin(t) * math.sqrt(1 - u ** 2), u)); d.x *= 1.25
    p = V((0, 0, 3.6)) + d * 3.0
    if i % 3 == 0: blob(random.uniform(.14, .22), BUMP, p - d * .05, 1)
    else: blob(random.uniform(.05, .09), NUB, p - d * .03, 1)
# stem and a leaf at the nub
stem(.2, .12, .8, 5, STEM, (-3.9, 0, 3.9), (0, -.3, 0)); stem(.1, .02, .3, 4, STEM, (-4.1, 0, 4.2))
blob(.55, LEAF, (-4.4, .3, 4.5), 1, .05, (1.6, .5, .12)).rotation_euler.z = .4
# a halved lemon on a plate: rind, pith, segments, juice glow
stem(2.6, 2.6, .3, 10, CREAM, (5.2, -2.2, 0)); stem(2.3, 2.3, .15, 10, RIND, (5.2, -2.2, .3)); stem(2.0, 2.0, .1, 10, CREAM, (5.2, -2.2, .45))
for k in range(8):
    a = k * math.pi / 4; c, s = math.cos(a), math.sin(a)
    blob(.85, JUICE, (5.2 + c * 1.0, -2.2 + s * 1.0, .62), 1, 0, (1, 1, .35)).rotation_euler.z = a + math.pi / 2
for i in range(3): blob(.12, DARK, (5.2 + random.uniform(-.3, .3), -2.2 + random.uniform(-.3, .3), .75), 1)
lit("POINT", (1, .8, .3), 220, (5.2, -2.2, 1.8))
# lemon wedges, a spoon and a bowl of lemonade
for i, (x, y) in enumerate(((-5.2, -2.4), (-3.6, -4.0), (-6.0, -.2))):
    stem(.9, .9, .5, 8, RIND, (x, y, .1), (0, 0, i)); stem(.7, .7, .45, 8, JUICE, (x, y, .25), (0, 0, i))
stem(.15, .15, 2.4, 5, CREAM, (2.0, -4.5, .1), (1.4, 0, .5)); blob(.4, CREAM, (3.1, -4.5, .2), 1, 0, (1, .8, .4))
blob(1.3, CREAM, (-1.2, -4.6, .55), 1, 0, (1, 1, .55)); blob(1.1, GLOW, (-1.2, -4.6, .95), 1, 0, (1, 1, .15)); lit("POINT", (1, .8, .3), 120, (-1.2, -4.6, 1.6))
# a small glowing lamp on a stand, the main light of the scene
stem(.25, .25, 4.2, 6, STEM, (6.2, 4.0, 0)); stem(.5, .5, .25, 6, STEM, (6.2, 4.0, 4.2)); stem(.2, .2, .6, 6, STEM, (6.2, 4.0, 4.4))
blob(.9, GLOW, (6.2, 4.0, 5.2), 2); lit("POINT", (1, .75, .3), 2500, (6.2, 4.0, 5.2))
lit("SUN", (1, .75, .45), 5, (-14, -10, 9), (0, 0, 3)); lit("SUN", (.3, .5, .9), 2.5, (12, 14, 8), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .02, .015, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = V((0, 0, 3)); co.location = t + V((-14, -37, 25))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
