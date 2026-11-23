import bpy, bmesh, math, random
from mathutils import Vector as V
random.seed(11)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def tone(rgb, em=0, rough=.5, metal=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location = at; o.rotation_euler = rot
    o.data.materials.append(m); sc.collection.objects.link(o); return o
def slab(w, d, h, at, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = V((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return put(bm, m, at, rot)
def cyl(r, h, n, at, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at, rot)
def ball(r, at, m, sq=(1, 1, 1)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co = V((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2]))
    return put(bm, m, at)
def beam(kind, rgb, p, at, aim=None):
    L = bpy.data.lights.new("b", kind); L.color = rgb; L.energy = p
    o = bpy.data.objects.new("b", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (V(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()

white, white2, glass, liquid, gold = tone((.62, .62, .64), rough=.3), tone((.5, .5, .52), rough=.3), tone((.7, .8, .85), rough=.08), tone((1, .55, .2), 3), tone((.9, .65, .2), rough=.3, metal=.8)
amber, cap, paper, wood, rose = tone((.9, .4, .1), 4), tone((.08, .08, .1), rough=.4), tone((.75, .72, .66), rough=.9), tone((.3, .2, .12), rough=.8), tone((.8, .2, .3), 2)

# round studio base, pale, with a soft darker rim
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=12, depth=2.2)
for v in bm.verts:
    v.co.z -= 1.1
    if v.co.z < 0: v.co += V((random.uniform(-.8, .8), random.uniform(-.8, .8), random.uniform(-1.2, .2)))
put(bm, white2)
cyl(11.8, .12, 10, (0, 0, 0), white)
cyl(6.5, .5, 10, (0, 0, .05), white2)
cyl(6.2, .1, 10, (0, 0, .5), white)
# the bottle: faceted glass body, glowing amber liquid inside, shoulders, neck, collar, cap
cyl(2.0, .3, 8, (0, 0, .6), glass)
cyl(1.8, 3.2, 8, (0, 0, .9), liquid)
cyl(2.1, 3.4, 8, (0, 0, .8), glass, 2.1)
cyl(2.0, 1.0, 8, (0, 0, 4.2), glass, .75)
cyl(.75, 1.0, 8, (0, 0, 5.2), glass)
cyl(.95, .35, 8, (0, 0, 5.0), gold)
cyl(.9, 1.8, 8, (0, 0, 5.55), cap, .75)
cyl(.78, .15, 8, (0, 0, 7.35), gold)
cyl(.12, .2, 5, (0, 0, 7.4), gold)
# paper label with a gold frame and a rose emblem
slab(2.0, .12, 1.6, (0, -1.98, 1.6), paper)
slab(1.7, .1, 1.3, (0, -2.06, 1.75), white)
ball(.35, (0, -2.12, 2.4), rose, (1, .25, 1))
slab(.5, .1, .12, (0, -2.12, 1.95), gold)
# a few props: a folded box, a sprig, loose petals, a small dropper tray
slab(2.6, 1.6, .9, (7, -2, .05), paper, (0, 0, .4)); slab(2.7, .15, .12, (7, -2, .95), rose, (0, 0, .4))
for i in range(5): ball(.22, (-5.5 + i * .5, -4.5 + (i % 2) * .4, .12), rose, (1, 1, .5))
slab(1.8, 1.0, .15, (-5.5, 1, .05), white2); cyl(.18, 1.4, 5, (-5.5, 1, .15), glass, rot=(0, math.pi / 2, 0))
# soft light from above: cool key high on the front-left, warm rim from behind-right
beam("SUN", (.9, .95, 1), 4.2, (-14, -10, 24), (0, 0, 2)); beam("SUN", (1, .75, .5), 2.2, (16, 16, 10), (0, 0, 2))
beam("POINT", (1, .5, .15), 900, (0, -1.5, 2.4)); beam("POINT", (1, .5, .15), 300, (0, 0, 6))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .02, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
co.location = V((5, -42, 25)); co.rotation_euler = (V((0, 0, 3.2)) - co.location).to_track_quat('-Z', 'Y').to_euler()
