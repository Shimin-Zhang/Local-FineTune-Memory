import bpy, bmesh, random, math
from mathutils import Vector
random.seed(377)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
sea, swell, foam, hull, deck, stripe, shark, sharkB, steel, rope, orange, lamp, eye = (
    paint((.01, .1, .16), rough=.15), paint((.03, .2, .26), rough=.15), paint((.6, .75, .8)), paint((.12, .2, .25)), paint((.35, .3, .22)), paint((.7, .12, .08)),
    paint((.45, .5, .55)), paint((.75, .8, .8)), paint((.3, .32, .35), rough=.4), paint((.4, .3, .15)), paint((.8, .35, .05)), paint((1, .7, .25), 9), paint((.9, .1, .05), 3))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(x, y, z, w, d, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mk(bm, m, (x, y, z), rot)
def cyl(x, y, z, r1, r2, h, n, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z), rot)
def line(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def ball(x, y, z, r, m, sq=1.0, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, m, (x, y, z))
def tooth(x, y, z, s, rot):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=s, radius2=0, depth=s * 2.4)
    for v in bm.verts: v.co.z += s * 1.2
    return mk(bm, sharkB, (x, y, z), rot)
def lamp(x, y, z, w, c=(1, .7, .3)):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = (x, y, z); sc.collection.objects.link(o)
# sea slab with a rough underside and a swell across the stern
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=15, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
mk(bm, sea)
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
for v in bm.verts: v.co = Vector((v.co.x * 7, v.co.y * 3.5, v.co.z * 1.0))
mk(bm, swell, (0, -7.2, .12))
# the Orca: hull, raised stern, deck, cabin, mast, boom, rigging, winch, barrels, net, rope, lanterns
box(0, 1.5, .4, 3.6, 9.5, 1.4, hull); box(0, 6.2, 1.8, 3.6, 1.6, 1.2, hull)
for s in (-1, 1):
    box(s * 1.82, 1.5, 1.2, .1, 9.5, .3, stripe)
    for y in (-2.5, 1.5, 5.5): line((s * 1.8, y, 1.6), (s * 1.8, y, 4.6), .12, steel)
box(0, 1.5, 1.8, 3.4, 9.2, .12, deck)
for i in range(5): box(0, -3 + i * 2, 1.92, 3.4, .1, .06, hull)
box(0, 3.8, 1.9, 3.0, 3.0, 1.8, deck); box(0, 2.2, 2.2, 1.2, .1, 1.0, lamp)
box(0, 3.8, 3.7, 3.4, 3.4, .2, hull)
for s in (-1, 1):
    for y in (3.2, 4.4): box(s * 1.52, y, 2.6, .1, .8, .6, lamp)
cyl(0, 1.5, 1.9, .12, .08, 6.5, 6, steel)
line((0, 1.5, 8.2), (0, -3.2, 2.0), .1, steel)
line((0, 1.5, 8.2), (0, 5.5, 3.8), .1, steel)
line((0, 1.5, 7.4), (-1.8, 4.6, 1.9), .06, rope); line((0, 1.5, 7.4), (1.8, 4.6, 1.9), .06, rope)
cyl(-1.2, -.5, 1.9, .35, .3, .6, 6, steel); cyl(-1.2, -.5, 2.5, .5, .5, .1, 6, rope)
cyl(1.2, 5.0, 1.9, .45, .4, .9, 7, rope); cyl(-1.2, 5.0, 1.9, .45, .4, .9, 7, orange)
box(1.0, -.5, 1.9, 1.4, 1.2, .5, rope)
for s in (-1, 1):
    ball(s * 1.5, -3.2, 4.6, .3, lamp, 1, 1); lamp(s * 1.5, -3.2, 4.9, 150)
lamp(0, 2.0, 2.6, 250)
# the great white: tail, body, pectoral fins, dorsal, snout, open jaw with teeth, eye
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 1.5, v.co.y * 5.5, v.co.z * 1.7))
    if v.co.y > 0: v.co.z *= .8
mk(bm, shark, (0, -9.6, 2.6))
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
for v in bm.verts:
    v.co = Vector((v.co.x * .9, v.co.y * 1.6, v.co.z * 1.0))
    if v.co.y < 0: v.co.x *= .3
mk(bm, shark, (0, -5.2, 3.2))
box(0, -5.2, 3.9, .25, 1.8, .1, sharkB)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=.1, radius2=.9, depth=1.8)
for v in bm.verts: v.co.z += .9
mk(bm, shark, (0, -5.4, 4.0), (0, 0, .78))
for s in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=.1, radius2=.6, depth=1.6)
    for v in bm.verts: v.co.z += .8
    mk(bm, shark, (s * .7, -5.0, 2.4)).rotation_euler = (0, s * .9, 0)
for s in (-1, 1):
    box(s * .45, -3.6, 3.35, .9, .5, .22, shark, (0, s * .2, 0)); box(s * .45, -3.6, 2.9, .9, .5, .22, shark, (0, -s * .2, 0))
    for i in range(4):
        tooth(s * (.15 + i * .27), -3.45, 3.3, .09, (math.pi, 0, 0)); tooth(s * (.15 + i * .27), -3.45, 2.95, .09, (0, 0, 0))
ball(.5, -3.7, 3.8, .13, eye, 1, 1)
# spray around the shark and the stern
for i in range(22):
    a = random.uniform(0, 6.28); r = random.uniform(1.5, 3.5)
    ball(math.cos(a) * r, -6.2 + math.sin(a) * r * .6, .5 + random.uniform(0, 1.4), random.uniform(.2, .5), foam, .8, 1)
# stormy dusk: cold teal key low from the left, steel rim from behind
for c, e, p in (((.55, .8, 1), 5, (-26, -12, 10)), ((.6, .65, .9), 2.2, (20, 24, 14))):
    s = bpy.data.lights.new("s", "SUN"); s.color, s.energy = c, e
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .025, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, -1, 3.2)); co.location = t + Vector((6, -58, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
