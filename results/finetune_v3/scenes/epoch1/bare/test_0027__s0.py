import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1362)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
ink = {}
def lacquer(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .8
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    ink[name] = m
for k, v in dict(bank=(.1, .17, .08), water=(.05, .16, .22), hullA=(.55, .07, .05), hullB=(.1, .22, .45), hullC=(.7, .5, .08), hullD=(.12, .38, .15),
                 gold=(.7, .45, .08), black=(.03, .03, .04), white=(.7, .65, .55), skin=(.6, .4, .3), red=(.7, .05, .04), green=(.1, .4, .15),
                 blue=(.1, .2, .6), roof=(.35, .08, .06), wood=(.3, .18, .1), flag1=(.8, .1, .05), flag2=(.85, .6, .1), flag3=(.2, .5, .2)).items(): lacquer(k, v)
lacquer("lantern", (1, .25, .05), 12); lacquer("eye", (1, .9, .3), 14)
def cast(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(ink[m]); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return cast(bm, m, at, rot)
def pole(at, r, h, m, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return cast(bm, m, at)
def egg(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return cast(bm, m, at)
def flame(c, w, at):
    L = bpy.data.lights.new("f", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("f", L); o.location = at; sc.collection.objects.link(o)
# river slab with a tapered rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 26 + random.uniform(-1.5, 1.5), v.co.y * 17 + random.uniform(-1, 1), -3.5 + random.uniform(-1, .5)))
    else: v.co = Vector((v.co.x * 30, v.co.y * 20, 0))
cast(bm, "bank")
cube((0, 0, 0), (30, 11, .3), "water")
for i in range(10): cube((-14 + i * 3.1, random.uniform(-4, 4), .3), (1.8, .12, .06), "white")
# two banks with flags and lantern posts
for sy in (-1, 1):
    cube((0, sy * 7.6, 0), (30, 4.8, 1.6), "bank"); cube((0, sy * 5.1, 0), (30, .5, .6), "wood")
    for i in range(9):
        x = -13 + i * 3.2
        pole((x, sy * 5.4, 1.6), .06, 3.2, "wood", 5)
        cube((x + .55, sy * 5.4, 4.2), (1.1, .06, .8), ("flag1", "flag2", "flag3")[i % 3])
    for i in range(4):
        x = -10 + i * 6.6; pole((x, sy * 5.0, 1.6), .08, 2.4, "wood", 5); egg((x, sy * 5.0, 4.1), .45, "lantern", (1, 1, 1.2))
# dragon boats: hull, dragon head with eye and horns, tail, paddlers and drummer
def dragon(x, y, hull, n):
    cube((x, y, .6), (12, 1.7, .9), hull); cube((x, y, 1.5), (11, .9, .12), "black")
    cube((x + 6.4, y, 1.5), (2.6, 1.0, .8), hull, (0, 0, 0)); cube((x + 7.6, y, 2.0), (1.2, .9, .7), hull)
    cube((x + 8.0, y, 2.6), (.3, .3, 1.0), "gold", (0, .3, 0)); cube((x + 8.0, y, 2.6), (.3, .3, 1.0), "gold", (0, -.3, 0))
    egg((x + 8.3, y - .5, 2.4), .17, "eye"); egg((x + 8.3, y + .5, 2.4), .17, "eye"); flame((1, .9, .3), 120, (x + 8.3, y, 2.4))
    cube((x - 6.4, y, 1.5), (2.0, .7, .8), hull); cube((x - 7.8, y, 2.2), (.5, .5, 1.2), hull, (0, .5, 0))
    for i in range(n):
        px = x - 4.4 + i * 1.4; egg((px, y, 2.1), .32, "skin"); cube((px, y, 1.7), (.5, .6, .5), ("red", "blue", "green", "gold")[i % 4])
        pole((px + .5, y + .5, 1.0), .04, 1.8, "wood", 4)
    egg((x + 3.2, y, 2.3), .4, "skin"); cube((x + 3.2, y, 1.8), (.7, .7, .5), "red"); cube((x + 3.2, y, 2.7), (1.0, 1.0, .3), "gold")
dragon(-2, -2.6, "hullA", 7); dragon(-2, 2.8, "hullB", 7); dragon(-6, -5.0, "hullC", 5); dragon(-6, 5.0, "hullD", 5)
# finish line pavilion with two posts, a roof and hanging lanterns
for sy in (-1, 1): pole((12.5, sy * 5.6, 0), .35, 6.0, "wood", 6)
cube((12.5, 0, 5.4), (1.6, 12.4, .5), "wood")
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=2.2, radius2=.3, depth=2.2)
for v in bm.verts: v.co.z += 1.1
cast(bm, "roof", (12.5, 0, 5.9), (0, 0, math.pi / 4))
for i in range(7):
    y = -4.2 + i * 1.4; egg((12.5, y, 4.9), .32, "lantern", (1, 1, 1.2))
flame((1, .25, .05), 900, (12.5, 0, 4.4))
# crowd on the far bank: little figures in bright coats
for i in range(22):
    x, y = random.uniform(-13, 13), random.uniform(6.0, 9.0)
    egg((x, y, 2.0), .3, "skin"); cube((x, y, 1.6), (.5, .5, .55), ("red", "blue", "green", "gold", "white")[i % 5])
# dusk: low orange key from the left, indigo rim behind
for c, e, p in (((1, .5, .22), 5, (-24, -14, 9)), ((.3, .35, 1), 2.4, (20, 22, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((-14, -60, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
