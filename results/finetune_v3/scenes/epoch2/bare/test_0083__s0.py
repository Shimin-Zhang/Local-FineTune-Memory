import bpy, bmesh, math, random
from mathutils import Vector
random.seed(1685)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
pal = {}
def dye(k, c, e=0, m=0, r=.8):
    pal[k] = m = bpy.data.materials.new(k); m.use_nodes = True
    n = next(x for x in m.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    n.inputs["Base Color"].default_value = (*c, 1); n.inputs["Roughness"].default_value = r; n.inputs["Metallic"].default_value = r
    if e: n.inputs["Emission Color"].default_value = (*c, 1); n.inputs["Emission Strength"].default_value = e
dye("floor", (.22, .13, .07)); dye("floor2", (.16, .09, .05)); dye("wall", (.12, .17, .15)); dye("wall2", (.08, .12, .11)); dye("wood", (.3, .17, .08))
dye("brass", (.9, .6, .15), 0, 0, .3); dye("black", (.03, .03, .035)); dye("cream", (.7, .65, .5)); dye("red", (.55, .08, .06))
dye("lamp", (1, .85, .5), 22); dye("clockface", (1, .95, .8), 10); dye("tray", (.1, .2, .18)); dye("screw", (.8, .8, .85), 0, 0, .3); dye("glass", (.4, .6, .6), .3, 0, .1)
def mk(bm, k, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("w"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("w", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(pal[k]); return o
def blk(at, s, k, rz=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * s[0], v.co.y * s[1], (v.co.z + .5) * s[2]))
    return mk(bm, k, at, (0, 0, rz))
def rod(at, r, h, n, k, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, k, at, rot)
def lamp(kind, c, w, at, aim=None):
    L = bpy.data.lights.new("l", kind); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# floor of planks, two walls only
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=5, radius2=10, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
mk(bm, "floor2")
for i in range(11): blk((0, -8 + i * 1.6, 0), (15, 1.5, .12), "floor" if i % 2 else "floor2")
blk((0, 9, 0), (16, .5, 7), "wall"); blk((-8, 0, 0), (.5, 18.5, 7), "wall2")
blk((0, 8.6, 0), (15.4, .4, .5), "wood"); blk((-7.6, 0, 0), (.4, 18, .5), "wood")
# the bench along the back wall with its tools
blk((-1.5, 7.2, 0), (9, 2.6, 2.0), "wood"); blk((-1.5, 7.2, 2.0), (9.4, 2.9, .2), "black")
for x in (-5, 2): blk((x, 6.2, 0), (1.2, 1.2, .5), "black")
blk((-4, 7.2, 2.2), (1.6, .8, .15), "tray")
for i in range(7):
    for j in range(3): rod((-4.7 + i * .22, 6.9 + j * .3, 2.35), .07, .08, 5, "screw", .04)
rod((-2.2, 7.2, 2.2), .35, .08, 8, "brass"); rod((-1.2, 7.4, 2.2), .2, .06, 6, "brass")
blk((.6, 7.2, 2.2), (.5, .3, .25), "red"); blk((1.5, 7.2, 2.2), (.9, .3, .12), "black")
# magnifying lamp over the bench: arm, elbow, big lens, glowing bulb
rod((-1.5, 7.9, 2.2), .12, 2.6, 6, "black"); rod((-1.5, 7.9, 4.8), .1, 1.6, 5, "black", rot=(math.radians(50), 0, 0))
rod((-1.5, 6.9, 6.2), .1, 1.4, 5, "black", rot=(math.radians(-55), 0, 0))
rod((-1.5, 5.8, 5.4), 1.0, .25, 10, "black", rot=(math.radians(180), 0, 0)); rod((-1.5, 5.8, 5.3), .85, .12, 10, "lamp", rot=(math.radians(180), 0, 0))
rod((-1.5, 5.8, 4.6), .3, .5, 6, "lamp")
lamp("POINT", (1, .85, .5), 1500, (-1.5, 5.8, 4.8)); lamp("POINT", (1, .85, .5), 400, (-1.5, 5.8, 3.2))
# glass cases of pocket watches along the left wall
for c in range(3):
    y = -4 + c * 3.6
    blk((-6.3, y, 0), (2.4, 3.0, 2.0), "wood"); blk((-6.3, y, 2.0), (2.6, 3.2, .15), "black")
    for s in (-1, 1): blk((-6.3, y + s * 1.35, 2.15), (2.4, .1, 1.3), "glass")
    blk((-6.3, y + 1.35, 3.4), (2.4, .1, .1), "brass")
    for w in range(3):
        x = -7 + w * .75
        rod((x, y, 2.2), .05, .5, 5, "brass"); rod((x, y, 2.7), .38, .1, 8, "brass", rot=(math.radians(90), 0, 0)); rod((x, y - .06, 2.7), .28, .1, 8, "cream", rot=(math.radians(90), 0, 0))
# the tall clock case in the corner
blk((5.8, 6.8, 0), (2.6, 2.6, 6.2), "wood"); blk((5.8, 5.4, 0), (2.4, .2, 6.0), "black")
blk((5.8, 5.3, 5.0), (1.8, .15, 1.2), "clockface")
rod((5.8, 5.2, 5.6), .1, .6, 5, "black", rot=(math.radians(90), 0, 0)); rod((5.8, 5.2, 5.6), .08, .4, 5, "red", rot=(math.radians(90), 0, 0))
rod((5.8, 5.3, 3.9), .7, .1, 10, "brass", rot=(math.radians(90), 0, 0)); rod((5.8, 5.2, 3.9), .1, .5, 5, "brass", rot=(math.radians(90), 0, 0))
for z in (1.2, 2.2): blk((5.8, 5.25, z), (1.6, .1, .1), "brass")
lamp("POINT", (1, .9, .6), 300, (5.8, 4.5, 5.2))
# stools, a shelf of watch parts on the wall, and a scale
for y in (-1.5, 1.5): rod((-3.2, y, 0), .5, 1.4, 7, "wood"); rod((-3.2, y, 1.4), .6, .15, 7, "red")
blk((-7.5, 1, 3.6), (.5, 6, .15), "wood")
for i in range(6): rod((-7.4, -1.5 + i * 1, 3.75), .15, .3, 6, "brass", .1)
rod((1, 4.5, 0), .3, 1.2, 6, "brass"); blk((1, 4.5, 1.2), (1.8, .12, .1), "brass")
# evening light: warm key from the front-left, teal rim from behind-right
lamp("SUN", (1, .7, .4), 4.5, (-18, -14, 9), (0, 2, 2)); lamp("SUN", (.3, .7, .75), 2, (14, 16, 10), (0, 2, 2))
w = bpy.data.worlds.new("shop"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 1.5, 3)); co.location = t + Vector((14, -42, 27))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
