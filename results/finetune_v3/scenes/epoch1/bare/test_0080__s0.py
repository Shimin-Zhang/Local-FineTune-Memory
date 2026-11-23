import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1438)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def alloy(name, rgb, glow=0, metal=0, rough=.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    M[name] = m
for k, v in dict(dust=(.22, .2, .24), rock=(.16, .15, .19), rock2=(.1, .1, .14), ore=(.1, .35, .4), hull=(.5, .5, .55), hull2=(.3, .32, .38), plate=(.4, .22, .1), dark=(.05, .05, .07),
                 strut=(.12, .12, .14), pod=(.6, .55, .45), cable=(.55, .45, .1), tyre=(.03, .03, .04)).items(): alloy(k, v)
alloy("ore", (.2, .85, .9), 4, .4, .4); alloy("window", (1, .75, .35), 12); alloy("lamp", (1, .9, .6), 20); alloy("beacon", (1, .1, .1), 20); alloy("screen", (.3, .9, 1), 8)
def mesh(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free(); me.materials.append(M[k])
    o = bpy.data.objects.new("a", me); o.location = at; o.rotation_euler = rot; sc.collection.objects.link(o); return o
def slab(x, y, z, w, d, h, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mesh(bm, k, (x, y, z), (0, 0, rz))
def pipe(x, y, z, r, h, n, k, rot=(0, 0, 0), r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, k, (x, y, z), rot)
def strut(a, b, t, k):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return mesh(bm, k)
def boulder(x, y, z, r, k, sq=(1, 1, .8)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.8, 1.2)
    return mesh(bm, k, (x, y, z))
def glow(c, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# asteroid surface: a rough slab of grey rock with a bumpy top
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=12.5, depth=3.6)
for v in bm.verts:
    v.co.z -= 1.8
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.6, .3)))
    else: v.co.z += random.uniform(-.15, .15)
mesh(bm, "dust")
for i in range(14): boulder(random.uniform(-10, 10), random.uniform(-10, 10), .1, random.uniform(.5, 1.2), random.choice(("rock", "rock2")))
# the rock outcrop at the back with a vein of ore
boulder(0, 8.5, 1.5, 5.5, "rock2", (1.2, 1, 1.1)); boulder(-3.5, 6.5, .8, 3, "rock", (1.2, 1, .9)); boulder(4, 6.5, .8, 3, "rock", (1.2, 1, .9))
for p in ((-.5, 5.6, 3.2), (1.2, 5.4, 2.0), (-1.8, 5.9, 1.5), (.4, 5.2, 4.4)): boulder(p[0], p[1], p[2], .5, "ore")
# the drill rig: legs, a boom, a head and a spinning drill bit
for sx in (-1, 1):
    for sy in (-1, 1): strut((3.0 + sx * 1.6, 3.6 + sy * 1.2, 0), (3.0 + sx * .8, 3.6 + sy * .6, 2.2), .22, "strut")
slab(3.0, 3.6, 2.2, 2.4, 2.0, 1.0, "plate"); slab(3.0, 3.6, 3.2, 1.4, 1.2, .5, "hull2"); slab(3.0, 2.9, 2.5, .8, .1, .4, "screen")
strut((3.0, 3.6, 3.6), (1.8, 6.0, 4.6), .5, "hull"); strut((3.0, 3.6, 3.2), (2.0, 5.8, 4.0), .3, "strut")
slab(1.8, 6.0, 3.9, 1.4, 1.4, 1.2, "hull"); pipe(1.8, 6.0, 4.0, .45, 1.4, 8, "hull2", (math.pi / 2, 0, 0))
pipe(1.8, 6.8, 4.0, .38, 2.2, 8, "ore", (math.pi / 2, 0, 0), .05); pipe(1.8, 6.8, 4.0, .5, .3, 8, "plate", (math.pi / 2, 0, 0))
for i in range(4): pipe(1.8 + math.cos(i * 1.57) * .45, 6.8 + math.sin(i * 1.57) * .45, 4.0, .1, .8, 5, "hull2", (math.pi / 2, 0, 0))
glow((.3, .9, 1), 500, (1.8, 6.2, 4.8)); slab(3.0, 2.9, 3.0, .5, .1, .1, "lamp")
# ore hopper: a funnel above a bin with a conveyor to the pod
for sx in (-1, 1):
    for sy in (-1, 1): strut((-5.5 + sx * 1.2, -1.0 + sy * 1.0, 0), (-5.5 + sx * .6, -1.0 + sy * .5, 3.0), .2, "strut")
pipe(-5.5, -1.0, 2.4, 1.5, 1.6, 8, "hull", (0, 0, 0), .6); pipe(-5.5, -1.0, 2.3, 1.55, .15, 8, "plate")
for i in range(7): boulder(-5.5 + random.uniform(-.4, .4), -1.0 + random.uniform(-.4, .4), 2.2 + random.uniform(0, .4), .35, "ore")
slab(-5.5, -1.0, 0, 2.2, 2.0, 1.4, "hull2"); slab(-5.5, -2.05, .8, 1.2, .1, .5, "ore")
strut((-4.2, -1.0, 1.2), (-.5, 2.0, 1.4), .5, "plate"); strut((-4.2, -1.0, 1.4), (-.5, 2.0, 1.6), .1, "dark")
for i in range(4): pipe(-4.0 + i * 1.1, -.2 + i * .75, .8, .25, .1, 7, "tyre", (0, math.pi / 2, 0))
# tethered cargo pod: a drum with a hatch, fins, a lamp, and a cable to the dome
pipe(-1.5, -4.0, 2.0, 1.5, 3.0, 8, "pod", (0, math.pi / 2, 0)); pipe(-1.5, -4.0, 2.0, 1.6, .3, 8, "plate", (0, math.pi / 2, 0), 1.6)
slab(-1.5, -5.6, 1.4, 1.0, .2, 1.0, "hull2"); slab(-1.5, -5.6, 1.9, .6, .2, .3, "lamp")
for a in (0, 2.1, 4.2):
    c, s = math.cos(a), math.sin(a)
    strut((-1.5, -4.0 + c * 1.5, 2.0 + s * 1.5), (-1.5, -4.0 + c * 2.4, 2.0 + s * 2.4), .15, "hull2"); slab(-1.5, -4.0 + c * 2.0, 2.0 + s * 2.0, .1, .8, .1, "plate")
strut((-1.5, -2.5, 2.0), (-4.5, -7.0, 3.5), .08, "cable")
# crew dome: a cramped glass dome with an interior glow, a door, a mast and a beacon
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=2.6)
for v in bm.verts: v.co.z = max(v.co.z, -.2) * .8
mesh(bm, "window", (-4.5, -7.0, .2))
pipe(-4.5, -7.0, 0, 2.7, .5, 9, "hull2"); slab(-4.5, -9.5, 0, 1.4, .3, 1.8, "hull"); slab(-4.5, -9.7, 1.0, .8, .1, .5, "lamp")
strut((-4.5, -7.0, 2.0), (-4.5, -7.0, 4.8), .12, "strut"); pipe(-4.5, -7.0, 4.8, .25, .3, 6, "beacon")
glow((1, .75, .35), 900, (-4.5, -7.0, 1.4)); glow((1, .9, .6), 250, (-1.5, -6.0, 2.0)); glow((1, .1, .1), 150, (-4.5, -7.0, 5.2))
for c, w, p in (((.6, .75, 1), 4, (-26, -14, 9)), ((.9, .4, .5), 1.8, (22, 20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((-1, 0, 1.5)); co.location = t + Vector((16, -56, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
