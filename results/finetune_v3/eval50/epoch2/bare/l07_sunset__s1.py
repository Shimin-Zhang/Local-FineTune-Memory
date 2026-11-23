import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(757)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def col(c, e=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .95
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
grass, hill, bark, leaf1, leaf2, rock, cloud = col((.1, .15, .07)), col((.14, .13, .07)), col((.2, .12, .08)), col((.3, .15, .06)), col((.38, .2, .08)), col((.28, .24, .22)), col((.5, .3, .3))
sun, lamp, stone, path = col((1, .35, .05), 25), col((1, .6, .2), 12), col((.35, .3, .26)), col((.3, .22, .15))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def bx(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = V((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cy(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def ball(at, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mk(bm, m, at)
def light(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
def hill_h(x, y): return max(0, 4.2 * (1 - math.hypot(x, y) / 12.5)) ** .9
# floating base: rough disc, tapering to a point
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=13, depth=3)
for v in bm.verts:
    v.co.x *= 1.25
    if v.co.z < 0: v.co += V((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1, .3)))
    v.co.z -= 1.5
mk(bm, grass)
# the hill: a faceted dome of grass
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=12.5, radius2=.3, depth=4.2)
for v in bm.verts:
    if v.co.z > 0: v.co += V((random.uniform(-.5, .5), random.uniform(-.5, .5), random.uniform(-.2, .2)))
    v.co.z += 2.1
mk(bm, hill)
# winding path up the hill, a bench and a lantern post
for k in range(11):
    t = k / 10; a = 2.2 + 1.6 * math.sin(t * 3)
    r = 11.5 - 7 * t; x, y = r * math.cos(a), r * math.sin(a)
    bx((x, y, hill_h(x, y) - .1), (1.8, 1.3, .2), path, (0, 0, a + 1.57))
bx((3.5, -4.5, hill_h(3.5, -4.5)), (2.2, .6, .5), bark, (0, 0, .6)); bx((3.5, -4.8, hill_h(3.5, -4.8) + .5), (2.2, .15, .8), bark, (0, 0, .6))
bx((7, -6.5, hill_h(7, -6.5)), (.2, .2, 3), bark); bx((7, -6.5, hill_h(7, -6.5) + 3), (.7, .7, .8), lamp); light("POINT", (1, .6, .2), 300, (7, -6.5, hill_h(7, -6.5) + 3.6))
# trees on the slope: trunk plus two or three blobs, all leaning to the light
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(3, 11)
    x, y = r * math.cos(a), r * math.sin(a)
    if abs(math.atan2(y, x) - 2.2) < .45 and r > 8: continue
    z = hill_h(x, y); h = random.uniform(2.2, 3.4); lean = .25
    cy((x, y, z), .35, h, 5, bark, .2, (lean * .6, lean, 0))
    for k in range(3):
        ball((x + lean * h * (k - 1) * .5, y + random.uniform(-.5, .5), z + h * (.8 + .15 * k)), random.uniform(1.0, 1.5), random.choice((leaf1, leaf2)), .8)
# rocks, tufts and a cairn
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(1, 12.5)
    ball((r * math.cos(a), r * math.sin(a), hill_h(r * math.cos(a), r * math.sin(a)) + .1), random.uniform(.3, .8), rock, .7)
for i in range(5):
    t = i / 4; x, y = 1.5 * math.cos(t * 3), 1.5 * math.sin(t * 3)
    ball((x, y, hill_h(x, y) + .3 + i * .3), .5 - i * .06, stone, .8)
# the low sun: a huge glowing disc behind the hill, with a haze
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=3.4, radius2=3.4, depth=.6)
mk(bm, sun, (-16, 8, 3.6), (0, math.pi / 2, 0))
for i in range(3): ball((-16 + i * 1.5, 8 + i * .5, 5.2 + i * .6), 1.8 - i * .3, cloud, .35)
# sunset: orange key from the sun's side, magenta rim from the other
light("SUN", (1, .5, .15), 6, (-24, 12, 6), (0, 0, 2)); light("SUN", (.7, .3, .6), 2.2, (22, -14, 10), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = V((-2, 2, 3)); co.location = t + V((14, -60, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
