import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1186)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def cold(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    return m
silt, silt2, gravel, basalt = cold((.2, .16, .14)), cold((.27, .21, .17)), cold((.3, .27, .24)), cold((.1, .1, .12))
snow, steam, wool, wool2 = cold((.7, .72, .78)), cold((.6, .65, .72)), cold((.5, .46, .38)), cold((.3, .27, .22))
pool, hot, wood, tin = cold((.1, .3, .35), 1.5, .3), cold((.1, .5, .5), 4, .3), cold((.25, .15, .09)), cold((.25, .3, .33))
lamp, glass, rock, sign = cold((1, .65, .25), 14), cold((1, .7, .3), 6), cold((.17, .15, .15)), cold((.5, .5, .45))
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, x, y, z, w, d, h, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return put(bm, m, (x, y, z), rot)
def column(m, x, y, z, r, h, n=7, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, (x, y, z))
def heap(m, x, y, z, r, sq=.5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return put(bm, m, (x, y, z))
def lit(kind, rgb, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: a cold desert of cracked silt
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=11, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.15, .15)
    v.co.z -= 2
put(bm, silt)
for i in range(10):
    slab(silt2, random.uniform(-9, 9), random.uniform(-9, 9), 0, random.uniform(2, 4), random.uniform(2, 3), .1, (0, 0, random.uniform(0, 3)))
for i in range(8): heap(snow, random.uniform(-10, 10), random.uniform(-9, 9), 0, random.uniform(.8, 1.4), .12)
# hot pool with a ring of standing stones
column(hot, 0, 0, 0, 3.0, .15, 10); column(pool, 0, 0, .1, 2.7, .05, 10)
for i in range(9):
    a = i * math.tau / 9 + .2
    heap(basalt, math.cos(a) * 4.0, math.sin(a) * 4.0, 0, random.uniform(.8, 1.1), 1.3)
lit("POINT", (.2, .9, .85), 500, (0, 0, 1.5))
# steaming vents with stone collars
for x, y in ((-8, 4), (7, 6), (9, -2), (-5, -8), (3, -9)):
    for k in range(5):
        a = k * math.tau / 5
        heap(basalt, x + math.cos(a) * .9, y + math.sin(a) * .9, 0, .4, .8)
    column(silt2, x, y, 0, .5, .3, 6)
    for k in range(3):
        heap(steam, x + k * .35, y + k * .2, 1.0 + k * 1.2, .6 + k * .35, .75)
# tourist hut with a tin roof, door, window and a sign
slab(wood, -8, -3, 0, 4.6, 3.6, 2.2); slab(tin, -8, -3, 2.2, 5.2, 4.2, .3, (0, .12, 0), .9)
slab(lamp, -6.0, -3, 0, .15, 1.1, 1.8); slab(lamp, -9.0, -4.85, 1.0, 1.0, .1, .8)
slab(sign, -8, -5.0, 2.8, 2.2, .1, .8); slab(basalt, -8, -5.1, 2.8, .1, .1, .5)
lit("POINT", (1, .65, .25), 350, (-6.5, -3.5, 1.2))
# shivering llama: big body, long neck, ears, legs and a fluffy tail
lx, ly = 4.5, -5.5
slab(wool, lx, ly, 1.5, 2.0, 1.0, 1.2, (0, 0, .5), .95)
slab(wool, lx + .9, ly - .35, 2.0, .6, .55, 1.6, (0, -.3, .5))
slab(wool2, lx + 1.4, ly - .7, 3.3, .7, .5, .5, (0, 0, .5))
for s in (-1, 1):
    slab(wool2, lx + 1.3 + s * .25, ly - .6, 3.8, .15, .15, .5, (s * .3, 0, 0))
    for fx in (-.7, .7):
        slab(wool2, lx + fx * math.cos(.5), ly + fx * math.sin(.5), 0, .22, .22, 1.5, (0, 0, .5))
slab(wool, lx - 1.0, ly + .5, 1.6, .5, .5, .7, (0, 0, .5))
for k in range(5): heap(steam, lx + random.uniform(-.8, .8), ly + random.uniform(-.6, .6), 2.8 + k * .4, .2, .8)
# boulders and dry scrub
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(8.5, 12)
    heap(rock, math.cos(a) * r, math.sin(a) * r, 0, random.uniform(.5, 1.1), .7)
for i in range(10):
    a = random.uniform(0, 6.28); r = random.uniform(5.5, 9)
    x, y = math.cos(a) * r, math.sin(a) * r
    if abs(x + 8) < 4 and abs(y + 3) < 3: continue
    column(gravel, x, y, 0, .12, .5, 5); heap(gravel, x, y, .6, .35, .6)
# cold blue dusk with a pale rim
lit("SUN", (.55, .7, 1), 4.5, (-24, -14, 10), (0, 0, 1)); lit("SUN", (.7, .55, .9), 2, (20, 22, 10), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((8, -56, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
