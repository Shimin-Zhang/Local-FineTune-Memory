import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1222)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def tint(rgb, glow=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
mud, plank, white, roofm, water, dark, moss, leaf, boat, skin, cloth, cane, lamp = (tint(c) for c in (
    (.16, .13, .09), (.22, .13, .08), (.38, .38, .36), (.1, .1, .12), (.05, .14, .16), (.06, .05, .05), (.25, .25, .12), (.08, .17, .08), (.3, .1, .07), (.55, .38, .28), (.6, .55, .4), (.3, .22, .12), (1, .65, .25)))
lamp = tint((1, .65, .25), 14)
def form(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("f"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("f", me); o.location = loc; o.rotation_euler = rot
    sc.collection.objects.link(o); me.materials.append(m); return o
def cube(m, x, y, z, w, d, h, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * w, v.co.y * d, (v.co.z + .5) * h))
    return form(bm, m, (x, y, z), (rx, 0, rz))
def post(m, x, y, z, r, h, n=6, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return form(bm, m, (x, y, z))
def limb(m, a, b, t):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * (b - a).length)) + a
    return form(bm, m)
def blob(m, x, y, z, sx, sy, sz, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1)
    for v in bm.verts: v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz)) * random.uniform(.85, 1.15)
    return form(bm, m, (x, y, z), rot)
def light(c, w, p):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = p; sc.collection.objects.link(o)
# bank of mud at the back, bayou in front, a plank landing
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 24, v.co.y * 22, v.co.z * 2.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-1, 1), v.co.y * .6 + random.uniform(-1, 1), v.co.z - random.uniform(0, 1.6)))
form(bm, mud, (0, 0, -1.1))
cube(water, 0, -8.2, .02, 24, 7.6, .12)
for i in range(11): cube(plank, 0, -3.8 + i * .5, 0, 13, .46, .22)
# blocks: four pairs of posts, with the house raised on them
for x in (-5.2, -1.7, 1.7, 5.2):
    for y in (1.0, 5.2): post(dark, x, y, .22, .2, 2.0, 5)
cube(white, 0, 3.1, 2.2, 12.4, 5.8, .3)
# shotgun house: long, narrow, with two rooms end to end
cube(white, 0, 3.4, 2.5, 11.4, 3.4, 3.6)
for x in (-2.8, 2.8): cube(roofm, x, 3.4, 6.1, 6.4, 4.4, .25, 0, -.12)
for x in (-2.8, 2.8): cube(roofm, x, 3.4, 6.1, 6.4, 4.4, .25, 0, .12)
cube(roofm, 0, 3.4, 6.35, 1.6, 4.4, .3)
cube(dark, 0, 1.62, 2.5, .2, .1, 3.6)
cube(white, -5.6, 1.5, 2.5, .3, .1, 3.6); cube(white, 5.6, 1.5, 2.5, .3, .1, 3.6)
cube(dark, 0, 1.62, 2.5, .2, .1, 3.6)
# deep porch along the front: posts, railing, roof, steps
for x in (-5.4, -2.7, 0, 2.7, 5.4): post(dark, x, -.3, 2.5, .12, 2.2)
cube(plank, 0, -.3, 2.5, 11.4, 2.6, .15)
cube(roofm, 0, -.3, 4.7, 11.6, 3.0, .2)
for x in (-5.4, 5.4):
    for y in (-1.5, .9): post(dark, x, y, 2.65, .08, .9)
cube(dark, 0, -1.5, 3.3, 11.4, .1, .1); cube(dark, 0, .9, 3.3, 11.4, .1, .1)
for i in range(11): cube(plank, -5.4 + i * 1.08, -1.5, 2.65, .1, .1, .7)
for i in range(3): cube(plank, 0, -1.9 - i * .5, 2.0 - i * .5, 3.0, .5, .5)
# rocking chair with a figure
for s in (-1, 1): limb(cane, (-3.2, -1.0, s * .5), (-2.0, -1.0, s * .5), .08); limb(cane, (-3.3, -1.0, s * .1), (-2.2, -1.0, s * .1), .08)
cube(cloth, -2.6, -1.0, .5, .9, .8, .15); cube(cloth, -2.6, -1.4, .5, .9, .12, 1.1, 0, .2)
blob(skin, -2.6, -1.0, 1.0, .28, .28, .3); blob(cloth, -2.6, -1.0, 1.5, .2, .2, .2)
# windows glowing, a lantern on the porch post
for x in (-2.8, 2.8):
    cube(lamp, x, 1.62, 3.4, 1.0, .1, 1.1); cube(dark, x, 1.6, 3.3, 1.2, .1, .1); cube(dark, x, 1.6, 4.5, 1.2, .1, .1)
cube(lamp, 0, 1.62, 2.6, 1.4, .1, 1.5)
light((1, .65, .25), 700, (0, .5, 3.4)); light((1, .65, .25), 400, (0, -1.5, 4.0))
# the boat, tied to a post at the landing
cube(boat, 4.0, -8.0, .05, 4.2, 1.5, .6, .15); cube(boat, 4.0, -8.0, .6, 4.2, 1.5, .1, .15)
for s in (-1, 1): cube(dark, 4.0 + s * .4, -8.0 + s * .6, .65, 4.2, .12, .15, .15)
cube(plank, 4.0, -8.0, .6, .8, 1.2, .1, .15)
post(dark, 6.6, -4.6, .22, .12, 1.2); limb(dark, (6.6, -4.6, 1.2), (4.8, -7.6, .8), .05)
# two oaks with hanging moss
for x, y in ((-8.5, 4.0), (8.5, 6.0)):
    post(dark, x, y, .2, .7, 4.5, 6, .5)
    for dx, dy, dz in ((0, 0, 6.2), (1.6, .5, 5.4), (-1.6, -.5, 5.6)): blob(leaf, x + dx, y + dy, dz, 2.2, 2.2, 1.6)
    for k in range(9):
        a = k * .7; limb(moss, (x + math.cos(a) * 1.8, y + math.sin(a) * 1.8, 5.2), (x + math.cos(a) * 1.8, y + math.sin(a) * 1.8, 3.0 + (k % 3) * .4), .07)
for x in (-9.5, -7.8, 9.2): post(dark, x, -5.0, .2, .08, 1.0)
for x in (-9, 8): blob(leaf, x, -3.5, .6, .8, .8, .6)
for c, w, p in (((.5, .7, .75), 3.5, (-24, -14, 10)), ((1, .5, .3), 2.2, (22, 22, 9))):
    S = bpy.data.lights.new("s", "SUN"); S.color = c; S.energy = w
    o = bpy.data.objects.new("s", S); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.012, .03, .035, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((0, 0, 3)); co.location = tg + Vector((8, -60, 38))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
