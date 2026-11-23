import bpy, bmesh, random, math
from mathutils import Vector
random.seed(869)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
mud, wet, granite, granite2 = pigment((.08, .07, .05)), pigment((.03, .04, .04), rough=.2), pigment((.2, .2, .22)), pigment((.14, .15, .17))
moss1, moss2, moss3, fern = pigment((.08, .22, .07)), pigment((.14, .3, .08)), pigment((.2, .34, .1)), pigment((.05, .2, .08))
fungus, mushroom, cap, crystal = pigment((.2, .8, .5), 6), pigment((.5, .5, .5)), pigment((.1, .9, .6), 10), pigment((.3, .9, .8), 14)
def shape(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def crag(r, m, loc, sq, sub=1, jit=.18):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * random.uniform(1 - jit, 1 + jit), v.co.y * random.uniform(1 - jit, 1 + jit), v.co.z * random.uniform(1 - jit, 1 + jit)))
    return shape(bm, m, loc, (0, 0, random.uniform(0, 6)))
def tuft(r, m, loc, h=.6):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= h; v.co += Vector((random.uniform(-.1, .1), random.uniform(-.1, .1), random.uniform(-.1, .1)))
    return shape(bm, m, loc)
def spire(m, loc, r, h, n=5):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=0, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, loc)
def beam(m, a, b, r):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r * .8, depth=d.length)
    return shape(bm, m, (a + b) / 2, d.to_track_quat('Z', 'Y').to_euler())
def glimmer(c, w, loc):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = loc; sc.collection.objects.link(o)
# forest floor base with a pool of rainwater in front
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=4, radius2=9, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
shape(bm, mud)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=3.6, radius2=3.6, depth=.12)
for v in bm.verts: v.co.x *= 1.3; v.co += Vector((random.uniform(-.3, .3), random.uniform(-.3, .3), 0))
shape(bm, wet, (1.5, -5.2, .05))
# the boulder: stacked crags, a flat-ish crown, a notch on the front
crag(4.6, granite, (0, 0, 0), 1, 2, .22)
crag(3.4, granite2, (-.6, 0, 4.3), 1, 2, .15)
crag(2.4, granite, (1.2, .3, 7.2), 1, 1, .12)
crag(2.6, granite2, (-3.6, -1.5, 2.2), 1, 1, .2)
crag(2.2, granite, (3.4, 1.8, 2.6), 1, 1, .2)
# moss: tufts clustered on every up-facing ledge and the crown
for i in range(46):
    a, r = random.uniform(0, 6.28), random.uniform(0, 4.6)
    h = 9.6 * (1 - (r / 5.2) ** 2) ** .5 + random.uniform(-.4, .4)
    if h < .6: continue
    tuft(random.uniform(.5, 1.0), (moss1, moss2, moss3)[i % 3], (r * math.cos(a), r * math.sin(a), h), .6)
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(0, 3.4)
    tuft(random.uniform(.4, .8), moss3, (r * math.cos(a), r * math.sin(a), 9.5 * (1 - (r / 4.6) ** 2) ** .5 + .1), .6)
# ferns, fungi and a mushroom ring at the foot
for i in range(16):
    a = i * .39 + random.uniform(-.1, .1); r = random.uniform(5.2, 7.6)
    for k in range(4): spire(fern, (r * math.cos(a), r * math.sin(a), .1), .22, 1.2 + k * .1, 4)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(4.8, 6.2)
    spire(fungus, (r * math.cos(a), r * math.sin(a), .05), .13, .5, 5); spire(cap, (r * math.cos(a), r * math.sin(a), .5), .2, .2, 5)
glimmer((.2, .9, .5), 220, (6, -4.5, 1)); glimmer((.2, .9, .5), 220, (-6, -4.5, 1))
# a faint crystal seam in the notch and one big crystal on a ledge
for i in range(5): spire(crystal, (2.0 + i * .35, -3.6 + i * .1, .3 + i * .2), .22, 1.4 + i * .2, 5)
spire(crystal, (-2.4, -2.6, 4.0), .5, 2.4, 5); glimmer((.3, .9, .8), 400, (-2.4, -3.2, 5))
# roots and fallen log, and a few standing trees at the edge for depth
for i in range(4):
    a = i * 1.6 + .4; beam(granite2, (8 * math.cos(a), 8 * math.sin(a), 0), (8 * math.cos(a) * .8, 8 * math.sin(a) * .8, 2.5), .35)
    tuft(moss2, (8 * math.cos(a) * .8, 8 * math.sin(a) * .8, 2.6), 1.0, .5)
for col, w, p in (((.5, .9, .8), 4.5, (-24, -14, 11)), ((.4, .6, 1), 2.2, (22, 20, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .02, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((12, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
