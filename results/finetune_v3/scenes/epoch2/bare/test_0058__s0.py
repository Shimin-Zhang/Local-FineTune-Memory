import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1125)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
ink = {}
def tone(k, c, e=0, r=.9):
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    if e: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    ink[k] = m
for k, c in (("basalt", (.1, .11, .13)), ("basalt2", (.17, .18, .2)), ("sea", (.03, .13, .18)), ("foam", (.75, .85, .9)), ("cliff", (.2, .2, .22)),
             ("pebble", (.3, .28, .26)), ("wall", (.32, .3, .27)), ("thatch", (.35, .26, .13)), ("door", (.1, .07, .05)), ("rope", (.5, .4, .25)), ("coat", (.6, .15, .1))): tone(k, c)
tone("sea", (.03, .13, .18), r=.2); tone("window", (1, .65, .25), 14); tone("lantern", (1, .7, .3), 20)
def put(bm, k, p, rz=0):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = p; o.rotation_euler.z = rz
    sc.collection.objects.link(o); o.data.materials.append(ink[k]); return o
def column(p, r1, r2, h, n, k, jit=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts:
        v.co.z += h / 2
        if jit: v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit)))
    return put(bm, k, p)
def block(p, s, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, k, p, rz)
def ball(p, r, k, sq=1, n=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=n, radius=r)
    for v in bm.verts: v.co.z *= sq
    return put(bm, k, p)
def lamp(kind, c, w, p, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: sea slab with a cliff block at the back, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.3, 1.3), random.uniform(-1.3, 1.3), random.uniform(-1.4, .2)))
    v.co.z -= 2
put(bm, "sea", (0, 0, 0))
block((0, 7.5, 0), (17, 6.5, 2.6), "cliff", 0)
for i in range(6): block((-8 + i * 3, 4.2, 0), (3.2, 1.2, 1.6 + (i % 2) * .5), "basalt2", i * .1)
# the stepping stones: hexagonal basalt columns of different heights across the water
path = [(-3, 3.2), (-2.2, 1.8), (-1, .6), (.2, -.6), (1.4, -1.8), (2.2, -3.2), (3.2, -4.6)]
for i, (x, y) in enumerate(path):
    h = 1.5 - i * .17
    column((x, y, 0), .95, .85, h, 6, "basalt" if i % 2 else "basalt2", .06)
    column((x, y, h), .85, .85, .05, 6, "basalt2")
# the sleeping giant's boot: a stone foot and shin standing in the shallows, toes pointing at the viewer
for i, (dx, dy, r) in enumerate(((0, 0, 1.0), (.5, -.7, .8), (1.0, -1.2, .7), (1.4, -1.6, .6), (-.5, -.8, .8))):
    column((-6 + dx, -2.5 + dy, 0), r, r * .85, .9 - i * .1, 6, "basalt2", .05)
column((-6, -2.5, .7), 1.1, .95, 1.6, 6, "basalt", .05)
column((-6, -2.5, 2.2), 1.0, .8, 1.4, 6, "basalt2", .05)
for i in range(5): column((-6 + math.cos(i * 1.26) * .5, -2.5 + math.sin(i * 1.26) * .5, 2.0), .22, .18, .3, 5, "basalt")
# fisherman's hut on the cliff: stone walls, thatched roof, lit window and door, chimney, lantern
block((5.5, 7, 2.6), (4.2, 3.4, 2.4), "wall")
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 5.2, v.co.y * 4.4, (v.co.z + .5) * 2.0))
    if v.co.z > 1: v.co.y = 0
put(bm, "thatch", (5.5, 7, 5.0))
block((4.2, 5.28, 3.4), (1.0, .1, 1.0), "window"); block((6.8, 5.28, 2.6), (.9, .1, 1.5), "door")
block((6.6, 7.8, 5.4), (.6, .6, 1.6), "wall"); block((3.4, 5.2, 4.2), (.2, .2, .6), "lantern")
lamp("POINT", (1, .65, .25), 450, (4.2, 4.6, 3.6)); lamp("POINT", (1, .7, .3), 250, (3.4, 4.8, 4.2))
block((3.6, 4.6, 2.6), (.12, .12, 1.6), "rope"); block((3.6, 4.6, 4.1), (.5, .06, .06), "rope")
# rough waves: foam crests and swells around the stones, a row of breakers
for i in range(26):
    x, y = random.uniform(-11, 11), random.uniform(-9, 3)
    if math.hypot(x, y) < 12 and not any(math.hypot(x - a, y - b) < 1.4 for a, b in path):
        ball((x, y, .02), random.uniform(.5, 1.1), "foam", .12)
for i in range(7):
    x = -9 + i * 3
    ball((x, -8.4 + math.sin(i) * .5, .05), 1.4, "basalt2", .15); ball((x, -8.4, .2), 1.2, "foam", .1)
# boat with a net and a fisherman in a red coat on the shore
block((-1, 3.2, 2.6), (2.6, .9, .5), "rope"); block((-1, 3.2, 3.1), (2.8, .3, .1), "basalt")
ball((-1, 3.2, 3.3), .35, "coat", 1.2); ball((-1, 3.2, 3.8), .25, "pebble")
lamp("SUN", (1, .5, .3), 5, (-26, -14, 8), (0, 0, 2)); lamp("SUN", (.3, .6, .9), 2.2, (22, 24, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((16, -54, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
