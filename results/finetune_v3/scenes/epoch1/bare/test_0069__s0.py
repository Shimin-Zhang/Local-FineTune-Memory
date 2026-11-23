import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1389)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
C = {}
def tint(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9
    if glow:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = glow
    C[name] = m
for k, v in dict(gravel=(.3, .24, .17), grass=(.08, .16, .07), asphalt=(.07, .07, .08), plaster=(.55, .45, .3), roof=(.22, .1, .08), wood=(.3, .17, .09),
                 car=(.55, .06, .06), tyre=(.02, .02, .02), trunk=(.2, .12, .07), leaf=(.1, .22, .08), leaf2=(.17, .28, .08), trunk2=(.12, .08, .05)).items(): tint(k, v)
tint("pink", (1, .1, .45), 10); tint("teal", (.1, 1, .8), 10); tint("window", (1, .7, .3), 7); tint("bulb", (1, .9, .6), 8)
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("c"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("c", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(C[m]); return o
def slab(at, s, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mesh(bm, m, at, (0, 0, rz))
def gable(at, w, d, h, m, ridge=(0, 0)):
    bm = bmesh.new(); p = [bm.verts.new(v) for v in ((-w, -d, 0), (w, -d, 0), (w, d, 0), (-w, d, 0), (-w, 0, h), (w, 0, h))]
    for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): bm.faces.new([p[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return mesh(bm, m, at)
def tube(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, at, rot)
def blob(at, r, m, sq=(1, 1, .8)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.85, 1.15)
    return mesh(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# base: gravel court with grass verges and a road along the front
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 26, v.co.y * 24, v.co.z * 2.4 - 1.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.2)))
mesh(bm, "grass")
slab((0, 1.5, 0), (20, 15, .12), "gravel"); slab((0, -9.8, 0), (26, 3.4, .1), "asphalt")
for i in range(7): slab((-9 + i * 3, -9.8, .1), (1.4, .18, .03), "bulb")
# six cabins around the court, each with a garage and porch
spots = [(-7, 8.2, 0), (0, 8.2, 0), (7, 8.2, 0), (-9.6, -1, -math.pi / 2), (9.6, -1, math.pi / 2), (-7, -6.6, math.pi)]
for i, (x, y, rz) in enumerate(spots):
    c, s = math.cos(rz), math.sin(rz)
    def at(d, l, z=0): return (x + c * d - s * l, y + s * d + c * l, z)
    slab(at(0, 0, 0), (5.4, 3.6, 2.2), "plaster", rz); gable(at(0, 0, 2.2), 3.2, 2.1, 1.5, "roof")
    slab(at(0, -2.0, 0), (2.6, 1.0, .2), "wood", rz); slab(at(0, -2.6, 0), (1.2, .12, 1.7), "wood", rz)
    for lx in (-1.6, 1.6): slab(at(lx, -1.85, .9), (.9, .1, .9), "window", rz)
    gx, gy = at(0, 4.2, 0)
    slab((gx, gy, 0), (3.4, 3.0, 2.0), "wood", rz); gable((gx, gy, 2.0), 2.0, 1.7, 1.1, "roof")
    slab(at(0, 3.1, 0), (2.4, .15, 1.7), "tyre", rz)
    if i == 1:
        slab(at(0, -2.2, 2.4), (.9, .12, 1.6), "pink", rz); slab(at(0, -2.3, 3.0), (.5, .1, .5), "pink", rz)
        slab(at(0, -2.3, 3.5), (.3, .1, .3), "pink", rz)
        lamp("POINT", (1, .1, .45), 500, (x, y - 3.2, 3.2))
# swing on a post pair, neon sign on poles, a big shade tree
for sx in (-1, 1):
    slab((-2.5 + sx * 2.2, -3.5, 0), (.25, .25, 3.2), "wood"); slab((-2.5 + sx * 2.2, -3.5, 3.0), (.25, .25, .25), "wood")
slab((-2.5, -3.5, 3.1), (4.6, .2, .2), "wood")
for sx in (-.7, .7): slab((-2.5 + sx, -3.5, 2.1), (.05, .05, 1.0), "tyre")
slab((-2.5, -3.5, 2.0), (1.9, .6, .12), "wood")
for sx in (-1, 1): slab((5.5 + sx * 1.8, -5.0, 0), (.2, .2, 4.2), "wood")
slab((5.5, -5.0, 4.2), (4.4, .3, 2.4), "tyre"); slab((5.5, -5.2, 4.4), (3.6, .12, 1.8), "teal")
for i in range(5): slab((4.2 + i * .65, -5.3, 4.9), (.3, .1, .8), "teal", 0, .7)
lamp("POINT", (.1, 1, .8), 900, (5.5, -6.5, 5.0))
tube((12, 6, 0), .9, 5.5, 7, "trunk", .5)
for dx, dy, dz, r in ((0, 0, 6.5, 3.2), (-2.4, 0, 5.5, 2.2), (2.4, 0, 5.6, 2.2), (0, 2, 5.8, 2.0), (0, -2, 5.6, 2.0)): blob((12 + dx, 6 + dy, dz), r, "leaf" if r > 2.5 else "leaf2", (1, 1, .8))
# a 1930s car in the court and a vintage street lamp
cx, cy = -5.5, 2.0
slab((cx, cy, .6), (4.0, 1.8, .9), "car", .3, .85); slab((cx - .3, cy, 1.4), (2.2, 1.5, .8), "car", .3, .7)
for dx in (-1.4, 1.4):
    for dy in (-.95, .95):
        wx, wy = cx + dx * math.cos(.3) - dy * math.sin(.3), cy + dx * math.sin(.3) + dy * math.cos(.3)
        tube((wx, wy, .5), .5, .35, 7, "tyre", rot=(math.pi / 2, 0, .3))
slab((cx + 1.9, cy + .4, .9), (.2, 1.4, .5), "bulb", .3)
tube((-11, -8.5, 0), .12, 5, 5, "trunk2"); slab((-10.5, -8.5, 5.0), (1.0, .12, .12), "trunk2"); slab((-10.1, -8.5, 4.7), (.5, .5, .4), "bulb")
lamp("POINT", (1, .85, .5), 500, (-10.1, -8.5, 4.6))
# dusk: low orange key from the left, violet rim behind
lamp("SUN", (1, .5, .22), 5, (-26, -14, 9), (0, 0, 1)); lamp("SUN", (.5, .3, .9), 2, (22, 24, 10), (0, 0, 1))
w = bpy.data.worlds.new("dusk"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .012, .035, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((14, -66, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
