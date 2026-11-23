import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1257)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def tone(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    mats[name] = m
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def slab(x, y, z, w, d, h, m, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mk(bm, m, (x, y, z), rot)
def tube(x, y, z, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z), rot)
def spar(a, b, t, m, t2=None):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * (t2 or t), (v.co.z + .5) * (b - a).length)) + a
    return mk(bm, m)
def lamp(kind, rgb, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = rgb; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()

tone("mud", (.17, .12, .08)); tone("flood", (.25, .15, .08), rough=.15); tone("steel", (.28, .3, .33), rough=.5)
tone("deck", (.14, .15, .17)); tone("timber", (.3, .2, .1)); tone("army", (.12, .2, .09)); tone("tyre", (.03, .03, .035))
tone("sandbag", (.4, .33, .2)); tone("head", (1, .9, .6), 14); tone("red", (.7, .08, .06), 8); tone("lampred", (1, .1, .08), 20)
tone("puddle", (.05, .08, .12), rough=.1)

# base: a muddy embankment with a flood channel cut across it
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co.x *= .8; v.co.y *= .8; v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.5, .3)))
    v.co = Vector((v.co.x * 24, v.co.y * 19, v.co.z * 4 - 2))
mk(bm, "mud")
slab(0, 0, -.5, 24, 7, .5, "flood")
for i in range(12): slab(random.uniform(-10, 10), random.uniform(-3, 3), -.02, random.uniform(1.5, 3), .5, .04, "puddle", rot=(0, 0, random.uniform(0, 3)))
for s in (-1, 1):
    slab(0, s * 11.5, 0, 24, 6, .3, "mud", top=.95)
    for i in range(10): slab(random.uniform(-11, 11), s * random.uniform(8.5, 14), .2, random.uniform(1.2, 2.4), random.uniform(1, 2), random.uniform(.3, .8), "mud", top=.7)

# the prefabricated bridge: timber blocks, steel stringers, truss, deck
for k in range(6):
    x = -8.5 + k * 3.4
    for s in (-1, 1):
        slab(x, s * 2.5, 0, 1.4, 2.0, 1.2, "timber", top=.8)
        slab(x, s * 2.5, 1.2, 1.6, 1.2, .25, "timber")
for s in (-1, 1):
    spar((-9.5, s * 2.5, 1.55), (9.5, s * 2.5, 1.55), .35, "steel", .5)
    for k in range(6):
        x = -8.5 + k * 3.4
        spar((x, s * 2.5, 1.5), (x, s * 2.5, 3.8), .22, "steel")
    for k in range(5):
        x0, x1 = -8.5 + k * 3.4, -5.1 + k * 3.4
        spar((x0, s * 2.5, 3.8), (x1, s * 2.5, 1.5), .14, "steel"); spar((x1, s * 2.5, 3.8), (x0, s * 2.5, 1.5), .14, "steel")
slab(0, 0, 1.45, 19, 4.2, .22, "deck")
for k in range(19): slab(-9 + k, 0, 1.67, .08, 4.2, .04, "timber")
for s in (-1, 1):
    for k in range(10): slab(-8.5 + k * 1.9, s * 2.05, 1.67, .2, .2, .7, "steel")
    spar((-9.5, s * 2.05, 2.3), (9.5, s * 2.05, 2.3), .1, "steel")
# floodwater laps the abutments and the piers
for x in (-9.5, 9.5):
    slab(x, 0, 0, 1.6, 5.4, .6, "flood", top=.9)
    slab(x, 0, .6, 1.2, 4.4, .3, "mud", top=.7)
for x in (-8.5, -1.7, 5.1, 8.5): slab(x, 0, -.1, 1.0, 4.4, .5, "flood", top=.8)

# army-green truck on the near bank, with a canvas cargo cover
tx, ty = -2.5, 9.0
slab(tx, ty, .7, 6.0, 2.6, .5, "army")
slab(tx - 1.5, ty, 1.2, 3.0, 2.4, 1.5, "army", top=.95)
slab(tx - 1.5, ty, 2.7, 3.2, 2.6, .12, "army", top=.9)
slab(tx + 1.7, ty, 1.2, 2.0, 2.4, 1.0, "army", top=.95)
slab(tx + 2.8, ty, 1.2, .2, 2.2, 1.0, "army")
slab(tx + 1.7, ty, 2.2, 1.9, 2.3, .15, "timber", top=.9)
for s in (-1, 1):
    for wx in (-3.3, 0, 2.6):
        tube(tx + wx, ty + s * 1.4, .75, .75, .6, 8, "tyre", rot=(math.pi / 2, 0, 0))
    slab(tx + 2.8, ty + s * .8, 1.0, .25, .5, .5, "head")
slab(tx - 1.5, ty, 2.8, 3.2, 2.6, .12, "army", top=.9)
lamp("POINT", (1, .9, .6), 250, (tx + 3.6, ty, 1.2))
slab(tx + 3.1, ty, .6, .2, 1.8, .3, "head")

# sandbags along the bank edge, a stack and a lone barrel
for i in range(14):
    slab(-9 + i * 1.4, 5.6 + (i % 2) * .4, .1, 1.3, .9, .6, "sandbag", rot=(0, 0, random.uniform(-.2, .2)), top=.8)
for i in range(5): slab(-11 + (i % 3) * .9, 6.5, .1 + (i // 3) * .6, 1.3, .9, .6, "sandbag", top=.8)
tube(10.5, 8, 0, .8, 1.8, 8, "army"); tube(10.5, 8, 1.8, .7, .1, 8, "tyre")
slab(9.5, 6.0, 0, .2, .2, 3.0, "steel"); slab(9.5, 6.0, 3.0, 1.2, .2, .5, "lampred")
lamp("POINT", (1, .1, .08), 120, (9.5, 6.0, 3.0))
for i in range(3): slab(7 + i * 1.2, 5.6, 0, 1.0, .8, .6, "sandbag", top=.8)

lamp("SUN", (1, .55, .3), 5, (-30, -18, 10), (0, 0, 1)); lamp("SUN", (.4, .6, .9), 2.2, (26, 24, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .025, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 2, 1.5)); co.location = t + Vector((12, -62, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
