import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1061)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tone(c, e=0, r=.8):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*c, 1); b.inputs["Roughness"].default_value = r
    b.inputs["Emission Color"].default_value = (*c, 1); b.inputs["Emission Strength"].default_value = e
    return m
floor, wall, under, line = tone((.07, .07, .09)), tone((.05, .05, .07)), tone((.03, .03, .04)), tone((.14, .15, .2))
sphere_m, cube_m, cone_m, rim_m = tone((.9, .35, .08)), tone((.9, .75, .1)), tone((.9, .12, .1)), tone((.1, .5, .8))
glow = tone((1, .6, .2), 6)
def make(bm, m, p=(0, 0, 0), r=(0, 0, 0)):
    me = bpy.data.meshes.new("o"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("o", me); o.location = p; o.rotation_euler = r
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(p, s, m, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return make(bm, m, p, (0, 0, rz))
def cyl(p, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return make(bm, m, p, rot)
def ball(p, r, m, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts: v.co.z *= sq
    return make(bm, m, p)
def shine(kind, p, c, w, aim=None):
    L = bpy.data.lights.new("s", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor slab with a rough underside
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 20, v.co.y * 16, v.co.z * 3 - 1.5))
    if v.co.z < -1.5: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.6)))
make(bm, floor)
for i in range(8): slab((-9.5 + i * 2.7, 0, .02), (.06, 15, .02), line)
for j in range(7): slab((0, -7.5 + j * 2.5, .02), (20, .06, .02), line)
slab((0, 7.6, 0), (20, .5, 3.2), wall); slab((-9.8, 0, 0), (.5, 15.6, 3.2), wall)
for i in range(3): slab((-6 + i * 6, 7.3, 3.2), (1.6, .12, .12), glow)
# the three shapes, each on a small plinth, a glowing ring laid at its foot
for x, kind in ((-5.5, "cube"), (0, "sphere"), (5.5, "cone")):
    slab((x, 0, 0), (4.2, 4.2, .35), line); cyl((x, 0, .35), 1.9, .08, 10, rim_m)
    if kind == "cube": slab((x, 0, .35), (2.2, 2.2, 2.2), cube_m, .3)
    elif kind == "sphere": ball((x, 0, 2.0), 1.5, sphere_m)
    else: cyl((x, 0, .35), 1.5, 3.4, 8, cone_m, .15)
slab((0, 0, .02), (20, .05, .05), line)
# a few scattered blocks and a small stack for set dressing
for x, y, h in ((-8.5, -5, 1.2), (-8, -5.5, .8), (8.5, 4.5, 1.5), (7.8, 5.2, .9), (-2.5, -6, .7)):
    slab((x, y, 0), (1.2, 1.2, h), line, random.uniform(0, 1.5))
slab((0, 0, .03), (.5, .5, .5), glow)
# warm key from the left, cool blue rim from behind
shine("SUN", (-24, -10, 11), (1, .6, .25), 5, (0, 0, 1))
shine("SUN", (8, 26, 12), (.3, .5, 1), 2.4, (0, 0, 1))
shine("POINT", (0, 0, .8), (1, .6, .2), 250)
shine("POINT", (0, 7, 3.6), (1, .6, .2), 400)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .012, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.8)); co.location = t + Vector((4, -56, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
