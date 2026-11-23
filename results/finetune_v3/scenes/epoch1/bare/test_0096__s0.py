import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1153)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, em=0, metal=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
snow, ice, ice2, ice3, steel, pine, pine2, hut, roof, wood, win, flag, helmet1, helmet2, helmet3, red, white, steel2 = (
    tint(c) for c in ((.55, .62, .72), (.1, .2, .3), (.06, .14, .24), (.14, .26, .36), (.3, .32, .36), (.04, .13, .1), (.03, .1, .08), (.3, .15, .1), (.5, .5, .55), (.25, .17, .1), (1, .7, .3), (.9, .1, .1), (.8, .15, .1), (.1, .3, .7), (.75, .75, .7), (.7, .05, .05), (.8, .8, .8), (.15, .16, .2)))
win = tint((1, .7, .3), 10); flag = tint((.9, .1, .1), 1.5); ice = tint((.1, .2, .3), rough=.2); ice2 = tint((.06, .14, .24), rough=.2); ice3 = tint((.14, .26, .36), rough=.2)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(x, y, z, w, d, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return put(bm, m, (x, y, z), rot)
def tube(x, y, z, r, h, m, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, (x, y, z))
def rail(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return put(bm, m)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: snow ground with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=13, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
put(bm, snow)
# the chute: a long icy trough curving away from the start ramp, with two rails and ice panels
pts = [Vector((1.5 - i * 1.6, -1.0 - i * 2.2 - i * .1, 1.2 - i * .45)) for i in range(10)]
for i in range(9):
    a, b = pts[i], pts[i + 1]
    for s in (-1.5, 1.5):
        rail(a + Vector((s, 0, .5)), b + Vector((s, 0, .5)), .22, steel)
    rail(a + Vector((0, 0, 0)), b + Vector((0, 0, 0)), 3.0, ice if i % 2 else ice2)
    for s in (-1.5, 1.5):
        rail(a + Vector((s, 0, 0)), a + Vector((s, 0, .5)), .2, steel2)
rail(pts[9] + Vector((0, 0, 0)), pts[9] + Vector((0, 0, 1.0)), 3.0, ice3)
# start ramp: a raised snowy platform with a lip, where the sled waits
slab(-4.5, 1.0, 0, 7.0, 5.0, 1.2, snow); slab(-4.5, 1.0, 1.2, 7.0, 5.0, .15, ice3)
for sx in (-1, 1): slab(-1.0, 1.0 + sx * 2.4, 1.35, 1.0, .2, .3, steel2)
# four-man sled: metal frame, four seats, runners, steering handle
slab(-4.5, 1.0, 1.6, 3.2, 1.6, .12, steel)
for i in range(4): slab(-5.4 + i * .6, 1.0, 1.72, .4, 1.0, .25, red if i % 2 else white)
for sy in (-.8, .8): rail((-6.0, 1.0 + sy, 1.35), (-2.9, 1.0 + sy, 1.35), .1, steel2)
for sx in (-6.0, -2.9): rail((sx, 1.0 - .8, 1.35), (sx, 1.0 + .8, 1.35), .1, steel2)
rail((-2.9, 1.0, 1.35), (-2.3, 1.0, 2.1), .1, steel2); rail((-2.3, 1.0, 2.1), (-2.9, 1.0, 2.1), .1, steel2)
# hut beside the ramp with a glowing window, a door, a chimney and a sloped roof
hx, hy = -9.0, 4.5
slab(hx, hy, 0, 4.0, 3.4, 2.6, hut); slab(hx, hy, 2.6, 4.6, 3.8, .3, roof, (.2, 0, 0)); slab(hx, hy, 2.8, 4.4, 3.6, .2, roof, (.2, 0, 0))
slab(hx + 1.4, hy - 1.72, 1.0, 1.2, .1, 1.0, win); slab(hx - 1.2, hy - 1.72, 0, .9, .1, 1.8, wood); slab(hx + 1.3, hy + .8, 2.9, .6, .6, 1.2, hut)
lamp("POINT", (1, .7, .3), 500, (hx + 1.4, hy - 2.5, 1.5))
# helmets on pegs on a board outside the hut
slab(hx - 3.4, hy - 2.0, 0, 2.4, .5, 1.0, wood)
for i, c in enumerate((helmet1, helmet2, helmet3)):
    tube(hx - 4.0 + i * .8, hy - 2.0, 1.2, .38, .4, c, 7, .3)
    tube(hx - 4.0 + i * .8, hy - 2.0, 1.1, .06, .1, steel2, 5)
# starter's flag on a pole at the ramp end, oversized
rail((0.2, -1.5, 0), (0.2, -1.5, 4.0), .14, steel2); slab(.2, -1.5, 3.2, 1.8, .08, 1.0, flag, (0, 0, 0)); slab(1.1, -1.5, 3.2, .08, .08, .08, white)
lamp("POINT", (1, .2, .15), 250, (.2, -2.0, 3.6))
# snow banks, trees and boulders
for i in range(14):
    x, y = random.uniform(-11, 11), random.uniform(-10, 10)
    if math.hypot(x, y) < 12 and (y > -1.5 or x < -1.5) and abs(x + 9) + abs(y - 4.5) > 4.5 and math.hypot(x + 4.5, y - 1) > 4.5:
        for k in range(3): tube(x, y, k * 1.0, 1.0 - k * .3, 1.4, pine if k % 2 else pine2, 6, .05)
        tube(x, y, 0, .15, 1.0, wood, 5)
for i in range(7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.5, 1.1))
    for v in bm.verts: v.co.z *= .7; v.co += Vector((random.uniform(-.15, .15), random.uniform(-.15, .15), 0))
    x, y = random.uniform(-11, 11), random.uniform(-9, 10)
    if math.hypot(x, y) < 12 and (y > -1.5 or x < -1.5): put(bm, snow, (x, y, .1))
lamp("SUN", (1, .55, .3), 6, (-24, -14, 7), (0, 0, 0)); lamp("SUN", (.4, .6, 1), 2.2, (22, 22, 12), (0, 0, 0))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .03, .06, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((-1, -1, 1)); co.location = t + Vector((26, -46, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
