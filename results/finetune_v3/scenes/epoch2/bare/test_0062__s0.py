import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1167)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def tint(k, c, e=0, r=.9):
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    if e: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    M[k] = m
for k, c in (("ice", (.55, .7, .8)), ("ice2", (.4, .55, .7)), ("steel", (.35, .37, .4)), ("snow", (.7, .75, .85)), ("orange", (.8, .25, .03)),
             ("orange2", (.65, .18, .03)), ("sled", (.5, .3, .1)), ("drum", (.1, .2, .45)), ("flag", (.9, .75, .1)), ("dark", (.04, .04, .05)), ("rope", (.5, .45, .3))):
    tint(k, c)
tint("core", (.6, .9, 1), 2.5, .1); tint("lamp", (1, .75, .35), 9); tint("pane", (1, .6, .2), 6)
def put(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def blk(at, s, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, k, at, (0, 0, rz))
def rod(a, b, r, k, n=5):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    return put(bm, k, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def cyl(at, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, k, at)
def drift(at, r, k, sq=.3):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.85, 1.2), v.co.y * random.uniform(.85, 1.2), v.co.z * sq))
    return put(bm, k, at)
def beam(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("b", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("b", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# ice shelf base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 2
put(bm, "ice2")
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(3, 12)
    drift((r * math.cos(a), r * math.sin(a), 0), random.uniform(1, 2.2), "snow", .25)
# the drill tower: four legs, cross braces, platform, winch, derrick, drill line
for sx in (-1, 1):
    for sy in (-1, 1): rod((sx * 2.4, sy * 2.4, 0), (sx * 1.0, sy * 1.0, 9), .17, "steel")
for z in (1.5, 3.5, 5.5, 7.5):
    t = z / 9; h = 2.4 - 1.4 * t
    for s in (-1, 1):
        rod((s * h, -h, z), (s * h, h, z), .08, "steel"); rod((-h, s * h, z), (h, s * h, z), .08, "steel")
blk((0, 0, 8.6), (2.6, 2.6, .25), "steel"); blk((0, 0, 8.85), (2.2, 2.2, .1), "orange2")
cyl((0, 0, 9), .8, .6, 8, "drum"); rod((0, 0, 9.6), (0, 0, 12.5), .12, "steel", 4)
rod((0, 0, 9.6), (0, 0, 1.0), .05, "rope", 4)
blk((0, 0, 8.9), (.2, .2, .4), "lamp"); beam("POINT", (1, .75, .35), 400, (0, 0, 9.6))
# the borehole with a glowing core sample beside it
cyl((0, 0, 0), 1.0, .08, 8, "dark"); cyl((0, 0, .05), .75, .05, 8, "core")
for i in range(4):
    cyl((2.6 + i * .55, 1.0, 0), .22, .8 - i * .1, 6, "core", .22)
beam("POINT", (.6, .9, 1), 350, (0, 0, 1.2))
# trench lab: cut into the ice with a glowing roof panel and a bench
blk((-9, -2, 0), (6, 3.4, 1.2), "ice"); blk((-9, -2, 1.2), (5.4, 2.8, .12), "pane")
blk((-9, -3.6, 0), (6, .5, .5), "steel"); blk((-9, -.4, 0), (6, .5, .5), "steel")
blk((-9, -2, 1.3), (4.4, 1.8, .1), "orange2")
for x in (-11, -7): blk((x, -2, 1.3), (.15, .15, .9), "steel")
blk((-9, -2.2, 1.35), (1.8, .7, .5), "steel"); blk((-9, -2.2, 1.85), (1.2, .4, .1), "lamp")
beam("POINT", (1, .7, .35), 500, (-9, -2, 2.6))
# orange tents, a fuel drum, sledges with ice-core crates
for i, (x, y) in enumerate(((6, -5), (9, -2), (6.5, 1.5))):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=2.0, radius2=.15, depth=2.2)
    for v in bm.verts: v.co.z += 1.1
    put(bm, "orange" if i != 1 else "orange2", (x, y, 0), (0, 0, math.pi / 4 + i * .3))
    blk((x - 1.2, y - 1.4, 0), (.9, .1, 1.4), "dark")
cyl((3.5, -7, 0), .6, 1.3, 8, "drum"); cyl((3.5, -7, 1.3), .5, .1, 8, "orange2")
for x, y, rz in ((-4, -8, .3), (1, -9.5, -.2)):
    blk((x, y, .15), (3.0, 1.0, .15), "sled", rz)
    for s in (-1, 1): blk((x + s * 1.5 * math.cos(rz), y + s * 1.5 * math.sin(rz), .05), (.15, 1.0, .1), "sled", rz)
    blk((x, y, .3), (1.6, .8, .6), "orange2", rz); blk((x, y, .9), (1.2, .6, .1), "core", rz)
    rod((x + 1.5 * math.cos(rz), y + 1.5 * math.sin(rz), .3), (x + 2.8 * math.cos(rz), y + 2.8 * math.sin(rz), .1), .05, "rope")
# route flags on poles from the tents to the borehole
for i in range(7):
    t = i / 6; x = 6.5 - 5.5 * t; y = -3.5 + 2.5 * t + math.sin(t * 5) * .8
    rod((x, y, 0), (x, y, 2.4), .06, "steel"); blk((x + .5, y, 1.9), (1.0, .06, .7), "flag")
# cold sun: low pale key, violet rim
beam("SUN", (1, .9, .7), 6, (-26, -14, 9), (0, 0, 3)); beam("SUN", (.5, .5, 1), 2.4, (22, 20, 12), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .03, .07, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 5)); co.location = t + Vector((16, -56, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
