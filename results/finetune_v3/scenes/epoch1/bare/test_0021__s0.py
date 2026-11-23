import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1444)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
col = {}
def tint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    col[name] = m
for k, c in dict(silt=(.12, .1, .08), water=(.05, .15, .17), shore=(.3, .22, .15), plank=(.4, .25, .13), rope=(.55, .45, .25), mussel=(.04, .06, .1),
                 hull=(.5, .08, .08), hull2=(.08, .15, .22), white=(.6, .6, .58), slate=(.15, .17, .2), stone=(.35, .3, .25), leaf=(.12, .22, .1)).items(): tint(k, c)
tint("lamp", (1, .75, .3), 12); tint("beacon", (1, .2, .1), 20)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(col[m]); return o
def blk(w, d, h, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mk(bm, m, at, rot)
def cyl(r, h, n, m, at, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def bar(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return mk(bm, m)
def bulb(c, w, at):
    L = bpy.data.lights.new("b", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
# floating slab: silt bed with a rough keel, water on top
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 24 + random.uniform(-1.5, 1.5), v.co.y * 20 + random.uniform(-1.5, 1.5), -4.5 + random.uniform(-1, 1)))
    else: v.co = Vector((v.co.x * 30, v.co.y * 26, 0))
mk(bm, "silt")
blk(29.4, 25.4, .4, "water", (0, 0, -.05))
# shore at the back with a village: stone houses, slate roofs, a church tower, trees
blk(30, 6, 1.2, "shore", (0, 10.5, 0))
for i, (x, w) in enumerate(((-12, 3.4), (-8, 3.0), (-4, 3.6), (0.5, 3.2), (5, 3.4), (9.5, 3.0))):
    blk(w, 3.0, 2.2 + (i % 2) * .4, "stone", (x, 10.8, 1.2))
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        if v.co.z > 0: v.co.y = 0
        v.co = Vector((v.co.x * (w + .6), v.co.y * 3.6, (v.co.z + .5) * 1.4))
    mk(bm, "slate", (x, 10.8, 3.4 + (i % 2) * .4))
    blk(.8, .1, 1.0, "lamp", (x + .5, 9.25, 1.8))
blk(2.4, 2.4, 6.0, "stone", (-1.2, 11.2, 1.2)); cyl(.9, 2.4, 4, "slate", (-1.2, 11.2, 7.2), .1, (0, 0, .8))
cyl(.2, .5, 5, "lamp", (-1.2, 11.2, 9.4)); bulb((1, .7, .3), 300, (-1.2, 11.2, 9.8))
for x in (-13, 12, 13.5): cyl(.2, 2.0, 5, "plank", (x, 9.5, 1.2)); cyl(1.1, 2.0, 6, "leaf", (x, 9.5, 3.0), .1)
# mussel rafts: float frames with hanging ropes and mussel bunches
for rx, ry, rz in ((-8, 3, 0), (-1, -1, .3), (6, 4, -.2), (-4, 7, .2)):
    for sx in (-1, 1):
        for sy in (-1, 1): cyl(.25, .7, 6, "plank", (rx + sx * 1.8, ry + sy * 1.3, .1), .22)
    blk(4.0, .2, .2, "plank", (rx, ry - 1.3, .55)); blk(4.0, .2, .2, "plank", (rx, ry + 1.3, .55))
    for i in range(7):
        x = rx - 1.6 + i * .55
        bar((x, ry, .6), (x + .1, ry, .05), .06, "rope")
        for k in range(2): cyl(.13, .45, 5, "mussel", (x + .1, ry, -.35 + k * .3), .06, (math.pi, 0, 0))
# workboat with a lifting crane: hull, cabin, mast, boom, cable, hook, load
blk(5.6, 2.0, .9, "hull", (3, -6, .1), (0, 0, .3)); blk(1.8, 1.5, 1.0, "white", (3.8, -5.6, 1.0), (0, 0, .3))
blk(.9, 1.1, .5, "slate", (4.5, -5.3, 1.9), (0, 0, .3)); blk(.5, .1, .5, "lamp", (4.0, -6.5, 1.3), (0, 0, .3))
bar((2.0, -6.6, 1.0), (2.0, -6.6, 4.8), .2, "hull2"); bar((2.0, -6.6, 4.8), (0.4, -6.6, 3.6), .15, "plank")
bar((0.4, -6.6, 3.6), (0.4, -6.6, 1.2), .06, "rope"); cyl(.2, .3, 5, "lamp", (0.4, -6.6, .9), .15)
cyl(.5, .8, 6, "mussel", (0.4, -6.6, .1), .35)
cyl(.25, .5, 5, "beacon", (3.9, -5.6, 2.4)); bulb((1, .2, .1), 200, (3.9, -5.6, 3.2)); bulb((1, .75, .3), 250, (4.0, -7.2, 1.5))
# buoys and a few rocks
for x, y in ((-12, -4), (12, 0), (-2, 9), (10, -8)): cyl(.4, .8, 6, "hull", (x, y, .1), .3); cyl(.1, .5, 4, "lamp", (x, y, .9)); bulb((1, .75, .3), 120, (x, y, 1.6))
for i in range(7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.4, .9))
    for v in bm.verts: v.co *= random.uniform(.8, 1.2)
    mk(bm, "stone", (random.choice((-1, 1)) * random.uniform(12, 14), random.uniform(-9, 8), .1))
for c, e, p in (((.6, .75, .85), 4.5, (-26, -14, 10)), ((1, .55, .3), 2.2, (24, 22, 9))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .035, .045, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 2, 1.5)); co.location = t + Vector((6, -66, 42))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
