import bpy, bmesh, math, random
from mathutils import Vector
random.seed(911)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def colour(rgb, glow=0, rough=.85):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
river, bank, red, gold, jade, black, wood, roof, skin, white, flag = (colour(c) for c in (
    (.04, .16, .2), (.12, .22, .1), (.55, .06, .05), (.7, .45, .08), (.08, .4, .25), (.05, .05, .06), (.2, .1, .06), (.5, .08, .06), (.55, .35, .25), (.7, .68, .6), (.9, .75, .1)))
lantern = colour((1, .4, .1), glow=22); lamp = colour((1, .8, .4), glow=18)
def shape(kind, m, loc, size, rot=(0, 0, 0), n=6, top=1.0):
    bm = bmesh.new()
    if kind == "cyl": bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=.5, radius2=.5 * top, depth=1)
    elif kind == "ball": bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.5)
    else: bmesh.ops.create_cube(bm, size=1)
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.data.materials.append(m)
    o.location, o.scale, o.rotation_euler = loc, size, rot; sc.collection.objects.link(o); return o
def line(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a
    o = shape("box", m, (a + b) / 2, (t, t, d.length)); o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); return o
def glow(col, e, loc):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = col, e
    o = bpy.data.objects.new("g", L); o.location = loc; sc.collection.objects.link(o)
# river slab, banks and crowd
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=12, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("b", me); o.data.materials.append(bank); o.location.z = -1.5; sc.collection.objects.link(o)
shape("box", river, (0, 0, .1), (22, 8, .2))
for s in (-1, 1):
    shape("box", bank, (0, s * 5.5, .3), (22, 5, .6)); shape("box", wood, (0, s * 3.2, .45), (22, .25, .3))
for s in (-1, 1):
    for i in range(9):
        x = -9 + i * 2.3 + random.uniform(-.4, .4)
        shape("cyl", random.choice((red, jade, gold, black, white)), (x, s * 6.3, 1.0), (.8, .8, 1.2), n=5, top=.7)
        shape("ball", skin, (x, s * 6.3, 1.85), (.5, .5, .5))
# two dragon boats, each with a drummer at the bow
for k, (y, c1, c2) in enumerate(((-1.7, red, gold), (1.7, jade, red))):
    x0 = -2.5 + k * 1.2
    shape("box", wood, (x0, y, .45), (9, 1.3, .7))
    shape("box", c1, (x0, y, .85), (8.8, 1.0, .15)); shape("box", c2, (x0, y, .85), (1.2, 1.0, .16))
    shape("cyl", c2, (x0 - 4.5, y, .6), (1.3, 1.3, 1.0), rot=(0, -math.pi / 2, 0), n=6, top=.3)
    shape("cyl", c1, (x0 + 4.6, y, .7), (1.2, 1.2, .8), rot=(0, math.pi / 2, 0), n=6, top=.3)
    # dragon head: neck, snout, jaw, horns, eyes, mane
    hx = x0 + 5.2
    shape("box", c2, (hx, y, 1.2), (.9, .9, 1.0)); shape("box", c1, (hx + .8, y, 1.4), (1.2, .7, .5)); shape("box", c2, (hx + .7, y, 1.0), (.9, .5, .3))
    for s in (-1, 1):
        shape("cyl", gold, (hx - .2, y + s * .45, 2.0), (.2, .2, 1.0), rot=(s * .5, 0, 0), n=4, top=.2)
        shape("ball", lamp, (hx + .3, y + s * .45, 1.55), (.3, .3, .3))
    shape("box", black, (hx + 1.4, y, 1.4), (.1, .5, .1))
    for i in range(4): shape("cyl", c2, (hx - .3 - i * .35, y, 1.9 - i * .05), (.35, .35, .5), n=4, top=.3)
    # drummer in the bow and a row of paddlers
    shape("cyl", c1, (x0 + 2.6, y, 1.3), (.9, .9, 1.2), n=6, top=.7); shape("ball", skin, (x0 + 2.6, y, 2.1), (.55, .55, .55))
    shape("cyl", wood, (x0 + 2.2, y, 1.1), (1.1, 1.1, .4), rot=(0, math.pi / 2, 0), n=8)
    for i in range(7):
        px = x0 - 3.2 + i * 1.15
        shape("cyl", c2 if i % 2 else red, (px, y, 1.1), (.7, .7, 1.0), n=5, top=.7); shape("ball", skin, (px, y, 1.8), (.45, .45, .45))
        line(wood, (px, y + .5, 1.5), (px + .3, y + 1.6, .2), .1)
    shape("box", c1, (x0 - 4.4, y, 1.3), (.1, .1, 1.6)); shape("box", c2, (x0 - 4.4, y, 1.8), (.1, .8, .5))
# finish line pavilion with lanterns
px = 8.5
for s in (-1, 1):
    shape("cyl", wood, (px, s * 4.2, 1.6), (.5, .5, 3.2), n=6)
shape("box", wood, (px, 0, 3.3), (.5, 9, .4)); shape("box", roof, (px, 0, 3.9), (2.2, 10, .5), top=.7)
for i in range(5):
    shape("ball", lantern, (px, -4 + i * 2, 2.9), (.6, .6, .8)); 
glow((1, .4, .1), 700, (px, 0, 2.5))
for i in range(4): shape("box", white if i % 2 else black, (px, -1.5 + i, .2), (.3, .1, .3))
# flags along the banks
for i in range(8):
    x = -10 + i * 2.9
    for s in (-1, 1):
        shape("cyl", wood, (x, s * 3.9, 1.2), (.12, .12, 2.4), n=4)
        shape("box", flag if i % 2 else red, (x + .4, s * 3.9, 2.3), (.8, .06, .5))
# lights: warm festival dusk
for col, e, p in (((1, .6, .3), 5, (-24, -14, 8)), ((.3, .5, .9), 2, (20, 18, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((-6, -58, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
