import bpy, bmesh, random, math
from mathutils import Vector
random.seed(829)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .8
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
cliff, cliff2, white, red, slate, grass, foam, glass, rockm, door, wood = (tone((.14, .14, .16)), tone((.2, .2, .22)), tone((.75, .74, .7)), tone((.6, .08, .06)), tone((.12, .13, .16)),
    tone((.1, .22, .1)), tone((.6, .7, .75)), tone((1, .75, .3), 12), tone((.25, .24, .26)), tone((.05, .05, .06)), tone((.3, .18, .1)))
def solid(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return solid(bm, m, at, rot)
def cube(at, w, d, h, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return solid(bm, m, at, (0, 0, rz))
def rock(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return solid(bm, m, at)
def glow(at, rgb, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = rgb, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# headland: a rocky cliff with a grassy top, a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 2
solid(bm, cliff)
drum((0, 0, 0), 11.5, .4, 9, grass, 11.2)
for i in range(7): rock((random.uniform(-9, 9), random.uniform(-9, 9), .1), random.uniform(.8, 1.6), cliff2, .5)
# the tower: nine tapering courses, alternating white and red
for k in range(9):
    r = 2.7 - k * .17
    drum((0, 0, .4 + k * 1.7), r, 1.7, 8, white if k % 2 else red, r - .17)
drum((0, 0, .4), 3.1, .8, 8, cliff2, 2.9)
# gallery, lantern room, roof
drum((0, 0, 15.5), 3.1, .5, 8, slate)
drum((0, 0, 16), 2.2, .25, 8, slate)
for k in range(8):
    a = k * math.pi / 4
    cube((math.cos(a) * 2.5, math.sin(a) * 2.5, 16.2), .1, .1, 1.0, wood, a + math.pi / 2)
cube((0, 0, 16.2), 5.1, .08, .1, wood); cube((0, 0, 17.1), 5.1, .08, .1, wood)
drum((0, 0, 16.25), 1.5, 2.4, 8, glass, 1.4)
drum((0, 0, 18.65), 1.8, .3, 8, slate)
drum((0, 0, 18.9), 2.4, 1.6, 8, red, .2)
drum((0, 0, 20.5), .12, .8, 5, slate)
glow((0, 0, 17.4), (1, .75, .3), 2200)
# stair door and a small keeper's cottage with a lit window
cube((0, -2.55, .4), 1.0, .3, 1.8, door); cube((0, -2.5, 2.2), 1.2, .3, .25, white)
cube((-6, 3, .4), 3.4, 2.6, 2.2, white); cube((-6, 3, 2.6), 3.8, 3.0, .3, slate)
cube((-6, 1.65, 1.1), .9, .1, .9, glass); cube((-6, 1.65, .4), .8, .1, 1.6, door)
glow((-6, .5, 1.5), (1, .7, .3), 350)
# rocks, a breakwater and foam
for i in range(6): rock((-10 + i * 1.7, -9 + i * .3 + (i % 2) * .6, .3), random.uniform(.7, 1.1), rockm)
for i in range(5): rock((-9 + i * 1.2, -6 + i * 1.3, .1), .35, foam, .4)
for i in range(4): rock((8 + (i % 2) * .5, -8 + i * 1.0, .1), .35, foam, .4)
# a row of bollards and a lantern post at the cliff edge
for i in range(3): drum((-2.5 + i * 1.6, -7.5, .4), .22, .7, 6, wood, .18)
drum((6, -5, .4), .15, 3.2, 5, wood); cube((6, -5, 3.6), .5, .5, .6, glass); glow((6, -5, 4), (1, .7, .3), 200)
# cold moonlit night: pale blue key from the left, a green-grey rim from behind
for rgb, w, at in (((.55, .7, 1), 4.5, (-26, -12, 11)), ((.4, .7, .6), 2, (22, 24, 12))):
    s = bpy.data.lights.new("sun", "SUN"); s.color, s.energy = rgb, w
    o = bpy.data.objects.new("sun", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 6)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 85
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
aim = Vector((0, 0, 9)); co.location = aim + Vector((14, -60, 36))
co.rotation_euler = (aim - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
