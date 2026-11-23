import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1183)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
snow, drift, wall, roof, cross, wood, metal, bag, flame, powder = (dye(c) for c in (
    (.5, .56, .68), (.36, .42, .56), (.28, .14, .1), (.12, .13, .18), (.8, .05, .05), (.2, .12, .07), (.2, .22, .26), (.7, .65, .5), (1, .45, .1), (.7, .75, .85)))
window = dye((1, .6, .2), 10); mercury = dye((1, .1, .05), 12)
def put(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("p"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("p", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(at, w, d, h, m, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return put(bm, m, at, (rx, 0, rz))
def pole(at, r, h, m, n=6, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return put(bm, m, at, rot)
def drift(at, sx, sy, sz, m):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)) * random.uniform(.85, 1.15)
    return put(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    l = bpy.data.lights.new("l", kind); l.color, l.energy = c, w
    o = bpy.data.objects.new("l", l); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# snowy mountain base
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=5, radius2=13, depth=4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.2, .2)
    v.co.z -= 2
put(bm, snow)
for i in range(9):
    a = i * .7 + random.uniform(-.3, .3); r = random.uniform(8, 11)
    drift((math.cos(a) * r, math.sin(a) * r, .2), random.uniform(1.8, 3), random.uniform(1.2, 2), random.uniform(.7, 1.2), drift)
# the hut
hx, hy = 0, 2.5
box((hx, hy, 0), 8, 5.4, 3.4, wall); box((hx, hy, 3.4), 8.6, 6.0, .4, roof)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 8.6, v.co.y * 6.0, (v.co.z + .5) * 1.6))
    if v.co.z > .8: v.co.y *= .15
put(bm, roof, (hx, hy, 3.8))
box((hx, hy - 2.8, 3.4), 8.4, .5, .25, snow)
# red cross on the front
box((hx - 2.6, hy - 2.72, 1.5), .9, .12, 2.2, cross); box((hx - 2.6, hy - 2.72, 2.2), 2.2, .12, .9, cross)
# door and window
box((hx + 1.6, hy - 2.72, 0), 1.4, .15, 2.3, wood); box((hx + 1.6, hy - 2.8, 2.3), 1.8, .12, .3, wood)
box((hx + 4.1, hy - 2.72, 1.2), 1.8, .12, 1.2, window); box((hx + 4.1, hy - 2.75, 1.7), .12, .1, .12, wood)
lamp("POINT", (1, .6, .2), 350, (hx + 4.1, hy - 3.6, 1.8))
# stove chimney
pole((hx - 3, hy + .8, 3.8), .35, 3.2, metal, 6); pole((hx - 3, hy + .8, 7.0), .5, .3, metal, 6); pole((hx - 3, hy + .8, 7.3), .35, .3, roof, 6)
# thermometer on a post
pole((hx + 5.8, hy - 3.6, 0), .1, 3.2, wood, 5); box((hx + 5.8, hy - 3.7, 1.4), .5, .35, 1.8, snow)
box((hx + 5.8, hy - 3.9, 1.6), .1, .1, 1.2, mercury); pole((hx + 5.8, hy - 3.9, 1.4), .18, .15, mercury, 6)
# stretcher sled with a body bag
box((hx - 5.5, hy - 4.2, .3), 4.4, 1.2, .18, wood)
for sy in (-.5, .5): box((hx - 5.5, hy - 4.2 + sy, .1), 4.4, .1, .1, wood)
box((hx - 5.5, hy - 4.2, .48), 3.2, .9, .5, bag); box((hx - 5.5, hy - 4.2, .98), 1.2, .9, .15, cross)
for i in range(4): box((hx - 5.5 + (i - 1.5) * .8, hy - 4.2, .48), .08, .95, .5, wood)
# rope bags on the wall and a pole
for i in range(4): box((hx - 5.0 + i * .7, hy - 2.72, 1.0 + (i % 2) * .9), .55, .3, .8, bag if i % 2 else cross)
pole((hx + 5.5, hy - 4.2, 0), .06, 2.4, wood, 5); box((hx + 5.5, hy - 4.2, 2.0), .5, .5, .6, bag)
# powder: flakes and gusts
for i in range(80):
    x, y, z = random.uniform(-11, 11), random.uniform(-10, 10), random.uniform(.5, 9)
    if abs(x - hx) < 5 and abs(y - hy) < 4: continue
    box((x, y, z), random.uniform(.12, .25), .1, .1, powder, random.random() * 3)
for i in range(6):
    a = random.uniform(0, 6.28); r = random.uniform(8, 10.5)
    drift((math.cos(a) * r, math.sin(a) * r, .6), 3.5, .6, .25, powder)
# blue storm light, pale moon behind
lamp("SUN", (.5, .65, 1), 5, (-24, -20, 12), (0, 0, 2)); lamp("SUN", (.8, .85, 1), 2.2, (22, 24, 10), (0, 0, 2))
w = bpy.data.worlds.new("storm"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .02, .04, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 1, 3.5)); co.location = t + Vector((12, -56, 34))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
