import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1553)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def stuff(rgb, em=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
turf, turf2, pit, timber, thatch, thatch2 = stuff((.1, .17, .08)), stuff((.14, .2, .1)), stuff((.05, .04, .035)), stuff((.3, .19, .1)), stuff((.35, .26, .12)), stuff((.25, .18, .09))
stone, stone2, pig, leaf, leaf2, cloth = stuff((.4, .38, .36)), stuff((.28, .26, .26)), stuff((.7, .5, .5)), stuff((.12, .3, .08)), stuff((.2, .36, .1)), stuff((.6, .55, .45))
fire, flame, pot = stuff((1, .4, .05), 25), stuff((1, .75, .2), 30), stuff((.12, .12, .14))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, d, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * k, v.co.y * d[1] * k, (v.co.z + .5) * d[2]))
    return mk(bm, m, at, (0, 0, rz))
def rod(at, r, h, m, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def lump(at, r, m, sq=(1, 1, 1), j=.15):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) + Vector((random.uniform(-j, j), random.uniform(-j, j), random.uniform(-j, j))) * r
    return mk(bm, m, at)
def lit(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# base: village clearing on a grassy mound, with the shallow pit dug into it
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
mk(bm, turf)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(3, 12)
    blk((math.cos(a) * r, math.sin(a) * r, 0), (random.uniform(1.5, 3), random.uniform(1.5, 3), .12), turf2, a)
blk((0, 0, .02), (7, 5.2, .1), pit)
# the hut: four posts, a thatched roof of two slopes, a fire inside and a doorway gap
for sx in (-1, 1):
    for sy in (-1, 1): rod((sx * 2.4, sy * 1.6, .1), .16, 2.8, timber, 5)
for z in (1.0, 2.2): blk((0, 1.6, z), (5, .12, .12), timber); blk((-2.4, 0, z), (.12, 3.2, .12), timber)
for s in (-1, 1):
    blk((0, s * 1.0, 2.9), (5.6, 2.2, .25), thatch, 0, .95).rotation_euler.x = -s * .45
    blk((0, s * 1.0, 3.0), (5.8, .2, .2), thatch2, 0, .95).rotation_euler.x = -s * .45
rod((0, 0, 2.9), .12, 2.2, timber, 5)
for i in range(3): lump((random.uniform(-.4, .4), random.uniform(-.4, .4), .35), .3, stone, (1, 1, .7), .2)
blk((0, 0, .2), (.8, .8, .35), fire)
lit((1, .5, .1), 450, (0, 0, 1.2))
# the warp-weighted loom: two beams, warp threads, and a row of hanging stones
for sx in (-1, 1): rod((sx * 1.7, -5.2, .1), .1, 2.6, timber, 5)
blk((0, -5.2, 2.5), (3.8, .2, .2), timber); blk((0, -5.2, 1.2), (3.8, .2, .2), timber)
for i in range(15):
    x = -1.5 + i * .22
    rod((x, -5.2, 1.3), .02, 1.2, cloth, 4)
    blk((x, -5.2, 1.0), (.18, .2, .22), stone if i % 2 else stone2, 0, .9)
# pig pen: four-sided stake fence, a trough, and two pigs
for i in range(9):
    rod((-7.5 + i * .8, -6.5, 0), .06, 1.1, timber, 5); rod((-7.5 + i * .8, -3.5, 0), .06, 1.1, timber, 5)
    rod((-7.5, -6.5 + i * .4, 0), .06, 1.1, timber, 5); rod((-3.5, -6.5 + i * .4, 0), .06, 1.1, timber, 5)
blk((-5.5, -6.2, .1), (3.6, .12, .6), timber); blk((-5.5, -3.8, .1), (3.6, .12, .6), timber)
blk((-6.5, -5, .1), (1.4, .5, .4), timber, 0, .8); lump((-5, -4.8, .75), .65, pig, (1.6, .9, .8), .05); lump((-6.8, -5.8, .7), .6, pig, (1.5, .85, .8), .05)
# vegetable plot: ridged beds with rows of greens, a watering pot
for i in range(5):
    blk((6.5, -3.5 + i * 1.3, .1), (6.5, .8, .3), stuff((.2, .12, .07)), 0, .9)
    for k in range(6): lump((4.2 + k * 1.0, -3.5 + i * 1.3, .5), .28, leaf if i % 2 else leaf2, (1, 1, .8), .08)
rod((9.2, -1, 0), .35, .8, pot, 7, .5)
# a few village trees and a stack of timber at the edge
for x, y, h in ((-10, 3, 5), (10, 5, 4.5), (-11, -3, 4), (11, -1, 5.5), (8, 9, 4)):
    rod((x, y, 0), .3, h * .6, timber, 5); lump((x, y, h * .8), h * .28, leaf, (1, 1, 1.2), .25)
for i in range(5): rod((-2.5 + i * .5, 6.5, .15), .22, 3.5, timber, 5).rotation_euler.x = math.pi / 2
# cold dawn: low blue key from the left, warm rim behind right
for c, w, at in (((.55, .65, 1), 5, (-30, -18, 9)), ((1, .6, .35), 2.2, (22, 26, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dawn"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
