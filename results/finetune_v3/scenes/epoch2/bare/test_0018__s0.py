import bpy, bmesh, math, random
from mathutils import Vector
random.seed(346)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
sand, sand2, stone, stone2 = hue((.42, .3, .17)), hue((.34, .24, .14)), hue((.4, .36, .32)), hue((.28, .25, .23))
wood, leather, rope, water = hue((.28, .17, .09)), hue((.35, .18, .08)), hue((.55, .45, .25)), hue((.05, .2, .25), rough=.1)
camel, camel2, dark, thorn = hue((.55, .38, .2)), hue((.4, .27, .14)), hue((.015, .012, .012)), hue((.1, .14, .05))
bloom, flame, ember, cloth = hue((.6, .4, .08)), hue((1, .5, .1), 14), hue((1, .3, .05), 8), hue((.5, .12, .08))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mesh(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, at, rot)
def blob(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.88, 1.12)
    return mesh(bm, m, at)
def line(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mesh(bm, m)
def fire(at, w):
    L = bpy.data.lights.new("f", "POINT"); L.color, L.energy = (1, .5, .12), w
    o = bpy.data.objects.new("f", L); o.location = at; sc.collection.objects.link(o)
# sand dunes
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.15, .15) + .3 * math.sin(v.co.x * .6)
mesh(bm, sand, (0, 0, -1.5))
# stone-ringed well with rope and leather bucket
wx, wy = -4.5, 3.5
for i in range(10):
    a = i * math.pi * 2 / 10
    cube((wx + 2.0 * math.cos(a), wy + 2.0 * math.sin(a), 0), (1.2, 1.0, 1.2), stone if i % 2 else stone2, (0, 0, a + math.pi / 2), .95)
cone((wx, wy, .3), 1.6, .2, 10, water, 1.6)
for sx in (-1, 1): cone((wx + sx * 2.6, wy, 0), .2, 4.6, 5, wood, .16)
cube((wx, wy, 4.4), (5.8, .35, .35), wood); cone((wx, wy, 4.0), .22, .4, 6, wood, .22, (0, math.pi / 2, 0)).location.x = wx
line((wx, wy, 4.1), (wx, wy, 2.0), .08, rope); line((wx, wy, 2.0), (wx + .1, wy, 1.5), .12, rope)
cone((wx + .1, wy, .6), .45, .9, 7, leather, .38)
for k in range(3): cone((wx + .1, wy, .75 + k * .3), .42 - k * .02, .08, 7, rope, .42 - k * .02)
# long watering trough
tx, ty = 3.5, -1.5
cube((tx, ty, 0), (8.0, 1.4, .9), wood, (0, 0, .12), .96)
cube((tx, ty, .55), (7.4, .95, .5), water, (0, 0, .12))
for s in (-1, 1): cube((tx + s * 3.9, ty + s * .2, 0), (.4, 1.6, 1.0), stone2, (0, 0, .12))
# camels
def camel(x, y, a, m):
    c, s = math.cos(a), math.sin(a)
    def at(dx, dy, z, w, d, h, rot=0): return cube((x + dx * c - dy * s, y + dx * s + dy * c, z), (w, d, h), m, (0, 0, a + rot))
    at(0, 0, 1.2, 2.6, 1.0, 1.2, 0); at(.3, 0, 2.2, .8, .7, .5); at(-1.3, 0, 1.6, .5, .5, .8, .2); at(-1.7, 0, 2.1, .7, .45, .35)
    for lx in (-.9, .9):
        for ly in (-.3, .3): at(lx, ly, 0, .25, .25, 1.3)
    line((x + 1.3 * c, y + 1.3 * s, 2.2), (x + 1.3 * c + .5 * math.cos(a), y + 1.3 * s + .5 * math.sin(a), 2.5), .1, m)
camel(1.5, 5.0, .5, camel); camel(7.5, 4.5, 3.8, camel2); camel(-9, -3.5, 1.2, camel)
# black tent with glowing door and a fire
tx2, ty2 = 8.0, 7.0
cone((tx2, ty2, 0), 3.4, 3.0, 4, dark, .2, (0, 0, math.pi / 4))
cube((tx2 - 2.2, ty2 - 2.2, 0), (1.0, .1, 1.8), flame, (0, 0, math.pi / 4)); fire((tx2 - 3.0, ty2 - 3.0, 1.0), 400)
fx, fy = 2.0, 7.0
for i in range(6): cube((fx + 1.0 * math.cos(i * 1.05), fy + 1.0 * math.sin(i * 1.05), 0), (.5, .4, .4), stone2, (0, 0, i))
cone((fx, fy, 0), .8, .5, 6, ember, .1); fire((fx, fy, 1.0), 500)
cube((fx - 1.8, fy - 1.2, 0), (1.0, .6, .4), wood); cube((fx + 1.8, fy + 1.2, 0), (1.0, .6, .4), wood)
# thorny acacias
for ax, ay, h in ((-10, 7, 1.0), (-1, -8, .9), (10, -4, 1.1), (-8, -8, .8)):
    line((ax, ay, 0), (ax + .3, ay, h * 3.2), .3, wood)
    for k in range(3): line((ax + .3, ay, h * 3.2), (ax + .3 + 2.2 * math.cos(k * 2.1), ay + 2.2 * math.sin(k * 2.1), h * 3.6 + k * .2), .12, wood)
    for k in range(4): blob((ax + 1.6 * math.cos(k * 1.7), ay + 1.6 * math.sin(k * 1.7), h * 4.0), 1.7, thorn, (1.3, 1.3, .5))
for i in range(14):
    a, r = random.uniform(0, 6.28), random.uniform(3, 12)
    x, y = r * math.cos(a), r * math.sin(a)
    if (x - tx) ** 2 + (y - ty) ** 2 < 20 or (x - wx) ** 2 + (y - wy) ** 2 < 12 or (x - tx2) ** 2 + (y - ty2) ** 2 < 16 or (x - fx) ** 2 + (y - fy) ** 2 < 6: continue
    cone((x, y, 0), .08, random.uniform(.5, 1.0), 4, bloom, .02)
for col, w, p in (((1, .5, .22), 5.5, (-26, -10, 8)), ((.4, .45, .9), 2.2, (22, 22, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((10, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
