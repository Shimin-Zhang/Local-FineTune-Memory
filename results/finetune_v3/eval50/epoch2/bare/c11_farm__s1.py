import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(170)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def mix(c, e=0):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .9
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
turf, hay, red, white, steel, tyre, wood, glass, soil, lamp = (mix((.12, .2, .07)), mix((.55, .4, .12)), mix((.45, .08, .06)), mix((.6, .58, .5)), mix((.3, .32, .35)), mix((.03, .03, .03)),
    mix((.3, .2, .12)), mix((1, .75, .35), 7), mix((.2, .13, .08)), mix((1, .85, .5), 14))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def bx(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = V((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cn(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def lt(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=8, radius2=14.5, depth=3.4)
for v in bm.verts:
    v.co.z -= 1.7
    if v.co.z < -1: v.co += V((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.6, .2)))
mk(bm, turf)
# barn: red walls, gambrel roof of dark boards, big lit doors, hayloft window
bx((0, 4, 0), (8, 5.4, 3.2), red)
bx((0, 4, 3.2), (8.6, 6.0, 1.0), white)
bx((0, 4, 4.2), (8.6, 6.0, .5), white, (0, 0, 0)).scale.y = .5
bx((0, 4, 4.5), (8.0, 4.2, .8), red)
bx((0, 1.25, 0), (3.0, .2, 2.6), soil); bx((0, 1.2, 0), (2.4, .1, 2.2), glass)
bx((0, 1.2, 3.0), (1.2, .1, 1.0), glass)
lt("POINT", (1, .7, .3), 700, (0, -.2, 1.6)); lt("POINT", (1, .7, .3), 250, (0, -.2, 3.2))
for s in (-1, 1): bx((s * 4.3, 4, 0), (.3, 5.6, 3.4), red)
# silo: cylinder, band rings, conical cap, ladder, glowing vent
cn((7.5, 4.5, 0), 1.9, 8.0, 9, steel); cn((7.5, 4.5, 8.0), 2.1, 1.6, 9, red, .2)
for z in (2, 4, 6): cn((7.5, 4.5, z), 1.98, .2, 9, white)
for k in range(6): bx((7.5, 2.5, .6 + k * 1.0), (.12, .12, 1.0), white)
bx((7.0, 2.5, 0), (.1, .1, 6.6), white); bx((8.0, 2.5, 0), (.1, .1, 6.6), white)
# tractor: body, cab, exhaust, big rear wheels, small front wheels, headlamp
tx, ty = -7.0, -1.5
bx((tx, ty, 1.2), (3.2, 1.5, .8), red); bx((tx - .2, ty, 2.0), (1.6, 1.4, 1.2), white); bx((tx - .2, ty, 3.2), (1.8, 1.6, .15), red)
bx((tx + 1.4, ty, 1.9), (.5, .8, .9), steel); cn((tx + 1.0, ty, 2.8), .12, 1.2, 6, steel)
for s in (-1, 1):
    cn((tx - .7, ty + s * .95, .85), .85, .4, 9, tyre, rot=(math.pi / 2, 0, 0)); cn((tx + 1.0, ty + s * .85, .55), .55, .35, 8, tyre, rot=(math.pi / 2, 0, 0))
bx((tx + 1.65, ty - .4, 1.2), (.1, .3, .3), lamp); bx((tx + 1.65, ty + .4, 1.2), (.1, .3, .3), lamp)
lt("POINT", (1, .85, .5), 250, (tx + 2.2, ty, 1.4))
# three hay bales, a fence round the yard, a well and a tree
for x, y in ((-2.5, -4.5), (1.0, -5.5), (-.8, -3.0)): cn((x, y, 0), .8, 1.5, 7, hay, rot=(0, math.pi / 2, random.uniform(0, 3)))
for i in range(15):
    x = -12 + i * 1.7
    if x > -1.5 and x < 1.5: continue
    bx((x, -8, 0), (.18, .18, 1.2), wood)
for i in range(9): bx((-12 + i * 1.5, -8, .8), (1.6, .1, .12), wood)
for i in range(9): bx((-12 + i * 1.5, 10, .8), (1.6, .1, .12), wood) if i < 9 else None
cn((-9, 6.5, 0), .9, 1.0, 8, white); cn((-9, 6.5, 1.0), .75, .15, 8, soil)
cn((9, -4, 0), .25, 3.2, 5, wood); cn((9, -4, 3.0), 1.8, 2.2, 6, mix((.08, .25, .1)), .1)
lt("SUN", (1, .6, .25), 5, (-24, -10, 9), (0, 0, 2)); lt("SUN", (.3, .5, .85), 2.2, (20, 18, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .035, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co); sc.camera = co
co.location = V((24, -50, 34)); co.rotation_euler = (V((0, 1, 2)) - co.location).to_track_quat('-Z', 'Y').to_euler()
