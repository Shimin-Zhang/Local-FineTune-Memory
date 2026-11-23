import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1465)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
V = {}
def pigment(n, c, e=0, r=.9):
    m = bpy.data.materials.new(n); m.use_nodes = True
    s = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    s.inputs["Base Color"].default_value = (*c, 1); s.inputs["Roughness"].default_value = r
    if e:
        s.inputs["Emission Color"].default_value = (*c, 1); s.inputs["Emission Strength"].default_value = e
    V[n] = m
for n, c in (("sand", (.3, .2, .13)), ("rock", (.12, .09, .08)), ("rock2", (.18, .13, .1)), ("ochre", (.55, .22, .08)), ("white", (.7, .65, .55)),
             ("ochre2", (.4, .14, .06)), ("wash", (.38, .3, .22)), ("stone", (.28, .24, .2)), ("wood", (.25, .16, .09)), ("sage", (.2, .26, .15)),
             ("thorn", (.15, .1, .06)), ("cloth", (.5, .1, .08)), ("skin", (.35, .2, .12)), ("torch", (1, .45, .08))):
    pigment(n, c)
pigment("lantern", (1, .55, .15), 22); pigment("flame", (1, .5, .1), 18)
def form(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("f"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("f", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(V[m]); return o
def slab(p, s, m, r=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return form(bm, m, p, r)
def post(p, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return form(bm, m, p, rot)
def pebble(p, r, m, sq=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return form(bm, m, p)
def line(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return form(bm, m)
def glow(c, w, p):
    l = bpy.data.lights.new("l", "POINT"); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
# desert base, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
form(bm, "sand")
# the varnished cliff: a faceted wall of dark rock with ledges
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=11, radius2=9, depth=9)
for v in bm.verts:
    if v.co.z > 0: v.co.z += random.uniform(-.3, .3)
    v.co.y = max(v.co.y, -3.5)
form(bm, "rock", (0, 7.5, 0))
slab((0, 1.2, 0), (15, .6, 1.2), "rock2")
for i, (x, z, w, h) in enumerate(((-7, 3, 3, 2.2), (-2, 5.5, 3.4, 2.6), (4, 3.4, 3, 2.4), (8, 5.8, 2.6, 2.2), (-5, 7.5, 3, 2.4))):
    slab((x, 2.5, z), (w, .5, h), "rock2" if i % 2 else "rock")
# petroglyphs: spirals, sheep, hunters, drawn as small strokes on the face
def glyph(cx, cz, kind):
    if kind == 0:
        for k in range(26):
            t = k / 25 * 4 * math.pi; r = .08 + .035 * t
            p = Vector((cx + r * math.cos(t), 2.1, cz + r * math.sin(t)))
            if k: line(q, p, .07, "ochre")
            q = p
    elif kind == 1:
        for k in range(8):
            p = Vector((cx - .6 + k * .17, 2.1, cz - .15 * math.sin(k * .8)))
            if k: line(q, p, .09, "white")
            q = p
        for dx in (-.4, .4): line((cx + dx, 2.1, cz - .1), (cx + dx, 2.1, cz - .5), .08, "white")
        line((cx + .6, 2.1, cz), (cx + .9, 2.1, cz + .25), .08, "white")
    else:
        line((cx, 2.1, cz - .6), (cx, 2.1, cz + .1), .12, "ochre2")
        pebble((cx, 2.0, cz + .35), .2, "ochre2", 1)
        line((cx, 2.1, cz), (cx + .6, 2.1, cz + .5), .08, "ochre2"); line((cx, 2.1, cz), (cx - .5, 2.1, cz + .6), .08, "ochre2")
        line((cx + .6, 2.1, cz + .5), (cx + .6, 2.1, cz + 1.0), .05, "ochre2")
for i, (x, z, k) in enumerate(((-6, 4.2, 0), (-3.5, 6.4, 1), (-1, 3.6, 2), (1.5, 6.2, 0), (3.5, 4.2, 1), (6, 6.4, 2), (-5, 8.2, 1), (7.5, 4.4, 0), (-.5, 7.6, 2))):
    glyph(x, z, k)
# the trail up to the rock, a small fence, and the dry wash below
for i in range(10):
    x = -8 + i * .9 + math.sin(i) * .8; y = -10 + i * .85
    slab((x, y, 0), (1.8, 1.4, .08), "wash", (0, 0, random.uniform(-.3, .3)))
for i in range(6):
    x = -8 + i * 1.8; y = -5.5 - math.sin(i) * .5
    post((x, y, 0), .1, 1.3, 5, "wood"); post((x + 1.8, y - math.sin(i + 1) * .5 + math.sin(i) * .5, 0), .1, 1.3, 5, "wood")
    if i < 5: line((x, y, .9), (x + 1.8, y - math.sin(i + 1) * .5 + math.sin(i) * .5, .9), .08, "wood")
for i in range(8):
    pebble((random.uniform(-10, 10), random.uniform(-12, -8), .1), random.uniform(.4, .9), "stone")
for i in range(6):
    pebble((random.uniform(-9, 9), random.uniform(-4, -1), .1), random.uniform(.3, .6), "stone")
# boulders and scrub
for i in range(7):
    a = random.uniform(.2, 2.9); r = random.uniform(11, 12.5)
    pebble((r * math.cos(a) * .9, r * math.sin(a) * .8 - 2, .3), random.uniform(.8, 1.4), "rock2", .7)
for i in range(10):
    x, y = random.uniform(-10, 10), random.uniform(-11, -1)
    post((x, y, 0), .3, .7, 5, "sage", .05)
# a campfire ring with a glowing lantern on a post, and two hunters' torches
for i in range(6):
    a = i * math.pi / 3; pebble((-3 + .6 * math.cos(a), -3.5 + .6 * math.sin(a), .1), .25, "stone", .7)
post((-3, -3.5, 0), .2, .5, 5, "wood", .1); post((-3, -3.5, .5), .25, .3, 5, "flame", .02); glow((1, .5, .15), 700, (-3, -3.5, 1.4))
post((1, -2, 0), .08, 2.2, 5, "wood"); post((1, -2, 2.2), .3, .5, 6, "lantern", .3); glow((1, .55, .15), 500, (1, -2, 2.6))
for x, y in ((-6, -4.5), (4, -5)):
    post((x, y, 0), .12, 1.7, 5, "skin", .1); post((x, y, 1.7), .12, .25, 5, "cloth", .05)
    line((x + .2, y, 1.5), (x + .9, y, 3.2), .06, "wood"); post((x + .9, y, 3.2), .15, .35, 5, "flame", .02)
    glow((1, .5, .15), 120, (x + .9, y, 3.4))
# light: dusk, a warm low key from the left, violet rim from behind
for c, e, p in (((1, .55, .3), 5, (-24, -14, 9)), ((.5, .4, 1), 2.2, (22, 24, 14))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = e
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((-6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
