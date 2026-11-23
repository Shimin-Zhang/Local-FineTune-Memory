import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1660)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def stain(rgb, em=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
oak, oak2, oak3, plaster, skin, bone, slate, iron, candle, cloth = stain((.3, .17, .08)), stain((.2, .11, .06)), stain((.14, .07, .04)), stain((.35, .3, .25)), stain((.5, .36, .28)), stain((.62, .58, .45)), stain((.1, .11, .15)), stain((.06, .06, .07)), stain((1, .7, .25), 14), stain((.4, .1, .12))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, d, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return mk(bm, m, at, rot)
def tube(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def bone(r, at, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    return mk(bm, m, at)
def beam(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def candle(x, y, z, c):
    blk((x, y, z), (.4, .4, .5), bone); blk((x, y, z + .5), (.2, .2, .3), candle)
    L = bpy.data.lights.new("c", "POINT"); L.color = (1, .65, .25); L.energy = 120
    o = bpy.data.objects.new("c", L); o.location = (x, y, z + 1.2); sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=8.5, depth=2.2)
for v in bm.verts:
    v.co.z -= 1.1
    if v.co.z < -1: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1, .3)))
mk(bm, oak3)
for i in range(8): blk((0, 0, i * .06), (15 - i * .1, 15 - i * .1, .06), oak2 if i % 2 else oak)
# four galleries, each a ring of planks with a railing and a support post at its corner
for k in range(4):
    z = 2.2 + k * 1.9
    for i in range(12):
        a = i * math.pi / 6 + .26
        blk((math.cos(a) * 5.2, math.sin(a) * 5.2, z), (2.0, 1.2, .12), oak if i % 2 else oak2, (0, 0, a + 1.57))
        blk((math.cos(a) * 5.9, math.sin(a) * 5.9, z + .5), (2.0, .1, .5), oak3, (0, 0, a + 1.57))
        blk((math.cos(a) * 5.9, math.sin(a) * 5.9, z + 1.0), (2.0, .1, .1), oak3, (0, 0, a + 1.57))
        if i % 3 == 0: beam((math.cos(a) * 5.9, math.sin(a) * 5.9, z), (math.cos(a) * 5.9, math.sin(a) * 5.9, z + 1.0), .12, oak3)
    blk((0, 0, z), (3.6, 3.6, .1), oak3)
for i in range(4):
    a = i * math.pi / 2 + .26
    beam((math.cos(a) * 6.2, math.sin(a) * 6.2, 0), (math.cos(a) * 6.2, math.sin(a) * 6.2, 9.8), .35, oak3)
    for k in range(3):
        for s in (-1, 1):
            a2 = a + s * .26
            beam((math.cos(a) * 6.2, math.sin(a) * 6.2, 2.2 + k * 1.9), (math.cos(a2) * 5.9, math.sin(a2) * 5.9, 2.2 + k * 1.9 + .6), .1, oak3)
# the central table and the dissected body on it
blk((0, 0, 1.1), (3.0, 1.7, .2), oak2)
for sx in (-1, 1):
    for sy in (-.6, .6): blk((sx * 1.3, sy, 0), (.25, .25, 1.1), oak3)
blk((0, 0, 1.3), (2.6, 1.3, .1), cloth)
bone(.38, (0, 0, 1.75), skin); bone(.3, (-.7, 0, 1.7), skin); bone(.28, (.7, 0, 1.7), skin)
for s in (-1, 1): beam((.5, s * .45, 1.7), (1.2, s * .8, 1.75), .12, skin); beam((-.5, s * .45, 1.7), (-1.2, s * .8, 1.75), .12, skin)
blk((0, 0, 1.35), (.5, .25, .05), bone)
# the skeleton on its stand
for sx in (-.5, .5): beam((sx, 2.0, 0), (sx, 2.0, 1.2), .1, iron)
blk((0, 2.0, 1.2), (1.2, .8, .1), oak2)
bone(.28, (0, 2.0, 3.1), bone)
for i in range(6): bone(.17, (0, 1.9, 2.8 - i * .18), bone)
for s in (-1, 1):
    beam((0, 1.9, 2.6), (s * .8, 1.9, 1.9), .07, bone); beam((0, 1.9, 2.6), (s * .8, 1.9, 3.1), .07, bone)
    beam((0, 1.9, 2.0), (s * .2, 1.9, 1.2), .07, bone); beam((s * .2, 1.9, 1.2), (s * .2, 1.9, .5), .07, bone)
blk((0, 1.9, 2.7), (.5, .3, .06), bone)
# skylight above the table: ribs, a glass disc and a shaft of light
for i in range(8):
    a = i * math.pi / 4
    beam((math.cos(a) * 1.8, math.sin(a) * 1.8, 10.0), (math.cos(a) * .1, math.sin(a) * .1, 10.8), .12, iron)
tube((0, 0, 10.0), 1.8, .08, 8, candle, 1.8)
L = bpy.data.lights.new("sky", "SPOT"); L.color = (.8, .9, 1); L.energy = 4500; L.spot_size = .5; L.spot_blend = .6
o = bpy.data.objects.new("sky", L); o.location = (0, 0, 10.2); sc.collection.objects.link(o)
o.rotation_euler = (Vector((0, 0, 1.3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
# students on the galleries, candles on the rails
for i in range(10):
    a = i * 2 * math.pi / 10 + .1; k = i % 4
    tube((math.cos(a) * 4.7, math.sin(a) * 4.7, 2.2 + k * 1.9), .22, .6, 5, stain((.1, .15, .25 + .1 * (i % 3))), .17)
    bone(.17, (math.cos(a) * 4.7, math.sin(a) * 4.7, 3.1 + k * 1.9), skin)
for i in range(12):
    if i % 3: continue
    a = i * math.pi / 6 + .26; candle(math.cos(a) * 5.9, math.sin(a) * 5.9, 2.2 + (i // 3) * 1.9 + 1.1)
for col, w, p in (((.7, .8, 1), 3.5, (-14, -10, 6)), ((.9, .5, .3), 2, (12, 14, 7))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((6, -42, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
