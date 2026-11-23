import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1675)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
cl = {}
def clay(k, rgb, em=0):
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    cl[k] = m
clay("cliff", (.16, .12, .11)); clay("cliff2", (.11, .08, .08)); clay("mud", (.34, .22, .14)); clay("thatch", (.4, .3, .12))
clay("thatch2", (.3, .21, .09)); clay("wood", (.14, .08, .05)); clay("moss", (.08, .17, .07)); clay("cave", (.01, .005, .005))
clay("flame", (1, .5, .1), 14); clay("maskA", (.55, .12, .08)); clay("maskB", (.1, .3, .35)); clay("maskC", (.7, .6, .3)); clay("maskD", (.25, .12, .35))
clay("eye", (1, .9, .6), 6)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(cl[k]); return o
def blk(at, d, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return mk(bm, k, at, (0, 0, rz))
def cone(at, r, h, n, k, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at)
def rough(at, r, k, s=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2])) * random.uniform(.88, 1.12)
    return mk(bm, k, at)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=13, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .2)))
mk(bm, "cliff2")
# cliff face: a wall of rough blocks at the back, with a cave mouth
for i in range(9):
    for j in range(3):
        rough((-10 + i * 2.5 + random.uniform(-.5, .5), 8 + random.uniform(-.5, .5), 1.5 + j * 3.2), random.uniform(1.8, 2.4), "cliff" if (i + j) % 2 else "cliff2", (1, .8, .75))
rough((0, 9.5, 6.5), 4.5, "cliff", (2.4, .7, .9))
blk((0, 5.4, 3.2), (4.4, .6, 3.4), "cave")
cone((0, 5.2, 6.6), 2.6, .8, 8, "cliff", 2.0).rotation_euler.x = math.pi / 2
for i in range(5): rough((-2.2 + i * 1.1, 5.0, 6.9 + (i % 2) * .3), .5, "cliff2", (1, .6, .6))
for i in range(3): cone((-.9 + i * .9, 5.0, 3.3), .13, .5, 5, "wood", .08)
for i in range(3): cone((-.9 + i * .9, 5.0, 3.8), .22, .35, 5, "flame", .02)
glow((0, 4.2, 4.4), (1, .5, .15), 700)
# terrace with steps and the masks
blk((0, 0, 0), (20, 12, 3.2), "cliff")
for i in range(5): blk((-2.5 + i * 1.25, -6.2 - i * .0, 0), (1.2, 1.0, 3.2 - i * .64), "cliff2")
for i in range(6):
    k = ("maskA", "maskB", "maskC", "maskD", "maskA", "maskC")[i]
    x = -6.5 + i * 2.6
    cone((x, -1.0, 3.2), .2, .5, 5, "wood", .15)
    rough((x, -1.0, 4.3), .9, k, (.8, .5, 1.1))
    for s in (-1, 1):
        rough((x + s * .35, -1.6, 4.5), .2, "eye", (1, .5, 1)); blk((x + s * .35, -1.75, 3.9), (.3, .1, .1), "cave")
    blk((x, -1.7, 3.55), (.5, .1, .15), "cave")
    blk((x, -1.0, 5.1), (1.3, .3, .25), "wood")
# flat-roofed mud house with a tall thatched roof
blk((-1, 2.5, 3.2), (8, 5.5, 3.4), "mud")
blk((-1, 2.5, 6.5), (8.6, 6.1, .3), "wood")
cone((-1, 2.5, 6.8), 6.6, 6.5, 4, "thatch", .5).rotation_euler.z = math.pi / 4
cone((-1, 2.5, 8.4), 5.4, 3.2, 4, "thatch2", .4).rotation_euler.z = math.pi / 4
cone((-1, 2.5, 11.4), 3.4, 2.4, 4, "thatch", .15).rotation_euler.z = math.pi / 4
cone((-1, 2.5, 13.7), 1.4, 1.8, 4, "thatch2", .05).rotation_euler.z = math.pi / 4
for i in range(7):
    a = i * math.pi / 3.5
    blk((-1 + math.cos(a) * 3.9, 2.5 + math.sin(a) * 3.9, 7.2), (.5, .5, .8), "wood").rotation_euler.z = a
blk((-1, -.05, 3.2), (1.6, .3, 2.2), "wood")
blk((-3.4, -.05, 4.4), (1.2, .2, 1.1), "flame"); blk((1.4, -.05, 4.4), (1.2, .2, 1.1), "flame")
glow((-1, -1.5, 4.5), (1, .55, .2), 300)
# stone lanterns and a few shrubs
for x, y in ((-8, -3), (8, -3)):
    cone((x, y, 3.2), .35, 1.4, 6, "cliff2", .25); blk((x, y, 4.6), (.9, .9, .8), "cliff"); cone((x, y, 5.4), .8, .5, 6, "flame", .1)
    glow((x, y, 5.2), (1, .5, .15), 120)
for i in range(7): rough((random.uniform(-9, 9), random.uniform(-5, 2), 3.3), random.uniform(.4, .8), "moss", (1, 1, .7))
# light: teal dusk key from the left, violet rim from behind
for c, w, p in (((.5, .8, .9), 4.5, (-26, -22, 11)), ((.7, .35, .9), 2.4, (22, 26, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 4)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("dusk"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .02, .03, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 85
ob = bpy.data.objects.new("cam", cm); sc.collection.objects.link(ob); sc.camera = ob
ob.location = (24, -58, 38)
ob.rotation_euler = (Vector((0, 1, 6)) - ob.location).to_track_quat('-Z', 'Y').to_euler()
