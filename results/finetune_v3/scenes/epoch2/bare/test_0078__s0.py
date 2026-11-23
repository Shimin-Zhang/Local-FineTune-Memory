import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1510)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
paints = {}
def alloy(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .5
    if glow:
        n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    paints[name] = m
for k, v in dict(hull=(.1, .12, .15), deck=(.07, .08, .1), stripe=(.3, .32, .36), white=(.6, .62, .65), red=(.5, .06, .05),
                 black=(.02, .02, .03), hose=(.7, .25, .05), green=(.05, .3, .12), skin=(.55, .35, .25), suit=(.05, .08, .2)).items(): alloy(k, v)
alloy("cyan", (.1, .9, 1), 14); alloy("amber", (1, .6, .1), 14); alloy("jet", (1, .5, .1), 20)
def form(bm, key, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(key); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(key, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(paints[key]); return o
def slab(key, at, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return form(bm, key, at, rot)
def tube(key, at, r, h, n=6, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return form(bm, key, at, rot)
def strut(key, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return form(bm, key)
def beam(kind, c, w, at, aim=None):
    l = bpy.data.lights.new(kind, kind); l.color = c; l.energy = w
    o = bpy.data.objects.new(kind, l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
def fighter(at, yaw, hull, glow):
    # fuselage, nose, canopy, tail fin, winglets, engine ring, thruster
    tube(hull, at, .5, 4.2, 6, .35, (0, math.pi / 2, yaw))
    tube(glow, (at[0] + 2.2 * math.cos(yaw), at[1] + 2.2 * math.sin(yaw), at[2]), .35, .3, 6, .05, (0, math.pi / 2, yaw))
    tube("cyan", (at[0] - 2.2 * math.cos(yaw), at[1] - 2.2 * math.sin(yaw), at[2]), .3, .5, 6, .5, (0, -math.pi / 2, yaw))
    slab("black", (at[0] - .3 * math.cos(yaw), at[1] - .3 * math.sin(yaw), at[2] + .35), (.9, .5, .35), (0, 0, yaw))
    slab(hull, (at[0] - 1.2 * math.cos(yaw), at[1] - 1.2 * math.sin(yaw), at[2] + .3), (.5, 1.6, .12), (0, 0, yaw))
    slab(hull, (at[0] - 1.9 * math.cos(yaw), at[1] - 1.9 * math.sin(yaw), at[2] + .1), (.3, .1, 1.0), (0, 0, yaw))
    # cradle: two fork legs, a base plate and a glowing status strip
    for sx in (-1.2, 1.2):
        x, y = at[0] + sx * math.cos(yaw), at[1] + sx * math.sin(yaw)
        slab("stripe", (x, y, 0), (.25, 1.2, .5), (0, 0, yaw)); slab("stripe", (x, y, .5), (.25, .9, .15), (0, 0, yaw))
    slab("black", at, (3.2, 2.2, .12), (0, 0, yaw)); slab(glow, (at[0], at[1] - 1.0, .12), (2.4, .1, .06), (0, 0, yaw))
# hangar floor slab, rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 26, v.co.y * 19, v.co.z * 3 - 1.5))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.5)))
form(bm, "deck", (0, 0, 0))
for i in range(11): slab("stripe", (-12 + i * 2.4, 0, .02), (.2, 17, .03))
for i in range(6): slab("red" if i % 2 else "black", (-9 + i * 3.6, -8.6, .02), (1.2, .5, .04))
# back wall with bay door frame, left wall with ribs, open front
slab("hull", (0, 9.2, 0), (25, .8, 8)); slab("hull", (-12.6, 0, 0), (.8, 18, 8))
for i in range(9): slab("stripe", (-11.5 + i * 2.9, 9.2, 0), (.3, .6, 8)); slab("stripe", (-12.6, -8 + i * 2.0, 0), (.6, .3, 8))
for i in range(5): slab("hull", (-10 + i * 5, 9.2, 8), (5, .8, .5))
slab("cyan", (0, 8.75, 7.2), (22, .1, .25)); slab("amber", (0, 8.75, .5), (22, .1, .25))
# launch rail: two beams, cross ties, glowing strip, end gantry
for sy in (-.9, .9): slab("stripe", (3, sy, 0), (18, .3, .5)); slab("cyan", (3, sy, .5), (17.5, .1, .06))
for i in range(18): slab("black", (-5.5 + i * 1.0, 0, 0), (.3, 2.2, .3))
for sx in (-6, 12): slab("stripe", (sx, 0, 0), (.6, 2.6, 3.0)); slab("amber", (sx, 0, 3.0), (.8, 2.8, .3))
beam("POINT", (.1, .9, 1), 700, (3, 0, 1.5)); beam("POINT", (1, .6, .1), 400, (-6, 0, 3.5))
# two fighters on cradles
fighter((-4.5, 3.8, .95), 0, "white", "cyan"); fighter((-4.5, -3.8, .95), 0, "red", "amber")
# fuel hoses from a manifold on the left wall, coiled and hanging
slab("hull", (-11.5, -6, 1.5), (1.2, 3, 2.5)); slab("amber", (-10.8, -6, 2.5), (.1, 1.4, .5))
for k, y in enumerate((-6.8, -5.2)):
    for i in range(8):
        a = i * .8; slab("hose", (-10.8 + 1.6 * math.cos(a * .5) * (i > 3), y + 1.2 * math.sin(a * .5), 1.6 + 1.0 * math.cos(a * .5) * (i > 3) - i * .08), (.22, .22, .25))
    slab("black", (-9.0, y, .1), (.3, .3, .3))
# deck officer with two glowing wands
ox, oy = 8.5, 5.0
tube("suit", (ox, oy, 0), .5, 1.6, 6, .35); tube("skin", (ox, oy, 1.6), .3, .45, 6, .25); tube("stripe", (ox, oy, 1.95), .32, .12, 6)
slab("suit", (ox - .3, oy - .5, 1.0), (.2, .2, .8), (.7, 0, 0)); slab("suit", (ox + .3, oy - .5, 1.0), (.2, .2, .8), (.7, 0, 0))
strut("cyan", (ox - .3, oy - .9, 1.4), (ox - .6, oy - 1.5, 2.2), .08); strut("amber", (ox + .3, oy - .9, 1.4), (ox + .6, oy - 1.5, 2.4), .08)
slab("cyan", (ox - .65, oy - 1.55, 2.2), (.2, .2, .2)); slab("amber", (ox + .55, oy - 1.55, 2.4), (.2, .2, .2))
beam("POINT", (.1, .9, 1), 300, (ox - .6, oy - 1.5, 2.4)); beam("POINT", (1, .6, .1), 300, (ox + .6, oy - 1.5, 2.6))
# crates and a barrel stack, a small ladder
for i, (x, y) in enumerate(((10, -6), (11.5, -6.5), (10.5, -4.5))): slab("green" if i else "hull", (x, y, 0), (1.5, 1.5, 1.2 + .3 * i), (0, 0, i))
for i in range(3): tube("red" if i == 1 else "hull", (6 + i * .9, -7, 0), .45, 1.2, 7)
beam("SUN", (.4, .8, 1), 4.5, (22, -22, 10), (0, 0, 2)); beam("SUN", (1, .3, .5), 2, (-20, 20, 12), (0, 0, 2))
w = bpy.data.worlds.new("hangar"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((16, -56, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
