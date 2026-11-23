import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1715)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(rgb, em=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
limestone, limestone2, slate, dark, gold, win, bulb = paint((.42, .34, .24)), paint((.3, .24, .17)), paint((.12, .13, .17)), paint((.03, .03, .04)), paint((.7, .5, .12)), paint((1, .62, .22), 14), paint((1, .8, .4), 14)
def form(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("f"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("f", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return form(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return form(bm, m, at, rot)
def dome(at, r, m, sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co.z = max(v.co.z, 0) * 1.15
    return form(bm, m, at)
def rib(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return form(bm, m)
def bulb(at, c):
    o = blk(at, (.28, .28, .28), c); o.scale.z = 1.3; return o
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# square paving as the base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=8, radius2=15, depth=3.4)
for v in bm.verts:
    v.co.x *= 1.1; v.co.z -= 1.7
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
form(bm, limestone2)
for i in range(14):
    for j in range(10):
        if (i + j) % 2: blk((-12.6 + i * 2, -9 + j * 2, 0), (1.9, 1.9, .08), limestone)
# nave, apse and the great dome on a drum
blk((0, 4, 0), (7, 11, 4.6), limestone); blk((0, 4, 4.6), (7.6, 11.6, .5), limestone2)
blk((0, 4, 5.1), (6.2, 9.6, .3), slate)
blk((0, -1.6, 0), (7, 4.4, 4.6), limestone); blk((0, -1.6, 4.6), (7.6, 5, .5), limestone2)
cyl((0, 4, 5.1), 3.2, 3.0, 10, limestone); cyl((0, 4, 8.1), 3.4, .4, 10, limestone2)
dome((0, 4, 8.5), 3.2, slate)
for k in range(8):
    a = k * math.pi / 4; rib((math.cos(a) * 3.2, 4 + math.sin(a) * 3.2, 8.5), (math.cos(a) * .3, 4 + math.sin(a) * .3, 12.2), .18, gold)
cyl((0, 4, 12.2), .5, 1.4, 6, limestone); dome((0, 4, 13.6), .5, slate, 1); blk((0, 4, 13.9), (.1, .1, .9), gold)
for k in range(8):
    a = k * math.pi / 4 + .39; blk((math.cos(a) * 3.0, 4 + math.sin(a) * 3.0, 8.3), (.9, .6, 1.2), win, (0, 0, a + 1.57))
glow((0, 4, 9), (1, .62, .22), 700)
# front portico with columns and steps
for i in range(4): blk((-1.6 + i * 1.07, -4.4, 0), (.7, .7, 3.6), limestone)
blk((0, -4.4, 3.6), (4.6, 2.4, .4), limestone2); blk((0, -4.4, 4.0), (3.4, 1.8, .3), slate)
for k in range(3): blk((0, -5.8 - k * .5, 0), (5, .5, .35 - k * .12), limestone)
blk((0, -1.6, 0), (1.8, .3, 2.6), dark); blk((0, -1.6, 2.6), (1.8, .3, .5), win)
for sx in (-1, 1): blk((sx * 2.6, -1.6, 1.4), (.9, .25, 1.6), win)
# two bell towers with clock faces
for sx in (-1, 1):
    x = sx * 5.4
    blk((x, -1.6, 0), (3.4, 4.4, 9), limestone); blk((x, -1.6, 9), (3.8, 4.8, .4), limestone2)
    blk((x, -3.85, 3), (1.6, .2, 2.4), dark); blk((x, -3.85, 6), (1.4, .2, 1.2), win)
    cyl((x, -3.85, 9.4), 1.0, .25, 12, limestone2, rot=(math.pi / 2, 0, 0))
    cyl((x, -4.05, 9.4), .8, .1, 12, win, rot=(math.pi / 2, 0, 0))
    rib((x, -4.15, 9.4), (x, -4.15, 10.2), .08, dark); rib((x, -4.15, 9.4), (x + .5, -4.15, 9.7), .08, dark)
    cyl((x, -1.6, 9.4), 1.5, 2.2, 4, slate, 1.5, (0, 0, math.pi / 4)); cyl((x, -1.6, 11.6), .1, 1.2, 4, gold)
# festival strings of lights across the square
def strand(p, q, n):
    p, q = Vector(p), Vector(q)
    for i in range(n + 1):
        t = i / n; pt = p.lerp(q, t) - Vector((0, 0, 1.2 * math.sin(math.pi * t)))
        bulb(pt, bulb); 
        if i < n: rib(pt, p.lerp(q, (i + 1) / n) - Vector((0, 0, 1.2 * math.sin(math.pi * (i + 1) / n))), .04, dark)
for i, (y, x) in enumerate(((-6.5, -11), (-6.5, 11), (-1.5, -11), (-1.5, 11))):
    strand((-11, y, 4.2), (11, y, 4.2), 11)
for x in (-11, 11):
    strand((x, -6.5, 4.2), (x, -1.5, 4.2), 4)
glow((-6, -4, 3.5), (1, .7, .3), 500); glow((6, -4, 3.5), (1, .7, .3), 500)
# a fountain and a few bollards
cyl((0, -8, 0), 1.6, .8, 8, limestone); cyl((0, -8, .8), 1.3, .1, 8, win); cyl((0, -8, .8), .2, 1.2, 5, limestone)
for i in range(8):
    a = i * math.pi / 4; cyl((math.cos(a) * 1.5, -8 + math.sin(a) * 1.5, 0), .15, 1.0, 5, limestone2)
for c, w, p in (((.5, .6, 1), 4, (-26, -16, 9)), ((.9, .4, .7), 2.2, (24, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .012, .035, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 4)); co.location = tg + Vector((22, -62, 36))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
