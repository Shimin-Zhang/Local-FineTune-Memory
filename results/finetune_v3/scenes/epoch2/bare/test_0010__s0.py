import bpy, bmesh, math, random
from mathutils import Vector
random.seed(498)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def clay(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
mud, root, bark, leaf, leaf2, fur, belly, fish, water, ripple, fire, stone = (
    clay((.2, .12, .07)), clay((.3, .17, .09)), clay((.18, .1, .06)), clay((.08, .22, .08)), clay((.14, .26, .06)), clay((.35, .2, .1)), clay((.6, .45, .3)),
    clay((.7, .72, .75), rough=.4), clay((.04, .16, .22), rough=.15), clay((.4, .8, 1), em=2.5), clay((1, .5, .1), em=14), clay((.3, .3, .3)))
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return shape(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, at)
def lump(at, r, m, sq=1, sx=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq; v.co.x *= sx
    return shape(bm, m, at)
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return shape(bm, m)
def shine(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13.5, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .2)))
shape(bm, mud)
# river in front, with a ripple trail of glowing rings leading to the den
cube((0, -8.6, 0), (21, 7.5, .12), water)
for i in range(7):
    t = i / 6; cone((2.2 * math.sin(t * 5) * .6 + 1, -5.5 - t * 5.2, .13), .5 + i * .12, .06, 7, ripple, .5 + i * .12)
for x, y in ((-6, -6), (6.5, -5.5), (-8, -9), (8, -9.5)): lump((x, y, .1), random.uniform(.5, .9), stone, .6)
# the bank: a raised shelf with a cutaway den, earth walls, a hidden chamber with two cubs and fish bones
cube((-1.5, 3.5, 0), (14, 9, 1.6), bark)
cube((-1.5, 4.6, 1.6), (13, 7, 3.2), mud)
cube((-1.5, 2.2, 1.6), (6, .3, 2.2), clay((.02, .015, .015)))
for i in range(5): cube((-4.4 + i * 1.5, 1.5, 1.6), (.9, .3, .25 + .1 * (i % 3)), root)
# cubs curled up, one with paws over its nose
for cx, cy, rz in ((-2.8, 4.2, .3), (.6, 4.8, -.4)):
    lump((cx, cy, 2.1), .85, fur, .75, 1.2).rotation_euler.z = rz
    lump((cx + .75 * math.cos(rz), cy + .75 * math.sin(rz), 2.4), .5, fur)
    cone((cx + .95 * math.cos(rz), cy + .95 * math.sin(rz), 2.4), .12, .3, 4, belly, .05)
    for s in (-1, 1): lump((cx + .6 * math.cos(rz) - s * .25 * math.sin(rz), cy + .6 * math.sin(rz) + s * .25 * math.cos(rz), 2.8), .16, fur)
    lump((cx - .85 * math.cos(rz), cy - .85 * math.sin(rz), 2.0), .22, fur)
# fish bones: spine, ribs, tail, larger than life
for k, (bx, by) in enumerate(((-1.2, 3.2), (2.2, 3.5))):
    rod((bx - 1, by, 1.7), (bx + 1, by, 1.7), .1, fish)
    for j in range(5): rod((bx - .6 + j * .3, by, 1.7), (bx - .6 + j * .3, by - .5, 1.7), .05, fish); rod((bx - .6 + j * .3, by, 1.7), (bx - .6 + j * .3, by + .5, 1.7), .05, fish)
    rod((bx + 1, by, 1.7), (bx + 1.5, by - .4, 1.7), .06, fish); rod((bx + 1, by, 1.7), (bx + 1.5, by + .4, 1.7), .06, fish)
# the tree: trunk rising behind the den, a canopy, and roots arching over the entrance like a cave roof
cone((-1.5, 7.5, 0), 1.6, 9, 7, bark, 1.0)
for i in range(5):
    a = i * 1.3; rod((-1.5, 7.5, 6.5), (-1.5 + 3 * math.cos(a), 7.5 + 3 * math.sin(a), 10.5), .35, bark)
for i in range(6):
    a = i * 1.05; lump((-1.5 + 3.2 * math.cos(a), 7.5 + 3.2 * math.sin(a), 11 + random.uniform(0, 1.5)), random.uniform(2, 2.8), leaf if i % 2 else leaf2, .7)
lump((-1.5, 7.5, 12), 3.2, leaf2, .7)
for i in range(7):
    a = -1.9 + i * .62; x = -1.5 + 3.4 * math.cos(a) * 1.0
    rod((-1.5, 7.5, 6.2), (x, 7.5 - 4.2, 5.0), .45, root); rod((x, 7.5 - 4.2, 5.0), (x * .8 - .3, 2.6, 4.3 - (i % 2) * .3), .3, root)
    rod((x, 7.5 - 4.2, 5.0), (x * .8 - .3, 2.0, .3), .2, root)
# a small fire laid out in the den, the glow of the hidden chamber
cone((-1.5, 5.2, 1.6), .6, .2, 6, stone, .5); cone((-1.5, 5.2, 1.8), .45, .8, 5, fire, .05)
shine("POINT", (1, .5, .1), 700, (-1.5, 4.2, 2.6)); shine("POINT", (.4, .8, 1), 250, (1, -8, 1.2))
for x, y, h in ((-8, 5, 3), (-9, 1, 2.4), (7, 6, 3.4), (9, 2, 2.6), (6, 9, 3)):
    cone((x, y, 0), .35, h, 5, bark, .2); lump((x, y, h + .8), 1.5, leaf if h > 3 else leaf2, .9)
for i in range(18):
    x, y = random.uniform(-11, 11), random.uniform(-3, 11)
    if abs(x + 1.5) < 7 and y > -1: continue
    cone((x, y, 0), .12, random.uniform(.5, 1.1), 4, leaf2, .02)
shine("SUN", (1, .6, .35), 5, (-26, -20, 9), (0, 0, 3)); shine("SUN", (.3, .6, .8), 2.2, (24, 24, 12), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .025, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((14, -62, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
