import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1669)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def glaze(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .3
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, v in dict(violet=(.3, .08, .5), violet2=(.22, .06, .4), cloud=(.9, .85, 1), cloud2=(.6, .5, .9), wood=(.3, .17, .09),
                 dark=(.06, .04, .07), steam=(.8, .75, 1), moon=(.9, .8, .55), rim=(.5, .2, .8)).items(): glaze(k, v)
glaze("teal", (.1, .9, .8), 6)
def mk(bm, key, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(key); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(key, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[key]); return o
def disc(at, r, h, n, key, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, key, at, rot)
def puff(at, r, key, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mk(bm, key, at)
def bar(a, b, t, key):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, key)
def shine(at, col, w):
    L = bpy.data.lights.new("s", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
# floating island of wood
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=10, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
mk(bm, "wood")
disc((0, 0, 0), 9.2, .15, 10, "dark")
# the pot: squashed icosphere body, neck, lid with knob
body = bmesh.new(); bmesh.ops.create_icosphere(body, subdivisions=2, radius=4)
for v in body.verts: v.co.z *= .85; v.co.x *= 1.05
mk(body, "violet", (0, 0, 3.4))
disc((0, 0, 6.0), 1.5, 1.0, 8, "violet2", 1.2)
disc((0, 0, 7.0), 1.8, .5, 8, "violet", .5)
puff((0, 0, 8.0), .5, "teal", 1)
# spout: curved tube of stacked rings
prev = Vector((4.2, 0, 3.4))
for i in range(1, 8):
    t = i / 8; p = Vector((4.2 + t * 3.2, 0, 3.4 + math.sin(t * 1.8) * 2.4 + t * .6))
    bar(prev, p, .9 - t * .35, "violet"); prev = p
disc((7.6, 0, 6.0), .5, .15, 6, "teal", rot=(0, math.pi / 2, 0))
# handle
for i in range(1, 8):
    a = math.pi * i / 8; p = Vector((-4.2 - math.sin(a) * 2.2, 0, 3.4 + math.cos(a) * 2.2))
    if i > 1: bar(prev, p, .55, "violet2")
    prev = p
# clouds painted on the pot: puffs sitting on its surface, with moon
def on_pot(theta, phi, lift=.15):
    r = 4.05 * (1 + lift); return Vector((r * math.sin(phi) * math.cos(theta) * 1.05, -r * math.cos(phi) * math.sin(theta), 3.4 + r * math.cos(phi) * .85))
for theta, phi, s in ((.2, .6, 1.2), (1.5, .75, 1.0), (2.8, .55, 1.3), (4.2, .7, 1.0), (5.3, .6, 1.1), (3.5, 1.0, .8), (0.9, 1.0, .8)):
    p = on_pot(theta, phi); puff(p, .75 * s, "cloud", .6)
    puff(p + Vector((.5 * s, 0, .15)), .5 * s, "cloud2", .6)
p = on_pot(3.6, .25); puff(p, .55, "moon", 1)
shine((0, -6, 4), (.9, .6, 1), 300)
# steam rising from the spout, drifting
for i in range(6):
    puff((7.6 + math.sin(i * 1.3) * .5, 0, 6.6 + i * .9), .4 + i * .08, "steam", 1)
# teacups on the base, a small tray, a moonlit lantern
for i, (x, y) in enumerate(((-6, -3), (6, -4), (-2, -6.5))):
    disc((x, y, .15), .8, .6, 8, "cloud", 1.0); disc((x, y, .75), .6, .05, 8, "teal")
    bar((x + .8, y, .5), (x + 1.5, y, .5), .2, "cloud")
disc((-6, 3, .15), 2.2, .12, 8, "violet2")
disc((-6, 3, .27), 1.4, .5, 7, "cloud", 1.1); disc((-6, 3, .77), 1.0, .05, 7, "teal")
disc((7, 5, .15), .35, 1.6, 6, "dark"); disc((7, 5, 1.75), .6, .9, 6, "teal", .5)
shine((7, 5, 2.2), (.1, .9, .8), 250)
# moonlit night: cool key from the left, violet rim from behind
for col, w, at in (((.55, .65, 1), 4.5, (-24, -16, 12)), ((.8, .3, .9), 2.5, (20, 22, 10))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("sun", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .008, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
co.location = (13, -42, 27)
co.rotation_euler = (Vector((0, 0, 4.5)) - co.location).to_track_quat('-Z', 'Y').to_euler()
