import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1315)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
G = {}
def paint(name, rgb, em=0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .8
    p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: pass
    G[name] = m
for k, c in dict(asphalt=(.1, .11, .14), curb=(.28, .28, .3), brick=(.3, .12, .1), slate=(.12, .14, .2), soil=(.18, .12, .08),
                 leaf=(.06, .3, .12), leaf2=(.12, .38, .1), trunk=(.25, .17, .1), plank=(.45, .28, .14), steel=(.35, .4, .45),
                 hut=(.5, .45, .35), roof=(.15, .25, .25), door=(.1, .3, .35), palm=(.2, .4, .12), rock=(.3, .3, .32)).items(): paint(k, c)
paint("pane", (.6, .9, .95), alpha=.16); paint("lamp", (1, .75, .3), 12); paint("neon", (1, .15, .5), 12); paint("screen", (.2, .9, .8), 6)
def solid(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("g"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("g", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(G[m]); return o
def box(x, y, z, w, d, h, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return solid(bm, m, (x, y, z), (0, 0, rz))
def cone(x, y, z, r, h, n, m, r2=0.0, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return solid(bm, m, (x, y, z), rot)
def blob(x, y, z, r, m, sq=.8):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return solid(bm, m, (x, y, z))
def glow(x, y, z, w, c):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = (x, y, z); sc.collection.objects.link(o)
# base: asphalt city block with raised kerb and rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    if v.co.z < 0: v.co.x *= .7; v.co.y *= .7; v.co.z -= random.uniform(0, .6)
    v.co = Vector((v.co.x * 26, v.co.y * 26, v.co.z * 3 - 1.5))
solid(bm, "asphalt")
for i in range(12): box(-11 + i * 2, -12.5, .0, .2, .3, .02, "curb")
# the glass dome: low-poly icosphere, faceted, with steel ribs and a glowing rim
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=7.5)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -.1], context='VERTS')
solid(bm, "pane", (0, 0, 0))
for i in range(8):
    a = i * math.pi / 4
    for k in range(1, 7):
        r = 7.5 * math.sin(k * .139 * 7.5) * 1.0; z = 7.5 * math.cos(k * .139 * 7.5) * 1.0
        if z < .5: continue
        box(r * math.cos(a) * .98, r * math.sin(a) * .98, z * .98 - .1, .12, .12, .15, "steel", rz=a)
for i in range(16):
    a = i * math.pi / 8
    box(7.5 * math.cos(a), 7.5 * math.sin(a), 0, .22, .22, .5, "steel")
cone(0, 0, 0, 7.7, .15, 16, "curb", 7.7)
cone(0, 0, 0, 6.6, .3, 12, "soil", 6.6)
# tropical plants: palms, banana leaves, ferns, a rock pool
for i, (x, y) in enumerate(((-3.5, 2), (3.5, -2.5), (2, 4), (-2, -4.5))):
    h = random.uniform(2.2, 3.2)
    cone(x, y, .3, .22, h, 5, "trunk", .12)
    for k in range(6):
        a = k * 1.05 + i
        cone(x + .3 * math.cos(a), y + .3 * math.sin(a), .3 + h, .35, 2.2, 4, "palm", 0.02, rot=(math.pi / 2 - .4, 0, a + math.pi / 2))
for i in range(10):
    a = random.uniform(0, 6.28); r = random.uniform(1.5, 5.5)
    blob(r * math.cos(a), r * math.sin(a), .45, random.uniform(.5, .9), random.choice(("leaf", "leaf2", "palm")), .7)
cone(-4.5, -2.5, .3, 1.6, .25, 7, "rock", 1.4)
# wooden walkway across the dome floor with posts and rails
for i in range(11):
    t = -1 + i * .2
    box(7.5 * t * .98 * .99 - .15, 0, .3, .9, 1.6, .1, "plank", rz=0)
for i in range(6):
    t = -1 + i * .4
    box(7.5 * t * .98, -1.0, .3, .12, .12, 1.0, "trunk"); box(7.5 * t * .98, 1.0, .3, .12, .12, 1.0, "trunk")
box(0, -1.0, 1.2, 14.5, .08, .08, "trunk"); box(0, 1.0, 1.2, 14.5, .08, .08, "trunk")
# research hut on stilts inside, with lit windows and a small sign
for sx in (-1, 1):
    for sy in (-1, 1): cone(5.2 + sx * 1.2, 4.2 + sy * 1.2, .3, .1, 1.2, 5, "trunk", .1)
box(5.2, 4.2, 1.5, 3.2, 3.2, 2.2, "hut")
cone(5.2, 4.2, 3.7, 2.8, 1.2, 4, "roof", .2, rot=(0, 0, math.pi / 4))
box(5.2, 2.55, 2.1, 1.2, .1, .8, "lamp"); box(3.5, 4.2, 2.1, .1, 1.2, .8, "lamp")
glow(5.2, 2.0, 2.2, 450, (1, .7, .3))
# airlock: steel door frame with glowing seam, steps and a sign lamp
box(0, -7.5, 0, 3.2, 1.0, 3.2, "steel")
box(0, -8.05, .2, 2.2, .15, 2.7, "door"); box(0, -8.15, .2, 2.2, .06, .1, "lamp"); box(0, -8.15, 2.8, 2.2, .06, .1, "lamp")
glow(0, -9.2, 1.6, 300, (.6, 1, .9))
for i in range(3): box(0, -8.5 - i * .4, 0, 3.0 - i * .4, .4, .2 + (2 - i) * .1, "curb")
# city: two brick blocks with lit windows, a neon sign, lamp posts
for bx, by, w, d, h in ((-9.5, 5, 6, 6, 8), (9.5, 6, 6, 5, 6)):
    box(bx, by, 0, w, d, h, "brick"); box(bx, by, h, w + .3, d + .3, .4, "slate")
    for i in range(3):
        for j in range(2): box(bx - 1.8 + i * 1.8, by - d / 2 - .05, 1.5 + j * 2.4, 1.0, .1, 1.2, "lamp" if (i + j) % 3 else "slate")
box(9.5, 3.4, 6.4, 2.4, .2, 1.0, "neon"); glow(9.5, 2.6, 7.0, 500, (1, .15, .5))
for x, y in ((-6, -9), (6, -9)):
    cone(x, y, 0, .1, 3.5, 5, "steel", .08); box(x, y, 3.5, .8, .5, .3, "lamp"); glow(x, y, 3.4, 250, (1, .75, .4))
# night: cool teal key from the left, magenta rim from behind, dark blue backdrop
for c, e, p in (((.45, .8, .9), 4.5, (-26, -14, 12)), ((.9, .3, .7), 2.4, (22, 20, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = e
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
co.location = (10, -54, 32)
co.rotation_euler = (Vector((0, 0, 2.5)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
