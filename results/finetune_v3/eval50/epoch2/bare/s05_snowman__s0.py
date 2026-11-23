import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1148)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
S = {}
def tint(k, c, e=0):
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = .9
    if e: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    S[k] = m
tint("snow", (.5, .58, .72)); tint("snow2", (.4, .48, .64)); tint("coal", (.03, .03, .04)); tint("felt", (.04, .04, .05)); tint("band", (.5, .06, .08))
tint("carrot", (.95, .35, .03)); tint("stick", (.25, .15, .08)); tint("stone", (.22, .22, .27)); tint("frost", (.12, .2, .3)); tint("lamp", (1, .65, .25), 16)
tint("mug", (.1, .3, .5)); tint("coalglow", (1, .4, .1), 10)
def spawn(bm, k, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(S[k]); return o
def ball(p, r, k, sq=1, j=0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= sq; v.co += Vector((random.uniform(-j, j), random.uniform(-j, j), random.uniform(-j, j)))
    return spawn(bm, k, p)
def cone(p, r, h, n, k, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return spawn(bm, k, p, rot)
def rod(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return spawn(bm, k)
def glimmer(p, c, w):
    l = bpy.data.lights.new("l", "POINT"); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
# snowy base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=10, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.4, .2)))
    else: v.co.z += random.uniform(-.12, .12)
    v.co.z -= 1.6
spawn(bm, "frost")
# the snowman: three lumps, carrot nose, coal face, hat
ball((0, 0, 1.7), 2.0, "snow", .95, .04); ball((0, 0, 4.5), 1.5, "snow", 1, .03); ball((0, 0, 6.9), 1.0, "snow", 1, .02)
cone((0, -1.7, 4.5), .28, 1.8, 6, "carrot", .04, (math.pi / 2, 0, 0))
for sx in (-1, 1):
    ball((sx * .5, -1.3, 5.1), .17, "coal", 1, 0); ball((sx * .5, -1.3, 4.0), .12, "coal"); ball((sx * .7, -1.15, 3.6), .1, "coal"); ball((sx * .4, -1.4, 3.5), .1, "coal")
cone((0, 0, 7.6), 1.05, .18, 8, "band", 1.05); cone((0, 0, 7.75), .62, 1.5, 8, "felt", .58); cone((0, 0, 9.2), .6, .12, 8, "felt", .56)
# stick arms with twig fingers, scarf, buttons
rod((-1.8, 0, 2.6), (-4.2, 0, 4.0), .12, "stick"); rod((-4.2, 0, 4.0), (-5.2, 0, 5.4), .09, "stick"); rod((-4.2, 0, 4.0), (-4.4, 0, 5.6), .08, "stick")
rod((1.8, 0, 2.6), (4.2, 0, 3.8), .12, "stick"); rod((4.2, 0, 3.8), (5.0, 0, 5.2), .09, "stick"); rod((4.2, 0, 3.8), (4.5, 0, 2.2), .08, "stick")
for i in range(3): ball((0, -1.85, 3.0 - i * .15), .38 - i * .05, "band", .5)
ball((.9, -1.5, 2.9), .3, "band", .4); rod((.9, -1.5, 2.9), (1.2, -1.5, 1.2), .12, "band")
# snow drifts, boulders, fir trees, fence, lantern, footprints
for x, y, r in ((-6, 3, 1.8), (6, 4, 2.0), (7, -3, 1.5), (-7, -4, 1.6), (3, 7, 1.4), (-3, 7.5, 1.2)): ball((x, y, 0), r, "snow2", .5, .15)
for x, y in ((-5, -6), (6.5, -6), (0, -7.5), (8, 1)): ball((x, y, .3), random.uniform(.5, .9), "stone", .7, .1)
for x, y, h in ((-7, 5, 4.5), (7.5, 6, 5.2), (-8, -1, 3.6), (8.5, -2, 4.0)):
    for k in range(3): cone((x, y, .3 + k * h * .22), 1.5 - k * .4, h * .38, 7, "frost", .1)
    ball((x, y, h * .95), .6, "snow", .8, .05)
for i in range(6): rod((-5 + i * 1.0, -7.2, 0), (-5 + i * 1.0, -7.2, 1.0), .14, "stick")
rod((-5, -7.2, .8), (.5, -7.2, .8), .1, "stick"); rod((-5, -7.2, .4), (.5, -7.2, .4), .1, "stick")
rod((3.2, -3.8, 0), (3.2, -3.8, 2.4), .14, "stick"); cone((3.2, -3.8, 2.4), .5, .8, 6, "lamp", .4); glimmer((3.2, -4.3, 2.8), (1, .65, .25), 500)
for i in range(5): ball((-1.5 + i * .9, -4.5 - i * .6, .05), .35, "coal", .25)
# cold moonlit night: silver-blue key from the left, rose rim from behind
for c, e, p in (((.55, .65, 1), 5, (-26, -14, 12)), ((1, .5, .6), 2.2, (22, 24, 10))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = e
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 3)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 0, 4.5)); co.location = tg + Vector((6, -46, 26))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
