import bpy, bmesh, math, random
from mathutils import Vector
random.seed(971)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, em=0, rough=.9):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    return m
grass, sand, plank, plank2, steel = col((.07, .16, .07)), col((.4, .32, .2)), col((.35, .2, .1)), col((.25, .14, .08)), col((.3, .32, .36), rough=.5)
mats = [col((.7, .12, .1)), col((.1, .35, .7)), col((.9, .6, .05)), col((.1, .5, .25))]
tube, bulb, bulb2, hoop1, hoop2, hoop3 = col((.8, .45, .1)), col((1, .7, .2), 9), col((.2, .8, 1), 9), col((.85, .1, .1)), col((.9, .7, .05)), col((.1, .5, .8))
def mesh(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("m"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("m", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(w, d, h, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return mesh(bm, m, at, rot)
def tube_(r1, r2, h, n, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mesh(bm, m, at, rot)
def ball(r, m, at, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co.z *= sq
    return mesh(bm, m, at)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# grassy base with a sand pit under the tower
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=14.5, depth=3.4)
for v in bm.verts:
    v.co.x *= 1.15
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.4, .2)))
    v.co.z -= 1.7
mesh(bm, grass)
tube_(8.4, 8.4, .12, 10, sand, (0, 0, 0))
# tower: four legs, cross braces, three decks, ladder
for sx in (-1, 1):
    for sy in (-1, 1): tube_(.22, .2, 10, 5, plank2, (sx * 2.4, sy * 2.4, 0))
for z in (3.3, 6.6):
    for sx in (-1, 1):
        box(4.8, .18, .18, plank2, (0, sx * 2.4, z - .1)); box(.18, 4.8, .18, plank2, (sx * 2.4, 0, z - .1))
    for sx in (-1, 1): box(.1, 4.6, 3.2, plank2, (sx * 2.4, 0, z), (.4, 0, 0)); box(4.6, .1, 3.2, plank2, (0, sx * 2.4, z), (0, -.4, 0))
for z, r in ((3.4, 3.1), (6.7, 2.7), (10, 2.3)):
    tube_(r, r, .22, 8, plank, (0, 0, z))
    for k in range(8):
        a = k * math.pi / 4 + .39
        box(.12, .12, .9, plank2, (math.cos(a) * r * .98, math.sin(a) * r * .98, z + .22))
tube_(.1, .1, 10, 5, steel, (-.6, 0, .2))
for k in range(30): tube_(.12, .12, .08, 5, steel, (-.6, 0, .6 + k * .3), (0, math.pi / 2, 0)).location.x = -.6
tube_(2.3, 2.3, .1, 8, plank, (0, 0, 10.4)); tube_(.5, .5, 1.2, 6, plank2, (0, 0, 10.4)); tube_(.5, .5, .1, 6, bulb, (0, 0, 11.6))
for k in range(8):
    a = k * .785
    tube_(.12, .12, .1, 5, bulb if k % 2 else bulb2, (math.cos(a) * 2.2, math.sin(a) * 2.2, 10.45), (0, math.pi / 2, 0))
# spiral slide: chute panels and side rails winding down
N = 40
for k in range(N):
    a0, a1 = k * .27, (k + 1) * .27
    r = 4.4 + k * .03; z = 9.6 - k * .24
    c, s = math.cos(a0), math.sin(a0)
    for off, m in ((-.5, tube), (.5, tube)):
        box(.12, 1.2, .1, m, (r * c - off * s, r * s + off * c, z + .15), (0, 0, a0))
    box(1.1, 1.2, .1, tube, (r * c, r * s, z), (0, 0, a0))
for k in range(4):
    a = 1.2 + k * 1.6
    box(.2, .2, 1.6, plank2, (4.6 * math.cos(a), 4.6 * math.sin(a), 0))
# landing mats in front of the slide exit
for k in range(4): box(3.4, 1.5, .15, mats[k % 4], (-1.0 + k * .1, -7.2 + k * .9, k * .05), (0, 0, .1 * (k - 1.5)))
# hoop-la stall: striped canopy, counter, hoops on stands, a stack of rings
sx0, sy0 = 9.0, -3.0
for dx in (-2.4, 2.4):
    for dy in (-1.6, 1.6): tube_(.1, .1, 3.2, 5, plank2, (sx0 + dx, sy0 + dy, 0))
for k in range(8): box(.55, 4.2, .1, hoop1 if k % 2 else hoop2, (sx0 - 2.4 + k * .65 + .27, sy0, 3.2), (0, 0, 0))
box(5.2, .3, .1, plank2, (sx0, sy0 + 2.0, 3.3))
box(4.6, 1.0, .9, plank, (sx0, sy0 + 1.2, 0)); box(4.8, 1.1, .12, plank2, (sx0, sy0 + 1.2, .9))
for k in range(5): tube_(.5, .5, .08, 8, (hoop1, hoop2, hoop3)[k % 3], (sx0 - 1.8 + k * .9, sy0 - 1.0, .5 + (k % 2) * .1), (math.pi / 2, 0, 0))
tube_(.1, .1, 1.0, 5, steel, (sx0 - 1.0, sy0 - 1.4, 0)); tube_(.1, .1, 1.0, 5, steel, (sx0 + 1.0, sy0 - 1.4, 0))
box(2.0, .1, .1, steel, (sx0, sy0 - 1.4, 1.0))
for k in range(3): tube_(.6, .6, .08, 8, (hoop1, hoop2, hoop3)[k], (sx0 + .2 + k * .1, sy0 + 1.0, 1.0 + k * .1), (math.pi / 2, 0, 0))
lamp("POINT", (1, .7, .2), 500, (sx0, sy0 - .5, 2.8))
# string lights from the tower to the stall, and a flag
for k in range(9):
    t = k / 8; p = Vector((0, 0, 9.8)).lerp(Vector((sx0, sy0, 3.4)), t) + Vector((0, 0, -1.2 * math.sin(t * math.pi)))
    ball(.22, bulb if k % 2 else bulb2, p)
tube_(.06, .06, 3.2, 5, steel, (0, 0, 11.6)); box(1.2, .06, .7, mats[0], (.6, 0, 13.6))
lamp("POINT", (1, .7, .2), 400, (0, 0, 12.4))
for i in range(12):
    a = random.uniform(0, 6.28); r = random.uniform(11, 14)
    ball(random.uniform(.3, .6), col((.1, .25, .1)), (r * math.cos(a) * 1.1, r * math.sin(a), .1), .7)
lamp("SUN", (1, .5, .22), 5, (-26, -14, 9), (0, 0, 4)); lamp("SUN", (.3, .5, .9), 2.2, (22, 20, 12), (0, 0, 4))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .04, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((2, 0, 5.5)); co.location = t + Vector((-14, -66, 40))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
