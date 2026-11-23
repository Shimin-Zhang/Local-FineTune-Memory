import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1144)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def board(r, g, b, glow=0, rough=.5):
    m = bpy.data.materials.new("b"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = p.inputs["Emission Color"].default_value = (r, g, b, 1)
    p.inputs["Roughness"].default_value = rough; p.inputs["Emission Strength"].default_value = glow
    return m
oak, oak2, ivory, ebony, brass, lamp, glow, boardglow = (board(*c) for c in (
    (.28, .16, .08), (.2, .11, .06), (.7, .62, .5), (.05, .045, .05), (.6, .42, .12, 0, .3), (.5, .9, 1, 14), (.2, .8, 1, 12), (.05, .3, .35, 1.2)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def disc(at, r1, r2, h, n, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def rod(a, b, r, n, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    return mk(bm, m, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def orb(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return mk(bm, m, at)
def light(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("o", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floating board corner: 6x6 of squares, thick underside, rough below
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 12, v.co.y * 12, v.co.z * 2 - 1))
    if v.co.z < -1: v.co = Vector((v.co.x * .8 + random.uniform(-.5, .5), v.co.y * .8 + random.uniform(-.5, .5), v.co.z - random.uniform(0, 1.5)))
mk(bm, oak2)
for i in range(6):
    for j in range(6): box((-5 + i * 2, -5 + j * 2, 0), (1.98, 1.98, .12), oak if (i + j) % 2 else boardglow)
# the king, huge, centred on the light square
kx, ky = 0, 0
disc((kx, ky, 0), 1.9, 1.5, .35, 8, ebony); disc((kx, ky, .35), 1.5, 1.0, .45, 8, ebony)
disc((kx, ky, .8), 1.0, .6, 1.4, 8, ebony); disc((kx, ky, 2.2), .6, .62, .15, 8, ebony)
disc((kx, ky, 2.35), .62, .45, .5, 8, ebony); disc((kx, ky, 2.85), .45, .3, .3, 8, ebony)
orb((kx, ky, 3.45), .32, ebony, (1, 1, 1.3))
for s in (-1, 1):
    rod((kx, ky, 3.4), (kx, ky + s * .9, 3.55), .1, 5, ebony); rod((kx, ky, 3.4), (kx + s * .9, ky, 3.55), .1, 5, ebony)
# ivory king, the rival, half behind
disc((-3.6, 2.8, 0), 1.7, 1.3, .3, 8, ivory); disc((-3.6, 2.8, .3), 1.3, .9, .4, 8, ivory)
disc((-3.6, 2.8, .7), .9, .55, 1.2, 8, ivory); disc((-3.6, 2.8, 1.9), .55, .5, .3, 8, ivory)
orb((-3.6, 2.8, 2.4), .3, ivory, (1, 1, 1.3))
# other pieces, blurred by distance: rooks, knights, pawns
for x, y, h, m in ((3.4, -2.6, 1.8, ebony), (5, 2, 1.7, ivory), (-4.8, -3, 1.5, ivory), (1.6, 4.6, 1.4, ebony), (-1.6, -4.2, 1.3, ebony)):
    disc((x, y, 0), .9, .7, .25, 8, m); disc((x, y, .25), .7, .55, h, 8, m); disc((x, y, .25 + h), .55, .65, .25, 8, m)
for x, y in ((-2.4, -1.4), (4.6, -4.2), (-.6, 3.8), (2.6, 1.4)):
    disc((x, y, 0), .6, .45, .2, 6, ivory); disc((x, y, .2), .45, .25, .8, 6, ivory); orb((x, y, 1.2), .25, ivory)
# glowing inlay line around the king's square and a brass lamp on a stand
for dx, dy, w, d in ((0, -1.0, 2.0, .1), (0, 1.0, 2.0, .1), (-1.0, 0, .1, 2.0), (1.0, 0, .1, 2.0)): box((kx + dx, ky + dy, .12), (w, d, .06), glow)
disc((-5.5, 4.8, 0), .35, .2, 1.6, 6, brass); rod((-5.5, 4.8, 1.6), (-5.5, 4.8, 2.6), .06, 5, brass)
orb((-5.5, 4.8, 2.8), .45, lamp, (1, 1, 1.1)); light("POINT", (.5, .9, 1), 450, (-5.5, 4.8, 2.8))
# light: warm key from the right, cool rim from behind left, deep brown backdrop
light("SUN", (1, .75, .5), 5, (18, -10, 9), (0, 0, 1.5)); light("SUN", (.4, .55, 1), 2, (-14, 16, 8), (0, 0, 1.5))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .015, .015, 1)
# camera with a shallow depth of field: focus on the king's head, wide aperture
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
cam.dof.use_dof = True; cam.dof.focus_distance = 22; cam.dof.aperture_fstop = 1.4
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.4)); co.location = t + Vector((-9, -30, 20))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
