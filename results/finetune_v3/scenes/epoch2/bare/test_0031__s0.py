import bpy, bmesh, math, random
from mathutils import Vector
random.seed(544)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def surf(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
sand, rock1, rock2, rock3, hole = surf((.3, .2, .13)), surf((.26, .15, .1)), surf((.32, .19, .12)), surf((.2, .12, .1)), surf((.01, .008, .008))
wood, rope, iron, flag, torch = surf((.3, .2, .12)), surf((.5, .42, .3)), surf((.1, .1, .12), 0, .5), surf((.7, .1, .1)), surf((1, .45, .08), 14)
gemA, gemB, gemC, bone = surf((.2, .9, 1), 6), surf((.9, .3, 1), 6), surf((.3, 1, .4), 6), surf((.6, .55, .45))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, sz, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * sz[0], v.co.y * sz[1], (v.co.z + .5) * sz[2]))
    return mesh(bm, m, at, (0, 0, rz))
def rod(a, b, r, m, n=5):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return mesh(bm, m)
def rock(at, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return mesh(bm, m, at)
def lamp(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# canyon floor of packed sand with a ragged underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=11, depth=3.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.4, 1.4), random.uniform(-1.4, 1.4), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.6
mesh(bm, sand)
# the canyon wall: a stack of crags along the back, with a ledge
for i in range(9):
    x = -9 + i * 2.2; h = random.uniform(6, 10)
    rock((x, 8.5, h / 2), random.uniform(2.6, 3.4), (rock1, rock2, rock3)[i % 3], 1.2)
    rock((x + 1.1, 7.6, 2.2), random.uniform(1.6, 2.2), (rock2, rock3, rock1)[i % 3], 1.1)
slab((0, 5.6, 2.8), (13, 2.6, .5), rock2)
for x in (-5.5, 5.5): slab((x, 4.4, 0), (1.2, 1.2, 2.8), rock3)
# tunnel mouths: round dark openings with stone rims
for (x, z, r) in ((-4.5, 1.6, 1.5), (-.8, 1.5, 1.3), (2.8, 1.7, 1.4), (6.0, 1.4, 1.1), (-2.4, 4.6, 1.0), (1.4, 4.8, .9)):
    slab((x, 4.2, z - r), (2 * r, .6, 2 * r), hole)
    for k in range(8):
        a = k * math.pi / 4
        slab((x + math.cos(a) * (r + .15), 3.9, z + math.sin(a) * (r + .15)), (.55, .5, .5), rock1, a)
# ladders leaning on the mouths and a plank ramp
for (x, z, r) in ((-4.5, 1.6, 1.5), (2.8, 1.7, 1.4)):
    for s in (-.35, .35): rod((x + s, 2.2, 0), (x + s, 3.9, z - .2), .07, wood)
    for k in range(7): rod((x - .35, 2.2 + k * .23, .3 + k * .2), (x + .35, 2.2 + k * .23, .3 + k * .2), .05, wood)
rod((-1.4, 2.2, 0), (-.8, 3.9, 1.2), .07, wood); rod((-.2, 2.2, 0), (-.8, 3.9, 1.2), .07, wood)
for k in range(5): rod((-1.2 + k * .12, 2.2 + k * .34, .3 + k * .2), (-.4 + k * .12, 2.2 + k * .34, .3 + k * .2), .05, wood)
# trap-laden entry: trip wire, stakes, pit cover, hanging weights
for i in range(5): slab((-1.5 + i * .5, 1.4, 0), (.12, .12, .6 + .1 * (i % 2)), bone, i)
rod((-3.6, 1.2, .1), (.6, 1.2, .1), .03, rope); rod((-3.6, 1.2, .9), (.6, 1.2, .9), .03, rope)
slab((-1.0, 1.2, 0), (1.6, 1.6, .12), wood, .15)
for s in (-1, 1): rod((s * 1.0, 1.2, 0), (s * 1.0, 1.2, 1.1), .05, wood)
for x in (-3.2, .2):
    rod((x, 1.2, 0), (x, 1.2, 2.6), .08, wood); slab((x - .3, 1.2, 2.0), (.6, .1, .1), wood)
    rod((x, 1.2, 2.0), (x, 1.2, 1.6), .03, rope); slab((x - .25, 1.2, 1.0), (.5, .5, .6), iron)
# the pile of shiny stones, big enough to see
for i, (m, r) in enumerate(((gemA, .55), (gemB, .5), (gemC, .5), (gemA, .45), (gemB, .4), (gemC, .45), (gemA, .35), (gemC, .3))):
    rock((-6.5 + (i % 4) * .75 + random.uniform(-.2, .2), -2.5 + (i // 4) * .8, .3 + (i // 4) * .45), r, m, .8)
lamp((-6.5, -2.5, 1.5), (.5, .9, 1), 600)
# tiny banner on a pole, torches by the mouths
rod((8.0, 1.0, 0), (8.0, 1.0, 5.2), .08, wood); slab((7.3, 1.0, 3.6), (1.5, .08, 1.1), flag)
for x in (-4.5, 2.8):
    rod((x, 3.0, 0), (x, 3.0, 2.2), .07, wood); slab((x - .15, 2.85, 2.2), (.3, .3, .5), torch)
    lamp((x, 2.6, 2.6), (1, .5, .15), 250)
for i in range(12):
    x, y = random.uniform(-9, 9), random.uniform(-9, 3)
    if abs(x) < 8 and y > -4: rock((x, y, .15), random.uniform(.3, .7), (rock1, rock3)[i % 2], .7)
for i in range(4): slab((random.uniform(-3, 3), random.uniform(-6, -3), 0), (.4, .4, .3), bone, random.random())
# lights: cold moon from the left, a violet rim from behind
for c, w, p in (((.55, .65, 1), 5, (-24, -14, 11)), ((.7, .4, 1), 2, (20, 22, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .015, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 2, 4)); co.location = t + Vector((6, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
