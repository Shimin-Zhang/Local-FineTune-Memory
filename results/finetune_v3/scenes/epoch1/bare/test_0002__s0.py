import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1503)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def pigment(rgb, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
dust, dust2, plank, plank2, wood, roof, signm, glass, tumble, tumble2, iron, piano, white, black = [pigment(c) for c in [(.42,.3,.18),(.34,.24,.14),(.36,.22,.12),(.28,.17,.1),(.2,.12,.07),(.17,.09,.06),(.5,.38,.2),(.9,.72,.45),(.55,.4,.22),(.4,.28,.15),(.08,.07,.07),(.1,.07,.06),(.5,.46,.38),(.04,.04,.05)]]
sun = pigment((1, .85, .5), 1.5); ember = pigment((1, .35, .08), 8)
def mesh(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(loc, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mesh(bm, m, loc, rot)
def tube(loc, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, loc, rot)
def blob(loc, r, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) * random.uniform(.85, 1.15)
    return mesh(bm, m, loc)
def glow(loc, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("g", L); o.location = loc; sc.collection.objects.link(o)
# desert base with a dusty yard
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=14, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.8, .3)))
    else: v.co.z += random.uniform(-.08, .08)
    v.co.z -= 2
mesh(bm, dust)
for i in range(14): blob((random.uniform(-11, 11), random.uniform(-10, 10), .1), random.uniform(.5, 1.2), dust2, (1.8, 1.8, .3))
# the saloon: walls, porch, false front and a sagging roof
blk((0, 3, 0), (13, 8, 5.4), plank)
blk((0, -1.3, 0), (14, 3.6, .4), plank2)
for i in range(7): blk((-6 + i * 2, -3.0, 0), (.3, .3, 3.0), wood)
blk((0, -1.3, 3.4), (14, 3.6, .3), wood)
blk((0, 3, 5.4), (13.6, 8.6, .4), roof)
blk((0, -1.1, 5.8), (14, .3, 1.0), plank2)
blk((-6.5, -1.1, 5.8), (.3, .3, 1.0), wood); blk((6.5, -1.1, 5.8), (.3, .3, 1.0), wood)
# the swinging doors, one half off its hinge
blk((0, -.5, .4), (3.4, .2, 3.0), wood)
blk((-1.5, -.6, .4), (.15, .15, 3.0), iron); blk((1.5, -.6, .4), (.15, .15, 3.0), iron)
blk((-.85, -.7, .4), (1.6, .15, 2.9), plank2, (0, 0, 0)); blk((.95, -.9, .5), (1.6, .15, 2.9), plank2, (.12, .2, .05))
blk((-.85, -.8, 1.6), (1.2, .06, 1.0), glass); blk((.95, -1.0, 1.8), (1.2, .06, 1.0), glass, (.12, .2, .05))
# window with the broken piano inside, and a bar window
blk((-4.2, -.5, 1.4), (3.2, .2, 2.2), iron); blk((-4.2, -.6, 1.5), (2.8, .1, 1.8), glass)
blk((-4.2, 1.5, .4), (2.4, 1.5, 1.3), piano); blk((-4.2, .8, 1.3), (2.2, .08, .5), white, (-.5, 0, 0)); blk((-4.2, 1.5, 1.7), (2.6, 1.6, .15), black, (.1, 0, 0))
blk((-4.2, .8, 1.1), (.9, .06, .1), black, (-.5, 0, 0))
blk((4.2, -.5, 1.4), (3.2, .2, 2.2), iron); blk((4.2, -.6, 1.5), (2.8, .1, 1.8), glass)
blk((4.2, 1.2, .4), (2.8, 1.0, 1.1), wood); blk((4.2, .65, 1.5), (2.6, .1, .1), iron)
# false front with sign and sun-bleached board
blk((0, -1.1, 6.8), (14, .4, 4.2), plank2)
blk((0, -1.4, 8.6), (8, .15, 1.5), signm); blk((0, -1.5, 9.0), (7.2, .1, .9), wood)
blk((-5.6, -1.3, 7.4), (.9, .1, 2.4), sun); blk((5.6, -1.3, 7.4), (.9, .1, 2.4), sun)
blk((0, -1.3, 11.0), (14, .2, .5), wood)
# the porch: a tumbleweed, a barrel, a cactus, a fence
blob((-2.5, -2.2, 1.0), 1.0, tumble, (1, 1, 1)); blob((-2.5, -2.2, 1.1), .7, tumble2, (1, 1, 1)); blob((-2.5, -2.2, 1.2), .4, tumble)
for i in range(6):
    a = i * 1.05; blk((-2.5 + math.cos(a) * 1.0, -2.2 + math.sin(a) * 1.0, .5 + i * .2), (.08, .08, .7), tumble2, (0, math.cos(a) * .9, math.sin(a) * .9))
tube((3.0, -2.2, .4), .6, 1.2, 7, wood); tube((3.0, -2.2, 1.6), .55, .12, 7, iron)
tube((-6.2, -2.2, .4), .35, 2.0, 6, tumble2); tube((-5.8, -2.2, 1.2), .22, 1.0, 5, tumble2)
for i in range(10):
    x = -6.5 + i * 1.5; blk((x, -5.6, .3), (.2, .2, 1.6), wood)
blk((0, -5.6, 1.3), (14.5, .15, .2), wood)
# a stump and a barrel fire glowing in the yard
tube((-9, -4, 0), .8, .9, 7, wood); tube((-9, -4, .9), .5, .1, 7, plank2)
for i in range(4): tube((-9 + math.cos(i * 1.6) * .9, -4 + math.sin(i * 1.6) * .9, 0), .25, .9, 5, iron, .15)
blob((-9, -4, 1.0), .5, ember, (1, 1, .9)); glow((-9, -4, 1.6), (1, .4, .1), 450)
# noon light: hard white sun nearly overhead, thin cool rim
for c, w, p in (((1, .9, .7), 6.5, (18, 12, 30)), ((.5, .65, 1), 2, (-20, -14, 10))):
    L = bpy.data.lights.new("s", "SUN"); L.color, L.energy = c, w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.025, .02, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((-8, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
