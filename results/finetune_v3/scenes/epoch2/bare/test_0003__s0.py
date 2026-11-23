import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1096)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def paint(name, rgb, glow=0, rough=.9):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow:
        n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    M[name] = m
for k, c in dict(snow=(.5, .56, .7), drift=(.62, .68, .8), timber=(.28, .16, .09), roof=(.12, .13, .16), pad=(.2, .22, .26),
                 heli=(.75, .1, .05), heli2=(.08, .09, .11), glass=(.05, .1, .15), steel=(.4, .42, .46), pine=(.04, .16, .13),
                 drum=(.7, .5, .05), orange=(.8, .3, .05), track=(.05, .05, .06)).items(): paint(k, c)
paint("pane", (1, .7, .3), glow=12); paint("beacon", (1, .1, .05), glow=30)
def spawn(bm, k, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def blk(loc, s, k, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return spawn(bm, k, loc, rot)
def cyl(loc, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return spawn(bm, k, loc, rot)
def ball(loc, r, k, sq=1, sx=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y, v.co.z * sq)) * random.uniform(.9, 1.1)
    return spawn(bm, k, loc)
def light(loc, col, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = loc; sc.collection.objects.link(o)
# snowfield on a rough floating slab
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=8, radius2=15, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .2)))
    else: v.co.z += random.uniform(-.1, .1)
spawn(bm, "snow")
# helipad with H, a beacon and a fuel cache
cyl((7.5, -2.5, 0), 5, .3, 10, "pad")
blk((7.5, -2.5, .3), (3.4, .7, .06), "heli2"); blk((5.8, -2.5, .3), (.7, .7, .06), "heli2"); blk((9.2, -2.5, .3), (.7, .7, .06), "heli2")
for i in range(10):
    a = i * .628; blk((7.5 + 4.7 * math.cos(a), -2.5 + 4.7 * math.sin(a), .3), (.7, .7, .12), "heli" if i % 2 else "pad")
cyl((11.6, -5.2, 0), .15, 1.2, 5, "steel"); cyl((11.6, -5.2, 1.2), .4, .4, 6, "beacon"); light((11.6, -5.2, 1.6), (1, .1, .05), 400)
for i in range(3):
    cyl((11.5 + i * 1.2, 3.5 - (i % 2) * .3, 0), .5, 1.1, 8, "drum", r2=.45)
blk((10.2, 3.8, 0), (2.4, .8, .5), "steel"); blk((10.2, 3.8, .5), (2.6, 1.0, .1), "timber")
# the helicopter: skis, body, tail, rotor, windows
hx, hy = 7.5, -2.5
for s in (-1, 1):
    blk((hx, hy + s * 1.2, .45), (4.6, .15, .15), "heli2"); blk((hx - 1.8, hy + s * 1.2, .3), (.15, .15, .4), "heli2"); blk((hx + 1.8, hy + s * 1.2, .3), (.15, .15, .4), "heli2")
    blk((hx, hy + s * 1.2, .6), (.3, .3, .3), "heli2")
ball((hx, hy, 1.5), 1.5, "heli", .9, 1.5); ball((hx + 1.5, hy, 1.7), .8, "glass", .9, .8)
blk((hx - 3.4, hy, 1.6), (3.6, .35, .35), "heli"); blk((hx - 5.2, hy, 1.5), (.3, .3, 1.5), "heli")
cyl((hx - .2, hy, 2.7), .2, .5, 6, "heli2"); blk((hx - .2, hy, 3.2), (7.5, .25, .12), "heli2"); blk((hx - .2, hy, 3.2), (.25, 5.5, .12), "heli2")
# the lodge: timber walls, steep roof, glowing windows, chimney, porch
blk((-5, 2, 0), (8, 5, 3.2), "timber")
for i in range(8): blk((-5, 2, i * .4), (8.1, 5.1, .1), "drift")
rf = bmesh.new(); vs = [rf.verts.new(p) for p in ((-4.8, -3.2, 0), (4.8, -3.2, 0), (4.8, 3.2, 0), (-4.8, 3.2, 0), (-4.8, 0, 2.4), (4.8, 0, 2.4))]
for f in ((0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)): rf.faces.new([vs[i] for i in f])
bmesh.ops.recalc_face_normals(rf, faces=rf.faces); spawn(rf, "roof", (-5, 2, 3.2))
blk((-5, 2, 5.6), (8.4, .5, .3), "drift")
blk((-1.6, 2, 4.6), (.9, .9, 2.2), "steel")
for i in range(3): blk((-7.4 + i * 1.6, -.55, 1.0), (1.0, .1, 1.2), "pane")
blk((-1.6, -.55, 0), (1.2, .1, 2.0), "pane"); blk((-5, -.55, 0), (.1, .1, .1), "pane")
blk((-5, -1.6, 0), (8.4, 2.4, .25), "timber")
for x in (-8.8, -1.2): blk((x, -2.6, 0), (.2, .2, 2.2), "timber")
blk((-5, -2.6, 2.2), (8.4, .2, .2), "timber"); blk((-5, -.9, 2.2), (8.4, .2, .2), "timber")
light((-5, -1.2, 1.5), (1, .65, .3), 700); light((-5, -3.5, 1.5), (1, .65, .3), 200)
# ski rack with skis and poles
for s in (-1, 1): blk((.5 + s * 1.0, -6.5, 0), (.15, .15, 1.2), "timber")
blk((.5, -6.5, 1.1), (2.4, .15, .15), "timber"); blk((.5, -6.5, .6), (2.4, .15, .1), "timber")
for i in range(6):
    blk((-.3 + i * .32, -6.5, .1), (.14, .08, 1.7), "heli" if i % 2 else "orange", rot=(0, 0, 0))
for i in range(4): cyl((1.7 + i * .2, -6.5, 0), .04, 1.6, 4, "steel")
# pines and drifts
for x, y, h in ((-11, 7, 4), (-12, -3, 3.2), (-8, 10, 3.6), (3, 9, 4.2), (12, 8, 3.8), (-2, -10, 3), (12, -9, 3.4), (-12, 2, 3.4)):
    cyl((x, y, 0), .3, 1.2, 5, "timber")
    for k in range(3): cyl((x, y, 1.0 + k * h * .22), 1.7 - k * .45, h * .4, 7, "pine", r2=.1)
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(9, 14)
    ball((r * math.cos(a), r * math.sin(a) * .8, .1), random.uniform(.8, 1.6), "drift", .35, 1.8)
for col, w, p in (((.6, .78, 1), 5.5, (-28, -14, 9)), ((1, .62, .45), 2.4, (24, 20, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .04, .09, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((1, 0, 1.5)); co.location = tg + Vector((10, -58, 32))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
