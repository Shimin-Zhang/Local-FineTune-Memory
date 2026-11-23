import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1744)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
grass, grass2, travertine, travertine2, oak, oakdark, water, clay, roofred, fire, smoke = (pigment(c) for c in (
    (.12, .17, .07), (.09, .13, .06), (.42, .36, .28), (.3, .25, .2), (.25, .16, .09), (.15, .09, .06), (.06, .2, .3), (.4, .22, .12), (.45, .15, .1), (1, .5, .1), (.3, .3, .32)))
flame = pigment((1, .45, .08), 12); hearth = pigment((1, .6, .2), 6)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); me.materials.append(m); return o
def block(at, d, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * k, v.co.y * d[1] * k, (v.co.z + .5) * d[2]))
    return shape(bm, m, at, (0, 0, rz))
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, at, rot)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return shape(bm, m)
def roofed(at, w, d, h, m, ridge=0):
    bm = bmesh.new(); p = [bm.verts.new(c) for c in ((-w, -d, 0), (w, -d, 0), (w, d, 0), (-w, d, 0), (-w + ridge, 0, h), (w + ridge, 0, h))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): bm.faces.new([p[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return shape(bm, m, at)
def glimmer(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# hillside: a stepped slope of eight terraces, each one a grass slab with a travertine retaining wall
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co.x *= .8 + random.random() * .2; v.co.y *= .8 + random.random() * .2; v.co.z -= random.random() * 1.5
    v.co = Vector((v.co.x * 25, v.co.y * 22, v.co.z * 4 - 2))
shape(bm, grass2)
for i in range(8):
    y = 8.2 - i * 2.1
    block((0, y, 0), (24, 2.1, 1.0 + i * .0), grass if i % 2 else grass2)
    block((0, y - 1.05, 0), (24, .5, .9), travertine2)
# two rows of eight water wheels, stepped down the slope: a trough with a water wheel and an axle post each
for row, x in enumerate((-5.5, 5.5)):
    for i in range(8):
        y = 8.0 - i * 2.1; z = .9 + i * .0
        block((x, y, 0), (2.4, 1.2, .7), travertine); block((x, y, .6), (2.0, .8, .1), water)
        drum((x, y, 1.0), .95, .15, 8, oak, rot=(math.pi / 2, 0, 0))
        for k in range(8):
            a = k * math.pi / 4; strut((x, y, 1.0), (x + math.cos(a) * .95, y + math.sin(a) * .95, 1.0), .1, oakdark)
        strut((x - 1.2, y, 1.0), (x + 1.2, y, 1.0), .12, oakdark)
        block((x - 1.2, y, 0), (.5, .5, 1.0), travertine2)
# the aqueduct along the top: a row of arches on piers carrying a trough, with a spill at each wheel
for i in range(8):
    x = -8.4 + i * 2.4
    block((x, 10.2, 0), (.7, .9, 3.4), travertine); block((x + 1.2, 10.2, 3.4), (1.0, .9, .5), travertine2)
block((0, 10.2, 3.9), (20, 1.0, .5), travertine); block((0, 10.2, 4.4), (20, .6, .15), water)
for x in (-5.5, 5.5): block((x, 9.7, 4.0), (.4, .3, .6), travertine2)
# the bakery at the foot of the hill: plaster walls, tile roof, chimney, arched door and a glowing oven mouth
bx, by = 0, -9.6
block((bx, by, 0), (8, 4.6, 2.6), travertine); roofed((bx, by, 2.6), 4.6, 2.6, 1.8, roofred)
block((bx + 2.5, by, 2.6), (.8, .8, 2.2), clay); block((bx + 2.5, by, 4.8), (1.1, 1.1, .3), travertine2)
block((bx, by - 2.35, 0), (1.4, .2, 1.8), oakdark); block((bx - 2.5, by - 2.35, 0), (1.6, .2, 1.2), hearth)
block((bx - 2.5, by - 2.5, 1.2), (2.0, .2, .3), clay)
glimmer((bx - 2.5, by - 3.2, 1.0), (1, .5, .15), 900); glimmer((bx, by - 3.2, 1.2), (1, .6, .3), 300)
# sacks of grain and a millstone beside the bakery, a few cypress and pines
for i in range(5): block((bx + 4.6 + (i % 3) * .7, by - 1.2 + (i // 3) * .7, 0), (.6, .5, .6), clay, rz=i)
drum((bx + 5.5, by - 2.5, 0), .8, .3, 8, travertine2)
for x, y in ((-10, -8), (10, -6), (-11, 2), (11, 3)):
    drum((x, y, 0), .2, 1.2, 5, oakdark)
    for k in range(3): drum((x, y, 1.0 + k * 1.3), 1.3 - k * .35, 1.8, 6, grass2, .05)
# lamps along the terrace steps
for i in range(4):
    block((-11.5, 7 - i * 4.4, 0), (.2, .2, 1.2), travertine2); block((-11.5, 7 - i * 4.4, 1.2), (.4, .4, .3), flame)
glimmer((-11.5, 5, 1.8), (1, .5, .15), 250)
for c, w, p in (((1, .62, .3), 5.5, (-26, -14, 8)), ((.4, .55, 1), 2.2, (22, 24, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dusk"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .04, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 85; cm.clip_end = 500
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((8, -62, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
