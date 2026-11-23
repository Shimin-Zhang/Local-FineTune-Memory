import bpy, bmesh, random, math
from mathutils import Vector
random.seed(594)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
def col(rgb, glow=0):
    m = bpy.data.materials.new("c"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .85
    if glow: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = glow
    return m
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def blk(w, d, h, m, at, rot=(0, 0, 0), top=1.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return mk(bm, m, at, rot)
def rod(r1, r2, h, n, m, at, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r1, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def spike(r, h, n, m, at, lean=0, jit=.25):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=.05, depth=h)
    for v in bm.verts:
        v.co.z += h / 2; v.co += Vector((random.uniform(-jit, jit), random.uniform(-jit, jit), 0))
    return mk(bm, m, at, (lean, 0, 0))
def shine(at, c, w):
    L = bpy.data.lights.new("s", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
def lamp(at, c, w, aim):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
deep, cliff, stone, stone2, floor = col((.03, .02, .02)), col((.1, .09, .1)), col((.28, .27, .3)), col((.17, .17, .2)), col((.34, .33, .36))
robe, skin, beard, wood, steel = col((.45, .42, .4)), col((.55, .38, .3)), col((.6, .6, .62)), col((.3, .17, .08)), col((.7, .72, .78))
black, eye, ember, fire, rune = col((.015, .015, .02)), col((.9, .75, .1)), col((.7, .25, .06)), col((.5, .1, .04)), col((.1, .5, .6))
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5), random.uniform(-1.2, .3)))
    v.co.z -= 1.5
mk(bm, deep)
# chasm: a dark trench down the middle, with glowing lava veins on its floor
blk(7, 22, .1, ember, (0, 0, -.05))
for i in range(5): blk(.5, 1.2, .12, fire, (random.uniform(-2, 2), -8 + i * 4, .02))
# two cliffs with faceted tops, rough undersides and layered ledges
for s in (-1, 1):
    blk(8, 22, 6.5, cliff, (s * 6.4, 0, 0), top=.93)
    for k in range(3): blk(8.2 - k * .4, 22.4, .5, stone2 if k % 2 else cliff, (s * 6.4, 0, 1.8 + k * 1.7), top=.9)
    for k in range(7):
        x = s * (2.3 + random.uniform(0, 1.5)); y = random.uniform(-9, 9)
        spike(random.uniform(.6, 1.1), random.uniform(1.2, 2.2), 5, stone2, (x, y, 6.5), lean=random.uniform(-.2, .2))
    for k in range(4): blk(.9, .9, .5, stone, (s * (3 + random.uniform(0, 5)), random.uniform(-9, 9), 6.5))
# the bridge: narrow deck of slabs, parapets of blocks, buttresses under each end
for i in range(12):
    blk(2.6, 1.7, .5, stone if i % 2 else floor, (0, -9.5 + i * 1.7 + .85, 5.6), rot=(0, 0, random.uniform(-.04, .04)))
for i in range(11):
    for s in (-1, 1):
        if i % 3 == 1: continue
        blk(.5, .5, .9, stone2, (s * 1.3, -9.5 + i * 1.7 + .85, 6.1), rot=(0, 0, random.uniform(-.1, .1)))
for s in (-1, 1):
    for i in range(3): blk(1.4 - i * .3, 1.8, .8, stone, (s * (2.0 + i * .9), 0, 4.8 - i * .9))
# carved stairways up each cliff to the gate
for s in (-1, 1):
    for i in range(5): blk(3, 1.0, .5, stone, (s * 3.6, 0, 6.5 + i * .5))
    for i in range(3):
        rod(.45, .45, 3.6, 8, stone, (s * 5.4, -2.5 + i * 2.5, 6.5))
    for y in (-2.5, 0, 2.5): blk(.9, .9, .9, stone2, (s * 5.4, y, 10.1))
# the gate of Moria: dark doorway with tall pillars, lintel and glowing runes
blk(1.8, .8, 3.6, black, (0, 10.2, 6.5))
for i in range(4): blk(.1, .1, .6, rune, (-.5 + i * .35, 9.7, 7.5 + (i % 2) * .9))
for i in range(6): blk(.1, .1, .5, rune, (-3.4 + i * 1.3, 9.4, 8.2 + (i % 2) * .5))
# Gandalf, enlarged: white robes, pointed hat, beard, staff, and a sword held toward the beast
gx, gy = -1.0, -3.0
rod(.85, .5, 2.6, 7, robe, (gx, gy, 6.1)); rod(.55, .3, .9, 7, robe, (gx, gy, 8.7))
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=.42); mk(bm, skin, (gx, gy, 9.5))
rod(.55, .05, 1.3, 6, robe, (gx, gy, 9.8)); rod(.3, .02, 1.2, 5, beard, (gx, gy - .25, 8.9), rot=(.3, 0, 0))
rod(.1, .1, 5.2, 5, wood, (gx - .9, gy, 6.1)); rod(.3, .05, .6, 5, rune, (gx - .9, gy, 11.2))
rod(.09, .09, 2.4, 5, steel, (gx + .6, gy - .1, 7.2), rot=(0, 1.2, 0)); blk(.25, .1, .5, wood, (gx + .6, gy - .1, 6.9))
# the Balrog: towering black body of jagged plates, a hooded head, burning eyes, whip and flame blade
bx, by = 1.0, 4.0
rod(2.6, 1.6, 6.5, 7, black, (bx, by, 6.1), top=1.0)
for k in range(7): spike(.9, 2.2, 5, black, (bx + 1.8 * math.cos(k * .9), by + 1.8 * math.sin(k * .9), 10.5), lean=math.cos(k * .9) * .6, jit=.15)
bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.2); mk(bm, black, (bx, by, 13.2))
for s in (-1, 1):
    blk(.5, .2, .35, eye, (bx + s * .5, by - 1.0, 13.3)); rod(.2, .02, .8, 4, black, (bx + s * .6, by - .9, 13.4), rot=(.3, 0, 0))
rod(.35, .35, 4.2, 5, black, (bx + 2.2, by - 1.2, 6.1), rot=(0, -.4, 0))
rod(.5, .1, 3.4, 5, fire, (bx + 3.2, by - 2.4, 9.0), rot=(0, -.6, 0)); rod(.35, .05, 1.4, 5, ember, (bx + 3.6, by - 2.9, 10.8), rot=(0, -.6, 0))
rod(.4, .1, 2.2, 5, fire, (bx - 2.4, by - 1.4, 6.1), rot=(0, .5, 0))
shine((bx, by - 2, 13.4), (1, .7, .15), 1400); shine((bx + 3.4, by - 2.6, 9.6), (1, .35, .08), 1200); shine((gx - .9, gy, 11.2), (.3, .8, 1), 300)
lamp((-26, -18, 11), (.55, .65, 1), 4.5, (0, 0, 6)); lamp((24, 24, 10), (.8, .45, .3), 2.2, (0, 0, 6))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.01, .012, .02, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 8)); co.location = t + Vector((6, -72, 44))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
