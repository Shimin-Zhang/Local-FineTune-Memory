import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1920)
sc = bpy.context.scene
for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
M = {}
def paint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .8
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, c in dict(sea=(.05, .12, .17), foam=(.6, .6, .6), hull=(.13, .07, .06), deck=(.3, .22, .15), brass=(.6, .45, .12),
                 white=(.62, .6, .57), dark=(.04, .04, .05), red=(.65, .1, .07), coat=(.5, .38, .22), skin=(.7, .5, .4),
                 dress=(.55, .1, .12), hat=(.2, .17, .14), rope=(.45, .35, .2), smoke=(.16, .13, .13)).items(): paint(k, c)
paint("window", (1, .65, .25), 14); paint("sun", (1, .5, .15), 3)
def add(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def box(at, d, k, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return add(bm, k, at, (rx, 0, rz))
def cyl(at, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, k, at)
def beam(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, k)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
def person(x, y, z, k, hatk, spread):
    cyl((x, y, z), .45, 1.5, 6, k, .3)
    for s in (-1, 1):
        if spread: beam((x, y, z + 1.4), (x + s * 1.5, y - .2, z + 1.9), .17, k)
        else: beam((x, y, z + 1.4), (x + s * .25, y - .1, z + .6), .15, k)
    cyl((x, y, z + 1.5), .32, .55, 6, "skin", .28)
    if hatk: cyl((x, y, z + 2.0), .4, .2, 6, hatk)
# sea slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=15, depth=3.2)
for v in bm.verts:
    v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .2)))
add(bm, "sea")
# the ship: tapered bow hull, decks, bulwarks, funnels, bridge, stern
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 28, v.co.y * 5.6, (v.co.z + .