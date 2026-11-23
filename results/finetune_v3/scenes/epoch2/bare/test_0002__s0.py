import bpy, bmesh, math, random
from mathutils import Vector
random.seed(27)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def dye(r, g, b, e=0, rough=.9):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = p.inputs["Emission Color"].default_value = (r, g, b, 1)
    p.inputs["Roughness"].default_value = rough; p.inputs["Emission Strength"].default_value = e
    return m
sand, dust, plaster, wood, wood2, board, tin, iron, cactus, tumble, lamp = (dye(*c) for c in (
    (.4, .27, .14), (.3, .2, .1), (.38, .3, .22), (.3, .16, .08), (.2, .1, .05), (.25, .18, .1), (.3, .3, .32, 0, .5), (.05, .05, .06), (.1, .25, .1), (.55, .45, .25), (1, .6, .15, 14)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def rnd(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return mk(bm, m)
def lit(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3.4)
for v in bm.verts:
    v.co.x *= 1.2; v.co.z -= 1.7
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .2)))
mk(bm, sand)
for i in range(14): blk((random.uniform(-14, 14), random.uniform(-9, 9), 0), (random.uniform(2, 4), random.uniform(1.5, 3), .08), dust, (0, 0, random.uniform(0, 3)))
# the saloon: back wall, two side walls with window openings, porch roof on posts
blk((0, 5, 0), (11, .5, 4.6), plaster); blk((-5.5, 0, 0), (.5, 10, 4.6), plaster); blk((5.5, 0, 0), (.5, 10, 4.6), plaster)
for x, y, w, d in ((-5.5, -5, .5, 1), (5.5, -5, .5, 1), (0, -5, 4.4, 1)): blk((x, y, 0), (w, d, 4.6), plaster)
blk((-3.2, -5, 0), (4.6, .6, .9), wood2); blk((-3.2, -5, 3.4), (4.6, .6, .9), wood2)
blk((0, 5, 4.6), (12, 11, .3), tin)
for x in (-5.4, 5.4): blk((x, -5.2, 4.9), (.4, .4, .3), iron)
for x in (-5.2, 5.2): strut((x, -4.8, 0), (x, -4.8, 4.9), .3, wood2)
for i in range(5): blk((-4.5 + i * 2.25, -4.8, 4.9), (.3, .3, .2), iron)
blk((0, -5, 4.9), (11, .3, .3), iron)
# porch floor and steps
blk((0, -6.6, 0), (12.4, 3.6, .25), wood)
for i in range(8): blk((0, -8.4 - i * .0, 0), (12.4, .01, .01), wood2)
blk((0, -8.6, 0), (4, .8, .12), wood2)
# swinging doors: one half off, hanging from its hinge
for x in (-1.9, 1.9): blk((x, -5.0, .9), (.2, .2, 2.5), iron)
blk((-1.1, -4.9, .9), (2.0, .15, 2.5), wood); blk((-1.1, -4.9, 1.2), (1.6, .1, 1.2), board)
strut((1.9, -4.9, 3.3), (3.6, -4.9, 1.0), .15, wood)
blk((2.7, -4.9, 1.0), (1.7, .15, 2.3), wood, (0, 0, .12)); blk((2.7, -4.9, 1.4), (1.3, .1, 1.0), board, (0, 0, .12))
# broken piano seen through the front window
blk((-3.2, -4.6, .9), (4.4, .1, .1), wood2)
blk((-3.2, 0.8, 0), (3.4, 1.8, 2.4), wood2); blk((-3.2, -.3, 2.2), (3.4, .2, .3), wood)
blk((-3.2, -.3, 2.5), (3.0, .15, .2), board)
for i in range(14): blk((-4.4 + i * .2, -.45, 2.4), (.1, .1, .12), wood if i % 2 else board)
blk((-3.2, -.4, 2.3), (2.6, .08, .08), iron)
for x in (-4.6, -1.8): blk((x, -.2, 0), (.2, .2, .8), iron)
blk((-3.2, 3.4, 0), (1.2, .8, .8), wood)
lit((-3.2, -1.5, 3.6), (1, .6, .2), 450)
# hanging lantern, swinging sign, hitching rail
strut((0, -4.8, 4.9), (0, -4.8, 4.0), .05, iron); rnd((0, -4.8, 3.5), .3, .6, 6, lamp)
lit((0, -4.8, 3.8), (1, .6, .15), 600)
blk((0, -4.6, 4.3), (2.4, .1, .7), board, (0, 0, .06))
for x in (-1.2, 1.2): strut((x, -8.2, 0), (x, -8.2, 1.0), .12, wood2)
strut((-1.2, -8.2, .9), (1.2, -8.2, .9), .1, wood2)
# tumbleweed on the porch
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.9)
for v in bm.verts: v.co *= random.uniform(.8, 1.2)
mk(bm, tumble, (2.6, -6.8, .9))
for i in range(7):
    a = random.uniform(0, 6.28); strut((2.6, -6.8, .9), (2.6 + 1.3 * math.cos(a), -6.8 + 1.3 * math.sin(a), .9 + random.uniform(-.4, .8)), .04, tumble)
# barrels, cacti, bones, wagon wheel, a dead post
for x, y in ((-4.2, -6.6), (4.3, -6.9)): rnd((x, y, .25), .55, 1.1, 7, wood2, .5)
for x, y, h in ((-11, 3, 2.2), (11, 6, 1.8), (-9, -6, 1.4)):
    rnd((x, y, 0), .35, h, 6, cactus, .3); rnd((x + .5, y, h * .6), .2, .8, 5, cactus, .15)
for x, y in ((6, -9), (-7, -9)):
    for k in range(8): a = k * math.pi / 4; strut((x + 1.1 * math.cos(a), y, .1), (x + 1.1 * math.cos(a + math.pi / 2), y, .1), .12, wood2)
for i in range(5): blk((random.uniform(-10, 10), random.uniform(-10, -9), 0), (.8, .15, .15), board, (0, 0, random.uniform(0, 3)))
# noon heat: hard white-yellow key from high, pale blue rim, long shadows
for c, w, at in (((1, .9, .65), 6, (-16, -10, 30)), ((.5, .65, 1), 2.2, (18, 16, 12))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.045, .035, .025, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
co.location = (6, -62, 36)
co.rotation_euler = (Vector((0, 0, 2)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
