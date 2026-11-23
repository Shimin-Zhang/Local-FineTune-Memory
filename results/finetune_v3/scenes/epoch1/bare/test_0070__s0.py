import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1742)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def glaze(rgb, em=0):
    m = bpy.data.materials.new("g"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .8
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
flag, flag2, brick, slate, iron, leaf, leaf2, pot, wicker, water, glow, trunk, cream, bulb = (
    glaze((.16, .18, .17)), glaze((.1, .12, .12)), glaze((.22, .1, .08)), glaze((.1, .12, .16)), glaze((.04, .05, .06)), glaze((.1, .38, .12)), glaze((.2, .5, .15)), glaze((.4, .15, .08)),
    glaze((.45, .3, .12)), glaze((.2, .7, .8)), glaze((.7, 1, .5), 10), glaze((.2, .12, .07)), glaze((.5, .42, .3)), glaze((1, .85, .4), 14))
def build(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("b", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, at, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return build(bm, m, at, rot)
def column(m, at, r, h, n=7, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return build(bm, m, at, rot)
def frond(m, at, length, ang, tilt):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * .2, v.co.y * length * (.7 - .5 * v.co.z), (v.co.z + .5) * .08))
    return build(bm, m, at, (tilt, 0, ang))
def lamp(kind, rgb, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = rgb, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# garden terrace: a floating slab of slate flagstones with a rough keel underneath
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=11.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .3)))
build(bm, flag2)
for i in range(9):
    for j in range(7): slab(flag if (i + j) % 2 else flag2, (-8 + i * 2, -6.5 + j * 2.2, 0), (1.9, 2.1, .15))
# the house wing at the back left: brick wall with sash windows and slate roof
slab(brick, (-6.5, 7.2, 0), (9, 3.2, 4.6)); slab(slate, (-6.5, 7.2, 4.6), (9.8, 3.8, .35), (.0, 0, 0))
for i in range(3):
    slab(cream, (-9 + i * 2.4, 5.55, 1.6), (1.0, .15, 1.6)); slab(glow, (-9 + i * 2.4, 5.45, 1.7), (.8, .1, 1.3))
slab(cream, (-6.5, 5.55, 3.4), (7, .15, .6))
# conservatory: glass walls on a brick plinth, cast iron ribs and a ridge with finials
slab(brick, (1.5, 2, 0), (12.4, 8.4, .6))
for x in (-4.5, 8.5): slab(cream, (x, 2, .6), (.3, 8, 3.4))
for y in (-2.0, 6.0): slab(cream, (2, y, .6), (12.6, .3, 3.4))
for y in (-1.85, 5.85): slab(glow, (2, y, .6), (12.4, .06, 3.2))
for x in (-4.35, 8.35): slab(glow, (x, 2, .6), (.06, 7.8, 3.2))
for i in range(11):
    x = -3.8 + i * 1.1
    slab(iron, (x, -1.9, .6), (.12, .12, 3.4)); slab(iron, (x, 5.9, .6), (.12, .12, 3.4))
for i in range(8):
    y = -1.4 + i * 1.05; slab(iron, (-4.3, y, .6), (.12, .12, 3.4)); slab(iron, (8.3, y, .6), (.12, .12, 3.4))
for s in (-1, 1):
    slab(iron, (2, 2 + s * 2.6, 3.9), (12.6, .12, .12), (-s * .5, 0, 0)); slab(iron, (2, 2 + s * 5.2, 3.9), (12.6, .12, .12), (-s * .5, 0, 0))
    for i in range(6):
        x = -3.8 + i * 2.2
        for k in range(2): slab(iron, (x, 2 + s * (1.3 + k * 2.6), 3.9 + .2 * k), (.1, .1, .1))
slab(iron, (2, 2, 5.1), (12.6, .2, .2)); slab(iron, (2, 2, 5.3), (.2, .2, .2))
for x in (-4, 8): slab(iron, (x, 2, 4.0), (.15, 7.4, .15))
# hanging lanterns inside
for x in (-1.5, 5.5):
    column(iron, (x, 2, 3.9), .03, 1.0); column(glow, (x, 2, 2.6), .35, .6, 6, .3); lamp("POINT", (1, .85, .4), 220, (x, 2, 2.7))
