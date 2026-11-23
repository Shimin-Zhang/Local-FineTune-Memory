import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1374)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, glow=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
bog, bog2, river, bank = tone((.1, .06, .04)), tone((.14, .08, .05)), tone((.06, .13, .15)), tone((.2, .15, .08))
peat, peat2, peat3 = tone((.22, .1, .05)), tone((.16, .07, .04)), tone((.3, .17, .09))
timber, timber2, thatch = tone((.3, .2, .12)), tone((.18, .11, .07)), tone((.35, .26, .12))
stone, smoke, grass = tone((.25, .25, .27)), tone((.3, .3, .34)), tone((.1, .2, .06))
win = tone((1, .65, .25), 12); fire = tone((1, .45, .1), 16)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(w, d, h, at, m, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mk(bm, m, at, rot)
def cyl(r, h, at, m, n=7, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def puff(r, at, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15)
    return mk(bm, m, at)
def lamp(kind, rgb, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = rgb, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# bog base with a winding river through it
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13.5, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .4)))
    else: v.co.z += random.uniform(-.1, .1)
mk(bm, bog, (0, 0, -1.7))
for i in range(14):
    a = i / 14 * math.tau; x, y = math.cos(a) * 11.2, math.sin(a) * 11.2
    if abs(y + math.sin(x * .45) * 1.5) < 2.6 or abs(x) > 9.5: continue
    puff(random.uniform(.8, 1.4), (x, y, .2), grass)
pts = [(-12, 0)]
for x in range(-11, 13, 2): pts.append((x, math.sin(x * .45) * 1.5))
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
    blk(L + .3, 4.2, .12, ((x0 + x1) / 2, (y0 + y1) / 2, 0), river, (0, 0, math.atan2(dy, dx)))
# peat quay: a timber-lined bank on the north side of the river
blk(17, 3.4, .5, (-1, 4.2, 0), bank)
for i in range(9):
    cyl(.12, 1.4, (-8 + i * 2, 2.7, 0), timber2, 5)
blk(17, .15, .9, (-1, 2.7, .5), timber2)
# the tall stack of peat, a stepped pyramid of cut blocks
for k, (n, z) in enumerate([(6, 0), (5, .8), (4, 1.6), (3, 2.4), (2, 3.2), (1, 4.0)]):
    for i in range(n):
        blk(1.5, 1.2, .8, (-4 + i * 1.5 - (n - 1) * .75 + k * .2, 5.4, z), (peat, peat2, peat3)[(i + k) % 3], (0, 0, .03 * i))
# the flat boat, loaded with turf blocks, and a pole
bx, by = 2.5, math.sin(2.5 * .45) * 1.5
blk(5.2, 1.8, .6, (bx, by, .1), timber2, (0, 0, math.sin(2.5 * .45) * .5)); blk(5.2, 1.8, .15, (bx, by, .7), timber, (0, 0, math.sin(2.5 * .45) * .5))
for i in range(3):
    for j in range(2): blk(1.3, .9, .7, (bx - 1.5 + i * 1.5, by - .4 + j * .8, .85), peat if (i + j) % 2 else peat3, (0, 0, .2))
cyl(.08, 5, (bx + 2.4, by + .6, .3), timber2, 5, rot=(0, .3, 0))
# wooden bridge across the river
for sx in (-1, 1): blk(.3, 5.6, .2, (7.5 + sx * .8, -1.2, 1.1), timber)
for i in range(9): blk(2.0, .6, .12, (7.5, -4.0 + i * .65, 1.0), timber)
for sy in (-1, 1):
    for sx in (-1, 1): blk(.14, .14, 1.2, (7.5 + sx * .8, -1.2 + sy * 2.6, 1.2), timber2)
    blk(1.8, .1, .1, (7.5, -1.2 + sy * 2.6, 2.3), timber2)
# the cottage with a smoking chimney
cx, cy = -6.5, 8.5
blk(5.2, 3.6, 2.2, (cx, cy, 0), stone)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z > 0: v.co.x = 0
    v.co = Vector((v.co.x * 6.0, v.co.y * 4.4, (v.co.z + .5) * 1.8))
mk(bm, thatch, (cx, cy, 2.2))
blk(1.0, .12, 1.8, (cx - 1.2, cy - 1.82, 0), timber2); blk(1.2, .12, .9, (cx + 1.2, cy - 1.82, .9), win)
cyl(.4, 2.8, (cx + 1.8, cy + .8, 2.6), stone, 5, r2=.3)
for i in range(4): puff(.4 + i * .2, (cx + 1.8 + i * .5, cy + .8, 5.8 + i * 1.1), smoke)
lamp("POINT", (1, .6, .25), 350, (cx + 1.2, cy - 2.6, 1.2))
# peat-cutting tools and a lantern on the quay
blk(.12, .12, 1.6, (3.5, 3.6, 0), timber2); blk(1.4, .12, .12, (4.0, 3.6, 1.5), timber2)
cyl(.3, .5, (6.5, 3.4, 0), fire, 6); cyl(.4, .1, (6.5, 3.4, .5), stone, 6); lamp("POINT", (1, .5, .15), 400, (6.5, 3.4, 1.2))
lamp("SUN", (1, .55, .35), 5, (-26, -14, 9), (0, 0, 1)); lamp("SUN", (.4, .55, .8), 2, (22, 24, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 1.5)); co.location = t + Vector((-6, -60, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
