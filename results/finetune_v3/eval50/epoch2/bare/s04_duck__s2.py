import bpy, bmesh, math, random
from mathutils import Vector
random.seed(842)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def toy(c, g=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .5
    if g: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = g
    return m
yellow, beak, cheek, eye, pond, rock, reed, pink, lampc, white = (toy((.95, .72, .05)), toy((.9, .3, .05)), toy((.9, .4, .35)), toy((.02, .02, .02)),
    toy((.04, .22, .3)), toy((.25, .26, .27)), toy((.12, .3, .1)), toy((.9, .35, .5)), toy((1, .75, .3), 9), toy((.7, .7, .7)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def ball(at, r, m, s=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    return mk(bm, m, at)
def cone(at, r, h, n, m, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def lit(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# round toy-room floor: a pond of glossy blue with a rock rim
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=10, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1, .2)))
    v.co.z -= 1.5
mk(bm, pond)
for i in range(10):
    a = i * math.tau / 10 + random.uniform(-.2, .2); r = random.uniform(8.6, 9.4)
    ball((math.cos(a) * r, math.sin(a) * r, .2), random.uniform(.7, 1.1), rock, (1, 1, .6))
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(6.5, 8.5)
    cone((math.cos(a) * r, math.sin(a) * r, 0), .1, random.uniform(1.2, 2.2), 4, reed, .02, (random.uniform(-.1, .1), random.uniform(-.1, .1), 0))
# the duck, enlarged, floating: body, tail, head, beak, cheeks, eyes
duck = Vector((0, 0, 0))
ball(duck + Vector((0, 0, 1.6)), 2.2, yellow, (1.2, 1, .9))
ball(duck + Vector((-.5, 0, 3.1)), 1.35, yellow, (1, 1, 1))
cone(duck + Vector((-2.3, 0, 1.8)), .5, 1.0, 5, yellow, .15, (0, -1.1, 0))
ball(duck + Vector((1.35, 0, 2.8)), .55, beak, (1, 1.1, .5))
ball(duck + Vector((1.1, .85, 2.7)), .22, cheek, (1, .4, .5)); ball(duck + Vector((1.1, -.85, 2.7)), .22, cheek, (1, .4, .5))
for s in (-1, 1):
    ball(duck + Vector((.9, s * .62, 3.35)), .17, eye, (1, 1, 1)); ball(duck + Vector((.95, s * .62, 3.4)), .06, white, (1, 1, 1))
# a little pink toy boat with a lantern, and a ring buoy
ball(Vector((5.5, -3, .3)), .9, pink, (1.3, 1, .45)); cone(Vector((5.5, -3, .5)), .12, 1.2, 5, white, .1)
ball(Vector((5.5, -3, 1.9)), .3, lampc, (1, 1, 1)); lit("POINT", (1, .7, .3), 450, (5.5, -3, 2.1))
cone(Vector((-5.5, 3.5, .1)), .9, .4, 8, beak, .9); cone(Vector((-5.5, 3.5, .2)), .5, .4, 8, white, .5)
# string lights: two poles and a sagging row of bulbs
for sx in (-1, 1): cone(Vector((sx * 7, 6, 0)), .12, 4.2, 5, rock, .1)
for i in range(9):
    t = i / 8; ball(Vector((-6.4 + t * 12.8, 6, 4.1 - math.sin(t * math.pi) * .9)), .22, lampc if i % 2 else pink, (1, 1, 1))
lit("POINT", (1, .7, .3), 500, (0, 6, 3.4))
# toy blocks and balls on the rim
for i, (x, y, m) in enumerate(((-3, -7.5, beak), (-1.8, -7.8, white), (3.5, -7.2, reed))):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.1)
    for v in bm.verts: v.co.z += .55
    mk(bm, m, (x, y, .1), (0, 0, i * .5))
for i, m in enumerate((pink, yellow, beak)): ball(Vector((6.5 + i * .2, 5 + i * .5, .5)), .6, m)
# moonlit toy room: cool moon key from the left, magenta rim behind
lit("SUN", (.6, .75, 1), 5, (-18, -10, 9), (0, 0, 1.5)); lit("SUN", (.9, .3, .6), 2, (14, 16, 8), (0, 0, 1.5))
w = bpy.data.worlds.new("room"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .045, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((6, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
