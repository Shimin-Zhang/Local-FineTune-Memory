import bpy, bmesh, math, random
from mathutils import Vector
random.seed(687)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def shade(c, glow=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = glow
    return m
moss, dirt, logc, bark, pine, pine2, canvas, canvas2, stone, rope, flame, flame2, ember = [shade(c) for c in [(.07,.14,.08),(.14,.1,.07),(.3,.2,.12),(.15,.09,.06),(.04,.15,.1),(.06,.2,.12),(.65,.2,.1),(.5,.12,.08),(.3,.3,.32),(.5,.4,.25),(.2,.08,.05)]]
flame = shade((1, .4, .05), 14); flame2 = shade((1, .8, .2), 16); ember = shade((1, .2, .03), 6)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return make(bm, m, at, (0, 0, rz))
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at)
def rod(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    return make(bm, m, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def rock(at, r, m, sq=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.8, 1.2), v.co.y * random.uniform(.8, 1.2), v.co.z * sq))
    return make(bm, m, at)
def glowlight(at, col, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = col, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# base: mossy forest floor with a dirt patch
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=12, depth=3)
for v in bm.verts:
    v.co.x *= 1.1
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.3, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
make(bm, moss)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6.5, radius2=6.5, depth=.1)
for v in bm.verts: v.co += Vector((random.uniform(-.4, .4), random.uniform(-.4, .4), 0))
make(bm, dirt, (0, 0, 0))
# campfire: stone ring, logs, flames, embers
for i in range(9):
    a = i * math.tau / 9
    rock((2.6 * math.cos(a), -1.5 + 2.6 * math.sin(a), .15), .45, stone)
for i in range(5):
    a = i * 1.3
    rod((1.3 * math.cos(a), -1.5 + 1.3 * math.sin(a), .3), (.3 * math.cos(a), -1.5 + .3 * math.sin(a), 1.0), .13, logc)
cone((0, -1.5, .3), .9, 2.0, 6, flame, .05); cone((.3, -1.4, .3), .55, 1.5, 5, flame2, .03); cone((-.4, -1.6, .3), .5, 1.2, 5, flame2, .03)
glowlight((0, -1.5, 1.6), (1, .45, .1), 900)
# log bench: two logs with end caps and cross logs
for dy in (-.5, .5):
    rod((-4.8, -2.5 + dy, .5), (-1.2, -2.5 + dy, .5), .3, logc)
    rod((-4.8, -2.5 + dy, 1.3), (-4.8, -2.5 + dy, 1.3), .01, logc)
rod((-4.5, -3.1, 1.3), (-4.5, -1.9, 1.3), .22, logc); rod((-1.6, -3.1, 1.3), (-1.6, -1.9, 1.3), .22, logc)
rod((-4.5, -2.5, .5), (-4.5, -2.5, 1.4), .1, logc); rod((-1.6, -2.5, .5), (-1.6, -2.5, 1.4), .1, logc)
# tent: ridge tent with flaps, door, guy ropes and pegs
slab((-5.5, 4.0, 0), (4.4, 5.4, 1.6), canvas, .3, .95)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 4.6, v.co.y * 5.6, (v.co.z + .5) * 1.7))
    if v.co.z > 1: v.co.y = 0
make(bm, canvas2, (-5.5, 4.0, 1.6), (0, 0, .3))
slab((-3.6, 2.2, 0), (1.1, .1, 1.3), flame2, .3)
for sx, sy in ((-7.4, 1.6), (-3.6, 6.4)): rod((sx, sy, 1.2), (sx * .85 - .3, sy * .9, .05), .03, rope, 4)
# lantern on a post and a sleeping bag
rod((4.2, 2.0, 0), (4.2, 2.0, 2.4), .09, bark); slab((4.2, 2.0, 2.4), (.4, .4, .5), flame2)
glowlight((4.2, 2.0, 2.7), (1, .6, .2), 160)
slab((-1.5, 5.5, 0), (1.2, 2.6, .3), canvas, .5, .8)
# pines: trunk plus three stacked cones, scattered around the rim
for i, (x, y, s) in enumerate([(-9, -4, 1.2), (-9.5, 3, 1.4), (-6, 8.5, 1.1), (0, 9.5, 1.5), (6, 8, 1.2), (10, 2, 1.4), (10, -5, 1.1), (5, -9, 1.0), (-5, -9, 1.2), (-1, -9.5, .9)]):
    cone((x, y, 0), .35 * s, 1.6 * s, 5, bark, .25 * s)
    for k in range(3): cone((x, y, (1.0 + k * 1.4) * s), (2.0 - k * .5) * s, 2.2 * s, 7, pine if (i + k) % 2 else pine2, .1)
for i in range(14): rock((random.uniform(-10, 10), random.uniform(-9, 9), .1), random.uniform(.2, .5), stone)
for col, w, p in (((.55, .65, 1), 3.5, (-22, -16, 9)), ((.2, .5, .6), 2, (22, 18, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((12, -56, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
