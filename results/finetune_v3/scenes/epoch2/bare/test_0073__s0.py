import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1375)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def clay(rgb, em=0, rough=.95):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
sand, brick, brick2, brick3, brick4, grass, canvas, canvas2, timber, dark, lamp = (clay(c) for c in (
    (.3, .22, .12), (.4, .26, .15), (.32, .2, .12), (.24, .16, .1), (.17, .12, .08), (.18, .22, .08), (.5, .42, .3), (.4, .1, .08), (.2, .12, .07), (.02, .02, .02), (1, .7, .3)))
lamp = clay((1, .7, .3), 14)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def wall(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def cone(at, r, h, n, m, r2=0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def glim(at, w):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = (1, .65, .25), w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=15, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .2)))
make(bm, sand)
# the mound: four stacked terraces, flat top, each a little smaller
for k, (r, h) in enumerate(((9, 2.2), (7.6, 2.0), (6.0, 1.8), (4.2, 1.6))):
    cone((0, 0, 0), r, h, 9, (brick, brick2, brick3, brick4)[k], r * .96, (0, 0, k * .35))
for k in range(4): wall((0, 0, 0), (0, 0, 0), brick)
# the stepped trench: a cut down the front face of the mound, terraces each showing a different layer
for i, (y, z, h) in enumerate(((-1.5, 0, 1.0), (-.5, 1.0, 1.0), (.5, 2.0, 1.0), (1.5, 3.0, 1.0))):
    wall((0, y, z), (7.0, 1.0, h), (brick4, brick3, brick2, brick)[i])
# mud-brick wall courses inside the cut: rows of little blocks in alternating shades, some missing
for i in range(4):
    for row in range(3):
        for c in range(11):
            if random.random() < .12: continue
            wall((-3.0 + c * .62 + (row % 2) * .3, -1.5 + i * 1.0, 1.0 + i * 1.0 + row * .33), (.55, .95, .3), (brick, brick2, brick3)[(row + c + i) % 3])
wall((0, -2.0, 0), (7.2, .1, .1), dark)
# a stair up the trench and the dig house with lit windows
for k in range(6): wall((4.6, -1.5 + k * .6, 0), (1.4, .6, .35 * (k + 1)), brick2)
wall((7.5, -3.5, 0), (4.2, 3.0, 2.2), canvas); wall((7.5, -3.5, 2.2), (4.8, 3.6, .3), timber)
wall((5.35, -3.5, .8), (.1, 1.0, 1.0), lamp); wall((9.65, -3.5, .8), (.1, 1.0, 1.0), lamp); wall((7.5, -5.05, 0), (1.0, .1, 1.5), dark)
glim((5.0, -3.5, 1.2), 400); glim((10.0, -3.5, 1.2), 400)
# tents: a big ridge tent and two small ones, with guy lines
def tent(x, y, w, d, h, m, rz=0):
    bm = bmesh.new(); a = [bm.verts.new(p) for p in ((-w, -d, 0), (w, -d, 0), (w, d, 0), (-w, d, 0), (0, -d, h), (0, d, h))]
    for f in ((0, 1, 4), (2, 3, 5), (1, 2, 5, 4), (3, 0, 4, 5), (3, 2, 1, 0)): bm.faces.new([a[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); make(bm, m, (x, y, 0), (0, 0, rz))
tent(-7.5, -4, 2.2, 1.8, 2.0, canvas, .3); tent(-3.5, -6.5, 1.6, 1.4, 1.6, canvas2, -.2); tent(10.5, 2, 1.8, 1.5, 1.7, canvas, 1.2)
wall((-7.5, -4.6, 0), (.8, .1, 1.2), lamp); glim((-7.5, -5.2, 1.0), 300)
# excavation grid stakes, a wheelbarrow, spoil heaps, a sieve, a flag
for i in range(5):
    for j in range(3): wall((-2.5 + i * 1.2, -5.2 - j * 1.0, 0), (.08, .08, .6), timber)
wall((.5, -6.5, .4), (1.0, .7, .5), canvas2); cone((.5, -6.5, .4), .3, .1, 6, timber, .3, (0, math.pi / 2, 0))
for x, y, r in ((-10, 2, 1.6), (-8.5, 5, 1.2), (9, 7, 1.4)):
    cone((x, y, 0), r, r * .8, 6, brick2, r * .3)
wall((-1, 5, 0), (.1, .1, 3.0), timber); wall((-.5, 5, 2.4), (.9, .05, .5), canvas2)
# a few dry shrubs and stones on the plain
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(11, 14)
    cone((math.cos(a) * r, math.sin(a) * r, 0), random.uniform(.2, .5), random.uniform(.4, .8), 5, grass, .05)
for col, w, p in (((1, .5, .22), 6, (-24, 12, 8)), ((.3, .45, .9), 2.2, (22, -20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = col, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.5)); co.location = t + Vector((12, -62, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
