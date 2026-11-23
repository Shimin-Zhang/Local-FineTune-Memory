import bpy, bmesh, math, random
from mathutils import Vector
random.seed(453)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def shade(rgb, glow=0, rough=.85):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
lawn, lawn2, bark, leaf, leaf2, leaf3, path, pond, stone, plank, iron, pad = (shade(c) for c in (
    (.1, .2, .08), (.14, .26, .1), (.2, .12, .07), (.07, .24, .1), (.12, .3, .08), (.2, .3, .08), (.45, .38, .27), (.05, .2, .26), (.35, .34, .33), (.35, .2, .1), (.08, .08, .1), (.5, .45, .35)))
lamp = shade((1, .75, .35), 14); pad = shade((1, .8, .4), 6)
def shape(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, loc, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return shape(bm, m, loc, rot)
def cone(m, loc, r, h, n=6, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, loc)
def clump(m, loc, r, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.85, 1.15), v.co.y * random.uniform(.85, 1.15), v.co.z * sq))
    return shape(bm, m, loc)
def line(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return shape(bm, m)
def shine(kind, c, w, loc, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = loc; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=12, depth=3.4)
for v in bm.verts:
    v.co.z -= 1.7
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .2)))
shape(bm, lawn)
# winding path made of slabs, with a pond of stone edge
for i, (x, y, a) in enumerate(((-9, -6, .4), (-6.5, -5, .2), (-4, -4.2, .1), (-1.5, -3.6, -.2), (1, -3.4, -.3), (3.5, -3.8, -.5), (6, -4.6, -.6), (8.2, -6, -.8))):
    slab(path, (x, y, 0), (2.6, 2.0, .1), (0, 0, a))
slab(path, (0, -1.2, 0), (2.4, 2.4, .1), (0, 0, .3)); slab(path, (2, 1, 0), (2.4, 2.4, .1), (0, 0, .1))
pond = Vector((-3.5, 3.5, 0))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4.2, radius2=4.2, depth=.2)
for v in bm.verts: v.co.x *= 1.25; v.co.y *= .85; v.co += Vector((random.uniform(-.3, .3), random.uniform(-.3, .3), 0))
shape(bm, pond, (pond.x, pond.y, .05))
for i in range(14):
    a = i * math.tau / 14; clump(stone, (pond.x + math.cos(a) * 4.9, pond.y + math.sin(a) * 3.6, .1), random.uniform(.35, .6))
for i in range(6): clump(pad, (pond.x + random.uniform(-2, 2), pond.y + random.uniform(-1.2, 1.2), .2), .45, .3)
# three trees: two round crowns and one tall cone
for tx, ty, k in ((-8, 5.5, 0), (6, 6, 1), (9.5, -1, 2)):
    cone(bark, (tx, ty, 0), .55, 2.6, 6, .35)
    if k == 2:
        for j, (r, z) in enumerate(((2.2, 2.2), (1.8, 3.4), (1.2, 4.6))): cone(leaf if j % 2 else leaf2, (tx, ty, z), r, 1.8, 7, .1)
    else:
        for j in range(4): clump((leaf, leaf2, leaf3)[(j + k) % 3], (tx + random.uniform(-.9, .9), ty + random.uniform(-.9, .9), 3.4 + random.uniform(0, 1.2)), random.uniform(1.5, 2.0))
# bench with iron legs, back slats and armrests
bx, by = 2.8, -.4
slab(plank, (bx, by, .75), (3.2, 1.0, .15)); slab(plank, (bx, by + .5, 1.1), (3.2, .15, .9), (-.15, 0, 0))
for sx in (-1.3, 1.3):
    for sy in (-.3, .35): slab(iron, (bx + sx, by + sy, 0), (.14, .14, .8))
for sx in (-1.5, 1.5): slab(iron, (bx + sx, by, .8), (.12, .9, .12)); slab(iron, (bx + sx, by + .45, .8), (.12, .12, .6))
# lamp post, flower beds, bushes and a few fallen leaves
line(iron, (-1.5, -1.2, 0), (-1.5, -1.2, 4.2), .2); slab(lamp, (-1.5, -1.2, 4.2), (.7, .7, .8)); slab(iron, (-1.5, -1.2, 5.0), (.9, .9, .15))
shine("POINT", (1, .75, .35), 500, (-1.5, -1.2, 4.6))
for fx, fy in ((4.5, 1.8), (-1, 6.5), (-6, 1.5), (8, 2.5)):
    slab(iron, (fx, fy, 0), (2.4, 1.4, .4))
    for j in range(5): clump((lamp, pad, leaf2)[j % 3], (fx - .9 + j * .45, fy + (j % 2 - .5) * .5, .7), .3, 1)
for x, y in ((-7, -2), (0, 5.5), (7, -1), (-2, -7.5), (10, 5), (-10, 1)): clump(leaf2 if x > 0 else leaf, (x, y, .3), random.uniform(.6, 1.0), .8)
for i in range(12): clump(leaf3, (random.uniform(-9, 9), random.uniform(-8, 8), .1), .18, .4)
shine("SUN", (1, .6, .3), 5, (-26, -14, 8), (0, 0, 1)); shine("SUN", (.3, .6, .75), 2.2, (22, 20, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .025, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((8, -52, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
