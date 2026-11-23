import bpy, bmesh, random, math
from mathutils import Vector
random.seed(513)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def stuff(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
moss, dirt, bone, bone2, river, grass, rockm, rune, fern = (stuff(c) for c in [(.12,.2,.07),(.2,.17,.12),(.62,.58,.45),(.45,.42,.32),(.1,.3,.45),(.2,.32,.08),(.2,.2,.22),(.3,.9,1),(.1,.3,.1)])
river = stuff((.15, .5, .7), 1.2, .1); rune = stuff((.2, .9, 1), 9)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return put(bm, m, at, rot)
def limb(a, b, r, m, r2=None):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r, radius2=r if r2 is None else r2, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return put(bm, m)
def boulder(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.8, 1.2), v.co.y * random.uniform(.8, 1.2), v.co.z * sq))
    return put(bm, m, at)
def tuft(at, h, m):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=.25, radius2=.02, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at)
def beam(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("b", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("b", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13, depth=3.2)
for v in bm.verts:
    v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
put(bm, moss)
for i in range(10): boulder((random.uniform(-9, 9), random.uniform(-9, 9), -.2), random.uniform(1.2, 2.4), moss, .3)
# the stream: a winding band of glowing water with stone banks
pts = [Vector((2.5 * math.sin(x * .3) - x * .5, x * .9 - 5, 0)) for x in range(0, 13)]
for a, b in zip(pts, pts[1:]):
    d = b - a; q = d.to_track_quat('Y', 'Z')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * 1.5, v.co.y * d.length * .9, v.co.z * .12)) + (a + b) / 2 + Vector((0, 0, .05))
    put(bm, river)
    for s in (-1, 1):
        c = (a + b) / 2 + q @ Vector((s * .95, 0, 0))
        boulder((c.x, c.y, .1), .35, rockm, .6)
beam("POINT", (.3, .8, 1), 400, (0, 0, 1.2))
# the great skull: cranium, jaw, snout and two curved horns
boulder((-5.5, 4, 1.2), 2.4, bone, .8)
slab((-5.5, 1.6, .5), (2.2, 1.6, .9), bone, (0, 0, 0))
slab((-5.5, .2, .8), (1.4, 1.8, .7), bone, (0, 0, 0))
for s in (-1, 1):
    limb((-5.5 + s * 1.1, 4.5, 2.2), (-5.5 + s * 2.6, 5.2, 3.8), .35, bone2, .08)
    limb((-5.5 + s * .8, 1.8, 1.4), (-5.5 + s * .8, 1.8, 2.0), .22, bone2)
    slab((-5.5 + s * .7, .3, 1.1), (.5, .5, .3), bone2)
for k in range(5): limb((-6.6 + k * .55, 1.55, .6), (-6.6 + k * .55, 1.55, 1.1), .1, bone2)
# ribs: pairs of curved arches standing along the valley, with a spine of vertebrae
for i in range(7):
    x = -8.5 + i * 2.7; y = 2.5 + 1.2 * math.sin(i * .9); h = 3.6 - abs(i - 3) * .4
    for s in (-1, 1):
        for k in range(5):
            a, b = Vector((x, y + s * h * .5 * math.sin(k * .35), h * .4 * math.cos(k * .35))), Vector((x, y + s * h * .5 * math.sin((k + 1) * .35), h * .4 * math.cos((k + 1) * .35)))
            limb(a, b, .3 - k * .02, bone, .28 - k * .02)
    for k in range(4): limb((x, y + s * h * .5 * math.sin((k + 1) * .35), h * .4 * math.cos((k + 1) * .35)), (x, y + s * h * .5 * math.sin((k + 2) * .35), h * .4 * math.cos((k + 2) * .35)), .26, bone2, .24)
    slab((x, y, h * .38), (.7, .7, .5), bone2)
    for k in range(3): tuft((x + random.uniform(-.5, .5), y + random.uniform(-1, 1), 0), random.uniform(.5, 1.0), grass)
# a fallen leg bone and a jaw bone lying in the grass
limb((3, -3, .4), (7, -1.5, .3), .5, bone, .4); limb((7, -1.5, .3), (8, -1.2, .5), .3, bone2, .2)
slab((-1.5, -4.5, .1), (2.4, .6, .3), bone2, (0, 0, .4))
# the standing stone with glowing runes
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1.1, radius2=.7, depth=4.6)
for v in bm.verts: v.co.z += 2.3; v.co.x *= 1.2
put(bm, rockm, (0, 0, 0), (0, 0, .3))
for k in range(3): slab((.2 + k * .1, -1.0, 1.2 + k * .9), (.15, .1, .45), rune, (0, 0, .3))
slab((0, -1.0, 3.6), (.9, .12, .15), rune, (0, 0, .3))
beam("POINT", (.3, .9, 1), 600, (0, -1.8, 2.2))
for i in range(34):
    x, y = random.uniform(-10, 10), random.uniform(-10, 10)
    if abs(x - 2.5 * math.sin(y / .9 * .3)) < 1.6 or math.hypot(x, y) > 11.5 or math.hypot(x + 5.5, y - 4) < 3: continue
    tuft((x, y, 0), random.uniform(.5, 1.1), grass if i % 3 else fern)
beam("SUN", (.6, .75, 1), 4.5, (-24, -14, 9), (0, 0, 1)); beam("SUN", (.9, .5, .6), 2.2, (20, 22, 8), (0, 0, 1))
w = bpy.data.worlds.new("moon"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((16, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
