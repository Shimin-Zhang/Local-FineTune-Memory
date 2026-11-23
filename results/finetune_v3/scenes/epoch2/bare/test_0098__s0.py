import bpy, bmesh, random, math
from mathutils import Vector
random.seed(843)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def mat(rgb, glow=0):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
earth, clay, claywet, brick, brick2, mud, cloth, timber, thatch, smoke, ember = (mat((.13, .1, .07)), mat((.3, .15, .08)), mat((.2, .1, .06)),
    mat((.45, .17, .08)), mat((.35, .13, .07)), mat((.07, .05, .04)), mat((.55, .45, .3)), mat((.22, .13, .07)), mat((.3, .22, .1)), mat((.12, .1, .12)), mat((1, .3, .05), 14))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, d, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * k, v.co.y * d[1] * k, (v.co.z + .5) * d[2]))
    return mk(bm, m, at, (0, 0, rz))
def drum(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def mound(at, r, m, sq=.5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x, v.co.y, v.co.z * sq)) * random.uniform(.85, 1.15)
    return mk(bm, m, at)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return mk(bm, m)
def glowlight(at, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# the field: a slab of earth, rough and tapering below
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=11.5, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .3)))
    v.co.z -= 2
mk(bm, earth)
# clay pit: a sunken dark mud basin with a rim of spoil heaps
box((-6.2, -2.2, -.05), (4.6, 3.2, .2), mud)
for i in range(8):
    a = i * math.pi / 4
    mound((-6.2 + math.cos(a) * 2.7, -2.2 + math.sin(a) * 2.0, .1), random.uniform(.5, .8), claywet, .6)
# the clamp kiln: a long domed mound of bricks, with a smouldering mouth at the end
box((5.6, 2.2, 0), (7.4, 3.4, 1.6), brick2, 0, .96)
box((5.6, 2.2, 1.6), (7.0, 3.0, .9), brick, 0, .55)
for i in range(7):
    for j in range(3):
        box((2.6 + i * .95, .5 + j * 1.7, 1.0 + (j % 2) * .2), (.9, .5, .25), brick if (i + j) % 2 else brick2)
box((1.7, 2.2, .2), (.3, 1.3, 1.0), ember)
glowlight((.8, 2.2, 1.2), (1, .35, .08), 900)
for i in range(5): mound((1.6 + i * .4, 2.2 + random.uniform(-.3, .3), 1.9 + i * .8), .5 + i * .12, smoke, .8)
# drying rows: stacks of bricks in courses, some covered by cloth
for r in range(3):
    for c in range(5):
        x, y = -2.6 + c * 1.5, -5.8 + r * 1.9
        for k in range(4):
            for j in range(3):
                if k % 2: box((x + .1, y, k * .22), (.8, .5, .2), brick if (j + k) % 2 else brick2)
                else: box((x, y, k * .22), (.8, .5, .2), brick2 if (j + k) % 2 else brick)
for (x, y) in ((-1.1, -5.8), (1.4, -2.0), (-2.6, -3.9)):
    for sx in (-1, 1):
        for sy in (-1, 1): strut((x + sx * .7, y + sy * .5, 0), (x + sx * .7, y + sy * .5, 1.3), .08, timber)
    box((x, y, 1.3), (1.9, 1.4, .1), cloth, 0, .9)
# moulding tables with wet clay and a worker's stack
for i in range(2):
    x = 1.0 + i * 2.8
    box((x, -1.0, .8), (2.0, 1.0, .15), timber)
    for sx in (-.9, .9):
        for sy in (-.4, .4): box((x + sx, -1.0 + sy, 0), (.15, .15, .8), timber)
    mound((x - .3, -1.0, 1.05), .35, claywet, .6); box((x + .5, -1.0, 1.0), (.6, .4, .15), brick)
box((7.8, -4.0, 0), (1.2, 1.2, 1.0), timber)
# wheelbarrow and a clay cart
drum((-1.0, 3.6, .3), .45, .6, 7, timber, .3).rotation_euler = (0, math.pi / 2, 0)
box((-1.0, 3.6, .7), (1.2, .8, .4), timber, 0, .8)
# a hut for tools, with a thatch roof
box((8.2, 6.0, 0), (3.0, 2.4, 1.8), timber); box((8.2, 6.0, 1.8), (3.6, 3.0, .15), thatch, 0, .6)
box((8.2, 4.75, 0), (.8, .1, 1.2), mud)
# light: low amber dusk sun from the right, violet rim behind
for c, w, p in (((1, .5, .2), 5.5, (22, -10, 6)), ((.5, .35, .9), 2, (-16, 14, 9))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("dusk"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 85; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
t = Vector((0, 0, 1.2)); co.location = t + Vector((-12, -41, 25))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
