import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1533)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
V = {}
def alloy(name, rgb, glow=0, rough=.5, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough; p.inputs["Metallic"].default_value = metal
    if glow: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    V[name] = m
for k, c in dict(hull=(.42, .43, .48), hull2=(.22, .24, .3), deck=(.3, .3, .34), white=(.6, .6, .62), dark=(.05, .05, .07), sail=(.5, .08, .06), sail2=(.7, .65, .5),
                 blimp=(.7, .12, .1), mast=(.5, .5, .55), cloud=(.5, .35, .06), cloud2=(.4, .26, .05), port=(.1, .3, .6)).items(): alloy(k, c)
alloy("window", (1, .7, .3), glow=7); alloy("solar", (.04, .08, .3), rough=.2, metal=.6); alloy("beacon", (1, .1, .05), glow=14); alloy("rim", (.8, .55, .15), glow=1)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("v"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("v", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(V[m]); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def rod(a, b, r, m, n=6):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return mk(bm, m)
def dome(r, m, at, sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.01], context='VERTS')
    return mk(bm, m, at)
def ring(n, r, z, m, h=.15):
    for i in range(n):
        a, b = i * 6.2832 / n, (i + 1) * 6.2832 / n
        rod((math.cos(a) * r, math.sin(a) * r, z), (math.cos(b) * r, math.sin(b) * r, z), .12, m)
        if i % 2 == 0: rod((math.cos(a) * r, math.sin(a) * r, z), (math.cos(a) * r, math.sin(a) * r, z + h), .06, m)
def beacon(at, col, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# the deck: a floating disc of cloud-metal with a glowing rim and a ragged underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=6, radius2=13, depth=2.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.8, .3)))
    v.co.z -= 1.1
mk(bm, "deck"); ring(12, 12.8, 0, "rim", .1)
# the habitat dome: layered shells, glowing window bands, an airlock and a hatch ring
dome(5.2, "hull", (0, 0, 0), 2); dome(4.6, "hull2", (0, 0, 0), 2)
for z, r in ((1.2, 4.9), (2.4, 4.2), (3.5, 3.1)):
    ring(12, r * 1.0, z, "window", .35)
dome(1.0, "hull2", (0, 0, 4.8), 1)
for k in range(4):
    a = k * 1.57 + .8; cube((math.cos(a) * 4.9, math.sin(a) * 4.9, 0), (1.6, .3, 1.4), "window", (0, 0, a + 1.57))
beacon((0, 0, 2.2), (1, .65, .25), 900)
# catwalk circling the dome: planked ring, posts, handrail, bridge to the mast
for i in range(24):
    a, b = i * .2618, (i + 1) * .2618
    rod((math.cos(a) * 7.0, math.sin(a) * 7.0, .15), (math.cos(b) * 7.0, math.sin(b) * 7.0, .15), .2, "white")
    if i % 3 == 0: rod((math.cos(a) * 7.0, math.sin(a) * 7.0, 0), (math.cos(a) * 7.0, math.sin(a) * 7.0, 1.1), .05, "mast")
ring(24, 7.0, 1.1, "mast", .08)
rod((7.0, 0, .15), (11.5, 0, .15), .12, "mast"); rod((7.0, 0, 1.1), (11.5, 0, 1.1), .05, "mast")
# docking mast: lattice tower with a docking collar, beacon and a gantry
rod((11.5, 0, 0), (11.5, 0, 10.5), .22, "mast", 6)
for z in (3, 6, 9): rod((11.5, 0, z), (11.5, 0, z + 1.2), .35, "hull2", 6)
rod((11.5, 0, 10.5), (11.5, 0, 11.2), .55, "white", 8); dome(.5, "beacon", (11.5, 0, 11.4), 1)
beacon((11.5, 0, 11.6), (1, .1, .05), 500)
rod((11.5, 0, 7.5), (9.5, 0, 7.5), .1, "mast")
# solar sails: two booms with a grid of red-and-cream panels
for s in (-1, 1):
    rod((-1, 0, 1.0), (s * 11, 0, 1.0), .12, "mast")
    for i in range(5):
        x = s * (2.5 + i * 1.8)
        cube((x, 0, 1.0), (1.6, 3.6, .06), "sail" if i % 2 else "sail2")
# the blimp: an airship tied to the catwalk by a rope, with gondola and fins
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1)
for v in bm.verts: v.co = Vector((v.co.x * 3.2, v.co.y * 1.5, v.co.z * 1.5))
mk(bm, "blimp", (-6.5, -6.5, 6.0), (0, 0, .6))
cube((-8.4, -7.7, 5.4), (1.0, .8, .8), "white", (0, 0, .6)); cube((-8.4, -7.7, 5.4), (1.2, .5, .3), "window", (0, 0, .6))
rod((-6.5, -6.5, 6.0), (-3.2, -3.2, 1.2), .05, "mast")
beacon((-8.4, -7.7, 5.2), (1, .7, .3), 200)
# clouds drifting under and beside the deck
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(7, 13)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.8, 1.6))
    for v in bm.verts: v.co.z *= .5
    mk(bm, "cloud" if i % 2 else "cloud2", (math.cos(a) * r, math.sin(a) * r, random.uniform(-2.2, -1.2)))
# sulphur-yellow light: low amber key from the left, a greenish rim from behind
for col, w, at in (((1, .75, .3), 6, (-26, -14, 12)), ((.5, .8, .6), 2.4, (24, 22, 10))):
    s = bpy.data.lights.new("s", "SUN"); s.color = col; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("venus"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.07, .045, .012, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 0, 4.5)); co.location = tg + Vector((8, -58, 36))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
