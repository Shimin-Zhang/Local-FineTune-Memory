import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1575)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def dye(rgb, glow=0):
    m = bpy.data.materials.new("d"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .95
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
sand, sand2, plaster, trim, dome, bronze, palm, frond, cloth, dark, lampm, wood = (dye(c) for c in (
    (.34, .22, .13), (.28, .18, .11), (.42, .32, .24), (.3, .22, .17), (.55, .5, .45), (.25, .14, .06), (.22, .12, .07), (.1, .2, .08), (.5, .12, .1), (.02, .015, .015), (1, .6, .2), (.2, .12, .07)))
lamp = dye((1, .6, .2), 12)
def build(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("b"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("b", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def box(x, y, z, w, d, h, m, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return build(bm, m, (x, y, z), rot)
def cyl(x, y, z, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return build(bm, m, (x, y, z), rot)
def blob(x, y, z, r, m, sq=(1, 1, 1), jit=.08):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * sq[0], v.co.y * sq[1], v.co.z * sq[2])) + Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), random.uniform(-jit, jit))) * r
    return build(bm, m, (x, y, z))
def lamp(x, y, z, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = (x, y, z); sc.collection.objects.link(o)
# dusty ground
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=7, radius2=15, depth=3.4)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.4, 1.4), random.uniform(-1.4, 1.4), random.uniform(-1.4, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.7
build(bm, sand)
for i in range(7): blob(random.uniform(-9, 9), random.uniform(-9, 9), 0, random.uniform(.8, 1.6), sand2, (1.5, 1, .12), .15)
# forecourt walls: low wall on three sides with a gate gap in front
for x, y, w, d in ((0, 6.8, 12.4, .6), (-6.0, 0, .6, 12.4), (6.0, 0, .6, 12.4)):
    box(x, y, 0, w, d, 1.0, plaster)
    box(x, y, 1.0, w + .2, d + .2, .2, trim, top=.8)
for i in range(8):
    box(-5.2 + i * 1.45, -6.2, 0, .7, .6, 1.0, plaster)
    box(-5.2 + i * 1.45, -6.2, 1.0, .9, .8, .2, trim, top=.7)
box(0, -6.2, 0, 1.6, .6, 1.5, trim, top=.8); box(0, -6.2, 1.5, 1.8, .8, .2, plaster)
for sx in (-1, 1):
    box(sx * 2.2, -6.2, 0, .8, .8, 2.2, trim, top=.85); box(sx * 2.2, -6.2, 2.2, 1.0, 1.0, .3, plaster)
# church: nave, apse, tower, dome
box(0, 3.0, 0, 6.4, 5.6, 3.4, plaster)
box(0, 3.0, 3.4, 6.8, 6.0, .4, trim)
box(0, 6.2, 0, 4.2, 2.6, 2.6, plaster); box(0, 6.2, 2.6, 4.6, 3.0, .35, trim)
cyl(0, 6.2, 2.9, 1.5, 1.6, 8, dome, 1.4)
cyl(0, 6.2, 4.5, 1.5, .5, 8, dome, .9)
cyl(0, 6.2, 5.0, .9, 1.2, 8, dome, .08)
box(-3.6, 3.0, 0, 2.4, 2.4, 6.2, plaster); box(-3.6, 3.0, 6.2, 2.8, 2.8, .4, trim)
cyl(-3.6, 3.0, 6.6, 1.3, 1.4, 8, dome, .9); cyl(-3.6, 3.0, 8.0, .9, 1.0, 8, dome, .08)
box(-3.6, 1.78, 3.6, .6, .1, 1.0, dark); box(-3.6, 1.78, 1.0, .5, .1, .9, dark)
box(0, .15, 0, 1.5, .15, 2.2, dark, top=.8); box(0, .1, 2.2, 1.9, .2, .25, trim)
for i in range(3): box(-1.9 + i * 1.9, .15, 1.0, .7, .1, 1.0, lamp)
for sx in (-1, 1):
    for sy in (-1, 1): box(sx * 2.8, 3.0 + sy * 1.6, 3.8, .1, .1, 1.2, trim)
box(0, 3.0, 5.0, 6.4, .1, .1, trim)
box(0, 1.7, 0, 2.0, .6, .3, trim); box(0, 1.1, 0, 2.0, .6, .15, trim)
lamp(0, -.8, 1.2, (1, .6, .2), 400)
# small bell frame
for sx in (-1, 1): box(3.4 + sx * .7, -1.0, 0, .22, .22, 3.2, wood)
box(3.4, -1.0, 3.2, 2.0, .25, .25, wood); box(3.4, -1.0, 2.6, .2, .2, .6, wood)
cyl(3.4, -1.0, 1.7, .38, .9, 6, bronze, .3); cyl(3.4, -1.0, 1.5, .3, .15, 6, bronze)
# palms
for px, py in ((-4.6, -2.8), (4.8, -3.0), (-5.0, 2.0), (4.9, 3.4), (1.5, -4.4)):
    h = random.uniform(3.4, 4.6)
    for k in range(3):
        cyl(px + k * .12, py, k * h / 3, .22 - k * .04, h / 3, 5, palm, .2 - k * .04, (0, .05, 0))
    for k in range(7):
        a = k * .9
        box(px + .3, py, h, 2.0, .5, .1, frond, (0, .25, a))
# brazier with flame, lanterns on gate posts
cyl(-1.6, -3.6, 0, .35, .5, 6, bronze, .5); cyl(-1.6, -3.6, .5, .3, .5, 5, lamp, .05)
lamp(-1.6, -3.6, 1.4, (1, .55, .15), 350)
for sx in (-1, 1):
    box(sx * 2.2, -6.6, 2.5, .25, .25, .4, lamp); lamp(sx * 2.2, -6.8, 2.7, (1, .6, .2), 90)
for col, w, p in (((1, .42, .2), 6, (-26, -12, 8)), ((.5, .25, .55), 2.4, (22, 24, 14))):
    L = bpy.data.lights.new("s", "SUN"); L.color = col; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 2)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.04, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 400
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1.5, 3)); co.location = t + Vector((16, -52, 30))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
