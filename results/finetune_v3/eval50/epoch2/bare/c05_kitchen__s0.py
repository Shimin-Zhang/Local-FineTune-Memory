import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1387)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def tone(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .8
    if glow:
        n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    mats[name] = m
for k, c in (("tileA", (.28, .26, .22)), ("tileB", (.2, .19, .17)), ("wall", (.32, .3, .3)), ("cabinet", (.12, .2, .2)), ("cabinet2", (.2, .12, .1)),
             ("counter", (.5, .48, .44)), ("steel", (.35, .37, .4)), ("black", (.04, .04, .05)), ("fridge", (.5, .52, .55)), ("wood", (.3, .17, .08)), ("copper", (.7, .35, .15))):
    tone(k, c)
tone("flame", (1, .45, .08), 14); tone("bulb", (1, .75, .4), 12); tone("lamp", (1, .6, .25), 10)
def add(bm, m, loc=(0, 0, 0), rz=0):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = loc; o.rotation_euler.z = rz
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def slab(m, x, y, z, w, d, h, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return add(bm, m, (x, y, z), rz)
def tube(m, x, y, z, r, h, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, (x, y, z))
def ball(m, x, y, z, r, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return add(bm, m, (x, y, z))
def glow(kind, c, w, loc, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = loc; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab with a rough underside, checkered tiles
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 14, v.co.y * 12, v.co.z * 2.4 - 1.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .7 + random.uniform(-.8, .8), v.co.y * .7 + random.uniform(-.8, .8), v.co.z - random.uniform(0, 1.2)))
add(bm, "tileB")
for i in range(7):
    for j in range(6):
        if (i + j) % 2: slab("tileA", -6 + i * 2, -5 + j * 2, 0, 2, 2, .06)
# two walls: back and left, with a window on the back wall
slab("wall", 0, 5.6, 0, 14, .8, 7); slab("wall", -6.6, 0, 0, .8, 12, 7)
slab("black", 3.2, 5.15, 2.2, 3.2, .1, 2.4); slab("steel", 3.2, 5.1, 2.2, 3.4, .2, .15); slab("steel", 3.2, 5.1, 4.6, 3.4, .2, .15)
slab("steel", 3.2, 5.1, 3.4, .12, .12, 2.4); slab("steel", 3.2, 5.1, 3.4, 3.2, .12, .12)
# counter along the back wall: cabinets, top, sink, stove, upper cabinets
slab("cabinet", -2.4, 4.2, 0, 9, 2.2, 2); slab("counter", -2.4, 4.2, 2, 9.4, 2.4, .25)
for i in range(5):
    slab("cabinet2", -6.2 + i * 1.8, 3.08, .3, 1.6, .1, 1.4)
    slab("steel", -6.2 + i * 1.8, 3.0, 1.0, .5, .06, .1)
slab("cabinet", -3.2, 4.6, 4.2, 7.2, 1.6, 1.8); slab("cabinet2", -3.2, 3.78, 4.5, 6.8, .1, 1.2)
slab("steel", -4.6, 4.2, 2.25, 2.2, 1.4, .12); slab("black", -4.6, 4.2, 2.3, 1.8, 1.0, .1)
tube("steel", -4.6, 4.9, 2.25, .1, 1.1, 6); slab("steel", -4.6, 4.5, 3.3, .8, .12, .12)
for i in range(4):
    slab("black", -1.2 + (i % 2) * 1.0, 4.2 + (i // 2) * .9 - .45, 2.25, .9, .8, .08)
    ball("flame", -1.2 + (i % 2) * 1.0, 4.2 + (i // 2) * .9 - .45, 2.55, .26, .5)
glow("POINT", (1, .5, .12), 450, (-.7, 4.2, 3.4))
slab("steel", -.7, 4.9, 2.25, 2.2, .2, .2); slab("black", -.7, 4.9, 2.45, 2.0, .1, .5)
# fridge on the left wall: tall, with a freezer drawer and handles
slab("fridge", -5.4, -1.2, 0, 2.4, 2.4, 6.4, top=.97); slab("black", -5.4, -1.2, 2.6, 2.5, 2.5, .12)
slab("steel", -4.15, -.4, 4.2, .1, .15, 1.6); slab("steel", -4.15, -.4, 1.4, .1, .15, 1.2)
slab("black", -5.4, -2.45, 5.8, 1.2, .1, .5)
# island with two stools, pendant lamps, and a bowl of fruit
slab("cabinet", 1.2, -1.0, 0, 6, 2.4, 2); slab("counter", 1.2, -1.0, 2, 6.4, 2.8, .25)
for sx in (-.8, 3.2):
    for sy in (-.2, -.8): slab("black", 1.2 + sx, -1.0 + sy, 0, .2, .2, 2.0)
for i, x in enumerate((.2, 2.2)):
    tube("wood", x, -1.0, 0, .45, 1.3, 6, .3); tube("copper", x, -1.0, 1.3, .55, .22, 6)
    for a in range(3): tube("black", x + math.cos(a * 2.1) * .3, -1.0 + math.sin(a * 2.1) * .3, 0, .05, 1.2, 4)
for x in (.2, 2.2):
    slab("black", x, -1.0, 5.4, .05, .05, 1.6); ball("bulb", x, -1.0, 5.2, .35, 1)
glow("POINT", (1, .7, .35), 350, (.2, -1.0, 4.8)); glow("POINT", (1, .7, .35), 350, (2.2, -1.0, 4.8))
tube("copper", 3.6, -1.0, 2.25, .5, .3, 7, .7)
for i, c in enumerate(("lamp", "flame", "copper")): ball(c, 3.4 + i * .2, -1.0 + (i % 2) * .2, 2.7, .22, .8)
# a shelf of jars and a hanging rack
slab("wood", -5.9, 2.5, 4.2, .8, 3.6, .15)
for i in range(5): tube(("copper", "steel", "lamp")[i % 3], -5.9, 1.2 + i * .6, 4.35, .2, .5, 6)
# window light and a cool rim from the right
glow("SUN", (1, .7, .45), 5, (14, -14, 7), (0, 0, 2)); glow("SUN", (.4, .55, 1), 2.2, (-10, 12, 8), (0, 0, 2))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .02, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((-.5, 0, 2.8)); co.location = t + Vector((24, -33, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
