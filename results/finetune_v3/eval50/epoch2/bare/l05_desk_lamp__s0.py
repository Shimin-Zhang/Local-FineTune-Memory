import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1645)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def paint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .8
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    M[name] = m
for k, v in dict(floor=(.07, .05, .04), wall=(.09, .08, .1), oak=(.3, .17, .09), oak2=(.18, .1, .06), brass=(.5, .38, .15),
                 black=(.03, .03, .035), paper=(.55, .5, .4), red=(.5, .08, .06), blue=(.1, .2, .45), green=(.1, .35, .15),
                 glass=(.1, .3, .3), rug=(.25, .08, .08)).items(): paint(k, v)
paint("shade", (1, .6, .22), 9); paint("bulb", (1, .75, .35), 18); paint("screen", (.3, .8, .6), 3)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("d"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("d", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[m]); return o
def slab(at, s, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, (0, 0, rz))
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, m)
def drum(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab with a ragged underside, rug
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 15, v.co.y * 13, v.co.z * 1.6 - .8))
    if v.co.z < 0: v.co = Vector((v.co.x * .7 + random.uniform(-.8, .8), v.co.y * .7 + random.uniform(-.8, .8), v.co.z - random.uniform(0, 1.5)))
add(bm, "floor")
slab((0, 0, 0), (11, 8, .06), "rug")
# two walls only: back and left, with skirting
slab((0, 6.4, 0), (15, .5, 7.5), "wall"); slab((-7.4, 0, 0), (.5, 13, 7.5), "wall")
slab((0, 6.1, 0), (15, .2, .5), "oak2"); slab((-7.1, 0, 0), (.2, 13, .5), "oak2")
slab((-1, 6.1, 3.6), (3.6, .1, 2.6), "oak2"); slab((-1, 6.0, 3.8), (3.2, .08, 2.2), "blue")
# desk: top, front panel, legs, drawer with a brass knob
slab((0, 0, 2.6), (8, 3.2, .3), "oak")
slab((0, 1.5, .3), (7.6, .2, 2.3), "oak2")
for x in (-3.8, 3.8):
    slab((x, -1.5, 0), (.3, .3, 2.6), "oak2"); slab((x, 1.5, 0), (.3, .3, 2.6), "oak2")
slab((1.8, -1.5, 1.3), (3.2, .2, 1.2), "oak2"); drum((1.8, -1.65, 1.9), .12, .1, 6, "brass", rot=(math.pi / 2, 0, 0))
# the lamp: base, two arms, big glowing shade, bulb
drum((-2.6, .8, 2.9), .5, .2, 8, "brass"); drum((-2.6, .8, 3.1), .12, 1.6, 6, "brass")
rod((-2.6, .8, 4.7), (-1.6, .2, 5.6), .12, "brass"); rod((-1.6, .2, 5.6), (-.4, -.4, 5.0), .12, "brass")
drum((-.4, -.4, 3.9), .2, 1.1, 8, "shade", .85, (math.pi, 0, 0))
drum((-.4, -.4, 3.6), .22, .5, 6, "bulb")
lamp("POINT", (1, .62, .25), 1500, (-.4, -.4, 3.4)); lamp("POINT", (1, .6, .25), 250, (-.4, -.4, 1.8))
# papers, a stack of books, a mug, a small globe and a chair
for i, (x, y, rz) in enumerate(((-.6, -.4, .2), (-1.0, .3, -.3), (.2, -.8, .5))): slab((x, y, 2.9), (1.1, .8, .03), "paper", rz)
for i, c in enumerate(("red", "green", "blue")): slab((-4.6 + i * .02, -.6, 2.9 + i * .25), (1.0, .7, .22), c, i * .1)
drum((4.0, .6, 2.9), .3, .5, 7, "red"); drum((4.0, .6, 3.35), .24, .05, 7, "glass")
drum((.6, 1.0, 2.9), .1, .5, 5, "brass"); drum((.6, 1.0, 3.4), .35, .35, 7, "blue", .3)
drum((.6, 1.0, 3.75), .3, .3, 7, "green", .1)
drum((0, -3.0, 0), .5, 1.4, 6, "black"); slab((0, -3.0, 1.4), (1.6, 1.4, .2), "red")
slab((0, -3.7, 1.6), (1.6, .15, 1.6), "red")
# a shelf of books on the left wall and a small frame
slab((-6.9, 1.0, 4.2), (1.0, 4.0, .15), "oak2")
for i in range(8): drum((-6.9, -.4 + i * .4, 4.35), .13, .9 + (i % 3) * .1, 5, ("red", "green", "blue", "paper")[i % 4])
lamp("SUN", (.3, .4, .9), .12, (20, -20, 8), (0, 0, 2))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.005, .006, .015, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((10, -34, 20))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
