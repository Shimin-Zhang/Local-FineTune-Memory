import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1307)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
turf, turf2, rock, rock2, wool, face, post, ink, moss = (tone(c) for c in (
    (.08, .15, .09), (.05, .1, .08), (.3, .3, .33), (.2, .2, .24), (.55, .5, .42), (.1, .08, .07), (.25, .15, .09), (.03, .03, .04), (.1, .2, .1)))
lines = [tone((.3, .9, 1), 5), tone((.8, .3, 1), 5), tone((1, .7, .2), 5), tone((.4, 1, .5), 5)]
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, m, at, rot)
def post_(at, r, h, m, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at)
def lump(at, s, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2])) * random.uniform(.88, 1.12)
    return put(bm, m, at)
def glow(c, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=3.4)
for v in bm.verts:
    v.co.x *= 1.15; v.co.y *= .95
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.08, .08)
    v.co.z -= 1.7
put(bm, turf)
for i in range(10):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=random.uniform(1.2, 2.2), radius2=random.uniform(1.2, 2.2), depth=.06)
    put(bm, turf2, (random.uniform(-9, 9), random.uniform(-7, 7), .02), (0, 0, random.random()))
# the ley lines: four glowing ribbons crossing the field at the standing stone
for i, (a, b) in enumerate(((math.radians(15), math.radians(100)), (math.radians(70), math.radians(160)), (math.radians(120), math.radians(30)), (math.radians(200), math.radians(320)))):
    for k in range(7):
        t = k / 6 - .5
        for r, w in ((.16, 0), (.06, 0)):
            p = Vector((math.cos(a) * t * 12, math.sin(a) * t * 12, .05 + .03 * k))
            slab(p, (1.9, w * 2 + .05, .05), lines[i], (0, 0, a + math.pi / 2))
    glow(((.3, .9, 1), (.8, .3, 1), (1, .7, .2), (.4, 1, .5))[i], 500, (math.cos(a) * 4, math.sin(a) * 4, 1.2))
# the standing stone: tall, tapering, with a cap and a few mossy boulders
post_((0, 0, 0), 1.0, 4.2, rock, 6, .55)
post_((0, 0, 4.2), .62, .5, rock2, 6, .4)
for i in range(5):
    a = i * 1.26
    lump((math.cos(a) * 1.8, math.sin(a) * 1.8, .3), (.7, .6, .45), rock2)
for i in range(3): lump((random.uniform(-.3, .3), random.uniform(-.3, .3), 1.5 + i * 1.2), (.15, .15, .3), moss)
# sleeping sheep: wool body, dark face, legs tucked, in a loose cluster
for sx, sy, a in ((-4.5, -3.5, .3), (-2.5, -5, 2.4), (-6, -1, 5), (-3.5, 1.5, 1.2), (4.5, -4, 3.5), (6.5, -1.5, 5.5), (5, 3.5, 2)):
    lump((sx, sy, .55), (1.0, .65, .55), wool, (0, 0, a))
    f = Vector((sx, sy, .55)) + Vector((math.cos(a), math.sin(a), 0)) * .95
    lump(f, (.3, .3, .3), face, (0, 0, a))
    for dx, dy in ((.4, .3), (.4, -.3), (-.4, .3), (-.4, -.3)):
        post_((sx + dx * math.cos(a) - dy * math.sin(a), sy + dx * math.sin(a) + dy * math.cos(a), 0), .08, .35, face, 4)
# old signpost with a tilted board and a broken arm
post_((8, 4.5, 0), .16, 3.2, post, 5)
slab((8.3, 4.5, 2.2), (2.0, .1, .7), post, (0, 0, .15))
for i in range(3): slab((7.6 + i * .6, 4.4, 2.45 - i * .05), (.4, .05, .12), ink, (0, 0, .15))
slab((7.4, 4.5, 1.6), (1.2, .1, .5), post, (0, .2, -.3))
for i in range(3): slab((7.0 - i * .3, 4.4, 1.55 + i * .12), (.3, .05, .1), ink, (0, .2, -.3))
for i in range(9):
    a = random.uniform(0, 6.28); r = random.uniform(8, 11)
    lump((math.cos(a) * r * 1.1, math.sin(a) * r * .85, .3), (random.uniform(.4, .8), random.uniform(.4, .7), .35), rock2)
for i in range(14):
    x, y = random.uniform(-10, 10), random.uniform(-7.5, 7.5)
    if abs(x) < 1.5 and abs(y) < 1.5: continue
    post_((x, y, 0), .05, random.uniform(.5, 1.0), moss, 4, .01)
for c, w, p in (((.45, .6, 1), 4.5, (-24, -16, 9)), ((.8, .3, .9), 2.5, (22, 22, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .012, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((14, -50, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
