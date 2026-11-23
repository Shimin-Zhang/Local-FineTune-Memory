import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1852)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def clay(rgb, em=0, r=.95):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = r
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
mud, pit, clay, brick = clay((.32, .2, .13)), clay((.04, .03, .03)), clay((.42, .22, .14)), clay((.55, .25, .15))
brick2, cloth, wood, thatch = clay((.45, .2, .13)), clay((.6, .55, .45)), clay((.28, .18, .1)), clay((.3, .22, .1))
smoke, fire, coal, leaf = clay((.3, .3, .32)), clay((1, .3, .05), 14), clay((.04, .03, .03)), clay((.12, .22, .1))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(w, d, h, m, at, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mk(bm, m, at, rot)
def rnd(r, h, m, at, n=7, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def lump(r, m, at, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x, v.co.y, v.co.z * sq)) * random.uniform(.85, 1.15)
    return mk(bm, m, at)
def lamp(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# field base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=7, radius2=15, depth=3.5)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.75
mk(bm, mud)
# clay pit with a ramp and spoil heaps
blk(9, 6.5, .08, pit, (-8, 6, .02))
for i in range(5): blk(1.6, 6.5, .06, pit, (-8 + i * 1.5, 6, .06 + i * .02))
for i in range(6):
    lump(random.uniform(.9, 1.5), clay, (-8 + random.uniform(-4, 4), random.uniform(1, 10.5), .3), .5)
blk(2.2, 5, .5, clay, (-3.4, 6, .1), (0, 0, 0), .8)
# moulding tables with wet bricks
for tx in (-2, 3):
    for ty in (-1, 1): blk(.3, .3, 1.3, wood, (tx, ty, 0))
    blk(5.6, 2.8, .2, wood, (tx, 0, 1.3))
    for i in range(6): blk(1.2, .9, .35, clay, (tx - 2.2 + i * .9, 0, 1.5))
# drying rows under cloth canopies
for ry, y in enumerate((-7, -9.5)):
    for px in (-6, 0, 6):
        for py in (-.5, .5): blk(.25, .25, 2.4, wood, (px, y + py, 0))
    for i in range(3): blk(1.9, 1.5, .08, cloth, (px - 3 + i * 3, y, 2.4), (.2, 0, 0))
    for i in range(8):
        for j in range(2): blk(1.0, .7, .35, brick if (i + j) % 2 else brick2, (px - 2.7 + i * .75, y - .2 + j * .4, .05 + j * .35))
# the clamp kiln: stacked brick pyramids with a firebox, smoke and a chimney
kx, ky = 8, 4
for k, (r, h) in enumerate(((4.2, 1.8), (3.4, 1.8), (2.6, 1.8), (1.8, 1.8))):
    for i in range(int(r * 3)):
        a = i * 2.4 + k
        blk(1.1, .8, h, brick if k % 2 else brick2, (kx + math.cos(a) * r * .8, ky + math.sin(a) * r * .8, k * 1.8), (0, 0, a + 1.57))
for i in range(4): blk(.9, .6, 1.0, coal, (kx - 1 + i * .7, ky - 3.6 + (i % 2) * .3, 0), (0, 0, i))
blk(2.4, 1.0, .6, fire, (kx, ky - 3.4, .1)); lamp((1, .4, .1), 1600, (kx, ky - 4.2, 1.2))
rnd(.7, 3.5, brick2, (kx + 1.5, ky + 1, 0), 6)
for i in range(5): lump(.5 + i * .12, smoke, (kx + 1.5 + i * .5, ky + 1 + i * .3, 3.6 + i * 1.1), .8)
# lamp on a pole, a wheelbarrow, a stack of finished bricks, a tree
blk(.2, .2, 4, wood, (4, 7, 0)); blk(.8, .8, .9, fire, (4, 7, 4)); lamp((1, .6, .25), 500, (4, 7, 4.5))
blk(1.6, 1.0, .6, wood, (-1, 5, .8), (0, 0, .5)); rnd(.35, .3, coal, (-1, 5, .3), 6)
for i in range(3): blk(2.6, 1.6, .4, brick, (4, 9, i * .4))
rnd(.3, 2.5, wood, (12, -6, 0), 5, .2); lump(1.8, leaf, (12, -6, 3.4), .8)
for i in range(12): lump(random.uniform(.2, .45), random.choice((leaf, brick2)), (random.uniform(-13, 13), random.uniform(-12, 12), .1), .5)
for c, w, p in (((1, .45, .25), 5.5, (-26, -12, 8)), ((.4, .3, .8), 2.2, (22, 24, 14))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 1, 2)); co.location = tg + Vector((14, -66, 40))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
