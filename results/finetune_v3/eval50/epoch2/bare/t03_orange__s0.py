import bpy, bmesh, random, math
from mathutils import Vector
random.seed(557)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def shade(c, e=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .8
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
def add(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(p, s, m, rz=0, top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return add(bm, m, p, (0, 0, rz))
def cone(p, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, p, rot)
def ball(p, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= sq
    return add(bm, m, p)
def glowlight(kind, p, c, w, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
wood, wood2, cloth, cloth2 = shade((.22, .12, .06)), shade((.16, .09, .045)), shade((.45, .12, .1)), shade((.55, .2, .12))
orange, dimple, leaf, stem = shade((.95, .32, .03)), shade((.7, .2, .02)), shade((.1, .4, .1)), shade((.3, .2, .08))
lamp, bulb, page, book = shade((.2, .1, .06)), shade((1, .75, .35), 25), shade((.6, .55, .45)), shade((.1, .25, .3))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=9, depth=2.2)
for v in bm.verts:
    v.co.z -= 1.1
    if v.co.z < -1: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .2)))
add(bm, wood2)
for i in range(10):
    a = i * .628
    cube((math.cos(a) * 8.6, math.sin(a) * 8.6, 0), (2.4, .5, .15), wood, a + 1.57)
for i in range(8):
    a = i * .785 + .3
    cube((math.cos(a) * 7.8, math.sin(a) * 7.8, 0), (1.5, .3, .12), wood2, a + 1.57)
# table top with a cloth, and the oversized orange on a little stand
cube((0, 0, 0), (11.5, 8.5, 1.0), wood)
cube((0, 0, 1.0), (9.5, 7, .12), cloth)
cube((0, 0, 1.1), (8.5, 6, .1), cloth2)
cone((0, 0, 1.1), 2.4, .3, 8, wood2, 2.0)
cone((0, 0, 1.4), 2.0, .2, 8, wood)
ball((0, 0, 3.6), 2.3, orange, .96)
# dimples: a lattice of little dark pits, plus a few lighter ones
for i in range(46):
    a = random.uniform(0, 6.28); z = random.uniform(-.8, .8)
    r = 2.3 * math.sqrt(1 - z * z) * .98
    d = Vector((math.cos(a) * r, math.sin(a) * r, z * 2.3 * .96)); d.normalize()
    cone(d * 2.2, .13, .1, 5, dimple, .05, d.to_track_quat('Z', 'Y').to_euler())
# stem nub and a small green leaf, oversized
cone((0, 0, 5.1), .35, .4, 5, stem, .2)
lf = bmesh.new(); bmesh.ops.create_cone(lf, cap_ends=True, segments=5, radius1=.5, radius2=.05, depth=1.6)
for v in lf.verts: v.co.y *= .55
add(lf, leaf, (1.0, 0, 5.6), (0, -1.1, .5))
cone((.35, 0, 5.4), .08, .8, 4, stem, .05, (0, -.5, 0))
# books, a bowl of fruit, a teacup, a lamp
for i, (x, y, r, c) in enumerate(((-3.4, 1.8, .3, book), (-3.3, 1.7, .1, page), (-3.5, 1.9, .5, shade((.5, .1, .15))))):
    cube((x, y, 1.1 + i * .35), (2.4, 1.7, .35), c, r)
cube((3.2, 2.2, 1.1), (2.2, 1.6, .3), book, .2)
cone((3.2, -1.8, 1.1), 1.3, .6, 8, shade((.5, .5, .55)), 1.0)
for i, c in enumerate((shade((.9, .2, .05)), shade((.9, .6, .05)), shade((.7, .3, .05)))):
    ball((3.2 + (i - 1) * .6, -1.8 + (i % 2) * .4 - .2, 1.9), .5, c, .85)
cone((-1.2, -2.2, 1.1), .55, .5, 8, shade((.7, .7, .65)), .75)
cone((-1.2, -2.2, 1.6), .5, .05, 8, shade((.3, .18, .08)))
cube((-1.7, -2.2, 1.3), (.4, .12, .12), shade((.7, .7, .65)))
cone((4.4, -.5, 1.1), .12, 2.2, 5, lamp)
cone((4.4, -.5, 3.3), .5, .5, 6, lamp, .8); ball((4.4, -.5, 3.9), .3, bulb)
glowlight("POINT", (4.4, -.5, 3.9), (1, .7, .3), 500)
# a small glowing fruit-juice jar on the cloth
cone((-4.4, -2.0, 1.1), .4, .9, 7, shade((1, .55, .08), 6), .35)
glowlight("POINT", (-4.4, -2.0, 1.8), (1, .5, .1), 150)
glowlight("SUN", (-16, -10, 7), (1, .6, .25), 5, (0, 0, 2))
glowlight("SUN", (12, 14, 9), (.4, .5, 1), 2.2, (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.6)); co.location = t + Vector((12, -32, 20))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
