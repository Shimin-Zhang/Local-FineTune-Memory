import bpy, bmesh, random, math
from mathutils import Vector, Matrix
random.seed(1373)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
sc = bpy.context.scene
M = {}
def paint(name, rgb, glow=0, rough=.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow:
        b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    M[name] = m
def part(bm, name, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me)
    o = bpy.data.objects.new(name, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(M[name]); return o
def blk(bm, x, y, z, w, d, h, rz=0):
    bmesh.ops.create_cube(bm, size=1, matrix=Matrix.Translation((x, y, z + h / 2)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Diagonal((w, d, h, 1)))
def cyl(bm, x, y, z, r, h, n=8, r2=None):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h, matrix=Matrix.Translation((x, y, z + h / 2)))
def ball(bm, x, y, z, r, sq=(1, 1, 1)):
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=Matrix.Translation((x, y, z)) @ Matrix.Diagonal((*sq, 1)))
def glowlight(at, col, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
for n, c in (("road", (.05, .05, .07)), ("kerb", (.2, .2, .22)), ("sidewalk", (.16, .16, .18)), ("rock", (.1, .08, .1)), ("brickA", (.25, .1, .08)), ("brickB", (.15, .15, .2)),
             ("brickC", (.2, .16, .12)), ("dark", (.02, .02, .03)), ("marsh", (.9, .85, .75)), ("face", (.35, .12, .08)), ("nose", (.55, .15, .1)), ("eye", (.03, .02, .02)),
             ("coat", (.1, .2, .4)), ("skin", (.5, .3, .22)), ("car1", (.5, .05, .05)), ("car2", (.1, .25, .45)), ("car3", (.55, .4, .05)), ("tyre", (.02, .02, .02)), ("lamp", (.9, .8, .5))):
    paint(n, c)
paint("win", (1, .65, .25), 4); paint("neon", (1, .1, .4), 14); paint("neon2", (.1, .8, 1), 14); paint("taillight", (1, .05, .03), 12); paint("headlight", (1, .9, .6), 12)
bm = bmesh.new(); blk(bm, 0, 0, -1.6, 28, 24, 1.6)
bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.calc_center_median().z < -1], context='FACES')
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
for v in bm.verts:
    if v.co.z < -1.5: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.4, .2)))
part(bm, "rock", (0, 0, -1.6))
bm = bmesh.new(); blk(bm, 0, 0, 0, 28, 11, .15)
for i in range(12): blk(bm, -12 + i * 2.2, 0, .15, 1.4, .25, .03)
part(bm, "road"); part(bm, "kerb", (0, 0, .15))
bm = bmesh.new()
blk(bm, 0, -8.6, 0, 28, 6.8, .3); blk(bm, 0, 8.6, 0, 28, 6.8, .3)
for i in range(14): blk(bm, -13 + i * 2, -5.1, .3, .15, .15, .02)
part(bm, "sidewalk")
def tower(x, y, w, d, h, mat, lit):
    bm = bmesh.new(); blk(bm, x, y, 0, w, d, h)
    for k in range(int(h / 1.5)):
        for j in range(int(w / 1.3)):
            if random.random() < lit:
                blk(bm, x - w / 2 + .6 + j * 1.3, y - d / 2 - .02, 1 + k * 1.5, .6, .05, .8)
    part(bm, mat)
