import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1659)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def tint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, v in dict(soil=(.2, .12, .07), stone=(.3, .22, .15), red=(.4, .07, .05), vine=(.12, .2, .06), vine2=(.2, .22, .08),
                 trunk=(.2, .12, .07), grape=(.12, .05, .2), leaf=(.06, .17, .06), path=(.35, .27, .18)).items(): tint(k, v)
tint("window", (1, .6, .2), 10); tint("shrine", (1, .5, .15), 12)
def make(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); me.materials.append(M[k]); return o
def blk(x, y, z, w, d, h, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return make(bm, k, (x, y, z), (0, 0, rz))
def col(x, y, z, r, h, k, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, k, (x, y, z))
def leaf(x, y, z, r, k):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2)
    return make(bm, k, (x, y, z))
def lamp(x, y, z, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = (x, y, z); sc.collection.objects.link(o)
# hillside plot
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 22, v.co.y * 22, v.co.z * 3))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
    else: v.co.z += random.uniform(-.06, .06)
make(bm, "soil", (0, 0, -1.5))
# the house: three tiers with flat terraces, each smaller than the last
for z, w, d, h in ((0, 11, 8, 3.2), (3.2, 8.4, 6, 3.0), (6.2, 6, 4.6, 2.8)):
    blk(-1, 1, z, w, d, h, "stone")
    blk(-1, 1, z + h, w + .5, d + .5, .25, "stone")
    for i in range(int(w / 1.9)): blk(-1 - w / 2 + 1.2 + i * 1.9, 1 - d / 2 - .05, z + h + .25, .25, .25, .3, "red")
# red columns on the ground floor, with a lintel and window shaft
for i in range(5):
    x = -5.5 + i * 2.2; col(x, -3.3, 0, .32, 3.2, "red", 6, .26)
    blk(x, -3.3, 3.2, .8, .8, .25, "red")
blk(-1, -3.3, 3.2, 11, .5, .25, "red")
blk(-1, -3.3, 0, .5, .1, 3.2, "red")
blk(1.4, -3.3, 0, .5, .1, 3.2, "red")
blk(-1, -3.3, 0, .9, .1, 3.2, "red")
blk(-1, -3.3, 0, .1, .1, 3.2, "red")
blk(-1, -3.3, 0, .5, .1, 3.2, "red")
blk(-1, -3.3, 0, 1.6, .1, .6, "red")
blk(-1, -3.3, 2.6, 1.6, .1, .6, "red")
blk(-1, -3.3, 1.2, .9, .1, 1.4, "red")
blk(-1, -3.4, 1.2, .9, .1, 1.4, "window")
blk(-1, -3.5, 0, 2.2, .3, .3, "stone"); blk(-1, -3.5, 3.2, 2.2, .3, .3, "stone")
# windows glowing on the upper tiers
for x in (-3.5, 1.5): blk(x, -2.2, 3.8, 1.0, .1, 1.6, "window")
for x in (-2.5, 1): blk(x, -1.4, 6.8, .8, .1, 1.4, "window")
lamp(-1, -4.2, 1.8, (1, .6, .2), 350); lamp(-1, -3.5, 4.2, (1, .6, .2), 250)
# stairs to the terrace on the right
for i in range(5): blk(6.2 + i * .5, -3.5, 0, .5, 1.2, .4 * (i + 1), "stone")
# small shrine room, glowing
blk(-8, -4.5, 0, 3.2, 2.6, 2.6, "stone")
blk(-8, -4.5, 2.6, 3.6, 3.0, .3, "red")
blk(-8, -5.85, 0, 1.0, .1, 2.2, "shrine"); blk(-8, -5.85, 2.2, 1.0, .1, .4, "red")
lamp(-8, -6.8, 1.5, (1, .5, .15), 300)
# vineyard: rows of vines on posts and wires, grapes and leaves
for r in range(4):
    y = -8 + r * 2.2
    for i in range(7):
        x = -9 + i * 3.0
        col(x, y, 0, .08, 1.2, "trunk", 4)
        leaf(x, y, 1.4, .6, "vine" if i % 2 else "vine2"); leaf(x, y + .2, 1.7, .35, "leaf")
        if (i + r) % 2: leaf(x + .3, y - .3, .9, .22, "grape")
    blk(-1, y, 1.0, 21, .04, .04, "trunk")
# path and a few olive trees
for i in range(6): blk(-1 + random.uniform(-.3, .3), -5.2 - i * 1.2, 0, 1.4, 1.0, .06, "path", random.uniform(-.1, .1))
for x, y in ((8.5, -6), (9, 2)):
    col(x, y, 0, .25, 2.4, "trunk", 5, .15)
    for dx, dz in ((-.8, 2.6), (.7, 2.8), (0, 3.3)): leaf(x + dx, y, dz, 1.1, "leaf")
# sunset: low amber key, purple rim
for c, e, p in (((1, .5, .22), 6, (-24, -14, 7)), ((.55, .3, .8), 2.4, (18, 20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.035, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, -1, 3)); co.location = t + Vector((8, -62, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
