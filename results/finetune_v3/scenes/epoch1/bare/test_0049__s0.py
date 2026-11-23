import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1326)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
dirt, wood, wood2, leaf, leaf2, mango, mango2, pine, pine2, scale, scale2, dragon, skin, shirt, hat, steel, bulb = (tone(c) for c in (
    (.14, .1, .06), (.3, .17, .08), (.2, .11, .06), (.1, .3, .08), (.16, .36, .1), (.9, .45, .05), (.8, .2, .03), (.5, .35, .08), (.3, .2, .05), (.9, .1, .3), (.6, .05, .25), (.6, .35, .3), (.5, .3, .2), (.7, .1, .1), (.2, .12, .08), (.7, .7, .7), (1, .6, .2)))
bulb = tone((1, .6, .2), 12)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, x, y, z, w, d, h, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return make(bm, m, (x, y, z), (0, 0, rz))
def pole(m, x, y, z, r, h, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, (x, y, z))
def fruit(m, x, y, z, r, sq=(1, 1, 1), rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return make(bm, m, (x, y, z), rot)
def glow(c, w, x, y, z):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = (x, y, z); sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=10.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
make(bm, dirt)
for i in range(5): slab(wood2, -6 + i * 3, -5.2, 0, 2.8, 1.4, .1)
# the stand: counter, shelves, back wall and posts
slab(wood, 0, 1.5, 0, 11, 3.2, 1.4); slab(wood2, 0, 1.5, 1.4, 11.4, 3.6, .2)
for x in (-5.4, 5.4):
    for y in (-.1, 3.1): pole(wood2, x, y, 0, .15, 3.6)
slab(wood2, 0, 3.1, 1.6, 11, .2, 2); slab(wood, 0, 3.0, 3.6, 11.4, .3, .2)
for i in range(5): slab(wood2, -4 + i * 2, 1.6, 2.3, 1.6, 1.2, .12)
# pyramids of fruit on the counter
for i, (x, m, m2) in enumerate(((-3.4, mango, mango2), (0, scale, scale2), (3.4, dragon, dragon))):
    for k, (n, z) in enumerate(((3, 1.6), (2, 2.15), (1, 2.7))):
        for j in range(n):
            fruit(m if (i + j) % 2 else m2, x - (n - 1) * .55 + j * 1.1, 1.3 + k * .1, z, .52 if i != 1 else .5, (1, 1, 1.1) if i == 1 else (1.15, .8, .85))
for i in range(4): fruit(scale, -2.5 + i * .9, 1.8, 1.65, .5, (1, 1, 1.2))
# the shade umbrella: striped canopy on a tall pole
pole(wood2, -6.5, -2.5, 0, .15, 4.6)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=3.6, radius2=.3, depth=1.2)
for v in bm.verts: v.co.z += .6
make(bm, shirt, (-6.5, -2.5, 4.4))
for i in range(4):
    a = i * math.pi / 4
    slab(wood, -6.5 + math.cos(a) * 1.7, -2.5 + math.sin(a) * 1.7, 4.5, .5, .5, .8, a + math.pi / 2)
# the seller with a cleaver, big enough to read
sx, sy = 6.5, -.5
pole(skin, sx, sy, 0, .45, 1.5, 6, .3); pole(shirt, sx, sy, 1.5, .5, 1.3, 6, .38)
fruit(skin, sx, sy, 3.2, .38)
slab(hat, sx, sy, 3.4, 1.1, 1.1, .3, .3); slab(hat, sx, sy - .1, 3.6, .5, .5, .4)
slab(skin, sx + .7, sy - .2, 2.2, .8, .25, .25, .5)
slab(steel, sx + 1.1, sy - .45, 2.1, .3, .9, .06, .5); slab(wood2, sx + .6, sy - .1, 2.0, .4, .2, .4)
# string lights along the back wall
for i in range(9):
    fruit(bulb, -5 + i * 1.25, 2.8, 3.3 - .25 * math.sin(i * .7), .18)
glow((1, .6, .2), 500, 0, 2.0, 3.2); glow((1, .6, .2), 300, -6.5, -2.5, 4.0)
# crates, a watermelon, a hanging sign, a few trees
for x, y in ((-8, 4), (8.5, 3)):
    for k in range(3): slab(wood2 if k % 2 else wood, x, y, k * .5, 1.6, 1.4, .5, k * .1)
for i in range(5): fruit(leaf2, -8.5 + i * .5, 3.8, 1.5, .45, (1.1, 1, .8))
slab(wood2, -1, 2.7, 2.4, 2.2, .1, .8)
for x, y, h in ((-8.5, -6, 3.5), (9, -5, 4.2)):
    pole(wood2, x, y, 0, .3, h, 5, .2)
    for k in range(3): fruit(leaf if k % 2 else leaf2, x + random.uniform(-.4, .4), y, h + k * .8, 1.7 - k * .4, (1, 1, .8))
for c, w, p in (((1, .5, .2), 5, (-26, -14, 8)), ((.2, .7, .8), 2.2, (22, 24, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((8, -42, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
