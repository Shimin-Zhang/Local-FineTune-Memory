import bpy, bmesh, random, math
from mathutils import Vector
random.seed(491)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def spooky(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
turf, dirt, rock, wood, grave, tomb, stem, jack, jack2, eye, tooth, bone, leaf, mushroom = (spooky(*a) for a in (
    (.05, .12, .07), (.1, .07, .06), (.14, .14, .16), (.16, .1, .06), (.2, .2, .22), (.22, .22, .25), (.1, .2, .08), (.9, .35, .03), (.7, .25, .03), (.02, .02, .02), (.8, .8, .7), (.6, .6, .5), (.35, .12, .08), (.1, .8, .3)))
def carve(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return carve(bm, m, at, rot)
def cyl(at, r1, r2, h, n, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return carve(bm, m, at, rot)
def lump(at, r, m, sq=(1, 1, 1), jit=.15, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) + Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit))) * r
    return carve(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: a patch of haunted turf with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=10, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
carve(bm, turf)
# the pumpkin: stacked rings, each with its own radius, and a stem
rings = [1.2, 2.2, 2.9, 3.1, 3.1, 2.9, 2.2, 1.2]
for i, r in enumerate(rings):
    cyl((0, 0, .45 + i * .5), r, rings[i + 1] if i < 7 else .9, .5, 8, jack if i % 2 else jack2)
cyl((0, 0, 4.4), .6, .3, 1.1, 6, stem)
# carved face: dark cut-outs that show the green glow behind
blk((-.95, -2.8, 1.9), (.9, .25, .7), eye); blk((.95, -2.8, 1.9), (.9, .25, .7), eye)
blk((-.5, -2.8, 1.3), (.8, .25, .5), eye, (0, 0, .4)); blk((.5, -2.8, 1.3), (.8, .25, .5), eye, (0, 0, -.4))
blk((0, -2.85, .7), (2.2, .25, .5), eye)
for k in range(4): blk((-1.0 + k * .65, -2.9, .7), (.2, .2, .35), tooth)
lamp("POINT", (.1, 1, .3), 1600, (0, 0, 1.8))
# a green pool of light under the pumpkin
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=3.6, radius2=3.6, depth=.08)
carve(bm, mushroom, (0, 0, .02))
# graveyard: tilted slabs, a cross, a broken obelisk, a fence of posts
for x, y, r, h in ((-5.5, 3, .1, 1.8), (5.5, 4, -.15, 1.5), (-6, -2, .1, 1.4), (6.2, -1.5, .1, 2.0), (3.5, 6.5, 0, 1.6)):
    blk((x, y, 0), (1.3, .3, h), tomb, (0, 0, r)); blk((x, y, h), (1.5, .4, .2), grave, (0, 0, r))
blk((-2.5, 6, 0), (.3, .3, 2.4), wood); blk((-2.5, 6, 1.5), (1.2, .3, .3), wood)
cyl((2.5, 6.5, 0), .5, .3, 1.6, 5, tomb); cyl((2.5, 6.5, 1.6), .3, .05, .9, 5, tomb)
for i in range(9):
    x = -7 + i * 1.7; cyl((x, -6.5, 0), .12, .12, 1.1, 4, wood)
blk((0, -6.5, .8), (14, .1, .1), wood)
# dead tree with bare branches, gnarled roots, and a crow
cyl((-8, 0, 0), .6, .3, 4.5, 5, wood)
for k, (dx, dz, ln) in enumerate(((-1, 3.2, 2.6), (1, 3.8, 2.4), (-.6, 4.2, 1.8), (.8, 2.6, 2.0))):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=.22, radius2=.05, depth=ln)
    carve(bm, wood, (-8 + dx * .3, 0, dz + ln * .3), (0, dx * .9, 0))
lump((-8.6, 3.8, 3.8), .35, bone, (1.3, .8, .8), .05)
# bones, glowing mushrooms, a skull on the ground
for x, y in ((-3, -4), (3, -3.5), (-1.5, 3.5), (4.5, 1)):
    blk((x, y, 0), (1.2, .2, .2), bone, (0, 0, random.uniform(0, 3))); lump((x + .5, y, .15), .25, bone, (1, 1, .8), .05)
for x, y in ((-3.8, -1.2), (3.8, -2), (2.5, 3), (-2.5, 4.5), (-4.5, 1.5)):
    cyl((x, y, 0), .1, .1, .6, 5, bone); cyl((x, y, .6), .4, .05, .35, 6, mushroom)
lamp("POINT", (.1, .8, .3), 200, (-3.8, -1.2, 1.2)); lamp("POINT", (.1, .8, .3), 200, (3.8, -2, 1.2))
lump((1.5, -5, .3), .4, bone, (1, .9, .8), .04); blk((1.5, -5.3, .25), (.12, .12, .12), eye)
# drifting leaves and mist
for i in range(18):
    a, r = random.uniform(0, 6.28), random.uniform(3, 9)
    blk((math.cos(a) * r, math.sin(a) * r * .9, random.uniform(.1, 5)), (.3, .2, .05), leaf, (random.random(), 0, random.random()))
lamp("SUN", (.55, .4, .9), 3, (-16, -10, 6), (0, 0, 1)); lamp("SUN", (.2, .6, .6), 1.8, (14, 14, 8), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((6, -44, 25))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
