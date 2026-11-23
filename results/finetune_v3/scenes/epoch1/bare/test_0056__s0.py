import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1070)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
ash, stone, iron, rust, path = pigment((.14, .13, .15)), pigment((.1, .09, .1)), pigment((.2, .22, .24), 0, .6), pigment((.3, .12, .06)), pigment((.22, .2, .2))
lava, steam, wood, flag, dark = pigment((1, .22, .03), 14), pigment((.6, .6, .65), .35), pigment((.25, .17, .1)), pigment((.7, .1, .08)), pigment((.03, .03, .04))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("v"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("v", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(x, y, z, w, d, h, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mk(bm, m, (x, y, z), (0, 0, rz))
def cyl(x, y, z, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z))
def puff(x, y, z, r, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15)
    return mk(bm, m, (x, y, z))
def beam(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return mk(bm, m)
def roof(x, y, z, w, d, h, m, rz=0):
    bm = bmesh.new(); p = [bm.verts.new(c) for c in ((-w/2, -d/2, 0), (w/2, -d/2, 0), (w/2, d/2, 0), (-w/2, d/2, 0), (-w/2, 0, h), (w/2, 0, h))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): bm.faces.new([p[i] for i in f])
    return mk(bm, m, (x, y, z), (0, 0, rz))
def flame(x, y, z, c, w):
    L = bpy.data.lights.new("f", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("f", L); o.location = (x, y, z); sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.7
mk(bm, ash)
# volcano cone behind: stacked dark stone rings with a glowing crater
for i in range(7):
    r = 7.2 - i * .85; z = .1 + i * 1.25
    cyl(0, 7.5, z, r, 1.3, 8, stone if i % 2 else dark, r - .85)
    for k in range(6):
        a = random.uniform(0, 6.28); x, y = math.cos(a) * r * .9, 7.5 + math.sin(a) * r * .9
        if z > 1.5 and y < 6: blk(x, y, z + .3, random.uniform(.6, 1.1), .8, random.uniform(.5, 1), stone, a)
cyl(0, 7.5, 8.6, 1.5, .4, 8, lava)
flame(0, 7.5, 9.6, (1, .3, .05), 1800)
for i in range(5): puff(random.uniform(-1.5, 1.5), 7.5 + random.uniform(-1, 1), 9.5 + i * 1.6, .9 + i * .3, steam)
# the hut: black stone base, corrugated iron roof, door, window, chimney
blk(-4, -2, .1, 5.4, 4.4, 2.6, stone)
roof(-4, -2, 2.7, 6.2, 5.2, 1.7, iron, 0)
for i in range(10): blk(-6.4 + i * .55, -2, 2.75, .08, 5.2, .08, dark)
blk(-4, -.2, .1, 1.0, .12, 1.9, dark); blk(-2.2, -.2, 1.0, .9, .12, .8, pigment((1, .6, .2), 8)); blk(-5.9, -.2, 1.0, .9, .12, .8, pigment((1, .6, .2), 8))
blk(-1.5, -2, 3.0, .6, .6, 1.4, rust)
for i in range(5): blk(random.uniform(-6.5, -1.5), random.uniform(-4, 0), 0, random.uniform(.5, 1), random.uniform(.5, 1), random.uniform(.3, .6), stone, random.random())
# marker pole with flag and a little sign
cyl(2.5, -3.5, .1, .1, 4.2, 5, wood); blk(3.1, -3.5, 3.0, 1.2, .08, .8, flag)
cyl(-1.5, -5.5, .1, .08, 1.8, 5, wood); blk(-1.5, -5.5, 1.4, 1.4, .1, .7, iron); blk(-1.5, -5.56, 1.7, 1.0, .04, .12, pigment((.9, .9, .85)))
# railed path curving from the front edge to the hut door
pts = [Vector((3.5, -9, .1)), Vector((2.5, -6.5, .1)), Vector((.5, -4.5, .1)), Vector((-1.5, -3.5, .1)), Vector((-3, -2.8, .1))]
for a, b in zip(pts, pts[1:]):
    beam(a, b, .9, path)
    for t in (0, .5):
        p = a.lerp(b, t); n = (b - a).normalized().perp()
        for s in (-.55, .55):
            q = p + n * s; cyl(q.x, q.y, .1, .05, 1.0, 4, wood)
    for s in (-.55, .55):
        beam(pts[0] + Vector((0, s, 1.0)), pts[-1] + Vector((0, s, 1.0)), .06, wood)
# boulders and ash drifts
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(8, 11.5); x, y = math.cos(a) * r, math.sin(a) * r * .9
    if y < -2 and abs(x) < 5 and y > -9: continue
    puff(x, y, .1, random.uniform(.5, 1.3), stone if i % 3 else ash)
for i in range(10):
    a = random.uniform(0, 6.28); r = random.uniform(8, 11.5); x, y = math.cos(a) * r, math.sin(a) * r * .9
    puff(x, y, .3, random.uniform(1.5, 2.5), ash)
# ember-lit dusk: deep red-orange key low from the left, violet rim from behind
for c, e, p in (((1, .45, .2), 5, (-26, -14, 8)), ((.55, .35, 1), 2.2, (20, 22, 12))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = e
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 2, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 2, 3.5)); co.location = t + Vector((-8, -54, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
