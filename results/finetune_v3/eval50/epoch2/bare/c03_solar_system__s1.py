import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1076)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def tone(r, g, b, e=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (r, g, b, 1); p.inputs["Roughness"].default_value = .8
    if e: p.inputs["Emission Color"].default_value = (r, g, b, 1); p.inputs["Emission Strength"].default_value = e
    return m
def mk(kind, m, x, y, z, sx, sy, sz, rot=(0, 0, 0), n=8):
    if kind == "ball": bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
    elif kind == "ring": bpy.ops.mesh.primitive_torus_add(vertices=16, major_segments=10, minor_segments=3)
    else: bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=1, radius2=1, depth=1)
    o = bpy.context.object; o.location = (x, y, z); o.scale = (sx, sy, sz); o.rotation_euler = rot; o.data.materials.append(m)
    return o
void, dust, orbit = tone(.012, .01, .03), tone(.08, .07, .1), tone(.25, .3, .5)
sun, core, fire = tone(1, .75, .2, 1.5), tone(1, .95, .6, 3), tone(1, .3, .05, 2)
col = [tone(.75, .4, .12), tone(.55, .5, .45), tone(.1, .35, .9), tone(.9, .35, .15)]
def shine(x, y, z, c, w):
    L = bpy.data.lights.new("s", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = (x, y, z); sc.collection.objects.link(o)
# the base: a dark disc of space dust with a rough, tapering underside
b = mk("cyl", void, 0, 0, -1.6, 15, 15, 3.2, n=10)
for v in b.data.vertices:
    if v.co.z < 0: v.co += Vector((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.2, .3)))
mk("cyl", dust, 0, 0, .05, 14.6, 14.6, .1, n=10)
# the sun, with a hot core and a spiky corona of little flames
mk("ball", core, 0, 0, 0, 2.4, 2.4, 2.4); mk("ball", sun, 0, 0, 0, 2.5, 2.5, 2.5)
for i in range(10):
    a = i * .63; mk("cone", fire, 2.9 * math.cos(a), 2.9 * math.sin(a), 0, .5, .5, 1.1 + i % 2 * .5, n=4)
shine(0, 0, 1, (1, .7, .3), 1600)
# four orbits and four planets, each a different colour, with a ring and moons
for k, (r, rad) in enumerate([(5.2, .7), (7.6, .9), (10.2, .6), (12.6, 1.0)]):
    mk("ring", orbit, 0, 0, .12, r, r, .03, n=10)
    a = k * 1.6 + .4; x, y = r * math.cos(a), r * math.sin(a)
    mk("ball", col[k], x, y, .12, rad, rad, rad)
    if k == 1: mk("ring", tone(.3, .28, .25), x, y, .12, rad * 1.8, rad * 1.8, .05, rot=(.5, 0, 0))
    if k == 2: mk("ball", tone(.5, .5, .55), x + rad * 2.4, y, .12, .2, .2, .2)
    if k == 3: mk("ball", tone(.5, .5, .55), x - rad * 2.2, y + .5, .12, .25, .25, .25)
    shine(x, y, rad + .5, (1, .75, .4), 40)
# a few asteroids drifting between the orbits, and stars on the dust
for i in range(14):
    a, r = random.uniform(0, 6.28), random.uniform(8.5, 11.2)
    mk("ball", tone(.3, .28, .26), r * math.cos(a), r * math.sin(a), .1, .15, .15, .12)
for i in range(16):
    a, r = random.uniform(0, 6.28), random.uniform(13, 14.2)
    mk("ball", core, r * math.cos(a), r * math.sin(a), .15, .08, .08, .08)
# two lights: cool starlight from the left, a faint warm rim from behind right
for c, w, p in (((.55, .65, 1), 3.5, (-30, -12, 12)), ((1, .55, .3), 1.5, (22, 28, 10))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("sun", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 0)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("space"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.004, .004, .012, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 0)); co.location = tg + Vector((0, -54, 28))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
