import bpy, bmesh, math, random
from mathutils import Vector
random.seed(676)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def glaze(rgb, em=0):
    m = bpy.data.materials.new("g"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
grass, rock, stone, stone2 = glaze((.22, .2, .07)), glaze((.2, .17, .15)), glaze((.36, .32, .28)), glaze((.26, .23, .21))
red, tile, gold, wood = glaze((.55, .08, .06)), glaze((.2, .12, .1)), glaze((.8, .5, .1), 1.5), glaze((.2, .12, .07))
autumn = [glaze((.7, .25, .05)), glaze((.6, .1, .04)), glaze((.55, .35, .05)), glaze((.4, .12, .06))]
fire, smoke = glaze((1, .4, .05), 25), glaze((.2, .18, .2))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def roof(at, w, d, h, m):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1, radius2=.05, depth=h)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, v.co.z + h / 2))
    return mk(bm, m, at, (0, 0, math.pi / 4))
def fire(at, c, w):
    L = bpy.data.lights.new("f", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("f", L); o.location = at; sc.collection.objects.link(o)
# ridge profile: x from -13 to 13, height falls toward the ends
def ridge(x): return 5.0 - .04 * abs(x) ** 2 - .02 * abs(x)
# base: grass slab with a rough tapered underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 24 + random.uniform(-1, 1), v.co.y * 14 + random.uniform(-1, 1), -3.5 + random.uniform(-.8, .5)))
    else: v.co = Vector((v.co.x * 30, v.co.y * 18, 0))
mk(bm, grass)
# the mountain ridge: a chain of rock masses along the crest
for i in range(14):
    x = -13 + i * 2; h = ridge(x) + random.uniform(-.3, .3)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(2.2, 3), v.co.y * random.uniform(1.8, 2.2), max(v.co.z, -.1) * h * .8))
    mk(bm, rock, (x, 0, 0))
# the wall following the ridge: a parapet of stone blocks with merlons, plus corner towers
for i in range(25):
    x = -12 + i * 1.0
    blk((x, 0, ridge(x) - .4), (1.0, .9, .9), stone if i % 2 else stone2)
    if i % 2 == 0: blk((x, 0, ridge(x) + .5), (.5, .6, .35), stone2)
for x in (-12, 12):
    cyl((x, 0, ridge(x) - .5), 1.1, 2.4, 6, stone); cyl((x, 0, ridge(x) + 1.9), 1.3, .8, 6, tile, .1)
# south gate pavilion: two towers, a wall span and a tiled roof over the gate
for x in (-2.6, 2.6): cyl((x, -3.2, 0), 1.2, 3.0, 6, stone); cyl((x, -3.2, 3.0), 1.4, .8, 6, tile, .1)
blk((0, -3.2, 0), (4.0, .8, 2.4), stone2); blk((0, -3.6, 0), (1.6, .3, 1.9), glaze((.03, .02, .02)))
roof((0, -3.2, 3.0), 4.6, 3.6, 1.8, tile); blk((0, -3.2, 3.0), (4.2, 3.2, .2), wood)
for x in (-2.6, 2.6): blk((x, -3.2, 3.2), (.3, .3, 1.0), gold)
blk((0, -5.2, 0), (2.4, .3, 1.6), wood); roof((0, -5.2, 1.6), 1.8, 1.6, .9, tile)
fire((0, -4.0, 1.2), (1, .6, .25), 450)
# signal fire station on the left peak: a stone platform, a brazier with a tall flame and smoke
cyl((-9, 0, ridge(-9) - .4), 1.6, .6, 6, stone)
cyl((-9, 0, ridge(-9) + .2), .8, .5, 6, wood); cyl((-9, 0, ridge(-9) + .7), .55, 1.2, 5, fire, .05)
for k in range(3): cyl((-9 + k * .3, 0, ridge(-9) + 2.0 + k * 1.1), .5 + k * .2, 1.0, 5, smoke, .3)
fire((-9, 0, ridge(-9) + 1.5), (1, .4, .1), 1500)
# small temple on the right slope: steps, a red hall with a hip roof and a gold finial
for k in range(3): blk((8.5, -1.8, k * .35), (4.6 - k * .6, 3.6 - k * .4, .35), stone)
blk((8.5, -1.8, 1.05), (3.2, 2.4, 1.6), red); blk((8.5, -3.05, 1.05), (1.0, .1, 1.2), glaze((.05, .03, .02)))
for x in (7.0, 10.0): blk((x, -3.1, 1.05), (.25, .25, 1.7), red)
roof((8.5, -1.8, 2.65), 2.6, 2.0, 1.4, tile); cyl((8.5, -1.8, 4.0), .15, .8, 5, gold, .05)
fire((8.5, -3.4, 1.8), (1, .6, .25), 300)
# a stair path from the gate to the ridge and a few lantern posts
for k in range(6): blk((0, -2.0 - k * .35, 0), (1.4, .4, .15 + (5 - k) * .3), stone2)
for x in (-1.0, 1.0): blk((x, -2.6, 0), (.12, .12, 1.4), wood); blk((x, -2.6, 1.4), (.35, .35, .4), glaze((1, .55, .15), 5))
# autumn trees on the slopes
for x, y in [(-6, -4), (-3, 4), (3, 4), (6, -4.5), (11, 3), (-11, 3), (5, 3.8), (-4.5, -3.5)]:
    h = max(ridge(x) - .3, .4)
    cyl((x, y, h), .15, 1.2, 5, wood)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15)
    mk(bm, random.choice(autumn), (x, y, h + 1.9))
# lights: low amber sun from the left, cool violet rim from behind right
for c, w, p in (((1, .55, .25), 5.5, (-30, -14, 9)), ((.45, .35, 1), 2.2, (24, 22, 12))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("autumn"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((6, -64, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
