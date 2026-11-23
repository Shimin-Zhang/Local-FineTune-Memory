import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1967)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
W = {}
def alloy(name, rgb, glow=0, rough=.8, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    W[name] = m
for k, v in dict(floor=(.22, .15, .1), wall=(.3, .22, .16), shade=(.45, .3, .15), wood=(.25, .14, .07), cloth=(.5, .12, .1), clay=(.4, .2, .12), iron=(.12, .12, .13),
                 leather=(.2, .1, .06), dark=(.03, .03, .035), rug=(.35, .08, .08)).items(): alloy(k, v)
alloy("copper", (.75, .32, .12), 0, .35, .9); alloy("brass", (.7, .5, .12), 0, .4, .9); alloy("ember", (1, .3, .05), 14); alloy("lampglow", (1, .65, .25), 25)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(W[m]); return o
def slab(at, d, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * k, v.co.y * d[1] * k, (v.co.z + .5) * d[2]))
    return shape(bm, m, at, (0, 0, rz))
def lathe(at, prof, m, n=8, rot=(0, 0, 0)):
    bm = bmesh.new(); rings = []
    for r, z in prof: rings.append([bm.verts.new((r * math.cos(i * 6.2832 / n), r * math.sin(i * 6.2832 / n), z)) for i in range(n)])
    for a, b in zip(rings, rings[1:]):
        for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bm.faces.new(rings[-1][::-1]); bm.faces.new(rings[0])
    return shape(bm, m, at, rot)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return shape(bm, m)
def glow(col, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# cutaway floor: two walls only, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=10, depth=2.4)
for v in bm.verts:
    v.co.y *= .9
    if v.co.z < 0: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-.9, .2)))
shape(bm, "floor", (0, 0, -1.2))
slab((0, 0, 0), (15, 12, .15), "floor"); slab((0, 0, .15), (13, 10, .1), "rug", 0, .95)
slab((0, 6.2, 0), (15, .5, 5.5), "wall"); slab((-7.2, 0, 0), (.5, 12.5, 5.5), "wall")
slab((0, 5.9, 1.2), (15, .2, .4), "wood"); slab((-6.9, 0, 1.2), (.2, 12.5, .4), "wood")
# striped awning over the back counter
for i in range(10): slab((-7 + i * 1.5, 5.2, 4.6), (1.5, 2.4, .12), "shade" if i % 2 else "cloth", 0, .95).rotation_euler.x = .2
# counter along the back wall with trays, stacked bowls, scales
slab((0, 5.0, 0), (12, 1.6, 1.4), "wood"); slab((0, 5.0, 1.4), (12.4, 1.9, .15), "leather")
for i, x in enumerate((-5, -3.2, -1.4, .4)):
    lathe((x, 4.9, 1.55), [(0, 0), (.9, .08), (1.15, .35), (1.15, .5)], "copper" if i % 2 else "brass", 8)
for x, y, h in ((2.6, 4.9, 0), (2.6, 4.9, .5), (2.6, 4.9, 1.0)):
    for k in range(3): lathe((x + (k - 1) * .5, y, 1.55 + h), [(0, 0), (.45, .15), (.4, .5)], "copper", 8)
slab((5, 4.9, 1.55), (1.4, .8, .15), "brass"); strut((5, 4.9, 1.7), (5, 4.9, 2.6), .06, "iron")
strut((4.3, 4.9, 2.5), (5.7, 4.9, 2.5), .06, "iron")
for s in (-1, 1): lathe((5 + s * .7, 4.9, 2.0), [(0, 0), (.4, .1), (.5, .5)], "copper", 8)
# workbench with a low anvil, charcoal pot, tools
slab((-1, 0, 0), (5, 2.2, 1.5), "wood"); slab((-1, 0, 1.5), (5.4, 2.5, .15), "leather")
slab((-1.6, 0, 1.65), (1.6, .9, .6), "iron", 0, .8); slab((-1.6, -.55, 2.25), (1.9, .4, .35), "iron", 0, .7)
strut((-1.2, 0, 1.9), (.4, 0, 2.4), .12, "iron")
lathe((.8, .3, 1.65), [(0, 0), (.8, .1), (1.0, .6), (.9, .8)], "clay", 8)
for k in range(5): lathe((.8 + random.uniform(-.4, .4), .3 + random.uniform(-.4, .4), 2.45), [(0, 0), (.3, .1), (.2, .3)], "ember", 5)
glow((1, .35, .08), 450, (.8, .3, 3.0))
for i in range(6): slab((-4.5 + i * .5, 0, 1.65), (.15, .15, .15), "copper", i)
# hammered trays on the rug and stacked bowls by the left wall
for i, (x, y, r) in enumerate(((-3, -3.5, 1.5), (0, -4.5, 1.2), (3, -3, 1.7))):
    lathe((x, y, .15), [(0, 0), (r * .8, .06), (r, .3), (r * .95, .35)], "copper" if i != 1 else "brass", 9)
    lathe((x, y, .35), [(0, 0), (r * .5, .05)], "brass" if i != 1 else "copper", 9)
for i in range(7): lathe((-6.2, -4 + i * .5, .15), [(0, 0), (.55, .2), (.5, .7)], "copper", 8)
for i in range(4): lathe((-6.2, -1 + i * .5, .15), [(0, 0), (.5, .2), (.45, .6)], "brass", 8)
# hanging lamp from a beam across the open side
strut((-6.9, -1.5, 4.4), (6.9, -1.5, 4.4), .25, "wood")
strut((0, -1.5, 4.4), (0, -1.5, 3.0), .05, "iron")
lathe((0, -1.5, 2.2), [(0, 0), (.5, .3), (.7, .8), (.4, 1.2), (.1, 1.4)], "lampglow", 8)
glow((1, .6, .25), 900, (0, -1.5, 2.8))
# warm dusk key from the front-left, teal rim from behind
for col, e, p in (((1, .6, .3), 5, (-24, -20, 12)), ((.3, .6, .7), 2.2, (22, 26, 14))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = col; L.energy = e
    o = bpy.data.objects.new("sun", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.8)); co.location = t + Vector((9, -44, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
