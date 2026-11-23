import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1597)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
V = {}
def alloy(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .5
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    V[name] = m
for k, c in (("cloudA", (.55, .42, .1)), ("cloudB", (.45, .33, .09)), ("hull", (.55, .55, .6)), ("hull2", (.3, .32, .38)), ("sail", (.7, .2, .12)),
             ("dark", (.04, .04, .06)), ("mast", (.5, .12, .1)), ("blimp", (.8, .75, .6)), ("wire", (.25, .25, .3))): alloy(k, c)
alloy("win", (.3, .9, 1), 8); alloy("win2", (1, .6, .2), 8); alloy("beacon", (1, .1, .05), 20); alloy("solar", (.1, .3, .9), 1.5)
def emit(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(V[k]); return o
def slab(at, d, k, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        s = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * s, v.co.y * d[1] * s, (v.co.z + .5) * d[2]))
    return emit(bm, k, at, rot)
def strut(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return emit(bm, k)
def tube(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return emit(bm, k, at, rot)
def orb(at, r, k, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return emit(bm, k, at)
def glow(at, rgb, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# the deck: a rough floating slab of cloud, tapering to a dark underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=7, radius2=15, depth=3.5)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.2, .4)))
    else: v.co.z += random.uniform(-.15, .15)
    v.co.z -= 1.75
emit(bm, "cloudB")
for i in range(11):
    a = random.uniform(0, 6.28); r = random.uniform(6, 13)
    orb((math.cos(a) * r, math.sin(a) * r, random.uniform(-.3, .4)), random.uniform(1.2, 2.2), "cloudA", (1.6, 1.1, .45))
# the habitat dome: a cut icosphere, ribs, glowing windows, a base ring
orb((0, 0, 4.2), 5.2, "hull", (1, 1, .85))
tube((0, 0, 0), 5.5, .8, 10, "hull2"); tube((0, 0, .8), 5.2, .3, 10, "dark")
for i in range(10):
    a = i * math.pi / 5
    for s in (-1, 1):
        x, y = math.cos(a) * 5.1, math.sin(a) * 5.1
        slab((x, y, 0), (.35, .35, 1.0), "hull2")
        p0 = Vector((x, y, .9)); p1 = Vector((x * .5, y * .5, 4.2 + 4.3 * .85 * math.cos(0) * 0 + 0)); p1 = Vector((x * .5, y * .5, 8.4))
        strut(p0, p1, .22, "hull2")
    for h in (2.2, 4.6):
        r = 5.2 * math.sin(math.acos((4.2 - h) / 5.2 * 1.0)) * 1.0
        for j in range(10):
            a = j * math.pi / 5 + math.pi / 10
            x, y = math.cos(a) * r * .98, math.sin(a) * r * .98
            if j % 2 == 0 and h == 2.2: slab((x, y, h), (.9, .12, .7), "win", rot=(0, 0, a + math.pi / 2))
for i in range(3):
    a = i * 2.1 + .4
    slab((math.cos(a) * 4.9, math.sin(a) * 4.9, 4.0), (.8, .1, .9), "win2", rot=(0, 0, a + math.pi / 2))
glow((0, -6.5, 2.5), (.3, .9, 1), 700); glow((0, 0, 9.5), (.3, .9, 1), 300)
# the catwalk: a ring of posts and deck slabs with rails, and a bridge to the mast
for i in range(20):
    a = i * math.pi / 10
    x, y = math.cos(a) * 7.4, math.sin(a) * 7.4
    tube((x, y, 0), .15, 1.6, 5, "hull2")
    slab((x, y, 1.6), (2.0, 1.6, .12), "hull", rot=(0, 0, a))
    slab((math.cos(a) * 8.3, math.sin(a) * 8.3, 2.2), (.1, 1.6, .08), "hull2", rot=(0, 0, a))
slab((0, -7.4, 1.6), (1.6, 3.0, .12), "hull"); slab((0, -9.2, 1.6), (1.6, 2.2, .12), "hull", rot=(0, 0, 0))
for i in range(3): slab((0, -8.2 - i * .6, 2.2), (.08, .08, .08), "hull2")
# docking mast: a tall tapered column with a ring pad, beacon, and a ladder of crossbars
tube((0, 0, 0), 1.0, 3.0, 8, "hull2", .7); tube((0, 0, 3.0), .45, 11, 6, "mast", .25)
for z in (3.5, 6.5, 9.5): tube((0, 0, z), .8 - z * .04, .35, 8, "hull")
for i in range(12): slab((0, 0, 1.0 + i * .85), (.12, .12, .12), "wire")
tube((0, 0, 14.0), .5, .6, 6, "dark"); orb((0, 0, 14.9), .5, "beacon")
glow((0, 0, 15.2), (1, .1, .05), 1500)
# solar sails: two booms from the catwalk, each carrying a striped sail on a frame
for s in (-1, 1):
    strut((s * 8.2, 0, 2.0), (s * 13.5, 0, 2.0), .18, "hull")
    for j in range(5):
        x = s * (9.0 + j * 1.0)
        slab((x, 0, 2.0), (.95, 3.4, .05), "sail" if j % 2 else "solar", rot=(0, 0, 0))
    for j in range(4):
        x = s * (9.5 + j * 1.0)
        strut((x, -1.7, 2.0), (x, 1.7, 2.0), .07, "wire")
# the blimp: a big hull, a gondola, fins, a mooring line to the catwalk
orb((-9, 6, 8.5), 2.6, "blimp", (1.7, .8, .8)); orb((-9, 6, 8.5), 2.6, "hull2", (1.7, .8, .8)).scale = (1, 1, .02)
slab((-9, 6, 5.2), (1.8, 1.0, .8), "hull2"); slab((-9, 5.5, 5.5), (.9, .08, .4), "win")
for s in (-1, 1): slab((-9 + s * 4.2, 6, 8.5), (.1, 1.6, 1.4), "hull2"); slab((-9 + s * 4.2, 6, 9.5), (.1, .8, .8), "hull2")
strut((-9, 6, 5.2), (-7.4, 7.4, 1.6), .06, "wire")
glow((-9, 5.0, 5.5), (1, .6, .2), 200)
# lights: a harsh pale sun low from the left, a dim orange rim from behind
for c, w, p in (((.9, .85, .7), 5, (-30, -14, 9)), ((1, .5, .2), 2.2, (22, 26, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .01, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 5)); co.location = t + Vector((20, -62, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
