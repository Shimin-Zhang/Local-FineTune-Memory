import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1325)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .85
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
grass, dirt, stone, plank = dye((.08, .22, .1)), dye((.2, .13, .08)), dye((.3, .28, .3)), dye((.35, .2, .1))
shingle, shingle2, brick, glass = dye((.45, .1, .08)), dye((.3, .07, .06)), dye((.4, .15, .1)), dye((1, .72, .3), 10)
balloon = [dye(c) for c in ((.9, .1, .1), (.95, .6, .05), (.1, .5, .85), (.2, .7, .3), (.8, .3, .7), (.95, .35, .1), (.5, .3, .9))]
rope, trunk, leaf, lampglow = dye((.5, .4, .25)), dye((.2, .12, .07)), dye((.1, .3, .12)), dye((1, .8, .4), 12)
def spawn(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, d, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return spawn(bm, m, at, (0, 0, rz))
def cyl(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return spawn(bm, m, at)
def ball(at, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return spawn(bm, m, at)
def roof(at, w, d, h, m, ridge=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        if v.co.z > 0: v.co.x = 0
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return spawn(bm, m, at)
def sun(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: grassy hill with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
spawn(bm, grass)
# the house: raised on stilts, with porch, chimney, roof, windows, door
hx, hy, z0 = 0, 1, 7.0
for sx in (-1, 1):
    for sy in (-1, 1): cyl((hx + sx * 3.0, hy + sy * 2.2, 0), .25, z0, 5, stone)
for k in range(3):
    cube((hx, hy - 2.2, z0 * (k + .5) / 3.3), (6.2, .12, .12), plank)
cube((hx, hy, z0), (7.4, 5.4, 3.0), plank)
cube((hx, hy - 2.7, z0), (7.4, .5, .3), plank)
for k in range(5): cube((hx - 3.0 + k * 1.5, hy - 2.7, z0 + .3), (.12, .12, 2.7), plank)
roof((hx, hy, z0 + 3.0), 8.4, 6.4, 2.6, shingle)
roof((hx, hy, z0 + 3.0), 8.4, 6.4, 2.6, shingle2).scale.x = .98
cube((hx + 2.0, hy + 1.2, z0 + 3.0), (.9, .9, 4.2), brick)
cube((hx + 2.0, hy + 1.2, z0 + 7.1), (1.2, 1.2, .3), stone)
for wx in (-2.4, -.8, 2.4):
    cube((hx + wx, hy - 2.75, z0 + 1.0), (1.1, .1, 1.3), glass)
    cube((hx + wx, hy - 2.8, z0 + 2.3), (1.1, .1, .5), glass)
cube((hx, hy - 2.8, z0 + .3), (1.0, .12, 2.0), dye((.1, .25, .45)))
cube((hx, hy - 3.1, z0 + 2.4), (1.6, .8, .12), plank)
cube((hx - 3.8, hy - 1.0, z0 + 3.0), (.5, 3.0, .15), shingle)
sun("POINT", (1, .72, .3), 700, (hx, hy - 4.0, z0 + 1.5))
# the balloon cluster above the chimney: strings from the chimney top to each balloon
top = Vector((hx + 2.0, hy + 1.2, z0 + 7.3))
for i in range(110):
    a = random.uniform(0, 6.28); r = random.uniform(0, 5.5) * (1 - i / 160)
    bx, by, bz = hx + 2.0 + r * math.cos(a), hy + 1.2 + r * math.sin(a) * .8, top.z + 1.5 + random.uniform(0, 12) * (1 - r / 9) + r * .3
    if bz < top.z + 1.5: bz = top.z + 1.5
    ball((bx, by, bz), random.uniform(.8, 1.15), balloon[i % 7], 1.15)
    bm = bmesh.new(); p, q = bm.verts.new(top), bm.verts.new((bx, by, bz - 1.0)); bm.edges.new((p, q))
    spawn(bm, rope)
# the town below: little houses, trees, a pond, lamp posts, a winding path
for i, (x, y) in enumerate(((-8, -4), (-4.5, -7), (6, -6), (9, -2), (-9, 3), (7, 4), (-3, 6), (3, 7))):
    h = random.uniform(1.8, 2.6); m = random.choice((brick, plank, dye((.55, .4, .25))))
    cube((x, y, 0), (3.2, 2.6, h), m, random.uniform(-.2, .2)); roof((x, y, h), 3.8, 3.2, 1.5, random.choice((shingle, shingle2)))
    cube((x + 1.0, y - 1.32, h * .45), (.6, .06, .7), glass)
for x, y in ((-6, -1), (-1, -4.5), (4, -2.5), (8.5, 1), (-8.5, 7), (-2, 3.5), (2, 3.5), (10, 7)):
    cyl((x, y, 0), .2, 1.6, 5, trunk); ball((x, y, 2.3), 1.3, leaf, 1.1)
for x, y in ((-3, -2.5), (2.5, -4.5), (-6.5, -7), (5, 6)):
    cyl((x, y, 0), .06, 2.0, 5, trunk); ball((x, y, 2.1), .25, lampglow); sun("POINT", (1, .8, .4), 120, (x, y, 2.2))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=2.2, radius2=2.2, depth=.1)
spawn(bm, dye((.1, .3, .5)), (-1, -2, .03))
# dawn light: warm gold key from the left, cool blue rim from behind
sun("SUN", (1, .75, .45), 5.5, (-24, -10, 11), (0, 0, 4)); sun("SUN", (.4, .55, 1), 2.2, (22, 20, 10), (0, 0, 4))
w = bpy.data.worlds.new("dawn"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .025, .06, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 12)); co.location = t + Vector((10, -66, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
