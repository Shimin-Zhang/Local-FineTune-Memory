import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1171)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
camp = {}
def glaze(name, rgb, em=0, rough=.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = rough
    if em:
        p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    camp[name] = m
def mold(bm, name, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(camp[name]); return o
def blk(bm, x, y, z, w, d, h, rz=0, rx=0):
    bmesh.ops.create_cube(bm, size=1, matrix=__import__("mathutils").Matrix.Translation((x, y, z + h / 2)) @ __import__("mathutils").Matrix.Rotation(rz, 4, 'Z') @ __import__("mathutils").Matrix.Rotation(rx, 4, 'X') @ __import__("mathutils").Matrix.Diagonal((w, d, h, 1)))
def cyl(bm, x, y, z, r, h, n=6, r2=None, rot=(0, 0, 0)):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h, matrix=__import__("mathutils").Matrix.Translation((x, y, z + h / 2)) @ __import__("mathutils").Matrix.Rotation(rot[0], 4, 'X') @ __import__("mathutils").Matrix.Rotation(rot[1], 4, 'Y'))
def spar(bm, a, b, t):
    a, b = Vector(a), Vector(b); q = (b - a).to_track_quat('Z', 'Y')
    bmesh.ops.create_cube(bm, size=1, matrix=__import__("mathutils").Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4() @ __import__("mathutils").Matrix.Diagonal((t, t, (b - a).length, 1)))
def drift(bm, x, y, z, r, sq=.3):
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r, matrix=__import__("mathutils").Matrix.Translation((x, y, z)) @ __import__("mathutils").Matrix.Diagonal((1, 1, sq, 1)))

glaze("snow", (.55, .62, .78), rough=.9); glaze("ice", (.3, .5, .75), rough=.2); glaze("steel", (.4, .43, .48), rough=.5)
glaze("orange", (.9, .3, .05)); glaze("dark", (.05, .06, .08)); glaze("white", (.7, .72, .75)); glaze("flag", (.9, .08, .05))
glaze("lamp", (1, .75, .4), 10); glaze("core", (.5, .8, 1), 2.5); glaze("sled", (.5, .1, .08)); glaze("drill", (.7, .5, .1))
glaze("wind", (.25, .4, .6), rough=.9); glaze("tunnel", (.03, .04, .06))

bm = bmesh.new(); blk(bm, 0, 0, -3, 30, 24, 3); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=6, radius2=14.5, depth=3, matrix=__import__("mathutils").Matrix.Translation((0, 0, -4.5)) @ __import__("mathutils").Matrix.Rotation(math.pi / 2, 4, 'X') @ __import__("mathutils").Matrix.Diagonal((1, .75, 1, 1)))
for v in bm.verts:
    if v.co.z < -2: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
mold(bm, "snow")
for i in range(12): drift(bm, random.uniform(-13, 13), random.uniform(-10, 10), .1, random.uniform(.8, 1.8), .22)
mold(bm, "snow")
# trench lab: cut into the ice, roofed, with a lit core rack inside and a tunnel mouth
bm = bmesh.new(); blk(bm, -6.5, 0, 0, 9, 5.5, 3.2); mold(bm, "ice")
bm = bmesh.new(); blk(bm, -6.5, 0, 0, 7.2, 3.6, 2.2); mold(bm, "tunnel")
bm = bmesh.new(); blk(bm, -6.5, 0, 3.2, 9.4, 5.9, .3); mold(bm, "white")
bm = bmesh.new()
for i in range(7):
    blk(bm, -8.9 + i * .9, 0, .2, .12, 2.6, 1.9)
    for k in range(5): blk(bm, -8.9 + i * .9, 0, .3 + k * .38, .22, .22, .22)
mold(bm, "core")
bm = bmesh.new(); blk(bm, -1.8, 0, 0, 1.4, 1.6, 2.0); mold(bm, "tunnel"); blk(bm, -1.8, -1.2, 0, 1.6, .2, 2.4); mold(bm, "dark")
bm = bmesh.new(); blk(bm, -6.5, -2.9, 0, 7.2, .1, 1.9); mold(bm, "lamp")
# drilling tower: lattice legs, cross braces, winch deck, mast, derrick, drill string and ice shaft
bm = bmesh.new()
for sx in (-1, 1):
    for sy in (-1, 1): spar(bm, (2 + sx * 1.6, sy * 1.6, 0), (2 + sx * .8, sy * .8, 7.5), .18)
