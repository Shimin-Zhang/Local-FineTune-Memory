import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1342)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(r, g, b, em=0, metal=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (r, g, b, 1); p.inputs["Roughness"].default_value = .7; p.inputs["Metallic"].default_value = metal
    if em: p.inputs["Emission Color"].default_value = (r, g, b, 1); p.inputs["Emission Strength"].default_value = em
    return m
oak, wall, floor, black, key, mug, mug2, bulb, screen, plant, book, book2, steel = (
    paint(*c) for c in ((.3, .18, .09), (.12, .14, .2), (.2, .12, .07), (.03, .03, .035), (.1, .1, .12), (.7, .15, .1), (.1, .3, .5), (.2, .2, .22), (.35, .1, .05), (.05, .25, .1), (.6, .1, .1), (.1, .3, .4), (.5, .5, .55)))
bulb, screen = paint(1, .7, .3, 16), paint(.2, .5, 1, 3)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def ball(at, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return add(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=11, depth=3)
for v in bm.verts:
    v.co.y *= .85
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
add(bm, floor)
# two walls: back and left, with a window frame on the back wall
cube((0, 6.4, 0), (15, .5, 8), wall); cube((-7.4, 1.5, 0), (.5, 10, 8), wall)
cube((-3.5, 6.1, 3.2), (4.2, .15, 3.2), paint(.04, .08, .2)); cube((-3.5, 6.0, 3.2), (.15, .1, 3.4), wall); cube((-3.5, 6.0, 4.7), (4.4, .1, .15), wall)
cube((-3.5, 6.0, 3.1), (4.6, .3, .2), wall)
# the desk: top, two legs each side, a drawer unit on the right
cube((0, 0, 3.0), (12, 4.6, .35), oak)
for x in (-5.4, 5.4):
    for y in (-1.9, 1.9): cube((x, y, 0), (.4, .4, 3.0), black)
cube((0, -1.9, 0), (11, .3, .6), oak)
cube((4.6, 1.3, .1), (3.4, 2.2, 2.9), black)
for k in range(3): cube((4.6, .15, .5 + k * .9), (3.0, .12, .7), oak); cube((4.6, .05, .85 + k * .9), (.9, .1, .1), steel)
# monitor on a stand, with a screen glowing blue
cube((-1.5, 1.2, 3.35), (1.8, .5, .25), steel); cube((-1.5, 1.2, 3.6), (.3, .3, .9), steel)
cube((-1.5, 1.2, 4.5), (5.4, .25, 3.0), black); cube((-1.5, 1.05, 4.7), (5.0, .1, 2.6), screen)
for i in range(4): cube((-3.2 + i * 1.1, 1.0, 5.2), (.8, .06, .12), black)
cube((-1.5, .9, 5.0), (2.4, .06, .12), black)
# keyboard and mouse on the desk
cube((-1.5, -.6, 3.35), (4.4, 1.3, .2), key)
for r in range(3):
    for c in range(12): cube((-3.4 + c * .36, -.9 + r * .35, 3.55), (.3, .26, .06), black if (r + c) % 3 else mug2)
ball((1.4, -.7, 3.6), .38, black, .7)
# mug with steam and a coaster
cyl((3.0, -.3, 3.35), .55, .1, 8, black); cyl((3.0, -.3, 3.45), .4, .8, 8, mug)
for k in range(3): ball((3.0 + .1 * k, -.3, 4.5 + k * .5), .12 + .04 * k, bulb, .8)
# desk lamp: base, two arms, a cone shade and a glowing bulb
cyl((-4.6, 1.4, 3.35), .6, .2, 8, black)
cube((-4.6, 1.4, 3.5), (.18, .18, 2.2), steel, (0, .35, 0)); cube((-4.0, 1.4, 5.6), (.18, .18, 1.6), steel, (0, -.5, 0))
cyl((-3.2, 1.4, 6.3), .55, .9, 8, black, .25, (0, math.pi / 2 + .3, 0))
ball((-2.6, 1.4, 6.0), .35, bulb)
lamp("POINT", (1, .7, .3), 650, (-2.6, 1.4, 5.8)); lamp("POINT", (.3, .55, 1), 500, (-1.5, -.5, 5.0))
# books, a notebook, a pen holder and a small plant
for i, m in enumerate((book, book2, mug)): cube((-4.6 + i * .55, -.4, 3.35 + i * .22), (1.6, 1.1, .22), m, (0, 0, .1 * i))
cyl((-6.4, 1.2, 3.35), .3, .5, 6, mug2); cyl((-6.4, 1.2, 3.85), .55, .8, 6, plant, .15)
cube((6.8, 1.2, 0), (1.2, 1.2, 2.0), black)
# a chair in front of the desk
cube((-.5, -3.4, .1), (1.2, .2, 2.6), black)
for x in (-1.2, .2): cyl((x, -3.4, 0), .1, 1.6, 5, steel)
cube((-.5, -3.2, 1.5), (2.4, 2.2, .3), mug); cube((-.5, -2.1, 1.8), (2.4, .3, 2.0), mug)
for x in (-1.5, .5): cube((x, -3.2, 1.8), (.2, 1.8, .12), black)
lamp("SUN", (.5, .6, 1), 4, (-24, -20, 12), (0, 0, 3)); lamp("SUN", (1, .5, .3), 2, (22, 24, 10), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((12, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
