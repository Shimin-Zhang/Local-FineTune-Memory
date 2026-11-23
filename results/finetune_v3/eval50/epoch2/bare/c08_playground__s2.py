import bpy, bmesh, random, math
from mathutils import Vector
random.seed(477)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def toy(c, glow=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .8
    if glow: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = glow
    return m
turf, sand, red, blue, yellow, green, wood, steel, tyre, bark, leaf, bulb = (toy((.1, .22, .09)), toy((.55, .42, .25)), toy((.8, .12, .1)), toy((.12, .3, .8)), toy((.9, .65, .08)),
    toy((.15, .6, .2)), toy((.35, .22, .12)), toy((.3, .32, .35)), toy((.05, .05, .06)), toy((.2, .13, .08)), toy((.2, .4, .12)), toy((1, .85, .5), 14))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    o.data.materials.append(m); sc.collection.objects.link(o); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def rod(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return mk(bm, m)
def ball(at, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=7, radius2=13, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .2)))
    else: v.co.z += random.uniform(-.06, .06)
    v.co.z -= 1.5
mk(bm, turf)
slab((0, 0, 0), (24, 18, .12), turf)
# slide: tower with roof, ladder, winding chute made of tilted panels
sx, sy = -5, 3
for dx in (-1, 1):
    for dy in (-1, 1): rod((sx + dx * 1.4, sy + dy * 1.2, 0), (sx + dx * 1.4, sy + dy * 1.2, 4.2), .12, red)
slab((sx, sy, 4.2), (3.6, 3.2, .2), blue)
slab((sx, sy, 4.4), (3.9, 3.5, .25), yellow, (0, 0, .3))
slab((sx - 1.6, sy, 3.0), (.12, 3.0, 1.2), blue); slab((sx, sy - 1.5, 3.0), (3.2, .12, 1.2), blue)
rod((sx - 1.4, sy - 1.2, 4.4), (sx - 1.4, sy - 1.2, 5.4), .06, steel); rod((sx + 1.4, sy + 1.2, 4.4), (sx + 1.4, sy + 1.2, 5.4), .06, steel)
rod((sx - 1.4, sy - 1.2, 5.4), (sx + 1.4, sy + 1.2, 5.4), .06, steel)
for i in range(6):
    t = i / 5; z = 3.4 - 3.0 * t; y = -1.2 - 4.2 * t
    slab((sx, sy + y, z), (2.0, 1.0, .12), yellow if i % 2 else red, (-.72, 0, 0))
    for s in (-1, 1): slab((sx + s * .95, sy + y, z + .06), (.1, 1.0, .35), blue, (-.72, 0, 0))
for k in range(6): slab((sx - 2.4, sy + 1.2, .5 + k * .6), (.1, .1, .1), wood)
rod((sx - 2.4, sy + 1.2, 0), (sx - 2.4, sy + 1.2, 4.2), .07, wood); rod((sx - 2.0, sy + 1.2, 0), (sx - 2.0, sy + 1.2, 4.2), .07, wood)
# swing set: A-frame, bar, two swings with chains and seats
wx, wy = 3.5, 4.5
for s in (-1, 1):
    rod((wx + s * 3.2, wy - 1.2, 0), (wx, wy, 5.2), .14, red, 6); rod((wx + s * 3.2, wy + 1.2, 0), (wx, wy, 5.2), .14, red, 6)
rod((wx - 3.2, wy, 5.0), (wx + 3.2, wy, 5.0), .1, steel)
for s in (-1, 1):
    for e in (-.35, .35): rod((wx + s * 1.2 + e, wy, 5.0), (wx + s * 1.2 + e, wy, 1.0), .03, steel, 4)
    slab((wx + s * 1.2, wy, .9), (1.0, .35, .12), blue if s < 0 else yellow)
# sandbox with a bucket, spade and tyre ring
bx, by = 5, -4
slab((bx, by, 0), (6, 4.6, .5), wood); slab((bx, by, .4), (5.4, 4.0, .2), sand)
slab((bx - 1.5, by + .5, .6), (1.0, 1.0, .5), red, (0, 0, .4)); slab((bx + 1.5, by - .8, .6), (.15, .8, .1), yellow, (0, 0, 1))
rod((bx + 1.5, by - .8, .6), (bx + 1.5, by - .8, 1.6), .04, wood)
for i in range(8):
    a = i * math.pi / 4
    slab((bx + 2.2 * math.cos(a) * .9 + 0, by + 1.5 + 2.2 * math.sin(a) * .9 - 0, .6), (.7, .4, .35), tyre, (0, 0, a + math.pi / 2))
# seesaw: tilted board on a fulcrum
gx, gy = -6.5, -4.5
rod((gx, gy, 0), (gx, gy, 1.1), .3, steel, 6)
slab((gx, gy, 1.1), (6.5, .9, .22), yellow, (0, .16, 0))
for s in (-1, 1): slab((gx + s * 3.0, gy, 1.1 + s * .5), (.5, .9, .12), red if s < 0 else blue)
# lamp posts, trees, benches, fence
for px, py in ((-10, 6), (10, 7), (-10, -7), (10, -8)):
    rod((px, py, 0), (px, py, 4.2), .1, steel, 5); ball((px, py, 4.5), .4, bulb); lamp("POINT", (1, .85, .5), 280, (px, py, 4.5))
for tx, ty in ((-9, 0), (9, 1), (-2, 8.5), (0, -8.5)):
    rod((tx, ty, 0), (tx, ty, 2.6), .3, bark, 5); ball((tx, ty, 3.6), 1.9, leaf, .9); ball((tx + .6, ty, 4.6), 1.2, leaf, .9)
for i in range(12): slab((-9 + i * 1.6, -9.2, 0), (.25, .25, 1.2), wood)
slab((0, -9.2, 1.0), (19, .15, .15), wood)
slab((-1, -7.5, 0), (3, .7, .12), wood); slab((-1, -7.5, .5), (3, .7, .12), wood)
for s in (-1, 1): slab((-1 + s * 1.3, -7.5, 0), (.15, .6, .55), wood)
lamp("SUN", (1, .6, .35), 4.5, (-26, -16, 9), (0, 0, 1)); lamp("SUN", (.35, .45, 1), 2.2, (22, 22, 12), (0, 0, 1))
w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .02, .045, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
t = Vector((0, 0, 1.5)); co.location = t + Vector((14, -52, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
