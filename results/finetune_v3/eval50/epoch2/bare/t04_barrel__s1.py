import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(875)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def rusty(c, e=0, r=.8):
    m = bpy.data.materials.new("r"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
tar, tar2, rust, rust2, band, dirt, puddle, drip, fire, ember = (rusty((.3, .12, .05)), rusty((.24, .1, .05)), rusty((.38, .15, .06)), rusty((.25, .09, .05)),
    rusty((.12, .08, .06), 0, .5), rusty((.16, .13, .1)), rusty((.02, .03, .04), 0, .05), rusty((.45, .18, .06)), rusty((1, .45, .08), 14), rusty((1, .2, .03), 8))
def mk(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("b", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); me.materials.append(m); return o
def tube(m, p, r, h, n=10, r2=None, rot=(0, 0, 0), j=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts:
        v.co.z += h / 2
        if j: v.co += V((random.uniform(-j, j), random.uniform(-j, j), random.uniform(-j, j)))
    return mk(bm, m, p, rot)
def slab(m, p, s, r=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = V((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, p, r)
def blob(m, p, r, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mk(bm, m, p)
def spark(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# concrete slab base with rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=10.5, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    v.co.z -= 1.7
mk(bm, tar2, (0, 0, 0))
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(6.5, 9.5)
    blob(tar if i % 2 else dirt, (r * math.cos(a), r * math.sin(a), 0), random.uniform(.5, 1.1), .35)
# the barrel: stacked rings with bulging radius, rust patches, three bands
def ring(r, z, m, j=.02):
    tube(m, (0, 0, z), r, .5, 10, r, (0, 0, 0), j)
for i in range(11):
    r = 2.0 * (1 + .1 * math.sin(math.pi * i / 10))
    ring(r, i * .5, rust if i % 3 else rust2)
for z in (.6, 2.5, 4.4):
    tube(band, (0, 0, z), 2.0 * (1 + .1 * math.sin(math.pi * z / 5)) + .08, .22, 10)
for i in range(16):
    a = random.uniform(0, 6.28); z = random.uniform(.4, 4.8)
    r = 2.0 * (1 + .1 * math.sin(math.pi * z / 5)) + .02
    slab(rust2 if i % 2 else tar, (r * math.cos(a), r * math.sin(a), z), (.5, .35, .45), (0, 0, a + 1.57))
# dented top lid with a spout
tube(rust, (0, 0, 5.5), 1.9, .15, 10, 1.8); tube(band, (0, 0, 5.6), 1.3, .08, 10)
for i in range(3): slab(tar, (math.cos(i * 2.1) * .9, math.sin(i * 2.1) * .9, 5.65), (.5, .1, .06), (0, 0, i * 2.1))
# the fire: glowing coals, flames, sparks
tube(ember, (0, 0, 5.7), 1.1, .1, 8)
for i, (x, y, h) in enumerate(((0, 0, 2.2), (.5, .3, 1.4), (-.4, .35, 1.6), (.1, -.5, 1.2))):
    tube(fire if i else ember, (x, y, 5.8), .35 - i * .03, h, 5, .02)
for i in range(8): blob(ember, (random.uniform(-.8, .8), random.uniform(-.8, .8), 5.8), .12, .8)
spark("POINT", (1, .45, .08), 1200, (0, 0, 7.5)); spark("POINT", (1, .3, .05), 400, (0, 0, 6.2))
# drips down the side and a puddle
for i in range(5):
    a = i * 1.3 + .4
    slab(drip, (2.05 * math.cos(a), 2.05 * math.sin(a), 2.0 + (i % 2) * .5), (.12, .1, 1.4 + (i % 3) * .5), (0, 0, a))
tube(puddle, (3.2, -2.2, 0), 1.7, .06, 8, 1.6); tube(puddle, (-2.5, 3, 0), 1.2, .06, 7, 1.1)
# crates, loose drum, scrap
slab(tar, (-5, -2, 0), (2.2, 2.2, 1.4), (0, 0, .3)); slab(tar2, (-4.7, -1.7, 1.4), (1.8, 1.8, 1.1), (0, 0, .6))
tube(rust2, (4.5, 3, 0), 1.1, 2.6, 8, 1.1, (0, 1.2, .5))
for i in range(4): slab(band, (random.uniform(-1, 1) + 5.5, random.uniform(-1, 1) - 3.5, 0), (.9, .1, .1), (0, 0, random.uniform(0, 3)))
spark("SUN", (.5, .65, 1), 3.5, (-22, -14, 9), (0, 0, 2)); spark("SUN", (1, .4, .15), 2.2, (20, 18, 10), (0, 0, 2))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = V((0, 0, 3)); co.location = t + V((6, -36, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
