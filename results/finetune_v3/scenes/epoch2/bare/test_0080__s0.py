import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1514)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def alloy(k, rgb, em=0, ru=.8, me=0):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = ru; n.inputs["Metallic"].default_value = me
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    M[k] = m
alloy("dust", (.14, .12, .12), ru=.95); alloy("rock", (.2, .18, .17), ru=.9); alloy("rock2", (.13, .12, .13), ru=.9)
alloy("hull", (.55, .56, .6), ru=.4, me=.3); alloy("hull2", (.3, .32, .36), ru=.4, me=.3); alloy("plate", (.45, .2, .08), ru=.5, me=.2)
alloy("ore", (.35, .15, .08), ru=.6, me=.4); alloy("oreglow", (.9, .35, .1), em=2.5); alloy("glass", (.3, .8, 1), em=6)
alloy("lamp", (1, .75, .4), em=18); alloy("tether", (.7, .7, .72), ru=.3); alloy("dark", (.04, .04, .05), ru=.6)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def slab(at, s, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, k, at, rot)
def drum(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at, rot)
def bar(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, k)
def blob(at, r, k, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.85, 1.15), v.co.y * random.uniform(.85, 1.15), v.co.z * sq * random.uniform(.8, 1.1)))
    return mk(bm, k, at)
def beam(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=3.6)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.8
mk(bm, "dust")
# the asteroid: a faceted lump of rock with a flat landing shelf
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=7)
for v in bm.verts:
    v.co = Vector((v.co.x * 1.1, v.co.y * 1.0, v.co.z * .8)) + Vector((random.uniform(-.5, .5), random.uniform(-.5, .5), random.uniform(-.3, .3)))
    if v.co.z < 0: v.co.z *= .55
mk(bm, "rock", (0, 0, -1.2))
slab((0, 0, -.4), (17, 14, .6), "rock2")
for i in range(7): blob((random.uniform(-10, 10), random.uniform(-9, 9), .2), random.uniform(.5, 1.2), "rock2", .8)
# drill rig bolted to the rock: four legs, cross-braces, a mast, drill head and glowing drill bit
rx, ry = -3.5, 2.5
for sx in (-1, 1):
    for sy in (-1, 1): bar((rx + sx * 2.2, ry + sy * 2.2, .3), (rx + sx * .9, ry + sy * .9, 3.2), .28, "hull2")
slab((rx, ry, 3.2), (2.6, 2.6, .4), "hull"); slab((rx, ry, 3.6), (1.8, 1.8, 2.4), "plate"); slab((rx, ry, 6.0), (2.4, 2.4, .4), "hull2")
bar((rx, ry, 3.6), (rx, ry, 1.2), .5, "hull2"); drum((rx, ry, .8), .9, .5, 8, "dark", .5)
for k in range(5): drum((rx, ry, 1.3 + k * .55), .38 - k * .04, .5, 6, "oreglow", .34 - k * .04)
beam((rx, ry, 1.4), (1, .45, .15), 900)
for s in (-1, 1): bar((rx + s * 1.4, ry, 3.6), (rx + s * 1.4, ry, 6.0), .15, "hull2")
# ore hopper with chute and glowing load
hx, hy = 2.2, 2.5
drum((hx, hy, 2.4), 1.7, 1.6, 8, "hull", 2.2); drum((hx, hy, 2.4), 2.2, .3, 8, "plate", 1.7)
drum((hx, hy, 1.0), 2.2, 1.4, 8, "hull", 1.7); drum((hx, hy, 1.0), 1.75, .3, 8, "oreglow", 1.75)
bar((hx - 1.6, hy, 1.8), (hx - 3.4, hy, .9), .9, "plate")
for i in range(6): slab((hx - 3.2 - i * .35, hy + random.uniform(-.2, .2), .3 + i * .0), (.5, .5, .4), "ore", (0, 0, i))
beam((hx, hy, 1.4), (1, .45, .15), 300)
# crew dome: cramped, lit from inside, with hatch and antenna
dx, dy = 4.5, -4.5
drum((dx, dy, .3), 3.2, .5, 8, "hull2")
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=3.2)
for v in bm.verts: v.co.z = max(v.co.z, 0) * .85
mk(bm, "glass", (dx, dy, .8))
for i in range(8):
    a = i * math.pi / 4; bar((dx + math.cos(a) * 3.2, dy + math.sin(a) * 3.2, .8), (dx + math.cos(a) * 3.2, dy + math.sin(a) * 3.2, 1.6), .2, "hull")
bar((dx, dy, .3), (dx, dy, 2.2), .15, "hull2"); drum((dx, dy, 2.2), .6, .4, 6, "lamp", .5)
beam((dx, dy, 2.0), (.3, .8, 1), 1200)
slab((dx - 1.4, dy - 3.0, .3), (1.2, .3, 1.8), "hull"); slab((dx - 1.4, dy - 3.2, .8), (.8, .1, .8), "lamp")
bar((dx + 2.5, dy + 1, 3.2), (dx + 3.2, dy + 1.6, 6.5), .1, "tether"); drum((dx + 3.2, dy + 1.6, 6.5), .25, .2, 6, "lamp", .05)
# tethered cargo pod: a capsule on a long cable, drifting above the rock with a thruster glow
cx, cy, cz = -6.5, -6.5, 7.5
drum((cx, cy, cz - 1.8), 1.0, 3.6, 8, "hull", 1.0, (math.pi / 2, 0, .4))
drum((cx + .6, cy - 1.9, cz - 1.8), .7, .8, 8, "hull2", .5, (math.pi / 2, 0, .4)); drum((cx + .6, cy - 2.4, cz - 1.8), .45, .2, 8, "lamp", .3, (math.pi / 2, 0, .4))
bar((cx + 1, cy - .5, cz + 1.5), (cx + 2.5, cy + .5, cz + 1.8), .12, "tether"); drum((cx + 2.5, cy + .5, cz + 1.8), .15, .15, 5, "lamp", .05)
bar((cx - 1, cy + .5, cz - 1.5), (2, 3, 1.0), .12, "tether")
beam((cx + .6, cy - 2.8, cz - 1.8), (1, .7, .3), 250)
# crates and a small rover
for i in range(4): slab((-8 + i * 1.3, -3 + (i % 2) * .2, .3), (1.1, 1.1, 1.1), "plate" if i % 2 else "hull2", (0, 0, i * .3))
for i in range(3): slab((8, 4, .3 + i * .9), (1.4, 1.4, .9), "hull2", (0, 0, i))
for c, w, p in (((1, .85, .6), 5, (24, -14, 10)), ((.3, .5, 1), 2.4, (-20, 20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("void"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .012, .03, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 2.5)); co.location = tg + Vector((-14, -52, 32))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
