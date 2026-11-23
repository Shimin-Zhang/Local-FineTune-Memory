import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1168)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
pal = {}
def tint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .3
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    pal[name] = m
for k, c in dict(snow=(.45, .55, .7), drift=(.6, .7, .85), ice=(.25, .5, .7), ice2=(.35, .6, .8), ice3=(.2, .4, .65),
                 fall=(.55, .85, 1), step=(.3, .45, .65), dark=(.05, .08, .15)).items(): tint(k, c)
tint("aurora", (.1, 1, .5), 2.2); tint("aurora2", (.2, .5, 1), 2.2); tint("crown", (.9, 1, .95), 8); tint("throne", (.7, .95, 1), 4)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(pal[k]); return o
def slab(at, s, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, k, at, rot)
def cone(at, r, h, n, k, r2=0.0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at, rot)
def lit(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color, l.energy = c, w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# ice plateau base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=4, radius2=12, depth=3.4)
for v in bm.verts:
    v.co.z -= 1.7
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
mk(bm, "snow")
# snowdrifts in a ring
for i in range(14):
    a = i / 14 * math.tau + random.uniform(-.1, .1); r = random.uniform(8.5, 10.3)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(1.2, 2.0))
    for v in bm.verts: v.co.z *= .35; v.co.x *= 1.3
    mk(bm, "drift", (r * math.cos(a), r * math.sin(a), 0))
# palace: stepped plinth, hall, roof and slender spires
slab((0, 3, 0), (10, 7, .8), "step"); slab((0, 3, .8), (8.4, 5.8, .8), "ice3")
slab((0, 3.5, 1.6), (6.6, 4.6, 3.4), "ice2"); slab((0, 3.5, 5.0), (7.2, 5.2, .3), "ice3")
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.4, radius2=0, depth=2.4)
for v in bm.verts: v.co.z += 1.2
mk(bm, "ice", (0, 3.5, 5.3), (0, 0, math.pi / 4))
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = sx * 4.6, 3.5 + sy * 3.2
        slab((x, y, 1.6), (1.6, 1.6, 4.6), "ice"); cone((x, y, 6.2), 1.2, 3.6, 6, "ice2", .05); cone((x, y, 9.8), .45, 1.2, 6, "crown", .02)
        slab((x, y, 6.2), (.15, .15, .15), "crown")
    slab((sx * 4.2, 1.2, 1.6), (.5, .5, 2.2), "ice3"); cone((sx * 4.2, 1.2, 3.8), .4, 1.8, 5, "ice2", .02)
for i in range(6): slab((sx * (1.2 + i * .0), 1.0 - i * .0, 1.6 + i * .5), (1.6, .1, .1), "ice3")
# frozen waterfalls down the front face
for x in (-3.2, -1.6, 1.6, 3.2):
    for i in range(7):
        slab((x + random.uniform(-.1, .1), .9 - i * .06, 1.6 + i * .45), (.9 - i * .06, .15, .5), "fall")
    slab((x, .75, 1.6), (1.1, .1, .25), "ice")
slab((0, 1.1, 1.6), (1.4, .12, 2.2), "dark"); slab((0, 1.05, 1.6), (.1, .1, 2.2), "fall")
# throne court open to the sky: steps, dais and a glowing throne
for i in range(5): slab((0, -1.5 - i * .8, 0), (5.2 - i * .5, .8, .3 + (4 - i) * .12), "ice2")
slab((0, -1.2, 2.0), (4.2, 2.6, .5), "ice"); slab((0, -1.2, 2.5), (3.4, 2.2, .4), "ice3")
slab((0, -1.7, 2.9), (1.5, .2, 1.8), "throne"); slab((0, -1.7, 4.7), (1.5, .2, .3), "throne"); slab((0, -1.4, 2.9), (1.5, .8, .3), "throne")
for sx in (-1, 1): slab((sx * .9, -1.7, 2.9), (.2, .2, 1.4), "throne")
for i in range(3): cone((0, -1.7, 5.0 + i * .4), .35 - i * .08, .5, 5, "crown", .02)
lit("POINT", (.6, 1, .95), 900, (0, -1.5, 3.8))
# aurora curtains behind the palace
for i in range(7):
    x = -8 + i * 2.6; h = 5 + random.uniform(0, 2.5)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * 2.0, v.co.y * .25, (v.co.z + .5) * h))
        if v.co.z > 0: v.co.x += random.uniform(-.4, .4)
    mk(bm, "aurora" if i % 2 else "aurora2", (x, 9.2, 0), (0, 0, random.uniform(-.2, .2)))
for i in range(3):
    x = -4 + i * 5; bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * 3.4, v.co.y * .2, (v.co.z + .5) * 2.2))
    mk(bm, "aurora2" if i % 2 else "aurora", (x, 9.8, 7.5 + i * .8), (0, 0, .1 * i))
lit("POINT", (.2, 1, .5), 700, (0, 8.5, 6))
# ice trees and shards
for i in range(16):
    a = random.uniform(0, math.tau); r = random.uniform(5.5, 11)
    x, y = r * math.cos(a), r * math.sin(a)
    if y < -4 and abs(x) < 3.5: continue
    cone((x, y, 0), .12, 1.0, 5, "ice3", .08); cone((x, y, 1.0), .7, 1.8, 6, "ice2", .02)
for i in range(8): cone((random.uniform(-10, 10), random.uniform(-8, 8), 0), .3, random.uniform(1.5, 3), 5, "ice3", .02)
lit("SUN", (.5, .65, 1), 4, (-22, -14, 8), (0, 0, 1)); lit("SUN", (.3, .9, .6), 2.5, (18, 22, 10), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((-8, -54, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
