import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1032)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def dye(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .35
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    mats[name] = m
for k, v in dict(mahogany=(.2, .1, .05), dark=(.02, .02, .025), light=(.5, .4, .28), gold=(.9, .65, .15),
                 felt=(.04, .12, .07), brass=(.4, .3, .12), velvet=(.25, .03, .06)).items(): dye(k, v)
dye("candle", (1, .6, .2), 25); dye("lamp", (1, .75, .4), 18)
def mk(bm, key, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(key); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(key, me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(mats[key]); return o
def slab(key, at, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, key, at, rot)
def cyl(key, at, r, h, n=8, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, key, at, rot)
def gem(key, at, r, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, key, at)
def rod(key, a, b, r):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return mk(bm, key, a, d.to_track_quat('Z', 'Y').to_euler())
# board slab floating in the dark
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 17, v.co.y * 15, v.co.z * 1.4 - .7))
    if v.co.z < 0: v.co = Vector((v.co.x * .8 + random.uniform(-.6, .6), v.co.y * .8 + random.uniform(-.6, .6), v.co.z - random.uniform(0, 1.6)))
mk(bm, "mahogany", (0, 0, 0))
for i in range(8):
    for j in range(8): slab("dark" if (i + j) % 2 else "light", (-7 + i * 2, -7 + j * 2, 0), (2, 2, .25))
# the king, enlarged, on a light square
kx, ky = -1, -3
cyl("light", (kx, ky, .25), 1.5, .3, 8, 1.3); cyl("gold", (kx, ky, .55), 1.0, .35, 8, .8)
cyl("light", (kx, ky, .9), .55, 1.4, 8, .38); cyl("light", (kx, ky, 2.3), .75, .25, 8, .6)
cyl("light", (kx, ky, 2.55), .3, 1.2, 6, .22); cyl("light", (kx, ky, 3.75), .5, .22, 6, .4)
cyl("gold", (kx, ky, 3.97), .5, .1, 6, .45)
cyl("gold", (kx, ky, 4.07), .2, 1.0, 4, .15); slab("gold", (kx, ky, 4.35), (.9, .14, .14))
gem("gold", (kx, ky, 5.2), .22, 1.3)
for i in range(8):
    a = i * math.pi / 4
    rod("light", (kx + 1.0 * math.cos(a), ky + 1.0 * math.sin(a), .55), (kx + .9 * math.cos(a), ky + .9 * math.sin(a), .9), .1)
# a few neighbouring pieces, small and out of focus
for x, y, h, key in ((3, 1, 1.0, "dark"), (-5, 2, .9, "dark"), (1, 4, 1.1, "light"), (5, -2, .8, "light"), (-6, -5, .9, "dark")):
    cyl(key, (x, y, .25), .6, .15, 6, .5); cyl(key, (x, y, .4), .35, h, 6, .22)
    gem("gold" if key == "dark" else "light", (x, y, .4 + h + .1), .15, 1.3)
# candle and lamp on the board's edge, glowing
cyl("brass", (6.5, 5.5, .25), .35, .3, 6); cyl("light", (6.5, 5.5, .55), .2, 1.0, 6, .15); cyl("candle", (6.5, 5.5, 1.55), .12, .3, 5, .02)
cyl("brass", (-6.5, 5.5, .25), .4, .2, 6); rod("brass", (-6.5, 5.5, .45), (-6.5, 5.5, 2.2), .06); cyl("lamp", (-6.5, 5.5, 2.0), .35, .6, 6, .5)
# a velvet cloth corner and a few scattered pawns' shadows
slab("velvet", (5, -6.5, 0), (4, 1.6, .08), (0, 0, .2))
def beam(kind, c, e, at, aim=None):
    d = bpy.data.lights.new(kind, kind); d.color, d.energy = c, e
    o = bpy.data.objects.new(kind, d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
beam("SUN", (1, .72, .4), 5.5, (-14, -9, 9), (0, 0, 1)); beam("SUN", (.4, .5, 1), 2.2, (12, 12, 8), (0, 0, 1))
beam("POINT", (1, .6, .2), 500, (6.5, 5.5, 1.9)); beam("POINT", (1, .75, .4), 400, (-6.5, 5.5, 2.3))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .012, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.4)); co.location = t + Vector((6, -38, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.dof.use_dof = True; cam.dof.focus_distance = (t - co.location).length; cam.dof.aperture_fstop = 1.6
sc.camera = co
