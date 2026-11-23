import bpy, bmesh, math, random
from mathutils import Vector
random.seed(536)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
plaster, plaster2, floor, wood, cheese, hole = pigment((.4, .36, .3)), pigment((.33, .3, .27)), pigment((.2, .14, .1)), pigment((.3, .17, .09)), pigment((.9, .65, .12)), pigment((.02, .02, .02))
red, blue, green, pink, thread, crumb = pigment((.65, .1, .08)), pigment((.1, .25, .6)), pigment((.12, .45, .2)), pigment((.7, .3, .4)), pigment((.7, .65, .55)), pigment((.7, .55, .3))
candle, flame, glass = pigment((.8, .78, .7)), pigment((1, .6, .12), 18), pigment((.4, .6, .65))
def form(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("f"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("f", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(x, y, z, w, d, h, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return form(bm, m, (x, y, z), (0, 0, rz))
def rod(x, y, z, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return form(bm, m, (x, y, z), rot)
def lamp(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 10 + random.uniform(-1, 1), v.co.y * 10 + random.uniform(-1, 1), -3 + random.uniform(-.8, .4)))
    else: v.co = Vector((v.co.x * 15, v.co.y * 15, 0))
form(bm, floor)
# two plaster walls meet in the corner; the back wall has an arched door cut from it
for i in range(4):
    cube(-7.5 + i * 5, 7.5, 0, 5, .8, 9, plaster if i % 2 else plaster2)
    cube(-7.5, -7.5 + i * 5, 0, .8, 5, 9, plaster if i % 2 else plaster2)
for s in (-1, 1):
    cube(s * 1.6, 7.1, 0, 1.6, .5, 2.4, plaster)
    cube(s * 1.6, 7.1, 3.5, 1.6, .5, 1.6, plaster)
    cube(s * .8, 7.1, 3.5, .5, .5, 1.6, plaster)
cube(0, 7.1, 0, 1.6, .5, 2.4, plaster)
cube(0, 7.0, 0, 2.6, .6, 2.4, hole)
cube(0, 7.2, 3.5, 2.6, .5, 1.6, hole)
for s in (-1, 1):
    cube(s * 1.4, 6.7, 0, .3, .3, 2.6, wood)
cube(0, 6.7, 2.6, 3.2, .3, .3, wood)
cube(0, 6.7, 3.9, 2.2, .3, .3, wood)
# cheese wheel table with a big wheel and a wedge
cube(3.5, 4, 0, 3.2, 2.2, 1.4, wood)
for sx in (-1, 1):
    for sy in (-1, 1): cube(3.5 + sx * 1.4, 4 + sy * .9, 0, .2, .2, 1.4, wood)
rod(3.5, 4, 1.4, 1.0, .5, 9, cheese)
for i in range(5): rod(3.5 + .5 * math.cos(i * 1.3), 4 + .5 * math.sin(i * 1.3), 1.9, .12, .05, 5, hole, rot=(math.pi / 2, 0, 0))
rod(3.5, 4, 1.9, .85, .05, 9, cheese)
# matchbox beds, each with a blanket and pillow
for i, (bx, by, m) in enumerate(((-5.5, 4.5, red), (-5.5, 1.5, blue), (-2.5, 5.5, green))):
    cube(bx, by, 0, 1.6, 2.4, .5, wood)
    cube(bx, by - .2, .5, 1.5, 2.0, .2, m)
    cube(bx, by + .9, .5, 1.3, .6, .2, glass)
# thread spools, a candle in a glass, crumbs
for i, (x, y, m) in enumerate(((1.5, 5, red), (2.4, 5.2, blue), (3.2, 4.9, green), (1.8, 4.2, pink))):
    rod(x, y, 0, .35, .8, 8, m); rod(x, y, 0, .5, .15, 8, wood); rod(x, y, .65, .5, .15, 8, wood)
rod(-.8, 5.5, 0, .3, .3, 8, wood)
rod(-.8, 5.5, .3, .16, 1.0, 6, candle)
rod(-.8, 5.5, 1.3, .22, .5, 6, glass, .1)
rod(-.8, 5.5, 1.3, .12, .5, 5, glass, .05)
rod(-.8, 5.5, 1.8, .1, .4, 5, flame, .02)
lamp((-1.5, 5, 2.6), (1, .6, .15), 350)
for i in range(30):
    t = i / 29; x = -6 + t * 8 + random.uniform(-.3, .3); y = 6.2 - t * 4.5 + random.uniform(-.4, .4)
    cube(x, y, 0, .22, .18, .12, crumb, random.random() * 3)
lamp((0, 4, 3), (1, .75, .4), 250)
for c, w, p in (((.55, .65, 1), 4.5, (22, -20, 10)), ((1, .55, .25), 2.2, (-20, -16, 8))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .045, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
tg = Vector((-.5, 0, 3.5)); co.location = tg + Vector((14, -34, 22))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
