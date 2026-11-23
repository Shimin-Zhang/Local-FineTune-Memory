import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1546)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
pal = {}
def pigment(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .95
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    pal[name] = m
for k, v in dict(dust=(.3, .17, .09), wall=(.45, .15, .06), wall2=(.33, .1, .05), relief=(.6, .25, .1), wood=(.28, .14, .07),
                 wood2=(.18, .08, .04), leaf=(.08, .22, .1), leaf2=(.14, .3, .08), bark=(.2, .13, .08), stone=(.3, .26, .22),
                 cloth=(.7, .65, .55), ember=(.02, .01, .01)).items(): pigment(k, v)
pigment("lantern", (1, .5, .1), 14); pigment("flame", (1, .35, .05), 22)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(pal[m]); return o
def slab(m, x, y, z, w, d, h, rz=0, top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return shape(bm, m, (x, y, z), (0, 0, rz))
def pole(m, x, y, z, r, h, n=6, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, (x, y, z), rot)
def blob(m, x, y, z, r, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.85, 1.15), v.co.y * random.uniform(.85, 1.15), v.co.z * sq))
    return shape(bm, m, (x, y, z))
def lamp(c, w, p):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=7, radius2=13.5, depth=3.5)
for v in bm.verts:
    v.co.z -= 1.75
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
shape(bm, "dust")
# two walls of the courtyard: red mud with stepped relief bands, a gate gap on the south wall
for x0, x1 in ((-10.5, -3.5), (-2.5, 10.5)):
    slab("wall", (x0 + x1) / 2, 9, 0, x1 - x0, 1.2, 3.4, 0, .96); slab("wall2", (x0 + x1) / 2, 9, 3.4, x1 - x0 + .2, 1.4, .4)
    for i in range(int(x1 - x0) // 2):
        slab("relief", x0 + .8 + i * 2, 8.35, 1.2, 1.4, .2, .9); slab("relief", x0 + .8 + i * 2, 8.35, 2.3, .8, .15, .4)
slab("wall", 0, -9, 0, 21, 1.2, 3.4, 0, .96); slab("wall2", 0, -9, 3.4, 21.2, 1.4, .4)
for i in range(10): slab("relief", -9 + i * 2, -8.35, 1.2, 1.4, .2, .9)
for s in (-1, 1):
    for z in (0, 1.4, 2.8): slab("wall", s * 3.5, 0, z, 1.0, 18, .7)
# the stool house: a square platform on four carved legs, a tall house with a pointed roof
slab("wood2", 0, 0, 0, 4.6, 4.6, .7)
for sx in (-1, 1):
    for sy in (-1, 1):
        pole("wood", sx * 1.9, sy * 1.9, 0, .38, .75, 6, .3)
slab("wood", 0, 0, .7, 3.6, 3.6, 3.0, 0, .95)
for i in range(3): slab("wood2", 0, -1.82, 1.0 + i * .9, 1.4, .1, .5)
slab("wood2", 0, 0, 3.7, 4.2, 4.2, .3)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=3.2, radius2=.3, depth=2.4)
for v in bm.verts: v.co.z += 1.2
shape(bm, "wood2", (0, 0, 4.0), (0, 0, math.pi / 4))
slab("lantern", 0, -1.9, 1.0, .9, .1, 1.2); lamp((1, .5, .15), 450, (0, -2.8, 1.8))
# sacred tree: twisted trunk with a wide canopy
for i in range(4):
    pole("bark", 0, 0, .7 + i * .9, .5 - i * .07, 1.0, 6, .45 - i * .07, (0, .1 * i, 0))
for x, y, z, r in ((0, 0, 5.4, 2.6), (-2.2, 1, 5.0, 1.8), (2.3, -.8, 5.1, 1.9), (0, 2.2, 4.9, 1.7), (0, -2, 4.8, 1.6)): blob("leaf" if x < 1 else "leaf2", x, y, z, r, .8)
# offering stones, a low altar, lanterns on posts and a water trough
for i in range(5): slab("stone", -7 + i * .9, -6.5, 0, .8, .8, .5 + (i % 2) * .3, i * .5, .8)
slab("stone", 7, -6, 0, 2.4, 1.6, .9, .2); slab("flame", 7, -6, .9, .8, .8, .5, .2, .7); lamp((1, .4, .1), 300, (7, -6, 2))
for x, y in ((-6, -4), (6, 4), (-6, 4), (6, -4)):
    pole("wood2", x, y, 0, .1, 2.6, 5); pole("lantern", x, y, 2.6, .3, .6, 6, .25); lamp((1, .5, .15), 160, (x, y, 3.2))
slab("stone", -6.5, 0, 0, 1.4, 4.0, .5); slab("wall2", -6.5, 0, .5, 1.0, 3.6, .1)
for i in range(6): blob("stone", random.uniform(-9, 9), random.choice((-1, 1)) * random.uniform(6.5, 8), 0, random.uniform(.3, .6), .7)
for col, w, p in (((1, .5, .2), 5.5, (-26, -14, 8)), ((.3, .5, .7), 2.2, (22, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((10, -58, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
