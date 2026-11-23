import bpy, bmesh, math, random
from mathutils import Vector
random.seed(843)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def glaze(rgb, em=0):
    m = bpy.data.materials.new("g"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
ocean, shore, grass, wood, wood2, white, black, fish, red, gold, gull, fire = (glaze(c) for c in (
    (.04, .22, .3), (.35, .3, .22), (.1, .3, .12), (.3, .2, .12), (.2, .13, .08), (.8, .8, .75), (.04, .04, .05), (.7, .72, .7), (.6, .1, .08), (.8, .55, .1), (.85, .85, .85), (1, .5, .08)))
def cast(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def block(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return cast(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0.0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return cast(bm, m, at, rot)
def gable(at, w, l, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); p = [bm.verts.new(c) for c in ((-w, -l, 0), (w, -l, 0), (w, l, 0), (-w, l, 0), (0, -l, h), (0, l, h))]
    for f in ((0, 1, 2, 3), (0, 1, 4), (2, 3, 5), (0, 3, 5, 4), (1, 2, 5, 4)): bm.faces.new([p[i] for i in f])
    return cast(bm, m, at, rot)
def gull(x, y, z, a):
    for s in (-1, 1): block((x, y, z), (1.6, .08, .08), gull, (0, 0, a + s * .6))
    cone((x, y, z - .1), .22, .4, 5, white, .05)
def spark(c, w, at):
    L = bpy.data.lights.new("s", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
# sea: a round slab with a rough dark keel
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=11, radius1=5, radius2=12.5, depth=3.5)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.75
cast(bm, ocean)
# the island: a fish-shaped sand bank with a tail and a head, grassy on top
pts = [(-9, 0), (-5.5, 1.2), (0, 1.6), (4, 1.1), (7, .4), (8.5, -.4), (7.5, -1.2), (8.5, -2.2), (6.5, -1.6), (3, -1.3), (-1, -1.7), (-5.5, -1.2)]
bm = bmesh.new(); top = [bm.verts.new((x, y, 0)) for x, y in pts]
low = [bm.verts.new((x * .9, y * .9, -1.6)) for x, y in pts]
bm.faces.new(top[::-1]); bm.faces.new(low)
for i in range(len(pts)): bm.faces.new((top[i], top[(i + 1) % len(pts)], low[(i + 1) % len(pts)], low[i]))
cast(bm, shore)
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
for v in bm.verts: v.co = Vector((v.co.x * 5.5, v.co.y * 1.5, v.co.z * .4))
cast(bm, grass, (0, 0, .1))
# the great hook: a pole of stacked tapered blocks curving over the water, with a barb
hx, hy = 1, 0
for k in range(9):
    a = k * .38
    x, y, z = hx + math.sin(a) * 4.2, hy, 1 + math.cos(a) * 4.2
    block((x, y, z), (1.0, 1.0, 1.2), wood2 if k % 2 else wood, (0, -a, 0))
for k in range(4):
    a = 3.14 + k * .3
    x, y, z = hx + math.sin(a) * 4.2, hy, 1 + math.cos(a) * 4.2
    block((x, y, z), (.9, .9, 1.1), wood2 if k % 2 else wood, (0, -a, 0))
block((hx - 4.0, hy, .5), (.9, .9, 1.6), wood2); cone((hx - 4.0, hy, .2), .5, 1.4, 6, wood, .2, (0, math.pi / 2, 0))
block((hx - 4.6, hy, .2), (.5, .5, 1.4), wood2, (0, math.pi / 2, 0)); block((hx - 4.6, hy, 1.6), (.5, .5, .5), wood2, (0, math.pi / 2, 0))
# canoe on the water with paddles and a sail pole
cone((3.0, -4.2, .25), .65, 4.6, 6, wood, .65, (0, math.pi / 2, .3)).scale.z = .6
block((3.0, -4.2, .5), (3.2, .5, .1), wood2, (0, 0, .3)); block((3.0, -4.2, .9), (.1, .1, 2.2), wood2)
# carved posts on shore: stacked blocks in alternating colours with a beak
for px, py in ((-3, 1.0), (-1, 1.1), (1, 1.1), (3, 1.0)):
    for k in range(4): block((px, py, .1 + k * .7), (.6, .6, .7), (white, red, black, gold)[k], (0, 0, k * .3))
    cone((px, py, 3.0), .45, .8, 5, gold, .05); block((px, py - .5, 3.2), (.3, .6, .12), black)
# a small hut and a fire with a glow
gable((-1.5, -.4, .2), 1.2, 1.0, 1.0, wood); block((-1.5, -.4, .2), (2.4, 2.0, .2), wood2)
for k in range(3): cone((5, -.6, .1), .35 - k * .1, 1.0 + k * .3, 5, red if k else fire, .02)
spark((1, .5, .1), 500, (5, -.6, 1.4))
for i in range(10): cone((random.uniform(-9, 8), random.uniform(-3.2, 3.4), .2), .25, random.uniform(.6, 1.4), 5, grass, .05)
for i in range(8): block((random.uniform(-9, 10), random.uniform(-8, 8), -.02), (random.uniform(.8, 1.6), .12, .12), white, (0, 0, random.uniform(0, 3)))
for i in range(6): gull(random.uniform(-2, 6), random.uniform(-3, 3), 8 + i * .6, i)
for c, w, p in (((.7, .85, 1), 4.5, (-24, -14, 11)), ((1, .6, .3), 2.2, (22, 20, 9))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dawn"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .03, .05, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 0, 2.5)); co.location = tg + Vector((12, -48, 30))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
