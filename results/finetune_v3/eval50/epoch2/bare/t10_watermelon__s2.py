import bpy, bmesh, math, random
from mathutils import Vector
random.seed(542)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0, rough=.8):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
grass, soil, rind, stripe, stripe2 = tone((.08, .2, .08)), tone((.2, .12, .08)), tone((.1, .45, .12)), tone((.04, .2, .07)), tone((.12, .5, .15))
flesh, seed, rind2, stem, leaf = tone((.9, .12, .2), 1.6, .5), tone((.03, .02, .02)), tone((.8, .9, .75)), tone((.15, .3, .1)), tone((.1, .35, .12))
lamp = tone((1, .85, .5), 12)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blob(r, m, at, rot=(0, 0, 0), jit=.04, sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit))) * r
    return put(bm, m, at, rot)
def stick(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return put(bm, m)
def glow(kind, rgb, w, at, aim=None):
    L = bpy.data.lights.new("g", kind); L.color, L.energy = rgb, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=10, depth=2.2)
for v in bm.verts:
    v.co.z -= 1.1
    if v.co.z < 0: v.co += Vector((random.uniform(-1.3, 1.3), random.uniform(-1.3, 1.3), random.uniform(-1.4, .2)))
    else: v.co.z += random.uniform(-.1, .1)
put(bm, grass)
# the melon: a striped ball, each stripe a patch of a dark or light green, drawn on a faceted sphere
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=7, radius=3.0)
for f in bm.faces:
    c = f.calc_center_median(); k = int((c.x + c.y * .5) * 1.6)
    f.material_index = (k % 2) + 1
melon = put(bm, rind); melon.data.materials.append(stripe); melon.data.materials.append(stripe2)
melon.location = (0, 0, 2.9); melon.scale = (1.0, 1.0, .85)
# a cut wedge standing beside it: rind, white pith, glowing red flesh and black seeds
w = bmesh.new(); bmesh.ops.create_cone(w, cap_ends=True, segments=6, radius1=1.0, radius2=1.0, depth=1.9)
for v in w.verts: v.co.z += .95
wedge = put(w, rind2, (-5.6, -3.6, .05), (0, math.pi / 2, -.5))
f = bmesh.new(); bmesh.ops.create_cone(f, cap_ends=True, segments=6, radius1=.9, radius2=.9, depth=1.9)
for v in f.verts: v.co.z += .95
flesh = put(f, flesh, (-5.6, -3.6, .1), (0, math.pi / 2, -.5)); glow("POINT", (1, .2, .3), 450, (-5.6, -3.6, 1.4))
for i in range(5):
    stick((-6.3 + i * .35, -3.6 + i * .17 - .08, .15), (-6.3 + i * .35, -3.6 + i * .17 + .08, .15), .1, seed)
# stem, tendril and a leaf
stick((0, 0, 5.4), (.2, .1, 6.4), .22, stem); stick((.2, .1, 6.4), (.6, .4, 6.9), .15, stem)
stick((.4, 0, 5.2), (1.6, .5, 5.6), .08, stem)
blob(.55, leaf, (2.4, .8, .15), (0, 0, .5), .2, 1)
# string lights on two stakes, and a few pebbles
for sx in (-1, 1):
    stick((sx * 6.5, 3.5, 0), (sx * 6.5, 3.5, 3.6), .15, soil)
    blob(.2, lamp, (sx * 6.5, 3.5, 3.7), jit=0)
    glow("POINT", (1, .85, .5), 380, (sx * 6.5, 3.0, 3.4))
for i in range(9):
    x = -6 + i * 1.5; z = 3.5 - 1.0 * math.sin(math.pi * (i + .5) / 9)
    blob(.2, lamp, (x, 3.5, z), jit=0); stick((x - .75, 3.5, z + .5), (x, 3.5, z), .03, soil); stick((x, 3.5, z), (x + .75, 3.5, z + .5), .03, soil)
for i in range(10): blob(random.uniform(.25, .5), soil, (random.uniform(-9, 9), random.uniform(-8, 8), .1), jit=.3)
glow("SUN", (1, .6, .3), 5, (-24, -16, 9), (0, 0, 2)); glow("SUN", (.4, .5, 1), 2.2, (22, 20, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.8)); co.location = t + Vector((14, -40, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
