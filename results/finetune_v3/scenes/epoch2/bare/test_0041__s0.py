import bpy, bmesh, math, random
from mathutils import Vector
random.seed(648)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def clay(c, e=0, r=.9):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
turf, dirt, plank, thatch, post, rock, iron, flame, sea, snow = (clay((.12, .22, .08)), clay((.22, .17, .11)), clay((.35, .22, .12)), clay((.4, .32, .14)),
    clay((.2, .12, .07)), clay((.2, .2, .22)), clay((.05, .05, .06), 0, .4), clay((1, .5, .1), 12), clay((.06, .12, .18), 0, .2), clay((.7, .75, .8)))
def put(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.rotation_euler = p, r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(p, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return put(bm, m, p, (0, 0, rz))
def post_(p, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, p)
def glow(p, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
# base: a round island of turf on a rock keel, with a small harbour cut into the front
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=8, radius2=16, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.3, .3)))
    v.co.z -= 1.6
put(bm, turf)
blk((0, -14.4, .02), (11, 3.4, .1), sea, 0)
for i in range(5): blk((-6 + i * 3, -12.6 + (i % 2) * .3, .05), (1.2, .8, .3), rock, i * .4)
# the ring: 28 earth bank segments with four gaps for gates; a ditch ring inside; plank roads across
R, H = 11.5, 1.9
gates = [0, 1, 2, 3]
for i in range(28):
    a = i * 2 * math.pi / 28
    if min(abs(a - g * math.pi / 2), 2 * math.pi - abs(a - g * math.pi / 2)) < .22 for g in gates: continue
    blk((R * math.cos(a), R * math.sin(a), 0), (2.7, 3.4, H), turf, a + math.pi / 2, .85)
    blk((R * math.cos(a), R * math.sin(a), H * .85), (2.0, 2.6, .2), dirt, a + math.pi / 2)
for g in gates:
    a = g * math.pi / 2; c, s = math.cos(a), math.sin(a)
    blk((R * c, R * s, 0), (2.6, 2.6, 1.0), plank, a + math.pi / 2)
    for sd in (-1, 1):
        px, py = R * c - s * sd * 1.5, R * s + c * sd * 1.5
        post_((px, py, 0), .3, 2.8, 5, post); blk((px, py, 2.6), (.5, .5, .5), iron, 0)
    glow((R * c * .8, R * s * .8, 1.2), (1, .5, .15), 220)
for g in gates:
    a = g * math.pi / 2; c, s = math.cos(a), math.sin(a)
    blk((c * 5.7, s * 5.7, .03), (11.4, 2.4, .1), dirt, a + math.pi / 2)
    blk((s * 5.7, -c * 5.7, .03), (11.4, 2.4, .1), a)
for i in range(10):
    a = i * .63 + .3
    blk((9.6 * math.cos(a), 9.6 * math.sin(a), .02), (1.6, 1.6, .25), rock, a, .6)
# longhouses in four groups, each facing the road; turf roof with ridge pole and a glowing doorway
def house(x, y, rz, L=7):
    blk((x, y, 0), (L, 3.2, 1.5), plank, rz, .95)
    for sd in (-1, 1):
        r = blk((x, y, 1.5), (L + .3, 1.9, 1.4), thatch, rz, .5)
        r.location = Vector((x, y, 1.5)) + Vector((math.cos(rz + math.pi / 2) * sd * .75, math.sin(rz + math.pi / 2) * sd * .75, .5))
    c, s = math.cos(rz), math.sin(rz)
    d = Vector((-s, c, 0)) * (L / 2 + .05)
    blk(Vector((x, y, 0)) + d, (.9, .15, 1.1), flame, rz)
    glow(Vector((x, y, 1)) + d * 1.6, (1, .5, .15), 160)
    for sd in (-1, 1): post_((x + d.x * sd * .9, y + d.y * sd * .9, 1.4), .12, 1.8, 4, post)
for gx, gy, rz in ((-4.6, -4.6, 0), (4.6, -4.6, 0), (-4.6, 4.6, 0), (4.6, 4.6, 0)):
    for i in range(3):
        off = (i - 1) * 3.0
        if rz == 0: house(gx + off * .95, gy, rz, 5.4)
        else: house(gx, gy + off * .95, rz, 5.4)
# central bonfire, a well, and a few barrels and a rowing boat at the harbour
post_((0, 0, 0), 1.2, .5, 7, rock); post_((0, 0, .5), .9, .3, 6, iron, .5)
post_((0, 0, .8), .5, 1.6, 5, flame, .05); glow((0, 0, 2.0), (1, .5, .15), 900)
for i in range(6):
    a = i * 1.05; blk((1.3 * math.cos(a), 1.3 * math.sin(a), .2), (.5, .3, .3), post, a)
post_((-2.5, 2.5, 0), .6, 1.0, 8, post); post_((-2.5, 2.5, 1.0), .5, .1, 8, plank, .5)
for i in range(3): post_((3 + i * 1.1, -9.2, 0), .4, .9, 7, post)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=.5, radius2=.9, depth=5.2)
for v in bm.verts: v.co.x *= .6
put(bm, plank, (-2, -13.6, .4), (0, math.pi / 2, 0))
blk((-2, -13.6, .8), (4.2, .1, .1), post, 0)
for i in range(3): blk((-3 + i * 1.2, -13.6, .9), (.1, .9, .08), post)
for i in range(4): post_((7.2 + i * .0, -12.2 + i * .9, 0), .12, 2.2, 4, post)
# cold dusk: steel-blue key from the left, orange rim from behind, fire glow inside
for c, e, p in (((.5, .65, 1), 4.2, (-28, -14, 11)), ((1, .45, .2), 2.2, (22, 24, 9))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .018, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, -1, 1.5)); co.location = t + Vector((12, -62, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
