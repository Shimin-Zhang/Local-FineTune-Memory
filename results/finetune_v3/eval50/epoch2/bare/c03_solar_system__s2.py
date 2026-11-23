import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1085)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(r, g, b, glow=0):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .85
    if glow: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = glow
    return m
rock, orbit, sun, mercury, venus, earth, mars = hue(.06, .06, .09), hue(.2, .22, .35), hue(1, .6, .1, 14), hue(.45, .42, .4), hue(.75, .55, .2), hue(.1, .3, .7), hue(.65, .22, .1)
moon, ring, star = hue(.6, .6, .65), hue(.55, .4, .25), hue(.9, .9, .95, 1)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def orb(r, m, at, sq=(1, 1, 1), n=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=n, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return make(bm, m, at)
def disc(r0, r1, h, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r0, radius2=r1, depth=h)
    return make(bm, m, at, rot)
def rod(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length))
    return make(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def lite(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# base: a rough dark disc with a tapered underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=7, radius2=16, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.06, .06)
    v.co.z -= 1.5
make(bm, rock)
# the sun at the centre, with a ring of faceted flame spikes
orb(2.6, sun, (0, 0, 0), n=2)
for k in range(8):
    a = k * math.pi / 4
    disc(.45, .05, 1.5, sun, (math.cos(a) * 2.7, math.sin(a) * 2.7, .3), (math.sin(a) * 1.2, -math.cos(a) * 1.2, 0))
lite((1, .6, .15), 4500, (0, 0, 1.5))
# four orbits: Mercury, Venus, Earth, Mars, each with its own colour and a moon or ring
for r, m, pr, a0, extra in ((5, mercury, .5, .5, None), (7.4, venus, .6, 2.2, None), (10, earth, .9, 4.2, moon), (12.8, mars, .65, 1.1, ring)):
    pts = [Vector((math.cos(i * math.pi / 12) * r, math.sin(i * math.pi / 12) * r, .06)) for i in range(25)]
    for p, q in zip(pts, pts[1:] + pts[:1]): rod(p, q, .09, orbit)
    px, py = math.cos(a0) * r, math.sin(a0) * r
    orb(pr, m, (px, py, 0), n=2)
    if extra is moon:
        orb(.28, extra, (px + pr * 1.8, py - pr * .9, .3))
    elif extra is ring:
        disc(pr * 2.1, pr * 2.1, .1, extra, (px, py, 0), (math.pi / 2 * .9, 0, .5))
# scattered stars and a few small rocks on the base
for i in range(26):
    a, r = random.uniform(0, 6.28), random.uniform(2.5, 15)
    if i % 3: orb(random.uniform(.1, .22), star, (math.cos(a) * r, math.sin(a) * r, random.uniform(.1, .3)))
for i in range(10):
    a, r = random.uniform(0, 6.28), random.uniform(3.5, 14.5)
    orb(random.uniform(.3, .6), rock, (math.cos(a) * r, math.sin(a) * r, .1), (1, 1, .6))
# lighting: cold blue rim from behind, faint warm fill from the front left, deep space background
for c, w, at in (((.4, .55, 1), 3.5, (-26, -14, 11)), ((1, .6, .3), 1.2, (22, 24, 14))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 0)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .01, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 0)); co.location = t + Vector((14, -62, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
