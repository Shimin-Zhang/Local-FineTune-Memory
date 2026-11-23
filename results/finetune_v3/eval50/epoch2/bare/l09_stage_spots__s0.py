import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1546)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
mats = {}
def tint(name, rgb, glow=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .8
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    mats[name] = m
for k, c in (("floor", (.55, .55, .6)), ("trim", (.1, .1, .12)), ("wall", (.04, .04, .06)), ("truss", (.12, .12, .14)),
             ("barrel", (.2, .2, .22)), ("black", (.02, .02, .025))): tint(k, c)
for k, c, g in (("red", (1, .05, .05), 6), ("green", (.05, 1, .1), 6), ("blue", (.08, .2, 1), 6),
                ("pool_red", (1, .1, .08), 1.2), ("pool_green", (.1, 1, .15), 1.2), ("pool_blue", (.15, .3, 1), 1.2)): tint(k, c, g)
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(mats[m]); return o
def box(x, y, z, w, d, h, m, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mk(bm, m, (x, y, z), (0, 0, rz))
def drum(x, y, z, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, (x, y, z), rot)
def lamp(x, y, z, m, aim):
    p = Vector((x, y, z)); d = (Vector(aim) - p).normalized(); q = d.to_track_quat('-Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=.55, radius2=.35, depth=1.4)
    for v in bm.verts: v.co = q @ Vector((v.co.x, v.co.y, v.co.z * 1.4 + .7)) + p
    return mk(bm, m)
def light(kind, c, e, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = e
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# stage floor as the base: a tapered slab with a rough underside, plus a dark trim line around the edge
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=6, radius2=13.2, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .2)))
    v.co.z -= 1.5
mk(bm, "floor", (0, 0, 0), (0, 0, math.pi / 4))
for sx, sy, w, d in ((0, -11.6, 22.6, .5), (0, 11.6, 22.6, .5), (-11.6, 0, .5, 22.6), (11.6, 0, .5, 22.6)): box(sx, sy, 0, w, d, .25, "trim")
# back wall with a thin glowing line, and a side wall
box(0, 12.4, 0, 25, .8, 8.5, "wall"); box(-12.4, 0, 0, .8, 25, 8.5, "wall")
box(0, 11.95, 1.2, 24, .1, .2, "blue"); box(0, 11.95, 5.5, 24, .1, .15, "red")
# overhead truss with three spotlight barrels on clamps, each aimed at a different patch of floor
box(0, 0, 9.2, 22, .5, .5, "truss"); box(0, 0, 9.7, 22, .15, .15, "truss")
for sx in (-1, 1):
    for sy in (-1, 1): box(sx * 10.6, sy * 2.4, 0, .4, .4, 9.2, "truss", top=.6)
for i, (x, m, aim) in enumerate(((-5, "red", (-1, -2, 0)), (0, "green", (1, 2, 0)), (5, "blue", (-1, 2, 0)))):
    box(x, 0, 8.7, .3, .3, .6, "black"); drum(x, 0, 7.9, .25, .8, 6, "black")
    lamp(x, 0, 7.9, m, aim)
    light("POINT", {"red": (1, .05, .05), "green": (.05, 1, .1), "blue": (.1, .2, 1)}[m], 900, (x, 0, 7.6))
# the pools of light on the floor: overlapping translucent discs, each a little darker where they cross
for x, y, r, m in ((-1, -2, 4.2, "pool_red"), (1, 2, 4.2, "pool_green"), (-1, 2, 4.2, "pool_blue")):
    drum(x, y, .03, r, .05, 10, m)
for x, y in ((0, 0), (-1.2, 0), (1.2, 0)): drum(x, y, .09, 2.2, .04, 10, "black")
# a small round table with a glass and a stool, so the beams have something to catch
drum(2.5, -3.5, 0, 1.2, 1.5, 8, "trim"); drum(2.5, -3.5, 1.5, 1.5, .15, 8, "floor"); drum(3.2, -3.5, 1.65, .2, .5, 6, "pool_green")
drum(-4, 3.5, 0, .5, 1.1, 6, "trim"); drum(-4, 3.5, 1.1, .7, .15, 6, "floor")
# a speaker stack and a drum kit silhouette at the back, plus cables across the floor
for i in range(2): box(7.5, 9.5, i * 1.8, 2.4, 1.6, 1.8, "black", top=.95)
for i, (x, y) in enumerate(((8.5, 6.5), (9.5, 8.5), (7, 8.5))): drum(x, y, 0, .7, 1.2, 8, "trim")
for i in range(5): box(-6 + i * 3, -8 + (i % 2) * .5, .02, 2.4, .12, .06, "black", rz=random.uniform(-.3, .3))
# near-black stage night: deep blue-black key from the front left, a dim magenta rim from behind
light("SUN", (.3, .4, 1), 1.6, (-26, -20, 12), (0, 0, 3)); light("SUN", (.8, .2, .6), .7, (22, 24, 10), (0, 0, 3))
w = bpy.data.worlds.new("night"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.008, .008, .02, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3.5)); co.location = t + Vector((12, -62, 36))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
