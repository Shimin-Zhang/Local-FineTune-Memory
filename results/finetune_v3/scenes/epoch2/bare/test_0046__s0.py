import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1971)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
col = {}
def tint(k, c, e=0):
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = .9
    if e: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    col[k] = m
tint("sand", (.32, .24, .14)); tint("sea", (.03, .2, .22)); tint("foam", (.5, .6, .6)); tint("log", (.25, .15, .08))
tint("log2", (.17, .1, .06)); tint("thatch", (.35, .26, .12)); tint("thatch2", (.24, .18, .09)); tint("steel", (.4, .42, .45))
tint("flame", (1, .45, .08), 12); tint("hull", (.3, .17, .08)); tint("hull2", (.18, .1, .06)); tint("leaf", (.06, .22, .1))
tint("bark", (.12, .08, .06)); tint("rope", (.5, .4, .25)); tint("skin", (.5, .3, .2)); tint("cloth", (.6, .12, .08))
def put(bm, k, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(col[k]); return o
def plank(p, s, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, k, p, (0, 0, rz))
def log(p, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, k, p)
def stick(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return put(bm, k)
def lump(p, r, k, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return put(bm, k, p)
def fire(p, w):
    l = bpy.data.lights.new("f", "POINT"); l.color = (1, .5, .15); l.energy = w; l.shadow_soft_size = .5
    o = bpy.data.objects.new("f", l); o.location = p; sc.collection.objects.link(o)
# base: sand slab, a sea inlet at the front, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=13, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
put(bm, "sand")
plank((0, -9.4, .02), (15, 3.6, .1), "sea"); plank((0, -7.6, .02), (15, .5, .08), "foam")
# half-carved dugout on two cradle logs, tapered at the bow
for i in range(6):
    x = -3.6 + i * 1.45
    plank((x, 3.5, 1.1), (1.5, 2.6 - .08 * abs(i - 2.5), .9 + .06 * abs(i - 2.5)), "log" if i % 2 else "log2")
for y in (2.5, 4.5): log((-4.6, y, 0), .4, 7.6, 7, "bark").rotation_euler = (0, math.pi / 2, 0)
plank((0, 3.5, 2.0), (6.8, 1.4, .2), "log2")
# the adze: long haft, iron blade, and a stump with a torch
stick((-1.0, 2.0, 0), (-.2, 1.6, 2.6), .12, "log2"); plank((-.1, 1.5, 2.5), (.5, .12, .45), "steel", .5)
log((-3.0, 1.0, 0), .5, .8, 6, "bark"); log((-3.0, 1.0, .8), .2, .5, 5, "flame"); fire((-3.0, 1.0, 1.6), 250)
# wood shavings scattered on the sand
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(.5, 3.2)
    plank((-1 + r * math.cos(a), 1.2 + r * math.sin(a) * .6, 0), (random.uniform(.3, .7), .08, .03), "log", random.uniform(0, 3))
# thatched shed: open front, posts, sloped thatch
for x, y in ((-9.5, 4.5), (-6.5, 4.5), (-9.5, 7.5), (-6.5, 7.5)): log((x, y, 0), .15, 3.4, 5, "bark")
for i in range(4):
    plank((-8.0, 4.2 + i * 1.0, 3.4 - i * .25), (4.2, 1.1, .15), "thatch" if i % 2 else "thatch2")
plank((-8.0, 7.0, 1.5), (3.0, .3, 1.6), "log2"); plank((-8.0, 7.0, 0), (3.4, .8, .5), "log")
log((-9.2, 6.4, 0), .15, 1.4, 5, "bark"); log((-9.2, 6.4, 1.4), .25, .3, 6, "flame"); fire((-9.2, 6.4, 1.8), 180)
# finished canoe waiting at the water, ribs and a paddle
for i in range(9):
    x = -4.2 + i * 1.05
    plank((x, -6.6, .15), (1.1, 1.5 - .12 * abs(i - 4) + .05, .5 - .05 * abs(i - 4)), "hull" if i % 2 else "hull2")
plank((-1.2, -6.6, .65), (6.4, .5, .1), "hull2"); plank((-1.2, -6.6, .15), (6.0, .8, .1), "hull2")
stick((-1.2, -6.6, .7), (-1.2, -6.6, 1.6), .08, "log2"); plank((-1.2, -6.6, 1.5), (.6, .1, .1), "log2")
# a builder at the dugout, larger than life, with a torch in hand
log((2.4, 2.0, 0), .5, 1.6, 6, "cloth", .3); lump((2.4, 2.0, 1.9), .38, "skin"); stick((2.4, 2.0, 1.3), (1.2, 1.4, 2.2), .14, "skin")
stick((2.4, 2.0, 1.3), (3.2, 1.0, 1.6), .14, "skin"); log((3.2, 1.0, 1.6), .15, .4, 5, "flame"); fire((3.2, 1.0, 2.1), 200)
# palms and rocks at the back
for x, y, h in ((7, 8, 4.5), (10, 5, 3.6), (-10, 1, 3.8)):
    log((x, y, 0), .22, h, 5, "bark", .14)
    for k in range(6):
        a = k * 1.05; stick((x, y, h), (x + 1.8 * math.cos(a), y + 1.8 * math.sin(a), h - .6), .22, "leaf")
for i in range(6): lump((random.uniform(-11, 11), random.uniform(8, 10), .2), random.uniform(.4, .8), "bark", .7)
# golden hour: low amber key from the left, teal rim from behind
for c, e, p in (((1, .6, .3), 5, (-24, -10, 7)), ((.3, .7, .8), 2.2, (16, 20, 9))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = e
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
