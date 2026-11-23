import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1535)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
sand, sand2, rockm, rock2, dome = tone((.42, .25, .12)), tone((.3, .17, .09)), tone((.3, .17, .1)), tone((.2, .12, .08)), tone((.5, .45, .4))
wood, wood2, cloth, skin, tunic = tone((.25, .15, .08)), tone((.15, .09, .05)), tone((.45, .1, .08)), tone((.55, .35, .25)), tone((.5, .45, .4))
sun1, sun2, sunrim, dune = tone((1, .5, .08), 3), tone((1, .15, .05), 3), tone((1, .75, .3), 4), tone((.35, .2, .1))
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def rod(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return make(bm, m)
def ball(at, r, m, sq=1, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co.z *= sq; v.co += Vector((random.uniform(-.1, .1), random.uniform(-.1, .1), random.uniform(-.1, .1))) * r
    return make(bm, m, at)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=8, radius2=15, depth=3.2)
for v in bm.verts:
    v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
make(bm, sand)
# dunes and boulders
for x, y, r in ((-11, 6, 4), (11, 8, 4.5), (-12, -4, 3.5), (12, -3, 3), (0, 12, 4)):
    ball((x, y, 0), r, dune, .25, 2)
for i in range(14):
    x, y = random.uniform(-13, 13), random.uniform(-12, 12)
    if abs(x) < 6 and y > -2: continue
    ball((x, y, .2), random.uniform(.3, .8), rockm if i % 2 else rock2, .7)
# the domed homestead: ribbed dome, door arch, windows, annex
hx, hy = 0, 4
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=5)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.01], context='VERTS')
make(bm, dome, (hx, hy, 0))
for k in range(8):
    a = k * math.pi / 8
    rod((hx + math.cos(a) * 5, hy + math.sin(a) * 5, 0), (hx, hy, 5), .12, wood2, 4)
for k in range(3):
    for a in range(8): rod((hx + math.cos(a * math.pi / 4) * (5 - k * 1.5), hy + math.sin(a * math.pi / 4) * (5 - k * 1.5), 5 * math.sqrt(1 - (1.5 * k / 5) ** 2)), (hx + math.cos((a + 1) * math.pi / 4) * (5 - k * 1.5), hy + math.sin((a + 1) * math.pi / 4) * (5 - k * 1.5), 5 * math.sqrt(1 - (1.5 * k / 5) ** 2)), .1, wood2, 4)
slab((hx, hy - 5, 0), (2.4, .8, 3), wood2); slab((hx, hy - 5.45, 0), (1.6, .2, 2.4), tone((.03, .02, .02)))
for a in (-.7, .7):
    slab((hx + math.sin(a) * 4.4, hy - math.cos(a) * 4.4, 2.2), (.9, .3, 1.1), sun1, rot=(0, 0, 0))
slab((hx + 7, hy - 1, 0), (4, 3.5, 2.2), dome); slab((hx + 7, hy - 1, 2.2), (4.4, 3.9, .3), wood2)
slab((hx + 7, hy - 2.8, .8), (.9, .15, .9), sun1)
glow((hx + 7, hy - 3.5, 1.2), (1, .5, .1), 400)
# well with a crossbar and a hand pump
rod((-7, -2, 0), (-7, -2, 3), .15, wood, 5); rod((-8.5, -2, 2.8), (-5.5, -2, 2.8), .12, wood, 5); rod((-7, -2, 2.8), (-7, -2.4, 1.2), .04, wood2, 4)
# a stack of crates, a barrel, a rack of dried meat and a water jug
for i, (x, y, z) in enumerate(((-4, -3, 0), (-3, -3.2, 0), (-3.5, -3.1, 1), (-10, 3, 0), (-10, 3, 1))):
    slab((x, y, z), (1.1, 1.1, 1), wood if i % 2 else wood2, rot=(0, 0, i * .3))
rod((10, -4, 0), (10, -4, 1.3), .7, wood2, 7)
# Luke: tunic, boots, belt, hood, and a blaster pistol
lx, ly = 5, -7
slab((lx, ly, 0), (.9, .5, 1.2), tunic); slab((lx, ly, 1.2), (.5, .5, 1.1), tunic); slab((lx, ly, 1.1), (.55, .55, .15), wood2)
for s in (-.2, .2): slab((lx + s, ly, 0), (.25, .35, .8), wood2)
ball((lx, ly, 2.55), .38, skin, 1, 1)
for s in (-1, 1): rod((lx + s * .3, ly, 1.9), (lx + s * .55, ly - .5, 1.5), .13, tunic, 4)
rod((lx + .6, ly - .5, 1.5), (lx + .9, ly - .7, 1.1), .1, wood2, 4)
# the two suns, low on the horizon behind the homestead
for sx, sy, r, m in ((-4, 14.5, 3.2, sun1), (4, 15, 2.4, sun2)):
    ball((sx, sy, r * .5), r, m, 1, 2)
    ball((sx, sy, r * .5), r * 1.12, sunrim, 1, 1).scale.z = .04
glow((-4, 10, 2), (1, .5, .1), 3000); glow((4, 10, 2), (1, .2, .08), 1800)
for c, w, p in (((1, .55, .2), 5.5, (-22, -10, 7)), ((.9, .3, .5), 2.2, (16, 22, 8))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("sunset"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .015, .02, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 3, 3)); co.location = tg + Vector((6, -66, 34))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
