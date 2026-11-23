import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1164)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
col = {}
def paint(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    col[name] = m
for k, v in dict(lawn=(.1, .2, .08), lake=(.05, .16, .22), thatch=(.45, .32, .12), wood=(.25, .15, .08), plank=(.4, .28, .16), stone=(.3, .3, .3),
                 swan=(.8, .8, .78), beak=(.7, .3, .05), leaf=(.1, .25, .08), leaf2=(.2, .3, .08), trunk=(.15, .1, .07), sign=(.55, .4, .2), rope=(.5, .4, .25)).items(): paint(k, v)
paint("window", (1, .65, .25), 10); paint("lantern", (1, .7, .3), 14)
def make(bm, key, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(col[key]); return o
def cube(at, size, key, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], (v.co.z + .5) * size[2]))
    return make(bm, key, at, rot)
def rod(a, b, r, key, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return make(bm, key, a, d.to_track_quat('Z', 'Y').to_euler())
def ball(at, r, key, squash=1, jit=0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= 1 + random.uniform(-jit, jit); v.co.z *= squash
    return make(bm, key, at)
def roof(at, w, d, h, key, ridge=0.0):
    bm = bmesh.new()
    p = [bm.verts.new(c) for c in ((-w/2, -d/2, 0), (w/2, -d/2, 0), (w/2, d/2, 0), (-w/2, d/2, 0), (-w/2 + ridge, 0, h), (w/2 + ridge, 0, h))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): bm.faces.new([p[i] for i in f])
    return make(bm, key, at)
def lamp(at, rgb, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.05, .05)
    v.co.z -= 1.5
make(bm, "lawn")
# lake in the middle, with a stone rim, and a small island
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=9.2, radius2=9.2, depth=.2)
for v in bm.verts: v.co.x *= 1.15; v.co.y *= .85; v.co += Vector((random.uniform(-.4, .4), random.uniform(-.4, .4), 0))
make(bm, "lake", (0, 0, .05))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=4.2, radius2=3.6, depth=.9)
for v in bm.verts: v.co += Vector((random.uniform(-.25, .25), random.uniform(-.25, .25), random.uniform(-.05, .1)))
make(bm, "lawn", (0, 0, .3))
# swan house on stilts: platform, four corner posts, door, windows, thatch
for sx in (-1, 1):
    for sy in (-1, 1): rod((-1.5 + sx * 1.7, 1.5 + sy * 1.5, .6), (-1.5 + sx * 1.7, 1.5 + sy * 1.5, 2.6), .14, "wood", 5)
cube((-1.5, 1.5, 2.6), (4.2, 3.8, .25), "plank")
cube((-1.5, 1.5, 2.85), (3.6, 3.2, 2.0), "wood")
roof((-1.5, 1.5, 4.85), 4.6, 4.0, 1.8, "thatch", 0.0)
cube((-1.5, -.1, 2.85), (.9, .1, 1.4), "trunk")
for wx in (-2.7, -.3): cube((wx, -.1, 3.4), (.7, .1, .7), "window")
cube((-1.5, -.15, 3.0), (3.8, .1, .12), "trunk")
lamp((-1.5, -1.2, 3.6), (1, .65, .25), 380)
# ladder up to the platform and a walkway to the jetty
for i in range(7):
    z = .7 + i * .32
    cube((.7, -.1, z), (.5, .12, .1), "wood")
rod((.4, -.1, .6), (.4, -.1, 2.7), .06, "wood"); rod((1.0, -.1, .6), (1.0, -.1, 2.7), .06, "wood")
# feeding jetty: planks on piles, with a lantern post and a swan
for i in range(11): cube((.6, -1.4 - i * .62, .25), (1.5, .55, .1), "plank")
for i in range(6):
    for sx in (-.7, .7): rod((.6 + sx, -1.5 - i * 1.2, -.1), (.6 + sx, -1.5 - i * 1.2, .3), .08, "wood", 5)
rod((.6, -7.6, .3), (.6, -7.6, 2.6), .08, "wood"); cube((.6, -7.6, 2.6), (.4, .4, .45), "lantern"); lamp((.6, -7.6, 2.9), (1, .7, .3), 220)
# swan nest on the island and two swans on the water
ball((2.4, 1.6, .8), 1.0, "rope", .5, .12); ball((2.4, 1.6, 1.1), .55, "swan", .6)
for sx, sy, ang in ((-3.5, -3.0, .5), (4.2, -2.5, 2.6)):
    ball((sx, sy, .2), .8, "swan", .6, .05)
    rod((sx + .5 * math.cos(ang), sy + .5 * math.sin(ang), .5), (sx + .5 * math.cos(ang), sy + .5 * math.sin(ang), 1.7), .13, "swan", 5)
    ball((sx + .5 * math.cos(ang), sy + .5 * math.sin(ang), 1.8), .22, "swan", 1, 0); cube((sx + .75 * math.cos(ang), sy + .75 * math.sin(ang), 1.75), (.3, .1, .1), "beak")
# signboard on the shore: two posts, a board and arrow
for sx in (-1, 1): rod((6.5 + sx * 1.0, -7.5, 0), (6.5 + sx * 1.0, -7.5, 2.2), .1, "wood", 5)
cube((6.5, -7.5, 1.4), (2.8, .12, 1.2), "sign"); cube((6.5, -7.6, 1.9), (2.0, .06, .15), "trunk"); cube((6.5, -7.6, 1.55), (1.4, .06, .15), "trunk")
# shore trees and bushes
for tx, ty, s in ((-9.5, 5.5, 1.2), (-8.5, -6.5, 1.0), (9.5, 6.5, 1.1), (9.5, -5.5, 1.0), (-4.5, 9.5, 1.1)):
    rod((tx, ty, 0), (tx, ty, 2.2 * s), .3 * s, "trunk", 6)
    for j in range(3): ball((tx, ty, 2.6 * s + j * 1.0 * s), 1.8 * s - j * .4 * s, "leaf" if j % 2 else "leaf2", .85, .12)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(10.2, 12.5)
    ball((r * math.cos(a) * 1.05, r * math.sin(a) * .8, .2), random.uniform(.4, .8), "leaf2", .7, .15)
# golden-hour light: low warm key from the right, teal rim from behind-left
for c, w, p in (((1, .65, .35), 5.5, (24, -10, 9)), ((.35, .6, .75), 2.2, (-20, 18, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .03, .04, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
aim = Vector((0, -1, 2)); co.location = aim + Vector((-6, -52, 30))
co.rotation_euler = (aim - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
