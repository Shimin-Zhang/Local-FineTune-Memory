import bpy, bmesh, math, random
from mathutils import Vector
random.seed(595)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def shade(rgb, em=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
turf, soil, plank, plank2, roofm, soil2 = shade((.1, .2, .1)), shade((.22, .13, .08)), shade((.38, .24, .14)), shade((.26, .16, .1)), shade((.2, .12, .1)), shade((.14, .09, .06))
mint, cham, lemon, bloom, herb, bee, wing, potm, wick = shade((.2, .5, .22)), shade((.55, .62, .3)), shade((.3, .5, .15)), shade((.9, .9, .75)), shade((.45, .38, .2)), shade((.95, .7, .05)), shade((.7, .8, 1), .5), shade((.5, .2, .12)), shade((1, .65, .2), 12)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def bush(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mk(bm, m, at)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# garden plot: turf slab with rough underside, three raised beds of soil
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 2
mk(bm, turf)
for i, (y, m) in enumerate(((3.6, mint), (0, cham), (-3.6, lemon))):
    slab((-1, y, 0), (12, 3.2, .6), soil); slab((-1, y, .6), (11.2, 2.6, .15), soil2)
    for k in range(7):
        x = -6 + k * 1.7 + random.uniform(-.2, .2)
        bush((x, y + random.uniform(-.8, .8), 1.1), .75, m, .85)
        if i == 1: bush((x + .2, y + .3, 1.7), .16, bloom, 1)
# fence round the plot: posts and two rails, with a gap at the front
for k in range(11):
    x = -7.5 + k * 1.5
    for y in (-6.4, 6.4): rod((x, y, 0), (x, y, 1.5), .14, plank2)
for y in (-6.4, 6.4):
    for z in (.5, 1.1): rod((-7.5, y, z), (7.5, y, z), .1, plank)
for y in (-6.4, 6.4): rod((-7.5, y, .5), (-.75, y, .5), .1, plank); rod((.75, y, .5), (7.5, y, .5), .1, plank)
for y in (-6.4, 6.4): rod((-7.5, y, 1.1), (-.75, y, 1.1), .1, plank); rod((.75, y, 1.1), (7.5, y, 1.1), .1, plank)
# drying shed at the back right: two posts, a sloped eave, hanging racks of herbs
for x in (6.5, 10.5): rod((x, 7.5, 0), (x, 7.5, 4.2), .25, plank2)
rod((6.5, 7.5, 4.2), (10.5, 7.5, 4.2), .2, plank2)
slab((8.5, 7.6, 4.2), (4.8, 3.2, .2), roofm, (.25, 0, 0))
rod((6.5, 5.6, 3.6), (10.5, 5.6, 3.6), .12, plank)
for k in range(6):
    x = 6.9 + k * .65
    rod((x, 5.6, 3.6), (x, 5.6, 2.9), .03, herb); bush((x, 5.6, 2.7), .3, herb if k % 2 else cham, .9)
# barrel table with a big teapot, cups and a candle, in the middle of the plot
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.9, radius2=.9, depth=1.6)
for v in bm.verts: v.co.z += .8
mk(bm, plank, (-1, 0, 0))
for z in (.3, 1.3): rod((-1.9, 0, z), (-1.9, 0, z + .12), .1, plank2)
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.8)
for v in bm.verts: v.co.z *= .85
mk(bm, potm, (-1, 0, 1.95))
slab((-1, 0, 2.5), (.5, .5, .15), potm); slab((-1.5, 0, 2.2), (.6, .15, .15), potm, (0, 0, 0))
rod((-1.4, 0, 2.3), (-2.0, 0, 2.1), .1, potm); rod((-1.5, 0, 2.3), (-1.0, 0, 2.9), .08, potm)
slab((-1, 0, 2.65), (.3, .3, .12), wick); glow((-1, 0, 3.2), (1, .65, .25), 250)
for k in range(3): slab((-1 + (k - 1) * .6, -.8, 1.6), (.3, .3, .2), shade((.7, .65, .55)))
# bees: fat striped bodies, wings, circling the beds and the flowers
for k in range(10):
    x, y, z = random.uniform(-6, 5), random.uniform(-5, 5), random.uniform(2, 4.5)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.28)
    for v in bm.verts: v.co.x *= 1.4
    mk(bm, bee, (x, y, z), (0, 0, random.uniform(0, 3))); bush((x, y, z + .3), .15, wing, .5)
# a watering can, a stool and a stack of drying bundles
rod((5, -2, 0), (5, -2, .8), .12, plank2); slab((5, -2, .8), (.6, .6, .15), plank)
rod((5.5, -2, 1.2), (6.3, -2, 1.6), .1, potm); slab((5.2, -2, 1.0), (.5, .4, .4), potm)
for k in range(3): bush((-6.5 + k * .5, -2.2, .5 + k * .1), .3, herb, .6)
for c, w, p in (((1, .72, .38), 5, (-24, -12, 8)), ((.5, .6, 1), 2.2, (22, 18, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .025, .035, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 1.5)); co.location = tg + Vector((-6, -50, 28))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
