import bpy, bmesh, math, random
from mathutils import Vector
random.seed(682)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def rock(r, g, b, e=0):
    m = bpy.data.materials.new("r"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .9
    if e: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = e
    return m
tuff, tuff2, earth, grass, water, marble, wood, cloth, tile, flame = (rock(*c) for c in (
    (.4, .33, .25), (.32, .26, .2), (.16, .1, .07), (.1, .2, .08), (.1, .3, .4), (.5, .48, .42), (.25, .15, .08), (.5, .2, .12), (.4, .15, .1), (1, .5, .1, 14)))
def add(m, bm, p=(0, 0, 0), rz=0):
    d = bpy.data.meshes.new("a"); bm.to_mesh(d); bm.free()
    o = bpy.data.objects.new("a", d); o.location = p; o.rotation_euler.z = rz
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(m, p, s, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return add(m, bm, p, rz)
def rnd(m, p, r, h, n=8, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    o = add(m, bm, p, 0); o.rotation_euler = rot; return o
def arch(m, p, w, h, z, y=0, n=9):
    # a tier of arches: piers, ring stones and a lintel course over each opening
    for i in range(n + 1):
        blk(m, (p + i * w, y, z), (w * .38, 1.6, h), 0, .95)
    for i in range(n):
        cx = p + w * (i + .5)
        for k in range(8):
            a = math.pi * (k + .5) / 8
            blk(m, (cx + math.cos(a) * w * .3, y, z + h + math.sin(a) * w * .3), (.45, 1.6, .35), 0).rotation_euler.y = -(a - math.pi / 2)
        blk(m, (cx, y, z + h + w * .3), (w * .6, 1.6, .3))
    blk(m, (p + w * (n + .5) / 2 - w * .19, y, z + h + w * .3), (w * (n + 1) * .0 + w * n + w * .38, 1.7, .5))
def lit(c, w, p):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
# valley floor and the slopes rising at both ends
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co.x *= .7; v.co.y *= .7; v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, 0)))
    v.co = Vector((v.co.x * 34, v.co.y * 18, v.co.z * 3 - 1.5))
add(earth, bm)
for sx in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * 9, v.co.y * 18, (v.co.z + .5) * 3.6))
    add(grass, bm, (sx * 12.5, 0, 0))
# the stream winding across the valley
for i in range(8):
    blk(water, (-12 + i * 3.4, math.sin(i * .9) * 1.8, .02), (3.8, 2.4, .08), math.sin(i * .9) * .15)
# the aqueduct: lower tier of seven arches, upper tier of seven smaller arches, conduit on top
arch(tuff, -12.5, 3.6, 3.6, 0, 0, 7)
arch(tuff2, -12.5, 3.6, 2.0, 5.6, 0, 7)
blk(tuff, (-1.8, 0, 7.6), (25.6, 1.9, .5))
blk(marble, (-1.8, 0, 8.1), (25.6, 1.2, .35))
for i in range(14): blk(marble, (-12.5 + i * 1.8, 0, 8.45), (.12, 1.0, .12))
# stone bridge over the stream, with a little parapet
for i in range(5):
    a = math.pi * i / 4
    blk(marble, (-1.8 + math.cos(a) * 3.0 - 1.5, 0, .05 + math.sin(a) * 1.6 - .8), (1.7, 2.4, .5), 0).rotation_euler.y = math.pi / 2 - a
blk(marble, (-1.8, 0, 1.6), (6.4, 2.4, .3))
for sy in (-1, 1): blk(marble, (-1.8, sy * 1.1, 1.9), (6.4, .3, .5))
# washing place: stone basin, steps, a woman with a basket, a lantern
blk(tuff2, (-8.5, -3.2, 0), (4.0, 2.4, .8)); blk(water, (-8.5, -3.2, .7), (3.4, 1.8, .1))
for i in range(3): blk(tuff, (-8.5, -5.0 + i * .5, 0), (2.4, .5, .3 * (i + 1)))
blk(cloth, (-10.4, -3.0, 0), (.8, .8, 1.2), 0, .7); rnd(tuff2, (-10.4, -3.0, 1.2), .35, .3, 6)
blk(wood, (-6.6, -3.2, .8), (.7, .7, .6), .3); rnd(flame, (-6.2, -4.6, .8), .22, .5, 5, .05); lit((1, .5, .1), 350, (-6.2, -4.6, 1.8))
# distribution tank at the far end: a vaulted hall with columns, a lit window and a tiled roof
tx = 12.5
blk(tuff, (tx, 0, 0), (7, 5.5, 3.2), 0, .95)
for i in range(5): blk(marble, (tx - 3 + i * 1.5, -3.2, 0), (.5, .5, 2.6), 0, .8)
blk(flame, (tx, -2.8, 1.0), (2.0, .1, 1.2)); lit((1, .55, .15), 900, (tx, -4.5, 1.8))
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts: v.co = Vector((v.co.x * 8, v.co.y * 6.4, (v.co.z + .5) * 2.2))
for v in bm.verts:
    if v.co.z > 1: v.co.x = 0
add(tile, bm, (tx, 0, 3.2))
# a few boulders, olive trees and bushes
for i in range(10):
    x, y = random.uniform(-12, 12), random.choice((-1, 1)) * random.uniform(4.5, 7.5)
    b = bmesh.new(); bmesh.ops.create_icosphere(b, subdivisions=1, radius=random.uniform(.5, 1.2))
    for v in b.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= .7
    add(tuff2, b, (x, y, .2))
for x, y in ((-11, 6.2), (8, -6.4), (10, 6.5)):
    rnd(wood, (x, y, 0), .25, 1.6, 5); rnd(grass, (x, y, 1.4), 1.3, 1.2, 6, .2)
# cold dawn: pale blue key low from the left, warm rose rim from the right behind
for c, e, p in (((.6, .75, 1), 4.5, (-30, -14, 9)), ((1, .6, .45), 2.2, (26, 20, 12))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = e
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .03, .05, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4)); co.location = t + Vector((-6, -80, 42))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