tower(-9, 8.6, 6, 6.5, 14, "brickA", .35); tower(-2, 8.6, 5, 6.5, 10, "brickB", .3); tower(5, 8.6, 6, 6.5, 16, "brickC", .4); tower(11.5, 8.6, 4, 6.5, 8, "brickA", .3)
tower(-9, -8.6, 6, 6.5, 9, "brickB", .35); tower(-2, -8.6, 5, 6.5, 12, "brickC", .4); tower(5, -8.6, 6, 6.5, 8, "brickA", .3); tower(11.5, -8.6, 4, 6.5, 13, "brickB", .35)
bm = bmesh.new()
blk(bm, -2, 5.2, 3, 3.2, .12, 1.1); blk(bm, 5, 5.2, 6, 3.6, .12, 1.0)
part(bm, "neon"); part(bm, "neon2", (5, 5.2, 6))
glowlight((-2, 4.5, 3.5), (1, .1, .4), 700); glowlight((5, 4.5, 6.5), (.1, .8, 1), 700)
bm = bmesh.new()
ball(bm, 0, 0, 5.5, 2.4, (1, 1, 1.05)); ball(bm, 0, 0, 9.5, 2.0, (1, 1, 1.1))
cyl(bm, 0, 0, 12.2, 2.2, 1.6, 8, .3); cyl(bm, 0, 0, 13.8, .25, .6, 5, .05)
ball(bm, -.7, -1.8, 10.0, .3, (1, 1, 1)); ball(bm, .7, -1.8, 10.0, .3, (1, 1, 1)); ball(bm, 0, -2.0, 9.3, .5, (1, 1, .9))
part(bm, "marsh")
bm = bmesh.new()
blk(bm, -.7, -1.85, 10.0, .3, .08, .3); blk(bm, .7, -1.85, 10.0, .3, .08, .3); blk(bm, 0, -2.1, 9.0, 1.5, .1, .5)
part(bm, "eye"); part(bm, "face", (0, -2.05, 8.7)); part(bm, "nose", (0, -2.55, 9.3))
bm = bmesh.new()
blk(bm, -2.9, 0, 4.5, 1.4, 1.4, 3.6); blk(bm, 2.9, 0, 4.5, 1.4, 1.4, 3.6)
ball(bm, -2.9, 0, 4.3, .9); ball(bm, 2.9, 0, 4.3, .9)
part(bm, "marsh")
bm = bmesh.new()
for i in range(26):
    x, y = random.uniform(-13, 13), random.choice((-1, 1)) * random.uniform(5.8, 8)
    if abs(x) < 3.5 and abs(y) < 5: continue
    cyl(bm, x, y, .3, .3, .8, 5); ball(bm, x, y, 1.25, .26)
part(bm, "coat")
bm = bmesh.new()
for i in range(10):
    x, y = random.uniform(-13, 13), random.choice((-1, 1)) * random.uniform(5.8, 8)
    if abs(x) < 3.5 and abs(y) < 5: continue
    ball(bm, x, y, 1.3, .24)
part(bm, "skin")
def car(x, y, mat, rz):
    bm = bmesh.new()
    blk(bm, 0, 0, .3, 2.4, 1.2, .55, rz); blk(bm, -.1, 0, .85, 1.2, 1.0, .4, rz)
    for sx in (-.8, .8):
        for sy in (-.62, .62): cyl(bm, sx, sy, .25, .27, .15, 6)
    part(bm, mat, (x, y, 0), (0, 0, rz))
    bm = bmesh.new(); blk(bm, -1.22, 0, .45, .1, .8, .2); part(bm, "taillight", (x, y, 0), (0, 0, rz))
    bm = bmesh.new(); blk(bm, 1.22, 0, .45, .1, .8, .2); part(bm, "headlight", (x, y, 0), (0, 0, rz))
car(-7, -2.5, "car1", 0); car(-3, 2.5, "car2", math.pi); car(8, 2.5, "car3", math.pi); car(11, -2.5, "car2", 0)
bm = bmesh.new()
for x in (-12, 12): cyl(bm, x, -4.6, .3, .08, 3.5, 5); blk(bm, x, -4.6, 3.8, .8, .4, .3)
part(bm, "dark"); part(bm, "lamp", (-12, -4.6, 3.9)); part(bm, "lamp", (12, -4.6, 3.9))
glowlight((-12, -4.6, 3.5), (1, .8, .5), 500); glowlight((12, -4.6, 3.5), (1, .8, .5), 500)
for col, w, p in (((.45, .5, 1), 4, (-24, -14, 10)), ((1, .2, .5), 2.5, (22, 18, 12))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("sun", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 5)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("night"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .01, .035, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 6)); co.location = t + Vector((14, -62, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
