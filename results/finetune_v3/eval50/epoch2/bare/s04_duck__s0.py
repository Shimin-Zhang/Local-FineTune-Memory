import bpy, bmesh, random, math
from mathutils import Vector
random.seed(936)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def surf(rgb, glow=0, rough=.7):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if glow: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    return m
duck, duck2, beak, eye, rock, rock2, pond, foam, reed, float = (surf(c) for c in (
    (.9, .65, .06), (.8, .58, .06), (.95, .3, .05), (.02, .02, .02), (.2, .2, .22), (.15, .15, .17), (.03, .1, .17), (.6, .7, .75), (.2, .25, .1), (.9, .1, .1)))
pond = surf((.03, .1, .17), .25, .1); lamp = surf((1, .75, .3), 14)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("d"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("d", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def ico(at, sc3, m, rot=(0, 0, 0), jit=0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * sc3[0], v.co.y * sc3[1], v.co.z * sc3[2])) + Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit)))
    return add(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def beam(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return add(bm, m)
def light(kind, rgb, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floating island of moss and stone with a pond in the middle
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=12, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
add(bm, rock2)
cyl((0, 0, 0), 8.2, .12, 10, pond)
for k in range(14):
    a = k * .45; ico((math.cos(a) * 8.6, math.sin(a) * 8.6, .2), (1.2, .9, .5), foam, jit=.1)
# the duck, enlarged: body, breast, head, beak, eyes, wings, tail, feet
ico((0, 0, 2.2), (3.2, 2.4, 2.2), duck, jit=.04)
ico((0, -1.5, 1.7), (2.0, 1.4, 1.6), duck2, jit=.03)
ico((0, 1.6, 5.2), (1.6, 1.5, 1.5), duck, jit=.03)
cyl((0, 2.9, 5.0), .6, 1.3, 6, beak, .3, rot=(math.pi / 2, 0, 0))
cyl((0, 2.7, 4.55), .5, .2, 6, beak, .5, rot=(math.pi / 2, 0, 0))
for s in (-1, 1):
    ico((s * .9, 2.85, 5.7), (.2, .2, .2), eye)
    ico((s * .95, 2.95, 5.75), (.07, .07, .07), surf((1, 1, 1), 3))
for s in (-1, 1):
    ico((s * 2.9, -.3, 2.4), (1.3, 1.9, .5), duck2, rot=(0, 0, s * .3))
ico((-1.8, -3.0, 3.6), (.9, .8, .8), duck, jit=.03)
for s in (-1, 1):
    ico((s * .9, -1.6, .3), (.4, .8, .25), beak)
# ripples around the duck
for k in range(3):
    for i in range(10):
        a = i * math.pi * 2 / 10 + k * .3
        ico((math.cos(a) * (4.6 + k * .9), math.sin(a) * (3.4 + k * .6), .15), (.7, .25, .06), foam, rot=(0, 0, a))
# lily pads, reeds, a little float and a floating lantern
for x, y, r in ((-5.5, 3.5, 1.3), (5.8, 4.2, 1.1), (-4.8, -4.5, 1.0)):
    cyl((x, y, .12), r, .08, 7, surf((.1, .35, .15)))
for x, y, h in ((7.5, -3.5, 3.0), (8.2, -2.5, 2.2), (-7.5, 5.5, 2.6), (-8.2, 4.2, 3.4), (6.5, 6.5, 2.8)):
    cyl((x, y, .1), .1, h, 4, reed, .04)
cyl((-6.5, -1.5, .1), .7, .5, 8, float, .65); cyl((-6.5, -1.5, .6), .65, .1, 8, surf((.9, .9, .9)))
ico((4.5, -4.5, 1.0), (.45, .45, .5), lamp)
light("POINT", (1, .75, .3), 450, (4.5, -4.5, 1.4))
for x, y, s in ((-9, 6, 1.5), (9, 7, 1.2), (-9.5, -6, 1.0), (9.5, -7, 1.4), (-3, 9.5, 1.1), (3, 9.8, 1.3)):
    ico((x, y, .3), (s * 1.2, s, s * .8), rock, jit=.2)
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(9, 11)
    ico((math.cos(a) * r, math.sin(a) * r, .1), (.3, .25, .2), reed, jit=.05)
# moonlit night: cool blue key, magenta rim, lantern glow
light("SUN", (.5, .65, 1), 4.5, (-24, -14, 11), (0, 0, 2)); light("SUN", (.9, .35, .8), 2.2, (20, 20, 9), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.6)); co.location = t + Vector((6, -50, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
