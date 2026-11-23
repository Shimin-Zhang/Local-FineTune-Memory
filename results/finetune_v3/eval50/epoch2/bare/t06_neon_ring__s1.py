import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(1253)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
S = bpy.context.scene
def neon(rgb, em=0):
    m = bpy.data.materials.new("n"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .6
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
deck, tile, tile2, wall, trim, cyan, pink, amber, core, dark = (neon((.012, .012, .03)), neon((.03, .03, .06)), neon((.02, .02, .04)), neon((.03, .03, .06)),
    neon((.08, .08, .12)), neon((.1, .9, 1), 14), neon((1, .1, .6), 14), neon((1, .65, .1), 12), neon((.6, .9, 1), 25), neon((.005, .005, .01)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    S.collection.objects.link(o); o.data.materials.append(m); return o
def panel(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = V((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def bar(a, b, t, m):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ V((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; S.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += V((random.uniform(-1.3, 1.3), random.uniform(-1.3, 1.3), random.uniform(-1.5, .2)))
mk(bm, deck)
for i in range(10):
    for j in range(10):
        if (i + j) % 2: panel((-9 + i * 2, -9 + j * 2, 0), (1.9, 1.9, .06), tile if (i // 2 + j // 2) % 2 else tile2)
for a in range(10):
    x, y = math.cos(a * .628) * 11, math.sin(a * .628) * 11
    panel((x, y, 0), (3.2, .18, .1), cyan if a % 2 else pink, (0, 0, a * .628 + 1.57))
# two cutaway walls with neon trim and lit panels
panel((0, 11.6, 0), (23, .6, 7), wall); panel((-11.6, 0, 0), (.6, 23, 7), wall)
panel((0, 11.25, 0), (23, .1, .25), trim); panel((-11.25, 0, 0), (.1, 23, .25), trim)
for k in range(7):
    panel((-9 + k * 3, 11.25, 1.2 + (k % 3) * 1.5), (1.6, .1, .9), (cyan, pink, amber)[k % 3]); panel((-11.25, -9 + k * 3, 1.2 + (k % 3) * 1.5), (.1, 1.6, .9), (pink, amber, cyan)[k % 3])
panel((0, 11.25, 6.2), (23, .1, .2), pink); panel((-11.25, 0, 6.2), (.1, 23, .2), cyan)
# the floating ring: outer neon band, inner band, core, spokes and a glowing centre
for i in range(24):
    a0, a1 = i * .2618, (i + 1) * .2618
    bar((math.cos(a0) * 5.4, math.sin(a0) * 5.4, 6.5), (math.cos(a1) * 5.4, math.sin(a1) * 5.4, 6.5), .3, cyan)
    bar((math.cos(a0) * 4.4, math.sin(a0) * 4.4, 6.5), (math.cos(a1) * 4.4, math.sin(a1) * 4.4, 6.5), .2, pink)
for i in range(6):
    a = i * 1.047
    bar((math.cos(a) * 4.4, math.sin(a) * 4.4, 6.5), (math.cos(a) * 5.4, math.sin(a) * 5.4, 6.5), .22, trim)
    cyl((math.cos(a) * 5.4, math.sin(a) * 5.4, 6.5), .38, .35, 6, amber, rot=(math.pi / 2, 0, a + math.pi / 2))
cyl((0, 0, 6.35), 1.2, .3, 8, core); cyl((0, 0, 6.2), 1.6, .1, 8, dark)
glow((0, 0, 7.6), (.5, .9, 1), 2200); glow((0, 0, 4.6), (.9, .2, .7), 900)
# a light column and a pedestal under the ring
cyl((0, 0, .1), 1.9, .5, 8, trim); cyl((0, 0, .6), 1.2, .2, 8, cyan); cyl((0, 0, .8), .12, 5.4, 5, dark)
for i in range(3): cyl((0, 0, 1.2 + i * 1.6), 1.5 - i * .3, .12, 8, cyan if i % 2 == 0 else pink)
# consoles, crates and a drone on the deck
for i, (x, y) in enumerate(((-7, -6), (7.5, -5), (-8, 3), (8, 5))):
    panel((x, y, 0), (2.2, 1.2, 1.1), trim); panel((x, y - .62, .7), (1.8, .06, .5), (cyan, pink, amber)[i % 3])
for i, (x, y) in enumerate(((3, -8), (4.5, -7.4), (-4, 8))): panel((x, y, 0), (1.3, 1.3, 1.1 + i * .2), trim, (0, 0, i))
cyl((6, 0, 3.5), .5, .5, 6, trim); cyl((6, 0, 3.2), .3, .3, 6, amber)
for s in (-1, 1): bar((6 + s * 1.1, 0, 3.8), (6 + s * .3, 0, 3.6), .08, trim)
for c, w, p in (((.2, .8, 1), 3.5, (-26, -14, 12)), ((1, .15, .6), 2.2, (22, 20, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; S.collection.objects.link(o)
    o.rotation_euler = (V((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); S.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .005, .02, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); S.collection.objects.link(co)
tg = V((0, 0, 3.5)); co.location = tg + V((12, -56, 34))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); S.camera = co
