import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1594)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
H = {}
def alloy(name, rgb, glow=0, metal=0, rough=.6):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    H[name] = m
for k, v in dict(deck=(.12, .13, .15), deck2=(.08, .09, .11), wall=(.17, .19, .22), wall2=(.1, .11, .14), hull=(.5, .52, .56), hull2=(.3, .32, .38),
                 red=(.55, .08, .06), black=(.02, .02, .03), rail=(.3, .32, .36), hose=(.7, .35, .05), hose2=(.1, .35, .5), skin=(.55, .35, .25),
                 suit=(.1, .15, .35), cap=(.12, .13, .16), white=(.7, .72, .75)).items(): alloy(k, v)
alloy("amber", (1, .6, .15), 12); alloy("cyan", (.2, .9, 1), 12); alloy("engine", (1, .5, .1), 14); alloy("strip", (.1, .8, 1), 6)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(H[k]); return o
def blk(at, d, k, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * d[0] * f, v.co.y * d[1] * f, (v.co.z + .5) * d[2]))
    return mk(bm, k, at, (0, 0, rz))
def cyl(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at, rot)
def beam(a, b, t, k):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, k)
def lamp(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# deck slab
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 20, v.co.y * 17, -3)) + Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, .3)))
    else: v.co = Vector((v.co.x * 26, v.co.y * 22, -3))
mk(bm, "deck2")
for i in range(13): blk((0, -10 + i * 1.7, 0), (26, .9, .06), "deck" if i % 2 else "deck2")
# hangar shell: back wall, left wall, ribs, trusses
blk((0, 10.4, 0), (26, .8, 10), "wall"); blk((-12.6, 0, 0), (.8, 21, 10), "wall2")
for x in (-10, -5, 0, 5, 10):
    blk((x, 10, 0), (.5, .6, 10), "wall2"); blk((x, 10, 8.6), (1.2, .8, .5), "wall2")
for z in (3, 6, 9): blk((0, 10, z), (25, .3, .25), "wall2"); blk((-12.4, 0, z), (.3, 20, .25), "wall2")
blk((-12.4, 9.6, 0), (.3, .3, 10), "wall2")
for x in (-10, 0, 10): beam((x, 9.6, 9), (x, 9.6, 9), .1, "rail")
for x in (-10, 0, 10):
    beam((x, 9.6, 9), (x, 9.6, 9), .1, "rail"); beam((-12.2, 9.6, 9), (x, 9.6, 9), .2, "rail")
for i in range(5): blk((-12.4, -9 + i * 4.5, 0), (.3, .3, 9), "rail")
# two fighters on cradles
for fx, fy, rz in ((-6.5, 3, .2), (6.5, 3, -.2)):
    c, s = math.cos(rz), math.sin(rz)
    def at(x, y, z): return (fx + x * c - y * s, fy + x * s + y * c, z)
    for x in (-2.4, 0, 2.4): blk(at(x, 0, 0), (.6, 1.6, .5), "black", rz)
    for x in (-2.4, 0, 2.4): beam(at(x, -.8, .5), at(x, -.8, 1.1), .12, "rail"); beam(at(x, .8, .5), at(x, .8, 1.1), .12, "rail")
    cyl(at(0, 0, 1.1), 1.3, 6, 7, "hull", 0.6, (0, math.pi / 2, rz))
    for sy in (-1, 1):
        blk(at(-.5, sy * 2.0, 1.6), (2.4, 2.2, .15), "hull2", rz); blk(at(-.5, sy * 1.0, 2.6), (.1, 1.4, .15), "hull2", rz)
        cyl(at(2.2, sy * 1.0, 1.4), .55, 1.0, 6, "black", .5, (0, math.pi / 2, rz)); cyl(at(2.8, sy * 1.0, 1.4), .5, .12, 6, "engine", rot=(0, math.pi / 2, rz))
    blk(at(-1.4, 0, 2.4), (1.4, .5, .5), "red", rz); blk(at(0, 0, 2.4), (.6, .6, .3), "cyan", rz)
    lamp((1, .5, .1), 250, at(3.4, 0, 1.4))
# fuel hoses from a manifold on the left wall
for i in range(3):
    y = -3 + i * 3.4
    cyl((-12.2, y, 2.5), .35, .5, 6, "rail", rot=(0, math.pi / 2, 0))
    for j in range(4):
        t = j / 3; beam((-11.8 + t * 1.4, y + math.sin(t * 5) * .4, 2.5 - t * 1.5), (-11.8 + (t + .33) * 1.4, y + math.sin((t + .33) * 5) * .4, 2.5 - (t + .33) * 1.5), .13, "hose" if i % 2 else "hose2")
    beam((-10.4, y, 1.0), (-9.8, y, .8), .1, "rail")
# launch rail down the deck
blk((0, -8.2, 0), (24, 1.6, .12), "rail"); blk((0, -8.2, .12), (23, .2, .12), "strip"); blk((0, -8.2, .24), (23, .1, .1), "amber")
for x in range(-11, 12, 2): blk((x, -8.2, 0), (.3, 1.8, .1), "black")
for x in (-11, 11):
    blk((x, -8.2, .1), (.4, 1.4, 1.6), "red", top=.7); blk((x, -8.2, 1.7), (.6, .6, .4), "amber")
lamp((1, .6, .15), 400, (0, -8.2, 1.2))
# deck officer with glowing wands
ox, oy = 2.5, -5.2
cyl((ox, oy, 0), .45, 1.3, 6, "suit", .32); cyl((ox, oy, 1.3), .26, .5, 6, "skin"); cyl((ox, oy, 1.75), .3, .22, 6, "cap")
beam((ox - .3, oy, 1.1), (ox - .8, oy - .3, 1.9), .13, "suit"); beam((ox + .3, oy, 1.1), (ox + .8, oy - .3, 1.9), .13, "suit")
blk((ox - .8, oy - .3, 1.9), (.22, .22, .22), "amber"); blk((ox + .8, oy - .3, 1.9), (.22, .22, .22), "cyan")
lamp((1, .6, .15), 120, (ox - .8, oy - .6, 2.1)); lamp((.2, .9, 1), 120, (ox + .8, oy - .6, 2.1))
# crates and a console
for i in range(3): blk((-10 + i * 1.3, 7.5, 0), (1.1, 1.1, 1.0 + i * .3), "red" if i == 1 else "hull2")
blk((10.5, 7.5, 0), (2.2, 1.0, 1.2), "rail"); blk((10.5, 7.0, 1.2), (1.8, .1, .8), "cyan"); lamp((.2, .9, 1), 150, (10.5, 6.4, 1.8))
for c, w, p in (((.55, .75, 1), 5, (22, -16, 9)), ((.9, .4, .5), 2, (-22, 18, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("hangar"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .012, .025, 1)
cm = bpy.data.cameras.new("cam"); cm.lens = 80
co = bpy.data.objects.new("cam", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 3)); co.location = tg + Vector((8, -62, 36))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
