import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1025)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, glow=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
dirt, leaf, leaf2, wood, wood2, crate, leafgold, ember, haze, cloth = (tint(c) for c in (
    (.3, .2, .1), (.3, .38, .1), (.22, .32, .08), (.35, .22, .12), (.22, .14, .08), (.4, .27, .15), (.5, .38, .08), (.5, .08, .02), (.8, .7, .5), (.6, .55, .45)))
fire = tint((1, .45, .08), 14)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(x, y, z, w, d, h, m, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return shape(bm, m, (x, y, z), (rx, 0, rz))
def post(x, y, z, r, h, m, r2=None, n=6):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, (x, y, z))
def glow(x, y, z, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = (x, y, z); sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=11.5, depth=3.2)
for v in bm.verts:
    v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
shape(bm, dirt)
# the tobacco field: rows of plants with big leaves, in front of the shed
for r in range(5):
    for c in range(12):
        x, y = -9.5 + c * 1.7 + random.uniform(-.1, .1), -7.5 + r * 1.4
        post(x, y, 0, .06, .9, leaf2, .05, 5)
        for k in range(4):
            a = k * 1.6 + c
            cube(x + math.cos(a) * .25, y + math.sin(a) * .25, .3 + k * .17, .5, .5, .06, leaf if k % 2 else leaf2, a, .5)
# the open-sided drying shed: back wall of planks, posts, rafters, hanging racks
for i in range(12): cube(-5.5 + i * 1.0, 3.0, 0, .98, .15, 3.4, wood2 if i % 2 else wood)
for i in range(7): cube(-5.5 + i * 1.9, 3.0, 3.4, 1.9, .2, .3, wood)
for x in (-6, -3, 0, 3, 6): post(x, 0, 0, .17, 3.6, wood)
for x in (-4.5, -1.5, 1.5, 4.5): cube(x, 1.5, 3.5, .25, 3.2, .25, wood, 0, .12)
for x in (-4.5, -1.5, 1.5, 4.5):
    for k in range(7):
        y = .4 + k * .4
        cube(x, y, 3.15, .05, .05, .35, wood2)
        cube(x, y, 1.2, .6, .06, 1.95, leafgold if (k + int(x)) % 2 else leaf, 0, .03)
# crates stacked by the shed, a cart, and a drying fire pit with glowing embers
for i in range(3):
    for j in range(3 - i): cube(7.2 + j * .85, -1.5 + i * .1, i * .6, .8, .8, .6, crate, j * .1)
cube(7.2, -.5, .6, .8, .8, .6, crate, .1)
for x in (-2.5, 2.5): post(x, -3.6, .5, .5, .12, wood2, n=8)
cube(0, -3.6, .6, 5, .9, .12, wood2)
post(-8, -1, 0, .9, .3, dirt, 1.0, 7); post(-8, -1, .3, .5, .2, fire, .3, 6)
glow(-8, -1, 1.2, (1, .45, .1), 700)
# heat haze: pale shimmering bands drifting over the field
for i in range(7):
    cube(random.uniform(-6, 6), random.uniform(-6, 0), random.uniform(.5, 2.5), random.uniform(3, 6), random.uniform(2, 4), .05, haze, random.uniform(0, 3))
for i in range(5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.5, .9))
    for v in bm.verts: v.co.z *= .6
    shape(bm, leaf, (random.choice((-1, 1)) * random.uniform(8, 9.5), random.uniform(-6, 4), .3))
for col, w, p in (((1, .7, .35), 6, (-26, -16, 9)), ((.55, .5, 1), 2.2, (24, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("haze"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.045, .03, .02, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, -.5, 1.5)); co.location = t + Vector((6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
