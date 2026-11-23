import bpy, bmesh, random, math
from mathutils import Vector
random.seed(463)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(c, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = glow
    return m
moss, dirt, trunk, pine, pine2, canvas, canvas2, log, rock, flame, ember, rope, bag, lantern, snow = (dye((.07, .15, .07)), dye((.2, .15, .1)), dye((.2, .12, .07)), dye((.04, .17, .1)), dye((.06, .22, .12)),
    dye((.7, .35, .1)), dye((.55, .22, .08)), dye((.3, .18, .1)), dye((.25, .25, .27)), dye((1, .5, .08), 14), dye((1, .2, .05), 8), dye((.6, .55, .4)), dye((.5, .12, .1)), dye((1, .8, .35), 12), dye((.7, .75, .8)))
def make(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cone(p, r, h, n, m, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, p, rot)
def block(p, s, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, p, (0, 0, rz))
def stick(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r * .8, depth=d.length)
    return make(bm, m, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def stone(p, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.8, 1.2), v.co.y * random.uniform(.8, 1.2), v.co.z * sq))
    return make(bm, m, p)
def glow(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=12, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
make(bm, moss)
# dirt clearing and a trail of flat stones to the fire
for i in range(12):
    a = i * math.pi / 6
    stone((math.cos(a) * 4.2, math.sin(a) * 4.2, 0), 1.2, dirt, .06)
for i in range(6): stone((-3 + i * .6, -5 + i * .5, 0), .45, rock, .2)
# tent: ridge roof from two sloped walls, a dark doorway, guy ropes and pegs
tx, ty = 3.5, 3.0
block((tx, ty, 0), (3.6, 4.6, .2), canvas2)
for s in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * 3.8, v.co.y * 4.8, (v.co.z + .5) * 2.0))
    make(bm, canvas if s > 0 else canvas2, (tx, ty, .2), (0, s * .62, 0))
block((tx, ty - 2.35, .2), (1.4, .1, 1.7), dye((.05, .04, .04)))
for sx in (-1, 1):
    for sy in (-1, 1):
        stick((tx + sx * 1.8, ty + sy * 2.3, 1.8), (tx + sx * 3.4, ty + sy * 3.6, 0), .05, rope); block((tx + sx * 3.4, ty + sy * 3.6, 0), (.3, .3, .3), rock)
stick((tx, ty - 2.3, .2), (tx, ty - 4.2, 0), .05, rope)
# campfire: ring of stones, crossed logs, flames, embers, and a lantern post
for i in range(9):
    a = i * math.pi * 2 / 9
    stone((math.cos(a) * 1.5, math.sin(a) * 1.5, .1), .5, rock, .8)
for k in range(3):
    a = k * math.pi / 3
    stick((math.cos(a) * 1.2, math.sin(a) * 1.2, .3), (-math.cos(a) * 1.2, -math.sin(a) * 1.2, .7), .17, log)
cone((0, 0, .3), .9, 1.8, 6, flame, .05); cone((.4, .2, .3), .5, 1.2, 5, ember, .03)
glow("POINT", (1, .5, .12), 900, (0, 0, 1.2))
stick((3.2, -1.5, 0), (3.2, -1.5, 2.2), .08, log); block((3.2, -1.5, 2.2), (.5, .5, .6), lantern); glow("POINT", (1, .75, .35), 250, (3.2, -1.5, 2.6))
# log bench: three logs on two stump legs, with a rolled sleeping bag
for i in range(3): cone((-3.2, -2.4 + i * .55, .85), .26, 3.4, 6, log, .26, (0, math.pi / 2, 0)).location.x = -1.5
for sx in (-1, 1): cone((-1.5 + sx * 1.4, -2.4, 0), .3, .85, 6, trunk)
cone((-2.4, -3.4, .3), .35, 1.4, 6, bag, .35, (0, math.pi / 2, .3))
# pines round the clearing: trunk, three stacked tiers, snow caps on some
for i in range(14):
    a = i * 2.399 + random.uniform(-.2, .2); r = random.uniform(8.2, 10.4)
    x, y = math.cos(a) * r, math.sin(a) * r * .9
    if abs(x - 3.5) < 3 and abs(y - 3) < 3 or (x > 0 and y < -1 and r < 9): continue
    h = random.uniform(.8, 1.3); R = random.uniform(1.2, 1.7)
    cone((x, y, 0), .35 * h, 1.6 * h, 6, trunk, .25 * h)
    for t in range(3):
        z = 1.0 * h + t * 1.3 * h; rr = R * (1 - t * .3) * h
        cone((x, y, z), rr, 2.2 * h, 7, pine if (i + t) % 2 else pine2, .1)
        if i % 3 == 0: cone((x, y, z + 1.5 * h), rr * .5, .8 * h, 7, snow, .08)
# a cooler, a backpack and a pair of boots by the tent
block((1.4, 1.0, 0), (1.0, .8, .8), canvas2); block((1.4, 1.0, .8), (1.1, .9, .15), dye((.1, .1, .12)))
block((5.4, -.5, 0), (.7, .5, .9), bag); block((5.4, -.5, .9), (.5, .4, .5), bag)
for k in (-.2, .2): block((5.2 + k, -.2, 0), (.35, .55, .35), dye((.15, .1, .08)))
# cold moonlight: pale blue key from the left, deep violet rim from behind
glow("SUN", (.55, .7, 1), 4.5, (-26, -14, 10), (0, 0, 2)); glow("SUN", (.6, .35, .9), 2.2, (22, 24, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((8, -54, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
