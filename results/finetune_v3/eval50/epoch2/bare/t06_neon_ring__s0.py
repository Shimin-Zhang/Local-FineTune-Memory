import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1123)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def neon(rgb, em=0, rough=.5, metal=0):
    m = bpy.data.materials.new("n"); m.use_nodes = True
    b = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
floor, floor2, slab, cyan, magenta, core, panel = (neon((.01, .012, .03), rough=.15), neon((.03, .03, .06), rough=.2), neon((.05, .05, .08), rough=.4),
    neon((.1, .9, 1), 12), neon((1, .1, .7), 12), neon((.8, .95, 1), 18), neon((.02, .02, .04), rough=.3, metal=.5))
def piece(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def disc(r, h, at, m, n=8, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return piece(bm, m, at, rot)
def bar(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return piece(bm, m)
def orb(r, at, m, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r); return piece(bm, m, at)
def beam(kind, c, e, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color, L.energy = c, e
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=7, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
piece(bm, floor)
for i in range(8):
    a = i * math.pi / 4
    for r in (2.5, 4.5, 6.5, 8.5, 10.5):
        bar((math.cos(a) * r, math.sin(a) * r, 0), (math.cos(a + math.pi / 4) * r, math.sin(a + math.pi / 4) * r, 0), .06, cyan if i % 2 else magenta)
for r in (2.5, 4.5, 6.5, 8.5, 10.5): disc(r, .02, (0, 0, 0), floor2, 8)
disc(1.6, .25, (0, 0, 0), slab, 8); disc(1.1, .1, (0, 0, .25), core, 8)
beam("POINT", (.8, .95, 1), 300, (0, 0, 1))
# the ring: a tube of glowing segments, tilted, with a bright core line and a second smaller ring behind
R, tilt = 5.2, .35
def ring_pt(t, r=R, z0=6.5):
    x, y = math.cos(t) * r, math.sin(t) * r
    return Vector((x, y, z0 + y * math.tan(tilt)))
for k in range(28):
    a0, a1 = k * 2 * math.pi / 28, (k + 1) * 2 * math.pi / 28
    bar(ring_pt(a0), ring_pt(a1), .38, cyan if k % 7 else magenta)
    bar(ring_pt(a0, R * .93), ring_pt(a1, R * .93), .1, core)
for k in range(14):
    a = k * 2 * math.pi / 14
    bar(ring_pt(a, 4.3, 6.9), ring_pt(a + .2, 4.3, 6.9), .14, magenta if k % 2 else cyan)
beam("POINT", (.1, .9, 1), 2400, (0, 0, 6.5)); beam("POINT", (1, .1, .7), 900, (0, 6, 6.5))
# pylons: three glowing columns around the floor, each with a ring of light at its top
for i, (x, y) in enumerate(((-10, -4), (10, -3), (0, 10.5))):
    disc(.55, 4.5, (x, y, 0), slab, 6, .4); disc(.7, .25, (x, y, 4.5), cyan if i != 1 else magenta, 6)
    for k in range(6): bar((x + math.cos(k) * .5, y + math.sin(k) * .5, 1.0 + k * .5), (x + math.cos(k) * .5, y + math.sin(k) * .5, 1.5 + k * .5), .08, cyan if i != 1 else magenta)
    beam("POINT", (.1, .9, 1) if i != 1 else (1, .1, .7), 220, (x, y, 4.8))
# floating shards and debris drifting around the ring
for i in range(16):
    a, r = random.uniform(0, 6.28), random.uniform(2.5, 9)
    orb(random.uniform(.15, .4), (math.cos(a) * r, math.sin(a) * r, random.uniform(1, 10)), random.choice((cyan, magenta, core)), 1)
beam("SUN", (.3, .6, 1), 3.2, (-24, -18, 12), (0, 0, 4)); beam("SUN", (1, .2, .7), 2.4, (22, 20, 10), (0, 0, 4))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .004, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((9, -54, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
