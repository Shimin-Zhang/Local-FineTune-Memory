import bpy, bmesh, math, random
from mathutils import Vector
random.seed(815)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
sea, shore, plank, rope, white, red, thatch, dark, buoy, lamp, hull, sail, win = (pigment((.05, .2, .22)), pigment((.3, .24, .16)), pigment((.4, .25, .12)),
    pigment((.55, .45, .25)), pigment((.6, .6, .55)), pigment((.6, .1, .08)), pigment((.5, .38, .15)), pigment((.1, .08, .07)), pigment((.9, .15, .05)),
    pigment((1, .7, .25), 14), pigment((.1, .3, .4)), pigment((.7, .65, .5)), pigment((1, .75, .35), 10))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def rod(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return mk(bm, m)
def post(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at)
def gable(at, w, d, h, m):
    bm = bmesh.new()
    a = [bm.verts.new(p) for p in ((-w, -d, 0), (w, -d, 0), (w, d, 0), (-w, d, 0), (0, -d, h), (0, d, h))]
    for f in ((0, 1, 2, 3), (0, 1, 4), (2, 3, 5), (1, 2, 5, 4), (3, 0, 4, 5)): bm.faces.new([a[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mk(bm, m, at)
def bulb(at, rgb, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=15, depth=3.2)
for v in bm.verts:
    v.co.z -= 1.6
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .2)))
mk(bm, sea)
# the shore: a raised bank along the back with a small beach
bank = bmesh.new(); bmesh.ops.create_cone(bank, cap_ends=True, segments=8, radius1=15, radius2=14.5, depth=1.0)
for v in bank.verts:
    v.co.y = v.co.y * .45 + 9.5
    if v.co.y > 11: v.co.z += random.uniform(0, .3)
mk(bank, shore, (0, 0, -.2))
# village: whitewashed houses with tiled roofs and lit windows, church tower
for i, (x, y, w, d) in enumerate(((-9, 10.5, 3, 2.6), (-5.2, 10.8, 2.6, 2.4), (-1.5, 10.4, 3, 2.6), (2.5, 10.8, 2.6, 2.4), (6.5, 10.5, 3, 2.6))):
    cube((x, y, 0), (w, d, 2.0), white)
    gable((x, y, 2.0), w / 2 + .2, d / 2 + .2, 1.3, red if i % 2 else thatch).rotation_euler.z = math.pi / 2
    cube((x, y - d / 2 - .02, 1.0), (.7, .06, .7), win)
    bulb((x, y - d / 2 - .8, 1.4), (1, .65, .25), 110)
cube((9.5, 10.5, 0), (2.2, 2.2, 4.5), white); gable((9.5, 10.5, 4.5), 1.6, 1.6, 1.6, red).rotation_euler.z = math.pi / 4
cube((9.5, 9.35, 2.8), (.5, .06, .8), win); bulb((9.5, 8.8, 3.2), (1, .7, .3), 150)
# a little pier with a lamp post and moored buoy
for k in range(6): cube((-12 + k * .9, 7.2 - k * .1, .05), (.7, 1.2, .25), plank)
post((-11.4, 7.0, .3), .1, 2.2, 5, dark); cube((-11.4, 7.0, 2.5), (.4, .4, .4), lamp); bulb((-11.4, 7.0, 2.7), (1, .7, .3), 220)
# mussel rafts: three rows of float drums with hanging ropes and mussel bags
for r, y in enumerate((-6, -1.5, 3)):
    for k in range(7):
        x = -9 + k * 3 + (r % 2) * 1.5
        post((x, y, -.2), .55, .5, 7, plank, .5); post((x + 1.5, y, -.2), .55, .5, 7, plank, .5)
        rod((x, y, .1), (x + 1.5, y, .1), .12, plank)
        for s in (-.3, .3): rod((x + 1.5, y + s, .1), (x + 1.5, y + s, -2.0), .05, rope)
        cube((x + 1.5, y, -2.3), (.7, .8, .5), dark)
    rod((-9, y, .1), (9 + (r % 2) * 1.5, y, .1), .14, plank)
    post((10.5 + (r % 2) * 1.5, y, -.3), .35, .8, 6, buoy, .25); bulb((10.5 + (r % 2) * 1.5, y, .6), (1, .2, .05), 60)
# workboat with a lifting crane: hull, deck, cabin, mast, boom, cable and basket
hx, hy = 1, -9.5
hull = bmesh.new(); bmesh.ops.create_cube(hull, size=1)
for v in hull.verts:
    v.co = Vector((v.co.x * 6, v.co.y * 2.2, (v.co.z + .5) * 1.0))
    if v.co.x > 0 and v.co.z > .5: v.co.y *= .15
    if v.co.x > 0: v.co.z += .3 * (v.co.x / 3)
mk(hull, hull, (hx, hy, -.3))
cube((hx - 1.5, hy, .7), (1.8, 1.8, 1.2), white); cube((hx - 1.5, hy - .92, 1.2), (1.0, .06, .5), win)
bulb((hx - 1.5, hy - 1.6, 1.4), (1, .7, .3), 120)
rod((hx + 1.5, hy, .7), (hx + 1.5, hy, 3.4), .2, plank); rod((hx + 1.5, hy, 3.4), (hx + 3.8, hy, 4.4), .15, red)
rod((hx + 3.8, hy, 4.4), (hx + 3.8, hy, 1.2), .05, rope); cube((hx + 3.8, hy, .8), (.9, .9, .5), red)
rod((hx + 1.5, hy, 3.4), (hx + 3.8, hy, 4.4), .05, rope)
# light: cold moon-blue key low from the left, warm rim from behind the village
for rgb, w, p in (((.5, .65, 1), 4.5, (-28, -14, 11)), ((1, .6, .35), 2, (20, 26, 14))):
    s = bpy.data.lights.new("s", "SUN"); s.color = rgb; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 0)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); co.location = (10, -60, 38)
co.rotation_euler = (Vector((0, 2, 1)) - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
