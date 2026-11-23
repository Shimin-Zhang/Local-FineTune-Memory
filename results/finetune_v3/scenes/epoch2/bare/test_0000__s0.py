import bpy, bmesh, random, math
from mathutils import Vector
random.seed(44)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def rust(r, g, b, e=0, rough=.9):
    m = bpy.data.materials.new("r"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = rough
    if e: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = e
    return m
sand, sand2, crack, hull, hull2 = rust(.3, .24, .17), rust(.22, .18, .13), rust(.06, .05, .04), rust(.4, .13, .05), rust(.28, .1, .05)
deck, white, shed, wood, scrub = rust(.18, .12, .08), rust(.4, .38, .33), rust(.3, .12, .08), rust(.2, .13, .08), rust(.2, .26, .1)
scrub2, lantern, rope, net = rust(.12, .2, .1), rust(1, .6, .15, 25), rust(.5, .4, .25), rust(.25, .22, .15)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def tube(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def bar(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def clump(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return make(bm, m, at)
def lamp(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# cracked dry seabed slab
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=11, radius1=7, radius2=14.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
make(bm, sand)
for i in range(26):
    a, r = random.uniform(0, 6.28), random.uniform(2, 12)
    box((math.cos(a) * r, math.sin(a) * r, 0), (random.uniform(.9, 2.2), .22, .1), sand2, (0, 0, a + random.uniform(-.4, .4)))
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(1, 12)
    p = Vector((math.cos(a) * r, math.sin(a) * r, .1)); q = p + Vector((math.cos(a + 1.5) * 1.8, math.sin(a + 1.5) * 1.8, 0))
    bar(p, q, .1, crack); bar(q, q + Vector((math.cos(a) * 1.4, math.sin(a) * 1.4, 0)), .1, crack)
# the ship, listing on its keel: hull, deck, cabin, mast, boom, net, dangling ladder
tilt = .14
def hullpt(x, y, z): return Vector((x, y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)))
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    x, y, z = v.co.x * 13, v.co.y * 5.2, v.co.z * 2.6 + 1.3
    if z > 2.6: y *= .8
    if x > 5.5: y *= max(.12, 1 - (x - 5.5) / 3.4); z -= (x - 5.5) * .12
    if x < -6.5: y *= max(.5, 1 + (x + 6.5) * .06)
    v.co = hullpt(x, y, z)
make(bm, hull)
box((0, 0, 2.6), (12.4, 4.4, .25), deck, (0, 0, 0)).rotation_euler = (0, 0, 0)
for o in list(sc.objects)[-1:]: o.location = hullpt(0, 0, 2.6); o.rotation_euler = (0, 0, tilt)
box(hullpt(-3.2, 0, 2.85), (4.4, 3.6, 2.4), white, (0, 0, tilt)); box(hullpt(-3.2, 0, 5.2), (4.8, 4.0, .3), hull2, (0, 0, tilt))
box(hullpt(-3.2, -1.85, 3.9), (1.0, .1, .9), lantern, (0, 0, tilt)); box(hullpt(-5.6, -1.85, 3.9), (1.0, .1, .9), lantern, (0, 0, tilt))
bar(hullpt(1.2, 0, 2.85), hullpt(1.2, 0, 10.5), .35, wood); bar(hullpt(1.2, 0, 8.2), hullpt(6.0, 0, 3.4), .22, wood)
bar(hullpt(1.2, 0, 8.2), hullpt(-3.0, 0, 4.0), .2, wood)
for i in range(5): bar(hullpt(1.2 + i * .9, 0, 8.2 - i * .8), hullpt(1.2 + i * .9, 0, 2.9), .05, rope)
box(hullpt(6.4, 0, 2.85), (1.8, 1.4, .5), net, (0, 0, tilt))
for i in range(9):
    x = -6.2 + i * 1.55
    bar(hullpt(x, -2.7, 2.85), hullpt(x, -2.7, 3.7), .12, wood)
for s in (-1, 1): bar(hullpt(-6.4, s * 2.7, 3.7), hullpt(6.4, s * 2.7, 3.7), .1, wood)
for i in range(12): bar(hullpt(-6.4 + i * 1.07, -2.7, 3.7), hullpt(-6.4 + i * 1.07, 2.7, 3.7), .05, rope)
for s in (-1, 1): bar(hullpt(-6.4, s * 2.7, 2.85), hullpt(-6.4, s * 2.7, 3.7), .12, wood)
lx, ly = 5.8, -3.6
bar((lx, ly, 3.0), (lx + .2, ly, .1), .09, wood); bar((lx + .9, ly, 3.0), (lx + 1.1, ly, .1), .09, wood)
for i in range(8): bar((lx + .02 + i * .025, ly, 2.8 - i * .35), (lx + .92 + i * .025, ly, 2.8 - i * .35), .07, wood)
lamp(hullpt(-3.2, -2.4, 3.9), (1, .6, .15), 500)
# wrecked sheds
for k, (x, y, rz) in enumerate(((-9, 6, .3), (-2, 9.5, -.4), (7, 8, .1))):
    c, s = math.cos(rz), math.sin(rz)
    def at(dx, dy, z): return Vector((x + dx * c - dy * s, y + dx * s + dy * c, z))
    box(at(0, 0, 0), (4.2, 3.2, 2.2), shed, (0, 0, rz))
    for sx in (-1, 1): box(at(sx * 2.2, 0, 2.2), (.2, 3.4, .2), wood, (0, 0, rz))
    box(at(0, 0, 2.4), (4.6, 3.6, .2), hull2, (.12 * (k - 1), 0, rz + .1 * k))
    box(at(-1.2, -1.65, 0), (1.0, .1, 1.5), crack, (0, 0, rz)); box(at(1.2, -1.65, 0), (1.0, .1, 1.1), wood, (0, 0, rz))
    if k == 1: box(at(-.5, -1.65, 1.5), (.8, .1, .7), lantern, (0, 0, rz))
lamp((-2.5, 7.5, 1.8), (1, .6, .15), 250)
# scrubby plants and driftwood
for i in range(30):
    a = random.uniform(0, 6.28); r = random.uniform(8, 13.5)
    if abs(math.cos(a) * r + 1) < 12 and abs(math.sin(a) * r) < 8.5: continue
    clump((math.cos(a) * r, math.sin(a) * r, .2), random.uniform(.3, .7), random.choice((scrub, scrub2)))
for i in range(5):
    a = random.uniform(0, 6.28); r = random.uniform(6, 11)
    bar((math.cos(a) * r, math.sin(a) * r, .2), (math.cos(a) * r + 1.5, math.sin(a) * r + .5, .3), .18, wood)
for col, w, p in (((1, .5, .25), 5.5, (-26, -12, 8)), ((.3, .5, .7), 2.2, (24, 18, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .02, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 1, 3)); co.location = tg + Vector((12, -60, 34))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
