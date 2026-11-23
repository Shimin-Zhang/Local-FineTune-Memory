import bpy, bmesh, math, random
from mathutils import Vector
random.seed(701)
sc = bpy.context.scene
def mat(c, e=0, r=.9):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
    return m
rock1, rock2, rock3, rock4, cub, tail, bark, leaf2, hippo, giraffe, zebra, zebrow, elephant, elephant2, bird, lion, lion2, grass, sand = (
    mat((.32, .2, .14)), mat((.24, .15, .11)), mat((.4, .25, .16)), mat((.28, .17, .12)), mat((.65, .35, .12)), mat((.3, .12, .05)), mat((.28, .14, .07)), mat((.1, .17, .07)), mat((.4, .4, .42)), mat((.7, .45, .1)), mat((.8, .8, .78)), mat((.05, .05, .05)), mat((.5, .5, .5)), mat((.4, .4, .4)), mat((.8, .55, .15)), mat((.5, .2, .06)), mat((.6, .3, .1)), mat((.2, .25, .08)), mat((.35, .22, .12)))
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location = Vector(at); o.rotation_euler = Vector(rot)
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cone(x, y, z, r1, r2, h, n, m, jit=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), h / 2 + random.uniform(-jit, jit)))
    return add(bm, m, (x, y, z))
def ball(x, y, z, r, m, sq=1, sub=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co.z *= sq; v.co *= random.uniform(.93, 1.07)
    return add(bm, m, (x, y, z))
def limb(ax, ay, az, bx, by, bz, r, m):
    d = Vector((bx - ax, by - ay, bz - az))
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r * .8, depth=d.length)
    return add(bm, m, (ax, ay, az), d.to_track_quat('Z', 'Y').to_euler())
