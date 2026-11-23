import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1242)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
snow, snow2, hedge, hedge2 = tint((.55, .6, .72)), tint((.42, .46, .6)), tint((.04, .12, .07)), tint((.06, .16, .09))
brick, roof, glass, dark = tint((.28, .12, .09)), tint((.05, .05, .07)), tint((1, .72, .3), 7), tint((.02, .02, .03))
path, pine, trunk, lampc = tint((.5, .45, .4)), tint((.04, .14, .1)), tint((.14, .08, .05)), tint((1, .8, .45), 14)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at)
def drift(at, r, m, sq=.45):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.85, 1.2), v.co.y * random.uniform(.85, 1.2), v.co.z * sq))
    return put(bm, m, at)
def lamp(kind, at, col, w, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = col; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=9, radius2=19, depth=3.4)
for v in bm.verts:
    v.co.x *= 1.05; v.co.z -= 1.7
    if v.co.z < -1: v.co += Vector((random.uniform(-1.4, 1.4), random.uniform(-1.4, 1.4), random.uniform(-1.5, .3)))
put(bm, snow2)
# hedge maze: a spanning tree over the cells keeps every passage reachable, walls added between unlinked cells
gx, gy, pitch, H = -6, -3, 2.6, 1.5
cells = [(x, y) for x in range(6) for y in range(5)]
order = cells[:]; random.shuffle(order)
seen = {order[0]}; stack = [order[0]]; walls = set()
def link(a, b):
    if a[0] == b[0]:
        for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1): walls.add((a[0], y))
    else:
        for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1): walls.add((x, a[1]))
while stack:
    c = stack[-1]
    nb = [n for n in ((c[0] + 1, c[1]), (c[0] - 1, c[1]), (c[0], c[1] + 1), (c[0], c[1] - 1)) if n in cells and n not in seen]
    if not nb: stack.pop(); continue
    n = random.choice(nb); seen.add(n); stack.append(n); link(c, n)
for (a, b) in zip(cells, cells[1:]):
    if abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 and not ((a[0], b[1]) in walls or (b[0], a[1]) in walls): walls.add((a[0], b[1]) if a[0] == b[0] else (b[0], a[1]))
for i in range(6): walls.add((i, 5))
for j in range(5): walls.add((6, j))
for i in range(6): walls.add((i, 0))
for j in range(1, 5): walls.add((0, j))
for (i, j) in walls:
    x, y = gx + i * pitch, gy + j * pitch
    w = pitch + .1 if i < 6 else pitch * .6
    d = pitch + .1 if j < 5 else pitch * .6
    blk((x, y, 0), (w, d, H), hedge if (i + j) % 2 else hedge2)
    blk((x, y, H - .05), (w + .08, d + .08, .35), snow)
for k in range(16):
    i, j = random.randrange(1, 6), random.randrange(1, 5)
    drift((gx + i * pitch + random.uniform(-.8, .8), gy + j * pitch + random.uniform(-.8, .8), .02), random.uniform(.5, .9), snow)
for k in range(7): blk((gx + 3 * pitch, gy - 1.4 - k * .9, .02), (1.4, .8, .05), path)
for sx in (-1, 1):
    cone((gx + 3 * pitch + sx * 1.6, gy - 3.5, 0), .12, 3.2, 5, trunk, .08); blk((gx + 3 * pitch + sx * 1.6, gy - 3.5, 3.2), (.5, .5, .55), lampc)
    lamp("POINT", (gx + 3 * pitch + sx * 1.6, gy - 3.5, 3.4), (1, .75, .4), 380)
# the Overlook behind the maze: long low block, central tower, rows of lit windows
hx, hy = 0, 10.5
blk((hx, hy, 0), (22, 6, 4.2), brick); blk((hx, hy, 4.2), (23, 6.8, .3), roof)
for k in range(7):
    blk((hx - 9 + k * 3, hy - 3.05, 1.4), (1.2, .1, 1.6), glass if k % 3 else dark); blk((hx - 9 + k * 3, hy - 3.05, 3.0), (1.2, .1, .12), roof)
blk((hx, hy - 3.05, 0), (1.8, .1, 2.6), dark)
blk((hx, hy, 4.5), (7, 5, 5), brick)
for s in (-1, 1):
    for k in range(3): blk((hx + s * 3.55, hy - .5, 5.8 + k * 1.5), (.1, 1.1, 1.0), glass)
blk((hx, hy - 2.55, 5.8), (1.1, .1, 1.1), glass)
for s in (-1, 1): blk((hx + s * 1.8, hy, 9.5), (4.2, 5.6, .35), roof, (0, s * .45, 0))
blk((hx, hy, 9.5), (3.6, 5.6, .35), roof)
cone((hx, hy, 9.8), 1.2, 1.6, 4, roof, .1).rotation_euler.z = .785
blk((hx, hy - 2.55, 8.6), (.9, .1, .9), glass)
lamp("POINT", (hx, hy - 5, 2), (1, .7, .3), 900); lamp("POINT", (hx, hy - 4.5, 6.5), (1, .7, .3), 500)
for (x, y, s) in ((-16, 6, 1.3), (-15, 12, 1.1), (15, 8, 1.4), (16, 13, 1.0), (-12, -10, 1.2), (12, -10, 1.3), (17, -3, 1.0), (-17, -2, 1.1)):
    cone((x, y, 0), .3, 1.2, 5, trunk, .2)
    for k in range(3): cone((x, y, 1 + k * 1.1 * s), 1.9 * s - k * .5 * s, 1.6 * s, 6, pine, .1)
    for k in range(3): cone((x, y, 1.2 + k * 1.1 * s), 1.6 * s - k * .5 * s, .1, 6, snow, .1)
for k in range(8): blk((-2 + k * .5 + (k % 2) * .3, -12.5 + k * .9, .03), (.3, .12, .04), path, (0, 0, .2))
lamp("SUN", (-26, -18, 12), (.45, .55, 1), 4.5, (0, 0, 2)); lamp("SUN", (22, 24, 14), (.5, .6, 1), 2.2, (0, 0, 2))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .012, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((8, -76, 46))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
