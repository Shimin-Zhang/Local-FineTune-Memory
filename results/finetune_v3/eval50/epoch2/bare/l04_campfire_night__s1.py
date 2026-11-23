import bpy, bmesh, random, math
from mathutils import Vector
random.seed(539)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def mat(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
turf, bark, bark2, stone, pine, pine2, cloth, ember, flame, flame2, wood = (
    mat((.05, .08, .04)), mat((.2, .12, .07)), mat((.14, .08, .05)), mat((.2, .2, .22)), mat((.03, .12, .08)), mat((.02, .08, .07)),
    mat((.5, .1, .08)), mat((1, .25, .03), 14), mat((1, .5, .08), 16), mat((1, .85, .2), 18), mat((.25, .15, .08)))
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cone(at, r, h, n, m, r2=0.0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def box(at, sx, sy, sz, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, (v.co.z + .5) * sz))
    return make(bm, m, at, rot)
def log(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    return make(bm, m, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def rock(at, r, m, sq=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return make(bm, m, at)
def firelight(at, col, w):
    L = bpy.data.lights.new("f", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("f", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=7, radius2=7, depth=1.6)
for v in bm.verts:
    v.co.z -= .8
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.6, .2)))
    else: v.co.z += random.uniform(-.1, .1)
make(bm, turf)
# the fire: ring of stones, crossed logs, flames and embers
for k in range(11):
    a = k * math.tau / 11
    rock((math.cos(a) * 1.7, math.sin(a) * 1.7, .1), random.uniform(.35, .55), stone)
for k in range(6):
    a = k * math.tau / 6
    log((math.cos(a) * 1.5, math.sin(a) * 1.5, .3), (0, 0, .6), .16, wood)
for k, (r, h, m) in enumerate(((.9, 2.6, ember), (.7, 3.4, flame), (.45, 4.2, flame2))):
    cone((0, 0, .4), r, h, 6, m, r2=0, rot=(0, 0, k))
    cone((.25 * k, .2, .4), r * .7, h * .8, 5, m, r2=0)
for k in range(8): rock((random.uniform(-.9, .9), random.uniform(-.9, .9), .35), .1, flame2, 1)
firelight((0, 0, 1.6), (1, .45, .1), 1600); firelight((0, -1.2, .9), (1, .3, .05), 400)
# two log seats and a blanket
for a in (-2.6, 2.4):
    log((math.cos(a) * 3.4, math.sin(a) * 3.4, .55), (math.cos(a) * 4.8, math.sin(a) * 4.8, .55), .45, bark)
    log((math.cos(a + .05) * 3.5, math.sin(a + .05) * 3.5, .55), (math.cos(a + .05) * 4.9, math.sin(a + .05) * 4.9, .55), .3, bark2)
box((-3.3, 2.2, 0), 2.4, 2.4, .25, cloth, (0, 0, .5)); box((-3.3, 2.2, .25), 1.6, 1.6, .12, bark2, (0, 0, .5))
# campfire tripod with a pot and a lantern
for k in range(3):
    a = k * math.tau / 3 + .3
    log((math.cos(a) * 1.1, -4.4 + math.sin(a) * 1.1, 0), (math.cos(a) * .15, -4.4 + math.sin(a) * .15, 2.6), .08, bark)
cone((0, -4.4, 1.9), .6, .7, 7, mat((.05, .05, .06), rough=.4), r2=.5)
for k in range(3):
    a = k * 2.1
    log((math.cos(a) * 1.1, 4.6 + math.sin(a) * 1.1, 0), (math.cos(a) * .15, 4.6 + math.sin(a) * .15, 2.6), .08, bark)
cone((0, 4.6, 2.0), .55, .3, 6, flame2, r2=.55)
firelight((0, 4.6, 2.4), (1, .5, .1), 250)
# trees and boulders round the clearing
for k in range(11):
    a = random.uniform(0, math.tau); r = random.uniform(5.3, 6.4)
    if abs(a - math.pi / 2) < .5 and r < 6: continue
    x, y = math.cos(a) * r, math.sin(a) * r
    cone((x, y, 0), .25, 1.4, 5, bark2, r2=.2)
    for j in range(3): cone((x, y, 1.0 + j * 1.0), 1.5 - j * .35, 1.8, 7, pine if (k + j) % 2 else pine2, r2=.05)
for k in range(7):
    a = random.uniform(0, math.tau); r = random.uniform(3.2, 5)
    rock((math.cos(a) * r, math.sin(a) * r, 0), random.uniform(.4, .8), stone)
for col, w, at in (((.35, .45, 1), .8, (-22, -14, 9)), ((.4, .3, .8), .3, (18, 22, 12))):
    L = bpy.data.lights.new("moon", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("moon", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((6, -42, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
