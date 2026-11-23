import bpy, bmesh, math, random
from mathutils import Vector
random.seed(534)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
mud, granite, granite2, moss, moss2, fern, cap, stem, rune, spore, peat = (dye(c) for c in (
    (.07, .06, .05), (.22, .22, .24), (.15, .15, .17), (.1, .3, .08), (.18, .38, .1), (.1, .32, .12), (.9, .1, .12), (.5, .45, .35), (.3, 1, .8), (.5, 1, .9), (.05, .07, .04)))
rune = dye((.2, 1, .75), 9); spore = dye((.4, 1, .8), 3)
def obj(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("o"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blob(at, r, m, flat=.7, jit=.25, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit))) * r; v.co.z *= flat
    return obj(bm, m, at)
def stem_(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return obj(bm, m)
def shine(at, c, w):
    L = bpy.data.lights.new("s", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
# forest-floor base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4, radius2=9, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
obj(bm, mud)
# the boulder: a faceted mass, moss caps on its upper faces
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=3.4)
for v in bm.verts:
    v.co += Vector((random.uniform(-.4, .4), random.uniform(-.4, .4), random.uniform(-.4, .4)))
    v.co.z *= .8; v.co.z -= .3
rock = obj(bm, granite)
for k in range(11):
    a = random.uniform(0, 6.28); r = random.uniform(0, 2.4)
    x, y = r * math.cos(a), r * math.sin(a) * .85
    z = max(0, 3.4 * .8 * math.sqrt(max(0, 1 - (r / 3.4) ** 2)) - .3 + random.uniform(-.1, .1))
    blob((x, y, z + .05), random.uniform(.7, 1.2), moss if k % 2 else moss2, .35, .3)
for k in range(7):
    a = random.uniform(0, 6.28); r = random.uniform(1.5, 3.3)
    blob((r * math.cos(a), r * math.sin(a) * .85, 0), random.uniform(.6, 1.0), granite2, .8, .2)
# carved runes on the front face, glowing
for i, (dx, dz, h) in enumerate(((-.9, 1.4, .9), (-.3, 1.55, 1.2), (.35, 1.4, .8), (1.0, 1.2, 1.0))):
    stem_((dx, -3.0, dz), (dx, -3.0, dz + h), .12, rune)
    if i % 2: stem_((dx, -3.0, dz + h * .5), (dx + .45, -3.0, dz + h * .85), .1, rune)
    else: stem_((dx, -3.0, dz + h * .6), (dx - .45, -3.0, dz + h * .3), .1, rune)
shine((0, -4.2, 1.5), (.3, 1, .75), 600)
# ferns, mushrooms, roots, peat
for k in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(4.2, 7.2)
    x, y = r * math.cos(a), r * math.sin(a) * .9
    for j in range(5):
        b = a + (j - 2) * .35
        stem_((x, y, .1), (x + 1.1 * math.cos(b), y + 1.1 * math.sin(b), .1 + .5 * math.sin(j * 1.2)), .08, fern)
    blob((x, y, .1), .35, moss2, .5, .2)
for k, (x, y) in enumerate(((4.4, -1.2), (4.9, -.4), (-4.6, 1.8), (-5.2, 1.2), (2.5, 5.2))):
    h = random.uniform(.7, 1.2)
    stem_((x, y, 0), (x, y, h), .16, stem)
    blob((x, y, h + .1), .45, cap, .6, .05)
for k in range(5):
    a = k * 1.3 + .5
    stem_((3.2 * math.cos(a), 2.6 * math.sin(a), .2), (7 + random.uniform(0, 1.5) * math.cos(a), 5.5 * math.sin(a), .1), .22, peat)
for k in range(22):
    a = random.uniform(0, 6.28); r = random.uniform(4, 8)
    blob((r * math.cos(a), r * math.sin(a) * .9, .15), random.uniform(.15, .3), moss if k % 2 else peat, .6, .2)
# drifting spores
for k in range(16):
    blob((random.uniform(-5, 5), random.uniform(-4, 4), random.uniform(1.5, 6)), .09, spore, 1, .1)
# misty teal-green key, pale moon rim
for c, w, at in (((.45, .9, .7), 4.5, (-16, -12, 7)), ((.55, .6, 1), 2, (14, 16, 9))):
    s = bpy.data.lights.new("sun", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("sun", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("mist"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .03, .03, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 1.6)); co.location = tg + Vector((6, -30, 17))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
