import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1642)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
sand, sand2, stone, stone2, water = tone((.32, .2, .11)), tone((.25, .15, .08)), tone((.36, .3, .24)), tone((.26, .21, .17)), tone((.05, .13, .17))
hide, hide2, leather, thorn, trunk = tone((.55, .38, .2)), tone((.4, .25, .13)), tone((.35, .2, .1)), tone((.14, .25, .1)), tone((.2, .13, .09))
black, fire, dark, rope = tone((.04, .04, .05)), tone((1, .5, .1), 14), tone((.02, .03, .04)), tone((.6, .5, .3))
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rz=0, top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return shape(bm, m, at, (0, 0, rz))
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return shape(bm, m, at, rot)
def blob(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return shape(bm, m, at)
def limb(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return shape(bm, m)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# desert base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14, depth=3.5)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.12, .12)
    v.co.z -= 1.75
shape(bm, sand)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(4, 12)
    slab((math.cos(a) * r, math.sin(a) * r, 0), (random.uniform(2, 4), random.uniform(1.5, 3), .12), sand2, random.uniform(0, 3))
# the well: stone ring, dark water, cross beam, rope and leather bucket
cyl((0, 0, 0), 1.9, .8, 10, stone2)
for i in range(10):
    a = i * .628
    slab((math.cos(a) * 1.9, math.sin(a) * 1.9, 0), (1.5, 1.0, .95), stone, a + 1.57, .95)
cyl((0, 0, .7), 1.35, .05, 10, water)
for sx in (-1, 1): slab((sx * 1.5, 0, 1.0), (.2, .2, 3.0), trunk)
slab((0, 0, 3.6), (3.6, .25, .25), trunk); cyl((0, 0, 3.4), .22, .25, 6, trunk, rot=(0, math.pi / 2, 0))
limb((0, 0, 3.4), (0, 0, 1.5), .06, rope)
cyl((0, 0, 1.5), .35, .5, 7, leather, .45); cyl((0, 0, 2.0), .45, .08, 7, leather)
# long watering trough with a little water
slab((-6.5, -3.5, 0), (6.0, 1.3, .9), stone2, .15)
slab((-6.5, -3.5, .8), (5.4, .9, .15), water, .15)
for sx in (-1, 1): slab((-6.5 + sx * 2.9, -3.5, 0), (.3, 1.4, 1.0), stone, .15)
# two camels
def camel(x, y, face, m):
    c, s = math.cos(face), math.sin(face)
    def at(dx, dy, z): return Vector((x + dx * c - dy * s, y + dx * s + dy * c, z))
    for dx in (-.9, .9):
        for dy in (-.25, .25): limb(at(dx, dy, 0), at(dx, dy, 1.1), .12, m)
    blob(at(0, 0, 1.7), 1.0, m, (1.3, .75, .8))
    blob(at(1.0, 0, 2.2), .38, m, (1, 1, 1.2)); limb(at(1.1, 0, 2.3), at(1.9, 0, 3.0), .16, m)
    blob(at(2.1, 0, 3.0), .3, m, (1.3, .6, .8)); limb(at(1.2, 0, 1.6), at(1.1, 0, 3.2), .1, m)
    limb(at(-1.2, 0, 1.8), at(-1.8, 0, 1.3), .08, m)
camel(-2.5, 4.5, .5, hide); camel(4.5, 5.0, -.8, hide2)
# black tent with a glowing doorway and a brazier
cyl((6.5, -3.5, 0), 2.6, 2.4, 7, black, .1)
slab((6.5, -6.0, 0), (1.3, .2, 1.8), fire, 0, .8)
lamp("POINT", (1, .55, .15), 500, (6.5, -6.8, 1.0))
cyl((3.5, -5.5, 0), .4, .6, 6, dark, .3); cyl((3.5, -5.5, .6), .3, .5, 6, fire, .02)
lamp("POINT", (1, .5, .12), 500, (3.5, -5.5, 1.4))
# thorny acacias
for x, y, s in ((-8, 5, 1.2), (9, 3, 1.0), (-3, 8, 1.1), (2, -8, .9)):
    limb((x, y, 0), (x + .3, y, 2.2 * s), .25 * s, trunk)
    for k in range(3):
        a = k * 2.1
        limb((x + .3, y, 2.2 * s), (x + .3 + math.cos(a) * 1.6 * s, y + math.sin(a) * 1.6 * s, 2.5 * s), .1 * s, trunk)
        blob((x + .3 + math.cos(a) * 1.8 * s, y + math.sin(a) * 1.8 * s, 2.7 * s), 1.0 * s, thorn, (1.5, 1.2, .5))
    blob((x + .3, y, 2.9 * s), 1.1 * s, thorn, (1.4, 1.2, .5))
lamp("SUN", (1, .55, .25), 5.5, (-26, -14, 8), (0, 0, 1)); lamp("SUN", (.45, .55, .9), 2.2, (22, 20, 10), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((12, -56, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
