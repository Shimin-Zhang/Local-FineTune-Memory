import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1766)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
P = {}
def paint(k, c, e=0, r=.85):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    P[k] = m
paint("sea", (.03, .13, .17), 0, .2); paint("sand", (.3, .22, .14)); paint("rock", (.14, .13, .14))
paint("post", (.2, .12, .07)); paint("plank", (.3, .2, .1)); paint("hull", (.1, .2, .25))
paint("sail", (.7, .65, .55)); paint("roof", (.2, .06, .05)); paint("foam", (.5, .55, .6), 0, .5)
paint("win", (1, .7, .3), 14); paint("lamp", (1, .8, .4), 20)
for i, c in enumerate(((.8, .15, .1), (.8, .5, .05), (.15, .45, .5), (.7, .25, .4), (.2, .5, .2), (.75, .75, .7), (.85, .4, .1))): paint("h%d" % i, c)
def add(bm, k, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = loc; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(P[k]); return o
def blk(k, x, y, z, w, d, h, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * f, v.co.y * d * f, (v.co.z + .5) * h))
    return add(bm, k, (x, y, z), (0, 0, rz))
def post(k, x, y, z, r, h, n=5, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, k, (x, y, z))
def gable(k, x, y, z, w, d, h):
    bm = bmesh.new(); a = [bm.verts.new(p) for p in ((-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0), (-w / 2, 0, h), (w / 2, 0, h))]
    for f in ((0, 1, 2, 3), (0, 1, 5, 4), (2, 3, 4, 5), (0, 3, 4), (1, 2, 5)): bm.faces.new([a[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return add(bm, k, (x, y, z))
def light(kind, c, w, p, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
add(bm, "sea")
# headland with beach and rocks at the back
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=8, radius2=3.5, depth=4.2)
for v in bm.verts: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), 0)); v.co.z += 2.1
add(bm, "rock", (-2, 12.5, 0))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5.5, radius2=4, depth=.8)
for v in bm.verts: v.co += Vector((random.uniform(-.5, .5), random.uniform(-.5, .5), 0)); v.co.z += .4
add(bm, "sand", (-2, 8.5, 0))
for i in range(10):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.4, 1))
    for v in bm.verts: v.co.z *= .6
    add(bm, "rock", (random.uniform(-12, 12), random.uniform(11, 13.5), .1))
# the plank walkway on trestles, with a zigzag, running out over the water
for i in range(11):
    x = 8 - i * 1.7; y = 5.2 - (i % 2) * .5
    blk("plank", x, y, 1.5, 1.9, 1.6, .12, .0)
    for sx in (-.8, .8): post("post", x + sx, y, 0, .09, 1.5, 4)
for x, y in ((5.5, 4.6), (2.5, 4.9), (-.5, 4.6), (-3.5, 4.9), (-6.5, 4.6)):
    blk("post", x, y, 1.6, .08, 1.5, .7); blk("post", x, y, 2.3, .08, 1.5, .08)
# seven palafitos on stilts, each with a ladder, a roof and a lit window
for i in range(7):
    x = 7 - i * 2.4; y = 2.6 - (i % 2) * 1.3; c = "h%d" % (i % 7)
    for sx in (-1, 1):
        for sy in (-1, 1): post("post", x + sx * 1.1, y + sy * .9, 0, .12, 1.8, 5)
    blk("post", x, y, .8, 2.0, .1, .1)
    blk(c, x, y, 1.8, 2.5, 2.0, 1.6, 0, .97)
    blk("plank", x, y, 1.65, 2.8, 2.3, .15)
    gable("roof", x, y, 3.4, 2.9, 2.5, 1.1)
    blk("win", x, y - 1.03, 2.2, .7, .06, .6); blk("win", x + .8, y - 1.0, 2.2, .4, .06, .5)
    blk("post", x - .5, y - 1.05, 1.8, .3, .05, .8)
    for s in (-.3, .3): blk("post", x + s, y - 1.35, 0, .05, .05, 1.7)
    for z in range(5): blk("post", x, y - 1.35, .2 + z * .32, .6, .05, .05)
    light("POINT", (1, .65, .25), 90, (x, y - 1.7, 2.6))
# a small boat under each walkway gap and one moored alongside
for bx, by, rz in ((6, 1.5, .1), (3, 1.2, -.1), (0, 1.5, .05), (-3, 1.2, -.15), (-6, 1.5, .1), (3.5, -2.2, 1.4)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * 2.0, v.co.y * .7 * (1 - .6 * abs(v.co.x)), (v.co.z + .5) * .4))
    add(bm, "hull", (bx, by, .05), (0, 0, rz))
    blk("plank", bx, by, .2, .5, .5, .08, rz)
    post("post", bx + .5, by, .3, .03, 1.6, 4); blk("sail", bx + .15, by, .7, .7, .04, .9, 0, .3)
# tide foam lines, a buoy and a lamp post at the shore end
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(7, 12)
    blk("foam", math.cos(a) * r, math.sin(a) * r * .9, .02, random.uniform(1, 2), .15, .04, a + 1.57)
post("h0", -9, 5, 0, .22, .8, 6); post("lamp", -9, 5, .8, .2, .3, 6); light("POINT", (1, .8, .4), 400, (-9, 5, 1.4))
light("SUN", (1, .55, .3), 5.5, (-26, -16, 8), (0, 0, 2)); light("SUN", (.3, .5, .8), 2.2, (24, 24, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 3, 2)); co.location = t + Vector((16, -60, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
