import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1854)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
W = {}
def lacquer(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .5
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    W[name] = m
for k, v in dict(oak=(.3, .17, .08), oak2=(.22, .12, .06), brass=(.7, .5, .12), wall=(.17, .22, .16), black=(.03, .03, .035),
                 white=(.7, .7, .65), steel=(.45, .47, .5), blue=(.1, .2, .5), red=(.5, .08, .06), leather=(.35, .15, .08)).items(): lacquer(k, v)
lacquer("glass", (.5, .75, .8), .4); lacquer("dial", (1, .95, .7), 1.5); lacquer("lamp", (1, .8, .45), 30); lacquer("clockface", (1, .95, .8), 2.5)
def mould(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(k); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(k, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(W[k]); return o
def blk(k, at, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mould(bm, k, at, rot)
def cyl(k, at, r, h, n=8, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mould(bm, k, at, rot)
def ball(k, at, r, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return mould(bm, k, at)
def lit(kind, rgb, w, at, aim=None):
    l = bpy.data.lights.new(kind, kind); l.color = rgb; l.energy = w
    o = bpy.data.objects.new(kind, l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab of planks with a ragged underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 12 + random.uniform(-.8, .8), v.co.y * 11 + random.uniform(-.8, .8), -3 + random.uniform(-.8, .4)))
    else: v.co = Vector((v.co.x * 16, v.co.y * 15, 0))
mould(bm, "oak2", (0, 0, 0))
for i in range(16): blk("oak" if i % 2 else "oak2", (-7.5 + i, 0, 0), (.96, 14.8, .12))
# two walls, wainscot, a window and shelves
blk("wall", (0, 7.5, 0), (16, .5, 7.5)); blk("wall", (-8, 0, 0), (.5, 15, 7.5))
blk("oak2", (0, 7.2, 0), (16, .3, 2.4)); blk("oak2", (-7.7, 0, 0), (.3, 15, 2.4))
blk("oak", (0, 7.15, 2.4), (16, .15, .15)); blk("oak", (-7.65, 0, 2.4), (.15, 15, .15))
blk("dial", (3.5, 7.2, 3.2), (3.2, .1, 2.2)); blk("oak", (3.5, 7.1, 3.0), (3.6, .2, .2)); blk("oak", (3.5, 7.1, 5.4), (3.6, .2, .2))
for i in range(2): blk("oak", (-7.6, -4 + i * 4.5, 3.4 + i * 1.8), (.6, 4.2, .15))
# tall clock case in the corner with glowing face and pendulum
blk("oak", (-6.6, 6.0, 0), (2.2, 1.5, 6.2)); blk("oak2", (-6.6, 6.0, 6.2), (2.6, 1.8, .3)); blk("oak2", (-6.6, 5.2, 0), (2.0, .1, 1.2))
blk("black", (-6.6, 5.2, 1.2), (1.6, .1, 4.4)); blk("clockface", (-6.6, 5.1, 4.4), (1.2, .1, 1.2))
cyl("brass", (-6.6, 5.0, 1.4), .04, 3.0, 4); ball("brass", (-6.6, 5.0, 1.4), .25, (1, 1, .8))
for i in range(8): a = i * math.pi / 4; blk("black", (-6.6 + math.cos(a) * .5, 5.0, 4.4 + math.sin(a) * .5), (.08, .05, .12), (0, 0, a))
# glass cases on the back wall with rows of pocket watches
for cx in (-3.5, 1.0):
    blk("oak", (cx, 6.4, 0), (3.0, 1.4, 2.2)); blk("oak2", (cx, 6.4, 2.2), (3.2, 1.6, .15))
    for z in (.6, 1.5): blk("oak2", (cx, 6.4, z), (2.8, 1.2, .08))
    for sx in (-1, 1): blk("glass", (cx + sx * 1.45, 6.4, .15), (.06, 1.2, 2.0))
    blk("glass", (cx, 7.0, .15), (2.9, .06, 2.0))
    for z in (.68, 1.58):
        for i in range(4):
            cyl("brass", (cx - 1.0 + i * .67, 6.4, z), .2, .06, 8, rot=(math.pi / 2, 0, 0)); cyl("dial", (cx - 1.0 + i * .67, 6.35, z), .14, .04, 8, rot=(math.pi / 2, 0, 0))
# workbench with the magnifying lamp, tray of screws and tools
blk("oak", (1.5, 0, 0), (5.0, 2.4, 1.4)); blk("oak2", (1.5, 0, 1.4), (5.2, 2.6, .12))
for sx in (-2.2, 2.2):
    for sy in (-1.0, 1.0): blk("oak2", (1.5 + sx, sy, 0), (.2, .2, 1.4))
blk("black", (1.5, .6, 1.52), (.3, .3, .1)); cyl("black", (1.5, .6, 1.6), .06, 2.6, 5, rot=(.0, .3, 0)); cyl("black", (1.5, .1, 4.1), .06, 1.6, 5, rot=(0, 1.0, 0))
cyl("black", (1.5, -1.1, 3.9), .7, .3, 8, rot=(math.pi / 2, 0, 0)); cyl("lamp", (1.5, -1.25, 3.9), .5, .12, 8, rot=(math.pi / 2, 0, 0))
lit("SPOT", (1, .8, .45), 2200, (1.5, -1.1, 3.9), (1.5, 0, 1.5))
blk("brass", (3.2, -.4, 1.52), (1.6, 1.1, .1)); blk("black", (3.2, -.4, 1.6), (1.4, .9, .04))
for i in range(24):
    cyl("steel", (2.5 + (i % 8) * .2, .1 - (i // 8) * .3, 1.64), .05, .06, 5); cyl("brass", (2.5 + (i % 8) * .2, .1 - (i // 8) * .3, 1.7), .02, .04, 4)
for i in range(5): cyl("brass", (.3 + i * .17, -.4, 1.52), .05, .5, 5, rot=(0, math.pi / 2, 0))
cyl("brass", (-.4, -.3, 1.52), .12, .12, 8); cyl("brass", (-.4, -.3, 1.64), .1, .12, 8); cyl("brass", (-.4, -.3, 1.76), .08, .12, 8)
blk("leather", (.6, .8, 1.52), (.8, .5, .1)); blk("black", (-.2, .9, 1.52), (.12, .12, .3), (0, .3, 0))
# stool and a few wall tools
cyl("oak2", (-2.2, -1.0, 0), .08, 1.0, 5); cyl("oak", (-2.2, -1.0, 1.0), .5, .15, 8)
for i in range(4): blk("brass", (-7.6, -1.5 + i * 1.1, 4.2), (.1, .1, 1.0))
lit("POINT", (1, .9, .6), 350, (0, 3, 6)); lit("POINT", (1, .85, .5), 150, (-6.6, 4.0, 4.5))
lit("SUN", (1, .85, .6), 5, (24, -22, 11), (0, 0, 1)); lit("SUN", (.4, .55, 1), 2.2, (-22, 24, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 2.5)); co.location = t + Vector((16, -36, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
