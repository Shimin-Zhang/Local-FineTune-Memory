import bpy, bmesh, random, math
from mathutils import Vector
random.seed(524)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, e=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .6
    if e: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = e
    return m
oak, oak2, brass, brass2, cloth = col((.2, .11, .06)), col((.13, .07, .04)), col((.55, .4, .12)), col((.35, .25, .08)), col((.35, .04, .12))
crystal, mist, mist2, eye, candle = col((.3, .55, 1), 1.4), col((.55, .35, 1), 6), col((.2, .8, .9), 6), col((1, .6, .1), 14), col((1, .75, .3), 12)
gem = [col(c, 4) for c in ((.9, .2, .5), (.2, .9, .8), (.9, .8, .2))]
def mesh(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(p, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mesh(bm, m, p, (0, 0, rz))
def ring(p, r1, r2, h, n, m):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, p)
def orb(p, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return mesh(bm, m, p)
def spark(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=9, depth=2.6)
for v in bm.verts:
    v.co.z -= 1.3
    if v.co.z < -1: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.2, .2)))
mesh(bm, oak2)
for i in range(8):
    a = i * math.pi / 4 + .2
    slab((math.cos(a) * 6.6, math.sin(a) * 6.6, .0), (3.6, 1.4, .12), oak if i % 2 else oak2, a + math.pi / 2)
# round table: turned top, turned foot, turned base, brass ring
ring((0, 0, 0), 2.8, 2.6, .5, 8, oak2); ring((0, 0, .5), 1.2, .9, 1.4, 8, oak); ring((0, 0, 1.9), 3.2, 3.4, .45, 8, oak)
ring((0, 0, 2.35), 3.5, 3.5, .12, 8, brass); ring((0, 0, 1.9), 3.2, 3.2, .08, 8, cloth)
# the stand: a brass bowl cradle with three claws, under the ball
ring((0, 0, 2.35), .5, .9, .35, 8, brass2)
for k in range(3):
    a = k * 2.09 + .4
    slab((math.cos(a) * 1.0, math.sin(a) * 1.0, 2.6), (.22, .22, 1.1), brass, a + math.pi / 2, .6)
    orb((math.cos(a) * 1.1, math.sin(a) * 1.1, 3.6), .2, brass2)
# the crystal ball: faceted glass sphere with a swirling mist inside
orb((0, 0, 5.0), 2.0, crystal, (1, 1, .95))
for i in range(3):
    z = 4.2 + i * .9
    r = 1.6 * math.sqrt(max(0, 1 - ((z - 5) / 2.0) ** 2)) * .8
    for k in range(5):
        a = k * 1.26 + i * 2.1
        orb((math.cos(a) * r, math.sin(a) * r, z + .1 * k), .38 - .05 * i, mist if (i + k) % 2 else mist2, (1.4, 1, .6))
orb((0, 0, 5.0), .5, mist2)
spark("POINT", (.4, .55, 1), 900, (0, 0, 5.0)); spark("POINT", (.7, .3, 1), 400, (0, -1.5, 4.2))
# a glowing eye in the mist, seen through the glass
orb((.2, -.2, 5.0), .55, col((.9, .95, 1), 8)); orb((.2, -.2, 5.0), .22, col((.02, .03, .1), 2))
# candles on the table rim, books, a dagger, gemstones
for i, (a, h) in enumerate(((.9, .9), (2.4, .6), (3.7, 1.1), (5.5, .7))):
    x, y = math.cos(a) * 2.9, math.sin(a) * 2.9
    ring((x, y, 2.35), .2, .17, h, 6, col((.8, .75, .65))); ring((x, y, 2.35 + h), .08, .04, .22, 5, candle)
    spark("POINT", (1, .7, .3), 90, (x, y, 2.9 + h))
for i, (a, c) in enumerate(((1.5, gem[0]), (1.9, gem[1]), (2.3, gem[2]))):
    slab((math.cos(a) * 2.7, math.sin(a) * 2.7, 2.35 + i * .15), (1.2, .9, .15), c, a + .3)
slab((-2.2, -1.8, 2.35), (.14, 1.3, .12), brass2, .6); slab((-2.2, -1.8, 2.47), (.5, .5, .1), brass, .6, .3)
for i, (x, y, c) in (((-1.4, 1.6, 0), (1.6, 1.7, 1), (-.6, 2.2, 2))):
    g = orb((x, y, 2.6), .32, c[gem.index(c) if False else 0]); g.data.materials.clear(); g.data.materials.append(c)
# a stool and a chair by the table
ring((-6.2, -1.5, 0), 1.0, .9, 1.3, 6, oak2); ring((-6.2, -1.5, 1.3), 1.2, 1.2, .25, 6, cloth)
for sx in (-1, 1):
    for sy in (-1, 1): slab((5.8 + sx * .9, 1.5 + sy * .9, 0), (.2, .2, 1.4), oak2)
slab((5.8, 1.5, 1.4), (2.2, 2.2, .2), oak); slab((5.8, 2.5, 1.6), (2.2, .2, 1.6), oak)
# moonlit night: cold moon key from the left, violet rim from behind
spark("SUN", (.5, .65, 1), 5, (-17, -10, 10), (0, 0, 3)); spark("SUN", (.8, .35, .9), 2.2, (14, 16, 8), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .01, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.2)); co.location = t + Vector((6, -40, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