# cast iron stair up to the wing door, with a spiral newel
for i in range(7): slab(iron, (-3.2 + i * .6, 3.0, 0), (.6, 1.4, .35 + i * .0))
for i in range(7): slab(cream, (-3.2 + i * .6, 3.0, .35 + i * .0), (.5, 1.2, .1))
for i in range(7): column(iron, (-3.2 + i * .6, 2.2, .35), .06, 1.0, 5)
column(iron, (-3.2, 2.2, .35), .12, 1.1, 6, .18); column(bulb, (-3.2, 2.2, 1.4), .2, .3, 6)
lamp("POINT", (1, .85, .4), 160, (-3.2, 2.2, 1.5))
# fountain: three tiers, basin, jets of water and a glowing bowl
column(iron, (2.0, 2.0, .6), 2.6, .5, 8); column(cream, (2.0, 2.0, 1.1), 2.3, .1, 8); column(water, (2.0, 2.0, 1.2), 2.1, .06, 8)
column(cream, (2.0, 2.0, 1.1), .45, 1.0, 7, .35); column(cream, (2.0, 2.0, 2.1), 1.0, .15, 8); column(cream, (2.0, 2.0, 2.25), .3, .6, 6, .22)
column(cream, (2.0, 2.0, 2.85), .6, .12, 8); column(glow, (2.0, 2.0, 2.97), .45, .05, 8)
for i in range(5):
    a = i * 1.26; column(water, (2.0 + math.cos(a) * .5, 2.0 + math.sin(a) * .5, 1.5), .06, 1.2, 4, .04)
lamp("POINT", (.6, 1, .6), 500, (2.0, 2.0, 3.4))
# ferns in terracotta pots, bigger than life
for x, y, s in ((-3, 4.5, 1.2), (-2, -1, 1.0), (7.5, 4.8, 1.1), (6.5, -.6, 1.3), (-3.5, -1.2, .9), (7.8, 1.2, 1.0), (-.5, 5.2, 1.0), (4.5, 5.0, 1.1)):
    column(pot, (x, y, .6), .5 * s, .6 * s, 7, .38 * s)
    for k in range(6): frond(leaf if k % 2 else leaf2, (x, y, 1.1 * s), 1.5 * s, k * math.pi / 3 + random.random() * .3, .9 + random.random() * .25)
# wicker chairs round a wrought iron table
tx, ty = 0.5, 2.0
column(iron, (tx, ty, .6), .12, 1.0, 5); column(iron, (tx, ty, 1.6), .9, .1, 8)
for k in range(4): column(iron, (tx + math.cos(k * 1.57) * .5, ty + math.sin(k * 1.57) * .5, .6), .05, 1.0, 4)
column(glow, (tx, ty, 1.7), .25, .3, 6, .35); lamp("POINT", (1, .85, .4), 150, (tx, ty, 2.0))
for k in range(4):
    a = k * math.pi / 2 + .4; cx, cy = tx + math.cos(a) * 2.0, ty + math.sin(a) * 2.0
    slab(wicker, (cx, cy, .6), (1.0, 1.0, .5), (0, 0, a)); slab(wicker, (cx - math.cos(a) * .5, cy - math.sin(a) * .5, 1.1), (1.0, .15, 1.0), (0, 0, a))
    for sx in (-.4, .4):
        for sy in (-.4, .4): column(iron, (cx + math.cos(a + 1.57) * sx, cy + math.sin(a + 1.57) * sx, .6), .05, .5, 4)
# a stone bench and a couple of clipped topiary cones
slab(cream, (6.5, 2.0, .6), (1.8, .6, .5)); slab(cream, (6.5, 2.35, 1.1), (1.8, .15, .5))
for x, y in ((-5.5, -1.5), (9.5, 4.5)):
    column(pot, (x, y, 0), .5, .8, 6, .4); column(leaf, (x, y, .8), .7, 1.6, 6, .1)
lamp("SUN", (.55, .75, 1), 4.5, (-22, -16, 9), (0, 0, 1)); lamp("SUN", (1, .55, .3), 2.2, (20, 22, 8), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .025, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 2)); co.location = t + Vector((12, -50, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
