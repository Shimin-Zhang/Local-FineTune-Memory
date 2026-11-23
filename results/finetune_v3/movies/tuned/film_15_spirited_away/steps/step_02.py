import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1084)
sc = bpy.context.scene
ink = {}
def dye(name, rgb, em=0, rough=.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    ink[name] = m
dye("wood", (.3, .14, .07)); dye("red", (.55, .08, .05)); dye("roof", (.08, .12, .15)); dye("paper", (1, .6, .2), 7); dye("stone", (.3, .3, .33))
dye("gold", (.7, .5, .12)); dye("moss", (.1, .22, .12)); dye("lotus", (.5, .25, .4), 1.5); dye("steam", (.55, .6, .65), .15, 1); dye("black", (.02, .02, .03)); dye("pond", (.04, .12, .16), rough=.1)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(ink[m]); return o
def slab(at, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return put(bm, m, at, (0, 0, rz))
def post(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at, rot)
def puff(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return put(bm, m, at)
def roof(at, w, d, h, m, over=.6):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        if v.co.z > 0: v.co.x = 0; v.co.z += h
        v.co.x *= w + over * (v.co.z < 0) * 1 + over * (v.co.z > 0) * .3
        v.co.y *= d + over * (v.co.z < 0) * 1 + over * (v.co.z > 0) * .3
        v.co.z += h / 2 if v.co.z > 0 else 0
    return put(bm, m, at)
def lit(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# fix the roof: rebuild as proper hip roofs with a ridge, and drop the steam that hides the top
for o in list(sc.objects):
    if o.name.startswith("p") and o.location.z > 4 and o.location.y > 1: o.data.materials.clear(); o.data.materials.append(ink["roof"])
# a stone landing at the bridge end and a small pavilion gate
for i in range(4): slab((-1.5 - i * 1.0, -11.2 + i * .5, 0), (1.2, 1.4, .3 + i * .1), "stone")
for s in (-1, 1): post((s * 1.6, -10.5, 0), .22, 3.0, 6, "red")
slab((0, -10.5, 2.8), (4.2, .5, .3), "red"); roof((0, -10.5, 3.1), 4.6, 1.6, .8, "roof", .5)
slab((0, -10.5, 2.6), (3.6, .1, .1), "gold")
# lotus pads and flowers on the pond
for i in range(26):
    a = random.uniform(0, 6.28); r = random.uniform(3, 9.5); x, y = math.cos(a) * r, math.sin(a) * r - 1
    if y > 0 or abs(x) < 1.6 and y < -6: continue
    post((x, y, .2), random.uniform(.3, .55), .06, 7, "moss", rot=(0, 0, a))
for i in range(7):
    a = random.uniform(0, 6.28); r = random.uniform(4, 9); x, y = math.cos(a) * r, math.sin(a) * r - 1
    if y > 0: continue
    puff((x, y, .35), .25, "lotus", 1.0)
# glowing reflections on the pond: small emissive patches under the windows and bridge
for i in range(5): slab((-4.8 + i * 2.4, -3.5, .22), (1.0, 1.4, .03), "paper")
for i in range(6): slab((-1.5 + i * 1.1, -9.5 + i * 1.1 * .9 - 1.5, .22), (.8, .8, .03), "paper")
# steps up to the veranda
for i in range(4): slab((0, -.6 - i * .5, 0), (5, .5, .3 * (i + 1)), "wood")
# paper lanterns hanging from the veranda edge, larger than before
for i in range(5):
    x = -4.8 + i * 2.4
    post((x, -.3, 2.2), .03, 1.2, 4, "black"); post((x, -.3, 1.5), .35, .8, 6, "paper", .3)
    lit("POINT", (1, .5, .15), 60, (x, -.6, 1.8))
# a stone path from the gate to the landing, with side stones
for i in range(5): slab((0, -8.8 + i * .6, 0), (1.2, .5, .12), "stone", random.uniform(-.1, .1))
# a small dragonfly-sized boat (a little rowboat) moored by the steps
slab((4.5, -4.5, .2), (2.4, 1.0, .35), "wood", .5, .8); slab((4.5, -4.5, .5), (1.6, .6, .1), "black", .5)
post((3.6, -4.2, .5), .05, .9, 4, "wood"); slab((3.6, -4.2, 1.3), (.5, .05, .5), "red")
# a few more trees at the rim, and floating mist patches
for x, y, h in ((-11, -8, 4), (11, -7, 4.5), (-14, 7, 5)):
    post((x, y, 0), .3, h, 5, "wood", .15)
    for k in range(3): puff((x, y, h + k * .8), 1.6 - k * .35, "moss", .8)
for i in range(6): puff((random.uniform(-10, 10), random.uniform(-10, -3), .3), random.uniform(.8, 1.4), "steam", .15)
# moonlit rim light and a warm rim from behind
lit("SUN", (.4, .55, 1), 3.5, (-26, -18, 14), (0, 0, 3)); lit("SUN", (.8, .4, .9), 2.5, (24, 26, 12), (0, 0, 3))
lit("POINT", (1, .55, .2), 400, (0, -4, 2.2))
# camera: a little lower and closer so the roof tiers and the bridge read clearly
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 600
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((14, -62, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
