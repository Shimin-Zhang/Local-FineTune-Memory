import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1778)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
D = {}
def glaze(name, rgb, em=0, rough=.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    D[name] = m
for k, v in dict(sand=(.22, .2, .22), flag=(.06, .07, .12), brick=(.3, .1, .09), trim=(.4, .38, .35), slate=(.12, .13, .17), stone=(.35, .32, .3),
                 coat=(.05, .05, .08), skin=(.55, .38, .3), red=(.5, .05, .05), wood=(.25, .15, .08), iron=(.07, .07, .09),
                 green=(.05, .25, .12), gold=(.7, .5, .1)).items(): glaze(k, v)
glaze("pane", (1, .7, .3), em=7); glaze("bulb", (1, .85, .5), em=14); glaze("clockface", (1, .95, .8), em=8); glaze("sign", (1, .1, .1), em=10)
def cast(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); me.materials.append(D[m]); return o
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return cast(bm, m, at, rot)
def col(at, r, h, m, n=8, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return cast(bm, m, at)
def orb(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return cast(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# street block: snow-dusted kerb and dark flagstone pavement
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=12, radius2=18, depth=3.6)
for v in bm.verts:
    v.co = Vector((v.co.x * 1.2, v.co.y * 1.1, v.co.z - 1.8)); v.co.x += random.uniform(-.5, .5); v.co.y += random.uniform(-.5, .5)
    if v.co.z < -1: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, .3)))
cast(bm, "sand"); box((0, 0, 0), (26, 16, .25), "flag")
for i in range(16): box((-12 + i * 1.6, -7.4, .25), (1.4, .2, .1), "sand", (0, 0, random.uniform(-.05, .05)))
# the store: two wings meeting at a domed corner, with a tall central block
box((-4, 3.5, .25), (16, 7, 8), "brick"); box((7, -1.5, .25), (7, 16, 8), "brick"); box((1.5, -1.5, .25), (5.5, 5.5, 10.5), "brick")
box((1.5, -1.5, 10.7), (6.3, 6.3, .5), "trim"); box((1.5, -1.5, 11.2), (5.5, 5.5, .3), "trim")
col((1.5, -1.5, 11.5), 2.9, .6, "trim", n=10); col((1.5, -1.5, 12.1), 2.7, 2.2, "slate", n=10, r2=1.4); col((1.5, -1.5, 14.2), 1.4, 1.0, "trim", n=10, r2=.2)
col((1.5, -1.5, 15.2), .12, 1.6, "iron", n=5); box((1.5, -1.5, 16.6), (.5, .5, .15), "gold")
for x in (-8, -4.5, -1, 2.5): box((x, -.05, .25), (2.4, .3, 4.6), "pane")
for x in (-8, -4.5, -1, 2.5): box((x, -.2, .25), (2.6, .2, .5), "trim"); box((x, -.2, 4.9), (2.6, .2, .25), "trim")
for x in (4.0, 6.5, 9.0): box((x, -7.2, .25), (2.0, .3, 4.6), "pane")
for x in (4.0, 6.5, 9.0): box((x, -7.4, .25), (2.2, .2, .5), "trim"); box((x, -7.4, 4.9), (2.2, .2, .25), "trim")
for x in (-8, -4.5, -1, 2.5, 4.0, 6.5, 9.0): box((x, -7.2 if x > 3 else -.05, 5.2), (2.0, .3, .5), "trim")
# corner entrance: arch, steps, and the doorman in a great coat
box((1.5, -4.6, .25), (2.4, 1.4, 3.4), "trim"); box((1.5, -5.4, .25), (2.2, .5, 3.2), "iron"); box((1.5, -5.4, 3.2), (2.2, .5, .2), "trim")
for i in range(3): box((1.5, -5.9 - i * .5, .25 - i * .08), (3.4, .5, .12 + i * .08), "stone")
col((1.5, -6.6, .25), .35, 1.3, "coat", n=6); orb((1.5, -6.6, 1.8), .3, "skin"); col((1.5, -6.6, 2.0), .32, .3, "red", n=6, r2=.2)
col((1.5, -6.6, 2.3), .3, .2, "iron", n=6)
# the clock, big and glowing, on the central block
box((1.5, -4.45, 8.2), (2.0, .2, 2.0), "trim"); col((1.5, -4.6, 9.2), .8, .15, "clockface", n=12).rotation_euler.x = math.pi / 2
box((1.5, -4.75, 9.0), (.12, .1, .6), "iron"); box((1.75, -4.75, 9.2), (.5, .1, .1), "iron", (0, 0, .5))
lamp("POINT", (1, .9, .6), 300, (1.5, -5.4, 9.2))
# shop sign and the festive bunting and bulbs
box((-4, -.2, 7.2), (9, .3, 1.2), "iron"); box((-4, -.4, 7.4), (8.4, .1, .9), "sign")
lamp("POINT", (1, .1, .1), 500, (-4, -1.2, 7.8))
for i in range(9):
    t = i / 8; box((-11.2 + t * 11, -.15, 5.6 + math.sin(t * math.pi) * .8), (.18, .18, .18), "bulb")
for i in range(7):
    t = i / 6; box((3.2 + t * 7.6, -7.25, 5.6 + math.sin(t * math.pi) * .8), (.18, .18, .18), "bulb")
# delivery carts and sacks, a winter tree, a lamppost
for cx, cy, ang in ((-9, -9.5, .1), (-4.5, -9.5, -.05)):
    box((cx, cy, .75), (2.2, 1.3, .3), "wood", (0, 0, ang)); box((cx + .9, cy, 1.05), (.1, 1.3, .9), "wood", (0, 0, ang))
    for sy in (-.5, .5): col((cx, cy + sy, .35), .35, .15, "iron", n=7).rotation_euler.x = math.pi / 2
    for k in range(2): orb((cx - .5 + k * .6, cy, 1.2), .38, "trim", (1, 1, 1.1))
box((-11, -9.5, .25), (1.6, 1.0, .6), "wood"); box((-11, -9.5, .85), (1.2, .8, .4), "trim")
col((-12, -4.5, .25), 1.2, 1.8, "green", n=7, r2=.2); col((-12, -4.5, 2.0), .9, 1.6, "green", n=7, r2=.1)
col((-12, -4.5, 3.4), .6, 1.2, "green", n=7, r2=.05); col((-12, -4.5, 4.6), .05, .5, "gold", n=5)
for z in (1.0, 2.2, 3.2): col((-12, -4.5, z), .5, .05, "bulb", n=7)
col((-12, -4.5, 4.6), .2, .3, "bulb", n=5)
lamp("POINT", (1, .8, .5), 300, (-12, -5.5, 2.5))
col((-2, -9.5, .25), .1, 4.5, "iron", n=5); box((-2, -9.5, 4.7), (.8, .8, .5), "bulb"); box((-2, -9.5, 5.2), (1.0, 1.0, .12), "iron")
lamp("POINT", (1, .8, .5), 500, (-2, -9.5, 4.8))
lamp("SUN", (.55, .65, 1), 4.5, (-24, -14, 10), (0, 0, 2)); lamp("SUN", (1, .45, .35), 2.2, (22, 20, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 5)); co.location = t + Vector((24, -62, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
