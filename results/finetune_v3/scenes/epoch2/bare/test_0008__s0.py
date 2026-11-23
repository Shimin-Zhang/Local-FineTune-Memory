import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1469)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
M = {}
def dye(k, c, e=0, r=.9):
    m = bpy.data.materials.new(k); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    if e: b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    M[k] = m
dye("grass", (.1, .17, .07)); dye("loam", (.2, .13, .07)); dye("timber", (.3, .2, .11)); dye("dark", (.14, .09, .05))
dye("thatch", (.4, .3, .13)); dye("pit", (.04, .03, .025)); dye("stone", (.4, .38, .35)); dye("pig", (.7, .45, .4))
dye("cloth", (.55, .5, .4)); dye("red", (.6, .12, .08)); dye("flax", (.55, .5, .3)); dye("cabbage", (.2, .35, .12))
dye("carrot", (.8, .3, .05)); dye("lantern", (1, .6, .2), 14); dye("mud", (.25, .17, .1))
def mesh(bm, k, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(M[k]); return o
def slab(p, s, k, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        f = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * f, v.co.y * s[1] * f, (v.co.z + .5) * s[2]))
    return mesh(bm, k, p, (0, 0, rz))
def post(p, r, h, n, k, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, k, p)
def lump(p, r, k, s=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2])) * random.uniform(.9, 1.1)
    return mesh(bm, k, p)
def roof(p, w, l, h, k):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1, radius2=.05, depth=h)
    for v in bm.verts: v.co = Vector((v.co.x * w * .71, v.co.y * l * .71, v.co.z + h / 2))
    return mesh(bm, k, p, (0, 0, math.pi / 4))
def glow(p, c, w):
    l = bpy.data.lights.new("l", "POINT"); l.color = c; l.energy = w
    o = bpy.data.objects.new("l", l); o.location = p; sc.collection.objects.link(o)
# the clearing: a grassy slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=11, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.7
mesh(bm, "grass")
# the hut: four posts, a plank wall on the back and left, open to the camera, thatch roof
hx, hy = -1.5, 1.5
for sx in (-1, 1):
    for sy in (-1, 1): post((hx + sx * 2.0, hy + sy * 1.6, 0), .16, 2.7, 5, "timber")
slab((hx, hy + 1.6, 0), (4.4, .2, 2.4), "timber"); slab((hx - 2.0, hy, 0), (.2, 3.4, 2.4), "timber")
for z in (.8, 1.6): slab((hx, hy + 1.6, z), (4.4, .22, .1), "dark")
roof((hx, hy, 2.7), 5.4, 4.6, 1.8, "thatch")
slab((hx + .3, hy + 1.4, 0), (1.2, 1.0, .6), "dark"); slab((hx - 1.2, hy - .2, 0), (1.6, 1.2, .12), "flax")
slab((hx + 1.0, hy - 1.2, 0), (.7, .7, .7), "dark"); slab((hx + 1.0, hy - 1.2, .7), (.5, .5, .5), "red")
glow((hx + 1.0, hy - 1.2, 1.5), (1, .6, .2), 220); post((hx + 1.0, hy - 1.2, 1.2), .22, .5, 6, "lantern", .15)
# the shallow pit in front of the hut, with a stone rim
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=1.9, radius2=1.9, depth=.3)
for v in bm.verts: v.co.z -= .15
mesh(bm, "pit", (hx + .3, hy - 3.6, .02))
for i in range(10):
    a = i * math.pi * 2 / 10; lump((hx + .3 + 2.1 * math.cos(a), hy - 3.6 + 2.1 * math.sin(a), .1), .35, "stone", (1, 1, .7))
# the warp-weighted loom: two beams, warp threads, hanging stones
lx, ly = 5.0, 2.0
for sy in (-1.4, 1.4):
    slab((lx, ly + sy, 1.9), (.2, .2, .2), "timber")
    post((lx, ly + sy, 0), .12, 2.0, 5, "timber")
slab((lx, ly, 1.9), (.2, 3.2, .2), "timber"); slab((lx, ly, .9), (.2, 3.2, .2), "timber")
for i in range(9):
    y = ly - 1.3 + i * .325
    slab((lx, y, .9), (.05, .05, 1.0), "cloth")
    lump((lx, y, .65), .22, "stone", (1, 1, .8)); slab((lx, y, .8), (.04, .04, .1), "dark")
slab((lx, ly, .9), (.1, 3.0, .1), "red"); slab((lx, ly, 1.4), (.1, 3.0, .1), "flax")
# pig pen: a roundish palisade with slatted gaps, two pigs and a trough
px, py = -7.0, -3.0
for i in range(14):
    a = i * math.pi * 2 / 14
    post((px + 2.6 * math.cos(a), py + 2.2 * math.sin(a), 0), .1, 1.2, 5, "timber")
    b = a + math.pi * 2 / 14
    slab((px + 2.6 * math.cos(a + .5), py + 2.2 * math.sin(a + .5), .5), (1.3, .06, .1), "timber", a + .5 + math.pi / 2)
lump((px - .6, py - .3, .5), .6, "pig", (1.5, 1, .9)); lump((px + .6, py + .7, .5), .5, "pig", (1.4, 1, .9))
slab((px + 1.2, py - 1.2, 0), (1.4, .5, .35), "dark")
# vegetable plot: raised beds of different crops with a scarecrow
vx, vy = 6.5, -4.5
for r in range(3):
    for c in range(2):
        bx, by = vx + c * 3.0, vy + r * 1.7
        slab((bx, by, 0), (2.6, 1.4, .25), "loam", 0, .95)
        for k in range(4):
            kx, ky = bx - .9 + k * .6, by + random.uniform(-.3, .3)
            if r == 0: lump((kx, ky, .45), .28, "cabbage")
            elif r == 1: post((kx, ky, .2), .06, .5, 5, "carrot", .02)
            else: lump((kx, ky, .5), .22, "flax", (1, 1, 1.4))
post((vx + 1.5, vy + 2.7, 0), .08, 2.2, 5, "timber"); slab((vx + 1.5, vy + 2.7, 1.5), (1.2, .08, .08), "timber")
lump((vx + 1.5, vy + 2.7, 2.4), .25, "red")
# trees at the edge of the clearing
for x, y, h in ((-9, 6, 4), (-4, 9, 3.4), (2, 9.5, 3.8), (9, 7, 4.2), (10, -2, 3.2), (-10, -7, 3.4)):
    post((x, y, 0), .3, h, 5, "dark", .2)
    for j in range(3): lump((x, y, h + j * .9), 1.5 - j * .35, "grass", (1, 1, .9))
# light: cool blue dusk from the left, faint amber rim from behind
for c, w, p in (((.55, .65, 1), 4.5, (-24, -10, 9)), ((1, .6, .3), 2, (18, 22, 8))):
    s = bpy.data.lights.new("s", "SUN"); s.color = c; s.energy = w
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("dusk"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .04, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 0, 1.5)); co.location = tg + Vector((6, -48, 27))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
