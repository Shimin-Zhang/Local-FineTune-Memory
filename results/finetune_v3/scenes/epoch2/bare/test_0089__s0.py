import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1763)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
paints = {}
def paint(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    paints[name] = m
for k, v in dict(sand=(.42, .32, .18), floor=(.36, .3, .22), floor2=(.3, .24, .18), sandstone=(.55, .42, .24), sandstone2=(.45, .34, .2),
                 green=(.12, .3, .18), green2=(.08, .22, .14), gold=(.8, .55, .12), dark=(.04, .03, .03), blue=(.1, .25, .5), red=(.5, .1, .06)).items(): paint(k, v)
paint("sun", (1, .85, .5), 14); paint("flame", (1, .45, .08), 16); paint("lotus", (1, .6, .15), 10)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("t"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("t", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(paints[m]); return o
def blk(at, s, m, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, (rx, 0, rz))
def col(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def lamp(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floating base of sand with rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3)
for v in bm.verts:
    v.co.y *= .85
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
add(bm, "sand")
# temple floor: two stepped terraces and inlaid bands
blk((0, 0, 0), (19, 15, .3), "floor"); blk((0, 0, .3), (18, 14, .25), "floor2")
for i in range(6): blk((0, -6.5 + i * 2.3, .55), (17.4, .35, .03), "sandstone2")
# papyrus-bud columns in two rows, each: stepped plinth, tapering shaft, bud cap, abacus
for r, y in enumerate((-4.2, 4.2)):
    for i in range(6):
        x = -7.5 + i * 3.0; z = .55
        blk((x, y, z), (1.5, 1.5, .4), "sandstone2"); blk((x, y, z + .4), (1.1, 1.1, .3), "sandstone")
        col((x, y, z + .7), .45, 5.0, 8, "sandstone", .38)
        col((x, y, z + 5.7), .62, .5, 8, "green2", .5)
        for k in range(4): col((x + .3 * math.cos(k * 1.57), y + .3 * math.sin(k * 1.57), z + 5.9), .22, 1.0, 5, "green", .04, (0, 0, 0)).rotation_euler = (math.sin(k * 1.57) * .25, -math.cos(k * 1.57) * .25, 0)
        blk((x, y, z + 6.6), (1.7, 1.7, .4), "sandstone")
# roof slabs on the back row only, front row left open; some slabs missing so noon sun pours in
for i in range(5):
    x0 = -9 + i * 3.0
    if i in (0, 1, 2, 4): blk((x0 + 1.5, 4.2, 7.0), (3.0, 1.9, .5), "sandstone2")
    if i in (1, 2, 3): blk((x0 + 1.5, 4.2, 7.5), (3.0, 1.9, .15), "green2")
for i in range(5):
    x0 = -9 + i * 3.0
    if i in (0, 2, 3): blk((x0 + 1.5, 0, 7.0), (3.0, 8.4, .5), "sandstone2")
# the inner sanctuary: back wall with a dark doorway, offering table and braziers
blk((0, 7.2, .55), (19, 1.0, 5.6), "sandstone")
blk((-8.2, 0, .55), (.9, 14.4, 5.6), "sandstone")
blk((0, 7.2, .55), (4.0, 1.0, 3.6), "dark")
blk((0, 7.2, 4.15), (4.0, 1.0, 1.4), "sandstone")
blk((0, 6.2, .55), (3.2, 1.4, .9), "floor2"); blk((0, 6.2, 1.45), (2.4, 1.0, .1), "gold")
for x in (-1.2, 1.2):
    col((x, 6.2, 1.55), .3, .8, 6, "gold", .2); col((x, 6.2, 2.35), .35, .15, 6, "flame")
lamp("POINT", (1, .5, .1), 500, (0, 5.8, 3.0))
# sunlit shafts: glowing patches on the floor where the missing slabs let noon light through
for x, y, w in ((-4.5, 1.0, 1), (-1.5, 2.2, 1), (1.5, -.5, 1), (4.5, 1.5, 1)):
    blk((x, y, .55), (2.4, 3.2, .04), "sun", .3 * x)
lamp("POINT", (1, .85, .5), 700, (-1.5, 1.0, 5.0))
# obelisk outside the front, with a gold pyramidion, and a pair of sphinxes
blk((-12, -8, 0), (1.8, 1.8, .8), "sandstone2")
col((-12, -8, .8), .7, 8.0, 4, "sandstone", .4, (0, 0, math.pi / 4)); col((-12, -8, 8.8), .45, 1.0, 4, "gold", .02, (0, 0, math.pi / 4))
for s in (-1, 1):
    blk((s * 7, -9.5, 0), (1.4, 2.6, 1.1), "sandstone"); blk((s * 7, -11.0, .6), (1.1, 1.1, 1.1), "sandstone2")
    col((s * 7, -11.0, 1.7), .4, .5, 6, "gold", .3)
# palms and a few scattered rocks
for x, y in ((11, -7), (12, 4), (-11, 9)):
    col((x, y, 0), .3, 4.0, 5, "sandstone2", .2)
    for k in range(6): col((x, y, 4.0), .12, 2.2, 4, "green", .02, (math.cos(k) * .9, math.sin(k) * .9, 0)).location = (x, y, 4.0)
lamp("SUN", (1, .88, .6), 8, (-20, -22, 24), (0, 0, 2)); lamp("SUN", (.35, .5, 1), 2, (22, 20, 10), (0, 0, 2))
w = bpy.data.worlds.new("noon"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((10, -62, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
