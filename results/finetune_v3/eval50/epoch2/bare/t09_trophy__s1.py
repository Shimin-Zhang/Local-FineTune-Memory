import bpy, bmesh, random, math
from mathutils import Vector as V
random.seed(991)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def gold(r, g, b, e=0, rough=.35, metal=1):
    m = bpy.data.materials.new("g"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if e: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = e
    return m
brass, brass2, dark, velvet, wood, gem, ink = gold(.85, .58, .12), gold(.55, .38, .08), gold(.2, .14, .05), gold(.4, .03, .06, 0, .9, 0), gold(.16, .09, .05, 0, .7, 0), gold(.1, .8, 1, 14), gold(.03, .02, .02, 0, .9, 0)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("t"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("t", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def bar(a, b, t, m, t2=None):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ V((v.co.x * t, v.co.y * (t2 or t), (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def ball(at, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, m, at)
def beam(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# round plinth: velvet top, wood sides, tapering underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5.5, radius2=9.2, depth=3.0)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.2, .2)))
    v.co.z -= 1.5
mk(bm, wood)
drum((0, 0, -.05), 8.4, .1, 10, velvet)
# trophy base: stepped blocks, a nameplate and a gem
drum((0, 0, 0), 3.0, .5, 8, dark); drum((0, 0, .5), 2.4, .5, 8, brass2, 2.1); drum((0, 0, 1.0), 1.7, .6, 8, brass, 1.3)
drum((0, 0, 1.6), 1.3, .5, 8, brass2, 1.0)
bar((0, -2.55, .75), (0, -2.55, 1.1), 1.2, ink); bar((0, -2.57, .9), (0, -2.57, .98), .9, brass)
ball((0, -2.5, .2), .3, gem, 1.0)
# stem: faceted column, rings and a node
drum((0, 0, 2.1), .45, 1.2, 6, brass2, .35); drum((0, 0, 3.3), .35, 1.0, 6, brass, .5)
drum((0, 0, 2.7), .62, .15, 6, brass); drum((0, 0, 3.9), .62, .15, 6, brass)
# bowl: stacked rings from wide rim to narrow foot, with a lip and inner glow
for i, (r1, r2, z) in enumerate(((1.0, 1.3, 4.05), (1.3, 1.7, 4.4), (1.7, 2.1, 4.8), (2.1, 2.4, 5.2), (2.4, 2.6, 5.6), (2.6, 2.7, 6.0), (2.7, 2.7, 6.4))):
    drum((0, 0, z), r1, .4, 10, brass if i % 2 else brass2, r2)
drum((0, 0, 6.4), 2.85, .22, 10, brass2, 2.7); drum((0, 0, 6.6), 2.5, .08, 10, dark)
drum((0, 0, 6.5), 2.3, .06, 10, gem)
beam('POINT', (.1, .8, 1), 500, (0, 0, 7.0))
# handles: swept bars curving out and back, with a finial at each end
for s in (-1, 1):
    pts = [(2.7, 0, 6.2), (3.5, 0, 6.0), (4.1, 0, 5.4), (4.2, 0, 4.6), (3.9, 0, 3.8), (3.2, 0, 3.2), (2.5, 0, 3.0)]
    for a, b in zip(pts, pts[1:]): bar((a[0] * s, a[1], a[2]), (b[0] * s, b[1], b[2]), .34, brass)
    ball((s * 2.5, 0, 2.9), .3, brass2)
# laurels on the front of the bowl: two arcs of leaves
for s in (-1, 1):
    for k in range(8):
        a = math.radians(150 + k * 10)
        p = V((s * 2.55 * math.cos(a) * .9, -1.8, 5.2 + 1.0 * math.sin(a)))
        bar(p - V((s * .3, 0, .1)), p + V((s * .3, 0, .1)), .14, brass2, .5)
# a pedestal lamp and a trophy case window frame behind
for sx in (-1, 1):
    drum((sx * 5.8, 3.0, 0), .35, 3.6, 6, ink, .25); drum((sx * 5.8, 3.0, 3.6), .9, .4, 6, brass2, .5)
beam('POINT', (1, .65, .25), 400, (-5.8, 3.0, 3.9)); beam('POINT', (1, .65, .25), 400, (5.8, 3.0, 3.9))
# spotlight beams and rim light
beam('SUN', (1, .8, .5), 5, (-14, -12, 10), (0, 0, 4)); beam('SUN', (.4, .55, 1), 2, (12, 14, 9), (0, 0, 4))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = V((0, 0, 3.8)); co.location = t + V((9, -34, 21))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
