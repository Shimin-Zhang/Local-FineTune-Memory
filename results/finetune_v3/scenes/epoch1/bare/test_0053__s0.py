import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1644)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def tone(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, v in dict(brick=(.3, .13, .1), brick2=(.22, .1, .09), plaster=(.55, .45, .3), floor=(.28, .18, .1), cheese=(.85, .65, .1),
                 red=(.55, .08, .06), blue=(.1, .25, .5), green=(.12, .35, .15), wood=(.3, .17, .08), thread=(.7, .65, .5),
                 crumb=(.7, .55, .3), wax=(.8, .75, .6), flame=(1, .6, .15), leaf=(.1, .3, .1)).items(): tone(k, v)
tone("candle", (1, .65, .2), 12); tone("cheese", (1, .75, .25), 1.5)
def put(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def cube(at, s, k, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * f, v.co.y * s[1] * f, (v.co.z + .5) * s[2]))
    return put(bm, k, at, (0, 0, rz))
def drum(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, k, at, rot)
def ball(at, r, k, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return put(bm, k, at)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# floor slab, rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 11 + random.uniform(-.8, .8), v.co.y * 11 + random.uniform(-.8, .8), -3.5 + random.uniform(-.6, .6)))
    else: v.co = Vector((v.co.x * 14, v.co.y * 14, -.6))
put(bm, "floor", (0, 0, .3))
# the two walls, built from brick courses with a few dark gaps
for side in (-1, 1):
    for i in range(7):
        for j in range(5):
            cube((side * 6.6, -5.2 + j * 2.3 + (i % 2) * 1.1, j * 1.15), (2.2, 2.15, 1.1), "brick" if (i + j) % 3 else "brick2")
    for i in range(5):
        for j in range(3):
            cube((-5.2 + i * 2.3 + (j % 2) * 1.1, 6.6, j * 1.15), (2.15, 2.2, 1.1), "brick" if (i + j) % 3 else "brick2")
cube((0, 6.6, 0), (14, 2.2, .4), "plaster"); cube((-6.6, 0, 0), (2.2, 14, .4), "plaster")
# the mouse house: a nest of twigs, sticks and straw at the corner
for i in range(26):
    a = random.uniform(0, math.tau); r = random.uniform(.5, 2.4)
    cube((-3.6 + math.cos(a) * r * .9, 3.6 + math.sin(a) * r * .9, random.uniform(.4, 2.2)), (random.uniform(.9, 1.6), .1, .1), "wood", a + 1.57)
cube((-3.6, 3.6, 0), (4.2, 4.2, .5), "wood"); cube((-3.6, 3.6, .5), (3.6, 3.6, .25), "plaster")
for i in range(14):
    a = i * .45
    cube((-3.6 + math.cos(a) * 2.2, 3.6 + math.sin(a) * 2.2, .75), (.15, .15, 2.0), "wood")
drum((-3.6, 3.6, .75), 3.0, 1.4, 8, "wood", 3.0).rotation_euler.z = .39
for i in range(10):
    a = i * .63; cube((-3.6 + math.cos(a) * 2.5, 3.6 + math.sin(a) * 2.5, 2.0), (2.4, .3, .3), "wood", a + 1.57, .98)
# the small arched door, glowing from within
cube((-3.6, 1.4, .75), (1.5, .3, 1.8), "candle")
for k in range(4): cube((-3.6, 1.4, 2.55 + k * .12), (1.5 - k * .35, .3, .12), "candle")
cube((-3.6, 1.4, .75), (.2, .4, 1.9), "wood")
cube((-4.5, 1.4, .75), (.3, .4, 2.0), "wood"); cube((-2.7, 1.4, .75), (.3, .4, 2.0), "wood")
glow((-3.6, .6, 1.3), (1, .65, .2), 260)
# cheese wheel table with a wedge cut
cube((1.2, 1.2, 0), (3.0, 2.2, .25), "wood")
for sx in (-1, 1):
    for sy in (-1, 1): cube((1.2 + sx * 1.3, 1.2 + sy * .9, 0), (.2, .2, .75), "wood")
drum((1.2, 1.2, .25), 1.0, .8, 10, "cheese"); drum((1.2, 1.2, 1.05), .95, .06, 10, "cheese")
for i in range(5): cube((1.2 + random.uniform(-.5, .5), 1.2 + random.uniform(-.5, .5), .85), (.18, .18, .06), "wood")
cube((2.4, .5, .25), (.5, .4, .5), "cheese", .5)
glow((1.2, 1.2, 1.3), (1, .75, .3), 120)
# matchbox beds: a bed of each colour with a pillow
for i, (x, y, c) in enumerate(((-.8, 3.2, "red"), (3.2, 3.4, "blue"), (-1.5, -.2, "green"))):
    cube((x, y, 0), (1.9, .9, .4), c, i * .2); cube((x + .6, y, .4), (.5, .6, .15), "plaster", i * .2)
# thread spools, big and stacked
for i, (x, y) in enumerate(((-5.4, -1.5), (-4.6, -2.2), (-5.4, -3.0), (5.2, -1.0), (4.4, -2.0))):
    drum((x, y, 0), .45, 1.1, 8, "wood"); drum((x, y, .25), .3, .6, 8, "thread")
    if i == 4: drum((x, y, 1.1), .3, .6, 8, "red"); drum((x, y, 1.1), .45, .1, 8, "wood")
# the candle on a little stand, big flame
drum((4.2, 1.2, 0), .35, .3, 6, "wood"); drum((4.2, 1.2, .3), .22, 1.2, 6, "wax"); drum((4.2, 1.2, 1.5), .2, .5, 5, "candle", .02)
glow((4.2, 1.2, 1.9), (1, .6, .2), 500)
# a trail of crumbs from the door to the cheese
for i in range(22):
    t = i / 21; x = -3.6 + t * 5.2 + math.sin(t * 9) * .5; y = .2 - t * .6 + math.cos(t * 7) * .4
    ball((x, y, .05), random.uniform(.1, .18), "crumb", (1, 1, .5))
# a few leaves and a twig on the floor
for i in range(8):
    x, y = random.uniform(-5, 5), random.uniform(-5, 2)
    cube((x, y, .02), (.8, .3, .05), "leaf", random.uniform(0, 3))
# moonlight from the left, violet rim from behind
for c, e, p in (((.5, .65, 1), 4.5, (-26, -14, 10)), ((.7, .35, .9), 2.2, (22, 24, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .015, .045, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.2)); co.location = t + Vector((10, -40, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
