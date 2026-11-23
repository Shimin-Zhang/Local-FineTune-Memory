import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1165)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def board(r, g, b, e=0):
    m = bpy.data.materials.new("b"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (r, g, b, 1); p.inputs["Roughness"].default_value = .5
    if e: p.inputs["Emission Color"].default_value = (r, g, b, 1); p.inputs["Emission Strength"].default_value = e
    return m
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def lathe(at, m, prof, n=8):
    bm = bmesh.new(); rings = []
    for r, z in prof: rings.append([bm.verts.new((r * math.cos(k * 6.2832 / n), r * math.sin(k * 6.2832 / n), z)) for k in range(n)])
    for a, b in zip(rings, rings[1:]):
        for k in range(n): bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return mk(bm, m, at)
def blk(at, m, w, d, h, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mk(bm, m, at, (0, 0, rz))
def lit(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
ivory, ebony, gold = board(.7, .65, .55), board(.05, .045, .05), board(.6, .42, .1)
felt, felt2, wood, glow = board(.04, .13, .1), board(.06, .17, .13), board(.22, .12, .07), board(1, .6, .2, 5)
# floating base: a cutaway of the board's corner, rough underside, felt top with a glowing inlay line
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co = Vector((v.co.x * 13 + random.uniform(-1, 1), v.co.y * 13 + random.uniform(-1, 1), -3.4 + random.uniform(-.8, .4)))
    else: v.co = Vector((v.co.x * 17, v.co.y * 17, 0))
mk(bm, wood)
blk((0, 0, 0), felt, 17, 17, .5); blk((0, 0, .5), glow, 17.2, .25, .05); blk((0, 0, .5), glow, .25, 17.2, .05)
for i in range(4):
    for j in range(4): blk((-6 + i * 4, -6 + j * 4, .5), felt2 if (i + j) % 2 else felt, 4, 4, .12)
# the king: eight-sided turnings, a cross and a ring, all oversized
lathe((0, 0, .6), ivory, [(4.4, 0), (3.4, .5), (2.4, 1.1), (2.0, 1.5)], 8)
lathe((0, 0, 1.5), gold, [(2.1, 0), (1.7, .4), (1.9, .8)], 8)
lathe((0, 0, 2.3), ivory, [(1.7, 0), (1.2, 3.5), (1.1, 6.0), (1.4, 6.6), (1.0, 7.2)], 8)
lathe((0, 0, 7.2), gold, [(1.1, 0), (1.3, .5), (1.0, 1.0)], 8)
lathe((0, 0, 8.2), ivory, [(1.0, 0), (.9, 2.2), (.5, 3.0), (.9, 3.4)], 8)
blk((0, 0, 11.6), gold, .7, .7, 2.8); blk((0, 0, 12.8), gold, 2.4, .7, .7)
# neighbouring pieces, slightly out of focus: rook, knight, pawn, a toppled bishop
lathe((-7, -2, .6), ebony, [(2.4, 0), (2.0, .4), (1.5, 2.0), (1.3, 3.0), (1.7, 3.4), (1.7, 4.2), (1.3, 4.2)], 8)
lathe((-3.5, 4, .6), ebony, [(2.0, 0), (1.5, .4), (1.0, 2.4), (1.0, 3.0), (.5, 3.6)], 7)
lathe((6, 3, .6), ivory, [(2.2, 0), (1.7, .4), (1.2, 1.4), (1.0, 2.0), (.8, 2.4), (1.3, 3.0), (.7, 3.4)], 7)
lathe((3.5, -4.5, .6), ivory, [(1.9, 0), (1.6, .3), (1.2, 1.4), (1.2, 2.0), (.5, 2.6)], 7, (1.57, 0, .5))
lathe((-1, -6.5, .6), ebony, [(1.9, 0), (1.5, .3), (1.1, 1.3), (.7, 1.8), (1.1, 2.3), (.6, 2.7)], 7)
# a candle in a brass holder, the warm key of the scene
lathe((7, -5, .6), gold, [(1.5, 0), (1.2, .3), (1.4, .7), (1.1, 1.0)], 8)
lathe((7, -5, 1.6), ivory, [(.5, 0), (.5, 2.4), (.4, 2.6)], 6); lathe((7, -5, 4.2), glow, [(.4, 0), (.3, .6), (.1, 1.0)], 5)
lit("POINT", (1, .6, .2), 1400, (7, -5, 5.4)); lit("POINT", (1, .6, .2), 300, (0, 0, 1))
lit("SUN", (1, .7, .4), 5, (-22, -16, 11), (0, 0, 4)); lit("SUN", (.3, .4, 1), 2, (20, 18, 10), (0, 0, 4))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .012, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 5)); co.location = t + Vector((12, -62, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
co.data.dof.use_dof = True; co.data.dof.focus_distance = (t - co.location).length; co.data.dof.aperture_fstop = 1.4
