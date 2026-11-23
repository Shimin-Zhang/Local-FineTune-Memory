import bpy, bmesh, random, math
from mathutils import Vector
random.seed(767)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0, rough=.85):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
soil, pot, pot2, rim = tone((.16, .09, .06)), tone((.6, .22, .12)), tone((.48, .17, .1)), tone((.7, .3, .17))
pad, pad2, spine, bloom = tone((.1, .3, .13)), tone((.16, .38, .16)), tone((.85, .8, .65)), tone((1, .2, .45), 10)
bloom2, stem, leaf, trunk = tone((1, .7, .15), 10), tone((.12, .25, .1)), tone((.15, .4, .15)), tone((.25, .15, .1))
sand, rock, book, lamp = tone((.5, .38, .25)), tone((.25, .22, .2)), tone((.5, .1, .12)), tone((1, .6, .2), 12)
def solid(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return solid(bm, m, at, rot)
def cone(at, r1, r2, h, n, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return solid(bm, m, at, rot)
def ball(at, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= sq
    return solid(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# round table top with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=9.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1, .2)))
    v.co.z -= 1.5
solid(bm, pot2)
# the terracotta pot: tapered body, a band, a rim, soil and a few pebbles
cone((0, 0, 0), 2.0, 2.7, 3.2, 8, pot)
cone((0, 0, 1.0), 2.35, 2.35, .35, 8, pot2)
cone((0, 0, 3.2), 2.7, 2.7, .45, 8, rim)
cone((0, 0, 3.4), 2.45, 2.45, .15, 8, soil)
for i in range(7):
    a = i * .9; ball((2.1 * math.cos(a), 2.1 * math.sin(a), 3.55), random.uniform(.18, .3), rock, .6)
# saguaro: a fat central column, two arms curving up, ribs of bumps, spines
def pad(x, y, z, r, h):
    cone((x, y, z), r, r * .92, h, 7, pad)
    for k in range(4): ball((x, y, z + h * .3 + k * h * .17), r * 1.01, pad2, .25)
    for k in range(5):
        a = k * 1.26 + x; ball((x + math.cos(a) * r * .95, y + math.sin(a) * r * .95, z + h * .6), .12, spine, 1.5)
    ball((x, y, z + h + .15), r * .9, pad2, .5)
pad(0, 0, 3.5, 1.0, 6.0)
cone((1.1, 0, 5.6), .45, .45, 1.8, 6, pad, (0, math.pi / 2, 0))
pad(1.9, 0, 5.6, .45, 2.6)
cone((-1.1, .3, 7.0), .4, .4, 1.7, 6, pad, (0, -math.pi / 2, 0))
pad(-1.8, .3, 7.0, .4, 2.0)
# flowers on the tips and a small side plant
for x, y, z in ((0, 0, 9.8), (1.9, 0, 8.4), (-1.8, .3, 9.2)):
    ball((x, y, z), .38, bloom, .8)
for i in range(6):
    a = i * 1.05; ball((2.2 + .4 * math.cos(a), -2.4 + .4 * math.sin(a), .5 + i * .02), .12, bloom2, 1.5)
cone((2.2, -2.4, 0), .55, .7, .8, 6, pot2); cone((2.2, -2.4, .8), .5, .5, .1, 6, soil)
for i in range(5): cone((2.2, -2.4, .9), .12, .02, 1.3, 4, leaf, (random.uniform(-.4, .4), random.uniform(-.4, .4), 0))
# a second little pot with a succulent, a book, a watering can, a lamp and a rug
cone((-4.0, -2.2, 0), .8, 1.0, 1.2, 7, pot2)
for i in range(6):
    a = i * 1.05; cone((-4.0 + .25 * math.cos(a), -2.2 + .25 * math.sin(a), 1.2), .2, .05, 1.0, 4, leaf, (.6 * math.cos(a), .6 * math.sin(a), 0))
box((-2.0, 3.4, 0), (2.2, 1.6, .25), book, (0, 0, .3)); box((-2.0, 3.4, .25), (2.0, 1.4, .2), tone((.7, .6, .4)), (0, 0, .3))
cone((4.2, 2.2, 0), .6, .5, 1.0, 6, tone((.2, .4, .5), 0, .4)); cone((4.2, 2.2, 1.0), .5, .5, .1, 6, tone((.1, .25, .3), 0, .4))
box((4.8, 2.2, 1.0), (.15, .15, .8), tone((.2, .4, .5), 0, .4), (0, 0, 0)); box((5.2, 2.2, 1.5), (.9, .15, .15), tone((.2, .4, .5), 0, .4))
box((-6.0, 3.6, 0), (.25, .25, 3.6), tone((.15, .1, .08))); box((-6.0, 3.6, 3.6), (1.2, 1.2, .9), lamp)
lamp("POINT", (1, .6, .2), 500, (-6.0, 3.6, 4.0)); lamp("POINT", (1, .25, .5), 400, (0, -1, 9.5))
lamp("SUN", (1, .6, .35), 5, (-24, -14, 11), (0, 0, 3)); lamp("SUN", (.3, .7, .8), 2.2, (22, 20, 9), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((12, -38, 23))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
