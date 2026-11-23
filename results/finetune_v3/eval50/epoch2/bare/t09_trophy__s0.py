import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1752)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
G = {}
def alloy(k, c, e=0, r=.5, m=0):
    mt = bpy.data.materials.new(k); mt.use_nodes = True
    n = next(x for x in mt.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r; n.inputs["Metallic"].default_value = m
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    G[k] = mt
alloy("brush", (.8, .55, .12), 0, .35, 1); alloy("brush2", (.55, .36, .08), 0, .4, 1); alloy("plinth", (.1, .07, .05), 0, .8)
alloy("plinth2", (.2, .13, .08), 0, .8); alloy("velvet", (.35, .02, .05), 0, 1); alloy("ruby", (1, .05, .08), 14, .3)
alloy("rim", (1, .75, .25), 3, .3, 1); alloy("spot", (.9, .7, .35), 0, .4, 1); alloy("brass", (.5, .35, .1), 0, .4, 1)
def mk(bm, k, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("t"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("t", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(G[k]); return o
def lathe(k, prof, n=12, p=(0, 0, 0), r=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=.1, radius2=.1, depth=1)
    for v in bm.verts:
        f = next(q for q in prof if abs(v.co.z - q[0]) < .06)
        v.co.x, v.co.y, v.co.z = f[1] * v.co.x * 10, f[2] * v.co.y * 10, (v.co.z + .5) * q[3]
    return mk(bm, k, p, r)
def bar(k, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, k)
def gem(k, p, s, j=0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2])) + Vector((random.uniform(-j, j), random.uniform(-j, j), random.uniform(-j, j)))
    return mk(bm, k, p)
def shine(kind, c, w, p, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# round plinth on a floating dark base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=4, radius2=7.4, depth=2.4)
for v in bm.verts:
    v.co.z -= 1.2
    if v.co.z < -.5: v.co += Vector((random.uniform(-.6, .6), random.uniform(-.6, .6), random.uniform(-.9, .2)))
mk(bm, "plinth")
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=7.4, radius2=7.4, depth=.2)
for v in bm.verts: v.co.z += .1
mk(bm, "brush2")
for i in range(8):
    a = i * math.pi / 4 + .39
    bar("plinth2", (6.9 * math.cos(a), 6.9 * math.sin(a), .2), (6.9 * math.cos(a), 6.9 * math.sin(a), 1.2), .25)
# three tiers, velvet-draped top with gold trim
lathe("plinth2", [(0, 3.2, 3.2), (.05, 3.2, 3.2), (1, 3.0, 3.2)], 8, (0, 0, 0))
lathe("plinth2", [(0, 2.4, 2.4), (.05, 2.4, 2.4), (1, 2.2, 2.4)], 8, (0, 0, 3.2))
lathe("plinth2", [(0, 1.7, 1.7), (.05, 1.7, 1.7), (1, 1.5, 1.7)], 8, (0, 0, 5.6))
lathe("velvet", [(0, 1.5, 1.5), (.05, 1.5, 1.5), (1, 1.45, 1.5)], 8, (0, 0, 7.3))
lathe("brush", [(0, 1.56, 1.56), (.05, 1.56, 1.56), (1, 1.5, 1.5)], 8, (0, 0, 8.8))
for i in range(8):
    a = i * math.pi / 4
    gem("ruby", (1.3 * math.cos(a), 1.3 * math.sin(a), 7.3), (.22, .22, .18), .03)
# the cup: foot, stem, swelling bowl, glowing rim
lathe("brush", [(0, 1.3, 1.3), (.05, 1.3, 1.3), (1, 1.1, 1.3)], 12, (0, 0, 9.3))
lathe("brush2", [(0, .35, .35), (.3, .28, .28), (.6, .5, .5), (1, .3, .3)], 12, (0, 0, 10.6))
lathe("brush", [(0, .85, .85), (.2, .6, .6), (.45, .7, .7), (.7, 1.0, 1.0), (1, 1.7, 1.7)], 12, (0, 0, 12.4))
lathe("rim", [(0, 1.72, 1.72), (.05, 1.72, 1.72), (1, 1.72, 1.72)], 12, (0, 0, 14.1))
lathe("brush2", [(0, 1.5, 1.5), (.05, 1.5, 1.5), (1, 1.45, 1.45)], 12, (0, 0, 14.12))
# two C-shaped handles with lugs
for s in (-1, 1):
    for z in (12.7, 13.7):
        bar("brush2", (s * 1.6, 0, z), (s * 2.3, 0, z), .22)
    for i in range(9):
        a0, a1 = math.radians(-80 + i * 20), math.radians(-80 + (i + 1) * 20)
        bar("brush", (s * (2.3 + 1.1 * math.cos(a0)), 0, 13.2 + 1.0 * math.sin(a0)), (s * (2.3 + 1.1 * math.cos(a1)), 0, 13.2 + 1.0 * math.sin(a1)), .26)
# spotlights on a ring bar behind, aimed at the cup
bar("plinth", (-5, 6.5, 0), (-5, 6.5, 12), .25); bar("plinth", (5, 6.5, 0), (5, 6.5, 12), .25); bar("plinth", (-5, 6.5, 12), (5, 6.5, 12), .25)
for x in (-4, 0, 4):
    gem("spot", (x, 6.0, 11.6), (.5, .4, .4)); shine("POINT", (1, .8, .4), 300, (x, 5.2, 11.4))
shine("SUN", (1, .78, .4), 5, (-14, -10, 10), (0, 0, 8)); shine("SUN", (.4, .55, 1), 2, (12, 14, 9), (0, 0, 8))
w = bpy.data.worlds.new("hall"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 8)); co.location = t + Vector((6, -40, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
