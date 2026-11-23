import bpy, bmesh, math, random
from mathutils import Vector
random.seed(88)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def clay(r, g, b, e=0, ro=.9):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = ro
    if e: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = e
    return m
bank, silt, water, stone, stone2, mud, mud2 = clay(.16, .2, .08), clay(.22, .17, .1), clay(.1, .26, .3, 0, .1), clay(.3, .3, .32), clay(.2, .2, .22), clay(.4, .26, .15), clay(.3, .18, .1)
reed, reed2, birdw, birdb, coat, skin, reedlamp = clay(.3, .32, .1), clay(.2, .26, .08), clay(.85, .85, .8), clay(.15, .15, .17), clay(.1, .3, .3), clay(.5, .35, .25), clay(1, .6, .15, 22)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def egg(at, r, m, sq=1, st=(1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq; v.co.x *= st[0]; v.co.y *= st[1]
    return mk(bm, m, at)
def glow(c, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# base: banks either side of a stream that runs front to back, with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=12, depth=4)
for v in bm.verts:
    v.co.y *= .85
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, .3)))
    v.co.z -= 2
mk(bm, silt)
blk((-5.6, 0, -.2), (10, 15, .2), bank); blk((5.6, 0, -.2), (10, 15, .2), bank)
blk((0, 0, -.3), (3.4, 15, .1), water)
# the stone bridge: two piers, a flat deck on arches, parapets, and a cutaway arch face showing the nest ledge
for py in (-4.5, 4.5):
    blk((0, py, 0), (3.8, 2.2, 4.2), stone)
    blk((0, py, 0), (4.2, 2.5, .5), stone2)
blk((0, 0, 3.6), (3.8, 15, .8), stone)
for py in (-7, 7): blk((0, py, 4.4), (3.8, .6, .8), stone2)
blk((-1.8, 0, 4.4), (.5, 15, .8), stone2); blk((1.8, 0, 4.4), (.5, 15, .8), stone2)
blk((0, 0, 0), (3.2, 15, 3.6), stone2)
blk((0, 0, 3.6), (3.4, 15, .15), stone)
# mud nests on the arch face: stacked lumps with a dark mouth, in rows along the wall
for i in range(11):
    for j in range(3):
        y = -6.6 + i * 1.3 + random.uniform(-.1, .1)
        if random.random() < .12: continue
        z = 1.0 + j * .95
        egg((0.02, y, z), .5, mud if (i + j) % 2 else mud2, .9, (1, .35))
        egg((.3, y, z - .05), .2, silt, .9, (1, .25))
# birds darting over the water: teardrop bodies with wings and beaks, at different heights
for i, (x, y, z, a) in enumerate(((-1.5, -1, 2.2, .4), (1.2, 2, 3.0, 2.5), (-.8, 4.5, 1.8, 1.0), (1.6, -4, 2.6, 3.6), (-1.2, -5, 3.4, 2.0))):
    c, s = math.cos(a), math.sin(a)
    egg((x, y, z), .38, birdw if i % 2 else birdb, .8, (1, 1.8)).rotation_euler.z = a
    egg((x + c * .5, y + s * .5, z + .1), .22, birdw if i % 2 else birdb)
    cone((x + c * .8, y + s * .8, z + .1), .05, .3, 4, reed2, .01, (0, 1.57, a))
    for sd in (-1, 1):
        blk((x - sd * .3 * s, y + sd * .3 * c, z + .1), (.5, .12, .12), birdb, (0, 0, a))
# the fisherman on the left bank: seated, rod out over the water, lantern, hat
cone((-3.2, 1, 0), .55, 1.3, 6, coat, .35)
egg((-3.2, 1, 1.6), .38, skin)
cone((-3.2, 1, 1.75), .55, .25, 7, reed2, .3)
blk((-3.2, 1.5, 0), (1.2, 1.2, .4), silt)
rod = Vector((-3.0, 1, 1.2)); tip = rod + Vector((3.2, 0, 2.2))
b = bmesh.new(); bmesh.ops.create_cone(b, cap_ends=True, segments=4, radius1=.05, radius2=.03, depth=3.8)
mk(b, reed2, (rod + tip) / 2, (0, math.atan2(2.2, 3.2), 0)).rotation_euler = (0, math.atan2(2.2, 3.2), 0)
blk((tip.x, tip.y, tip.z - .1), (.1, .1, .1), reedlamp)
glow((1, .6, .15), 450, (tip.x, tip.y, tip.z + .3))
# reeds along the banks and the stream edge
for i in range(26):
    x = random.choice((-1, 1)) * random.uniform(1.9, 9)
    y = random.uniform(-7, 7)
    if abs(x) < 4.5 and abs(y) < 2: continue
    cone((x, y, 0), .06, random.uniform(1.2, 2.2), 4, reed if i % 2 else reed2, .02, (random.uniform(-.15, .15), random.uniform(-.15, .15), 0))
for i in range(7):
    cone((random.choice((-1.7, 1.7)) + random.uniform(-.2, .2), -7 + i * 2.2, -.1), .06, random.uniform(1, 1.8), 4, reed2, .02)
# lights: low rose-gold dawn from the left, cool green-teal rim from behind right
for c, e, p in (((1, .6, .45), 5, (-26, -10, 9)), ((.3, .8, .7), 2.2, (22, 24, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .025, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((20, -46, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
