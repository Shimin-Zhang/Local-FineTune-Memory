import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1205)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
W = {}
def pigment(name, rgb, em=0, metal=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    W[name] = m
for k, v in dict(sand=(.4, .27, .14), cliff=(.3, .17, .1), cliff2=(.22, .12, .08), floor=(.28, .17, .09), dark=(.01, .008, .008), bone=(.7, .65, .5), iron=(.1, .1, .12),
                 flag=(.7, .06, .08), flag2=(.9, .75, .1), hide=(.5, .3, .15), wood=(.2, .12, .07), boulder=(.25, .2, .18)).items(): pigment(k, v)
pigment("gem", (.3, .9, 1), 5); pigment("gem2", (.8, .2, 1), 5); pigment("gem3", (.2, 1, .4), 5); pigment("torch", (1, .5, .1), 14); pigment("eye", (.2, 1, .3), 10)
def shape(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(W[k]); return o
def block(at, s, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return shape(bm, k, at, rot)
def post(at, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, k, at)
def pebble(at, r, k, sq=(1, 1, .8)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.85, 1.15)
    return shape(bm, k, at)
def lamp(at, rgb, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13, depth=3.2)
for v in bm.verts:
    v.co.x *= 1.15; v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
shape(bm, "sand")
# canyon wall of stacked strata with a ledge, and a flat floor of packed sand
for i, (y, h, k) in enumerate(((11.5, 5.5, "cliff"), (8.5, 5.0, "cliff2"), (5.8, 4.5, "cliff"))):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * 24 * random.uniform(.95, 1.05), v.co.y * (y - h / 2 + 1), (v.co.z + .5) * h))
    shape(bm, k)
block((0, 3.8, 0), (24, 4.6, 1.0), "floor"); block((0, 3.8, 1.0), (24, 4.6, .25), "cliff2")
for i in range(9): pebble((random.uniform(-11, 11), random.uniform(-9, 2), .1), random.uniform(.5, 1.1), "boulder", (1.2, 1, .7))
# round tunnel mouths: dark hole, stone rim, ladder up to the topmost one
for x, z, r in ((-7, 3.2, 1.2), (-2.5, 5.2, 1.0), (2, 3.4, 1.1), (6.5, 5.0, .9), (-4.5, 6.8, .8), (4, 6.6, .9)):
    post((x, 1.4, z - r), r * 1.4, .3, 8, "bone", r * 1.4); post((x, 1.55, z - r), r, .2, 8, "dark")
    for s in (-1, 1): block((x + s * r * .8, .9, z - r * 1.3), (.15, .15, r * 1.3), "wood")
    for k in range(4): block((x, .9, z - r * 1.3 + k * r * .35), (r * 1.6, .1, .08), "wood")
# trap-laden entry: spiked pit, trip wire, trip board, trip barrel
block((0, -2.2, 0), (4.2, 3.2, .15), "dark")
for i in range(7):
    for s in (-1, 1):
        x = -2.4 + i * .8
        post((x, -2.2 + s * 1.7, .1), .12, .9, 5, "bone", .02)
for s in (-1, 1): block((s * 2.4, -2.2, 0), (.25, 3.6, .3), "wood")
for s in (-1, 1): post((s * 3.2, -2.2, 0), .15, 2.6, 5, "wood"); post((s * 3.2, -2.2, 2.6), .1, .5, 5, "bone", .05)
block((0, -2.2, 2.6), (6.6, .05, .05), "bone")
block((-5.5, -3.5, 0), (1.2, 1.2, .3), "wood", (0, 0, .4)); block((-5.5, -3.5, .3), (.1, .1, 1.6), "wood"); block((-5.5, -3.5, 1.9), (1.4, .12, .12), "wood")
post((5.5, -3.5, 0), .5, 1.2, 7, "wood", .5); post((5.5, -3.5, 1.2), .5, .15, 7, "bone", .5)
# pile of shiny stones
for i in range(16):
    a, r = random.uniform(0, 6.28), random.uniform(0, 1.6)
    pebble((-1 + r * math.cos(a), -5.5 + r * math.sin(a) * .8, .25 + (1.6 - r) * .15), random.uniform(.25, .45), random.choice(("gem", "gem2", "gem3")))
lamp((-1, -5.5, 1.0), (.4, .9, 1), 500)
# tiny banner on a pole with a kobold skull
post((-9, -4.5, 0), .12, 6.0, 5, "wood"); block((-8.0, -4.5, 4.2), (1.9, .08, 1.4), "flag"); block((-8.0, -4.5, 5.0), (1.9, .1, .3), "flag2")
pebble((-8.0, -4.5, 4.2), .35, "bone", (1, 1, 1.1)); block((-8.0, -4.8, 4.1), (.3, .1, .1), "dark")
# torches on the wall and a kobold guard at the entry
for x in (-6, 6):
    post((x, 1.0, 1.0), .1, 1.8, 5, "wood"); post((x, 1.0, 2.8), .3, .5, 6, "torch", .15); lamp((x, .2, 3.2), (1, .5, .1), 300)
pebble((2.5, -3.0, .8), .55, "hide", (1, 1, 1.2)); pebble((2.5, -3.0, 1.6), .35, "hide"); block((2.5, -3.0, 1.7), (.15, .15, .3), "bone")
for s in (-1, 1): block((2.5 + s * .12, -3.3, 1.6), (.12, .1, .1), "eye")
block((2.5, -3.0, 1.1), (.1, .1, 1.0), "bone"); block((2.5, -3.0, .9), (.9, .1, .1), "bone"); lamp((2.5, -3.5, 1.6), (.2, 1, .3), 60)
for col, w, p in (((1, .55, .25), 5.5, (-26, -18, 8)), ((.4, .5, 1), 2.2, (22, 26, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("canyon"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .025, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((6, -62, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
