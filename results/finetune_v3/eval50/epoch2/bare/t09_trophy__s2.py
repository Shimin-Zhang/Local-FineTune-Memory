import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1820)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def metal(c, e=0, r=.35):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
def mk(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def ring(m, x, y, z, r1, r2, h, n=10, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z), rot)
def orb(m, x, y, z, r, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, m, (x, y, z))
def bar(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def beam(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
gold, gold2, gold3 = metal((.62, .42, .08), r=.3), metal((.8, .58, .14), r=.22), metal((.42, .26, .05), r=.4)
plaque, velvet, wood = metal((.03, .025, .03)), metal((.3, .02, .06)), metal((.16, .09, .05))
gem, glow = metal((.1, .8, 1), 6), metal((1, .75, .3), 5)
# round pedestal: dark wood top, gold band, stepped base
ring(wood, 0, 0, 0, 3.4, 4.2, 1.0, 10); ring(gold, 0, 0, 1.0, 4.2, 4.2, .12, 10); ring(plaque, 0, 0, 1.12, 3.6, 3.6, .5, 10)
ring(gold2, 0, 0, 1.62, 3.0, 3.0, .15, 10); ring(velvet, 0, 0, 1.77, 2.9, 2.9, .1, 10)
for i in range(10): ring(gold2 if i % 2 else gold, 4.2 * math.cos(i * .628), 4.2 * math.sin(i * .628), .3, .2, .2, .3, 5, (0, math.pi / 2, i * .628 + .314))
# the cup: foot, stem, node, bowl, rim
ring(gold, 0, 0, 1.87, 1.2, .7, .3, 8); ring(gold2, 0, 0, 2.17, .55, .3, .9, 8); ring(gold, 0, 0, 3.07, .9, .9, .22, 8)
ring(gold2, 0, 0, 3.29, .3, .75, .9, 8); ring(gold, 0, 0, 4.19, .8, 2.1, 1.9, 8); ring(gold2, 0, 0, 6.05, 2.1, 2.2, .12, 8)
ring(glow, 0, 0, 6.17, 1.9, 1.9, .05, 8)
for i in range(8): ring(gold2 if i % 2 else gold3, 1.45 * math.cos(i * .785), 1.45 * math.sin(i * .785), 4.5, .12, .12, 1.2, 4)
# two scrolled handles: bars around a half ring each side
for s in (-1, 1):
    for k in range(8):
        a, b = math.radians(-80 + k * 22.8), math.radians(-80 + (k + 1) * 22.8)
        bar(gold2, (s * (2.0 + 1.0 * math.cos(a)), 0, 4.4 + 1.1 * math.sin(a)), (s * (2.0 + 1.0 * math.cos(b)), 0, 4.4 + 1.1 * math.sin(b)), .22)
    orb(gold, s * 3.0, 0, 4.4, .28, 1.3)
# gems set into the bowl and the plaque, with a glowing core
for k in range(5):
    a = k * 1.256 + .3; orb(gem, 1.9 * math.cos(a) * .9, 1.9 * math.sin(a) * .9, 5.1 - abs(k - 2) * .15, .22)
orb(gem, 0, -2.95, 2.0, .3)
for k in range(3): orb(gem, -1.2 + k * 1.2, -3.62, 1.37, .13)
beam("POINT", (.1, .8, 1), 500, (0, -3.5, 2.0)); beam("POINT", (1, .75, .3), 400, (0, 0, 6.8))
# velvet cushion, a few medals and a small plate on the plinth
orb(velvet, 3.0, -2.4, .1, .9, .45); orb(velvet, -3.1, -2.2, .1, .8, .4)
for k, (x, y) in enumerate(((2.6, -2.8), (3.4, -2.1), (-3.4, -2.6))): ring(gold2, x, y, .5, .35, .35, .08, 8, (math.pi / 2, 0, 0))
ring(gold, -3.1, -2.2, .3, .5, .5, .08, 8)
# a trophy room corner: two walls, a banner, a shelf of small cups
ring(plaque, 0, 6.5, 0, .1, .1, .1, 4)
for i in range(4): bar(gold2, (-3.5 + i * 2.3, 5.8, 0), (-3.5 + i * 2.3, 5.8, 6.5), .1)
for z in (6.5, 1.0): bar(gold, (-4, 5.8, z), (4, 5.8, z), .1)
for i in range(3): ring(gold3, -2.5 + i * 2.5, 5.2, 0, .5, .3, .6, 6); ring(gold2, -2.5 + i * 2.5, 5.2, .6, .3, .7, .8, 6)
bar(gold, (-4, 5.2, 1.4), (4, 5.2, 1.4), .25)
beam("SUN", (1, .8, .45), 5, (-14, -12, 8), (0, 0, 3)); beam("SUN", (.4, .5, 1), 2.5, (12, 14, 6), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .012, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.6)); co.location = t + Vector((9, -33, 21))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
