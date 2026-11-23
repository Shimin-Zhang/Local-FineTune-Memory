import bpy, bmesh, math, random
from mathutils import Vector
random.seed(835)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, em=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
sand, sand2, track, sea, shallows, trunk, frond, tin, wall, wood, pink, roof, tyre, lampm = (col(c) for c in (
    (.42, .33, .2), (.36, .28, .17), (.3, .24, .16), (.03, .25, .3), (.1, .5, .45), (.25, .17, .1), (.07, .3, .12), (.5, .52, .55), (.55, .3, .2), (.3, .2, .12), (.6, .2, .25), (.45, .12, .1), (.03, .03, .03), (1, .7, .3)))
lampm = col((1, .7, .3), 14); bulb = col((1, .85, .5), 10)
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(x, y, z, w, d, h, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mesh(bm, m, (x, y, z), (0, 0, rz))
def cyl(x, y, z, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, (x, y, z))
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mesh(bm, m)
def palm(x, y, h, lean):
    pts = [Vector((0, 0, 0)), Vector((lean * .3, 0, h * .4)), Vector((lean * .8, 0, h * .75)), Vector((lean, 0, h))]
    for i in range(3): strut(pts[i], pts[i + 1], .35 - i * .06, trunk)
    for k in range(7):
        a = k * 2 * math.pi / 7 + x
        strut((x + lean, y, h), (x + lean + math.cos(a) * 2.4, y + math.sin(a) * 2.4, h - .9), .35, frond)
def lamp(x, y):
    strut((x, y, 0), (x, y, 3.2), .1, wood); box(x, y, 3.2, .5, .5, .5, lampm)
    L = bpy.data.lights.new("l", "POINT"); L.color = (1, .7, .3); L.energy = 260
    o = bpy.data.objects.new("l", L); o.location = (x, y, 3.4); sc.collection.objects.link(o)
# base: sand slab, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
mesh(bm, sand)
# turquoise bay behind: shallows ring and a deep patch, with foam line
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=13.2, radius2=13.2, depth=.12)
mesh(bm, shallows, (0, 0, .02))
bay = bmesh.new(); bmesh.ops.create_cone(bay, cap_ends=True, segments=10, radius1=12.2, radius2=12.2, depth=.2)
for v in bay.verts:
    if v.co.y < 0: v.co.y = 0
mesh(bay, sea, (0, 0, .1))
for i in range(12):
    a = .15 + i * .14
    box(math.cos(a) * 12.4, math.sin(a) * 12.4, .12, 1.2, .25, .06, tin, rz=a + 1.57)
# sandy track winding from front to the bay, with ruts
for i in range(10):
    t = i / 9
    x = 1.5 * math.sin(t * 5) - 1 + t * 3; y = -11 + t * 20
    box(x, y, 0, 3.2, 2.6, .1, track, rz=.2 * math.cos(t * 5))
    for s in (-.8, .8): box(x + s, y, .1, .25, 2.4, .04, sand2)
# roadside shop with tin roof, awning, counter, crates, neon sign
sx, sy = -8, 2
box(sx, sy, 0, 5.2, 3.6, 2.4, wall); box(sx, sy, 2.4, 5.8, 4.2, .15, tin, rz=0)
for k in range(6): box(sx - 2.6 + k * 1.04, sy, 2.55, .12, 4.2, .1, wood)
box(sx + 2.65, sy, 0, .1, 3.6, 2.4, lampm); box(sx - 1, sy - 1.85, 1.7, 3.2, .15, .6, pink)
box(sx, sy - 2.6, 1.6, 4.6, 1.6, .1, roof, top=1)
for dx in (-2, 2): strut((sx + dx, sy - 3.2, 0), (sx + dx, sy - 3.2, 1.7), .1, wood)
box(sx, sy - 1.2, 0, 2.4, .8, .9, wood); box(sx + 2.6, sy - 2.6, 0, .8, .8, .7, wood); box(sx + 2.6, sy - 2.6, .7, .6, .6, .5, pink)
box(sx - 1.2, sy - 2.6, 0, .8, .8, .7, wood)
L = bpy.data.lights.new("s", "POINT"); L.color = (1, .65, .3); L.energy = 600
o = bpy.data.objects.new("s", L); o.location = (sx, sy - 1.5, 1.4); sc.collection.objects.link(o)
# tuk-tuk without a driver: body, canopy, three wheels, headlamps
tx, ty, tr = 2.5, -5, .4
def at(rz, dx, dy, z=0): return (tx + dx * math.cos(rz) - dy * math.sin(rz), ty + dx * math.sin(rz) + dy * math.cos(rz), z)
box(*at(tr, 0, 0, .6), 2.4, 1.4, 1.0, pink, rz=tr, top=.8)
box(*at(tr, .8, 0, .5), .1, 1.5, 1.2, wood, rz=tr); box(*at(tr, 0, 0, 1.6), 1.8, 1.6, .12, tin, rz=tr)
for dx, dy, r in ((1.2, 0, .65), (-1.1, -.7, .5), (-1.1, .7, .5)):
    p = at(tr, dx, dy, r); cyl(p[0], p[1], p[2], r, .35, 8, tyre).rotation_euler = (0, math.pi / 2, tr)
for s in (-.4, .4): box(*at(tr, 1.3, s, .9), .2, .3, .3, bulb, rz=tr)
# hammock between two palms, and a beach ball
for (x, y, h, l) in ((-3, 6, 7, .8), (3, 7, 6.5, -.7), (-10, 7, 6.5, -.6), (10, 5, 7, .7), (-6, -9, 6, .5), (9, -9, 6.5, -.5), (11, -2, 6, .4)): palm(x, y, h, l)
for i in range(8):
    t = i / 7; p = Vector((-3.8 + t * 6.8, 6.5, 3.6 - math.sin(t * math.pi) * 1.5))
    if i: strut(p - Vector((-3.8 + (t - 1 / 7) * 6.8, 6.5, 3.6 - math.sin((t - 1 / 7) * math.pi) * 1.5)), p, .22, wood)
strut((-3, 6, 3.6), (-3.8, 6.5, 3.6), .06, tin); strut((3, 7, 3.6), (3.8, 6.5, 3.6), .06, tin)
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.6)
mesh(bm, pink, (6, -7, .6))
# lamp posts along the track
for (x, y) in ((-2, -9), (3.5, -1), (5, 6)): lamp(x, y)
# light: warm low sunset from the left, teal rim from behind
for c, w, p in (((1, .6, .3), 5.5, (-26, -14, 8)), ((.3, .8, .8), 2.2, (20, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("sunset"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .04, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 2)); co.location = tg + Vector((14, -58, 36))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
