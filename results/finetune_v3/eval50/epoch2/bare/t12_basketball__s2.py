import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1968)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def surf(r, g, b, glow=0):
    m = bpy.data.materials.new("s"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .85
    if glow: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = glow
    return m
board, board2, black, orange, line, floor, glow, hoop, pad, net = (surf(*c) for c in (
    (.2, .12, .07), (.14, .08, .05), (.02, .02, .02), (.9, .38, .06), (.03, .03, .03), (.05, .05, .07), (1, .5, .1, 14), (1, .1, .05), (.7, .7, .72), (.8, .8, .85)))
def solid(m, bm, p=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("b", me); o.location = p; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, p, s, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return solid(m, bm, p, rot)
def drum(m, p, r, h, n=10, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return solid(m, bm, p, rot)
def orb(m, p, r, k=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= k
    return solid(m, bm, p)
def lit(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 17, v.co.y * 17, v.co.z * 3.4 - 1.7))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-.8, .8), v.co.y * .6 + random.uniform(-.8, .8), v.co.z - random.uniform(0, 1.6)))
solid(floor, bm)
for i in range(16):
    for j in range(16):
        if (i + j) % 2: slab(board2, (-7.5 + i, -7.5 + j, 0), (1, 1, .06))
for x in (-6, 6): slab(line, (x, 0, .06), (.2, 15, .03))
slab(line, (0, 0, .06), (12.4, .2, .03)); drum(line, (0, -4, .06), 3, .03, 10)
slab(line, (0, -4, .06), (6, .2, .03)); slab(line, (0, -4, .06), (.2, 6, .03))
# the ball, enlarged: orange sphere with pebble texture, seams and a flat spot for the lines
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=3.0)
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=1, use_grid_fill=True)
for v in bm.verts: v.co += Vector((random.uniform(-.1, .1), random.uniform(-.1, .1), random.uniform(-.1, .1)))
solid(orange, bm, (0, 0, 4.4))
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=3.06)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.1], context='VERTS')
for f in bm.faces: f.material_index = 0
solid(line, bm, (0, 0, 4.4))
for k in range(6):
    a = k * math.pi / 3
    drum(black, (0, 0, 4.4), 3.04, .12, 10, rot=(math.pi / 2, 0, a)).scale = (1, 1, 1)
    drum(black, (0, 0, 4.4), 3.04, .12, 10, rot=(0, math.pi / 2, a)).scale = (1, 1, 1)
for i in range(150):
    a, b = random.uniform(0, 6.28), random.uniform(-1.2, 1.2)
    p = Vector((math.cos(a) * math.cos(b), math.sin(a) * math.cos(b), math.sin(b))) * 3.02
    slab(orange, p + Vector((0, 0, 4.4)), (.14, .14, .06), (b, 0, a))
# a hoop behind: pole, arm, backboard, rim and net
slab(board2, (6, 6.5, 0), (.5, .5, 5.6)); slab(board2, (6, 6.5, 5.4), (.4, 2.6, .4), (0, 0, 0))
slab(pad, (6, 5.0, 3.6), (3.4, .2, 2.6)); slab(line, (6, 4.85, 3.6), (3.0, .05, 2.2)); slab(line, (6, 4.85, 5.0), (1.6, .05, .8))
drum(hoop, (6, 3.7, 3.9), .5, .15, 8, rot=(math.pi / 2, 0, 0)); drum(hoop, (6, 3.7, 3.9), .45, .15, 8, r2=.45, rot=(math.pi / 2, 0, 0))
for k in range(8):
    a = k * math.pi / 4
    slab(net, (6 + math.cos(a) * .45, 3.7 + math.sin(a) * .45, 2.7), (.05, .05, 1.2), (math.sin(a) * .3, -math.cos(a) * .3, 0))
# a bench and a few glowing floodlight masts
slab(board, (-6, 7, 1.0), (4.5, 1.2, .3))
for x in (-7.8, -4.2): slab(board2, (x, 7, 0), (.3, 1, 1))
for x, y in ((-7, -6), (7, -6)):
    slab(board2, (x, y, 0), (.3, .3, 6.5)); slab(glow, (x, y, 6.5), (1.4, .5, .5)); lit("POINT", (1, .75, .4), 450, (x, y, 6.2))
lit("SUN", (1, .72, .4), 5.5, (-24, -16, 10), (0, 0, 3)); lit("SUN", (.3, .5, 1), 2.2, (22, 20, 12), (0, 0, 3))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .012, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.8)); co.location = t + Vector((12, -48, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
