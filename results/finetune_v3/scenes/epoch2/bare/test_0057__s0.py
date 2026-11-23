import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1542)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
salt = {}
def glaze(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .5
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    salt[name] = m
for k, v in dict(rock=(.3, .27, .26), rock2=(.2, .18, .18), floor=(.38, .34, .32), pale=(.8, .76, .7), wood=(.25, .14, .07),
                 wood2=(.18, .1, .05), relief=(.5, .45, .4), brass=(.45, .3, .1)).items(): glaze(k, v)
glaze("crystal", (.7, .85, 1), 6); glaze("lantern", (1, .6, .2), 16); glaze("candle", (1, .75, .3), 12)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(salt[m]); return o
def cube(at, d, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return add(bm, m, at, (0, 0, rz))
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = d.to_track_quat('Z', 'Y') @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, m)
def spike(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at)
def blob(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return add(bm, m, at)
def beam(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# salt floor slab
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=11, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.06, .06)
    v.co.z -= 1.7
add(bm, "floor")
# two salt walls of rough blocks with a gap at the front
for i in range(8):
    for j in range(3):
        h = 2.2 + random.uniform(-.2, .2)
        cube((-9.2 + i * 2.6, 8.4, j * 2.2), (2.5, 1.2, h), "rock" if (i + j) % 3 else "rock2", random.uniform(-.05, .05))
        cube((-9.2 + i * 2.6, -8.4, j * 2.2), (2.5, 1.2, h), "rock" if (i + j) % 3 else "rock2", random.uniform(-.05, .05))
for i in range(7):
    for j in range(3):
        h = 2.2 + random.uniform(-.2, .2)
        cube((9.4, -9.2 + i * 2.6, j * 2.2), (1.2, 2.5, h), "rock2" if (i + j) % 3 else "rock")
        cube((-9.4, -9.2 + i * 2.6, j * 2.2), (1.2, 2.5, h), "rock" if (i + j) % 3 else "rock2")
# salt stalactites and stalagmites
for i in range(9):
    x, y = random.uniform(-8, 8), random.uniform(-7, 7)
    blob((x, y, 0), random.uniform(.5, 1.1), "rock2", 1.3)
for i in range(6):
    spike((random.uniform(-7, 7), random.uniform(-6, 6), 6.6), .5, random.uniform(1.5, 3), 5, "rock2", .05).rotation_euler.z = math.pi
# altar: pale stone table, steps, candles, cross
cube((0, 5.4, 0), (6, 2.4, 1.2), "pale"); cube((0, 5.4, 1.2), (6.6, 3, .2), "pale")
for i in range(3): cube((0, 3.2 - i * .5, 0), (3.4 - i * .4, .6, .3 * (3 - i)), "pale")
for x in (-2.4, 2.4): spike((x, 5.4, 1.4), .22, .8, 6, "pale", .15); spike((x, 5.4, 2.2), .18, .35, 5, "candle", .1)
cube((0, 6.6, 1.4), (.35, .35, 3.2), "pale"); cube((0, 6.6, 3.4), (1.8, .35, .35), "pale")
beam((0, 4.2, 2.6), (1, .8, .5), 500)
# carved reliefs: raised panels on the side walls
for sx in (-1, 1):
    for k in range(4):
        y = -6 + k * 4
        cube((sx * 8.6, y, 1.6), (.2, 2.2, 2.6), "relief")
        spike((sx * 8.45, y, 2.4), .6, .15, 6, "pale", .1).rotation_euler.y = math.pi / 2
        cube((sx * 8.45, y, 3.2), (.1, 1.2, .15), "pale")
# wooden pews
for r in range(5):
    for sx in (-1, 1):
        x = sx * 2.3
        cube((x, -4.5 + r * 1.8, 0), (2.2, .5, .7), "wood"); cube((x, -4.5 + r * 1.8 + .3, .7), (2.2, .12, .9), "wood2")
        for ex in (-1, 1): cube((x + ex * 1.0, -4.5 + r * 1.8, 0), (.15, .5, .7), "wood2")
# crystal chandeliers: rings of spikes hung from rods
for cx, cy in ((-4.5, 0), (4.5, 0), (0, -3)):
    rod((cx, cy, 6.6), (cx, cy, 5.2), .1, "brass")
    for k in range(6):
        a = k * math.pi / 3
        px, py = cx + math.cos(a) * 1.1, cy + math.sin(a) * 1.1
        rod((cx, cy, 5.2), (px, py, 5.2), .08, "brass"); spike((px, py, 4.9), .25, .8, 5, "crystal", .02)
    beam((cx, cy, 4.4), (.7, .85, 1), 900)
# lantern-lit stair down into the cave
for i in range(9):
    cube((7, -2.5, -i * .35), (2.4, 1.0, .35), "pale" if i % 2 else "rock2")
for i in range(0, 9, 2):
    cube((5.7, -2.5, -i * .35), (.15, .15, 1.1), "wood2"); blob((5.7, -2.5, -i * .35 + 1.2), .3, "lantern", 1.2)
    beam((5.5, -2.5, -i * .35 + 1.3), (1, .6, .2), 220)
cube((7, -2.5, -3.6), (3.6, 3.6, .4), "rock2")
# cold salt light from above, warm key from the front right
for c, w, p in (((.6, .8, 1), 4.5, (-24, -18, 16)), ((1, .7, .45), 2.2, (22, 24, 12))):
    s = bpy.data.lights.new("s", "SUN"); s.color, s.energy = c, w
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("cave"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .025, .04, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
co.location = (28, -46, 38)
co.rotation_euler = (Vector((0, 0, 2)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
