import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1216)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def dye(r, g, b, e=0, ro=.9):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = p.inputs["Emission Color"].default_value = (r, g, b, 1)
    p.inputs["Roughness"].default_value = ro; p.inputs["Emission Strength"].default_value = e
    return m
oak, oak2, wall, wall2 = dye(.3, .18, .1), dye(.22, .13, .07), dye(.2, .22, .3), dye(.14, .15, .22)
bed, quilt, quilt2, rug = dye(.55, .5, .45), dye(.5, .12, .15), dye(.15, .25, .4), dye(.4, .1, .2)
rug2, shade, bulb, glass = dye(.55, .3, .2), dye(.9, .75, .5), dye(1, .75, .4, 20), dye(.3, .5, .7, 3)
plant, pot, frame, moon = dye(.1, .3, .12), dye(.5, .25, .15), dye(.6, .45, .2), dye(.8, .9, 1, 6)
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def lamp(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 15, v.co.y * 13, v.co.z * 2.4 - 1.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .7 + random.uniform(-.8, .8), v.co.y * .7 + random.uniform(-.8, .8), v.co.z - random.uniform(0, 1.6)))
make(bm, oak2)
for i in range(15): box((-7 + i, 0, 0), (.98, 12.8, .12), oak if i % 2 else oak2)
# two walls: back wall with a window, left wall with a shelf and a picture
box((0, 6.4, 0), (15, .5, 8)); box((-7.4, 0, 0), (.5, 12.8, 8))
box((0, 6.1, 0), (15, .2, 1.2), wall2); box((-7.1, 0, 0), (.2, 12.8, 1.2), wall2)
box((-3.5, 6.1, 2.2), (4.2, .2, 4.2), glass); box((-3.5, 6.0, 2.2), (4.4, .3, .2), frame); box((-3.5, 6.0, 6.4), (4.4, .3, .2), frame)
box((-3.5, 6.0, 4.3), (.15, .3, 4.2), frame); box((-3.5, 6.0, 4.3), (4.2, .3, .15), frame)
box((-3.5, 6.2, 2.0), (4.8, .8, .2), frame)
box((-1.6, 6.15, 5.2), (.7, .06, .7), moon)
box((-7.1, 1.5, 4.4), (.9, 3.2, .15), frame); box((-7.1, 1.5, 4.55), (.5, .5, .5), pot)
box((-7.0, 3.2, 3.4), (.1, 1.6, 1.4), quilt2); box((-7.0, 3.2, 3.5), (.05, 1.2, 1.0), quilt)
# the bed: frame, headboard, mattress, quilt folded at the foot, two pillows
bx, by = 2.2, 1.0
box((bx, by, 0), (5.4, 3.8, .5), oak); box((bx, by + 1.8, .5), (5.4, .3, 2.6), oak)
box((bx, by, .5), (5.0, 3.4, .6), bed)
box((bx, by - .4, 1.1), (5.0, 2.6, .35), quilt); box((bx, by + 1.2, 1.1), (5.0, .9, .4), quilt2)
for dx in (-1.4, 1.4): box((bx + dx, by + 1.0, 1.1), (1.8, .8, .5), bed)
# nightstand with lamp, and a book stack
box((5.4, 4.0, 0), (1.6, 1.6, 1.6), oak2); box((5.4, 3.1, .8), (.9, .1, .5), oak)
cyl((5.4, 4.0, 1.6), .12, 1.0, 6, oak2); cyl((5.4, 4.0, 2.6), .55, .8, 8, shade, .35)
cyl((5.4, 4.0, 2.5), .2, .3, 6, bulb)
for i in range(3): box((5.0, 3.5, 1.6 + i * .18), (.9, .6, .15), quilt if i % 2 else quilt2, (0, 0, i * .2))
lamp((5.4, 4.0, 2.8), (1, .7, .35), 450)
# wardrobe with doors, handles and a top
box((-5.2, 4.2, 0), (4.4, 1.8, 6.2), oak2)
for s in (-1, 1): box((-5.2 + s * 1.1, 3.25, .2), (2.0, .1, 5.8), oak); cyl((-5.2 + s * .1, 3.15, 3.0), .1, .1, 5, frame, rot=(1.57, 0, 0))
box((-5.2, 4.2, 6.2), (4.8, 2.0, .25), oak)
# rug with a border, a chair, a plant and a small table by the window
for r, m in ((2.8, rug2), (2.3, rug), (1.4, rug2)): cyl((-1.0, -1.8, .1), r, .06, 10, m)
cyl((.8, 3.4, .1), .7, .5, 7, quilt2); cyl((.8, 3.4, .6), .9, .5, 7, quilt2, .7)
box((.8, 3.4, 1.1), (1.6, .1, 1.2), quilt2)
cyl((5.0, -3.0, 0), .2, 1.0, 6, pot, .3); cyl((5.0, -3.0, 1.0), .8, .3, 7, plant, .1)
cyl((5.0, -3.0, 1.0), .1, 1.4, 5, plant)
for i in range(4): cyl((5.0, -3.0, 1.2), .5 - i * .1, .5, 5, plant, .05, (i * .8, 0, i * 1.2))
lamp((-3.5, 5.2, 4.5), (.5, .7, 1), 300)
# moonlit night: cool moon from the window side, warm lamp glow
for c, e, p in (((.5, .65, 1), 4, (-26, -14, 12)), ((.9, .5, .7), 1.8, (20, 24, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((20, -44, 32))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
