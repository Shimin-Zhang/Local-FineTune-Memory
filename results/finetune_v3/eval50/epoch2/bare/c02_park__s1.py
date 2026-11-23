import bpy, bmesh, random, math
from mathutils import Vector
random.seed(557)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(c, glow=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = glow
    return m
grass, grass2, dirt, water, trunk, leaf1, leaf2, leaf3, plank, rock, lampc, flower = (
    tint((.07, .17, .07)), tint((.1, .22, .08)), tint((.3, .2, .12)), tint((.05, .2, .25)), tint((.22, .13, .08)),
    tint((.08, .26, .1)), tint((.14, .3, .08)), tint((.2, .28, .06)), tint((.35, .2, .1)), tint((.3, .3, .3)), tint((1, .7, .3), 14), tint((.9, .3, .4)))
def spawn(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return spawn(bm, m, at, rot)
def stem(at, r1, r2, h, n, m):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return spawn(bm, m, at)
def crown(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return spawn(bm, m, at)
def shine(at, c, w):
    L = bpy.data.lights.new("s", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
# grass base with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=12.5, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    else: v.co.z += random.uniform(-.12, .12)
    v.co.z -= 1.7
spawn(bm, grass)
# pond with a stone rim and reeds
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4.6, radius2=4.6, depth=.2)
for v in bm.verts: v.co.x *= 1.3; v.co += Vector((random.uniform(-.3, .3), random.uniform(-.3, .3), 0))
spawn(bm, water, (-1, -3.5, .03))
for i in range(14):
    a = i * .45; crown((-1 + math.cos(a) * 5.6, -3.5 + math.sin(a) * 4.4, .1), random.uniform(.35, .6), rock, .6)
for i in range(6): stem((-5.6 + i * .25, -1.2 + i * .1, 0), .05, .02, 1.1, 4, leaf2)
# winding path of slabs from the front to the bench
for i in range(11):
    x, y = 5.5 - i * .1 + math.sin(i * .6) * 1.1, -9.5 + i * .95
    slab((x, y, 0), (1.8, 1.1, .12), dirt, (0, 0, math.sin(i * .6) * .4))
# three trees: trunks with layered crowns
for x, y, k, h in ((-7, 4, 0, 4.2), (-1, 7.5, 1, 5), (7.5, 3, 2, 4.6)):
    stem((x, y, 0), .45, .25, h, 6, trunk)
    for j in range(3): crown((x + random.uniform(-.5, .5), y + random.uniform(-.5, .5), h + j * .9), 2.3 - j * .5, (leaf1, leaf2, leaf3)[k], .85)
# bench facing the pond, with a lamp post
slab((2.5, -2.5, .55), (2.6, .8, .15), plank, (0, 0, .15)); slab((2.5, -2.0, 1.0), (2.6, .15, .7), plank, (0, 0, .15))
for s in (-1, 1): slab((2.5 + s * 1.0 * .98, -2.45 + s * .15, 0), (.15, .7, .6), plank, (0, 0, .15))
stem((5.2, -1.2, 0), .12, .08, 3.2, 5, rock); slab((5.2, -1.2, 3.2), (.6, .6, .6), lampc); shine((5.2, -1.2, 3.6), (1, .7, .3), 500)
# flowers and a few boulders
for i in range(18):
    x, y = random.uniform(-9, 9), random.uniform(-9, 9)
    if math.hypot(x + 1, y + 3.5) > 5.5 and math.hypot(x - 5.5, y + 5.5) > 1.2 and abs(y - 4) > 0: stem((x, y, 0), .12, .02, .5, 4, flower if i % 2 else leaf2)
for i in range(5): crown((random.uniform(-9, 9), random.uniform(-9, 9), .1), random.uniform(.4, .7), rock, .6)
# blue-hour light: cool key from the left, warm rim behind, lamp glow
for c, w, p in (((.45, .6, 1), 4.5, (-24, -14, 10)), ((1, .5, .3), 2.2, (22, 20, 8))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("dusk"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .045, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((9, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
