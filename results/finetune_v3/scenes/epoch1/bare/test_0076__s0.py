import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1594)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def tone(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    mats[name] = m
for k, c in (("cliff", (.2, .12, .09)), ("cliff2", (.15, .09, .08)), ("mud", (.42, .27, .16)), ("mud2", (.33, .2, .12)), ("thatch", (.5, .38, .15)), ("thatch2", (.38, .28, .12)),
             ("wood", (.2, .12, .07)), ("maskA", (.7, .1, .08)), ("maskB", (.75, .6, .15)), ("maskC", (.1, .3, .3)), ("white", (.7, .65, .55)), ("stone", (.25, .2, .18)), ("step", (.3, .22, .17))): tone(k, c)
tone("flame", (1, .5, .1), 14); tone("cave", (1, .35, .1), 2.5)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def blk(x, y, z, w, d, h, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mk(bm, m, (x, y, z), (0, 0, rz))
def post(x, y, z, r, h, m, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z))
def cone(x, y, z, r, h, m, n=7):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=0, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z))
def lump(x, y, z, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.85, 1.15)
    return mk(bm, m, (x, y, z))
def lit(x, y, z, w, c):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = (x, y, z); sc.collection.objects.link(o)
# cliff mass: a tall ragged block, top flat for the terrace, front face cut into ledges
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=5, use_grid_fill=True)
for v in bm.verts:
    top = v.co.z > .4; front = v.co.y < -.3
    v.co = Vector((v.co.x * 28 * (1 if top else .8 + random.random() * .1), v.co.y * 22 * (1 if top else .8), v.co.z * 17 + 8.5))
    if not top:
        v.co.z += random.uniform(-1, 1)
        if front: v.co.x += random.uniform(-1.5, 1.5); v.co.y -= random.uniform(0, 2)
    elif front: v.co.y -= random.uniform(0, .5)
mk(bm, "cliff")
# terrace steps up to the mud house
for i in range(5): blk(-3.5, -9 + i * 1.0, 0, 8, 1.0, .35 * (i + 1), "step")
# mud house: flat-roofed base, tall thatched roof
blk(-3.5, -3.5, 0, 7, 6, 3.2, "mud", top=.97)
blk(-3.5, -3.5, 3.2, 7.4, 6.4, .3, "mud2")
blk(-3.5, -6.55, 0, 1.4, .1, 2.2, "wood"); blk(-6.2, -6.55, 1.0, 1.2, .1, 1.0, "flame"); blk(-.8, -6.55, 1.0, 1.2, .1, 1.0, "flame")
cone(-3.5, -3.5, 3.5, 5.2, 4.2, "thatch", 8); cone(-3.5, -3.5, 7.7, 4.0, 3.6, "thatch2", 8); cone(-3.5, -3.5, 11.3, 2.8, 2.6, "thatch", 8); cone(-3.5, -3.5, 13.9, 1.4, 1.8, "thatch2", 8)
for k in range(8): blk(-3.5 + 3.6 * math.cos(k * .785), -3.5 + 3.6 * math.sin(k * .785), 3.2, .3, .3, .5, "wood")
lit(-3.5, -7.5, 1.2, 350, (1, .5, .15))
# cave-mouth shrine on a ledge above, with a torii-like frame and a glowing mouth
blk(6, -1, 0, 10, 7, 4.5, "cliff2", top=.9)
blk(6, -4.4, 0, 3.2, .2, 3.2, "cave"); blk(6, -4.6, 3.0, 3.6, .3, .5, "stone")
for sx in (-1.9, 1.9): blk(6 + sx, -5.3, 0, .4, .4, 3.6, "wood"); blk(6 + sx, -5.3, 3.6, .5, .5, .3, "wood")
blk(6, -5.3, 3.6, 4.6, .5, .4, "wood"); blk(6, -5.3, 4.1, 5.4, .3, .3, "wood")
for k in range(3): blk(6 + (k - 1) * 2.6, -5.6, 0, .5, .5, 1.0, "stone"); blk(6 + (k - 1) * 2.6, -5.6, 1.0, .3, .3, .4, "flame")
lit(6, -6.2, 2.2, 700, (1, .4, .12))
# masks lined up on the terrace ledge, larger than life
for i in range(9):
    x = -10.5 + i * 2.5; m = ("maskA", "maskB", "maskC")[i % 3]
    blk(x, -9.2, 1.2, 1.4, .5, 1.9, m, top=.8); blk(x, -9.6, 1.8, 1.0, .1, .3, "white"); blk(x, -9.6, 1.0, .9, .1, .25, "white")
    for s in (-.3, .3): blk(x + s, -9.65, 2.0, .22, .1, .2, "white")
    post(x, -9.2, 3.1, .5, .4, "white", 5, .2); blk(x, -9.2, 0, .5, .5, 1.2, "stone")
# stone lanterns along the steps
for x in (-8.5, 1.5):
    post(x, -8.6, 0, .35, 1.4, "stone", 5); blk(x, -8.6, 1.4, 1.0, 1.0, .8, "stone"); blk(x, -8.6, 1.55, .5, .5, .4, "flame"); cone(x, -8.6, 2.2, .9, .7, "stone", 4)
    lit(x, -8.6, 1.8, 150, (1, .5, .15))
# boulders and scrub at the cliff foot
for i in range(9):
    x = random.uniform(-12, 12); y = random.uniform(-11, -10)
    lump(x, y, .3, random.uniform(.6, 1.3), "stone", (1.2, 1, .8))
for i in range(10): lump(random.uniform(-13, 13), random.uniform(-11, 10), 0, random.uniform(.5, 1.0), "cliff2", (1, 1, .7))
# dusk: low orange key from the right, violet rim from behind left
for c, w, p in (((1, .5, .22), 5.5, (36, -24, 11)), ((.5, .3, .8), 2.2, (-28, 30, 16))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 5)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("dusk"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .01, .03, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, -1, 6)); co.location = t + Vector((-16, -76, 44))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
