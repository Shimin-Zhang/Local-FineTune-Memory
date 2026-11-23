import bpy, bmesh, math, random
from mathutils import Vector
random.seed(833)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, em=0, rough=.8):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
oak, oak2, frost, inner, stem, petal, petal2, candle, wax, leaf = (tint((.22, .13, .07)), tint((.15, .09, .05)), tint((.55, .62, .68), rough=.5), tint((.2, .26, .32), rough=.6),
    tint((.12, .3, .12)), tint((.9, .35, .5)), tint((.95, .75, .3)), tint((1, .7, .3), 14), tint((.8, .75, .65)), tint((.1, .35, .2)))
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, w, d, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return put(bm, m, at, rot)
def stemline(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    return put(bm, m, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def bud(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return put(bm, m, at)
def shine(kind, at, col, w, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=4.5, radius2=9, depth=2.4)
for v in bm.verts:
    v.co.x *= 1.2; v.co.z -= 1.2
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
put(bm, oak2)
for i in range(8):
    a = i * math.pi / 4 + .39
    slab((math.cos(a) * 9.2, math.sin(a) * 7.6, -.05), 3.0, .35, .12, oak if i % 2 else oak2, (0, 0, a + math.pi / 2))
slab((0, 0, 0), 16, 12, .4, oak)
for z in (.1, .22): slab((0, 0, z), 15.4, 11.4, .03, oak2)
slab((0, 0, .4), 14.4, 10.4, .25, oak2)
slab((0, 0, .65), 13.6, 9.6, .2, oak)
# the vase: a frosted-glass silhouette built from stacked rings, with a darker inner core showing through
def profile(r): return 1.2 + 1.0 * math.sin(math.pi * r * .5) ** 1.3
bm = bmesh.new(); rings = []
N = 9
for i in range(N + 1):
    r = i / N; z = r * 6.2; rad = profile(r)
    rings.append([bm.verts.new((rad * math.cos(k * math.pi / 4) * random.uniform(.98, 1.02), rad * math.sin(k * math.pi / 4) * random.uniform(.98, 1.02), z)) for k in range(8)])
for a, b in zip(rings, rings[1:]):
    for k in range(8): bm.faces.new((a[k], a[(k + 1) % 8], b[(k + 1) % 8], b[k]))
bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
put(bm, frost, (0, 0, .85))
bm = bmesh.new(); rings = []
for i in range(N + 1):
    r = i / N; rad = profile(r) * .86
    rings.append([bm.verts.new((rad * math.cos(k * math.pi / 4), rad * math.sin(k * math.pi / 4), .95 + r * 6.0)) for k in range(8)])
for a, b in zip(rings, rings[1:]):
    for k in range(8): bm.faces.new((a[k], a[(k + 1) % 8], b[(k + 1) % 8], b[k]))
bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
put(bm, inner, (0, 0, 0))
# stems and blooms rising out of the mouth
for i, (m, x, y) in enumerate(((petal, -.3, .2), (petal2, .5, -.2), (petal, .1, .5))):
    a, b = Vector((x, y, 5.5)), Vector((x * 2.2 + (i - 1) * .8, y * 1.5, 8.6 + i * .5))
    stemline(a, b, .09, stem, 5)
    for k in range(5):
        ang = k * 1.26 + i
        bud(b + Vector((math.cos(ang) * .38, math.sin(ang) * .38, .15)), .3, m, .9)
    bud(b + Vector((0, 0, .1)), .26, petal2 if m is petal else petal, 1.0)
    for s in (-1, 1): bud(b + Vector((s * .5, 0, -.9)), .22, leaf, .4)
# candle, books and a folded cloth on the table
slab((-4.6, -1.5, .85), 1.0, 1.0, 1.6, wax); slab((-4.6, -1.5, 2.45), .14, .14, .3, candle)
shine("POINT", (-4.6, -1.5, 3.1), (1, .65, .25), 450)
for i, (m, w) in enumerate(((tint((.5, .1, .12)), 3.0), (tint((.1, .25, .4)), 2.6))):
    slab((4.6, 2.0, .85 + i * .38), w, 2.2, .38, m, (0, 0, .15 * (i - .5)))
slab((4.4, -2.6, .85), 2.6, 2.0, .22, tint((.6, .55, .5)), (0, 0, .4)); slab((4.4, -2.6, 1.07), 1.6, 1.4, .12, tint((.7, .65, .6)), (0, 0, .2))
shine("SUN", (-22, -14, 10), (.7, .8, 1), 4, (0, 0, 2))
shine("SUN", (18, 20, 9), (1, .5, .6), 2, (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((12, -46, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
