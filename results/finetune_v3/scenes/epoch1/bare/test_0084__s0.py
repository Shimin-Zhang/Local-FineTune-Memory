import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1654)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
R = {}
def tone(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    R[name] = m
for k, v in dict(grass=(.1, .2, .08), dirt=(.3, .17, .1), straw=(.55, .42, .18), white=(.7, .68, .6), red=(.6, .08, .06), blue=(.1, .2, .5),
                 wood=(.25, .14, .07), wood2=(.35, .22, .12), cloth=(.5, .08, .08), cloth2=(.6, .6, .55), dark=(.03, .03, .04), steel=(.2, .22, .24),
                 arrow=(.5, .3, .1), fletch=(.7, .65, .1), post=(.2, .12, .07)).items(): tone(k, v)
tone("lantern", (1, .6, .2), 12); tone("paper", (.7, .7, .65), .3)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(R[k]); return o
def blk(at, d, k, rz=0, top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * f, v.co.y * d[1] * f, (v.co.z + .5) * d[2]))
    return mk(bm, k, at, (0, 0, rz))
def pole(at, r, h, k, n=5, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at)
def ball(at, r, k, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return mk(bm, k, at)
def beam(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, k)
def lamp(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# grassy field, tapering rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.3, 1.3), random.uniform(-1.3, 1.3), random.uniform(-1.3, .3)))
    v.co.z -= 1.6
mk(bm, "grass")
blk((0, 3.5, 0), (22, 17, .12), "dirt", 0, .97)
# shooting line with stakes and a marker flag
blk((-1, -7.2, 0), (19, .22, .1), "white")
for i in range(7): blk((-8 + i * 2.8, -7.2, 0), (.2, .2, .8), "white")
pole((-9.5, -7.2, 0), .06, 3.2, "post"); blk((-9.1, -7.2, 2.6), (.9, .06, .6), "red")
# three straw targets at three distances on A-frame stands
for i, y in enumerate((2.5, 6.5, 10.5)):
    for s in (-1, 1): beam((-1 + s * 1.2, y, 0), (-1, y, 1.9), .14, "post")
    beam((-2.2, y, 1.9), (.2, y, 1.9), .12, "post")
    for r, k in ((1.0, "white"), (.7, "blue"), (.45, "red"), (.22, "white")):
        pole((-1, y - .06, 1.9), r, .55, k, 8)
    pole((-1, y - .06, 1.9), .06, .7, "dark", 4)
    for a in range(3):
        beam((-1.3 + a * .3, y - .25, 1.95), (-1.3 + a * .3, y - .25, 2.7), .05, "arrow"); beam((-1.3 + a * .3, y - .25, 2.6), (-1.3 + a * .3, y - .25, 2.9), .12, "fletch")
# scorekeeper's table with a chair, a clipboard and a lamp
blk((5.5, -4, 0), (3.2, 1.4, .9), "wood")
for sx in (-1.4, 1.4):
    for sy in (-.6, .6): blk((5.5 + sx, -4 + sy, 0), (.14, .14, .9), "post")
blk((5.5, -4, .9), (3.4, 1.5, .1), "wood2"); blk((5.0, -4, 1.0), (.9, .6, .06), "paper"); blk((6.2, -4, 1.0), (.2, .2, .6), "lantern")
pole((7.8, -4, 0), .35, .6, "wood", 6); blk((7.8, -4, .6), (.8, .8, .1), "wood2"); blk((7.8, -4.4, .6), (.8, .1, .8), "wood2")
lamp((5.5, -4, 1.8), (1, .6, .2), 220)
# arrow rack with arrows in it
for sx in (-1, 1): pole((-7.5 + sx * .9, -4, 0), .08, 1.8, "post", 4)
blk((-7.5, -4, 1.2), (2.0, .3, .1), "post")
for i in range(8):
    beam((-8.2 + i * .2, -4, .15), (-8.2 + i * .2, -4, 2.0), .05, "arrow"); beam((-8.2 + i * .2, -4, 1.9), (-8.2 + i * .2, -4, 2.2), .12, "fletch")
# striped pavilion: four posts, flat roof with a striped awning, bench and lantern
for sx in (-1, 1):
    for sy in (-1, 1): pole((7 + sx * 2.4, 4 + sy * 2.0, 0), .12, 3.4, "post", 5)
for sy in (-1, 1): blk((7, 4 + sy * 2.0, 3.4), (5.6, .15, .12), "cloth2")
for i in range(8): blk((4.7 + i * .62, 4, 3.25), (.62, 4.6, .1), "cloth" if i % 2 else "cloth2", 0, 1)
blk((7, 4, 3.5), (5.8, 4.8, .12), "cloth2", 0, .96)
blk((7, 4, 0), (3.4, 1.0, .7), "wood"); blk((7, 4, .7), (3.6, 1.2, .1), "wood2")
pole((7, 4, 2.2), .05, 1.1, "dark", 4); ball((7, 4, 2.1), .35, "lantern", (1, 1, 1.3)); lamp((7, 4, 2.1), (1, .6, .2), 350)
for i in range(3): blk((5.8 + i * 1.2, 4, .8), (.6, .3, .06), "paper")
# boulders and tufts of grass at the edge
for x, y in ((-10, 8), (10, 10), (-10.5, -9), (10.5, -8), (-3, 11.5)):
    ball((x, y, .2), random.uniform(.7, 1.1), "dirt", (1.2, 1, .8))
for i in range(14):
    x, y = random.uniform(-11, 11), random.uniform(-10, 11)
    if abs(x + 1) < 12 and -9 < y < 12 and (x - 7) ** 2 + (y - 4) ** 2 > 9: pole((x, y, 0), .12, .5, "grass", 4, .02)
# dusk light: low orange sun from the left, violet rim from behind
for c, w, p in (((1, .5, .22), 6, (-30, -16, 8)), ((.5, .3, .8), 2.2, (24, 28, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dusk"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
tg = Vector((0, 2, 1.2)); co.location = tg + Vector((6, -56, 34))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
