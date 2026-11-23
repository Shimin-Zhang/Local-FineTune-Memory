import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1125)
sc = bpy.context.scene
mats = {}
def tone(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    mats[name] = m
for n, c, g in [("soil", (.07, .05, .04), 0), ("paving", (.22, .22, .24), 0), ("trunk", (.14, .09, .06), 0), ("pine", (.04, .13, .09), 0),
        ("pine2", (.06, .17, .11), 0), ("frame", (.55, .08, .06), 0), ("chrome", (.7, .72, .75), 0), ("tyre", (.03, .03, .03), 0),
        ("skin", (.5, .55, .6), 0), ("skin2", (.35, .4, .45), 0), ("jeans", (.1, .15, .4), 0), ("shirt", (.5, .3, .1), 0),
        ("hair", (.3, .15, .05), 0), ("basket", (.45, .3, .12), 0), ("moon", (.9, .92, 1), 1.2), ("crater", (.55, .6, .75), .4),
        ("lamp", (1, .85, .5), 20), ("tail", (1, .1, .05), 12), ("star", (1, 1, 1), 10)]:
    tone(n, c, g)
def put(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def cube(p, s, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, m, p, (0, 0, rz))
def tube(p, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, p, rot)
def ball(p, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return put(bm, m, p)
def bar(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return put(bm, m)
def shine(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floating slab: rough tapered underside, grass and a strip of road
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co.x *= .55; v.co.y *= .55; v.co.z -= random.uniform(0, .8); v.co.x += random.uniform(-.1, .1)
    v.co = Vector((v.co.x * 28, v.co.y * 22, v.co.z * 3 - 1.5))
put(bm, "soil")
cube((0, -6.5, 0), (26, 3.4, .1), "paving"); cube((0, -6.5, .1), (26, .12, .05), "chrome")
for i in range(14): cube((-12 + i * 1.85, -6.5, .1), (.9, .12, .05), "lamp")
# the full moon, huge, low behind the trees, with craters
ball((-2, 9.5, 8), 6.5, "moon")
for x, y, z, r in [(-4, 9, 9.5, 1.2), (-.5, 9