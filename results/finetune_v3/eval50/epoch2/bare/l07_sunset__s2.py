import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1029)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(c, e=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = .9
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
grass, grass2, bark, leaf1, leaf2, rock, rock2, soil = (tone((.1, .16, .06)), tone((.17, .2, .07)), tone((.14, .09, .07)), tone((.3, .12, .06)),
    tone((.38, .2, .05)), tone((.28, .22, .2)), tone((.2, .17, .18)), tone((.12, .08, .06)))
sunm, cloud, flower = tone((1, .5, .08), 14), tone((.5, .25, .25)), tone((.9, .85, .4))
def put(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def block(p, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return put(bm, m, p, (0, 0, rz))
def stem(p, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, p)
def lump(p, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return put(bm, m, p)
def glow(kind, p, c, w, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
put(bm, soil)
# the hill: a faceted mound of stacked discs, with a flat top
for i in range(7):
    r = 9.5 - i * 1.1
    stem((0, 0, 0), r, .55, 9, grass if i % 2 else grass2, r - .15).location.z = i * .55 - .05
# a winding path of flat stones up the slope
for i in range(9):
    a = .5 + i * .12; r = 8.6 - i * .95
    block((math.cos(a) * r, math.sin(a) * r * .9, i * .55 + .1), (1.1, .8, .12), rock, a + 1.5)
# simple trees: tapered trunk, stacked lumps, each with a long shadow toward the viewer
def tree(x, y, h, k):
    z = .0
    stem((x, y, z), .28 * k, h * .5, 6, bark, .18 * k)
    for j in range(3):
        lump((x + random.uniform(-.3, .3), y, h * .5 + j * h * .18), 1.3 * k * (1 - j * .22), (leaf1, leaf2)[(j + int(x)) % 2], .85)
    # long shadow: a dark flat wedge stretched away from the sun
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=.9 * k, radius2=.2, depth=h * 1.6)
    for v in bm.verts: v.co.z = 0
    put(bm, soil, (x + 1.2, y - 2.2, .08), (0, 0, 0))
for x, y, h, k in ((-5, 3, 4.2, 1.1), (-1, 6, 5, 1.3), (4.5, 4, 3.8, 1), (6, -2, 3.2, .9), (-7, -2, 3.4, .95), (0, -6, 3, .85)):
    tree(x, y, h, k)
# rocks, tufts and a few flowers
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(2, 11)
    lump((math.cos(a) * r, math.sin(a) * r, .1), random.uniform(.3, .8), rock if i % 2 else rock2, .7)
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(3, 11)
    stem((math.cos(a) * r, math.sin(a) * r, 0), .05, .5, 4, grass2); lump((math.cos(a) * r, math.sin(a) * r, .55), .16, flower, 1)
# the low sun: a big glowing disc just above the rim, with a warm lens glow
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=2.4)
put(bm, sunm, (0, -13.2, 2.6))
glow("POINT", (0, -12, 3.5), (1, .55, .12), 2500)
# clouds: flat pink-orange slabs
for x, y, z, s in ((-9, -5, 9.5, 3.5), (6, -8, 11, 4), (10, 4, 8.5, 3), (-4, 8, 12, 3.2)):
    block((x, y, z), (s * 2.2, s, .5), cloud, random.uniform(0, 3), .8)
# sunset: strong orange key from the front-right, low; violet rim from behind
glow("SUN", (24, -20, 7), (1, .5, .15), 7, (0, 0, 2))
glow("SUN", (-14, 22, 12), (.55, .3, .8), 2.4, (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, -1, 3.5)); co.location = t + Vector((-10, -56, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
