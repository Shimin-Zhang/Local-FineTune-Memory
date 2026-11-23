import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1106)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def mat(r, g, b, em=0):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .55
    if em: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = em
    return m
slab, slab2, wall, brass, teal, rust, lamp = mat(.1, .1, .12), mat(.16, .16, .19), mat(.035, .035, .05), mat(.6, .4, .12), mat(.1, .4, .42), mat(.5, .15, .08), mat(1, .65, .25, 14)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at)
def ball(at, r, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r); return add(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floating slab: chequered top of two greys, rough underside, glowing rim line
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 15 + random.uniform(-1, 1), v.co.y * 15 + random.uniform(-1, 1), -3.2 + random.uniform(-.8, .4)))
    else: v.co = Vector((v.co.x * 21, v.co.y * 21, 0))
add(bm, slab)
for i in range(6):
    for j in range(6):
        if (i + j) % 2: box((-9.25 + i * 3.5, -9.25 + j * 3.5, 0), (3.5, 3.5, .12), slab2)
for s in (-1, 1):
    box((s * 10.5, 0, .05), (.3, 20.6, .12), lamp); box((0, s * 10.5, .05), (20.6, .3, .12), lamp)
# two walls at the back with a thin ledge and a hanging lamp
box((0, 10.4, 0), (21, .6, 8.5), wall); box((-10.4, 0, 0), (.6, 21, 8.5), wall)
box((-10.1, 0, 3.2), (.5, 14, .35), slab2)
for i in range(5): box((-10.1, -5 + i * 2.6, 3.5), (.5, 1.2, 1.0), (rust, teal, brass)[i % 3])
box((-9.6, -4.5, 8.4), (.1, .1, 2.0), brass); box((-9.6, -4.5, 7.6), (1.2, 1.2, .6), lamp)
lamp("POINT", (1, .65, .25), 1400, (-9.6, -4.5, 7.4))
# the three primitives: sphere, cube, cone, each on a plinth
box((-5, -1, 0), (3.2, 3.2, .5), slab2); ball((-5, -1, 2.3), 1.8, teal)
box((1, 1.5, 0), (3.2, 3.2, .5), slab2); box((1, 1.5, .5), (2.6, 2.6, 2.6), brass, (0, 0, .4))
box((6.5, -2, 0), (3.2, 3.2, .5), slab2); cone((6.5, -2, .5), 1.9, 3.6, 8, rust)
for i in range(4): cone((-8.5 + i * .5, 5 + i * .4, .12), .5, 1.0, 6, teal if i % 2 else rust, .12)
for i in range(3): ball((-2 + i * 1.3, 6.2, .4), .4, (brass, rust, teal)[i])
lamp("SUN", (1, .6, .28), 5, (-28, -14, 14), (0, 0, 1.5)); lamp("SUN", (.3, .5, 1), 2.4, (22, 26, 18), (0, 0, 1.5))
w = bpy.data.worlds.new("dark"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .025, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((8, -62, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
