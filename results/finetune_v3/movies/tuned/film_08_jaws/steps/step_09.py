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
