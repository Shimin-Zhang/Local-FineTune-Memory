import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(128)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def paint(c, e=0, r=.9):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
slate, marble, frost, frost2, stem, bloom1, bloom2, ember, petal = (paint(c) for c in (
    (.05, .05, .07), (.28, .26, .27), (.5, .58, .66), (.4, .5, .6), (.1, .3, .12), (.8, .2, .35), (.9, .75, .3), (1, .5, .1), (.9, .9, .95)))
frost = frost; core = paint((.3, .8, 1), 6, .2); candle = paint((1, .55, .15), 14, .2); wick = paint((.05, .05, .05))
def solid(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); me.materials.append(m); return o
def ring(r0, r1, z0, z1, n, m, jit=0, loc=(0, 0, 0), rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r0, radius2=r1, depth=z1 - z0)
    for v in bm.verts: v.co.z += (z0 + z1) / 2; v.co += V((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit)))
    return solid(bm, m, loc, rot)
def bar(a, b, t, m):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ V((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return solid(bm, m)
def ball(loc, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return solid(bm, m, loc)
def lite(kind, c, w, loc, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = loc; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# slate slab on a floating rock
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=11, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
solid(bm, slate)
ring(0, 10.2, 0, .3, 8, marble, .15)
# the vase: frosted glass body with a glowing core inside, a thick rim, and a foot
ring(1.4, 1.2, .3, .8, 8, frost2, 0)
ring(1.2, 2.2, .8, 2.6, 8, frost, .06)
ring(2.2, 2.2, 2.6, 5.2, 8, frost, .05)
ring(2.2, 1.5, 5.2, 6.2, 8, frost2, 0)
ring(1.5, 1.7, 6.2, 6.6, 8, frost, 0)
ring(1.2, 1.0, .8, 5.2, 8, core, 0)
lite("POINT", (.3, .8, 1), 600, (0, 0, 3.2))
for k in range(3): ring(1.0 + k * .02, 1.0 + k * .02, 1.2 + k * 1.5, 1.25 + k * 1.5, 8, frost2, 0)
# flowers leaning out of the mouth: stems, leaves, petals
for i in range(7):
    a = i * .9 + .3; h = 3.2 + (i % 3) * .8; lean = .35 + (i % 2) * .2
    top = V((math.cos(a) * lean * h, math.sin(a) * lean * h, 6.4 + h))
    bar((math.cos(a) * .3, math.sin(a) * .3, 5.8), top, .12, stem)
    ball(top, .5 + (i % 2) * .15, bloom1 if i % 3 else bloom2, .8)
    for k in range(5):
        pa = k * 1.26 + i; ball(top + V((math.cos(pa) * .4, math.sin(pa) * .4, .25)), .2, petal, .6)
    bar(top * .85, top * .85 + V((math.cos(a + 1.5) * .8, math.sin(a + 1.5) * .8, -.3)), .08, stem)
# candle and a few petals on the marble
ring(2.2, 2.0, .3, .6, 7, marble, 0, (5.2, -3.5, 0)); ring(1.9, 1.7, .6, 1.9, 7, candle, 0, (5.2, -3.5, 0)); ring(.1, .1, 1.9, 2.3, 4, wick, 0, (5.2, -3.5, 0))
lite("POINT", (1, .55, .15), 250, (5.2, -3.5, 2.8))
for i in range(6): ball((random.uniform(-4, 4), random.uniform(-4, 3), .35), .15, petal, .3)
# cold moonlight key from the left, warm ember rim from behind right
lite("SUN", (.6, .75, 1), 4.5, (-16, -10, 8), (0, 0, 3)); lite("SUN", (1, .5, .25), 2, (14, 14, 6), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = V((0, 0, 4)); co.location = t + V((6, -46, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
