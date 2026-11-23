import bpy, bmesh, math, random
from mathutils import Vector
random.seed(526)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def citrus(rgb, e=0, r=.85):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = e
    return m
flesh, peel, pore, nub, leaf, board, wood, fruit = (citrus((.95, .78, .06)), citrus((.85, .62, .04)), citrus((.5, .32, .02)), citrus((.45, .4, .1)),
    citrus((.1, .3, .08)), citrus((.3, .17, .09)), citrus((.18, .1, .06)), citrus((.7, .08, .05)))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("l"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("l", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def ball(at, r, m, sx=1, sy=1, sz=1, jit=.08, sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)) * random.uniform(1 - jit, 1 + jit)
    return mesh(bm, m, at)
def knob(at, r, m, k=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= k
    return mesh(bm, m, at)
def stem(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=t, radius2=t * .7, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return mesh(bm, m)
def wedge(at, r0, r1, a0, a1, h, m):
    bm = bmesh.new(); ring = []
    for r, z in ((r0, 0), (r1, 0), (r1, h), (r0, h)):
        ring.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for a in (a0, a1)])
    for i in range(4):
        j = (i + 1) % 4
        if i != 3: bm.faces.new((ring[i][0], ring[i][1], ring[j][1], ring[j][0]))
    bm.faces.new(ring[0][::-1]); bm.faces.new(ring[3])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh(bm, m, at)
def lite(kind, at, col, w, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = col, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# round fruit-board plinth
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=10, depth=2.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .2)))
    v.co.z -= 1.2
mesh(bm, wood)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=9.2, radius2=9.2, depth=.5)
for v in bm.verts: v.co.z += .25
mesh(bm, board)
# the lemon: bumpy ellipsoid, tapering at both ends
ball((0, 0, 2.6), 3.0, peel, 1.25, 1, .9, .07)
for i in range(7):
    knob((-3.9 + i * 1.3 + random.uniform(-.3, .3), random.uniform(-.8, .8), 3.9 + random.uniform(-.1, .1)), .5, peel, .5)
    knob((-3.4 + i * 1.2, random.uniform(-.9, .9), 1.2 + random.uniform(-.1, .1)), .45, peel, .5)
# dimpled pores, a few clustered on the shoulders
for i in range(110):
    p = Vector((random.gauss(0, 2.4), random.gauss(0, 1.8), random.gauss(2.6, 1.1))); p.normalize() * 3.0
    p.x *= 1.25; p.z *= .9
    knob(p * 1.005, .13, pore, .45)
# stem nub and a leaf
stem((0, 0, 4.3), (0, 0, 4.9), .22, nub)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=.08, radius2=.08, depth=1.6)
mesh(bm, leaf, (1.0, 0, 5.0), (0, math.pi / 2, 0))
# a halved lemon lying in front, segments glowing faintly
hx, hy = 0, -5.2
ball((hx, hy, 1.1), 2.4, peel, 1, 1, .45, .04)
ball((hx, hy, 1.5), 2.0, flesh, 1, 1, .1, .02)
for k in range(8):
    a0 = k * math.pi / 4 + .06; a1 = (k + 1) * math.pi / 4 - .06
    wedge((hx, hy, 1.55), .3, 1.7, a0, a1, .1, peel)
    wedge((hx, hy, 1.55), .45, 1.5, a0 + .05, a1 - .05, .12, flesh)
lite("POINT", (hx, hy, 2.4), (1, .85, .2), 220)
# two smaller lemons and a red apple for colour
ball((-6.2, -2.0, 1.3), 1.4, peel, 1.2, 1, .85, .08); ball((6.4, -1.5, 1.3), 1.3, peel, 1.2, 1, .85, .08)
ball((5.6, 3.8, 1.5), 1.5, fruit, 1, 1, 1, .05); stem((5.6, 3.8, 2.8), (5.8, 3.8, 3.5), .08, wood)
lite("SUN", (-24, -16, 12), (1, .72, .35), 5, (0, 0, 2)); lite("SUN", (22, 20, 12), (.4, .6, 1), 2.2, (0, 0, 2))
w = bpy.data.worlds.new("w"); w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
sc.world = w
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.2)); co.location = t + Vector((8, -44, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
