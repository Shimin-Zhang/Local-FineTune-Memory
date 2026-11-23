import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1104)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def neon(rgb, em=0, rough=.6, metal=0):
    m = bpy.data.materials.new("n"); m.use_nodes = True
    b = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
tar, wet, steel, brick, glass, skin, car, white = neon((.02, .02, .03), rough=.25), neon((.03, .05, .08), rough=.05), neon((.1, .1, .13), metal=.5, rough=.4), neon((.07, .06, .08)), neon((.02, .03, .05), rough=.1), neon((.55, .35, .25)), neon((.5, .02, .03)), neon((.7, .7, .72))
pink, cyan, mag, amber, lime, rain = neon((1, .1, .5), 14), neon((.1, .9, 1), 14), neon((1, .1, .8), 10), neon((1, .6, .1), 10), neon((.4, 1, .2), 10), neon((.5, .6, .8), 1.2)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return add(bm, m, at, (0, 0, rz))
def tube(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def blob(at, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return add(bm, m, at)
def glow(at, rgb, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# street base: wet asphalt, rough underside, with a gutter line
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=7, radius2=15, depth=3.5)
for v in bm.verts:
    v.co.y *= .8
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.75
add(bm, tar)
for i in range(5): slab((-12 + i * 6, -1.2, .02), (3.2, .35, .03), wet)
# towers: back row and side rows, stacked floors with lit windows and ad screens
def tower(x, y, w, d, h, m):
    slab((x, y, 0), (w, d, h), m, top=.88)
    for k in range(int(h / 2.2)):
        for j in range(int(w / 1.6)):
            if random.random() < .55: slab((x - w / 2 + .8 + j * 1.6, y - d / 2 - .02, 1.2 + k * 2.2), (.8, .05, 1.0), neon((.05, .06, .1), rough=.2) if random.random() < .3 else (cyan, amber, pink)[(k + j) % 3])
    slab((x, y, h), (w + .3, d + .3, .4), steel)
for i, (x, h) in enumerate(((-11, 15), (-5.5, 19), (0, 14), (6, 21), (11.5, 16))): tower(x, 8.5, 4.6, 4.2, h, brick if i % 2 else steel)
for i, (y, h) in enumerate(((-4, 11), (2, 14))): tower(-12.2, y, 3.4, 4, h, steel); tower(12.2, y, 3.4, 4, h, brick)
# huge ad screens: a face each, with bars of light
for x, z, c, w in ((-5.5, 12, pink, 3.6), (6, 14, cyan, 3.6), (0, 8, amber, 3.2), (-12.2, 7, mag, 2.4), (12.2, 8, lime, 2.4)):
    slab((x, 6.3 if abs(x) < 9 else (8.3 if x < 0 else -8.3), z), (w if abs(x) < 9 else .1, .1 if abs(x) < 9 else w, 2.4), c)
    for k in range(4): slab((x, 6.2 if abs(x) < 9 else (8.3 if x < 0 else -8.3), z + .3 + k * .5), (w * .8 if abs(x) < 9 else .1, .08 if abs(x) < 9 else w * .8, .18), white)
    glow((x, 4.5 if abs(x) < 9 else 0, z + 1.2), ((1, .1, .5) if c is pink else (.1, .9, 1) if c is cyan else (1, .6, .1) if c is amber else (.4, 1, .2) if c is lime else (1, .1, .8)), 900)
# noodle bar: low building with awning, steam, sign and stools
slab((-1.5, 3.8, 0), (5.2, 3.4, 3.6), brick)
for k in range(3): slab((-3.2 + k * 1.6, 2.05, 1.0), (1.2, .1, 1.4), amber)
slab((-1.5, 2.1, 3.4), (5.6, 1.6, .25), pink, top=.9); slab((-1.5, 2.0, 3.2), (4.6, .1, .9), pink)
glow((-1.5, 1.4, 3.0), (1, .1, .5), 500)
for k in range(4): blob((-3.2 + k * 1.1, 1.5, 4.6 + k * .4), .5 + k * .15, white, .8)
for k in range(3): tube((-3.4 + k * 1.9, 1.2, 0), .35, .9, 6, steel, .25); slab((-3.4 + k * 1.9, 1.2, .9), (.8, .8, .12), car)
# crowd with umbrellas
for i in range(18):
    x, y = random.uniform(-9, 9), random.uniform(-6, 1.0)
    if abs(x + 1.5) < 3 and y > 1: continue
    c = random.choice((pink, cyan, amber, lime, car, mag))
    tube((x, y, 0), .3, 1.2, 6, c, .2); blob((x, y, 1.5), .26, skin)
    if i % 2 == 0:
        tube((x + .3, y, 1.1), .04, 1.4, 4, steel, rot=(.2, 0, 0)); tube((x + .3, y, 2.5), 1.0, .35, 8, c, .05)
# flying police car overhead: hull, cockpit, rotor, searchlights
fx, fy, fz = 2.0, 0, 11.5
slab((fx, fy, fz), (4.4, 1.6, .8), white, top=.8); slab((fx + 1.8, fy, fz + .8), (1.4, 1.2, .7), glass, top=.6)
slab((fx - 1.0, fy, fz + .8), (1.8, 1.0, .3), car); tube((fx - 1.2, fy, fz + 1.0), .08, 1.4, 4, steel, rot=(0, 1.57, 0)); slab((fx - 1.2, fy, fz + 2.2), (.3, 3.2, .1), steel)
for s in (-1, 1): tube((fx + .6, fy + s * .8, fz - .1), .25, .3, 6, cyan, rot=(1.57, 0, 0)); slab((fx - 2.25, fy + s * .5, fz - .1), (.1, .3, .3), cyan)
glow((fx + .6, fy, fz - .5), (.2, .9, 1), 500); glow((fx - 2.6, fy, fz), (1, .1, .3), 300)
# street furniture: lamp posts, a pillar of rain
for x in (-8, 0, 8):
    tube((x, -3.5, 0), .1, 4.2, 5, steel); slab((x + .6, -3.5, 4.2), (1.4, .2, .2), steel); slab((x + .6, -3.5, 4.0), (1.0, .25, .12), cyan)
    glow((x + .6, -3.5, 3.8), (.2, .9, 1), 120)
for i in range(90):
    x, y, z = random.uniform(-12, 12), random.uniform(-9, 9), random.uniform(1, 16)
    slab((x, y, z), (.04, .04, 1.3), rain, rz=0).rotation_euler = (.0, .12, 0)
# lights: cold teal key from the left, magenta rim from behind, deep night
for col, w, at in (((.3, .8, 1), 4.5, (-24, -16, 12)), ((1, .2, .6), 2.5, (20, 22, 14))):
    S = bpy.data.lights.new("s", "SUN"); S.color = col; S.energy = w
    o = bpy.data.objects.new("s", S); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 4)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .008, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 2, 7)); co.location = t + Vector((10, -62, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
