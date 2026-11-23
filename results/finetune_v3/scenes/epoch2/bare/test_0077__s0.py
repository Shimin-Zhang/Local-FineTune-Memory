import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1456)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
paints = {}
def tint(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    paints[name] = m
def build(bm, name, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(paints[name]); return o
def brick(name, at, size, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * size[0] * k, v.co.y * size[1] * k, (v.co.z + .5) * size[2]))
    return build(bm, name, at, (0, 0, rz))
def drum(name, at, r, h, n=8, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return build(bm, name, at)
def blob(name, at, r, flat=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= flat
    return build(bm, name, at)
def lamp(kind, col, w, at, aim=None):
    d = bpy.data.lights.new(kind, kind); d.color = col; d.energy = w
    o = bpy.data.objects.new(kind, d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()

tint("earth", (.2, .12, .07)); tint("mud", (.38, .12, .07)); tint("mud2", (.3, .09, .06)); tint("relief", (.45, .17, .09))
tint("wood", (.22, .12, .06)); tint("wood2", (.15, .08, .04)); tint("bark", (.2, .14, .1)); tint("leaf", (.12, .26, .08))
tint("leaf2", (.2, .34, .1)); tint("clay", (.5, .25, .12)); tint("flame", (1, .45, .08), 18); tint("dark", (.03, .02, .02))

# packed-earth courtyard on a rough floating base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, .2)))
    else: v.co.z += random.uniform(-.06, .06)
    v.co.z -= 2
build(bm, "earth", (0, 0, 0))
# three mud walls with relief bands, and a gate opening in the front wall
def wall(x0, x1, y0, y1, h):
    if y0 == y1:
        brick("mud", ((x0 + x1) / 2, y0, 0), (x1 - x0, .9, h))
        for k in range(int(x1 - x0) // 2 + 1):
            x = x0 + .8 + k * 2
            if x < x1 - .5: brick("relief", (x, y0 - .5, 1.0), (1.0, .15, 1.4), 0, .6)
    else:
        brick("mud", (x0, (y0 + y1) / 2, 0), (.9, y1 - y0, h))
        for k in range(int(y1 - y0) // 2 + 1):
            y = y0 + .8 + k * 2
            if y < y1 - .5: brick("relief", (x0 - .5, y, 1.0), (.15, 1.0, 1.4), 0, .6)
wall(-10, -3, 9, 9, 3.4); wall(3, 10, 9, 9, 3.4); wall(-10, -10, -9, 9, 3.4); wall(10, 10, -9, 9, 3.4)
wall(-10, -6, -9, -9, 3.4); wall(6, 10, -9, -9, 3.4)
for x in (-6, 6):
    drum("mud2", (x, -9, 0), .9, 4.2, 8); drum("wood2", (x, -9, 4.2), 1.1, .4, 8, .3)
brick("mud2", (0, -9, 3.2), (12, 1.0, .8))
for x in (-3, 3): brick("relief", (x, -9.6, 1.6), (1.2, .15, 1.2), 0, .5)
# raised relief diamonds and zigzags on the inner faces
for i in range(7):
    brick("relief", (-7 + i * 2.3, 8.5, 1.2), (.9, .12, .9), 0, .5); brick("relief", (-7 + i * 2.3, 8.5, 2.2), (.5, .12, .4), 0, .5)
# the sacred tree: a forked trunk, a crown of leaves, offerings at its foot
drum("bark", (0, 0, 0), .9, 3.2, 7, .5)
for a in (0, 2.1, 4.2):
    drum("bark", (math.cos(a) * .4, math.sin(a) * .4, 3.0), .35, 2.4, 5, .2).rotation_euler = (math.sin(a) * .45, -math.cos(a) * .45, 0)
for k, (x, y, z, r) in enumerate(((-2, 0, 6.2, 2.2), (2, .5, 6.4, 2.0), (0, -1.5, 6.8, 2.1), (0, 1.5, 7.0, 2.2), (.3, 0, 7.8, 1.8))):
    blob("leaf" if k % 2 else "leaf2", (x, y, z), r, .8)
for k in range(5):
    a = k * 1.26; drum("clay", (math.cos(a) * 1.6, math.sin(a) * 1.6, 0), .35, .5, 6, .25)
drum("wood2", (0, 0, 0), 2.4, .12, 10)
# stool house: a tall carved stool with a thatched roof, doorway and steps
brick("wood2", (-5.5, 4.5, 0), (3.6, 3.6, .5))
for sx in (-1, 1):
    for sy in (-1, 1): drum("wood", (-5.5 + sx * 1.3, 4.5 + sy * 1.3, .5), .35, 2.2, 6, .3)
brick("wood", (-5.5, 4.5, 2.7), (3.4, 3.4, .5)); brick("wood2", (-5.5, 4.5, 3.2), (3.0, 3.0, .15))
for k in range(5): brick("relief", (-6.8 + k * .65, 2.7, 1.2), (.25, .1, .6), 0, .5)
brick("dark", (-5.5, 2.75, .5), (1.0, .1, 1.6)); brick("flame", (-5.5, 2.9, .9), (.5, .08, .7))
drum("wood2", (-5.5, 4.5, 3.4), 3.4, 1.4, 4, .2).rotation_euler = (0, 0, math.pi / 4)
brick("wood2", (-5.5, 1.8, 0), (1.4, 1.0, .3)); brick("wood2", (-5.5, 2.3, 0), (1.2, .6, .5))
# a clay pot, a low altar and a lamp post in the courtyard
for k in range(3): drum("clay", (5.5 + k * .9, 5.5, 0), .5, .9, 7, .35)
brick("wood2", (4.5, -3, 0), (2.2, 1.2, .9)); brick("wood", (4.5, -3, .9), (2.4, 1.4, .2))
drum("wood", (4.5, -3, 1.1), .25, .5, 6); drum("flame", (4.5, -3, 1.6), .3, .4, 5, .05)
drum("wood2", (-3.5, -5, 0), .15, 3.0, 5); drum("flame", (-3.5, -5, 3.0), .4, .6, 6, .1)
lamp("POINT", (1, .5, .1), 500, (-3.5, -5, 3.4)); lamp("POINT", (1, .5, .1), 300, (4.5, -3, 2.0)); lamp("POINT", (1, .5, .1), 250, (-5.5, 2.0, 1.2))
lamp("SUN", (1, .6, .3), 5, (-26, -20, 12), (0, 0, 2)); lamp("SUN", (.3, .45, .8), 2, (22, 24, 10), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .025, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((14, -58, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
