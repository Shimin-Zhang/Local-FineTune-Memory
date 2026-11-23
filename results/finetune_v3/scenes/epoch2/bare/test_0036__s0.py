import bpy, bmesh, math, random
from mathutils import Vector
random.seed(591)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def mat(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
frost, dirt, wall, tile, wood = mat((.4, .45, .52)), mat((.12, .1, .09)), mat((.45, .4, .33)), mat((.14, .12, .12)), mat((.22, .13, .07))
fruit, fruit2, bamboo, bark, leaf = mat((1, .35, .03), 1.5), mat((.85, .2, .02), 1.2), mat((.5, .42, .15)), mat((.14, .1, .08)), mat((.9, .4, .05))
win, frostcap = mat((1, .65, .25), 14), mat((.8, .85, .95))
def make(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(loc, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return make(bm, m, loc, (0, 0, rz))
def pole(loc, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, loc, rot)
def blob(loc, r, m, sq=(1, 1, 1), sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.88, 1.12)
    return make(bm, m, loc)
def cord(a, b, m, t=.03):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def lamp(kind, col, w, loc, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = loc; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# frosty yard: pale blue-grey ground, a trodden dirt patch
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13.5, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 2
make(bm, frost)
pole((0, -1.5, .02), 7.5, .06, 9, dirt, 7.0)
for i in range(18):
    a = random.uniform(0, 6.28); r = random.uniform(8, 12)
    blob((math.cos(a) * r, math.sin(a) * r * .9, .1), random.uniform(.5, 1.1), frostcap, (1.3, 1, .5))
# farmhouse: whitewashed wall, dark tiled roof, glowing window and door
box((0, 9, 0), (11, 6, 4.6), wall)
box((0, 9, 4.6), (12.6, 7.6, 1.8), tile, top=.6)
box((0, 9, 6.2), (12.8, 7.8, .25), frostcap, top=.55)
box((-3.2, 5.95, 1.6), (1.8, .1, 1.5), win); box((3.2, 5.95, 1.6), (1.8, .1, 1.5), win)
box((0, 5.95, 0), (1.4, .1, 2.5), wood)
box((0, 5.6, 0), (2.4, 1.4, .25), wood)
for x in (-3.2, 3.2):
    for k in (-.45, .45): box((x + k, 5.9, 1.6), (.08, .1, 1.5), wood)
    box((x, 5.9, 1.6), (1.8, .1, .08), wood)
box((0, 5.9, 2.9), (2.2, .1, .12), wood)
lamp("POINT", (1, .6, .2), 450, (0, 4.5, 2.2))
# drying eave: bamboo rafters, cords with strings of fruit
for i in range(5):
    x = -4.4 + i * 2.2
    pole((x, 4.6, 4.2), .09, 1.8, 5, bamboo)
for i in range(10):
    x = -4.4 + i * .95; y = 4.6
    cord((x, y, 4.2), (x, y, 3.4), bamboo, .02)
    for k in range(5):
        blob((x + .02 * math.sin(k), y, 3.3 - k * .32), .15, fruit if (i + k) % 2 else fruit2, (1, 1, 1.2))
# bare orange-laden trees: trunk, limbs, small glowing fruit
for tx, ty, s in ((-9, -1, 1.1), (9.5, 2, 1.0), (-6, 3.5, .8)):
    pole((tx, ty, 0), .45 * s, 3.2 * s, 6, bark, .25 * s)
    for k in range(5):
        a = k * 1.25 + tx
        tip = Vector((tx + math.cos(a) * 2.6 * s, ty + math.sin(a) * 2.6 * s, 3.2 * s + 1.4 * s))
        cord((tx, ty, 2.8 * s), tip, bark, .16 * s)
        for j in range(3):
            blob(tip + Vector((random.uniform(-.5, .5), random.uniform(-.5, .5), random.uniform(-.2, .3))), .22 * s, fruit if (k + j) % 2 else fruit2)
    for k in range(3): blob((tx + random.uniform(-1, 1), ty + random.uniform(-1, 1), 1.2 + k * .6), .18, fruit2)
# bamboo baskets heaped with fruit, a drying rack and a wooden cart
for bx, by in ((5.5, -3.5), (7.2, -2.2), (6.2, -1.2), (-3.5, -5.5)):
    pole((bx, by, 0), 1.0, 1.1, 8, bamboo, .75)
    for k in range(7): blob((bx + random.uniform(-.5, .5), by + random.uniform(-.5, .5), 1.0), .26, fruit if k % 2 else fruit2)
for i in range(4):
    pole((-8 + i * .8, -5.5, 0), .06, 1.8, 5, bamboo)
for z in (.7, 1.5): cord((-8, -5.5, z), (-5.6, -5.5, z), bamboo, .05)
for k in range(6): blob((-7.7 + k * .4, -5.5, 1.65), .22, fruit2)
box((-1, -7, .6), (3.4, 1.6, .25), wood)
for sx in (-1.2, 1.2):
    for sy in (-.8, .8): pole((-1 + sx, -7 + sy, 0), .08, .6, 5, wood)
    pole((-1 + sx, -7.85, .5), .5, .12, 8, wood, rot=(1.57, 0, 0))
for k in range(4): blob((-2 + k * .6, -7, .95), .3, fruit)
# lantern pole and a low stone wall at the front corner
pole((9, -6, 0), .12, 3.4, 5, wood); box((9, -6, 3.4), (.7, .7, .8), win)
lamp("POINT", (1, .6, .2), 500, (9, -6, 3.8))
for i in range(5): box((-9.5 + i * 1.2, -9, 0), (1.2, .6, .5 + (i % 2) * .1), wall, random.uniform(-.1, .1))
lamp("SUN", (1, .75, .55), 5.5, (-24, -14, 9), (0, 0, 2))
lamp("SUN", (.5, .6, 1), 2.4, (22, 20, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .025, .045, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((8, -66, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
