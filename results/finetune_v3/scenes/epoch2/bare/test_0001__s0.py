import bpy, bmesh, math, random
from mathutils import Vector
random.seed(404)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, em=0):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
scree, scree2, plank, plank2, tin = hue((.28, .24, .2)), hue((.2, .18, .17)), hue((.3, .2, .13)), hue((.22, .15, .1)), hue((.35, .3, .25))
rust, road, rock, snow, ghost = hue((.4, .15, .05)), hue((.35, .27, .2)), hue((.18, .17, .18)), hue((.55, .6, .65)), hue((.4, 1, .9), 12)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def block(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def roofed(at, w, d, h, rh, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
        if v.co.z > 0: v.co.y = 0; v.co.z += rh
    return make(bm, m, at, rot)
def spike(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at)
def rail(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Y', 'Z')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, (v.co.y + .5) * d.length, v.co.z * t)) + a
    return make(bm, m)
def glim(kind, at, col, w, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = col; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=7, radius2=14, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, 0)))
make(bm, scree)
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(1, 12)
    spike((r * math.cos(a), r * math.sin(a) * .8, 0), random.uniform(.4, 1.1), random.uniform(.3, .8), 5, rock, r2=.2)
# bare hillside with a snow cap
spike((0, 10, 0), 8, 9, 8, scree2, r2=2.2)
spike((0, 10, 8.4), 2.6, .9, 8, snow, r2=.1)
for i in range(5): spike((random.uniform(-6, 6), random.uniform(7, 12), 1.5 + i * .8), random.uniform(.5, 1), random.uniform(.6, 1.2), 5, rock, r2=.2)
# winding road: slabs laid along a sine curve
for i in range(16):
    t = i / 15; x = -11 + 22 * t; y = -11 + 17 * t + 3 * math.sin(t * 5)
    block((x, y, 0), (2.6, 2.2, .12), road, rot=(0, 0, .4 + .2 * math.cos(t * 5)))
# company store with fallen sign
block((-8, 2, 0), (6, 4.4, 3.2), plank)
roofed((-8, 2, 3.2), 6.8, 5.2, .2, 1.4, tin)
block((-8, -.3, 0), (1.4, .2, 2.4), plank2); block((-5.4, -.3, 1.2), (1.2, .15, 1.2), plank2)
block((-10.6, -.3, 1.2), (1.2, .15, 1.2), plank2)
for i in range(5): block((-8 + (i - 2) * .9, -.45, 1.2), (.1, .1, 1.2), plank2)
block((-8, -.5, 3.6), (5, .15, 1.1), plank2); block((-8, -.6, 3.9), (.5, .1, .5), plank2)
block((-11.5, -1.8, .1), (5, .15, 1.1), plank2, rot=(0, 0, .5)); block((-10, -1.4, .1), (.5, .15, .5), plank2, rot=(0, 0, .5))
glim('POINT', (-8, -2.5, 1.6), (.7, .9, 1), 120)
# shuttered cabins
for i, (x, y, r) in enumerate(((-1, -6, .1), (5, -4, -.2), (9, 3, .3), (-2, 6, .0), (6, 8, -.1))):
    block((x, y, 0), (4.2, 3.4, 2.6), plank if i % 2 else plank2)
    roofed((x, y, 2.6), 4.8, 4, .2, 1.2, tin, rot=(0, 0, r))
    block((x, y - 1.72, 0), (1.2, .12, 2.1), plank2)
    block((x + 1.4, y - 1.72, 1.1), (1, .12, 1), plank2)
    for k in range(4): block((x + 1.4, y - 1.8, .9 + k * .3), (1.1, .06, .1), plank)
    block((x + 1.4, y - 1.85, 1.1), (.1, .06, 1), plank2, rot=(0, .5, 0))
    block((x - 1.3, y + .5, 3.6), (.5, .5, 1.2), tin)
# rusted ore cart on rails
for k in range(7):
    block((-2.5 + k * .9, -9.5, .1), (.25, .25, .25), tin)
for sy in (-.55, .55): rail((-3.5, -9.5 + sy, .3), (3.5, -9.5 + sy, .3), .1, rust)
for i in range(5):
    block((-2.5 + i * 1.1, -9.5, .3), (.2, 1.6, .12), plank2)
block((-.3, -9.5, .6), (3, 1.7, .5), rust); block((-.3, -9.5, 1.1), (3.1, 1.8, .5), rust)
block((.2, -9.5, 1.5), (1.6, 1.2, .35), rock)
for dx in (-.9, .9):
    for sy in (-1, 1): spike((-.3 + dx, -9.5 + sy * .95, .6), .5, .2, 8, tin).rotation_euler = (math.pi / 2, 0, 0)
# ghost lantern on a post, the only light that works
block((2, -3, 0), (.25, .25, 4), plank2)
block((2, -3, 4), (.8, .8, .9), ghost)
glim('POINT', (2, -3, 4.4), (.4, 1, .9), 900)
glim('SUN', (-24, -12, 8), (.55, .7, 1), 4, (0, 0, 2))
glim('SUN', (20, 20, 10), (.6, .5, .9), 2, (0, 0, 2))
w = bpy.data.worlds.new("moon"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .018, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((12, -62, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
