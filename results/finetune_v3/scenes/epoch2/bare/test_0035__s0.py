import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1044)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
turf, turf2, rock, rock2 = tint((.07, .12, .08)), tint((.1, .16, .1)), tint((.2, .2, .24)), tint((.14, .14, .18))
wool, face, wood, moss = tint((.6, .58, .52)), tint((.08, .07, .08)), tint((.25, .16, .1)), tint((.1, .2, .1))
blue, gold, rose = tint((.2, .6, 1), 5), tint((1, .75, .2), 5), tint((.9, .3, .6), 5)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def rod(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def blob(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mk(bm, m, at)
def glim(at, rgb, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# field base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=13.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
mk(bm, turf)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(3, 11)
    blob((math.cos(a) * r, math.sin(a) * r, 0), random.uniform(.6, 1.2), turf2, .12)
# the ley lines: three crossing bands of glowing tiles, each a chain of thin slabs
def line(a, b, m, w):
    a, b = Vector(a), Vector(b); d = b - a; n = int(d.length / 1.3)
    for i in range(n):
        p = a + d * ((i + .5) / n); rot = (0, 0, math.atan2(d.y, d.x))
        cube(p, (1.2, w, .12), m, rot)
line((-11, -5, .05), (11, 5, .05), blue, .5)
line((-10, 7, .05), (9, -7, .05), gold, .5)
line((-2, -11, .05), (3, 11, .05), rose, .5)
# the standing stone at the crossing: tall tapering slab, moss, glowing runes
sx, sy = .5, -.5
cone((sx, sy, 0), 2.2, .5, 7, rock2, 1.6)
cube((sx, sy, .5), (2.2, 1.2, 8.5), rock, (0, 0, .2), .6)
for i in range(5):
    cube((sx - .1, sy - .65 + i * .02, 2 + i * 1.2), (.5, .1, .35), gold, (0, 0, .2))
for i in range(6):
    a = i * 1.05; blob((sx + math.cos(a) * 2.2, sy + math.sin(a) * 2.2, .2), random.uniform(.5, .8), rock2, .7)
blob((sx - .8, sy - .6, 7.5), .5, moss, .6)
glim((sx, sy - 1.5, 4.5), (1, .75, .3), 700)
# sleeping sheep: wool body, dark face, tucked legs, curled tail
def sheep(x, y, a, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.9)
    for v in bm.verts: v.co = Vector((v.co.x * 1.25, v.co.y, v.co.z * .85)) * random.uniform(.92, 1.08)
    mk(bm, m, (x, y, .7), (0, 0, a))
    f = Vector((math.cos(a), math.sin(a), 0))
    blob((x + f.x * 1.2, y + f.y * 1.2, .75), .42, face, 1)
    blob((x - f.x * 1.1, y - f.y * 1.1, .8), .28, wool, 1)
for i, (x, y, a) in enumerate(((-4.5, -3.5, .5), (-3.2, -5.2, 2.5), (4.5, 2.5, 1.2), (5.8, 1.2, 3.5), (-6, 4.5, -.4), (3.5, -5.5, 1.8))):
    sheep(x, y, a, wool if i % 2 else tint((.5, .48, .45)))
# old signpost: leaning post with three boards and arrow ends
px, py = -7, -1.5
rod((px, py, 0), (px + .5, py, 6), .3, wood)
for i, (z, a) in enumerate(((4.8, .1), (3.7, -.2), (2.6, .15))):
    cube((px + .5 + .4, py, z), (2.2, .12, .55), wood, (0, 0, a), 1)
    cube((px + .5 + 1.6, py, z), (.5, .1, .55), wood, (0, 0, a), .1)
# stones, tufts, a broken ring of old stones
for i in range(8):
    a = i * .785 + .3; blob((math.cos(a) * 6.2, math.sin(a) * 6.2, .1), random.uniform(.5, .8), rock2, .8)
for i in range(18):
    a = random.uniform(0, 6.28); r = random.uniform(3, 11)
    cone((math.cos(a) * r, math.sin(a) * r, 0), .12, random.uniform(.4, .8), 4, moss, .02)
# twilight: violet key from the left, cold blue rim behind
for rgb, w, at in (((.7, .5, 1), 5, (-22, -14, 10)), ((.3, .6, .9), 2.2, (16, 20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("twilight"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .045, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 3)); co.location = tg + Vector((6, -50, 30))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
