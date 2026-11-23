import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1553)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def stuff(rgb, glow=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
grass, grass2, ditch, bank, thatch, thatch2, clay, clay2, stone, timber, fire, iron = (stuff(c) for c in (
    (.12, .2, .06), (.2, .27, .09), (.06, .08, .05), (.2, .15, .08), (.4, .3, .12), (.3, .22, .09), (.3, .18, .1), (.22, .13, .08), (.25, .25, .24), (.2, .12, .07), (1, .4, .06), (.06, .06, .07)))
fire = stuff((1, .4, .06), 14); ember = stuff((1, .15, .04), 8)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def pole(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return mk(bm, m)
def blob(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.85, 1.15)
    return mk(bm, m, at)
def flame(at, c, w):
    L = bpy.data.lights.new("f", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("f", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=11, radius1=5, radius2=11.5, depth=3.5)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.1, .1)
mk(bm, grass, (0, 0, -1.75))
cone((0, 0, 0), 8.6, .3, 11, grass2)
# ditch ring and raised bank, a ring of grass
cone((0, 0, .3), 6.6, .12, 11, ditch, 6.6)
for i in range(11):
    a = i * 6.283 / 11; blob((math.cos(a) * 6.6, math.sin(a) * 6.6, .4), 1.1, bank, (1.5, 1.2, .55))
    blob((math.cos(a + .3) * 7.4, math.sin(a + .3) * 7.4, .35), .9, grass2, (1.5, 1.1, .45))
# thatched huts in a circle, each with a door facing in
for i in range(8):
    a = i * 6.283 / 8 + .39; x, y = math.cos(a) * 4.6, math.sin(a) * 4.6
    cone((x, y, .3), 1.5, 1.3, 8, clay if i % 2 else clay2, 1.45)
    cone((x, y, 1.5), 1.95, 1.7, 8, thatch if i % 2 else thatch2, .1)
    cone((x, y, 3.1), .15, .5, 5, thatch2, .02)
    box((x - math.cos(a) * 1.4, y - math.sin(a) * 1.4, .3), (.8, .2, 1.1), timber, (0, 0, a))
    box((x - math.cos(a) * 1.55, y - math.sin(a) * 1.55, .3), (.5, .15, .9), fire if i % 3 == 0 else ember)
# central gathering place: fire ring, hearth stones, seating logs
for i in range(7):
    a = i * 6.283 / 7; blob((math.cos(a) * 1.5, math.sin(a) * 1.5, .45), .4, stone, (1, 1, .8))
cone((0, 0, .3), 1.1, .2, 7, iron, 1.0); cone((0, 0, .5), .8, .5, 6, fire, .1)
cone((0, 0, 1.0), .45, .5, 5, ember, .05)
flame((0, 0, 1.2), (1, .45, .1), 1400)
for i in range(5):
    a = i * 1.26 + .5; cone((math.cos(a) * 2.4, math.sin(a) * 2.4, .3), .3, 1.6, 6, timber, .3, (0, math.pi / 2, a + 1.57))
# the smithy: timber walls, thatched roof, forge fire and anvil
sx, sy = 3.3, -3.0
box((sx, sy, .3), (2.6, 2.2, 1.7), clay2); box((sx, sy, 2.0), (3.0, 2.6, .25), thatch)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 3.0, v.co.y * 2.6, (v.co.z + .5) * 1.1))
    if v.co.z > .5: v.co.x *= .1
mk(bm, thatch2, (sx, sy, 2.2))
box((sx, sy - 1.12, .3), (1.0, .1, 1.3), fire); flame((sx, sy - 1.6, 1.0), (1, .4, .08), 600)
box((sx + 1.6, sy - 1.0, .3), (1.2, .9, .5), stone); box((sx + 1.6, sy - 1.0, .8), (.7, .4, .2), iron); box((sx + 1.6, sy - 1.0, 1.0), (.2, .2, .5), iron)
for sx2 in (-1.4, 1.4): pole((sx + sx2, sy - 1.0, .3), (sx + sx2, sy - 1.0, 2.0), .15, timber)
for i in range(5): box((sx + 2.0 + i * .35, sy + .2, .3 + (i % 2) * .2), (.25, .25, .5), iron, (0, .3, 0))
# grass tufts, boulders and a standing stone
for i in range(14):
    a, r = random.uniform(0, 6.28), random.uniform(8.8, 10.8)
    cone((math.cos(a) * r, math.sin(a) * r, .3), .2, .5, 4, grass2, .02)
blob((-7.5, 4.5, .5), .9, stone, (1.2, 1, 1.2)); blob((7.5, 5.0, .4), .6, stone)
box((-3.2, -4.0, .3), (.7, .5, 2.4), stone); box((-3.2, -4.0, 2.7), (.9, .6, .3), stone)
for col, w, p in (((.55, .65, 1), 4.5, (-22, -14, 10)), ((.9, .5, .3), 2, (20, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 0, 1)); co.location = tg + Vector((10, -54, 34))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
