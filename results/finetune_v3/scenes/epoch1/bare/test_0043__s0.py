import bpy, bmesh, random, math
from mathutils import Vector
random.seed(536)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def colour(rgb, glow=0, rough=.9):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if glow: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = glow
    return m
moss, loam, bark, leaf1, leaf2, leaf3, stone, toad, leafA, leafB, firefly, bark2 = (colour(c) for c in (
    (.05, .16, .06), (.14, .09, .06), (.2, .12, .08), (.04, .2, .07), (.08, .28, .08), (.12, .32, .06), (.3, .3, .27), (.12, .3, .1), (.1, .22, .08), (.2, .3, .08), (1, .9, .3), (.13, .08, .06)))
fire = colour((1, .85, .3), glow=20)
def shape(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(at, s, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return shape(bm, m, at, rot)
def stalk(a, b, t, m):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return shape(bm, m)
def leaf(at, r, m, tilt=0, yaw=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=r, radius2=r * .1, depth=.12)
    return shape(bm, m, at, (tilt, 0, yaw))
def glowlight(c, w, at):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = at; sc.collection.objects.link(o)
# forest floor
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=9, radius1=5, radius2=10, depth=3)
for v in bm.verts:
    v.co.z -= 1.5
    if v.co.z < -1: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.5, .3)))
    else: v.co.z += random.uniform(-.1, .1)
shape(bm, moss)
# stepping stones along a winding path
for i in range(9):
    x = -5.5 + i * 1.35; y = -2.2 + math.sin(i * .7) * 1.4
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=.8, radius2=.7, depth=.18)
    for v in bm.verts: v.co.x *= random.uniform(.85, 1.15); v.co.y *= random.uniform(.85, 1.15)
    shape(bm, stone, (x, y, .06), (0, 0, i))
# toad on a flat stone, with lantern and a small fire bowl
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=1.4, radius2=1.2, depth=.5)
for v in bm.verts: v.co.z += .25
shape(bm, stone, (-2.2, 1.2, 0))
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=.9)
for v in bm.verts: v.co.z *= .65; v.co.x *= 1.2
shape(bm, toad, (-2.2, 1.2, .6))
for s in (-1, 1):
    for x in (-.3, .3):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.28); shape(bm, toad, (-2.2 + x, 1.2 + s * .55, .95))
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.14); shape(bm, firefly, (-2.2 + x, 1.2 + s * .6, 1.15))
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.12); shape(bm, firefly, (-2.2, 1.2, 1.2))
for x, y in ((-4.5, -1.0), (3.5, 2.8)):
    cube((x, y, 0), (.2, .2, 1.2), bark); cube((x, y, 1.2), (.5, .5, .6), fire)
    glowlight((1, .8, .3), 160, (x, y, 1.7))
# wide-leaf plants: big leaves on stems, in clusters
for cx, cy, n in ((-6.5, 3.5, 7), (-3.5, 5.5, 6), (1.5, 5.8, 7), (6.5, 4.5, 6), (-7, -2.5, 5), (7, -.5, 5), (0, -5.5, 5), (-5.5, -5.5, 4), (4.5, -5, 4)):
    for k in range(n):
        a = k * 6.28 / n + random.uniform(-.3, .3); r = random.uniform(.5, 1.4)
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        h = random.uniform(.8, 1.6)
        stalk((x, y, 0), (x + math.cos(a) * .4, y + math.sin(a) * .4, h), .1, leafA)
        leaf((x + math.cos(a) * .6, y + math.sin(a) * .6, h + .1), random.uniform(.7, 1.0), (leaf1, leaf2, leaf3)[k % 3], .5, a)
# old trees: twisted trunks, buttress roots, canopy
for tx, ty, h, lean in ((-3.5, -3.5, 8, .15), (3.8, -2.5, 7, -.12), (-1, 3.2, 9, .1)):
    for k in range(4):
        a = k * 1.57 + tx
        stalk((tx + math.cos(a) * 1.2, ty + math.sin(a) * 1.2, 0), (tx + math.cos(a) * .3, ty + math.sin(a) * .3, 1.2), .5, bark2)
    stalk((tx, ty, 0), (tx + lean * h, ty, h), 1.1, bark)
    for k in range(5):
        a = k * 1.26; r = 2.4 - k * .25
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
        for v in bm.verts: v.co.z *= .6; v.co += Vector((random.uniform(-.5, .5), random.uniform(-.5, .5), random.uniform(-.4, .4)))
        shape(bm, (leaf2, leaf1)[k % 2], (tx + lean * h + math.cos(a) * 2.2, ty + math.sin(a) * 2.2, h + 1.5 + k * .5))
# hammock between two trunks
for hx, hy in ((-6.2, 1.5), (-3.2, 4.8)):
    stalk((hx, hy, 0), (hx + .2, hy, 4.2), .45, bark)
stalk((-6.0, 1.5, 3.0), (-3.4, 4.8, 3.0), .1, leafB)
for k in range(7):
    t = k / 6; x = -6.0 + t * 2.6; y = 1.5 + t * 3.3; z = 3.0 - math.sin(t * math.pi) * 1.0
    cube((x, y, z), (.35, .5, .08), leafB, (0, 0, math.atan2(3.3, 2.6)))
# dappled light: warm key from the left, cool rim, fireflies
for c, w, at in (((1, .75, .35), 5.5, (-24, -14, 9)), ((.3, .5, .8), 2.2, (20, 22, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .03, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 2)); co.location = t + Vector((12, -40, 26))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
