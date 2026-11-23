import bpy, bmesh, random, math
from mathutils import Vector
random.seed(679)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dyed(rgb, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
turf, turf2, red, cream, wicker, wicker2, linen, apple, apple2, lemon, bread, leaf, bulb, trunk = (dyed(c) for c in (
    (.1, .22, .08), (.15, .28, .1), (.6, .08, .1), (.75, .68, .5), (.5, .32, .12), (.35, .2, .08), (.85, .8, .7), (.7, .1, .08), (.8, .6, .05), (.8, .6, .05), (.6, .4, .18), (.12, .3, .1), (.5, .9, .3), (.2, .12, .07)))
lamp = dyed((1, .85, .5), 14); berry = dyed((.5, .1, .4))
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(x, y, z, w, d, h, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return put(bm, m, (x, y, z), (0, 0, rz))
def tube(x, y, z, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, (x, y, z), rot)
def ball(x, y, z, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return put(bm, m, (x, y, z))
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# meadow slab
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=7, radius2=12.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.3, .2)))
    v.co.z -= 1.5
put(bm, turf)
for i in range(30):
    a, r = random.uniform(0, 6.28), random.uniform(2, 11)
    ball(math.cos(a) * r, math.sin(a) * r, .05, random.uniform(.3, .6), turf2, .4)
# checkered blanket, 10 x 8 squares of .9 m, with a ragged edge and a fold
for i in range(10):
    for j in range(8):
        cube(-4.5 + i * .9, -3.2 + j * .9, .02 + (i + j) * .002, .9, .9, .05, red if (i + j) % 2 else cream)
cube(-1, 0, .08, 9.6, 7.2, .03, linen, .03)
# wicker basket with weave rings, lid ajar, handle, and a cloth tail
bx, by = 1.5, 0
tube(bx, by, .1, 1.3, 1.5, 8, wicker, 1.1)
for k in range(3): tube(bx, by, .35 + k * .45, 1.22 - k * .06, .12, 8, wicker2)
tube(bx, by, 1.6, 1.2, .12, 8, wicker2)
cube(bx, by + .1, 1.7, 2.2, 2.2, .12, wicker, .3)
tube(bx - .2, by - .1, 1.75, .1, 1.4, 5, wicker2, rot=(0, math.pi / 2 - .2, 0)).location.z = 2.2
cube(bx + 1.4, by - 1.3, .1, 1.0, 1.4, .04, linen, .4)
# picnic goods: plate with sandwich, apples, lemon, loaf, a thermos, and a bottle
tube(-2.5, -.8, .1, .9, .1, 8, linen)
cube(-2.5, -.8, .2, .8, .6, .3, bread, .3); cube(-2.5, -.8, .5, .7, .5, .12, cream, .3)
for i, (dx, dy) in enumerate(((-3.6, 1.4), (-3.0, 1.9), (-3.8, 2.2))): ball(dx, dy, .3, .38, apple if i != 1 else apple2)
ball(-1.2, 1.8, .3, .35, lemon)
cube(-.2, 2.4, .1, 1.6, .6, .5, bread, .5)
tube(3.6, 1.8, .1, .3, 1.1, 7, linen); tube(3.6, 1.8, 1.2, .3, .15, 7, berry)
tube(3.6, -1.5, .1, .2, .9, 6, leaf); tube(3.6, -1.5, 1.0, .12, .3, 6, leaf)
# string lights between two posts, each bulb glowing
for px in (-8, 8): tube(px, -5.5, 0, .12, 3.6, 5, trunk)
for k in range(9):
    t = k / 8; x = -8 + t * 16
    cube(x, -5.5, 3.4 - math.sin(t * math.pi) * .8 - .2, .3, .3, .3, bulb)
    if k % 2 == 0: glow((x, -5.5, 3.0 - math.sin(t * math.pi) * .8), (1, .8, .45), 140)
# a tree with a broad crown, a bench, and a few flowers
tube(8, 4, 0, .5, 3, 6, trunk, .35)
for i in range(3): ball(8 + (i - 1) * .8, 4 + (i % 2) * .6, 4.2 + i * .2, 1.9 - i * .25, leaf, .8)
cube(-6, -7, 0, 3, .8, .5, wicker2); cube(-6, -7.5, .5, 3, .15, .7, wicker2)
for i in range(14):
    a, r = random.uniform(0, 6.28), random.uniform(9, 11.5)
    tube(math.cos(a) * r, math.sin(a) * r, 0, .05, .5, 4, leaf); ball(math.cos(a) * r, math.sin(a) * r, .55, .2, berry if i % 3 else apple)
# golden hour: warm low key, cool green rim
for c, w, at in (((1, .65, .35), 5.5, (-26, -12, 9)), ((.4, .6, 1), 2.2, (22, 16, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .03, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, -1, 1.2)); co.location = tg + Vector((8, -42, 26))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
