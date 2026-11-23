import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(782)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def surf(c, e=0, r=.8, a=1):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r; n.inputs["Alpha"].default_value = a
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
lawn, lawn2, stem, petal, dirt, rockm, pond, foam, glass = (surf(c, r) for c in ((.1, .26, .12), (.15, .32, .14), (.12, .22, .1), (.9, .35, .6), (.14, .1, .08), (.3, .3, .34), (.05, .2, .35), (.8, .9, 1), (.04, .06, .1)))
rain = [surf(c, 1.5, .4) for c in ((.9, .1, .1), (.95, .35, .05), (.95, .8, .1), (.1, .8, .2), (.1, .5, .9), (.2, .2, .9), (.6, .15, .8))]
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); me.materials.append(m); return o
def cone(r1, r2, h, n=7, j=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co += V((random.uniform(-j, j), random.uniform(-j, j), 0)); v.co.z += h / 2
    return bm
def ball(r, k=(1, 1, 1), j=0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = V((v.co.x * k[0], v.co.y * k[1], v.co.z * k[2])) + V((random.uniform(-j, j),) * 3)
    return bm
def beam(a, b, w):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ V((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return bm
bm = cone(3.5, 9.5, 4.0, 9, .5)
for v in bm.verts:
    if v.co.z < 0: v.co.z += random.uniform(-1.2, .3)
mk(bm, dirt, (0, 0, -2))
mk(cone(9.5, 9.5, .3, 9, .15), lawn, (0, 0, -.1))
for i in range(14):
    a = i * .45; r = random.uniform(5.5, 8.2)
    mk(cone(random.uniform(.9, 1.4), .1, random.uniform(.8, 1.6), 5, .1), lawn2 if i % 2 else lawn, (math.cos(a) * r, math.sin(a) * r, 0))
mk(cone(2.6, 2.6, .1, 8), pond, (5.5, -3.5, .05)); mk(cone(2.8, 2.8, .08, 8), foam, (5.5, -3.5, .02))
for i in range(5): mk(ball(random.uniform(.25, .45), (1, 1, .6), .05), rockm, (math.cos(i * 1.26) * 3.0, -3.5 + math.sin(i * 1.26) * 3.0, .1))
for i in range(16):
    a, r = random.uniform(0, 6.28), random.uniform(2.5, 8.2)
    x, y = math.cos(a) * r, math.sin(a) * r
    mk(cone(.08, .04, random.uniform(.8, 1.5), 5), stem, (x, y, 0))
    for k in range(5):
        b = k * 1.256 + a; mk(ball(.22, (1, 1, .5), .02), petal, (x + math.cos(b) * .3, y + math.sin(b) * .3, 1.3))
    mk(ball(.14, j=.02), rain[2], (x, y, 1.35))
# the bubble: a thin iridescent shell of seven rainbow bands, a pale core, and a wet highlight
R, C = 3.0, V((-1.5, 1.0, 6.0))
mk(ball(R * .97, j=.02), glass, C, rot=(0, 0, 0)).data.materials.append(glass)
sh = bmesh.new(); bmesh.ops.create_icosphere(sh, subdivisions=3, radius=R * 1.02)
for f in sh.faces:
    c = f.calc_center_median(); k = int((math.atan2(c.z, math.sqrt(c.x ** 2 + c.y ** 2)) + math.pi / 2) * 7 / math.pi * 1.05) % 7
    f.material_index = k
for m in rain: sh.materials.append(m)
mk(sh, None, C)
for i in range(7):
    a = i * .9 + .5; mk(ball(.12), rain[i], C + V((math.cos(a) * R * 1.05, math.sin(a) * R * .4, math.sin(a) * R * 1.05 * .5)), rot=(0, 0, 0))
mk(ball(.35, j=.02), surf((1, 1, 1), 4), C + V((-1.1, -1.0, 1.4)))
for i, (x, y, z) in enumerate(((-6, -4, 1.2), (4, 4, 1.0), (1, 6, 1.8), (-4, 6, 1.5), (6.5, 1, 1.1), (-7, -1, 1.0))):
    mk(ball(random.uniform(.3, .5), (1, 1, .8), .03), glass, (x, y, z)); mk(ball(.1), rain[(i * 2) % 7], (x + .1, y - .2, z + .2))
def lt(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
lt(C, (.9, .7, 1), 900); lt((5.5, -3.5, 1.5), (.3, .8, 1), 250)
for c, w, at in (((.55, .65, 1), 4.5, (-22, -14, 10)), ((1, .5, .65), 2.5, (18, 20, 12))):
    S = bpy.data.lights.new("s", "SUN"); S.color, S.energy = c, w
    o = bpy.data.objects.new("s", S); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (V((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .05, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = V((0, 0, 3.5)); co.location = tg + V((10, -40, 22))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
