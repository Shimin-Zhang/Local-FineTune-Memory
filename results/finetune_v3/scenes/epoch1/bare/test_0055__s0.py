import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1850)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def glaze(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    mats[name] = m
for k, c in (("moss", (.1, .22, .08)), ("moss2", (.07, .15, .06)), ("gravel", (.35, .3, .25)), ("stone", (.3, .3, .33)), ("stone2", (.22, .22, .26)),
             ("wood", (.3, .18, .1)), ("bark", (.2, .12, .08)), ("pine", (.05, .2, .12)), ("pine2", (.1, .26, .1)), ("fern", (.15, .35, .1)),
             ("bush", (.1, .25, .08)), ("flower", (.7, .5, .1)), ("cub", (.38, .38, .42))): glaze(k, c)
glaze("gold", (1, .75, .3), 3)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def cube(at, d, m, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return put(bm, m, at, (rx, 0, rz))
def cone(at, r, h, n, m, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at)
def ball(at, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return put(bm, m, at)
def lamp(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# forest edge: grassy knoll with a gravel path winding in from the front
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=11, depth=3.2)
for v in bm.verts:
    v.co.x *= 1.1; v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.6, .2)))
    elif v.co.z > 0: v.co.z += random.uniform(-.1, .1)
put(bm, "moss")
for i in range(11):
    t = i / 10; x = 6 - 8 * t; y = -8 + 6 * t + 1.5 * math.sin(t * 5)
    cube((x, y, .03), (2.4, 2.2, .12), "gravel", rz=t * 3)
for i in range(14): ball((random.uniform(-11, 11), random.uniform(-10, 10), .05), random.uniform(.2, .4), "fern", (1, 1, .5))
# the pillar: tapered stone shaft, plinth and cap, with the wolf on top
px, py, h = -1.5, 2.5, 5.0
cone((px, py, 0), 1.7, .8, 8, "stone2"); cone((px, py, .8), 1.1, h - .8, 8, "stone", .9)
cone((px, py, h), 1.3, .5, 8, "stone2", 1.0)
for z in (1.8, 3.0, 4.2): cone((px, py, z), 1.0 - z * .02, .25, 8, "stone2", .95 - z * .02)
top = h + .5
def wolf(x, y, z, s, face, c="stone"):
    f = Vector((math.cos(face), math.sin(face), 0)); s = s
    def P(a, b, d, m, r=None):
        cube((x + f.x * a * s, y + f.y * a * s, z + b * s), (d[0] * s, d[1] * s, d[2] * s), m, rz=face, rx=0).rotation_euler = (0, 0, face)
    P(0, 0, (2.0 * s, .8 * s, .9 * s), c)
    P(1.2 * s, .5 * s, (.8 * s, .5 * s, .5 * s), c)
    P(1.9 * s, .8 * s, (.8 * s, .45 * s, .45 * s), c)
    for a in (-.15, .15): P(2.2 * s, .9 * s, (.2 * s, .2 * s, .3 * s), c)
    for a in (-.3, .3):
        P(-.6 * s, -.2 * s, (.3 * s, .3 * s, .8 * s), c); P(1.0 * s, -.1 * s, (.3 * s, .3 * s, .8 * s), c)
    P(-1.2 * s, .6 * s, (.3 * s, .3 * s, .8 * s), c)
    P(1.2 * s, 1.2 * s, (.2 * s, .2 * s, .5 * s), "cub")
wolf(px, py, top, 1.2, 2.0)
for k, (dx, dy) in enumerate(((-.9, -.5), (.9, -.5))):
    wolf(px + dx, py + dy, top, .5, 2.0 + k * .6 - .3)
lamp((1, .75, .3), 140, (px, py - 1.5, top + 1))
# bench, wooden sign and lamp post
cube((4.5, -2.0, .8), (2.4, .8, .12), "wood"); cube((4.5, -1.5, 1.0), (2.4, .1, .8), "wood")
for s in (-1, 1): cube((4.5 + s * 1.0, -2.0, 0), (.15, .7, .8), "wood")
for s in (-1, 1): cube((-5.5 + s * .8, -3.0, 0), (.2, .2, 3.2), "wood")
cube((-5.5, -3.0, 2.2), (2.4, .15, 1.1), "wood"); cube((-5.5, -3.1, 2.5), (1.8, .06, .3), "gravel")
cone((9, 3, 0), .15, 4.2, 5, "wood", .1); cube((9, 3, 4.2), (.9, .9, .9), "gold"); lamp((1, .75, .3), 400, (9, 3, 4.7))
# pines behind the pillar, ferns and bushes at the edge
for i in range(9):
    a = math.radians(20 + i * 20); x, y = 11 * math.cos(a) * .9, 9.5 * math.sin(a) + 1
    if y < -3: continue
    cone((x, y, 0), .3, 1.8, 5, "bark")
    for k in range(3): cone((x, y, 1.5 + k * 1.2), 1.6 - k * .4, 1.8, 6, "pine" if k % 2 else "pine2", .1)
for i in range(10):
    a = random.uniform(0, 6.28); x, y = random.uniform(7, 10) * math.cos(a), random.uniform(6, 9) * math.sin(a)
    if y < -2 or x < 0: continue
    ball((x, y, .3), random.uniform(.6, 1.0), "bush", (1, 1, .8))
for i in range(8):
    a = random.uniform(0, 6.28); x, y = random.uniform(7.5, 10.5) * math.cos(a), random.uniform(7, 10) * math.sin(a)
    if y < -3: continue
    cone((x, y, .1), .06, .8, 4, "fern", .02)
for i in range(6): ball((random.uniform(-9, 9), random.uniform(-9, -4), .15), .12, "flower", (1, 1, 1.2))
# morning: low gold sun from the left, soft violet rim from behind right
for c, w, at in (((1, .7, .4), 6, (-26, -14, 8)), ((.6, .5, 1), 2, (20, 22, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .03, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
t = Vector((0, 1, 2.5)); co.location = t + Vector((8, -50, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
