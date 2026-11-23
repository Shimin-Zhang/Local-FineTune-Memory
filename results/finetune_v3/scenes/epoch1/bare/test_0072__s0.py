import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1486)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
paints = {}
def pigment(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    paints[name] = m
for k, c in (("rock", (.17, .14, .13)), ("rock2", (.12, .1, .1)), ("scree", (.2, .16, .12)), ("trail", (.32, .25, .17)), ("wash", (.2, .15, .1)),
             ("bush", (.2, .22, .1)), ("bush2", (.28, .26, .12)), ("fence", (.28, .2, .13)), ("pit", (.02, .02, .02)), ("lamp", (1, .65, .25))): pigment(k, c)
pigment("ochre", (.7, .3, .08)); pigment("white", (.8, .75, .65)); pigment("black", (.02, .02, .02)); pigment("lampglow", (1, .65, .25), 16)
def make(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(paints[m]); return o
def slab(c, w, d, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return make(bm, m, c, rot)
def pole(c, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, c)
def pebble(c, r, m, squash=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= squash
    return make(bm, m, c)
def stick(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return make(bm, m)
def glow(c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = (1, .65, .25), w
    o = bpy.data.objects.new("g", L); o.location = c; sc.collection.objects.link(o)
# mesa ground: a stepped rock face at the back, a scree slope, a dry wash and a trail in front
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 26, v.co.y * 22, v.co.z * 3))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
make(bm, "scree", (0, 0, -1.5))
for i, (y, h) in enumerate(((-10.2, 1.6), (-8.2, 3.2), (-6.2, 4.8), (-4.4, 6.6))):
    slab((0, y, 0), 26, 2.4, h, "rock" if i % 2 else "rock2")
    for k in range(5): slab((random.uniform(-12, 12), y + 1.25, random.uniform(.2, h - .5)), random.uniform(1, 2.5), .1, random.uniform(.3, .9), "rock2")
# the pictographs on the lower ledge face: spirals, a flock of sheep, hunters with bows
for sx, sz, r in ((-8, 3.4, 1.2), (-3.5, 4.6, 1.0), (2, 3.2, 1.3), (7, 4.4, 1.0)):
    for k in range(14):
        a = k * .55; b = a + .55
        stick((sx + r * math.cos(a), -4.3, sz + r * math.sin(a)), (sx + r * math.cos(b), -4.3, sz + r * math.sin(b)), .22, "ochre")
for i in range(6):
    x, z = -9.5 + i * 1.3, 1.5 + (i % 2) * .6
    slab((x, -4.3, z), .9, .1, .5, "white"); slab((x + .55, -4.3, z + .5), .3, .1, .3, "white")
    for dx in (-.3, .3): slab((x + dx, -4.3, z - .3), .1, .1, .3, "black")
for i in range(4):
    x, z = 3.5 + i * 2.2, 1.4 + (i % 2) * .5
    slab((x, -4.3, z), .35, .1, 1.3, "black"); slab((x, -4.3, z + 1.3), .5, .1, .45, "black")
    stick((x + .1, -4.3, z + .9), (x + 1.0, -4.3, z + 1.4), .1, "black"); stick((x + .1, -4.3, z + .9), (x - .6, -4.3, z + .3), .1, "black")
    stick((x + 1.0, -4.3, z + 1.4), (x + 1.0, -4.3, z + .5), .06, "black")
# a trail winding up to a small wooden fence gate, with a lantern post
for i in range(9):
    t = i / 8; x = -9 + 18 * t; y = -8.5 + 2.5 * math.sin(t * 4) + t * 3
    slab((x, y, 0), 2.6, 1.8, .06, "trail", (0, 0, .3 * math.cos(t * 4)))
for i in range(7):
    x = 5 + i * 1.3; pole((x, -2.5, 0), .1, 1.2, 5, "fence")
    if i < 6: stick((x, -2.5, .8), (x + 1.3, -2.5, .8), .08, "fence"); stick((x, -2.5, .35), (x + 1.3, -2.5, .35), .08, "fence")
pole((-2.5, -2.0, 0), .12, 2.2, 5, "fence"); slab((-2.5, -2.0, 2.2), .6, .6, .6, "lampglow"); glow((-2.5, -2.6, 2.5), 450)
# dry wash: a shallow dark channel with pebbles and a couple of small boulders
slab((0, -8.5, 0), 24, 3.4, .08, "wash"); slab((0, -8.5, .08), 24, 1.2, .06, "pit")
for i in range(14): pebble((random.uniform(-11, 11), random.uniform(-9.5, -7.5), .2), random.uniform(.3, .6), "rock2", .7)
# desert scrub and a few rocks
for i in range(22):
    x, y = random.uniform(-12, 12), random.uniform(-11, -5)
    if abs(y + 8.5) < 2.2 or abs(y + 2.2) < 1.4: continue
    pebble((x, y, .3), random.uniform(.4, .8), "bush" if i % 2 else "bush2", .8)
for i in range(5): pebble((random.uniform(-12, 12), random.uniform(-5, -3), .5), random.uniform(.6, 1.1), "rock", .8)
# dusk: low orange key from the left, violet rim behind
for c, w, p in (((1, .55, .25), 6, (-28, -16, 9)), ((.5, .3, .8), 2.2, (24, 24, 14))):
    s = bpy.data.lights.new("sun", "SUN"); s.color, s.energy = c, w
    o = bpy.data.objects.new("sun", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dusk"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .035, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, -2, 3)); co.location = t + Vector((8, -60, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
