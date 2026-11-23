import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1653)
sc = bpy.context.scene
def tone(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
dust, rock, rock2, fur, fur2, bone, grass, bark, leaf, fire, water, reed, bird, shell, flame, sun, smoke = (tone((.35, .17, .09)), tone((.3, .22, .18)), tone((.22, .16, .15)), tone((.3, .17, .09)), tone((.2, .11, .06)), tone((.7, .65, .55)), tone((.25, .22, .08)), tone((.2, .12, .07)), tone((.12, .2, .07)), tone((1, .45, .08), 12), tone((.05, .12, .15), rough=.2), tone((.3, .3, .1)), tone((.05, .04, .05)), tone((.5, .4, .3)), tone((1, .3, .05), 20), tone((1, .5, .15), 3), tone((.2, .18, .2)))
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
def limb(a, b, r, m):
    a, b = Vector(a), Vector(b); d = b - a
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r * .8, depth=d.length)
    for v in bm.verts: v.co.z += d.length / 2
    return mesh(bm, m, a, d.to_track_quat('Z', 'Y').to_euler())
def ape(x, y, h, face, m, reach=False):
    c, s = math.cos(face), math.sin(face)
    P = lambda dx, dy, z: Vector((x + dx * c - dy * s, y + dx * s + dy * c, z))
    limb(P(0, 0, 0), P(0, 0, h * .6), h * .26, m); limb(P(0, 0, h * .55), P(0, 0, h * 1.0), h * .2, m)
    limb(P(-.28, 0, h * .5), P(-.5, .2, .05), h * .09, m); limb(P(.28, 0, h * .5), P(.5, .2, .05), h * .09, m)
    for sx in (-.17, .17): limb(P(sx, 0, h * .95), P(sx, 0, .75), h * .07, m)
    b = bmesh.new(); bmesh.ops.create_icosphere(b, subdivisions=1, radius=h * .2)
    for v in b.verts: v.co.z *= .9
    mesh(b, m, P(0, .1, h * 1.15))
    if reach:
        for sx in (-1, 1): limb(P(sx * .15, 0, h * 1.0), P(sx * .1, .6, h * 1.4), h * .06, m)
def antelope(x, y, face):
    c, s = math.cos(face), math.sin(face)
    P = lambda dx, dy, z: Vector((x + dx * c - dy * s, y + dx * s + dy * c, z))
    limb(P(0, 0, .6), P(0, 0, 1.1), .22, fur2); limb(P(.5, 0, 1.0), P(.8, 0, 1.4), .12, fur2)
    for sx in (-.25, .25):
        for sy in (-.1, .1): limb(P(sx, sy, 0), P(sx, sy, .6), .05, fur2)
    stick(P(.85, 0, 1.4), P(.95, 0, 1.7), .04, bone)
def tuft(x, y, h):
    for k in range(3): limb((x + k * .12 - .12, y, 0), (x + k * .12 - .12 + random.uniform(-.1, .1), y, h), .05, reed)
def dawn(at, col, w):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
# the sun itself, a glowing disc low behind the rocks at the right
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=1.6, radius2=1.6, depth=.2)
mesh(bm, sun, (12, 10, 1.2), (math.pi / 2, 0, 0))
# a ring of stones around the fire, a second fire pit, a stack of stones
for i in range(8):
    a = i * .785
    crag((math.cos(a) * 1.0, math.sin(a) * 1.0, .1), .22, rock2, .8)
for i in range(3): crag((7, -3, .2 + i * .2), .35 - i * .06, rock, .8)
# a trail of footprints from the fire toward the watering hole
for i in range(8):
    for s in (-.15, .15): crag((.5 + i * .5 + s, -1 - i * .5, .03), .12, dust, .3)
# the apes, gathered in a loose arc, two of them reaching toward the monolith
for i, (x, y, h, f) in enumerate(((-3.2, -3.4, 1.5, 1.0), (-1.6, -4.2, 1.4, .8), (.2, -4.6, 1.6, .5), (2.0, -4.2, 1.4, .2), (3.6, -3.2, 1.5, -.1), (-4.4, -1.6, 1.4, 1.3), (4.8, -1.2, 1.5, -.4), (-2.4, -2.2, 1.2, 1.1), (1.2, -3.0, 1.3, .6))):
    ape(x, y, h, f, fur if i % 2 else fur2, reach=(i in (2, 4)))
# the bone tool, larger than life
stick((2.0, -4.2, 1.0), (2.0, -4.2, 2.6), .12, bone)
# a few footprints of dust and scattered pebbles
for i in range(12): crag((random.uniform(-6, 6), random.uniform(-5, 2), .05), random.uniform(.12, .25), rock2, .5)
# the fire's flames, taller and more visible
for i in range(5):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=5, radius1=.2, radius2=0, depth=random.uniform(.8, 1.4))
    mesh(bm, flame, (random.uniform(-.2, .2), random.uniform(-.2, .2), .5), (0, 0, 0))
# smoke drifting up from the fire
for i in range(4): crag((.3 * i, .2 * i, 1.5 + i * .8), .3 + i * .1, smoke, .8)
dawn((22, -8, 6), (1, .45, .18), 6)
dawn((-14, 16, 9), (.4, .35, .9), 2.2)
fl = bpy.data.lights.new("fire", "POINT"); fl.color = (1, .45, .1); fl.energy = 400
fo = bpy.data.objects.new("fire", fl); fo.location = (0, 0, 1.2); sc.collection.objects.link(fo)
w = bpy.data.worlds.new("dawn"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((-8, -47, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
