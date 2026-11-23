import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1834)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, em=0, rough=.85):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*rgb, 1); n.inputs["Roughness"].default_value = rough
    if em: n.inputs["Emission Color"].default_value = (*rgb, 1); n.inputs["Emission Strength"].default_value = em
    return m
def solid(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("s"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("s", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def cube(x, y, z, w, d, h, m, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return solid(bm, m, (x, y, z), rot)
def cone(x, y, z, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return solid(bm, m, (x, y, z))
def glow(x, y, z, c, w):
    L = bpy.data.lights.new("g", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("g", L); o.location = (x, y, z); sc.collection.objects.link(o)
salt, salt2, salt3 = tint((.55, .48, .5), 0), tint((.45, .38, .45), 0), tint((.3, .26, .34), 0)
wood, wood2, stone = tint((.28, .17, .1), 0), tint((.2, .12, .08), 0), tint((.5, .47, .5), 0)
candle, lantern, halo = tint((1, .8, .4), 14), tint((1, .6, .2), 20), tint((1, .95, .8), 3)
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=10.5, depth=3)
for v in bm.verts:
    v.co.x *= 1.35; v.co.y *= 1.15
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.5, .3)))
    v.co.z -= 1.5
solid(bm, salt3)
# the cave: a back wall and a left wall, built from stacked salt blocks, with a carved relief on the back
for i in range(7):
    for j in range(3):
        cube(-7.5 + i * 2.5, 7.5, j * 1.8, 2.5, 1.2, 1.8, (salt, salt2, salt3)[(i + j) % 3])
for j in range(3):
    for k in range(3): cube(-10, -6 + k * 3, j * 1.8, 1.2, 3, 1.8, (salt, salt2, salt3)[(j + k) % 3])
cube(0, 6.9, 3.6, 12, .1, 2.6, stone)
for i in range(7):
    cube(-5 + i * 1.7, 6.8, 3.9, 1.2, .12, 1.8, salt3)
    if i % 2 == 0: cube(-5 + i * 1.7, 6.7, 4.4, .6, .15, .8, stone)
for i in range(3):
    cube(-1.8 + i * 1.8, 6.7, 4.2, .5, .15, 1.4, salt2)
# the altar: a pale plinth, a table, a cross, candles and a halo of light behind
cube(0, 5.6, 0, 3.6, 1.8, .8, stone); cube(0, 5.6, .8, 3.2, 1.4, .5, halo)
cube(0, 5.9, 1.3, 2.2, .9, .2, stone); cube(0, 6.2, 1.5, .2, .2, 1.6, halo); cube(0, 6.2, 2.2, .9, .2, .2, halo)
for sx in (-1, 1):
    cube(sx * 1.1, 5.9, 1.5, .18, .18, .5, stone); cone(sx * 1.1, 5.9, 2.0, .1, .3, 5, candle)
    glow(sx * 1.1, 5.9, 2.4, (1, .8, .4), 140)
glow(0, 5.4, 3.4, (1, .95, .8), 900)
# crystal chandeliers: rings, drops and a glowing core, hung from the rock
for cx, cy in ((-3.8, 3.2), (3.8, 3.2)):
    cube(cx, cy, 7.2, .06, .06, 2.6, wood2); cone(cx, cy, 6.8, .9, .25, 8, halo, .5); cone(cx, cy, 6.8, .2, .5, 6, halo, .05)
    for k in range(8):
        a = k * math.pi / 4; cone(cx + math.cos(a) * .85, cy + math.sin(a) * .85, 6.0, .12, .8, 4, halo, .03)
    glow(cx, cy, 6.4, (.9, .95, 1), 800)
# wooden pews in two rows, with a lantern-lit stair down to the nave floor
for r in range(4):
    for c in (-1, 1):
        cube(c * 2.4, 3.2 - r * 1.5, 0, 2.6, .6, .8, wood); cube(c * 2.4, 3.2 - r * 1.5 + .3, .8, 2.6, .1, .8, wood2)
for i in range(6):
    cube(-7.5, -1.0 - i * 1.0, 0, 3.0, 1.0, 1.0 - i * .17, stone)
    if i % 2 == 0:
        cube(-6.0, -1.0 - i * 1.0, 1.0 - i * .17, .15, .15, 1.2, wood2); cone(-6.0, -1.0 - i * 1.0, 2.2 - i * .17, .22, .4, 6, lantern, .15)
        glow(-6.0, -1.0 - i * 1.0, 2.5 - i * .17, (1, .6, .2), 120)
cube(-7.5, -6.8, 0, 3.0, 1.2, .3, stone)
# salt stalagmites and a few fallen crystals
for x, y, h in ((-8.5, 4.5, 3.2), (-8.8, 0, 2.2), (8.5, 5, 3.0), (8.2, -3, 2.4), (-1.5, 7.2, 2.0)):
    cone(x, y, 0, .9, h, 6, salt2, .15)
for x, y in ((5.5, 1.5), (-4, 0), (1, 1.5)): cone(x, y, 0, .3, .8, 5, halo, .05)
for col, w, p in (((.6, .55, .9), 4.5, (-26, -16, 10)), ((.5, .7, .8), 2.5, (24, 22, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 3, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.015, .012, .03, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 2, 2.5)); co.location = t + Vector((20, -46, 28))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
