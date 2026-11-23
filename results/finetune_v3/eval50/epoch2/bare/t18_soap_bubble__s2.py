import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1333)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def paint(r, g, b, glow=0):
    m = bpy.data.materials.new("p"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (r, g, b, 1); n.inputs["Roughness"].default_value = .5
    if glow:
        n.inputs["Emission Color"].default_value = (r, g, b, 1); n.inputs["Emission Strength"].default_value = glow
    return m
def make(kind, m, x, y, z, sx, sy, sz, rot=(0, 0, 0), n=8, top=1.0):
    if kind == "ball": bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=.5, location=(x, y, z))
    elif kind == "cyl": bpy.ops.mesh.primitive_cylinder_add(vertices=n, radius=.5, depth=.5, location=(x, y, z))
    elif kind == "cone": bpy.ops.mesh.primitive_cone_add(vertices=n, radius1=.5, radius2=.5 * top, depth=.5, location=(x, y, z))
    else: bpy.ops.mesh.primitive_cube_add(size=.5, location=(x, y, z))
    o = bpy.context.object; o.scale = (sx, sy, sz); o.rotation_euler = rot; o.data.materials.append(m)
    return o
def shine(kind, c, w, x, y, z, aim=None):
    d = bpy.data.lights.new("s", kind); d.color = c; d.energy = w
    o = bpy.data.objects.new("s", d); o.location = (x, y, z); sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
lawn, pond, rim = paint(.07, .17, .13), paint(.04, .13, .22), paint(.12, .2, .17)
bark, leaf, leaf2 = paint(.17, .1, .07), paint(.06, .22, .12), paint(.1, .3, .15)
petal, rock = paint(.45, .3, .4), paint(.25, .26, .28)
bands = [paint(.9, .1, .12), paint(.95, .4, .05), paint(.95, .8, .05), paint(.1, .8, .2), paint(.05, .5, .9), paint(.1, .15, .9), paint(.5, .1, .9)]
# round lawn island with a small pond
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=4, radius2=9.5, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .2)))
    else: v.co.z += random.uniform(-.08, .08)
    v.co.z -= 1.5
me = bpy.data.meshes.new("island"); bm.to_mesh(me); bm.free()
o = bpy.data.objects.new("island", me); sc.collection.objects.link(o); o.data.materials.append(lawn)
make("cyl", pond, 3.5, -3, .05, 4.5, 3.4, .12, n=8)
for i in range(8):
    a = i * .8; make("ball", rim, math.cos(a) * 9.3, math.sin(a) * 9.3, 0, 1.6, 1.4, .8, rot=(0, 0, a))
# the great bubble: seven thin rainbow shells, each a little larger than the last
for k, m in enumerate(bands):
    make("ball", m, 0, 0, 5.2, 7.0 + k * .16, 7.0 + k * .16, 7.0 + k * .16)
# a few smaller bubbles drifting away, each with a pale shell and a rim
for x, y, z, r in ((5.5, 1.5, 3.0, 1.3), (-5.2, 2.5, 7.0, 1.0), (3.0, -4.0, 9.0, .8)):
    make("ball", bands[(int(x) + 3) % 7], x, y, z, r, r, r)
    make("ball", bands[(int(y) + 5) % 7], x, y, z, r * 1.1, r * 1.1, r * 1.1)
# pond-side willow, flower beds and rocks
make("cyl", bark, -6.5, 3.5, 1.8, .9, .9, 3.6, n=6)
for i in range(7):
    a = i * .9
    make("cone", leaf if i % 2 else leaf2, -6.5 + math.cos(a) * 1.8, 3.5 + math.sin(a) * 1.8, 4.2, 1.2, 1.2, 3.0, rot=(math.sin(a) * .3, -math.cos(a) * .3, 0), n=5, top=.2)
for i in range(14):
    x, y = random.uniform(-8, 8), random.uniform(-7, 7)
    if x * x + y * y > 45 or (x - 3.5) ** 2 + (y + 3) ** 2 > 10:
        make("cyl", bark, x, y, .3, .1, .1, .6, n=4)
        make("ball", petal, x, y, .75, .45, .45, .45)
for i in range(5): make("ball", rock, random.uniform(-8, 8), random.uniform(-8, 8), .2, random.uniform(.6, 1.2), .8, .6)
# light: cool moon key from the left, magenta rim from behind, rainbow spill
shine("SUN", (.6, .75, 1), 4.5, -20, -12, 9, (0, 0, 4))
shine("SUN", (.9, .3, .8), 2.5, 16, 18, 10, (0, 0, 4))
for i, c in enumerate(((1, .2, .2), (.2, .9, .3), (.2, .4, 1))):
    shine("POINT", c, 300, -3 + i * 3, -3, 5.2)
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .015, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 4.5)); co.location = t + Vector((6, -42, 20))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
