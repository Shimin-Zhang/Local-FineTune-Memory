import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1311)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def mat(r, g, b, e=0, ro=.9):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (r, g, b, 1); p.inputs["Roughness"].default_value = ro
    if e: p.inputs["Emission Color"].default_value = (r, g, b, 1); p.inputs["Emission Strength"].default_value = e
    return m
def add(k, m, p, s, r=(0, 0, 0), n=6):
    if k == "box": bpy.ops.mesh.primitive_cube_add(size=1)
    elif k == "ball": bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=.5)
    else: bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=.5, radius2=.5, depth=1)
    o = bpy.context.object; o.location = p; o.scale = s; o.rotation_euler = r
    o.data.materials.append(m); return o
def lamp(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
def rough(o, a):
    for v in o.data.vertices: v.co += Vector((random.uniform(-a, a), random.uniform(-a, a), random.uniform(-a, a)))

floor, wall, rug, wood, wood2, black = mat(.1, .07, .06), mat(.07, .08, .11), mat(.14, .06, .08), mat(.28, .15, .08), mat(.2, .1, .06), mat(.02, .02, .025)
shade, bulb, paper, red, blue, green, brass = mat(1, .62, .25, 9), mat(1, .75, .4, 20), mat(.55, .5, .4), mat(.5, .08, .06), mat(.1, .2, .5), mat(.1, .35, .2), mat(.7, .5, .15, 0, .4)
for i in range(10):
    for j in range(8): add("box", floor if (i + j) % 2 else wood2, (-4.5 + i, -3.5 + j, -.5), (1.02, 1.02, 1))
for x in range(-5, 5): add("box", black, (x, 4.6, 0), (.1, .1, .2))
add("box", wall, (0, 5, 2.5), (12, .5, 5)); add("box", wall, (-6, 0, 2.5), (.5, 10, 5))
add("box", black, (-6, 0, 5.1), (.6, 10.4, .3)); add("box", black, (0, 5, 5.1), (12.4, .6, .3))
add("box", rug, (0, -.4, .03), (7, 4.6, .06)); add("box", mat(.2, .1, .12), (0, -.4, .07), (6.2, 3.8, .04))
# desk: top, apron, four tapered legs, drawer unit with brass pulls
add("box", wood, (0, 1, 1.5), (5.4, 2.2, .22)); add("box", wood2, (0, 1, 1.32), (5, 1.8, .14))
for sx in (-2.4, 2.4):
    for sy in (-.8, .8): add("cyl", wood2, (sx, 1 + sy, .75), (.22, .22, 1.5), n=5)
add("box", wood2, (1.4, 1.9, .95), (2, .8, 1)); 
for z in (.75, 1.1): add("box", brass, (1.4, 1.48, z), (.5, .06, .06))
# lamp: weighted base, tilted arm, joint, cone shade, glowing bulb under it
add("cyl", black, (-1.5, 1.5, 1.72), (.9, .9, .16), n=8)
add("cyl", black, (-1.5, 1.5, 2.4), (.14, .14, 1.3), (.5, 0, 0), 5); add("ball", black, (-1.5, .9, 3.0), (.3, .3, .3))
add("cyl", black, (-1.5, .9, 3.1), (.1, .1, .8), (-.6, 0, 0), 5)
add("cyl", shade, (-1.5, .5, 3.0), (1.3, 1.3, .8), (.5, 0, 0), 8)
add("ball", bulb, (-1.5, .5, 2.7), (.5, .5, .5))
lamp("POINT", (1, .65, .28), 700, (-1.5, .4, 2.5)); lamp("POINT", (1, .65, .3), 150, (-1.5, .8, 1.8))
# papers, books, inkwell, pen, mug, chair, framed window, shelf, globe
for k in range(3): add("box", paper, (-1.2 + k * .25, .7 - k * .1, 1.64 + k * .02), (1.4, 1, .04), (0, 0, k * .25 - .3))
for k, c in enumerate((red, blue, green)): add("box", c, (1.8, .5, 1.68 + k * .14), (1.4, 1, .14), (0, 0, k * .15))
add("cyl", black, (2.3, 1.2, 1.7), (.3, .3, .3), n=6); add("cyl", brass, (2.3, 1.2, 1.9), (.12, .12, .12), n=6)
add("box", black, (-.4, .2, 1.64), (.8, .08, .05), (0, 0, .5)); add("cyl", brass, (2.4, -.2, 1.72), (.4, .4, .4), n=7)
add("cyl", wood2, (0, -1.4, .55), (1.2, 1.2, 1.1), n=6); add("box", wood2, (0, -1.4, 1.2), (1.2, .12, 1.2)); add("box", wood2, (0, -1.9, 1.1), (1.2, .9, .12))
add("box", black, (-2.6, 4.72, 3.2), (2.2, .1, 2.4)); add("box", mat(.03, .04, .08), (-2.6, 4.65, 3.2), (1.9, .06, 2.1))
add("box", wood2, (3, 4.65, 3.6), (3, .5, .12)); add("cyl", green, (3.5, 4.65, 3.95), (.7, .7, .7), n=6); add("cyl", brass, (3.5, 4.65, 3.72), (.1, .1, .3), n=5)
lamp("SUN", (.4, .5, 1), 1.5, (14, -22, 8), (0, 0, 2)); lamp("SUN", (1, .45, .3), 1, (-14, 20, 9), (0, 0, 2))
w = bpy.data.worlds.new("dark"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.005, .004, .008, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 300
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 2.4)); co.location = t + Vector((6, -26, 16))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
