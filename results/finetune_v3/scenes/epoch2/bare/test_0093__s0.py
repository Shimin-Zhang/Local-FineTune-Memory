import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1757)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def paint(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    M[name] = m
for k, c in dict(grass=(.12, .2, .06), dirt=(.28, .2, .12), plaster=(.42, .38, .3), roof=(.25, .12, .08), plank=(.3, .17, .08), dark=(.03, .03, .04),
                 iron=(.06, .06, .07), brass=(.65, .45, .1), white=(.5, .5, .48), pole=(.3, .3, .32), red=(.55, .06, .05), blue=(.1, .2, .5),
                 orange=(.7, .3, .05), gold=(.7, .5, .05), trunk=(.2, .12, .07), water=(.1, .3, .45)).items(): paint(k, c)
paint("window", (1, .7, .3), 9)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("x"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("x", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[m]); return o
def cube(at, w, d, h, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return make(bm, m, at, (0, 0, rz))
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def gable(at, w, d, h, m, over=.6):
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in ((-w / 2 - over, -d / 2 - over, 0), (w / 2 + over, -d / 2 - over, 0), (w / 2 + over, d / 2 + over, 0), (-w / 2 - over, d / 2 + over, 0), (-w / 2 - over, 0, h), (w / 2 + over, 0, h))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): bm.faces.new([a[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return make(bm, m, at)
def shine(at, rgb, w):
    L = bpy.data.lights.new("s", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
def sun(at, rgb, w, aim):
    L = bpy.data.lights.new("s", "SUN"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# the yard: a grassy square with a dirt patch, floating
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3.4)
for v in bm.verts:
    v.co.x *= 1.15
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.7
make(bm, "grass")
cyl((3, -6, 0), 3.4, .06, 9, "dirt")
# schoolhouse: plaster walls, plank skirt, shingled gable roof with a cupola and bell
cube((-2, 4, 0), 9, 6, .4, "plank")
cube((-2, 4, .4), 8.4, 5.4, 3.4, "plaster")
gable((-2, 4, 3.8), 8.4, 5.4, 2.6, "roof")
for i in range(5):
    cube((-5.6 + i * 1.8, 1.25, .4), .25, .12, 3.4, "plank")
cube((-2, 1.25, .4), 1.4, .15, 2.4, "dark"); cube((-2, 1.2, 2.8), 1.4, .15, .1, "plank")
for x in (-5.2, 1.2):
    cube((x, 1.25, 1.4), 1.3, .12, 1.5, "window"); cube((x, 1.2, 1.4), 1.5, .1, .12, "plank"); cube((x, 1.2, 2.9), 1.5, .1, .12, "plank")
    cube((x, 1.2, 1.4), .08, .1, 1.5, "plank")
shine((-5.2, .2, 2.0), (1, .65, .25), 220); shine((1.2, .2, 2.0), (1, .65, .25), 220)
cube((-2, 4, 6.4), 1.5, 1.5, 1.2, "plaster"); gable((-2, 4, 7.6), 1.5, 1.5, .9, "roof", .2)
cube((-2, 3.2, 6.8), .5, .1, .6, "window")
cyl((-2, 4, 8.4), .5, .8, 6, "brass", .12)
cube((-2, 4, 9.2), .1, .1, .4, "brass")
shine((-2, 3.0, 7.0), (1, .7, .3), 120)
# yard: water pump, flagpole, two outhouses, a bench, a path, a pile of leaves
cyl((4.5, -5.5, 0), .5, .2, 8, "iron"); cyl((4.5, -5.5, .2), .12, 2.0, 6, "iron")
cube((4.5, -5.5, 2.2), .5, .5, .5, "iron"); cube((5.6, -5.5, 1.9), 1.6, .18, .18, "iron"); cube((6.3, -5.5, 1.2), .12, .12, .8, "iron")
cube((6.3, -5.5, 1.0), .3, .3, .2, "water")
cyl((7, -1.5, 0), .12, 7.5, 6, "pole"); cube((7.5, -1.5, 6.4), 1.6, .06, 1.1, "red"); cube((7.5, -1.5, 6.9), 1.6, .06, .3, "white")
for i, (x, y) in enumerate(((-8.5, -2.5), (-8.0, 1.0))):
    cube((x, y, 0), 2.2, 1.8, 2.0, "plank"); gable((x, y, 2.0), 2.2, 1.8, .8, "roof", .2)
    cube((x, y - .95, .8), .9, .1, .9, "dark"); cube((x + .8, y - .95, 0), .1, .1, 1.4, "dark")
    for k in range(3): cube((x - .6 + k * .6, y - .95, 1.2), .06, .06, .7, "plank")
for i in range(7):
    a = i / 6; px, py = -2 + 5 * a, 1.2 - 6.5 * a + 1.5 * math.sin(a * 3)
    cube((px, py, 0), 1.4, 1.0, .06, "dirt", a)
cube((0, -2, 0), 3, .5, .5, "plank"); cube((0, -2, .5), 3, .12, .5, "plank")
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(3, 12)
    x, y = math.cos(a) * r * 1.1, math.sin(a) * r * .85 - 1
    if abs(x + 2) < 5.5 and 0.5 < y < 7.5: continue
    cyl((x, y, 0), .18, 2.4, 5, "trunk", .12)
    for j, c in enumerate(("orange", "gold", "red")):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.9, 1.3))
        for v in bm.verts: v.co *= random.uniform(.85, 1.15)
        make(bm, c, (x + random.uniform(-.3, .3), y + random.uniform(-.3, .3), 3.2 + j * .5))
for i in range(14):
    x, y = random.uniform(-10, 10), random.uniform(-9, 8)
    if abs(x + 2) < 5.5 and 0 < y < 7.5: continue
    cyl((x, y, 0), .35, .08, 5, ("orange", "gold", "red")[i % 3])
sun((-28, -14, 11), (1, .72, .4), 5.5, (0, 0, 2)); sun((22, 26, 12), (.5, .6, 1), 2.2, (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((14, -56, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
