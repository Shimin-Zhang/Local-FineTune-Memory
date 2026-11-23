import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1068)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
P = {}
def tint(k, rgb, glow=0, rough=.6):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow:
        n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    P[k] = m
tint("snow", (.55, .65, .8)); tint("ice", (.2, .55, .75), rough=.2); tint("ice2", (.35, .65, .9), rough=.2)
tint("fall", (.3, .85, .95), 1.2); tint("throne", (.5, .9, 1), 3); tint("drift", (.8, .88, 1), .3)
tint("aurora", (.2, 1, .5), 1.2); tint("aurora2", (.5, .2, 1), 1.2); tint("dark", (.04, .1, .2))
def mesh(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("i"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("i", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(P[k]); return o
def prism(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, k, at, rot)
def block(at, w, d, h, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mesh(bm, k, at, (0, 0, rz))
def drift(at, r, k, sq=.35):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.9, 1.3), v.co.y * random.uniform(.9, 1.3), v.co.z * sq))
    return mesh(bm, k, at)
def beam(kind, rgb, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = rgb; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# snowfield base with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
mesh(bm, "snow")
# open throne court: a raised octagonal dais with a glowing ice throne
prism((0, 1, 0), 5.2, .5, 8, "ice2"); prism((0, 1, .5), 4.4, .5, 8, "ice")
prism((0, 3.2, 1.0), 1.2, 2.2, 6, "throne", r2=.9); block((0, 3.2, 3.2), 2.0, .3, .3, "throne")
for sx in (-1, 1): block((sx * 1.1, 3.2, 1.0), .35, .35, 1.6, "throne")
block((0, 2.2, 1.0), 1.6, .5, .3, "throne")
for i in range(4): block((0, 1.0 - i * .6, 1.0 - i * .25), 1.6, .6, .25 + i * .25, "ice2")
# slender spires around the court: tall tapered cones, some with a second tier
for i in range(10):
    a = i * math.pi / 5 + .3; r = 8.4
    h = random.uniform(6, 11)
    prism((r * math.cos(a), 1 + r * math.sin(a), 0), 1.0, h, 5, "ice" if i % 2 else "ice2", r2=.05)
    prism((r * math.cos(a), 1 + r * math.sin(a), 0), 1.5, .6, 5, "ice2")
    if i % 3 == 0: prism((r * math.cos(a), 1 + r * math.sin(a), h * .6), .55, h * .4, 5, "ice2", r2=.04)
# frozen waterfalls as walls: layered icicle sheets hanging between spires, with a dark gap behind
for i in range(14):
    a = .45 + i * .15; r = 7.0
    x, y = r * math.cos(a), 1 + r * math.sin(a)
    h = random.uniform(2.5, 5.0)
    block((x, y, 0), 1.0, .25, h, "fall", a + math.pi / 2)
    for k in range(3):
        prism((x + (k - 1) * .3, y, h - .1), .13, random.uniform(.6, 1.4), 4, "fall", r2=.02, rot=(math.pi, 0, 0))
    block((x, y, h), 1.2, .4, .3, "ice2", a + math.pi / 2)
# the ring of glittering snowdrifts, larger than life, scattered with ice crystals
for i in range(12):
    a = i * math.pi / 6 + random.uniform(-.1, .1); r = 10.6 + random.uniform(-.5, .8)
    drift((r * math.cos(a), 1 + r * math.sin(a) * .9, 0), random.uniform(1.4, 2.2), "drift")
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(2.5, 12)
    prism((r * math.cos(a), 1 + r * math.sin(a), 0), .2, random.uniform(.5, 1.2), 4, "ice", r2=.02)
# aurora curtains high behind the palace: ribbons of green and violet light
for j, (k, z) in enumerate((("aurora", 15.5), ("aurora2", 17.0), ("aurora", 18.5))):
    for i in range(11):
        x = -10 + i * 2.0; y = 11.5 + j * .5
        block((x, y, z + math.sin(i * .7) * .8), 2.1, .08, 2.2, k).rotation_euler.x = -.2
beam("POINT", (.3, .9, 1), 1800, (0, 1, 3.5)); beam("POINT", (.3, .9, 1), 500, (0, 8, 2))
beam("SUN", (.55, .75, 1), 3.5, (-22, -16, 12), (0, 1, 3)); beam("SUN", (.4, 1, .6), 2.5, (18, 22, 14), (0, 1, 3))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 3, 8)); co.location = t + Vector((8, -66, 44))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
