import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1596)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
paints = {}
def pigment(name, rgb, glow=0, rough=.8, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    paints[name] = m
for k, v in dict(granite=(.2, .19, .22), granite2=(.14, .13, .16), steel=(.3, .32, .36), steel2=(.18, .2, .24), glass=(.15, .3, .4), cloud=(.6, .65, .8), cloud2=(.45, .5, .65),
                 red=(.7, .08, .06), amber=(.9, .5, .05), dark=(.04, .04, .06)).items(): pigment(k, v)
pigment("pane", (.3, .8, 1), glow=1.6, rough=.1); pigment("beacon", (1, .1, .08), glow=30); pigment("lamp", (1, .7, .3), glow=12)
def add(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(paints[m]); return o
def slab(c, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, c, rot)
def cyl(c, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, c, rot)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, m)
def puff(c, r, m, sq=.5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return add(bm, m, c)
def lamp(c, rgb, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = c; sc.collection.objects.link(o)
# cliff base: a tapering, ragged rock mass under the platform
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=4, radius2=9, depth=3)
for v in bm.verts:
    v.co.z -= 1.5; v.co.x *= 1.25
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
add(bm, "granite2")
# the cliff body on the left: stacked craggy slabs rising to a flat ledge at z=4.5
for i in range(6):
    slab((-6.2 + i * .3, 0, i * .7), (4.6 - i * .5, 5.4 - i * .3, .9), "granite" if i % 2 else "granite2", (0, random.uniform(-.06, .06), 0))
slab((-4.5, 0, 4.5), (5.2, 5.4, .35), "granite")
for i in range(5): slab((-7 + random.uniform(-.4, .4), random.uniform(-2, 2), random.uniform(.5, 4)), (1.4, 1.2, 1.2), "granite2", (0, 0, random.uniform(0, 3)))
# the walkway: glass panes on a steel frame, hung out to x=10.5
for i in range(11):
    x = -2 + i * 1.0
    for y in (-1.4, 1.4):
        slab((x, y, 3.85), (.16, .16, .6), "steel2"); slab((x, y, 4.2), (.12, .12, .08), "steel")
    slab((x + .5, 0, 4.2), (1.0, 2.8, .08), "pane")
    slab((x + .5, 0, 4.1), (1.0, .1, .1), "steel2")
for y in (-1.4, 1.4): slab((4.25, y, 4.15), (12.5, .14, .14), "steel2")
# railings: posts, top rail, mid rail, and a red beacon at the far end
for i in range(14):
    x = -1.5 + i * .95
    for y in (-1.55, 1.55):
        slab((x, y, 4.28), (.1, .1, 1.0), "steel")
        if y < 0: slab((x, y, 4.9), (.05, .05, .05), "red")
for y in (-1.55, 1.55):
    slab((4.25, y, 5.25), (13.5, .1, .1), "steel"); slab((4.25, y, 4.7), (13.5, .07, .07), "steel2")
slab((10.8, 0, 5.25), (.1, 3.2, .1), "steel")
cyl((10.8, 0, 5.35), .3, .5, 6, "red"); slab((10.8, 0, 5.9), (.4, .4, .15), "beacon")
lamp((10.8, 0, 6.2), (1, .1, .08), 900)
# ticket gate at the cliff edge: two posts, a swinging arm, and a ticket machine
for y in (-1.9, 1.9): slab((-2.0, y, 4.55), (.5, .5, 1.8), "steel2")
slab((-2.0, 0, 6.3), (.5, 4.3, .3), "steel2"); slab((-2.0, 0, 6.6), (.5, 4.3, .08), "red")
slab((-2.0, 0, 5.9), (.2, 3.6, .1), "amber"); slab((-2.0, 0, 5.2), (.1, .1, .1), "red")
slab((-3.6, -2.6, 4.55), (1.4, 1.0, 1.6), "red"); slab((-3.6, -3.15, 5.2), (.9, .06, .5), "pane")
cyl((-3.6, -3.15, 4.9), .12, .05, 8, "amber", rot=(math.pi / 2, 0, 0)); lamp((-3.6, -3.8, 5.4), (1, .7, .3), 160)
# a little viewing deck at the far end with a lamp post
slab((10.2, 0, 4.15), (1.6, 3.0, .08), "steel2"); slab((10.2, 0, 4.23), (1.2, 2.6, .04), "granite")
slab((9.9, 1.2, 4.25), (.1, .1, 2.4), "steel"); slab((9.9, 1.2, 6.6), (.4, .4, .3), "lamp"); lamp((9.9, 1.2, 6.7), (1, .7, .3), 260)
# sea of cloud below, a few wisps of mist around the walkway
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(3, 10)
    puff((math.cos(a) * r * 1.2, math.sin(a) * r * .8, random.uniform(-3.2, -2.0)), random.uniform(1.8, 3.2), "cloud" if i % 2 else "cloud2", .4)
for i in range(6): puff((random.uniform(-1, 9), random.choice((-1, 1)) * random.uniform(2.5, 4), random.uniform(-1.5, .5)), random.uniform(.8, 1.4), "cloud2", .3)
for i in range(3): puff((random.uniform(-7, -4), random.uniform(-2.5, 2.5), random.uniform(1, 3.5)), random.uniform(.5, .8), "cloud2", .4)
# cold dawn: pale gold key from the right, steel-blue rim behind
for col, w, p in (((1, .8, .5), 5.5, (26, -12, 10)), ((.35, .5, 1), 2.5, (-22, 20, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .05, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((1, 0, 1.5)); co.location = t + Vector((-10, -50, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
