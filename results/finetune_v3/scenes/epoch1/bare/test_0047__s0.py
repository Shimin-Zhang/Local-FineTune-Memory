import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1303)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
col = {}
def tint(name, rgb, em=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = .9
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    col[name] = m
for k, c in dict(sand=(.5, .38, .22), track=(.38, .26, .15), sea=(.02, .3, .36), foam=(.55, .7, .7), trunk=(.3, .2, .12), leaf=(.05, .25, .1),
                 leaf2=(.1, .3, .12), tin=(.35, .38, .4), wall=(.5, .42, .3), awn1=(.6, .1, .1), awn2=(.6, .5, .1), tyre=(.03, .03, .03),
                 body=(.7, .3, .05), roof=(.1, .25, .3), post=(.2, .12, .07), rope=(.4, .35, .25), cloth=(.7, .15, .2), cloth2=(.1, .35, .6),
                 crate=(.3, .2, .1), glass=(.1, .25, .3), white=(.6, .6, .55)).items(): tint(k, c)
tint("lamp", (1, .7, .3), 12); tint("neon", (1, .1, .3), 10)
def make(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(col[m]); return o
def blk(p, s, m, r=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return make(bm, m, p, r)
def cyl(p, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, p, rot)
def ball(p, r, m, sq=1.0):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return make(bm, m, p)
def limb(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def lamp(p, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=11, radius1=7, radius2=13.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
make(bm, "sand")
# turquoise bay behind, with a pale foam line and a little sandbar
blk((0, 9.6, 0), (17, 5.6, .5), "sea", top=.98); blk((0, 6.6, 0), (17, .9, .12), "foam")
blk((5.5, 7.8, .5), (3.2, 1.4, .3), "sand", top=.7); blk((6, 7.8, .8), (.9, .6, .3), "white", top=.6)
# sandy track with ruts, running from the front to the shop
blk((0, -2.5, 0), (4.6, 15, .25), "track", top=.97)
for sx in (-1, 1): blk((sx * 1.2, -2.5, .25), (.4, 14, .06), "sand")
# small roadside shop with a tin roof, awning, crates, neon sign and a lantern
blk((-6.2, 1.5, 0), (5.2, 4.2, 2.8), "wall", top=.98); blk((-6.2, 1.5, 2.8), (6, 5, .25), "tin", r=(.12, 0, 0))
blk((-6.2, -.75, 1.9), (5.6, 1.2, .15), "awn1", r=(.15, 0, 0)); blk((-6.2, -.75, 1.75), (5.6, 1.2, .15), "awn2", r=(.15, 0, 0))
blk((-6.2, -.62, .0), (1.4, .12, 2.2), "post"); blk((-4.2, -.62, 1.0), (1.0, .1, .9), "glass")
blk((-7.2, -.75, 2.2), (1.6, .12, .8), "neon"); blk((-7.2, -.82, 2.4), (1.2, .06, .4), "lamp")
lamp((-7.2, -1.4, 2.6), (1, .15, .3), 300)
for i in range(3): blk((-8.2 + i * .9, -.2, 0), (.7, .7, .7 - i * .15), "crate", r=(0, 0, i))
cyl((-8.4, -1.2, 0), .05, 3.0, 5, "post"); blk((-8.4, -1.2, 3.0), (.7, .7, .8), "lamp"); lamp((-8.4, -1.2, 3.2), (1, .7, .3), 350)
# tuk-tuk without a driver: three wheels, a cabin, a roof and a headlight
tx, ty = 1.8, -5.5
for wx, wy in ((0, -1.3), (-1.1, 1.0), (1.1, 1.0)):
    cyl((tx + wx, ty + wy, .6), .6, .35, 8, "tyre", rot=(math.pi / 2, 0, 0))
blk((tx, ty, .9), (2.2, 2.6, .8), "body", top=.9); blk((tx, ty + .4, 1.7), (2.0, 1.6, 1.0), "body", top=.85)
blk((tx, ty + .5, 2.7), (2.6, 2.4, .15), "roof", r=(.1, 0, 0)); blk((tx, ty - .8, 1.7), (1.2, .1, .6), "glass")
blk((tx, ty - 1.35, 1.0), (.5, .12, .4), "lamp"); lamp((tx, ty - 2, 1.2), (1, .8, .5), 150)
# hammock between two palms, with a rope and a sleeping mat
for px in (6.5, 9.2):
    cyl((px, 2.5, 0), .35, 5.2, 6, "trunk", .22, rot=(0, .1, 0))
    for k in range(7):
        a = k * .9; limb((px, 2.5, 5.2), (px + math.cos(a) * 2.6, 2.5 + math.sin(a) * 2.6, 4.2), .28, "leaf", )
limb((6.8, 2.5, 4.6), (8.9, 2.5, 4.6), .06, "rope"); blk((7.85, 2.5, 3.3), (2.2, .9, .08), "cloth", r=(0, 0, 0)); blk((7.85, 2.5, 3.38), (2.2, .9, .08), "cloth2", r=(0, 0, 0))
# palms along the track and a few boulders and a beach umbrella
for px, py, h in ((-3.5, -7.5, 5.5), (-3.2, -1, 6), (3.4, 1.5, 5.2), (-2.8, 6, 6.2), (3.8, 6.5, 5.5)):
    cyl((px, py, 0), .3, h, 6, "trunk", .2, rot=(random.uniform(-.1, .1), random.uniform(-.1, .1), 0))
    for k in range(7):
        a = k * .9 + px; limb((px, py, h), (px + math.cos(a) * 2.4, py + math.sin(a) * 2.4, h - 1.0), .26, "leaf2" if k % 2 else "leaf")
for i in range(7):
    x, y = random.uniform(-9, 9), random.uniform(-9, 8)
    if abs(x) < 3.5 and y < 6 or abs(x + 6) < 4 and abs(y - 1) < 3: continue
    ball((x, y, .2), random.uniform(.4, .8), "trunk", .7)
cyl((-2.5, -8.8, 0), .06, 2.8, 5, "post"); blk((-2.5, -8.8, 2.8), (2.4, 2.4, .1), "awn1", r=(.5, 0, 0), top=.5)
for c, w, p in (((1, .55, .35), 6, (-22, -12, 8)), ((.3, .55, .85), 2.2, (16, 20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("w"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80; cm.clip_end = 500
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 1, 1.5)); co.location = tg + Vector((20, -50, 32))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