for z in (1.5, 3.2, 5.0, 6.6):
    r = 1.6 - z * .11
    for s in (-1, 1): spar(bm, (2 + s * r, -r, z), (2 + s * r, r, z), .1); spar(bm, (2 - r, s * r, z), (2 + r, s * r, z), .1)
mold(bm, "steel")
bm = bmesh.new(); blk(bm, 2, 0, 7.5, 2.4, 2.4, .3); mold(bm, "orange")
bm = bmesh.new(); spar(bm, (2, 0, 7.8), (2, 0, 14.5), .3); spar(bm, (2, 0, 14.5), (2, 0, 9), .12); spar(bm, (2, 0, 12.5), (3.2, 0, 14.5), .1); mold(bm, "steel")
bm = bmesh.new(); blk(bm, 2, 0, 10.5, 1.2, 1.2, 1.4); mold(bm, "drill")
bm = bmesh.new(); cyl(bm, 2, 0, 0, 1.0, .5, 8, .8); mold(bm, "dark"); cyl(bm, 2, 0, .5, .7, .1, 8); mold(bm, "core")
# orange tents, sledges, flag on a pole
bm = bmesh.new()
for tx, ty, rz in ((7.5, -4.5, .2), (9.5, 2.5, -.3), (-1.5, -6.5, .5)):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=1.5, radius2=.15, depth=2.4, matrix=__import__("mathutils").Matrix.Translation((tx, ty, 1.2)) @ __import__("mathutils").Matrix.Rotation(rz, 4, 'Z') @ __import__("mathutils").Matrix.Rotation(math.pi / 4, 4, 'Z'))
mold(bm, "orange")
bm = bmesh.new()
for sx, sy, rz in ((-2.5, -8.5, .3), (4.5, 7.5, -.2)):
    bmesh.ops.create_cube(bm, size=1, matrix=__import__("mathutils").Matrix.Translation((sx, sy, .45)) @ __import__("mathutils").Matrix.Rotation(rz, 4, 'Z') @ __import__("mathutils").Matrix.Diagonal((2.6, 1.2, .3, 1)))
    for s in (-1, 1): spar(bm, (sx + s * 1.2, sy, .6), (sx + s * 1.2, sy, 2.2), .1)
    spar(bm, (sx - 1.3, sy, .6), (sx - 1.3, sy, 2.2), .1); spar(bm, (sx + 1.3, sy, .6), (sx + 1.3, sy, 2.2), .1)
mold(bm, "sled")
bm = bmesh.new(); spar(bm, (-11, 5, 0), (-11, 5, 7.5), .15); mold(bm, "steel")
bm = bmesh.new(); blk(bm, -10.1, 5, 5.8, 1.8, .06, 1.3); mold(bm, "flag")
bm = bmesh.new(); blk(bm, -10.1, 5, 5.8, 1.8, .1, .4); mold(bm, "white")
# wind-blown snow drifts and ice shards
bm = bmesh.new()
for i in range(8): drift(bm, random.uniform(-12, 12), random.uniform(-9, 9), .1, random.uniform(1.2, 2.2), .2)
mold(bm, "wind")
bm = bmesh.new()
for i in range(10):
    x, y = random.uniform(-12, 12), random.uniform(-9, 9)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=5, radius1=random.uniform(.2, .4), radius2=0, depth=random.uniform(.8, 1.6), matrix=__import__("mathutils").Matrix.Translation((x, y, .8)))
mold(bm, "ice")

def sun(rgb, w, at, aim=Vector((0, 0, 1))):
    L = bpy.data.lights.new("sun", "SUN"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("sun", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (aim - o.location).to_track_quat('-Z', 'Y').to_euler()
def lamp(at, rgb, w):
    L = bpy.data.lights.new("lamp", "POINT"); L.color = rgb; L.energy = w
    o = bpy.data.objects.new("lamp", L); o.location = at; sc.collection.objects.link(o)
sun((1, .85, .6), 5.5, (-26, -14, 9)); sun((.45, .6, 1), 2.4, (24, 20, 14))
lamp((-6.5, -3.6, 1.4), (.6, .85, 1), 700); lamp((2, -2, 1), (1, .8, .5), 300)
sc.world = bpy.data.worlds.new("cold"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .02, .045, 1)
cam = bpy.data.cameras.new("cam"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 3)); co.location = t + Vector((22, -60, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
