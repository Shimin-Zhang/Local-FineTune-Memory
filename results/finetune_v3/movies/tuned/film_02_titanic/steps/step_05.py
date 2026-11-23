import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1916)
sc = bpy.context.scene
for o in list(sc.objects): bpy.data.objects.remove(o, do_unlink=True)
M = {}
def paint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .8
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, c in dict(sea=(.04, .1, .14), foam=(.6, .6, .6), hull=(.13, .07, .06), deck=(.3, .22, .15), brass=(.6, .45, .12),
                 white=(.62, .6, .57), dark=(.04, .04, .05), red=(.65, .1, .07), coat=(.5, .38, .22), skin=(.7, .5, .4),
                 dress=(.55, .1, .12), hat=(.2, .17, .14), rope=(.45, .35, .2), smoke=(.16, .13, .13)).items(): paint(k, c)
paint("window", (1, .65, .25), 14); paint("sun", (1, .5, .15), 3)
def add(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def box(at, d, k, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return add(bm, k, at, (rx, 0, rz))
def cyl(at, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, k, at)
def beam(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, k)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
def person(x, y, z, k, hatk, spread):
    cyl((x, y, z), .45, 1.5, 6, k, .3)
    for s in (-1, 1):
        if spread: beam((x, y, z + 1.4), (x + s * 1.5, y - .2, z + 1.9), .17, k)
        else: beam((x, y, z + 1.4), (x + s * .25, y - .1, z + .6), .15, k)
    cyl((x, y, z + 1.5), .32, .55, 6, "skin", .28)
    if hatk: cyl((x, y, z + 2.0), .4, .2, 6, hatk)
# sea slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=15, depth=3.2)
for v in bm.verts:
    v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .2)))
add(bm, "sea")
# the ship: tapered bow hull, decks, bulwarks, funnels, bridge, stern
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 28, v.co.y * 5.6, (v.co.z + .5) * 3.6))
    if v.co.y > 0 and v.co.z < 1: v.co.y *= max(.06, 1 - v.co.y / 3.2)
add(bm, "hull", (0, 0, -.4))
box((0, 0, 3.2), (28, 5.6, .25), "deck")
for sy in (-1, 1):
    box((0, sy * 2.7, 3.45), (27, .2, .9), "white"); box((0, sy * 2.7, 3.45), (27, .2, .12), "brass")
    for i in range(14): beam((-12.5 + i * 1.9, sy * 2.7, 3.45), (-12.5 + i * 1.9, sy * 2.7, 4.35), .08, "brass")
    for i in range(13):
        box((-11 + i * 1.8, sy * 2.82, 3.9), (.7, .06, .35), "window" if i % 3 else "dark")
for i, x in enumerate((-9, -3, 3, 9)):
    cyl((x, 0, 3.45), .9, 3.2, 8, "red", .75); cyl((x, 0, 6.4), .78, .5, 8, "dark", .6)
box((0, 0, 6.7), (26, 4.4, .2), "deck")
box((0, 0, 6.9), (24, 3.8, .6), "white")
for i in range(18):
    box((-11 + i * 1.25, -1.92, 7.0), (.5, .06, .3), "window" if i % 2 else "dark")
box((0, 0, 7.5), (24, 3.8, .25), "deck"); box((0, 0, 7.75), (6, 3.4, 1.4), "white"); box((0, -1.72, 8.2), (5, .06, .5), "window")
box((0, 0, 9.15), (6.6, 3.8, .2), "deck")
for sy in (-1, 1): beam((0, sy * 1.7, 9.3), (0, sy * 1.7, 11.5), .12, "brass")
# bow: anchor, hawse pipes, figurehead, flag
beam((13.5, 0, 3.0), (13.5, 0, 1.2), .15, "dark"); cyl((13.5, 0, 1.1), .5, .12, 6, "dark").rotation_euler = (0, math.pi / 2, 0)
for sy in (-1, 1): cyl((12.6, sy * 2.3, 3.45), .25, .12, 6, "dark").rotation_euler = (math.pi / 2, 0, 0)
box((14.0, 0, 3.45), (.5, .5, 1.0), "brass", rx=.3); box((14.3, 0, 4.3), (.2, .2, .6), "brass", rx=.5)
beam((13.9, 0, 9.0), (13.9, 0, 12.5), .1, "dark"); box((13.5, 0, 11.6), (1.2, .05, .8), "red")
# the two of them at the bow, arms spread
person(13.2, -1.2, 3.45, "coat", None, True); person(13.2, 1.2, 3.45, "dress", "hat", True)
beam((13.2, -1.2, 4.6), (13.2, 1.2, 4.6), .12, "skin")
glow((13.2, 0, 5.0), (1, .6, .25), 300)
# lifeboats on davits, mast, smoke
for i in range(4):
    for sy in (-1, 1):
        x = -10 + i * 6.5
        beam((x, sy * 2.7, 7.7), (x, sy * 3.5, 7.0), .1, "dark"); beam((x + 1.5, sy * 2.7, 7.7), (x + 1.5, sy * 3.5, 7.0), .1, "dark")
        box((x + .75, sy * 3.2, 6.6), (1.9, .9, .4), "rope")
beam((-12, 0, 9.3), (-12, 0, 13), .14, "dark"); beam((-12, 0, 12.2), (-9.5, 0, 11.2), .08, "rope")
for i in range(3):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.8 + i * .25)
    add(bm, "smoke", (9 + i * .9, 0, 7.4 + i * 1.1))
# foam at the bow and waves
for i in range(10):
    a = random.uniform(0, 6.28); r = random.uniform(1, 3)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.3, .7))
    for v in bm.verts: v.co.z *= .3
    add(bm, "foam", (15 + r * math.cos(a) * .6, r * math.sin(a) * .8, .05))
for i in range(12):
    x, y = random.uniform(-14, 14), random.choice((-1, 1)) * random.uniform(6, 12)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.4, .8))
    for v in bm.verts: v.co.z *= .2
    add(bm, "foam", (x, y, .02))
# sunset: amber key from the right, rose rim from behind-left, warm bounce from the sea
for c, w, at in (((1, .55, .25), 5.5, (30, -14, 9)), ((.9, .35, .5), 2.4, (-26, 24, 12)), ((1, .45, .3), 1.2, (0, -30, 3))):
    s = bpy.data.lights.new("sun", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("sun", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 4)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("sunset"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.035, .015, .02, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
co.location = (24, -62, 36)
co.rotation_euler = (Vector((0, 0, 4.5)) - co.location).to_track_quat('-Z', 'Y').to_euler()
