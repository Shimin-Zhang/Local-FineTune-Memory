import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1329)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def tint(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow:
        n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    M[name] = m
for k, c in dict(grass=(.12, .2, .1), path=(.28, .26, .22), stone=(.3, .3, .3), slate=(.12, .14, .17), spoil=(.22, .23, .25),
                 spoil2=(.16, .17, .2), wall=(.35, .35, .33), oak=(.2, .12, .07), wool=(.7, .68, .62), face=(.1, .08, .07),
                 leaf=(.1, .22, .12), rain=(.6, .7, .85), dark=(.02, .02, .03)).items(): tint(k, c)
tint("window", (1, .65, .25), 12); tint("lamp", (1, .7, .3), 20)
def make(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def box(at, s, k, rz=0, peak=None):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
        if peak is not None and v.co.z > s[2] / 2: v.co.x *= peak
    return make(bm, k, at, (0, 0, rz))
def cone(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, k, at, rot)
def blob(at, r, k, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.15); v.co.z *= sq
    return make(bm, k, at)
def lit(kind, c, w, at, aim=None):
    d = bpy.data.lights.new("l", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("l", d); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# ground: a grassy slab, hillside rising at the back
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    v.co.z -= 2
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
make(bm, "grass")
for i in range(5):
    box((0, 7.5 + i * 1.1, 0), (17 - i * 2.2, 1.5, 1.0 + i * .9), "spoil" if i % 2 else "spoil2", 0, .96)
for i in range(14):
    blob((random.uniform(-9, 9), random.uniform(6, 12), 1.5 + random.uniform(0, 4.5)), random.uniform(.4, .9), "spoil2", .7)
# cottage: stone walls, slate roof with ridge, chimney, door, windows
cx, cy = -1, 1.5
box((cx, cy, 0), (8, 5, 3), "stone")
box((cx, cy, 3), (9.4, 6.4, 2.2), "slate", 0, .1)
box((cx, cy, 5.1), (9.4, .3, .3), "slate")
box((cx + 2.6, cy + .8, 3), (1.2, 1.2, 3.2), "stone"); box((cx + 2.6, cy + .8, 6.2), (1.5, 1.5, .3), "dark")
box((cx - 1.5, cy - 2.52, 0), (1.3, .15, 2.2), "oak")
for x in (-3.2, 1.2): box((x + cx, cy - 2.52, 1.2), (1.2, .12, 1.1), "window")
box((cx - 1.5, cy - 2.8, 2.4), (.5, .5, .5), "lamp")
box((cx, cy - 3.2, 0), (9, 1.4, .1), "path")
lit("POINT", (1, .65, .25), 500, (cx - 1.5, cy - 3.4, 2.4)); lit("POINT", (1, .65, .25), 300, (cx + 1.2, cy - 3.4, 1.8))
# walled yard: low dry-stone walls with a gate gap on the front
for x0, x1, y, h in ((-9, -5.2, -6.5, 1.1), (5.2, 9, -6.5, 1.1), (-9, 9, 8.2, 1.0), (-9, -9, -6.5, 1.1), (9, 9, -6.5, 1.1)):
    for i in range(int(abs(x1 - x0) + abs(y - (-6.5)) * 1.2) + 1):
        t = i / 12
        px, py = x0 + (x1 - x0) * t, y + (8.2 - y) * t if y < 8 else y
        if abs(x0 - x1) < .1: px, py = x0, -6.5 + (8.2 + 6.5) * t
        box((px, py, 0), (1.3, 1.1, h * random.uniform(.85, 1.1)), "wall", random.uniform(-.2, .2))
for sx in (-1, 1):
    box((-5.2 + sx * .5 + (sx > 0) * .0, -6.5, 0), (.4, .4, 1.8), "oak")
box((-5.2, -6.5, 1.8), (1.8, .4, .3), "oak")
box((-4.0, -6.5, 0), (1.6, .15, 1.4), "oak", .5)
# sheep trough, tree, and the ewe with her lamb by the gate
box((5, -4.5, 0), (2.4, .8, .6), "oak")
cone((-7, 5, 0), .3, 3, 5, "oak"); blob((-7, 5, 3.8), 1.8, "leaf", 1.1)
def sheep(x, y, s, rz):
    c, sn = math.cos(rz), math.sin(rz)
    def at(dx, dy, z): return (x + dx * c - dy * sn, y + dx * sn + dy * c, z)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.9 * s)
    for v in bm.verts: v.co.x *= 1.3; v.co.z *= .9
    make(bm, "wool", at(0, 0, 1.0 * s), (0, 0, rz))
    blob(at(.95 * s, 0, 1.25 * s), .38 * s, "face", 1)
    for dx in (-.5, .5):
        for dy in (-.35, .35): box(at(dx * s, dy * s, 0), (.18 * s, .18 * s, .7 * s), "face")
    blob(at(1.0 * s, .45 * s, 1.6 * s), .12 * s, "face", 1)
sheep(-3.2, -7.6, 1.3, .4); sheep(-1.6, -7.0, .75, 1.1)
# drizzle: pale slanted streaks over the whole scene
for i in range(70):
    x, y, z = random.uniform(-11, 11), random.uniform(-9, 11), random.uniform(1, 12)
    box((x, y, z), (.04, .04, 1.1), "rain", 0).rotation_euler = (.2, .1, 0)
lit("SUN", (.55, .65, .8), 4, (-26, -14, 9), (0, 0, 2)); lit("SUN", (.7, .65, .8), 2, (22, 20, 12), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((14, -52, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
