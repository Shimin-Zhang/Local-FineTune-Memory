import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1254)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def tone(name, rgb, glow=0, rough=.8):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    mats[name] = m
for k, v in dict(concrete=(.16, .17, .2), court=(.08, .22, .3), line=(.7, .72, .75), post=(.25, .27, .3), bench=(.35, .2, .1),
                 cooler=(.1, .3, .5), steel=(.2, .2, .22), city=(.12, .14, .2), roof=(.08, .09, .11), shirt=(.8, .3, .1), shirt2=(.2, .5, .8)).items(): tone(k, v)
tone("glass", (.35, .6, .8), 1.2, .1); tone("flood", (1, .95, .8), 22); tone("neon", (.1, .9, 1), 14); tone("amber", (1, .6, .2), 10); tone("cyan", (.1, .8, .9), 10)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return shape(bm, m, at, rot)
def pole(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color, l.energy = c, w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=14.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
shape(bm, "roof")
slab((0, 0, 0), (15, 10.5, .25), "concrete")
slab((0, 0, .25), (13.6, 9.2, .1), "court")
for x in (-6.8, 6.8): slab((x, 0, .35), (.12, 9.2, .02), "line")
slab((0, -4.6, .35), (13.6, .12, .02), "line"); slab((0, 4.6, .35), (13.6, .12, .02), "line")
slab((0, 0, .35), (6.8, .1, .02), "line")
slab((0, 0, .35), (.1, 9.2, .02), "line")
for sx in (-1, 1):
    for sy in (-1, 1): pole((sx * 6.8, sy * 4.6, .25), .1, 4.2, 5, "post")
    slab((sx * 6.8, 0, 4.45), (.15, 9.2, .12), "post"); slab((0, sy * 4.6, 4.45), (13.6, .15, .12), "post")
    slab((sx * 6.8, sy * 4.6, .25), (.15, .15, 4.2), "post")
    for sy2 in (-1, 1): slab((sx * 6.8, sy2 * 4.6, 2.2), (.1, 9.2, .06), "post")
    for x2 in (-1, 1): slab((x2 * 6.8, sy * 4.6, 2.2), (13.6, .1, .06), "post")
    slab((sx * 6.8, 0, .3), (.05, 9.0, 4.0), "glass"); slab((0, sy * 4.6, .3), (13.4, .05, 4.0), "glass")
    for x2 in (-4.5, 4.5): slab((x2, sy * 4.6, .3), (.06, .06, 4.0), "post")
for i in range(11):
    x = -6.0 + i * 1.2
    pole((x, 0, .35), .05, 1.2, 4, "post"); slab((x, 0, 1.5), (.08, .08, .08), "line")
slab((0, 0, 1.5), (12.2, .04, .04), "line")
slab((0, 0, 1.4), (12.2, .5, .1), "neon")
for x in (-6.9, 6.9):
    pole((x, 0, .25), .12, 7.5, 6, "steel")
    slab((x, 0, 7.5), (1.4, 1.0, .6), "steel")
    slab((x * .97, 0, 7.4), (.3, .8, .15), "flood")
    lamp("SPOT", (1, .95, .8), 3000, (x * .95, 0, 7.4), (0, 0, 0))
for i in range(2):
    slab((7.2 + i * 1.6, -2.5, .25), (1.4, .6, .1), "bench"); slab((7.2 + i * 1.6, -2.9, .25), (1.4, .1, .6), "bench")
    for dx in (-.5, .5): slab((7.2 + i * 1.6 + dx, -2.5, .25), (.1, .5, .25), "steel")
    pole((7.2 + i * 1.6, -2.5, .35), .22, .5, 6, "shirt" if i == 0 else "shirt2", .18)
slab((8.2, 3.5, .25), (1.8, 1.2, 1.8), "cooler"); slab((8.2, 2.85, .4), (1.6, .08, 1.3), "cyan")
slab((8.2, 3.5, 2.05), (2.0, 1.4, .12), "steel"); slab((8.2, 2.85, 1.5), (1.0, .06, .12), "neon")
lamp("POINT", (.1, .8, .9), 250, (8.2, 2.2, 1.2))
for x in (-8.5, -5.5, -2.5, 5.0, 10.5):
    h = random.uniform(3, 6.5); w = random.uniform(2.2, 3.2)
    slab((x, 10.2 - random.uniform(0, 1.5), 0), (w, 2.2, h), "city")
    for k in range(int(h * 1.5)):
        slab((x + random.uniform(-.8, .8), 9.0 - random.uniform(0, 1.2), .8 + k * .5), (.4, .08, .22), random.choice(("amber", "cyan", "neon")))
for x in (-11.5, 12.0):
    slab((x, 6.5, 0), (2.0, 2.0, 3.0), "city"); slab((x, 5.45, 1.0), (1.2, .08, .3), "amber")
lamp("SUN", (.45, .55, 1), 4.5, (-26, -20, 12), (0, 0, 0)); lamp("SUN", (1, .4, .55), 2.2, (24, 26, 10), (0, 0, 0))
w = bpy.data.worlds.new("blue"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .06, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 2.5)); co.location = t + Vector((10, -62, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
