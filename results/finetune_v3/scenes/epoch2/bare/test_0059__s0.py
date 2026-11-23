import bpy, bmesh, math, random
from mathutils import Vector
random.seed(979)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def ink(rgb, em=0):
    m = bpy.data.materials.new("i"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
sea, deep, land, rock, foam = ink((.04, .16, .22)), ink((.02, .08, .12)), ink((.12, .2, .1)), ink((.2, .2, .22)), ink((.6, .7, .75))
hook, wood, sail, fish, beak = ink((.35, .38, .42)), ink((.3, .17, .08)), ink((.6, .5, .35)), ink((.3, .35, .4)), ink((.7, .5, .1))
fire, eye, gull = ink((1, .45, .08), 12), ink((1, .1, .05), 14), ink((.8, .85, .9))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def spike(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def orb(at, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, m, at)
def beam(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length))
    return mk(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def lit(kind, at, rgb, w, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = rgb; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=15, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 2
mk(bm, deep)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=14.8, radius2=14.8, depth=.3)
for v in bm.verts: v.co.z += random.uniform(-.05, .05)
mk(bm, sea, (0, 0, -.1))
# the island: a fish-shaped land mass, nose to the right, tail to the left, with a hump and a fin
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 9.5, v.co.y * 4.6, v.co.z * 1.7))
    if v.co.x < -6: v.co.y *= .55
    if v.co.z > 0: v.co.z += random.uniform(-.1, .15)
mk(bm, land, (0, 0, 0))
for k in range(5): orb((-3 + k * 2.6, random.uniform(-1.5, 1.5), 1.4), random.uniform(.8, 1.2), land, .6)
slab((3.5, 0, 1.4), (3.0, .5, 2.2), land, (0, .3, 0)); slab((-7.5, 0, 1.3), (1.4, .5, 2.4), land, (0, -.2, 0))
# the great hook: a carved stone hook rising from the nose, with a glowing eye
hx = 9.5
for i in range(7):
    a = math.pi * (1.0 + i * .143)
    p = Vector((hx + 2.6 * math.cos(a), 0, 5.5 + 2.6 * math.sin(a)))
    q = Vector((hx + 2.6 * math.cos(a + .2), 0, 5.5 + 2.6 * math.sin(a + .2)))
    beam(p, q, 1.5 - i * .1, hook)
beam((hx, 0, 0), (hx, 0, 5.5), 1.7, hook); beam((hx + 2.6, 0, 5.5), (hx + 1.4, 0, 4.0), 1.1, hook)
spike((hx, 0, 0), 2.4, 1.2, 7, rock, 1.8)
orb((hx + 1.5, -1.1, 8.4), .7, eye); lit("POINT", (hx + 1.5, -2, 8.4), (1, .1, .05), 500)
# carved posts on the shore, each with a face and arms
for k, (px, py) in enumerate(((-2, -4.6), (0.5, -4.9), (3, -4.6), (-4.5, -4.2))):
    spike((px, py, 0), .55, 3.4 + k * .3, 6, wood, .45)
    slab((px, py - .5, 2.4), (.7, .3, .5), wood); beam((px - .8, py, 3.0), (px + .8, py, 3.4), .22, wood)
    for s in (-1, 1): orb((px + s * .2, py - .55, 2.9), .13, fire)
# a fire on the beach with logs
for k in range(3): beam((-1.0 + k * .1, -3.2, .1), (-1.0 - k * .1, -3.2, .5), .22, wood)
spike((-1, -3.2, .3), .5, 1.3, 5, fire, .05); lit("POINT", (-1, -3.6, 1.2), (1, .45, .1), 700)
# a canoe pulled up on the sand with a sail rolled on a mast
cx, cy = 6.5, -7.0
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 5.0, v.co.y * 1.3, v.co.z * .8))
    if abs(v.co.x) > 1.5: v.co.z += .5
    if v.co.z > 0: v.co.y *= .7
mk(bm, wood, (cx, cy, .5), (0, 0, .4))
beam((cx - .5, cy, .8), (cx - .5, cy, 4.2), .15, wood); beam((cx - .5, cy, 3.0), (cx + 1.5, cy, 3.2), .12, wood)
slab((cx + 1.0, cy, 2.9), (2.4, .2, .3), sail)
for k in range(3): beam((cx - 1.5 + k * 1.0, cy - .4, .8), (cx - 1.5 + k * 1.0, cy + .4, .8), .12, wood)
# a few rocks and foam lines
for k in range(7):
    a = random.uniform(0, 6.28); r = random.uniform(10, 13)
    orb((r * math.cos(a) * 1.0, r * math.sin(a) * .8, .1), random.uniform(.4, .9), rock, .7)
for k in range(10):
    a = k * .63; slab((11 * math.cos(a), 5.5 * math.sin(a) - 1, .02), (1.8, .2, .06), foam, (0, 0, a + 1.57))
# gulls circling above
for k in range(6):
    a = k * 1.05; r = 5 + k * .8; z = 12 + (k % 3) * 1.5
    gx, gy = r * math.cos(a), r * math.sin(a) * .6
    for s in (-1, 1): beam((gx, gy, z), (gx + s * 1.2 * math.cos(a + 1.57), gy + s * 1.2 * math.sin(a + 1.57), z + .8), .16, gull)
    orb((gx, gy, z), .35, gull, .8)
# moonlit dusk: cold blue key from the left, magenta rim behind
lit("SUN", (-26, -12, 10), (.55, .65, 1), 4.5, (0, 0, 3))
lit("SUN", (22, 20, 12), (.9, .4, .7), 2.2, (0, 0, 3))
w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .045, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 5)); co.location = t + Vector((6, -66, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
