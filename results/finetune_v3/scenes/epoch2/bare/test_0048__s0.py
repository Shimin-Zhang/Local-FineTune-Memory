import bpy, bmesh, math, random
from mathutils import Vector
random.seed(860)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def surf(rgb, em=0, rough=.8, metal=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
cobble, cobble2, snow, iron, red = surf((.13, .13, .15)), surf((.09, .09, .11)), surf((.55, .6, .72)), surf((.04, .04, .05), metal=.5, rough=.5), surf((.4, .05, .05))
wood, coal, ember, paper, brown = surf((.25, .15, .08)), surf((.03, .03, .03)), surf((1, .3, .05), 16), surf((.8, .75, .65)), surf((.3, .18, .08))
lamp, glass, steam, flame = surf((1, .75, .35), 20), surf((1, .8, .45), 12), surf((.7, .75, .85), .2), surf((1, .6, .15), 25)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, rot)
def tube(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def ball(at, r, m, sq=1, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co.z *= sq
    return add(bm, m, at)
def lamp(kind, rgb, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color, d.energy = rgb, w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# cobbled square with snow drifts
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=11, depth=2.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    v.co.z -= 1.2
add(bm, cobble)
for i in range(16):
    a, r = random.uniform(0, 6.28), random.uniform(1, 9.5)
    slab((math.cos(a) * r, math.sin(a) * r, 0), (random.uniform(1.4, 2.4), random.uniform(1.2, 2), .08 + random.random() * .06), cobble2 if i % 2 else snow, (0, 0, a))
for i in range(10): ball((random.uniform(-9, 9), random.uniform(-9, 9), .1), random.uniform(.5, 1.1), snow, .35)
# the brazier on wheels
bx, by = 0, 0
slab((bx, by, .75), (3.4, 2.4, .35), iron)
for sx in (-1, 1):
    for sy in (-1, 1):
        tube((bx + sx * 1.6, by + sy * 1.1, .55), .55, .22, 8, wood, rot=(math.pi / 2, 0, 0)).location.y = by + sy * 1.25
        tube((bx + sx * 1.6, by + sy * 1.25, .55), .12, .3, 5, iron, rot=(math.pi / 2, 0, 0))
tube((bx, by, .9), 1.7, 1.5, 8, red, 1.45); tube((bx, by, 2.4), 1.55, .12, 8, iron)
for i in range(8):
    a = i * .8
    ball((bx + math.cos(a) * 1.0, by + math.sin(a) * 1.0, 1.15), .5, coal, .6)
    ball((bx + math.cos(a + .4) * .5, by + math.sin(a + .4) * .5, 1.1), .35, ember, .6)
tube((bx, by, 1.0), 1.2, .15, 8, ember)
lamp("POINT", (1, .4, .1), 700, (bx, by, 1.8))
# dome roaster with a turn spit and paper cones
tube((bx, by, 2.4), 1.3, .5, 8, iron, 1.3)
ball((bx, by, 2.9), 1.3, iron, .8, 2)
slab((bx, by - 1.2, 2.55), (1.2, .2, .5), flame)
tube((bx, by, 3.0), .1, .8, 5, iron, .06); ball((bx, by, 3.9), .22, iron, 1, 1)
for i in range(5):
    a = i * 1.26
    slab((bx + math.cos(a) * 1.0, by + math.sin(a) * 1.0, 2.4), (.12, .12, .5), iron, (0, 0, a))
for i in range(6):
    a = i * 1.05 + .3
    x, y = bx + math.cos(a) * 2.4, by + math.sin(a) * 2.4
    tube((x, y, .0), .02, 1.0, 4, wood)
    tube((x, y, 1.0), .35, .8, 6, paper, .06)
    ball((x, y, 1.0), .22, brown, 1, 1)
# the lamp post
lx, ly = 5.5, 2.5
tube((lx, ly, 0), .5, .3, 6, iron, .35); tube((lx, ly, .3), .18, 6.5, 6, iron, .13)
tube((lx, ly, 6.8), .55, 1.1, 6, glass, .45); tube((lx, ly, 7.9), .6, .3, 6, iron, .1)
slab((lx - .1, ly, 7.0), (.08, .08, .8), iron)
lamp("POINT", (1, .75, .35), 900, (lx, ly, 7.0))
# a snow-laden bench and a crate of coal
slab((-5, 3, .6), (3, .9, .15), wood); slab((-5, 3, 1.1), (3, .15, .8), wood)
for sx in (-1.3, 1.3): slab((-5 + sx, 3, 0), (.2, .8, .6), iron)
slab((-5, 3, .75), (2.9, .8, .08), snow)
slab((-5.5, -3.5, 0), (1.6, 1.2, .9), wood)
for i in range(5): ball((-5.5 + (i - 2) * .3, -3.5 + (i % 2) * .3, .95), .22, coal, .8, 1)
# steam wisps and a few flakes
for i in range(6):
    ball((bx + random.uniform(-.3, .3), by + random.uniform(-.3, .3), 4.4 + i * .5), .22 + i * .04, steam, .8, 1)
for i in range(24):
    ball((random.uniform(-9, 9), random.uniform(-9, 9), random.uniform(1, 8)), .07, snow, 1, 1)
lamp("SUN", (.5, .65, 1), 4, (-18, -10, 8), (0, 0, 1)); lamp("SUN", (.8, .4, .5), 2, (14, 16, 9), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.8)); co.location = t + Vector((9, -41, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
