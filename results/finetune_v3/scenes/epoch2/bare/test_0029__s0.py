import bpy, bmesh, math, random
from mathutils import Vector
random.seed(835)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, em=0):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
sand, sand2, foam, sea, wood, cloth, white, dark = (hue(c) for c in ((.5, .36, .22), (.4, .28, .18), (.75, .85, .85), (.08, .3, .38), (.3, .18, .1), (.7, .12, .1), (.7, .7, .68), (.05, .05, .06)))
red, gold, teal, lamp = hue((.8, .1, .08)), hue((.8, .6, .1)), hue((.1, .5, .5)), hue((1, .7, .3), 14)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cone(r1, r2, h, n=8, m=None, at=(0, 0, 0), rot=(0, 0, 0), j=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co += Vector((random.uniform(-j, j), random.uniform(-j, j), 0)); v.co.z += h / 2
    return shape(bm, m, at, rot)
def slab(w, d, h, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return shape(bm, m, at, rot)
def strut(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r, depth=d.length)
    return shape(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def glimmer(at, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = (1, .7, .3), w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# beach slab, tide side at the front
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=13.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.3, 1.3), random.uniform(-1.3, 1.3), random.uniform(-1.4, .2)))
shape(bm, sand)
# incoming tide: shallow sea with foam crests and small waves
cone(13.3, 13.3, .3, 10, sea, (0, 0, -.02)).scale.y = .45
for i in range(7):
    x = -9 + i * 3; cone(.9, .9, .12, 6, foam, (x, -6.2 + math.sin(i) * .5, .05), (0, 0, i), .12)
for i in range(5): cone(.5, .5, .1, 5, foam, (-6 + i * 3.2, -7.6, .05), (0, 0, i), .1)
# the line of sand sculptures, each on its own plinth with a flag
for k, (x, h, m, r) in enumerate(((-9, 3.2, red, 1.7), (-3.2, 4.4, gold, 2.0), (2.8, 3.6, teal, 1.8), (8.8, 4.8, red, 2.1))):
    cone(r + .5, r + .2, .5, 8, sand2, (x, 3, 0), (0, 0, k), .1)
    cone(r * .8, r * .5, h * .45, 8, m, (x, 3, .5), (0, 0, k * .4), .12)
    cone(r * .55, r * .25, h * .35, 8, sand, (x, 3, .5 + h * .45), (0, 0, k * .3), .1)
    cone(r * .3, .08, h * .3, 6, m, (x, 3, .5 + h * .8), (0, 0, 0), .05)
    for a in range(4):
        ang = a * 1.57 + k; cone(.35, .05, .6, 5, sand, (x + math.cos(ang) * r * .6, 3 + math.sin(ang) * r * .6, .5), (0, 0, 0), .05)
    strut((x, 3, .5 + h * .75), (x, 3, .5 + h + 2.2), .05, wood)
    slab(1.2, .05, .7, [red, gold, teal, red][k], (x + .6, 3, .5 + h + 1.9), (0, 0, 0))
# rope barrier with posts and a gate gap
for i in range(11):
    x = -10.5 + i * 2.1
    if abs(x - 0) < 1.2: continue
    cone(.1, .1, 1.2, 5, wood, (x, -2.5, 0))
    if i:
        x0 = -10.5 + (i - 1) * 2.1
        if abs(x0) > 1.2 and abs(x) > 1.2: strut((x0, -2.5, 1.0), (x, -2.5, 1.0), .04, cloth)
# judge's table with a lamp, chairs and a scorecard
slab(3.4, 1.2, 1.0, wood, (-6, -5.5, 0)); slab(3.6, 1.4, .12, white, (-6, -5.5, 1.0))
cone(.3, .2, .5, 6, lamp, (-5.2, -5.5, 1.12)); glimmer((-5.2, -5.5, 2.0), 450)
slab(.5, .35, .08, dark, (-6.8, -5.5, 1.12)); slab(.5, .35, .08, gold, (-4.2, -5.5, 1.12))
for sx in (-1, 1):
    slab(.8, .8, .1, wood, (-6 + sx * 2.3, -5.5, .6)); slab(.8, .1, .8, wood, (-6 + sx * 2.3, -5.5 + sx * .35, 1.0))
# a few baskets and a shovel leaning on the table
for i in range(3): cone(.4, .3, .5, 6, sand2, (-2 + i * 1.0, -5.5, 0))
strut((-7.5, -5.5, 0), (-7.8, -5.5, 2.2), .05, wood)
# sunset: low orange key from the right, violet rim from the sea side
for c, e, p in (((1, .55, .25), 6, (26, -8, 8)), ((.45, .35, .9), 2.2, (-18, -24, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("sunset"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((-12, -58, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
