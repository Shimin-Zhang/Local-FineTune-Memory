import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1236)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
moss, bark, track, sleeper, log, login, hut, tin, coal, smoke, red, cream, steel, fire, mist = (dye(c) for c in (
    (.12, .2, .09), (.22, .15, .1), (.3, .2, .12), (.2, .13, .08), (.3, .18, .1), (.55, .4, .25), (.35, .2, .12), (.3, .32, .35), (.04, .04, .05), (.45, .45, .5), (.5, .1, .08), (.55, .5, .4), (.2, .22, .25), (1, .45, .1), (.6, .65, .7)))
fire = dye((1, .4, .1), 18)
def part(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rz=0, rx=0, ry=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return part(bm, m, at, (rx, ry, rz))
def cone(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return part(bm, m, at, rot)
def puff(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return part(bm, m, at)
def glowlight(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# forest floor base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.4, 1.4), random.uniform(-1.4, 1.4), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.7
part(bm, moss)
# the logging track: sleepers and two rails along a gentle curve
for i in range(28):
    x = -10 + i * .78; y = -2.2 + .006 * (x + 10) ** 2
    blk((x, y, .05), (.35, 1.9, .18), sleeper, rz=.012 * (x + 10))
for s in (-.6, .6):
    for i in range(27):
        x = -10 + i * .78; y = -2.2 + s + .006 * (x + 10) ** 2
        blk((x + .39, y, .22), (.8, .14, .14), steel, rz=.012 * (x + 10))
# small steam engine at the front of the line
ex, ey = 6.5, -1.7
blk((ex, ey, .6), (4.2, 1.5, .3), red)
cone((ex - .3, ey, .9), .95, 3.0, 8, red, .85, rot=(0, math.pi / 2, 0)).location.x = ex - 1.5
blk((ex - 2.6, ey, .9), (.15, 1.2, .5), coal)
cone((ex + .8, ey, 1.5), .8, 1.6, 8, red)
cone((ex + .8, ey, 3.0), .5, .5, 8, red, .35)
blk((ex + .8, ey, 3.4), (.12, .12, 1.0), steel)
blk((ex - .2, ey, 2.5), (2.0, 1.1, .5), coal)
blk((ex + 2.2, ey, 1.0), (1.0, 1.2, .9), coal)
blk((ex + 2.2, ey, 1.9), (.9, .9, .3), tin)
for wx in (-1.4, .3, 1.6):
    for s in (-.8, .8): cone((ex + wx, ey + s, .5), .5, .2, 8, steel, rot=(math.pi / 2, 0, 0)).location.z = .5
blk((ex - 2.4, ey, .2), (.3, .3, .3), red)
for k in range(4): puff((ex + 1.5 + k * 1.1, ey, 3.8 + k * .5), .5 + k * .2, smoke, .8)
glowlight((1, .45, .1), 300, (ex - 2.8, ey, 1.4))
# flat wagons stacked with logs
for wx in (1.5, -1.5, -4.5):
    wy = -2.2 + .006 * (wx + 10) ** 2
    blk((wx, wy, .3), (2.4, 1.7, .15), sleeper)
    for s in (-.8, .8): cone((wx, wy + s, .3), .22, .2, 6, steel, rot=(math.pi / 2, 0, 0))
    for row, (dy, dz) in enumerate(((-.45, .5), (.45, .5), (0, .85), (0, 1.15))):
        for k in range(3):
            cone((wx - .8 + k * .8, wy + dy, dz), .22, 2.0, 6, log, rot=(0, math.pi / 2, 0))
            cone((wx - .8 + k * .8, wy + dy, dz), .15, .05, 6, login, rot=(0, math.pi / 2, 0))
# loader crane on wheels beside the track
cx, cy = -6.5, 2.6
blk((cx, cy, .3), (2.6, 2.0, .3), red)
for s in (-1, 1): cone((cx, cy + s * .95, .35), .38, .2, 7, steel, rot=(math.pi / 2, 0, 0))
blk((cx - .4, cy, .6), (1.8, 1.6, 1.2), red); blk((cx - .4, cy, 1.8), (2.0, 1.8, .15), tin)
blk((cx + 1.0, cy, .6), (.5, 1.4, .8), cream)
blk((cx + .6, cy, 1.8), (.25, .25, 3.2), steel)
blk((cx + .6, cy, 4.7), (3.6, .25, .25), steel, rz=0, ry=.25)
blk((cx + 3.8, cy, 3.3), (.08, .08, 1.5), steel)
blk((cx + 3.8, cy, 3.2), (.5, .5, .25), steel)
blk((cx + 3.8, cy, 3.0), (.15, .15, .2), coal)
# camp hut with tin roof and a chimney
blk((-1, 6.2, 0), (4.2, 3.0, 2.2), hut)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 4.8, v.co.y * 3.6, (v.co.z + .5) * 1.6))
    if v.co.z > .8: v.co.x *= .1
part(bm, tin, (-1, 6.2, 2.2))
blk((-1, 4.65, 0), (.9, .1, 1.6), coal); blk((.3, 4.65, .8), (.9, .1, .8), fire)
blk((.8, 6.6, 2.4), (.5, .5, 1.4), steel)
glowlight((1, .5, .15), 350, (.3, 4.0, 1.2))
# camp fire ring and stump seats
for i in range(7):
    a = i * .9; cone((-4.5 + math.cos(a) * .9, 4.5 + math.sin(a) * .9, 0), .22, .3, 5, steel)
cone((-4.5, 4.5, 0), .5, .8, 5, fire, .05)
glowlight((1, .5, .15), 500, (-4.5, 4.5, 1.0))
for i in range(3): cone((-3.2 + i * 1.2, 3.6, 0), .35, .5, 6, sleeper)
# pines around the clearing, misty trunks, and a few stumps
for i in range(34):
    a = random.uniform(0, 6.28); r = random.uniform(10.2, 13.2)
    x, y = r * math.cos(a), r * math.sin(a)
    if abs(y) < 4.5 and x > -9 and x < 9 and y > -6: continue
    h = random.uniform(4.5, 7)
    cone((x, y, 0), .35, h * .3, 5, bark)
    for k in range(3): cone((x, y, h * .25 + k * h * .22), 1.7 - k * .45, h * .38, 7, moss, .1)
for i in range(5): puff((random.uniform(-11, 11), random.uniform(-8, 8), .1), random.uniform(.6, 1.2), mist, .12)
for i in range(4): cone((random.uniform(-9, 9), random.uniform(2, 9), 0), .45, .5, 6, sleeper)
# moonlit fog: pale cyan key, violet rim
for c, w, p in (((.65, .85, .95), 5, (-24, -16, 11)), ((.55, .4, .8), 2.2, (22, 22, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("fog"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .025, .035, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80
cr = bpy.data.objects.new("cam", cm); sc.collection.objects.link(cr); sc.camera = cr
cr.location = (26, -52, 30)
cr.rotation_euler = (Vector((0, 0, 1.5)) - cr.location).to_track_quat('-Z', 'Y').to_euler()
