import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1164)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(r, g, b, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = n.inputs["Emission Color"].default_value = (r, g, b, 1)
    n.inputs["Roughness"].default_value = .8; n.inputs["Emission Strength"].default_value = glow
    return m
snow, snow2, coal, carrot, wood, coal2 = dye(.55, .62, .75), dye(.45, .52, .66), dye(.03, .03, .04), dye(.95, .4, .05), dye(.2, .12, .07), dye(.06, .06, .08)
scarf, pine, lantern, trunk = dye(.8, .08, .1), dye(.05, .2, .15), dye(1, .7, .25, 14), dye(.2, .13, .08)
def make(kind, m, p, s, r=(0, 0, 0), n=7, sub=1):
    bm = bmesh.new()
    if kind == "ico": bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=.5)
    elif kind == "cyl": bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=.5, radius2=.5, depth=1)
    elif kind == "cone": bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=.5, radius2=.05, depth=1)
    else: bmesh.ops.create_cube(bm, size=1)
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.scale, o.rotation_euler = p, s, r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def shine(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4, radius2=8, depth=2.6)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.3, .3)))
    else: v.co.z += random.uniform(-.08, .08)
me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
b = bpy.data.objects.new("b", me); b.location.z = -1.3; sc.collection.objects.link(b); b.data.materials.append(snow)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(5.5, 7.3)
    make("ico", snow2, (r * math.cos(a), r * math.sin(a), .1), (random.uniform(1, 2.2), random.uniform(1, 1.8), .5), (0, 0, random.random()))
# snowman: three lumps, hat, carrot, coal face, scarf, stick arms, coal buttons
make("ico", snow, (0, 0, 1.5), (3.4, 3.4, 3.0)); make("ico", snow, (0, 0, 3.9), (2.5, 2.5, 2.3)); make("ico", snow, (0, 0, 5.8), (1.7, 1.7, 1.6))
make("cyl", coal, (0, 0, 6.8), (1.5, 1.5, .35), n=8); make("cyl", coal, (0, 0, 7.4), (1.0, 1.0, .9), n=8)
make("cone", carrot, (0, -1.25, 4.0), (.45, .45, 1.5), (math.pi / 2, 0, 0), 5)
for s in (-1, 1):
    make("ico", coal, (s * .5, -1.0, 4.5), (.28, .28, .28)); make("ico", coal, (s * .3, -1.05, 3.55), (.17, .17, .17)); make("ico", coal, (s * .7, -1.0, 3.5), (.17, .17, .17))
make("cyl", scarf, (0, 0, 3.0), (2.7, 2.7, .45), n=8); make("cube", scarf, (.9, -1.0, 2.2), (.5, .2, 1.2))
for s in (-1, 1):
    make("cyl", wood, (s * 2.4, 0, 3.2), (.14, .14, 2.4), (0, s * .9, 0), 5); make("cyl", wood, (s * 3.0, 0, 4.2), (.1, .1, 1.2), (0, s * 1.9, 0), 5)
for k in range(3): make("ico", coal2, (0, -1.6, 1.0 + k * .8), (.3, .3, .3))
# a string of glowing lanterns on a pole beside him, and a small fir
make("cyl", wood, (-4.5, -2.5, 2.5), (.2, .2, 5), n=5); make("cyl", wood, (-4.5, -2.5, 4.8), (.12, .12, 2.2), (0, .9, 0), 5)
for i in range(5):
    x = -4.5 + i * .9
    make("ico", lantern, (x, -2.5, 4.8 - .45 * math.sin(i / 4 * math.pi) - .2), (.4, .4, .5)); shine("POINT", (1, .7, .25), 120, (x, -2.5, 4.4))
for k in range(3): make("cone", pine, (4.5, 2.5, 1.0 + k * 1.1), (2.6 - k * .7, 2.6 - k * .7, 1.6), (0, 0, k), 6)
make("cyl", trunk, (4.5, 2.5, .4), (.35, .35, .8), n=5)
for i in range(6): make("ico", snow2, (random.uniform(-7, 7), random.uniform(2, 7), .3), (1.5, 1.2, .5), (0, 0, random.random()))
shine("SUN", (.55, .65, 1), 4, (-14, -10, 8), (0, 0, 3)); shine("SUN", (1, .5, .3), 2.2, (12, 14, 7), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 300
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.6)); co.location = t + Vector((5, -31, 19))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
