import bpy, bmesh, random, math
from mathutils import Vector
random.seed(882)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def clr(rgb, em=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
cliff, cliff2, river, concrete, concrete2 = clr((.12, .11, .11)), clr((.09, .09, .1)), clr((.03, .12, .15)), clr((.45, .45, .47)), clr((.3, .3, .33))
foam, steel, pylon, wire, roof = clr((.7, .85, .9)), clr((.15, .16, .18)), clr((.5, .5, .52)), clr((.03, .03, .03)), clr((.2, .12, .1))
glass, lamp, pine = clr((.2, .45, .6)), clr((1, .75, .35), 12), clr((.04, .12, .08))
def part(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(m, x, y, z, w, d, h, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return part(bm, m, (x, y, z), (0, 0, rz))
def cyl(m, x, y, z, r, h, n=8, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return part(bm, m, (x, y, z))
def beam(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return part(bm, m)
def shine(x, y, z, w, c=(1, .75, .35)):
    L = bpy.data.lights.new("s", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = (x, y, z); sc.collection.objects.link(o)
# valley floor: rock base, river along the front, banks either side
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 18 + random.uniform(-2, 2), v.co.y * 13 + random.uniform(-2, 2), -4 + random.uniform(-1, .5)))
    else: v.co = Vector((v.co.x * 24, v.co.y * 18, 0))
part(bm, cliff2)
blk(river, 0, -6.5, .02, 24, 5, .1)
for s in (-1, 1): blk(cliff, s * 7.6, -6.5, 0, 8.8, 5, .15)
# the valley walls: stepped rock masses behind the dam, narrowing toward the back
for i, (w, h, y) in enumerate(((24, 7, 3), (20, 12, 6.5), (14, 16, 9.5))):
    for s in (-1, 1):
        blk(cliff if i % 2 else cliff2, s * (w / 2 + 1.5), y, 0, 7, 4.2, h, random.uniform(-.05, .05), .8)
# the arch dam: a curved wall of blocks, thick at the foot, with a crest road
N = 17
for i in range(N):
    t = (i - (N - 1) / 2) / ((N - 1) / 2) * 1.25
    x, y = 8 * math.sin(t), -1 + 2.6 * (1 - math.cos(t)) * -1
    h = 11 - 1.6 * abs(t) ** 2 * 2
    blk(concrete if i % 2 else concrete2, x, y, 0, 1.1, 1.3, h, t, .82)
blk(concrete2, 0, -1, 11, 16.5, 1.8, .5)
for i in range(7): blk(lamp, -7.5 + i * 2.5, -1, 11.5, .3, .3, .3)
# spillway at the right end: chute down the face, white water, mist at the foot
blk(concrete2, 9.8, -2.3, 8.5, 2.6, 1.4, 3.4, 0, .8)
for i in range(6):
    blk(foam, 9.8, -2.3 - i * .5, 8.0 - i * 1.25, 1.8 - i * .12, .5, .35, 0, .8)
for i in range(5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.6, 1.0))
    part(bm, foam, (9.8 + random.uniform(-.8, .8), -5.5 + random.uniform(-.5, .5), 1.0 + random.uniform(0, 1.5)))
# power house at the base, with glowing windows, a bus bar and a transformer
blk(concrete, 0, -4.2, 0, 7, 3, 2.6); blk(roof, 0, -4.2, 2.6, 7.4, 3.4, .3, 0, .9)
for i in range(5): blk(glass, -2.4 + i * 1.2, -5.75, 1.0, .7, .1, .9)
blk(steel, 4.5, -5, 0, .3, .3, 2.2); blk(steel, 5.4, -5, 0, .3, .3, 2.2); beam(steel, (4.5, -5, 2.2), (5.4, -5, 2.2), .15)
cyl(steel, 5.0, -4.5, 0, .5, 1.0, 6, .4); shine(0, -6.4, 1.5, 500, (.4, .8, 1))
# pylons marching away over the far bank, wires sagging between them
for i in range(5):
    x = -6 + i * 3.2; y = 5.5 + i * 1.0
    for sx in (-.5, .5): beam(pylon, (x + sx, y, 0), (x + sx * .3, y, 6.5), .18)
    beam(pylon, (x - .6, y, 6.5), (x + .6, y, 6.5), .15); beam(pylon, (x - .8, y, 5.6), (x + .8, y, 5.6), .12)
    for z in (6.5, 5.6): beam(wire, (x - .8, y, z), (x + .8, y, z), .1)
for i in range(4):
    for z in (6.5, 5.6):
        a = Vector((-6 + i * 3.2 + .8, 5.5 + i * 1.0, z)); b = Vector((-6 + (i + 1) * 3.2 - .8, 5.5 + (i + 1) * 1.0, z))
        mid = (a + b) / 2; mid.z -= .8
        beam(wire, a, mid, .05); beam(wire, mid, b, .05)
# a few pines on the near bank and boulders in the river
for i in range(12):
    x, y = random.choice((-1, 1)) * random.uniform(5.5, 10.5), random.uniform(-9, -2)
    if abs(x) < 3 and y < -3: continue
    for k in range(2): cyl(pine, x, y, .5 + k * 1.0, 1.0 - k * .35, 1.6, 6, .1)
for i in range(5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.3, .6))
    part(bm, cliff, random.uniform(-3, 3), random.uniform(-8, -5), .15)
for c, e, p in (((.55, .65, 1), 4.5, (-26, -14, 9)), ((1, .5, .3), 2.5, (24, 20, 12))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("sun", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 5)); co.location = t + Vector((10, -72, 42))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
