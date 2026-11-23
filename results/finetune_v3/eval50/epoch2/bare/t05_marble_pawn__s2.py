import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1060)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def marble(c, e=0, r=.5, k=1.0):
    m = bpy.data.materials.new("m"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r; b.inputs["IOR"].default_value = k
    if e: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    return m
def stone_(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def disc(p, r0, r1, h, n, m, j=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r0, radius2=r1, depth=h)
    for v in bm.verts:
        v.co.z += h / 2
        if j: v.co += Vector((random.uniform(-j, j), random.uniform(-j, j), random.uniform(-j, j) * .5))
    return stone_(bm, m, p)
def bead(p, r, m, s=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    return stone_(bm, m, p)
def rod(a, b, r, n, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r * .9, depth=d.length)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return stone_(bm, m)
def glow(kind, c, w, p, aim=None):
    L = bpy.data.lights.new("g", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
white, vein, dark = marble((.72, .73, .76), 0, .22), marble((.3, .32, .38), 0, .3), marble((.1, .1, .12))
amber, gold, slate = marble((.3, .2, .12)), marble((.9, .65, .2), 0, .4), marble((.2, .2, .24))
under, halo, fire = marble((.02, .03, .06)), marble((.3, .8, 1), 14), marble((1, .55, .15), 20)
# board: octagonal plinth, then a 4x4 grid of squares, then the glowing slot ring under the pawn
disc((0, 0, -2.6), 3.4, 6.6, 2.6, 8, under, .45); disc((0, 0, -.2), 6.4, 6.4, .2, 8, dark)
for i in range(4):
    for j in range(4):
        x, y = (i - 1.5) * 1.9, (j - 1.5) * 1.9
        disc((x, y, 0), .95, .95, .12, 4, white if (i + j) % 2 else amber, 0).rotation_euler.z = math.pi / 4
disc((0, 0, .12), 1.65, 1.65, .04, 12, halo); disc((0, 0, .16), 1.3, 1.3, .04, 12, dark)
glow("POINT", (.3, .8, 1), 700, (0, 0, .8))
# the pawn: stepped plinth, tapered shaft with a turned neck, a collar, the head, a small crown finial
disc((0, 0, .16), 1.2, 1.0, .45, 8, white); disc((0, 0, .6), 1.0, .8, .15, 8, vein)
disc((0, 0, .75), .78, .5, 1.8, 8, white); disc((0, 0, 2.55), .5, .62, .35, 8, white)
disc((0, 0, 2.9), .62, .5, .12, 8, vein)
disc((0, 0, 3.02), .5, .3, .4, 8, white)
bead((0, 0, 4.0), .62, white, (1, 1, 1.05))
disc((0, 0, 4.6), .18, .05, .3, 6, gold)
# grey veins: thin dark strips laid on the shaft and head, each a tilted rod segment
for i in range(7):
    a = i * .9 + .2; z = .9 + i * .45
    p = Vector((math.cos(a) * .62, math.sin(a) * .62, z))
    q = Vector((math.cos(a + .5) * .5, math.sin(a + .5) * .5, z + .7))
    rod(p, q, .045, 4, vein)
for i in range(4):
    a = i * 1.6 + .4
    rod((math.cos(a) * .6, math.sin(a) * .6, 3.9), (math.cos(a + .7) * .45, math.sin(a + .7) * .45, 4.25), .04, 4, vein)
# the other pieces of the set, small and dark, on their squares
for x, y, h in ((-2.85, -2.85, 1.6), (-2.85, 2.85, 1.9), (2.85, -2.85, 1.4), (2.85, 2.85, 2.1)):
    disc((x, y, .12), .5, .35, .25, 6, slate); disc((x, y, .37), .3, .17, h, 6, slate)
    bead((x, y, .37 + h + .15), .26, slate)
# chessboard lamp: brass arm from the plinth, a hanging lantern that lights the board
rod((5.6, -3.2, 0), (5.6, -3.2, 5.2), .12, 5, gold); rod((5.6, -3.2, 5.2), (2.6, -.6, 5.2), .1, 5, gold)
rod((2.6, -.6, 5.2), (2.6, -.6, 4.2), .03, 4, gold)
disc((2.6, -.6, 3.2), .5, .3, 1.0, 6, fire); disc((2.6, -.6, 4.2), .3, .5, .3, 6, gold)
glow("POINT", (1, .55, .2), 1200, (2.6, -.6, 3.6))
# floating marble chips and dust around the plinth
for i in range(9):
    a = i * .7; r = random.uniform(4.5, 5.6)
    b = bmesh.new(); bmesh.ops.create_icosphere(b, subdivisions=1, radius=random.uniform(.15, .3))
    for v in b.verts: v.co *= random.uniform(.8, 1.2)
    stone_(b, white if i % 2 else vein, (math.cos(a) * r, math.sin(a) * r, random.uniform(1, 3.5)))
glow("SUN", (.6, .75, 1), 4.5, (-14, -10, 9), (0, 0, 2)); glow("SUN", (1, .6, .3), 2.2, (12, 14, 8), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2.2)); co.location = t + Vector((9, -30, 19))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
