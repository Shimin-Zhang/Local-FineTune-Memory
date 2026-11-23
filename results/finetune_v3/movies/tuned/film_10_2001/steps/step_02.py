import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1053)
sc = bpy.context.scene
for o in list(sc.objects): sc.objects.unlink(o)
def tone(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
dust, dust2, rock, rock2, black, fur, fur2, bone, grass, bark, leaf, fire, eye = (tone((.35, .17, .09)), tone((.28, .13, .08)), tone((.3, .22, .18)), tone((.22, .16, .15)),
    tone((.008, .008, .012), rough=.2), tone((.3, .17, .09)), tone((.2, .11, .06)), tone((.7, .65, .55)), tone((.25, .22, .08)), tone((.2, .12, .07)), tone((.12, .2, .07)),
    tone((1, .45, .08), 12), tone((.9, .8, .5), 4))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def crag(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(.8, 1.25), v.co.y * random.uniform(.8, 1.25), v.co.z * sq * random.uniform(.8, 1.2)))
    return mesh(bm, m, at, (0, 0, random.random() * 3))
def stick(a, b, w, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * w, v.co.y * w, (v.co.z + .5) * d.length)) + a
    return mesh(bm, m)
def slab(at, w, d, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mesh(bm, m, at, rot)
def limb(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r * .8, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return mesh(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def ape(x, y, h, face, m, tool=None):
    c, s = math.cos(face), math.sin(face)
    P = lambda dx, dy, z: Vector((x + dx * c - dy * s, y + dx * s + dy * c, z))
    limb(P(0, 0, 0), P(0, 0, h * .6), h * .26, m); limb(P(0, 0, h * .55), P(0, 0, h * 1.0), h * .2, m)
    limb(P(-.28, 0, h * .5), P(-.5, .2, .05), h * .09, m); limb(P(.28, 0, h * .5), P(.5, .2, .05), h * .09, m)
    for sx in (-.17, .17):
        limb(P(sx, 0, h * .95), P(sx, 0, .75), h * .07, m)
        b = bmesh.new(); bmesh.ops.create_icosphere(b, subdivisions=1, radius=h * .2)
        for v in b.verts: v.co.z *= .9
        mesh(b, m, P(0, .1, h * 1.15))
        for sx2 in (-1, 1): slab(P(sx2 * .1, .27, h * 1.15), .07, .05, .05, eye)
    if tool: stick(P(.5, .2, .05), P(.5, .2, h * .9), .09, bone)
# dusty savanna slab, ragged underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.15, .15)
    v.co.z -= 2
mesh(bm, dust)
for i in range(14): crag((random.uniform(-10, 10), random.uniform(-9, 9), 0), random.uniform(.8, 1.6), dust2, .15)
# the monolith: 1 : 4 : 9 proportions, tilted slightly, on a flat rock plinth
slab((0, 0, 0), 4.6, 3.4, .3, rock2, (0, 0, .1))
slab((0, 0, .3), 1.2, .4, 9.0, black, (0, .02, .1))
# boulders and a small hill behind
for i, (x, y, r) in enumerate(((-6, 5, 2.2), (-3.5, 7, 1.6), (4, 6.5, 2.0), (7, 4, 1.4), (-8, 1, 1.2), (8.5, -1, 1.5), (-5, -6, 1.3), (6, -7, 1.1), (0, 8.5, 1.5), (-9, 6, 1.0))):
    crag((x, y, r * .3), r, rock if i % 2 else rock2, .8)
# the apes, gathered in a loose arc, one holding a bone
for i, (x, y, h, f) in enumerate(((-3.2, -3.4, 1.5, 1.0), (-1.6, -4.2, 1.4, .8), (.2, -4.6, 1.6, .5), (2.0, -4.2, 1.4, .2), (3.6, -3.2, 1.5, -.1), (-4.4, -1.6, 1.4, 1.3), (4.8, -1.2, 1.5, -.4), (-2.4, -2.2, 1.2, 1.1), (1.2, -3.0, 1.3, .6))):
    ape(x, y, h, f, fur if i % 2 else fur2, tool=(i == 3))
stick((2.0, -4.2, 1.0), (2.0, -4.2, 2.6), .1, bone)
# acacia tree with a flat crown, grass tufts, bones on the ground
for k in range(3):
    a = 2.2 + k * .5
    limb((-9 + math.cos(a) * 1.5, -3 + math.sin(a) * 1.5, 0), (-9 + math.cos(a) * 1.2, -3 + math.sin(a) * 1.2, 3.2 + k * .5), .22, bark)
for k in range(6): crag((-9 + random.uniform(-1.8, 1.8), -3 + random.uniform(-1.8, 1.8), 4.0 + random.uniform(0, .5)), random.uniform(.9, 1.4), leaf, .3)
for i in range(40):
    x, y = random.uniform(-10, 10), random.uniform(-9, 9)
    if math.hypot(x, y) < 5 or math.hypot(x + 9, y + 3) < 3: continue
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=4, radius1=.2, radius2=0, depth=random.uniform(.5, 1.0))
    mesh(bm, grass, (x, y, .3), (random.uniform(-.3, .3), random.uniform(-.3, .3), 0))
# small fire of sticks in the middle of the gathering
for k in range(5):
    a = k * 1.26
    stick((math.cos(a) * .5, math.sin(a) * .5, .1), (-math.cos(a) * .4, -math.sin(a) * .4, .5), .08, bark)
slab((0, 0, .1), .5, .5, .3, fire)
for i in range(5): stick((random.uniform(-3, 3), random.uniform(-3, -1), .1), (random.uniform(-3, 3), random.uniform(-3, -1), .15), .08, bone)
# dawn: low orange key from the right, violet-blue rim from behind
def dawn(at, col, w):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
dawn((22, -8, 6), (1, .45, .18), 6)
dawn((-14, 16, 9), (.4, .35, .9), 2.2)
fl = bpy.data.lights.new("fire", "POINT"); fl.color = (1, .45, .1); fl.energy = 250
fo = bpy.data.objects.new("fire", fl); fo.location = (0, 0, 1.0); sc.collection.objects.link(fo)
w = bpy.data.worlds.new("dawn"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((-8, -47, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
