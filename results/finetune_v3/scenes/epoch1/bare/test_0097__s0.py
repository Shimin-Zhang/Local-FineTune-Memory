import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1914)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, em=0, rough=.85, metal=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
water, quay, quayline, hull, hull2, deck, black, red, white, coal, iron, fog = (tint(c) for c in (
    (.06, .13, .17), (.22, .2, .18), (.3, .27, .22), (.1, .13, .16), (.06, .08, .1), (.2, .17, .13), (.03, .03, .04), (.35, .06, .05), (.5, .5, .45), (.02, .02, .02), (.25, .26, .28), (.5, .55, .6)))
steam = tint((.8, .85, .9), .5, 1); win = tint((1, .65, .25), 10); flag = tint((.7, .08, .08)); lamp = tint((1, .8, .4), 14)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return shape(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, at, rot)
def spar(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return shape(bm, m)
def puff(at, r, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15)
    return shape(bm, m, at)
def glow(c, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# harbour water with a quay along the back and a pier head at the right
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 27, v.co.y * 22, v.co.z * 2.4 - 1.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .8 + random.uniform(-1, 1), v.co.y * .8 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
shape(bm, water)
blk((0, 9.6, 0), (27, 4.4, 1.2), quay); blk((0, 7.4, 0), (27, .5, 1.3), quayline)
for x in range(-12, 13, 3): blk((x, 7.2, 1.2), (.3, .3, .8), white)
# the ironclad: a tapered hull, deck, casemate, masts, two turrets and a rudder
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 20, v.co.y * 4.4, (v.co.z + .5) * 3.0))
    if v.co.z > 1.5: v.co.y *= .75
    if v.co.x > 8: v.co.y *= .5
shape(bm, hull, (0, 0, .2))
blk((0, 0, 3.2), (19, 3.4, .25), deck); blk((0, 0, 3.45), (19.4, 3.8, .2), hull2)
blk((0, 0, 3.65), (15, 2.6, 1.6), hull2)
for i in range(7):
    for s in (-1, 1): blk((-6 + i * 2, s * 1.35, 4.2), (.8, .1, .6), win)
blk((0, 0, 5.25), (15.4, 2.9, .15), deck)
cyl((0, 0, 5.4), 1.3, 1.4, 8, hull2); cyl((0, 0, 6.8), .9, .5, 8, black)
cyl((0, 0, 7.3), .5, .5, 6, red)
for x in (-6.5, 6.5):
    cyl((x, 0, 3.65), 1.5, 1.2, 8, hull2); cyl((x, 0, 4.85), 1.1, .5, 8, black)
    for k in range(4): spar((x + math.cos(k * 1.57) * 1.2, math.sin(k * 1.57) * 1.2, 4.9), (x + math.cos(k * 1.57) * 3.0, math.sin(k * 1.57) * 3.0, 4.7), .22, black)
for x in (-5, 5):
    spar((x, 0, 3.4), (x, 0, 10), .16, black)
    spar((x - 1.5, 0, 7), (x + 1.5, 0, 7), .08, black)
    spar((x - 1.2, 0, 8.2), (x + 1.2, 0, 8.2), .08, black)
spar((-5, 0, 9.5), (5, 0, 9.5), .06, black)
blk((9.4, 0, 3.45), (1.2, 1.2, 2.4), hull2); blk((9.4, 0, 5.85), (1.4, 1.4, .15), deck)
cyl((9.4, 0, 6), .5, 1.4, 6, black); cyl((9.4, 0, 7.4), .5, .3, 6, red)
blk((9.4, 0, 3.45), (.2, .2, .2), win)
glow((1, .65, .25), 500, (0, -2.2, 4.3)); glow((1, .65, .25), 300, (9.4, -1.2, 4.3))
for i in range(3): puff((9.4 + i * .9, 0, 8.4 + i * 1.1), .7 + i * .2, steam)
# flag at the stern on a tall staff
spar((-9.6, 0, 3.4), (-9.6, 0, 9), .1, black); blk((-9.0, 0, 7.6), (1.2, .08, .9), flag); blk((-9.0, 0, 7.6), (.08, 1.2, .9), white)
# gangway from quay to the ship, with a rail
for i in range(5): blk((6.5 - i * .5, 2.5 + i * .7, 3.0 - i * .1), (.45, .9, .12), deck)
spar((6.5, 2.2, 3.7), (4.3, 5.6, 2.6), .08, black); spar((6.5, 2.8, 3.7), (4.3, 6.2, 2.6), .08, black)
# two coal barges alongside, heaps of coal and a crane on the quay
for y, x0 in ((-6.2, -6), (-6.4, 4.5)):
    blk((x0, y, .2), (9, 3.2, .8), hull2); blk((x0, y, 1.0), (8.4, 2.6, .15), deck)
    for k in range(4): puff((x0 - 3 + k * 2, y, 1.4), .9, coal)
    cyl((x0 + 3.6, y, 1.0), .5, 1.2, 6, hull2)
    spar((x0 - 4.5, y, 1.0), (x0 - 4.5, y, 3.2), .1, black)
cyl((10.5, 8.5, 1.2), .5, 1.2, 6, iron); spar((10.5, 8.5, 2.4), (10.5, 5.5, 6.5), .2, iron); spar((10.5, 8.5, 2.4), (10.5, 9.5, 4.5), .15, iron)
spar((10.5, 5.5, 6.5), (10.5, 5.5, 3.0), .05, iron); blk((10.5, 5.5, 2.5), (.5, .5, .5), red)
blk((7, 9.5, 1.2), (3, 1.6, 1.2), red); blk((7, 9.5, 2.4), (3.2, 1.8, .2), black)
for x in (-11, -7, 12):
    cyl((x, 8.5, 1.2), .3, 1.4, 6, lamp); glow((1, .8, .4), 220, (x, 8.5, 3.0))
# fog banks drifting across the water
for x, y, z, r in ((-9, -4, 1.2, 3.5), (2, -9, 1.0, 3.2), (10, 3, 1.4, 3.0), (-12, 2, 1.5, 2.6)):
    puff((x, y, z), r, fog)
for c, w, p in (((.75, .85, .95), 4.5, (-24, -20, 12)), ((.55, .6, .7), 2.2, (22, 24, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("fog"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .04, .05, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((6, -72, 44))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
