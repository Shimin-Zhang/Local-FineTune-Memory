import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1357)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(r, g, b, glow=0, rough=.8, metal=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if glow: n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = glow
    return m
def make(kind, m, p, s, r=(0, 0, 0), n=6, top=1.0):
    if kind == "box": bpy.ops.mesh.primitive_cube_add(size=1)
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(vertices=n, depth=1)
    elif kind == "cone": bpy.ops.mesh.primitive_cone_add(vertices=n, radius2=top, depth=1)
    else: bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1)
    o = bpy.context.object; o.location = p; o.scale = s; o.rotation_euler = r
    o.data.materials.append(m); return o
def glow_at(p, col, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = col; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = p; sc.collection.objects.link(o)
tar, tar2, kerb, post, box, black, white = paint(.07, .07, .09), paint(.1, .1, .12), paint(.35, .35, .38), paint(.2, .22, .26, metal=.4, rough=.5), paint(.1, .11, .13), paint(.015, .015, .02), paint(.8, .8, .75)
red, amber, green, redg, amberg, greeng = paint(.6, .05, .05), paint(.7, .4, .05), paint(.1, .4, .1), paint(1, .06, .04, 14), paint(1, .55, .08, 14), paint(.1, 1, .25, 14)
yellow = paint(.9, .7, .05)
# street slab, kerb, zebra stripes, lane dashes
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=10.5, depth=2.2)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.1
me = bpy.data.meshes.new("slab"); bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("slab", me); sc.collection.objects.link(ob); me.materials.append(tar)
make("box", kerb, (0, 4.6, .06), (12, 1.2, .12)); make("box", kerb, (-4.8, 0, .06), (1.2, 10, .12))
for i in range(6): make("box", white, (-2.5 + i * 1.1, -1.2, .14), (.55, 2.6, .04))
for i in range(7): make("box", white, (-4.2 + i * 1.4, 1.8, .14), (.8, .22, .04))
# the traffic light: base, tapered post, head with visors, three glowing lenses
make("cyl", post, (0, 3.2, .5), (.8, .8, 1), n=8); make("cyl", post, (0, 3.2, 3.8), (.3, .3, 6.6), n=8)
make("cyl", post, (0, 3.2, 7.3), (.5, .5, .4), n=8)
make("box", box, (0, 3.2, 7.6), (1.9, 1.9, 4.4)); make("box", black, (0, 2.15, 7.6), (1.5, .15, 4.0))
for z, lit, off in ((9.2, redg, red), (7.6, amberg, amber), (6.0, greeng, green)):
    make("cyl", off, (0, 2.05, z), (.62, .62, .25), r=(math.pi / 2, 0, 0), n=8); make("cyl", lit, (0, 1.9, z), (.5, .5, .2), r=(math.pi / 2, 0, 0), n=8)
    make("cone", black, (0, 1.5, z + .62), (.8, .8, .45), r=(math.pi / 2, 0, 0), n=8, top=.35)
    glow_at((0, 1.0, z), (1, .1, .05) if z > 8 else ((1, .55, .1) if z > 7 else (.1, 1, .25)), 250)
make("box", black, (0, 3.2, 9.9), (2.1, 2.1, .3)); make("box", post, (0, 3.2, 5.4), (2.0, 2.0, .25))
# pedestrian pole with a small red-man sign, a bollard and a bin
make("cyl", post, (3.6, 3.4, 1.5), (.16, .16, 3), n=6); make("box", box, (3.6, 3.3, 3.2), (.9, .2, 1.1)); make("ico", redg, (3.6, 3.15, 3.4), (.28, .28, .28))
make("cyl", yellow, (-3.4, 2.6, .6), (.28, .28, 1.2), n=6); make("ico", yellow, (-3.4, 2.6, 1.4), (.3, .3, .3))
make("cyl", post, (3.4, 1.0, .8), (.5, .5, 1.6), n=7); make("cone", post, (3.4, 1.0, 1.7), (.55, .55, .3), n=7, top=.8)
# street lamp, a few cars parked on the kerb, a hydrant
make("cyl", post, (-5.8, 3.8, 3.5), (.18, .18, 7), n=6); make("box", post, (-5.2, 3.8, 7), (1.4, .2, .2)); make("box", greeng, (-4.5, 3.8, 6.9), (.5, .5, .2))
for x, c in ((-2.2, paint(.5, .1, .1)), (1.8, paint(.1, .2, .5))):
    make("box", c, (x, 4.5, .8), (2.4, 1.1, .8)); make("box", paint(.05, .05, .08), (x + .1, 4.5, 1.4), (1.3, .9, .5))
    for dx in (-.8, .8): make("cyl", black, (x + dx, 3.8, .35), (.35, .35, .2), r=(0, math.pi / 2, 0), n=7); make("cyl", black, (x + dx, 5.2, .35), (.35, .35, .2), r=(0, math.pi / 2, 0), n=7)
make("cyl", red, (-5.4, 2.4, .5), (.3, .3, .8), n=6); make("ico", red, (-5.4, 2.4, 1.0), (.28, .28, .28))
# night: wet blue street, sodium-orange rim from the left, teal key from behind
for col, w, p in (((.35, .55, 1), 4, (-24, -16, 10)), ((1, .55, .2), 2.4, (22, 14, 9))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .012, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3.8)); co.location = t + Vector((10, -41, 22))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
