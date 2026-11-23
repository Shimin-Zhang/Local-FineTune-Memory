import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1943)
sc = bpy.context.scene
for o in list(sc.objects):
    if o.name != "cam": sc.objects.unlink(o)
M = {}
def paint(name, rgb, em=0, rough=.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    M[name] = m
paint("grass", (.05, .09, .05)); paint("tarmac", (.12, .12, .14)); paint("tarmac2", (.07, .07, .09)); paint("hangar", (.3, .29, .27)); paint("hangarroof", (.12, .13, .16))
paint("plane", (.6, .62, .64), rough=.4); paint("stripe", (.1, .3, .25), rough=.4); paint("dark", (.02, .02, .03)); paint("furnace", (1, .35, .05), em=9)
paint("coat", (.35, .33, .3)); paint("hat", (.1, .08, .07)); paint("skin", (.5, .35, .28)); paint("car", (.06, .07, .12)); paint("tyre", (.02, .02, .02))
paint("lamp", (1, .85, .5), em=22); paint("fog", (.28, .36, .45), em=.2); paint("sign", (1, .6, .15), em=5); paint("brass", (.7, .5, .15), rough=.3)
def spawn(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(k); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(k, me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def box(x, y, z, w, d, h, k, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return spawn(bm, k, (x, y, z), (rx, 0, rz))
def cyl(x, y, z, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return spawn(bm, k, (x, y, z), rot)
def bar(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return spawn(bm, k)
def bulb(x, y, z, c, w):
    L = bpy.data.lights.new("b", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("b", L); o.location = (x, y, z); sc.collection.objects.link(o)
# base: grass slab with ragged underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=14.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .2)))
    v.co.z -= 1.5
spawn(bm, "grass", (0, 0, 0))
box(0, 0, 0, 22, 17, .15, "tarmac")
for i in range(6): box(-8 + i * 3.2, -1 + (i % 2) * .5, .15, 1.8, .12, .02, "tarmac2")
# hangar: open doors with glowing furnace, roof ridge, sign
hx, hy = 0, 8.5
box(hx, hy, .15, 13, 6, 4.2, "hangar"); box(hx, hy, 4.35, 13.6, 6.6, .3, "hangarroof")
for s in (-1, 1):
    for k in range(4): box(hx - 6.2 + k * 4.1, hy + (s * 3.2 - 1.5), 4.65, 4.1, 1.8, .15, "hangarroof", 0, -s * .45)
box(hx, hy - 3.0, .15, 8, .2, 3.4, "dark"); box(hx, hy - 3.4, .15, 7, 1.6, 2.6, "furnace")
for k in range(5): box(hx - 3.2 + k * 1.6, hy - 3.8, .15, .15, .15, 3.2, "hangar")
bulb(hx, hy - 4.5, 2.0, (1, .45, .1), 900)
box(hx + 3.5, hy - 3.1, 3.0, 3.2, .1, .8, "sign"); bulb(hx + 3.5, hy - 4, 3.2, (1, .6, .15), 120)
# the plane: fuselage, nose, cowling, prop, wings, tail, wheels, windows
px, py = 1.5, -1.5
cyl(px - 1.1, py, 1.9, .9, 6.2, 8, "plane", .75, rot=(0, math.pi / 2, 0))
cyl(px - 4.4, py, 1.9, 1.0, .5, 8, "dark", rot=(0, math.pi / 2, 0))
cyl(px - 4.6, py, 1.9, .12, .6, 5, "brass", rot=(0, math.pi / 2, 0))
bar((px - 4.8, py, 3.0), (px - 4.8, py, .8), .1, "dark")
box(px - .3, py, 2.4, 1.6, 11, .25, "plane"); box(px - .3, py, 2.65, 1.2, 10, .1, "stripe")
box(px + 3.3, py, 1.7, .3, 3.4, 2.4, "plane"); box(px + 3.3, py, 3.9, 1.2, 5.4, .2, "plane"); box(px + 3.3, py, 4.0, .9, 4.4, .12, "stripe")
for s in (-1, 1):
    cyl(px - 1.2, py + s * 1.5, .55, .55, .35, 8, "tyre", rot=(math.pi / 2, 0, 0)); bar((px - 1.2, py + s * 1.5, 1.1), (px - 1.2, py + s * 1.2, 1.9), .12, "dark")
for i in range(4): box(px - 1.5 + i * .8, py - .85, 2.1, .45, .06, .45, "lamp")
# the two: trench coats, hats, one holding a suitcase; enlarged so they read
def person(x, y, h, coat):
    cyl(x, y, .15, .45, 1.5, 6, coat, .3); cyl(x, y, 1.6, .22, .4, 6, "skin", .2); cyl(x, y, 2.0, .38, .12, 7, "hat"); cyl(x, y, 2.1, .22, .35, 7, "hat", .18)
    bar((x + .3, y, 1.1), (x + .8, y, .5), .1, coat)
person(-2.2, -5.0, 2, "coat"); person(-1.2, -5.2, 2, "dark")
box(-2.9, -5.0, .15, .5, .35, .5, "brass")
# the car: 1940s sedan, headlights on, parked at the edge
cx, cy = 8.5, -5.5
box(cx, cy, .6, 3.4, 1.5, .6, "car"); box(cx + .2, cy, 1.2, 1.8, 1.3, .6, "car"); box(cx + .2, cy, 1.8, 1.9, 1.4, .1, "dark")
for sx in (-1, 1):
    for sy in (-1, 1): cyl(cx + sx * 1.1, cy + sy * .8, .35, .38, .25, 8, "tyre", rot=(math.pi / 2, 0, 0))
    box(cx - 1.75, cy + sy * .45, .85, .15, .3, .25, "lamp")
bulb(cx - 2.2, cy, 1.0, (1, .85, .5), 250)
# fog: low drifting pale banks, lamp posts, crates, barrels
for i in range(7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(1.6, 2.6))
    for v in bm.verts: v.co.z *= .18
    spawn(bm, "fog", (random.uniform(-10, 10), random.uniform(-9, 5), random.uniform(.3, .9)))
for x in (-9, 9):
    bar((x, -8, .15), (x, -8, 4.2), .12, "dark"); box(x, -8, 4.2, .5, .5, .5, "lamp"); bulb(x, -8, 4.2, (1, .8, .45), 300)
for i in range(3): box(-9 + i * .9, 3, .15, .8, .8, .7, "brass", rz=i)
for c, w, p in (((.5, .65, 1), 4.5, (-24, -14, 9)), ((.7, .5, .9), 2.2, (22, 18, 12))):
    L = bpy.data.lights.new("sun", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("sun", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("night"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .03, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
t = Vector((0, 1, 2)); co.location = t + Vector((6, -56, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
