import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1516)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
camp = {}
def dye(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    camp[name] = m
for k, v in dict(sand=(.3, .2, .12), dune=(.22, .14, .08), canvas=(.45, .38, .26), canvas2=(.2, .25, .3), wood=(.25, .15, .08),
                 tube=(.5, .52, .55), dark=(.04, .04, .06), cloth=(.12, .1, .1), star=(.9, .95, 1), core=(.55, .65, 1),
                 red=(.9, .04, .03), rock=(.16, .1, .07)).items(): dye(k, v)
dye("lamp", (1, .06, .03), 20); dye("tentlight", (1, .7, .35), 8)
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(camp[m]); return o
def slab(at, s, m, rz=0, rx=0, ry=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return add(bm, m, at, (rx, ry, rz))
def pole(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def ball(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return add(bm, m, at)
def tent(at, w, d, h, m, rz):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1, radius2=.12, depth=h)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, v.co.z + h / 2))
    o = add(bm, m, at, (0, 0, rz + math.pi / 4)); slab((at[0] * .0 + math.sin(rz + .785) * d * .5, math.cos(rz + .785) * d * .5, at[2] + .1), (1.0, .9, h * .6), "tentlight", rz + .785, top=.5); return o
def glow(c, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# desert base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=13.5, depth=3.4)
for v in bm.verts:
    v.co.z -= 1.7
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
add(bm, "sand")
for x, y, r in ((-8, 5, 3.2), (8, 7, 3.6), (-9, -6, 2.6), (10, -3, 2.8), (0, 10.5, 3)):
    ball((x, y, 0), r, "dune", (1.4, 1, .22))
# three tents with glowing doorways
for at, w, d, h, m, rz in (((-3, 1, 0), 2.6, 2.4, 2.4, "canvas", .3), ((1.5, 3.5, 0), 2.2, 2.0, 2.1, "canvas2", 2.5), ((-7, -2, 0), 2.0, 1.9, 1.9, "canvas", 5.0)):
    tent(at, w, d, h, m, rz); glow((1, .65, .3), 120, (at[0] + math.sin(rz + .785) * d * .7, at[1] + math.cos(rz + .785) * d * .7, 1.0))
# three telescopes on tripods, different sizes, pointed at the sky
for x, y, h, tilt in ((-4, -7, 2.6, .5), (1, -8.5, 3.4, -.4), (6, -6, 2.2, .8)):
    for a in (0, 2.1, 4.2):
        c, s = math.cos(a), math.sin(a); pole((x + c * 1.1, y + s * 1.1, 0), .08, h * .8, 5, "wood", rot=(s * .3, -c * .3, 0))
    ball((x, y, h * .8), .35, "dark"); pole((x, y, h * .8), .1, .8, 5, "dark")
    pole((x, y, h * .9), .5, 2.2, 8, "tube", .38, rot=(tilt, 0, 0)); pole((x, y, h * .9), .52, .3, 8, "dark", .5, rot=(tilt, 0, 0))
    pole((x + math.sin(tilt) * 1.1, y, h * .9 + math.cos(tilt) * 1.1), .2, .5, 6, "dark", rot=(tilt, 0, 0))
# red warning lamp on a tall mast
pole((9.5, 3, 0), .1, 5.5, 5, "tube"); pole((9.5, 3, 5.5), .45, .6, 8, "lamp", .45); glow((1, .05, .03), 1400, (9.5, 3, 6.0))
# folding chairs, a table and a generator
for x, y, rz in ((-1.5, -4, .4), (.5, -4.3, -.3), (-.5, -2.5, 2.0)):
    for sx in (-.4, .4):
        slab((x + sx * math.cos(rz), y + sx * math.sin(rz), 0), (.08, .08, .7), "cloth", rz)
    slab((x, y, .7), (1.0, .9, .1), "cloth", rz); slab((x - math.sin(rz) * .45, y + math.cos(rz) * .45, .7), (.1, .9, .7), "cloth", rz)
slab((0, -3.3, 0), (1.8, 1.0, .8), "wood"); slab((0, -3.3, .8), (2.0, 1.2, .1), "canvas")
slab((-9.5, -6, 0), (1.6, 1.0, .9), "dark"); slab((-9.5, -6, .9), (1.7, 1.1, .1), "canvas2"); pole((-9.5, -6, 1.0), .1, .8, 5, "tube")
for x, y in ((-2, 7), (5, 6), (3, -1), (-5, 4), (8, -8), (-10, 0), (0, 6)): ball((x, y, .1), random.uniform(.3, .6), "rock", (1, 1, .6))
# the Milky Way: a band of stars and a bright core, high above
for i in range(130):
    t = random.uniform(-1.2, 1.2); x, y = random.uniform(-12, 12), random.uniform(-8, 8)
    ball((x, y, 12 + t * 3 + random.uniform(0, 2)), random.uniform(.08, .16), "star")
ball((0, 0, 15), 1.2, "core", (2.6, .6, .5)); ball((-4, 0, 14.2), .8, "core", (1.4, .5, .5)); ball((5, 0, 15.5), .8, "core", (1.4, .5, .5))
for c, w, p in (((.5, .6, 1), 3.5, (-24, -14, 10)), ((.9, .75, .5), 1.2, (20, 24, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.004, .006, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 1, 6)); co.location = tg + Vector((16, -52, 30))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
