import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1216)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
T = {}
def paint(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .6
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    T[name] = m
def make(bm, name, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(T[name]); return o
def slab(at, s, name, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, name, at, (rx, 0, rz))
def tube(at, r, h, n, name, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, name, at)
def shine(kind, rgb, w, at, aim=None):
    d = bpy.data.lights.new(kind, kind); d.color = rgb; d.energy = w
    o = bpy.data.objects.new(kind, d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
for k, c, g in [("asphalt", (.07, .07, .09), 0), ("paving", (.2, .2, .22), 0), ("pole", (.12, .13, .15), 0), ("box", (.04, .045, .05), 0),
                ("red", (1, .06, .05), 22), ("amber", (1, .6, .05), 2), ("green", (.1, 1, .2), 2), ("white", (.8, .8, .85), 1),
                ("car", (.5, .08, .1), 0), ("glass", (.05, .1, .2), 0), ("tyre", (.02, .02, .02), 0)]:
    paint(k, c, g)
# base: asphalt road block, rough underneath
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 14 + random.uniform(-1, 1), v.co.y * 11 + random.uniform(-1, 1), -3.4 + random.uniform(-.8, .4)))
    else: v.co = Vector((v.co.x * 20, v.co.y * 15, -1.2))
make(bm, "asphalt")
# paving island at the front corner where the light stands
slab((0, -6.2, -1.2), (4.4, 3.2, 1.2), "paving")
for i in range(3): slab((-.8 + i * 1.6, -6.2, 0), (.9, 2.6, .04), "white", 0)
# lane dashes and a stop line on the road
for i in range(6): slab((-8 + i * 3.2, 0, -1.2), (1.6, .25, .05), "white")
slab((0, -3.8, -1.2), (10, .3, .05), "white")
# the traffic light: pole, base plate, backlit housing, visors, three lenses
tube((0, -6.2, 0), .5, .35, 6, "pole", .38); tube((0, -6.2, .35), .22, 5.2, 6, "pole", .18)
slab((0, -6.2, 5.5), (1.7, 2.4, 5.2), "box")
for z, c in [(10.0, "red"), (8.3, "amber"), (6.6, "green")]:
    tube((0, -7.45, z - .75), .72, .12, 8, c).rotation_euler = (math.pi / 2, 0, 0)
    tube((0, -7.6, z - .95), .62, .5, 8, "pole").rotation_euler = (math.pi / 2, 0, 0)
    slab((0, -7.5, z + .7), (1.5, .8, .12), "pole", 0, .35)
# a pedestrian signal on a short pole beside it, glowing white
tube((2.2, -5.4, 0), .1, 2.6, 5, "pole"); slab((2.2, -5.4, 2.6), (.8, .4, .8), "box"); tube((2.2, -5.2, 3.0), .22, .08, 6, "white").rotation_euler = (math.pi / 2, 0, 0)
# a small car waiting at the stop line, and a street lamp
for dx in (-2.6, 2.6):
    for sy in (-1, 1): tube((-6 + dx, sy * 1.0, -1.2), .55, .35, 8, "tyre").rotation_euler = (math.pi / 2, 0, 0)
slab((-6, -1.6, -.8), (5.6, 2.2, .9), "car"); slab((-6, -1.5, .1), (3.0, 1.9, .8), "glass")
for sy in (-1, 1): slab((-6, sy * 1.15, -.5), (.2, .2, .25), "amber")
tube((7.5, 3.5, -1.2), .15, 6.5, 5, "pole"); slab((7.5, 3.5, 5.3), (2.0, .2, .15), "pole"); slab((7.5, 3.5, 5.1), (1.2, .5, .2), "amber")
shine("POINT", (1, .1, .08), 900, (0, -8.2, 10)); shine("POINT", (1, .6, .1), 200, (0, -8.2, 8.3)); shine("POINT", (1, .6, .1), 300, (7.5, 3.5, 4.8))
# rainy blue night: cold key from the left, magenta rim from behind
shine("SUN", (.5, .65, 1), 4, (-26, -14, 12), (0, 0, 2)); shine("SUN", (.9, .35, .8), 2.2, (22, 22, 10), (0, 0, 2))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, -1, 3.5)); co.location = t + Vector((14, -52, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
