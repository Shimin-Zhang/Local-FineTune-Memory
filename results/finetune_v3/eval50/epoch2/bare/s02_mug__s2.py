import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1310)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def glaze(rgb, glow=0):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .3
    if glow: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    return m
red, white, wood, cream, leaf, saucer = glaze((.6, .05, .04)), glaze((.75, .75, .72)), glaze((.28, .17, .09)), glaze((.55, .45, .3)), glaze((.1, .3, .1)), glaze((.6, .6, .58))
steam, leaf2 = glaze((.9, .9, .9), 1.2), glaze((.2, .4, .12))
def part(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return part(bm, m, at, rot)
def can(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return part(bm, m, at, rot)
def puff(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return part(bm, m, at)
def shine(kind, at, col, w, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = col; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=10, depth=2.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .2)))
    else: v.co.z = 0
part(bm, wood, (0, 0, -1.2))
for i in range(8):
    a = i * math.pi / 4 + .2
    slab((math.cos(a) * 8.4, math.sin(a) * 8.4, 0), (1.8, .5, .12), cream, (0, 0, a))
# the mug: red body, white handle, cream rim, sitting on a saucer
can((0, 0, 0), 2.6, .35, 10, saucer); can((0, 0, .35), 2.1, 4.2, 10, red, 1.8)
can((0, 0, 4.5), 1.8, .15, 10, cream, 1.8)
can((0, 0, 4.55), 1.6, .1, 10, leaf, 1.6)
for k in range(3): can((0, 0, .6 + k * 1.5), 2.05 - k * .1, .18, 10, white)
for k in range(10):
    a = k * math.pi / 5
    slab((math.cos(a) * 1.9, math.sin(a) * 1.9, 3.9), (.5, .1, .35), white, (0, 0, a + math.pi / 2))
for i in range(11):
    a = -math.pi / 2 + i * math.pi / 10
    x, y, z = 2.55 + math.cos(a) * 1.15, 0, 1.4 + math.sin(a) * 1.15
    slab((x, y, z), (.5, .5, .5), white, (0, a + math.pi / 2, 0)).scale.y = 1
# steam rising from the mug
for k in range(5): puff((.2 * k - .3, .1 * k, 5.4 + k * .9), .45 + k * .08, steam, (1, 1, .8))
# a leafy sprig and a few loose leaves on the table
for k in range(4): puff((4.6 + k * .35, -1.0, .15 + k * .02), .45, leaf2, (1.4, .6, .3)); slab((4.6 + k * .35, -1.0, .1), (.1, .1, .3), leaf)
for k in range(5): puff((random.uniform(-5, 5), random.uniform(-4, 3), .1), .3, leaf2, (1.5, 1, .4))
# a small stack of sugar cubes and a spoon on the saucer
for i in range(3): slab((3.0, 1.5, i * .35), (.5, .5, .35), white, (0, 0, i * .4))
slab((-3.0, -2.0, 0), (.2, 1.4, .1), white, (0, 0, .5)); puff((-3.3, -2.3, .15), .3, white, (1, 1, .5))
# a little shelf of books at the back
for i, (c, h) in enumerate(((.5, .1, .1), (.1, .3, .3), (.6, .4, .12), (.15, .15, .45))):
    slab((-5.5 + i * .9, 4.5, 0), (.8, 1.4, 3.0 + h * 2), c)
slab((-2.4, 4.5, 0), (3.6, 1.6, .3), wood)
slab((-2.4, 4.5, .3), (3.4, 1.4, .35), red); slab((-2.4, 4.5, .65), (3.0, 1.2, .3), cream)
shine("POINT", (-2.4, 4.0, 1.6), (1, .6, .2), 150)
# a hanging lamp over the table
slab((0, 0, 8.6), (.1, .1, 1.6), white); can((0, 0, 7.0), .3, 1.6, 6, leaf, 1.4)
shine("POINT", (0, 0, 6.8), (1, .75, .4), 900)
shine("SUN", (-14, -10, 6), (1, .6, .3), 4, (0, 0, 2)); shine("SUN", (12, 14, 8), (.3, .5, .9), 2, (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .012, .012, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.0)); co.location = t + Vector((6, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
