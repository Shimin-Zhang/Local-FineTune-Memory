import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(1210)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
S = bpy.context.scene
def dye(c, em=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = .8
    if em: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = em
    return m
oak, oak2, wall, sofa, cushion, rug1, rug2, lampm, shade, book1, book2, plant, pot, glass, tv, frame = (dye((.28, .16, .09)), dye((.2, .11, .06)), dye((.2, .17, .2)), dye((.12, .3, .32)), dye((.7, .55, .3)), dye((.45, .1, .1)), dye((.6, .5, .38)), dye((.1, .1, .12)), dye((1, .65, .3), 6), dye((.6, .15, .1)), dye((.15, .3, .5)), dye((.1, .35, .12)), dye((.4, .2, .12)), dye((.6, .75, .8)), dye((.02, .02, .03)), dye((.8, .65, .35)))
def add(bm, m, loc=(0, 0, 0), rz=0):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = loc; o.rotation_euler.z = rz
    S.collection.objects.link(o); o.data.materials.append(m); return o
def box(m, x, y, z, w, d, h, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = V((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return add(bm, m, (x, y, z), rz)
def cyl(m, x, y, z, r1, r2, h, n=7):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, (x, y, z))
def rod(m, a, b, r):
    a, b = V(a), V(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=r, radius2=r, depth=d.length)
    for v in bm.verts: v.co = q @ V((v.co.x, v.co.y, v.co.z + d.length / 2)) + a
    return add(bm, m)
def glow(c, w, p):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; S.collection.objects.link(o)
# floor slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=10.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
add(bm, oak2)
for i in range(10):
    box(oak if i % 2 else oak2, 0, -8.5 + i * 1.85, 0, 17, 1.8, .06)
# two walls: back and left, with a window on the back wall
box(wall, 0, 9.3, 0, 17, .8, 7.5); box(wall, -8.8, 0, 0, .8, 17, 7.5)
box(glass, 3.8, 8.85, 2.2, 4.6, .1, 3.2); box(oak2, 3.8, 8.8, 1.9, 5, .25, .2); box(oak2, 3.8, 8.8, 5.4, 5, .25, .2); box(oak2, 3.8, 8.8, 2.2, .2, .12, 3.2)
for i in range(3): box(oak2, -2.5 + i * 1.5, 8.8, 0, .3, .3, 7.5)
# rug with a border, and the sofa on it
box(rug1, 0, -.5, .06, 11, 7, .1); box(rug2, 0, -.5, .16, 9.4, 5.6, .05)
box(sofa, 0, 3.6, .5, 6.4, 2.2, 1.2, 0, .95); box(sofa, 0, 4.6, 1.5, 6.4, .6, 1.8, 0, .9)
for s in (-1, 1): box(sofa, s * 3.1, 3.6, 1.5, .7, 2.2, 1.0)
for i, c in enumerate((cushion, rug2, cushion)):
    box(c, -1.9 + i * 1.9, 3.3, 1.5, 1.8, 1.6, .5, 0, .9)
    box(c, -1.9 + i * 1.9, 4.3, 2.0, 1.7, .5, 1.1, 0, .85)
# coffee table with books and a vase
box(oak, 0, -.2, .85, 3.2, 1.6, .18)
for sx in (-1.4, 1.4):
    for sy in (-.6, .6): box(oak2, sx, -.2 + sy, 0, .18, .18, .85)
box(book1, -.6, -.2, 1.03, 1.0, .7, .12, .3); box(book2, -.5, -.2, 1.15, .9, .6, .1, -.2); cyl(glass, .8, -.3, 1.03, .22, .15, .6, 6); cyl(plant, .8, -.3, 1.6, .05, .05, .4, 4)
# floor lamp with a warm shade, and a side table with a plant
cyl(lampm, -5.2, 4.2, 0, .5, .3, .3, 6); rod(lampm, (-5.2, 4.2, .3), (-5.2, 4.2, 4.2), .08); cyl(shade, -5.2, 4.2, 4.0, .9, .6, 1.3, 8)
glow((1, .65, .3), 900, (-5.2, 3.6, 4.2))
cyl(oak, 5.2, 4.2, 0, .7, .7, 1.2, 7); cyl(pot, 5.2, 4.2, 1.2, .45, .35, .6, 6)
for k in range(5): rod(plant, (5.2, 4.2, 1.7), (5.2 + math.cos(k * 1.3) * .8, 4.2 + math.sin(k * 1.3) * .8, 2.5), .12)
# TV stand with a big screen, and a wall shelf with books and a framed picture
box(oak2, 4.5, 8.2, 0, 4.6, 1.0, 1.0); box(tv, 4.5, 8.0, 1.0, 3.8, .15, 2.2); box(glass, 4.5, 7.9, 1.3, 3.2, .05, 1.6)
box(oak2, -4.5, 8.7, 3.4, 4.4, .6, .15)
for i in range(7): box((book1, book2, cushion)[i % 3], -6.1 + i * .45, 8.7, 3.55, .3, .4, .8 + (i % 2) * .15)
box(frame, -1.2, 8.8, 3.6, 1.6, .12, 1.3)
# a window box with plants, and a small armchair by the window
box(oak2, 3.8, 8.4, 1.9, 4.6, .5, .15)
for i in range(4): cyl(plant, 2.4 + i * 1.0, 8.4, 2.0, .3, .1, .5, 5)
box(sofa, -6.2, 1.5, .5, 1.8, 1.8, 1.1, .5, .9); box(sofa, -6.9, 1.9, 1.5, .5, 1.8, 1.5, .5, .9); box(cushion, -5.8, 1.2, 1.5, 1.2, 1.2, .35, .5)
# moonlight from the window, cold rim from behind
for c, w, p in (((.5, .6, 1), 4, (20, -26, 11)), ((.4, .5, .9), 2, (-24, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; S.collection.objects.link(o)
    o.rotation_euler = (V((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
S.world = bpy.data.worlds.new("w"); S.world.use_nodes = True
next(n for n in S.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .012, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); S.collection.objects.link(co)
t = V((0, 1, 2.5)); co.location = t + V((10, -40, 24))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); S.camera = co
