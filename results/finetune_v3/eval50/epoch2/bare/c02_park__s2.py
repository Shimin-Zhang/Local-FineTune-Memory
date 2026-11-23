import bpy, bmesh, random, math
from mathutils import Vector
random.seed(535)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
grass, path, trunk, leaf1, leaf2, leaf3 = tone((.07, .2, .08)), tone((.45, .38, .26)), tone((.25, .15, .09)), tone((.05, .25, .1)), tone((.1, .3, .08)), tone((.2, .3, .06))
water, rock, plank, iron, lampc, flower = tone((.05, .2, .3)), tone((.3, .3, .32)), tone((.4, .22, .1)), tone((.06, .06, .08)), tone((1, .75, .3), 14), tone((.8, .2, .3))
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, m, at, rot)
def stem(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at, rot)
def puff(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.85, 1.15), v.co.y * random.uniform(.85, 1.15), v.co.z * sq))
    return put(bm, m, at)
def bulb(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color, L.energy = c, w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=11, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, .2)))
put(bm, grass)
# winding path of pale slabs from the front edge to the bench
for i in range(11):
    t = i / 10; x = -6 + 9 * t + 1.2 * math.sin(t * 5); y = -9 + 10 * t
    blk((x, y, 0), (1.7, 1.3, .08), path, (0, 0, .3 * math.cos(t * 5)))
# pond with a stone rim, a lily pad and a little jet
stem((6, 2, 0), 3.6, .15, 9, water)
for i in range(11):
    a = i * 6.2832 / 11; blk((6 + 3.7 * math.cos(a), 2 + 3.7 * math.sin(a), 0), (1.1, .8, .35), rock, (0, 0, a))
for x, y, r in ((5, 1, .4), (7.2, 3, .5), (6, 3.4, .35)): stem((x, y, .15), r, .03, 7, leaf3)
stem((6, 2, .1), .12, 1.2, 5, rock, .06); stem((6, 2, 1.3), .22, .12, 6, water, .05)
# three trees: trunk, roots, three stacked crowns each
for x, y, s, c in ((-6, 4, 1.2, leaf1), (-1, 7.5, 1.0, leaf2), (1, -5, .9, leaf3)):
    stem((x, y, 0), .45 * s, 2.6 * s, 6, trunk, .25 * s)
    for k in range(3): puff((x + random.uniform(-.3, .3), y + random.uniform(-.3, .3), 3.0 * s + k * 1.0 * s), (2.0 - k * .45) * s, c, .85)
# bench facing the pond, a lamp post, flowers, rocks
blk((1.5, 0, .55), (2.4, .7, .12), plank); blk((1.5, .45, .6), (2.4, .12, .6), plank)
for sx in (-1, 1): blk((1.5 + sx * 1.0, 0, 0), (.12, .6, .55), iron); blk((1.5 + sx * 1.0, .45, .3), (.12, .1, .5), iron)
stem((-3, -1, 0), .1, 3.2, 5, iron); blk((-3, -1, 3.2), (.55, .55, .6), lampc); blk((-3, -1, 3.9), (.7, .7, .12), iron)
bulb("POINT", (1, .75, .3), 450, (-3, -1, 3.5))
for i in range(16):
    x, y = random.uniform(-9, 4), random.uniform(-8, 8)
    if math.hypot(x - 6, y - 2) < 4.5 or math.hypot(x - 1.5, y) < 2: continue
    stem((x, y, 0), .04, .4, 4, leaf2); stem((x, y, .4), .12, .15, 5, flower if i % 3 else tone((.9, .8, .2)), .02)
for i in range(6): puff((random.uniform(-9, 3), random.uniform(2, 9), .1), random.uniform(.4, .7), rock, .6)
# blue hour: cool key from the right, warm rim from behind left
bulb("SUN", (.45, .6, 1), 4.5, (24, -14, 8), (0, 0, 1)); bulb("SUN", (1, .5, .35), 2.2, (-20, 20, 9), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
co.location = Vector((0, 0, 1)) + Vector((-6, -48, 30))
co.rotation_euler = (Vector((0, 0, 1)) - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
