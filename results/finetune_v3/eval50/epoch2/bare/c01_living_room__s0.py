import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1643)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
R = {}
def dye(k, c, e=0, r=.85):
    m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    R[k] = m
dye("plank", (.2, .12, .07)); dye("plank2", (.16, .09, .055)); dye("wall", (.12, .15, .22)); dye("rug", (.35, .08, .1)); dye("rug2", (.5, .3, .12))
dye("sofa", (.12, .3, .3)); dye("sofa2", (.08, .22, .22)); dye("cushion", (.6, .45, .2)); dye("wood", (.28, .16, .08)); dye("brass", (.7, .5, .15), 0, .4)
dye("lamp", (1, .65, .25), 14); dye("book1", (.5, .1, .1)); dye("book2", (.1, .25, .4)); dye("book3", (.15, .35, .2)); dye("frame", (.8, .75, .65)); dye("plant", (.1, .35, .12)); dye("pot", (.5, .22, .15))
def mk(bm, k, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(R[k]); return o
def slab(p, s, k, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * f, v.co.y * s[1] * f, (v.co.z + .5) * s[2]))
    return mk(bm, k, p, (0, 0, rz))
def post(p, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, p)
def ball(p, r, k, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mk(bm, k, p)
def glow(kind, p, c, w, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab, planks laid in two tones, rough tapered underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co.x *= .8; v.co.y *= .8; v.co.z -= random.uniform(0, .6)
    v.co = Vector((v.co.x * 14, v.co.y * 12, v.co.z * 2.4 - 1.2))
mk(bm, "plank2")
for i in range(14): slab((-6.3 + i, 0, 0), (.96, 11.6, .1), "plank" if i % 2 else "plank2")
# two walls with a framed picture and a shelf
slab((0, 5.6, 0), (14, .5, 6.2), "wall"); slab((-6.8, 0, 0), (.5, 11.6, 6.2), "wall")
slab((0, 5.25, 0), (13.4, .15, .35), "wood"); slab((-6.45, 0, 0), (.15, 11.2, .35), "wood")
slab((-1.5, 5.3, 3.2), (2.6, .1, 1.8), "frame"); slab((-1.5, 5.24, 3.3), (2.2, .08, 1.5), "book2")
ball((-1.5, 5.15, 3.9), .5, "cushion", .6)
slab((2.5, 5.2, 3.6), (3.4, .8, .15), "wood")
for i in range(6): slab((1.4 + i * .5, 5.2, 3.75), (.3, .4, .8 + (i % 3) * .15), ("book1", "book3", "book2")[i % 3])
# rug
slab((.5, -1.5, .1), (8.5, 5.2, .12), "rug", 0, .96); slab((.5, -1.5, .22), (6.5, 3.8, .06), "rug2", 0, .96)
# sofa: base, back, arms, seat and back cushions, throw pillows
slab((-1.5, 3.2, .1), (6.4, 2.6, 1.0), "sofa2"); slab((-1.5, 4.2, 1.1), (6.4, .8, 1.8), "sofa")
slab((-4.5, 3.2, 1.1), (.8, 2.6, 1.2), "sofa"); slab((1.5, 3.2, 1.1), (.8, 2.6, 1.2), "sofa")
for i in range(3):
    slab((-3.3 + i * 1.8, 3.1, 1.1), (1.7, 1.9, .5), "sofa", 0, .95); slab((-3.3 + i * 1.8, 4.0, 1.5), (1.6, .5, 1.2), "sofa2", 0, .9)
slab((-3.6, 3.9, 2.2), (.9, .4, .8), "cushion", .4); slab((.4, 3.9, 2.2), (.9, .4, .8), "book1", -.3)
# coffee table with books and a vase
slab((.5, -.3, .1), (3.2, 1.8, .25), "wood", 0, .95)
for sx in (-1, 1):
    for sy in (-1, 1): slab((.5 + sx * 1.4, -.3 + sy * .7, .1), (.18, .18, .9), "wood")
slab((-.2, -.3, 1.0), (.9, .6, .12), "book1", .2); slab((-.1, -.3, 1.12), (.8, .5, .1), "book3", .5)
post((1.2, -.3, 1.0), .22, .55, 6, "brass", .3); post((1.2, -.3, 1.55), .12, .1, 6, "lamp")
# floor lamp: base, stem, glowing shade
post((-5.2, 1.2, .1), .5, .15, 8, "brass"); post((-5.2, 1.2, .25), .08, 3.8, 5, "brass")
post((-5.2, 1.2, 4.0), .55, 1.2, 8, "lamp", .4); glow("POINT", (-5.2, 1.2, 4.2), (1, .65, .25), 700)
# side table with a plant
slab((4.8, 3.2, .1), (1.4, 1.4, 1.0), "wood"); post((4.8, 3.2, 1.1), .3, .5, 6, "pot", .4); ball((4.8, 3.2, 2.1), .5, "plant", 1.3)
# armchair and a side stool
slab((5.0, -1.5, .1), (2.0, 2.0, .9), "sofa2", .3); slab((5.3, -.6, 1.0), (2.0, .5, 1.4), "sofa", .3)
# window light and lamp light
glow("SUN", (20, -22, 10), (.6, .75, 1), 4.5, (0, 0, 1)); glow("SUN", (24, 22, 10), (1, .55, .3), 2, (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.2)); co.location = t + Vector((13, -38, 27))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
