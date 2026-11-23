import bpy, bmesh, math, random
from mathutils import Vector
random.seed(573)
sc = bpy.context.scene
def coat(rgb, glow=0, rough=.9, metal=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
def put(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, x, y, z, w, d, h, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return put(bm, m, (x, y, z), (0, 0, rz))
def strut(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return put(bm, m)
def disc(m, x, y, z, r, h, n=8, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, (x, y, z))
def egg(m, x, y, z, a, b, c):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    for v in bm.verts: v.co = Vector((v.co.x * a, v.co.y * b, v.co.z * c))
    return put(bm, m, (x, y, z))
def shine(kind, c, e, loc, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = loc; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
tar, road, glass, steel = coat((.05, .05, .06)), coat((.08, .08, .09)), coat((.04, .06, .1)), coat((.12, .13, .15))
fur, fur2, window, red = coat((.16, .13, .11)), coat((.1, .08, .07)), coat((1, .75, .3), 6), coat((.4, .06, .05))
beacon, wood, canvas, lamp = coat((1, .05, .03), 30), coat((.35, .22, .1)), coat((.7, .65, .5)), coat((1, .85, .5), 12)
def tower(x, y, w, d, h, m, top=None):
    slab(m, x, y, 0, w, d, h)
    for k in range(int(h / 3)):
        for s in (-1, 1):
            for j in range(int(w / 2.5)): slab(window if random.random() < .45 else glass, x - w / 2 + 1.2 + j * 2.5, y + s * (d / 2 + .02), 2 + k * 3, 1.1, .06, 1.2)
            for j in range(int(d / 2.5)): slab(window if random.random() < .45 else glass, x + s * (w / 2 + .02), y - d / 2 + 1.2 + j * 2.5, 2 + k * 3, .06, 1.1, 1.2)
    if top: top(x, y, h)
def block(x, y, w, d, h):
    def top(x, y, h):
        slab(steel, x, y, h, w * .6, d * .6, 1.2)
        for k in range(int(h / 2.5)):
            for j in range(int(w / 2.2)): slab(window if random.random() < .3 else glass, x - w / 2 + 1 + j * 2.2, y + d / 2 + .02, 1.5 + k * 2.5, .9, .05, 1)
    tower(x, y, w, d, h, random.choice((glass, tar)), top)
# base: a city block of tar with streets cut through it
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=8, radius2=20, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 2
put(bm, tar)
for k in range(-2, 3): slab(road, k * 7, 0, 0, 1.6, 26, .05); slab(road, 0, k * 7, 0, 26, 1.6, .05)
for k in range(-2, 3):
    for j in range(-2, 3):
        x, y = k * 7, j * 7
        if abs(x) < 3 and abs(y) < 3: continue
        if abs(x) < 10.5 and abs(y) < 10.5: block(x, y, 5, 5, random.uniform(3, 8))
# Empire State Building: three stacked tiers with setbacks, a mast and a red beacon
def ems(x, y, h):
    slab(steel, x, y, h, 5.6, 5.6, 1.5); slab(steel, x, y, h + 1.5, 4, 4, 2.2); slab(steel, x, y, h + 3.7, 2.2, 2.2, 1.8)
    disc(steel, x, y, h + 5.5, 1.2, 3.5, 8, .3); disc(beacon, x, y, h + 9, .45, .7, 6)
tower(0, 0, 8, 8, 11, glass, None); tower(0, 0, 6.4, 6.4, 9, glass, None); tower(0, 0, 4.8, 4.8, 8, glass, ems)
for s in (-1, 1):
    for t in (-1, 1): slab(window, s * 2.4, t * 2.4, 28, .9, .06, 1.2); slab(window, s * 2.4, t * 2.4, 31, .9, .06, 1.2)
shine("POINT", (1, .1, .05), 1200, (0, 0, 38))
# Kong seated on the roof, legs hanging over the edge, arms raised
kz = 28
egg(fur, 0, 0, kz + 2.2, 2.2, 1.8, 2.2); egg(fur2, 0, -.3, kz + 4.2, 1.3, 1.1, 1.1)
for s in (-1, 1):
    egg(fur2, s * .5, -.8, kz + 4.6, .28, .2, .28)
    strut(fur, (s * 1.8, 0, kz + 3.4), (s * 3.6, 0, kz + 6.8), .9); strut(fur, (s * 3.6, 0, kz + 6.8), (s * 3.9, 0, kz + 9.2), .75)
    egg(fur2, s * 3.9, 0, kz + 9.5, .6, .55, .55)
    strut(fur, (s * 1.2, -.5, kz + .5), (s * 1.2, -2.8, kz - 1.2), 1.1); slab(fur2, s * 1.2, -3.3, kz - 1.9, 1.0, 1.6, .6)
    slab(fur2, s * .5, -1.4, kz + 4.7, .3, .1, .3)
# five biplanes circling above, nose to nose, each with a pilot and a searchlight
def biplane(x, y, z, yaw):
    q = Vector((math.cos(yaw), math.sin(yaw), 0)); n = Vector((-math.sin(yaw), math.cos(yaw), 0)); c = Vector((x, y, z))
    egg(canvas, x, y, z, 2.0, .6, .55); egg(canvas, x + q.x * 2.2, y + q.y * 2.2, z, .5, .4, .4)
    for dz in (-.6, .6):
        for s in (-1, 1):
            p = c + n * s * 2.2 + Vector((0, 0, dz)); slab(wood, p.x, p.y, p.z, .12, 5, .12).rotation_euler = (0, 0, yaw)
    for s in (-1, 1): strut(wood, c + n * s * 2.2 + Vector((0, 0, .6)), c + n * s * 2.2 + Vector((0, 0, -.6)), .1)
    slab(wood, c.x, c.y, c.z - .7, .12, 3.6, .12).rotation_euler = (0, 0, yaw)
    slab(red, c.x - q.x * 1.5, c.y - q.y * 1.5, c.z + .1, .9, .12, .12).rotation_euler = (0, 0, yaw)
    shine("POINT", (1, .8, .4), 60, (c + q * 3 + Vector((0, 0, -.5))).x, (c + q * 3 + Vector((0, 0, -.5))).y, (c + q * 3 + Vector((0, 0, -.5))).z)
for i in range(5):
    a = i * math.pi * 2 / 5 + .3; biplane(math.cos(a) * 13, math.sin(a) * 13, 36 + (i % 2) * 1.5, a + math.pi / 2)
# street furniture: lamp posts, fire hydrants, a parked car and a newsstand on the avenues
for x, y in ((-3.5, -10.5), (3.5, 10.5), (-10.5, 3.5), (10.5, -3.5), (-3.5, 10.5), (3.5, -10.5)):
    strut(steel, (x, y, 0), (x, y, 3.2), .12); disc(lamp, x, y, 3.2, .35, .4, 6)
slab(red, 5.5, -9.5, 0, .5, .5, .9); slab(steel, -9.5, -5.5, 0, 2.2, 1.1, .8); slab(glass, -9.5, -5.5, .8, 1.8, .9, .5)
shine("POINT", (1, .85, .5), 120, (-3.5, -10.5, 3.6))
# night: sodium streetlight key, moon-blue rim, deep blue-black sky
shine("SUN", (1, .65, .35), 4, (-26, -20, 12), (0, 0, 10)); shine("SUN", (.3, .45, 1), 2.4, (24, 22, 18), (0, 0, 10))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 15)); co.location = t + Vector((14, -78, 42))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
