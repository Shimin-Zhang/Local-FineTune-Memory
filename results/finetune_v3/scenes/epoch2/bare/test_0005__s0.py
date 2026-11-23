import bpy, bmesh, random, math
from mathutils import Vector
random.seed(377)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def hue(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("h"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
sea, snow, ice, wood, plank, tin, red, cream, dark, glass, rock, fire, pump, green = (
    hue((.02, .09, .13), rough=.15), hue((.5, .56, .66)), hue((.45, .6, .7)), hue((.2, .13, .08)), hue((.35, .24, .14)), hue((.25, .28, .32)), hue((.55, .08, .06)),
    hue((.6, .55, .45)), hue((.04, .04, .05)), hue((1, .75, .35), 9), hue((.18, .2, .26)), hue((1, .5, .1), 14), hue((.1, .35, .25)), hue((.2, .4, .15)))
def make(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, at, rot)
def strut(a, b, t, m):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return make(bm, m)
def post(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, at, rot)
def peak(at, r, h, m):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=r, radius2=r * .12, depth=h)
    for v in bm.verts: v.co.z += h / 2; v.co += Vector((random.uniform(-.3, .3), random.uniform(-.3, .3), random.uniform(-.2, .2)))
    return make(bm, m, at)
def beacon(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=6, radius2=13.5, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.2, .3)))
make(bm, sea)
# cold blue mountains behind, snow caps, and a frozen shore
for i, (x, y, r, h) in enumerate(((-9, 9, 3.5, 7), (-3, 10.5, 4, 9), (4, 10, 3.8, 8), (10, 8, 3, 6))):
    peak((x, y, 0), r, h, rock); peak((x, y, h * .72), r * .38, h * .28, snow)
slab((0, 10.5, 0), (20, 3, .3), ice)
# floating dock: planks on piles, with a ramp down to the water
for i in range(14): slab((-3.5, -7 + i * .9, .55), (2.6, .8, .12), plank if i % 2 else wood)
for i in range(7):
    for sx in (-1.3, 1.3): post((-3.5 + sx, -6.6 + i * 1.8, -.2), .15, 1.1, 5, wood)
for i in range(6): slab((-3.5, -9 + i * .5, .1 * (5 - i) + .02), (2.6, .5, .1), plank)
# boathouse on stilts with a lit window and a sloped tin roof
for sx in (-1, 1):
    for sy in (-1, 1): post((4.5 + sx * 2, -4 + sy * 1.4, 0), .2, 1.6, 5, wood)
slab((4.5, -4, 1.6), (5, 3.6, .2), plank)
slab((4.5, -4, 1.8), (4.4, 3.2, 2.2), wood)
slab((4.5, -4, 4.0), (5.4, 4.0, .2), tin, rot=(0, 0, 0))
slab((2.7, -4, 1.8), (.15, 1.8, 1.7), dark); slab((4.5, -5.65, 2.5), (1.2, .1, .9), glass)
beacon("POINT", (1, .7, .3), 500, (4.5, -6.5, 2.6))
for i in range(3): slab((4.5, -4 + (i - 1) * 1.2, 1.8), (.1, .1, 2.3), plank)
# the plane on a cradle in the water: floats, fuselage, wings, tail, cockpit
px, py = -8.5, -1.5
for s in (-1, 1):
    post((px, py + s * 1.8, -.6), .45, 5, 6, cream, rot=(0, math.pi / 2, 0)).location.x = px - 2.5
slab((px, py, -.3), (.6, .6, .6), wood); slab((px, py, .3), (.5, 3.6, .15), wood)
post((px, py, .45), .6, 5.2, 7, cream, rot=(0, math.pi / 2, 0)).location.x = px - 2.6
slab((px + .3, py, 1.2), (4.6, .15, .15), red); slab((px - .2, py, 1.0), (.9, 3.2, .1), red)
slab((px - 2.3, py, 1.0), (.1, 1.8, .1), red); slab((px - 2.5, py, 1.0), (.1, .1, 1.0), red)
slab((px + .9, py, 1.0), (1.3, 1.0, .6), glass)
slab((px + 3.0, py, .9), (.2, .2, .15), fire)
beacon("POINT", (1, .5, .1), 300, (px + 3.6, py, 1.2))
# gas pump with a glowing globe and a hose, plus a bench and barrels
slab((-1, -1, 0), (1.0, .8, 1.6), green); slab((-1, -1, 1.6), (.7, .5, .5), pump)
beacon("POINT", (.2, 1, .6), 250, (-1, -1.6, 2.4))
slab((-1, -1.45, .5), (.5, .05, .5), glass)
for i in range(3): post((-2 + i * .9, -.2, 0), .35, .9, 7, red if i == 1 else tin)
# fire barrel on the dock, lit
post((-3.5, -4, .7), .4, .7, 7, dark); post((-3.5, -4, 1.4), .3, .3, 6, fire)
beacon("POINT", (1, .5, .1), 400, (-3.5, -4, 2.2))
beacon("SUN", (.6, .75, 1), 4.5, (-24, -22, 12), (0, 0, 2)); beacon("SUN", (.9, .5, .6), 2.2, (22, 24, 10), (0, 0, 2))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3)); co.location = t + Vector((6, -56, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
