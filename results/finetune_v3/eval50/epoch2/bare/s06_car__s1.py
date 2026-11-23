import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(1673)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
S = bpy.context.scene
def paint(rgb, e=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .5
    if e: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = e
    return m
road, asphalt, line, kerb, blue, blue2, glass, tyre, hub, steel, neon, pink, white, dark = (paint((.04, .04, .055)), paint((.1, .1, .13)), paint((.9, .8, .2)), paint((.2, .2, .22)), paint((.03, .2, .85)),
    paint((.02, .1, .55)), paint((.03, .05, .09)), paint((.02, .02, .025)), paint((.5, .5, .55)), paint((.3, .3, .34)), paint((.1, .9, 1), 12), paint((1, .1, .5), 12), paint((.9, .9, .9)), paint((.02, .02, .03)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    S.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = V((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def light(kind, at, col, w, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; S.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: a street block of asphalt with a rough underside, kerbs and lane dashes
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = V((v.co.x * 19 + random.uniform(-1.5, 1.5), v.co.y * 10 + random.uniform(-1, 1), -3.5 + random.uniform(-1, .5)))
    else: v.co = V((v.co.x * 24, v.co.y * 14, 0))
mk(bm, road)
for sy in (-1, 1): cube((0, sy * 6.4, 0), (24, 1.2, .5), kerb)
for i in range(8): cube((-10.5 + i * 3, 0, .02), (1.6, .25, .03), line)
# the car: tapered body, cabin, glass, spoiler, lights, exhausts
cube((0, 0, .7), (6.4, 2.6, 1.1), blue, top=.88)
cube((0, 0, 1.8), (6.2, 2.4, .12), blue2)
cube((.1, 0, 1.8), (3.0, 2.2, 1.2), blue2, top=.75)
cube((.1, 0, 2.0), (2.6, 2.0, .9), glass, top=.7)
cube((-3.4, 0, 1.5), (.5, 1.8, .35), blue2); cube((-3.7, 0, 1.75), (.2, 1.6, .1), blue2)
cube((-3.25, 0, 1.55), (.1, 2.0, .3), pink)
for sy in (-1, 1):
    cube((3.2, sy * .85, 1.2), (.2, .7, .3), white)
    drum((3.6, sy * .8, .6), .12, .5, 5, steel, rot=(0, math.pi / 2, 0))
# four black wheels: tyre, hub, glowing brake ring
for wx in (-2.1, 2.1):
    for wy in (-1.3, 1.3):
        drum((wx, wy * 1.05, .7), .72, .55, 10, tyre, rot=(math.pi / 2, 0, 0)).location.y = wy * 1.05 - .27
        drum((wx, wy * 1.05, .7), .38, .6, 6, hub, rot=(math.pi / 2, 0, 0)).location.y = wy * 1.05 - .3
        drum((wx, wy * 1.05, .7), .3, .62, 6, neon if wx < 0 else pink, rot=(math.pi / 2, 0, 0)).location.y = wy * 1.05 - .31
# neon signs on the kerbs, a lamp post, a bin, a bench
cube((-8, 6.8, 1.2), (4.5, .3, 1.4), neon); cube((-8, 6.6, 1.4), (3.4, .1, .3), white)
cube((7, 6.8, 1.2), (4.0, .3, 1.2), pink); cube((7, 6.6, 1.4), (3.0, .1, .3), white)
drum((10, -6.2, 0), .15, 4.5, 5, steel); cube((10, -6.2, 4.5), (1.4, .3, .2), white); cube((10, -6.2, 4.3), (1.0, .15, .2), neon)
drum((-10, -6.2, 0), .4, 1.0, 7, steel); cube((-6, -6.2, .5), (2.2, .6, .15), steel)
for sy in (-1, 1): cube((-6, -6.2 + sy * .3, 0), (.15, .15, .5), steel)
light("POINT", (-8, 6.2, 2.0), (.1, .9, 1), 600); light("POINT", (7, 6.2, 2.0), (1, .1, .5), 600); light("POINT", (10, -6.2, 4.2), (.1, .9, 1), 250)
light("SUN", (-24, -18, 10), (.4, .6, 1), 4, (0, 0, 1)); light("SUN", (24, 20, 9), (1, .2, .6), 2.5, (0, 0, 1))
w = bpy.data.worlds.new("w"); w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .01, .03, 1)
S.world = w
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); S.collection.objects.link(co)
tgt = V((0, 0, 1.4)); co.location = tgt + V((11, -52, 27))
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler(); S.camera = co
