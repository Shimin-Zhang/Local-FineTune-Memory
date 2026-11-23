import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1939)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(rgb, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
soil, poppy, poppy2, brick, brick2 = paint((.12, .08, .06)), paint((.8, .08, .12)), paint((.55, .05, .1)), paint((.9, .65, .12)), paint((.75, .5, .08))
blue, straw, tin, mane, fur, skin, leaf, trunk, ruby, green = paint((.1, .2, .6)), paint((.8, .6, .2)), paint((.5, .55, .6)), paint((.55, .3, .05)), paint((.7, .45, .12)), paint((.8, .55, .4)), paint((.1, .3, .1)), paint((.2, .13, .08)), paint((1, .05, .08), 10), paint((.1, 1, .4), 3)
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mesh(bm, m, at, rot)
def ball(at, r, m, sub=1, squash=1, jit=0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co.z *= squash; v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit)))
    return mesh(bm, m, at)
def stem(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return mesh(bm, m)
def glow(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
def walker(x, y, face, kind, scale=1.0):
    # face: radians, 0 = along +y (toward the city); kind: 0 Dorothy, 1 Scarecrow, 2 Tin Man, 3 Lion
    def P(dx, dy, dz): return (x + (dx * math.cos(face) - dy * math.sin(face)) * scale, y + (dx * math.sin(face) + dy * math.cos(face)) * scale, dz * scale)
    if kind == 0:
        cube(P(0, 0, 0), (.7, .5, 1.0), blue); cube(P(0, 0, 1.0), (.5, .4, .45), blue)
        ball(P(0, 0, 1.8), .38, skin, 1, 1, .02); ball(P(0, 0, 2.05), .4, blue, 1, .8); cube(P(0, .1, 2.1), (.8, .3, .08), blue)
        for s in (-1, 1): stem(P(s * .3, 0, 2.0), P(s * .45, 0, 3.0), .08, skin); cube(P(s * .25, 0, .0), (.25, .3, .25), ruby)
    elif kind == 1:
        cube(P(0, 0, 0), (.9, .6, 1.2), straw); ball(P(0, 0, 1.6), .5, straw, 1, 1, .05)
        cube(P(0, 0, 1.9), (.4, .4, .6), straw); cube(P(0, 0, 2.4), (.3, .3, .2), straw); cube(P(0, 0, 2.6), (1.6, .3, .12), straw); cube(P(0, 0, 2.6), (.2, .3, .12), straw)
        for s in (-1, 1): stem(P(s * .45, 0, 1.1), P(s * .8, 0, 1.8), .08, straw)
    elif kind == 2:
        cube(P(0, 0, 0), (.7, .5, 1.1), tin); cube(P(0, 0, 1.1), (.5, .4, .4), tin); ball(P(0, 0, 1.8), .36, tin, 1, 1, .02); cube(P(0, 0, 2.0), (.8, .3, .08), tin)
        for s in (-1, 1): stem(P(s * .35, 0, 1.1), P(s * .6, 0, 1.7), .08, tin)
    else:
        ball(P(0, 0, .7), .8, fur, 1, .8, .05); ball(P(0, .9, 1.2), .5, fur, 1, 1, .03); ball(P(0, .9, 1.7), .5, mane, 1, 1, .06); ball(P(0, 1.4, 1.2), .25, fur, 1, 1, .02)
        for s in (-1, 1): cube(P(s * .25, 1.5, 1.2), (.1, .1, .1), skin)
    glow(P(0, 1.0, 1.2), (1, .7, .3), 60)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3.2)
for v in bm.verts:
    v.co.x *= 1.2
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.3, .3)))
    v.co.z -= 1.6
mesh(bm, soil)
# yellow brick road: zig-zag courses of big bricks from the front to the city gate
for i in range(18):
    t = i / 17; x = 1.5 * math.sin(t * 5) - 1.5 * t; y = -11 + t * 19
    for k in (-1, 0, 1):
        cube((x + k * .85, y, 0), (1.5, 1.1, .25), brick if (i + k) % 2 else brick2, (0, 0, .1 * math.cos(t * 5)))
# poppy field: rows of flowers on both sides, some bent by the wind
for i in range(70):
    side = random.choice((-1, 1)); x = side * random.uniform(4, 15); y = random.uniform(-11, 10)
    if abs(x - (1.5 * math.sin((y + 11) / 19 * 5) - 1.5 * (y + 11) / 19)) < 2.5: continue
    h = random.uniform(.8, 1.5); stem((x, y, 0), (x + .2, y, h), .05, leaf); ball((x + .2, y, h + .1), .22, poppy if i % 3 else poppy2, 1, 1, .03)
for i in range(10): ball((random.uniform(-16, 16), random.uniform(-11, 10), .1), random.uniform(.5, 1), leaf, 1, .4, .1)
# the Emerald City: gate arch with glowing windows, spires, domes and a lit tower
cx, cy = -1.5 * 1.0 - 1.5, 9
cube((cx, cy, 0), (12, 4, 2.2), green); cube((cx - 3, cy, 0), (2.4, 2.4, 5.5), green); cube((cx + 3, cy, 0), (2.4, 2.4, 5.5), green)
for s in (-1, 1):
    for j in range(3): cube((cx + s * 3 + (j - 1) * .8, cy - 1.25, 2.8 + j * 1.2), (.5, .1, .8), paint((.6, 1, .8), 5))
    cube((cx + s * 3, cy - 1.25, 5.5), (1.2, 1.2, 1.0), paint((.4, 1, .7), 4))
    b = bmesh.new(); bmesh.ops.create_cone(b, cap_ends=True, segments=4, radius1=1.8, radius2=.1, depth=2.5); mesh(b, green, (cx + s * 3, cy, 6.4), (0, 0, .78))
cube((cx, cy - 1.25, 0), (3.2, .2, 2.0), paint((.5, 1, .7), 6)); ball((cx, cy, 3.6), 1.6, green, 1, 1, .05); b = bmesh.new(); bmesh.ops.create_cone(b, cap_ends=True, segments=4, radius1=1.8, radius2=.1, depth=2.2); mesh(b, green, (cx, cy, 5.2), (0, 0, .78))
for s in (-1, 1): cube((cx + s * 5.6, cy, 0), (1.2, 1.2, 4.0), green); b = bmesh.new(); bmesh.ops.create_cone(b, cap_ends=True, segments=4, radius1=1.1, radius2=.05, depth=2.0); mesh(b, green, (cx + s * 5.6, cy, 4.0), (0, 0, .78))
glow((cx, cy - 3, 2.5), (.2, 1, .5), 1500); glow((cx, cy - 2, 6), (.2, 1, .5), 500)
# the four travellers on the road, walking toward the city
walker(-.9, -6, .1, 0, 1.0); walker(.4, -3.5, .1, 1, 1.05); walker(-1.4, -1, .1, 2, 1.0); walker(.6, 1.5, .1, 3, 1.1)
# twilight: pink-gold key low from the left, teal rim from behind
for c, w, p in (((1, .55, .35), 5.5, (-24, -14, 8)), ((.2, .8, .7), 2.2, (16, 24, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 85; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 2.5)); co.location = tg + Vector((-24, -72, 46))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
