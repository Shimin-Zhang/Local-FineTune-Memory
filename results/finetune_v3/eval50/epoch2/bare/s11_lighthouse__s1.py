import bpy, bmesh, random, math
from mathutils import Vector as V
random.seed(814)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def dye(c, glow=0, r=.8):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*c, 1); b.inputs['Roughness'].default_value = r
    if glow: b.inputs['Emission Color'].default_value = (*c, 1); b.inputs['Emission Strength'].default_value = glow
    return m
grass, rock, sea, white, red, slate, door, wood, brass, lamp, foam, rock2 = (dye((.07, .14, .07)), dye((.16, .16, .18)), dye((.04, .1, .18), r=.2), dye((.75, .75, .72)), dye((.6, .08, .06)),
    dye((.12, .13, .16)), dye((.1, .06, .04)), dye((.2, .12, .07)), dye((.7, .5, .15), r=.3), dye((1, .85, .45), 20), dye((.7, .8, .85)), dye((.24, .22, .22)))
def obj(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("o"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = V((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return obj(bm, m, at, rot)
def cyl(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return obj(bm, m, at, rot)
def boulder(at, r, m, sq=.7):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= 1 + random.uniform(-.2, .2); v.co.z *= sq
    return obj(bm, m, at)
def beam(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=13, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += V((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.3, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
obj(bm, grass)
# the sea: a dark pool along the front edge, with a foam rim and a breakwater of rocks
sea = bmesh.new(); bmesh.ops.create_cone(sea, cap_ends=True, segments=9, radius1=1, radius2=1, depth=.12)
for v in sea.verts: v.co = V((v.co.x * 10.5, v.co.y * 4.2, v.co.z))
obj(sea, sea, (0, -8.2, .05))
for i in range(11):
    a = i * math.pi / 10
    boulder((math.cos(a) * 10.2, -8.2 + math.sin(a) * 4.0, .1), random.uniform(.4, .8), foam if i % 2 else rock2)
for i in range(9):
    boulder((10.5 + random.uniform(-.3, .5), -6 + i * .9, .1), random.uniform(.5, .9), rock)
# the headland: a grassy mound with a rocky underside
cyl((0, 1.5, 0), 7.2, 1.6, 9, rock, 6.0)
cyl((0, 1.5, 1.4), 6.0, .6, 9, grass, 5.2)
for i in range(8):
    a = i * .8 + .3
    boulder((math.cos(a) * 6.6, 1.5 + math.sin(a) * 6.6, 1.0), random.uniform(.6, 1.1), rock2)
# lighthouse: plinth, tapering tower with five red bands, gallery, lantern room, dome
LX, LY, BZ = 0, 1.5, 2.0
blk((LX, LY, BZ), (4.6, 4.6, .6), white, top=.9); blk((LX, LY, BZ + .6), (3.8, 3.8, .5), white, top=.9)
for i in range(5):
    z0 = BZ + 1.1 + i * 2.0
    r0, r1 = 2.0 - i * .18, 1.82 - i * .18
    cyl((LX, LY, z0), r0, 1.0, 8, white, r1)
    cyl((LX, LY, z0 + 1.0), r1, 1.0, 8, red, r1 - .18)
    if i < 4: cyl((LX, LY, z0 + 1.0), r1 + .05, .1, 8, white, r1 - .02)
for k in range(4):
    a = k * 1.57 + .78
    blk((LX + math.cos(a) * 1.4, LY + math.sin(a) * 1.4, BZ + 4.0), (.35, .12, .8), door, (0, 0, a + 1.57))
blk((LX, LY - 1.7, BZ + 1.1), (1.0, .3, 1.7), door, top=.8)
blk((LX, LY, BZ + 11.1), (3.0, 3.0, .3), slate)
for k in range(8):
    a = k * math.pi / 4 + math.pi / 8
    blk((LX + math.cos(a) * 1.5, LY + math.sin(a) * 1.5, BZ + 11.4), (.1, .1, .9), slate, (0, 0, a))
    blk((LX + math.cos(a + .39) * 1.5, LY + math.sin(a + .39) * 1.5, BZ + 12.2), (.1, .1, .9), slate, (0, 0, a + .39))
cyl((LX, LY, BZ + 11.4), 1.3, 1.6, 8, lamp)
for k in range(8):
    a = k * math.pi / 4 + math.pi / 8
    blk((LX + math.cos(a) * 1.3, LY + math.sin(a) * 1.3, BZ + 11.4), (.14, .14, 1.7), slate, (0, 0, a))
cyl((LX, LY, BZ + 13.0), 1.5, .25, 8, slate)
cyl((LX, LY, BZ + 13.2), 1.2, .9, 8, red, .2)
cyl((LX, LY, BZ + 14.1), .08, 1.0, 4, brass)
beam('POINT', (1, .85, .45), 2500, (LX, LY, BZ + 12.2))
# the keeper's cottage, with a lit window, chimney and a path of slabs
blk((-6.0, -2.0, 2.0), (3.6, 2.8, 2.2), white, top=.95)
blk((-6.0, -2.0, 4.2), (4.2, 3.2, .3), slate, (.0, 0, 0), top=.9)
blk((-6.0, -3.45, 3.0), (1.2, .12, .9), lamp)
blk((-7.0, -1.2, 4.4), (.7, .7, 1.4), rock2)
beam('POINT', (1, .75, .35), 200, (-6.0, -4.0, 3.2))
for i in range(6): blk((-2.6 + i * .5, -1.6 - i * .5, 2.0), (.8, .6, .08), rock2, (0, 0, random.uniform(-.2, .2)))
# a small rowboat on the sea, a buoy, shrubs and a lamp post
blk((5.5, -8.0, .1), (2.6, 1.0, .5), wood, (0, 0, .5), top=.6)
blk((5.5, -8.0, .5), (1.8, .6, .12), door, (0, 0, .5))
cyl((-6.5, -7.0, .1), .3, .8, 6, red, .22); cyl((-6.5, -7.0, .9), .15, .3, 5, lamp)
beam('POINT', (1, .85, .45), 120, (-6.5, -7.0, 1.4))
for i in range(9):
    a = random.uniform(0, 6.28); r = random.uniform(2.5, 5.2)
    boulder((math.cos(a) * r, 1.5 + math.sin(a) * r, 2.0), random.uniform(.3, .6), grass)
# stormy dusk: cold teal key from the left, magenta rim behind, lamp is the warm glow
beam('SUN', (.45, .75, .9), 4, (-22, -10, 10), (0, 0, 5))
beam('SUN', (.9, .35, .6), 2, (16, 22, 9), (0, 0, 5))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == 'BACKGROUND').inputs['Color'].default_value = (.015, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
co.location = V((3, -52, 34)); co.rotation_euler = (V((0, 0, 6.5)) - co.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = co
