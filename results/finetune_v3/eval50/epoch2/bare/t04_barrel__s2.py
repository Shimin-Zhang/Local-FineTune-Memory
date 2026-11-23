import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1237)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def rust(r, g, b, glow=0):
    m = bpy.data.materials.new("rust"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .9
    if glow: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = glow
    return m
def shape(kind, m, p, s, r=(0, 0, 0), n=8):
    if kind == "box": bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(vertices=n, depth=1)
    else: bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1)
    o = bpy.context.object; o.location = p; o.scale = s; o.rotation_euler = r
    o.data.materials.append(m); return o
def shine(kind, c, e, p, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
def weld(o, w, at):
    for v in o.data.vertices:
        if v.co.z > .4: v.co += Vector((random.uniform(-w, w), random.uniform(-w, w), random.uniform(-w, w)))
    for f in o.data.polygons: f.center.z += at
    return o
dust, dirt, iron = rust(.22, .17, .1), rust(.14, .1, .07), rust(.07, .06, .06)
oxide = [rust(.45, .16, .05), rust(.3, .12, .06), rust(.5, .28, .08)]
band, drip, puddle = rust(.1, .09, .09), rust(.55, .18, .05), rust(.04, .05, .05)
fire, flame, soot, glass = rust(1, .35, .05, 14), rust(1, .7, .2, 20), rust(.03, .03, .03), rust(.1, .3, .3, 3)
bpy.ops.mesh.primitive_cone_add(vertices=9, radius1=2, radius2=7, depth=3.6, location=(0, 0, -1.8))
weld(bpy.context.object, .5, 0)
for m in (dust, dirt, iron): bpy.context.object.data.materials.append(m)
# the barrel: tapered body, dished lid, three reinforcing bands, rivets, a spout and a bung
bx, by = -1.5, 1.0
weld(shape("cyl", oxide[0], (bx, by, 1.6), (1.6, 1.6, 3.2), n=10), .04, 0)
shape("cyl", band, (bx, by, .5), (1.7, 1.7, .22), n=10); shape("cyl", band, (bx, by, 2.7), (1.55, 1.55, .22), n=10)
shape("cyl", band, (bx, by, 1.6), (1.65, 1.65, .2), n=10)
shape("cyl", oxide[1], (bx, by, 3.25), (1.5, 1.5, .12), n=10)
shape("cyl", oxide[1], (bx, by, 3.4), (.9, .9, .12), n=10)
for k in range(10):
    a = k * math.tau / 10
    shape("cyl", iron, (bx + 1.62 * math.cos(a), by + 1.62 * math.sin(a), 1.6), (.08, .08, .08), (0, math.pi / 2, a), 5)
shape("cyl", iron, (bx + 1.4, by - .4, .9), (.12, .12, .8), (0, 1.57, 0), 6); shape("cyl", iron, (bx + 1.7, by - .4, .6), (.1, .1, .3), (0, 1.57, 0), 6)
shape("cyl", iron, (bx - .4, by + .3, 3.4), (.15, .15, .1), n=6)
for k, (dx, dy, h) in enumerate(((.8, .2, 1.0), (-.7, -.5, .6), (.2, .9, .8), (-.5, .6, 1.3))):
    shape("cyl", drip, (bx + dx, by + dy, 3.3 - h / 2), (.06, .06, h), n=4)
# fire burning inside the lid: logs, flames, embers and the glow they throw
for k in range(3):
    shape("cyl", soot, (bx, by, 3.55), (.14, .14, 1.6), (0, math.pi / 2, k * 1.05), 5)
for k in range(5):
    a = k * 1.26; shape("cone", flame if k % 2 else fire, (bx + .4 * math.cos(a), by + .4 * math.sin(a), 4.4), (.3, .3, 1.4), n=5)
shape("cone", flame, (bx, by, 4.7), (.4, .4, 2.0), n=5)
for k in range(8): shape("ico", fire, (bx + random.uniform(-1.4, 1.4), by + random.uniform(-1.4, 1.4), 3.6), (.08, .08, .08))
shine("POINT", (1, .4, .08), 2200, (bx, by, 4.6))
# a rusted ladder, a leaning drum, a crate, a puddle and a glowing flask
for s in (-.5, .5): shape("box", oxide[2], (4.2 + s, 1.0, 1.7), (.1, .1, 3.4), (0, .12, 0))
for k in range(6): shape("box", oxide[2], (4.2, 1.0, .6 + k * .55), (1.1, .1, .08))
shape("cyl", oxide[1], (2.6, -1.6, 1.1), (1.1, 1.1, 2.2), (.2, 0, 0), 9)
shape("box", oxide[0], (-4.2, -1.6, .7), (1.2, 1.2, 1.4)); shape("box", band, (-4.2, -1.6, .7), (1.25, .1, 1.45))
shape("cyl", puddle, (-.5, -3.4, .05), (1.8, 1.1, .05), n=8)
shape("ico", glass, (-3.6, 3.2, .4), (.4, .4, .5)); shine("POINT", (.2, .8, .7), 120, (-3.6, 3.2, 1.0))
for k in range(14):
    x, y = random.uniform(-6, 6), random.uniform(-5.5, 5.5)
    if math.hypot(x - bx, y - by) > 2.4: shape("ico", random.choice((dust, dirt, oxide[1])), (x, y, .1), (random.uniform(.2, .55),) * 3)
# cold dawn: pale blue key low from the left, orange rim from behind the fire
shine("SUN", (.6, .7, 1), 4.5, (-16, -10, 6), (0, 0, 2)); shine("SUN", (1, .5, .2), 2.5, (14, 14, 7), (0, 0, 2))
w = bpy.data.worlds.new("dawn"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .025, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.4)); co.location = t + Vector((-10, -30, 19))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
