import bpy, bmesh, math, random
from mathutils import Vector
random.seed(543)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, em=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .6
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
wood, peel, peel2, leaf, stem, soil = dye((.2, .12, .07)), dye((.85, .3, .03)), dye((.7, .2, .02)), dye((.12, .4, .1)), dye((.25, .16, .08)), dye((.12, .08, .06))
lamp, glow = dye((1, .6, .2), 14), dye((1, .5, .1), 6)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(m, at, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, rot)
def rod(m, at, r, h, n=5, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def orb(m, at, r, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= sq
    return add(bm, m, at)
def lite(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# floating wooden board on a rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 17, v.co.y * 13, v.co.z * 2.4))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
    v.co.z -= 1.2
add(bm, soil)
cube(wood, (0, 0, 0), (16, 12, .5))
for i in range(5): cube(dye((.15, .09, .05)), (0, -5 + i * 2.5, .5), (16, .1, .02))
# the orange: a faceted sphere with dimples pressed into it
R = 3.6
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=R)
for v in bm.verts: v.co.z *= .95
dimp = []
for i in range(30):
    d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized()
    dimp.append(d)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        if (v.co - d * R).length < 1.0: v.co -= d * .3 * (1 - (v.co - d * R).length / 1.0)
add(bm, peel)
for i, d in enumerate(dimp):
    cube(peel2, d * (R + .02), (.9, .9, .08), d.to_track_quat('Z', 'Y').to_euler())
# stem nub, a leaf, a second small leaf and a highlight spot
rod(stem, (0, 0, R * .95 - .1), .45, .6, 5, .2)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=.55, radius2=.02, depth=2.4)
add(bm, leaf, (1.0, .3, R * .95 + .4), (0, math.pi / 2 - .35, .2)).scale = (1, 1, 1)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=.4, radius2=.02, depth=1.7)
add(bm, leaf, (-.9, .2, R * .95 + .3), (0, math.pi / 2 + .3, -.2))
# a small lamp beside the fruit, glowing warm
rod(wood, (6.5, -2.5, .5), .15, 2.2, 5); rod(wood, (6.5, -2.5, .5), .5, .2, 6)
rod(glow, (6.5, -2.5, 2.7), .5, .8, 6, .3); lite((6.5, -2.5, 3.2), (1, .55, .15), 700)
# a few orange slices on a small plate
rod(dye((.7, .65, .6)), (-5.5, -2.5, .5), 2.2, .2, 8)
for i in range(3):
    a = i * .6
    rod(peel, (-5.5 + math.cos(a) * .5, -2.5 + math.sin(a) * .5, .7 + i * .15), 1.5, .25, 10)
    rod(lamp, (-5.5 + math.cos(a) * .5, -2.5 + math.sin(a) * .5, .95 + i * .15), 1.2, .08, 10)
lite((-5.5, -2.5, 1.6), (1, .55, .15), 200)
# a few scattered peel curls
for i in range(5): cube(peel2, (random.uniform(-2, 3), random.uniform(-4, 3), .5), (.8, .15, .05), (0, 0, random.uniform(0, 3)))
for col, w, p in (((1, .55, .25), 5, (-22, -14, 9)), ((.4, .6, 1), 2, (22, 16, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .012, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((6, -34, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
