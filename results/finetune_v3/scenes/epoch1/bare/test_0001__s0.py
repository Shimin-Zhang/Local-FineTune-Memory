import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1324)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(rgb, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
dirt, rockm, hill, plank, plank2, roof, rust, coal, snow, dead, fog, win = (paint((.13, .1, .08)), paint((.2, .18, .17)), paint((.22, .17, .12)), paint((.22, .15, .1)), paint((.16, .11, .08)),
    paint((.1, .09, .1)), paint((.4, .15, .06)), paint((.03, .03, .035)), paint((.55, .6, .68)), paint((.25, .18, .12)), paint((.4, .5, .62), .3), paint((.9, .75, .35), 2))
def add(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return add(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, at, rot)
def limb(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return add(bm, m)
def lamp(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# base: rough rock slab, winding dirt road on top
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    v.co.x *= 1.15
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    v.co.z -= 2
add(bm, rockm)
pts = [Vector((-2 + 2.2 * math.sin(i * .45), -10 + i * 1.9, 0)) for i in range(12)]
for a, b in zip(pts, pts[1:]): blk(((a + b) / 2).to_tuple(), (2.4, 2.6, .1), dirt, (0, 0, math.atan2(b.x - a.x, b.y - a.y)))
# bare hillside behind: stacked eroded cones, scree, a few dead scrub
for i in range(9):
    a = random.uniform(2.0, 5.4); r = random.uniform(7, 11); h = random.uniform(3, 6.5)
    cyl((math.cos(a) * r, math.sin(a) * r, 0), random.uniform(2.4, 3.6), h, 7, hill, r2=random.uniform(.6, 1.2))
    for k in range(3): blk((math.cos(a) * r + random.uniform(-1, 1), math.sin(a) * r + random.uniform(-1, 1), random.uniform(.5, 1.5)), (1.2, 1, .6), rockm, (0, 0, k))
for i in range(16): blk((random.uniform(-11, 11), random.uniform(-9, 9), .05), (random.uniform(.6, 1.2), random.uniform(.6, 1.2), .2), rockm, (0, 0, random.random()))
# cabins: shuttered, sagging roofs, some leaning, a few with a lit window
for x, y, rot, lean in ((-8, 1, .2, .06), (-4.5, 4.5, -.3, -.05), (4.5, 5.5, .4, .08), (8, 1.5, -.2, -.07), (-7, 8, .1, .05), (6, 9, -.4, .06)):
    blk((x, y, 0), (4.2, 3.2, 2.6), plank, (lean, 0, rot))
    blk((x, y, 2.5), (4.8, 3.8, .3), roof, (lean * 2, 0, rot)).rotation_euler.x += .08 * (1 if rot > 0 else -1)
    for k in range(4):
        sx = -1.4 + k * .95
        blk((x + sx * math.cos(rot) - y * 0, y - 1.65 * math.cos(rot) - sx * math.sin(rot) * 0, 1.0), (.7, .1, 1.2), plank2, (0, 0, rot))
        blk((x + sx, y - 1.7, 1.0), (.06, .06, 1.2), plank2, (0, 0, rot))
    blk((x + 1.5 * math.cos(rot), y - 1.65 * math.cos(rot), 0), (.9, .12, 1.8), plank2, (0, 0, rot))
    if (x, y) in ((-4.5, 4.5), (6, 9)):
        blk((x - 1.2, y - 1.72, 1.4), (.8, .1, .8), win, (0, 0, rot)); lamp((.9, .75, .35), 260, (x - 1.2, y - 2.4, 1.6))
# company store with a fallen sign
blk((0, 9.5, 0), (7, 4.2, 3.4), plank2)
blk((0, 9.5, 3.4), (7.8, 4.8, .35), roof, (0, .05, 0))
blk((0, 7.3, 0), (2.4, .12, 2.4), plank)
for sx in (-2.4, 2.4): blk((sx, 7.35, 1.2), (1.2, .1, 1.0), win)
lamp((.9, .75, .35), 420, (0, 6.4, 1.5))
blk((-1.5, 7.0, 4.4), (3.6, .12, 1.0), plank)
blk((5.2, 4.6, .12), (3.6, 1.0, .12), plank, (0, 0, .5))
for sx in (-1, 1): blk((5.2 + sx * 1.6 * math.cos(.5), 4.6 + sx * 1.6 * math.sin(.5), .12), (.12, .12, 1.2), dead, (.1, 0, .5))
# rusted ore cart on rails with a pile of coal
for s in (-.5, .5): limb((-12, -2, .35), (-4, -2, .35), .12, dead)
for i in range(8): blk((-11 + i * 1.1, -2, .2), (.15, 1.6, .1), plank2)
cx, cy = -8, -2
blk((cx, cy, .6), (2.6, 1.7, .9), rust, (0, 0, 0))
blk((cx, cy, 1.5), (2.7, 1.8, .12), rust)
for s in (-1, 1):
    for sx in (-1, 1): cyl((cx + sx * .9, cy + s * 1.0, .35), .35, .12, 8, coal, rot=(math.pi / 2, 0, 0))
for i in range(5): cyl((cx + random.uniform(-.8, .8), cy + random.uniform(-.5, .5), 1.5), random.uniform(.2, .35), .5, 5, coal, r2=.1)
cyl((cx + 1.7, cy, .5), .12, 1.0, 5, dead, rot=(0, math.pi / 2, 0))
# snow drifts and fog patches
for i in range(10):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(.5, 1.0))
    for v in bm.verts: v.co.z *= .4
    add(bm, snow, (random.uniform(-11, 11), random.uniform(-9, 9), .1))
for i in range(4):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=random.uniform(1.2, 1.8))
    for v in bm.verts: v.co.z *= .25
    add(bm, fog, (random.uniform(-9, 9), random.uniform(-8, 8), .3))
# cold moonlit night: steel key from the left, violet rim behind
for c, w, at in (((.55, .65, .9), 4.5, (-26, -18, 12)), ((.6, .4, .9), 2, (22, 26, 14))):
    s = bpy.data.lights.new("s", "SUN"); s.color, s.energy = c, w
    o = bpy.data.objects.new("s", s); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("n"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .02, .035, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
tg = Vector((0, 2, 2)); co.location = tg + Vector((10, -60, 38))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
