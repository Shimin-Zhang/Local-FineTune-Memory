import bpy, bmesh, math, random
from mathutils import Vector
random.seed(887)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def shade(rgb, em=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
flag, flag2, plaster, plinth, dark, brass, gold = (shade(c) for c in [(.1,.1,.13),(.06,.06,.08),(.62,.62,.6),(.3,.3,.32),(.02,.02,.025),(.5,.35,.12),(.8,.6,.15)])
lampm, eye = shade((1, .65, .2), 14), shade((.03, .03, .04))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, at, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mesh(bm, m, at, rot)
def cyl(m, at, r, h, n=8, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, at, rot)
def ball(m, at, r, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mesh(bm, m, at)
def rod(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mesh(bm, m)
def beam(col, w, at, aim):
    L = bpy.data.lights.new("b", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# plaza base: round flagstone disc, dark rim, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=4, radius2=10, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.7
mesh(bm, flag2)
for k in range(10):
    a = k * math.pi / 5
    slab(flag if k % 2 else flag2, (math.cos(a) * 6.4, math.sin(a) * 6.4, 0), (3.4, 3.4, .1), (0, 0, a + math.pi / 2))
# pedestal: three tiers, cornice, a plaque and a relief line
slab(plinth, (0, 0, 0), (4.6, 4.6, .5)); slab(plaster, (0, 0, .5), (3.6, 3.6, .6)); slab(plaster, (0, 0, 1.1), (2.4, 2.4, 2.6))
slab(plaster, (0, 0, 3.7), (2.8, 2.8, .25)); slab(plinth, (0, -1.22, 1.6), (1.2, .1, .9))
for i in range(3): slab(dark, (-.4 + i * .4, -1.28, 1.75), (.2, .06, .6))
slab(brass, (0, -1.22, .75), (1.6, .08, .3))
# the statue: robed figure from simple shapes, right arm raised
cyl(plaster, (0, 0, 3.95), 1.25, .25, 8, 1.0)
cyl(plaster, (0, 0, 4.2), .75, 2.0, 7, .45)
cyl(plaster, (0, 0, 6.2), .4, .35, 7, .3)
cyl(plaster, (0, 0, 6.55), .5, .7, 6, .38)
ball(plaster, (0, 0, 7.5), .5, 1.15)
cyl(plaster, (0, 0, 7.9), .5, .3, 6, .05)
cyl(dark, (0, -.4, 7.45), .1, .1, 5, rot=(math.pi / 2, 0, 0))
rod(plaster, (.5, 0, 6.1), (1.6, -.2, 7.0), .3); rod(plaster, (1.6, -.2, 7.0), (1.9, -.3, 8.4), .26)
ball(plaster, (1.9, -.3, 8.6), .26)
rod(plaster, (-.5, 0, 6.1), (-1.1, .1, 4.9), .3)
rod(dark, (1.9, -.3, 8.8), (1.9, -.3, 10.2), .08)
ball(gold, (1.9, -.3, 10.4), .3)
# lamp standards with glowing globes
for x, y in [(-5.6, -3.2), (5.6, -3.2), (-5.6, 3.2), (5.6, 3.2)]:
    cyl(dark, (x, y, 0), .12, 2.8, 5, .08); cyl(dark, (x, y, 2.8), .3, .25, 6, .2); ball(lampm, (x, y, 3.25), .38)
# a few benches and a low wall at the back
for x in (-3.2, 3.2): slab(plaster, (x, 5.6, 0), (1.8, .6, .5)); slab(dark, (x, 5.9, .5), (1.8, .12, .6))
for i in range(7): slab(plaster, (-6 + i * 2, 8, 0), (2, .8, .9 + (i % 2) * .2))
# three-point key: hard amber key from the front-left, cool blue rim from behind-right, violet fill
beam((1, .72, .35), 5, (-16, -12, 9), (0, 0, 4)); beam((.3, .5, 1), 2.4, (14, 15, 10), (0, 0, 4)); beam((.6, .35, 1), 1.2, (14, -14, 7), (0, 0, 4))
for x, y, c in [(-5.6, -3.2, (1, .65, .2)), (5.6, -3.2, (1, .65, .2)), (-5.6, 3.2, (1, .65, .2)), (5.6, 3.2, (1, .65, .2))]:
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, 160
    o = bpy.data.objects.new("g", L); o.location = (x, y, 3.2); sc.collection.objects.link(o)
L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = (1, .75, .2), 500
o = bpy.data.objects.new("g", L); o.location = (1.9, -.3, 10.4); sc.collection.objects.link(o)
w = bpy.data.worlds.new("w"); w.use_nodes = True; sc.world = w
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .01, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((9, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