def slab(x, y, z, w, d, h, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return add(bm, m, (x, y, z), (0, 0, rz))
def beast(x, y, s, m, face=0, horn=False):
    c, sn = math.cos(face), math.sin(face)
    slab(x, y, .5 * s, 1.7 * s, .8 * s, .8 * s, m, face)
    ball(x + 1.1 * s * c, y + 1.1 * s * sn, 1.3 * s, .45 * s, m)
    for dx in (-.6, .6):
        for dy in (-.25, .25): slab(x + dx * s * c - dy * s * sn, y + dx * s * sn + dy * s * c, 0, .22 * s, .22 * s, .6 * s, m)
    limb(x - .8 * s * c, y - .8 * s * sn, 1.0 * s, x - 1.4 * s * c, y - 1.4 * s * sn, 1.3 * s, .12 * s, m)
    if horn:
        for sgn in (-1, 1): limb(x + 1.1 * s * c, y + 1.1 * s * sn + sgn * .2 * s, 1.7 * s, x + 1.1 * s * c, y + 1.1 * s * sn + sgn * .4 * s, 2.2 * s, .06 * s, zebrow)
def acacia(x, y, s):
    limb(x, y, 0, x + .2 * s, y, 2.4 * s, .3 * s, bark)
    for k in range(4):
        a = k * 1.6; limb(x + .2 * s, y, 2.2 * s, x + .2 * s + 1.6 * s * math.cos(a), y + 1.6 * s * math.sin(a), 2.7 * s, .1 * s, bark)
    ball(x + .2 * s, y, 3.2 * s, 2.2 * s, leaf2, .45, 2)
# the savanna floor: a flat, wide disc with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=13, radius2=13, depth=2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1, .2)))
    v.co.z -= 1
add(bm, sand)
# the rock: a squat, wide, layered cliff, with ledges and a flat top
for r1, r2, z, m in ((8.0, 6.8, 0, rock1), (6.8, 5.6, 1.8, rock2), (5.6, 4.6, 3.6, rock3), (4.6, 3.6, 5.4, rock1), (3.6, 2.6, 7.2, rock4), (2.6, 2.2, 9.0, rock2)):
    cone(0, 0, z, r1, r2, 1.9, 7, m, .45)
cone(0, 0, 10.8, 2.2, 2.2, .6, 7, rock3, .1)
for i in range(10):
    a = i * .63 + .3; r = 3.2 + (i % 3) * .6
    slab(r * math.cos(a) * .95, r * math.sin(a) * .95, 2.2 + (i % 4) * 2.0, 1.6, .9, .6, rock4 if i % 2 else rock2, a + 1.57)
# the cub held up at the tip, arms raised, and the king's arms
cz = 11.4
ball(0, 0, cz + .9, .5, cub, 1.0, 1); ball(0, 0, cz + 1.8, .42, cub, 1.0, 1)
for sgn in (-1, 1):
    ball(sgn * .35, 0, cz + 2.0, .13, cub); limb(sgn * .45, 0, cz + 1.0, sgn * .9, 0, cz + 2.0, .11, cub); limb(sgn * .35, 0, cz + .8, sgn * .45, 0, cz + .1, .12, cub)
limb(-.1, 0, cz + .8, -.45, 0, cz + .2, .1, tail)
for sgn in (-1, 1): limb(sgn * 1.1, 0, 11.2, sgn * .45, 0, 12.1, .15, lion)
# the gathered animals, a little larger so they read
for i, (x, y, f) in enumerate(((-6, -9, 1.2), (-3, -10, 1.0), (3, -10, 2.5), (7, -9, 3.4), (-10, -5, 1.5), (10, -4, 3.0), (-5, -7, 1.1), (5, -7, 2.4), (-8, 8, 1.2), (8, 8, 3.2))): beast(x, y, 1.2, lion if i % 3 else lion2, f)
for x, y, f in ((-11, 1, 1.0), (11.5, 2, 3.5), (-8, 9, 1.3), (8, 10, 3.2)):
    slab(x, y, .9, 2.8, 1.3, 1.5, elephant, f); ball(x + 1.6 * math.cos(f), y + 1.6 * math.sin(f), 1.8, .85, elephant, .9)
    for dx in (-1, 1):
        for dy in (-.45, .45): slab(x + dx * math.cos(f) - dy * math.sin(f), y + dx * math.sin(f) + dy * math.cos(f), 0, .55, .55, .9, elephant)
    limb(x + 1.9 * math.cos(f), y + 1.9 * math.sin(f), 1.9, x + 2.7 * math.cos(f), y + 2.7 * math.sin(f), 1.6, .2, elephant2)
for x, y, f in ((-3.5, -4, 1.2), (3, -4.5, 2.6), (-12, -1, 1.0), (12, -1, 3.2)): beast(x, y, 1.1, zebra, f, True)
for x, y, f in ((-6, 4, 1.2), (6.5, 4.5, 3.2)):
    limb(x, y, 1.0, x, y, 3.6, .22, giraffe); slab(x, y, 1.0, 1.8, .8, .9, giraffe, f); ball(x, y, 4.0, .45, giraffe, 1.0)
beast(-10, 6, 1.5, hippo, 1.2)
for i in range(8):
    a = i * .8 + .2; cone(3.2 * math.cos(a), 3.2 * math.sin(a), 12.4 + (i % 3) * .9, .25, .02, .9, 4, bird, 0)
for x, y, s in ((-12, 6, 1.1), (12.5, 7, 1.2), (-12, -3, .9), (12.5, -2, 1.0)): acacia(x, y, s)
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(9, 12)
    ball(r * math.cos(a), r * math.sin(a), .2, random.uniform(.3, .6), rock3 if i % 2 else rock1, .7)
for i in range(30):
    a = random.uniform(0, 6.28); r = random.uniform(8.5, 12.4)
    cone(r * math.cos(a), r * math.sin(a), 0, .25, .02, random.uniform(.6, 1.3), 4, grass, .05)
# sunrise: low gold key from the left, warm pink rim behind right
for c, w, p in (((1, .5, .2), 5.5, (-26, -12, 8)), ((.9, .4, .55), 2.2, (22, 24, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 5)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .02, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 400
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 5.5)); co.location = tg + Vector((6, -56, 30))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
