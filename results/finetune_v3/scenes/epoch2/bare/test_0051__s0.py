import bpy, bmesh, math, random
from mathutils import Vector
random.seed(677)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
turf, ashlar, ashlar2, oak, water, tile, stone, fire, dark = (col((.12, .15, .08)), col((.42, .38, .32)), col((.3, .27, .24)), col((.28, .17, .09)), col((.1, .3, .4), .6, .2),
    col((.4, .15, .1)), col((.5, .48, .44)), col((1, .45, .08), 14), col((.03, .03, .035)))
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(w, d, h, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return add(bm, m, at, rot)
def cyl(r, h, n, m, at, rot=(0, 0, 0), r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def roof(w, d, h, m, at, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((0 if v.co.z > 0 else v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return add(bm, m, at, (0, 0, rz))
def light(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# terraced hillside: nine steps, each 3 m deep, falling 1.1 m; the top is the bakery terrace
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 30, v.co.y * 34, v.co.z * 5 - 2.5))
    if v.co.z < 0: v.co.x *= .6; v.co.y *= .6; v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, 0)))
add(bm, turf, (0, 0, -2.5))
for i in range(9):
    blk(30, 3, 2.2 + i * 1.1, ashlar if i % 2 else ashlar2, (0, -14.5 + i * 3, -2.5))
# two rows of eight water wheels stepped down the slope, each in a stone channel
for r in range(2):
    for k in range(8):
        y = -12.5 + k * 3; z = 2.2 + k * 1.1; x = -6 + r * 12
        blk(2.6, 3.0, .5, stone, (x, y, z))
        blk(2.2, 2.6, .25, water, (x, y, z + .5))
        cyl(.2, 3.2, 6, oak, (x, y, z + .75), (0, math.pi / 2, 0))
        for j in range(8):
            a = j * math.pi / 4
            blk(1.6, .18, .6, oak, (x + math.cos(a) * 1.2, y, z + .75 + math.sin(a) * 1.2), (0, -a, 0))
        blk(.12, .12, 1.5, dark, (x - 1.7, y, z + .75))
# the aqueduct along the back: piers, arches, a trough that feeds both rows
for k in range(7):
    blk(.8, .8, 3.4, ashlar, (-12 + k * 4, 13, 2.2))
    a = bmesh.new(); bmesh.ops.create_cone(a, cap_ends=True, segments=8, radius1=.5, radius2=.5, depth=.8)
    add(a, ashlar, (-12 + k * 4 + 2, 13, 5.6), (math.pi / 2, 0, 0))
blk(30, 1.2, .5, ashlar, (0, 13, 6.0)); blk(29, .8, .3, water, (0, 13, 6.5))
for x in (-6, 6): blk(.6, 14, .5, stone, (x, 6, 6.5))
for x in (-6, 6): blk(.5, .5, .4, stone, (x, 6, 5.5))
# bakery terrace at the top: a long hall with a tiled roof, a dome oven and chimney fire
blk(24, 8, 4.5, ashlar, (0, 10, 6.5)); roof(25, 9, 2.2, tile, (0, 10, 11))
for k in range(6): blk(.9, .2, 1.8, dark, (-9 + k * 3.6, 5.9, 7.6))
blk(1.8, 1.8, 2.4, stone, (-7, 5.5, 6.5)); cyl(1.4, 1.2, 8, stone, (-7, 5.5, 8.9), r2=.5)
blk(1.4, 1.4, 4.5, ashlar, (7, 10, 11)); blk(1.0, 1.0, .5, fire, (7, 10, 15.5))
for k in range(4): blk(1.4, .3, .4, stone, (-2 + k * 2.4, 5.5, 6.5))
blk(1.2, 1.2, .3, fire, (2, 5.2, 6.5)); blk(1.2, 1.2, .3, fire, (-1, 5.2, 6.5))
light((-7, 4.5, 7.5), (1, .45, .1), 900); light((2, 4.5, 7.5), (1, .5, .15), 500); light((7, 10, 17), (1, .4, .1), 700)
for i in range(5): cyl(.6, .5, 6, ashlar2, (10 + i * .1, 4.5 + (i % 2) * .8, 6.5), r2=.5)
# olive trees and a cypress on the slopes
for (x, y, k) in ((-13, -8, 0), (-13, 2, 1), (13, -4, 0), (13, 6, 1)):
    z = 2.2 + max(0, min(8, int((y + 14.5) / 3))) * 1.1
    cyl(.2, 1.4, 5, oak, (x, y, z)); cyl(.9, .8, 6, turf, (x, y, z + 1.3), r2=.2)
# golden afternoon: low amber key from the left, cool blue rim from behind right
for c, w, at in (((1, .72, .38), 5.5, (-30, -14, 12)), ((.4, .55, 1), 2.2, (24, 26, 16))):
    s = bpy.data.lights.new("sun", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("sun", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 4)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("gold"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .025, .04, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 85; cm.clip_end = 500
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 6)); co.location = tg + Vector((-24, -78, 52))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
