import bpy, bmesh, random, math
from mathutils import Vector
random.seed(434)
sc = bpy.context.scene
def tint(rgb, em=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = .9
    if em: b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = em
    return m
dust, dust2, grass, stone, stone2, bone = tint((.4, .3, .16)), tint((.32, .23, .12)), tint((.25, .26, .1)), tint((.38, .36, .33)), tint((.28, .26, .25)), tint((.7, .66, .55))
hats = [tint((.1, .1, .12)), tint((.25, .12, .06)), tint((.35, .33, .3))]
coats = [tint((.5, .48, .45)), tint((.2, .12, .08)), tint((.15, .15, .17))]
skin, wood, iron, rope, cactus, flame = tint((.55, .38, .27)), tint((.22, .13, .07)), tint((.07, .07, .08)), tint((.4, .3, .18)), tint((.1, .22, .1)), tint((1, .5, .1), 12)
def add(bm, m, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("a"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("a", me); o.location, o.rotation_euler = loc, rot
    sc.collection.objects.link(o); o.data.materials.append(m); return o
def slab(m, x, y, z, w, d, h, rz=0, top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * w * k, v.co.y * d * k, (v.co.z + .5) * h))
    return add(bm, m, (x, y, z), (0, 0, rz))
def rod(m, a, b, t):
    a, b = Vector(a), Vector(b); d = b - a; q = d.to_track_quat('Z', 'Y')
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = q @ Vector((v.co.x * t, v.co.y * t, (v.co.z + .5) * d.length)) + a
    return add(bm, m)
def cone(m, x, y, z, r, h, n=6, r2=0):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return add(bm, m, (x, y, z))
def blob(m, x, y, z, r, sq=1):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.8, 1.2); v.co.z *= sq
    return add(bm, m, (x, y, z))
def lit(kind, c, e, loc, aim=None):
    L = bpy.data.lights.new("l", kind); L.color, L.energy = c, e
    o = bpy.data.objects.new("l", L); o.location = loc; sc.collection.objects.link(o)
    if aim: o.rotation_euler = (Vector(aim) - o.location).to_track_quat('-Z', 'Y').to_euler()
# the base: a low mesa, rough underside
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=14, depth=3.6)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2), random.uniform(-1.3, .2)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.8
add(bm, dust)
for i in range(16):
    a = random.uniform(0, 6.28); r = random.uniform(6, 12.5)
    blob(dust2 if i % 2 else grass, r * math.cos(a), r * math.sin(a), .05, random.uniform(.8, 1.8), .25)
# the stone circle: broken slabs with two gaps, a flat stone and a skull in the middle
for i in range(14):
    a = i * math.pi * 2 / 14
    if i in (3, 9): continue
    slab(stone if i % 2 else stone2, 4.6 * math.cos(a), 4.6 * math.sin(a), 0, 1.5, .7, random.uniform(.7, 1.2), a + math.pi / 2 + random.uniform(-.2, .2), .8)
slab(stone2, 0, 0, 0, 2.6, 2.6, .12, .3, .9); blob(bone, .3, .2, .25, .35, .8); slab(bone, -.5, -.3, .12, .8, .3, .12, .5)
# three gunmen: boots, legs, coat, belt, head, hat, and a long gun held out with a muzzle flash
def gunman(x, y, a, k):
    c, s = math.cos(a), math.sin(a)
    for sd in (-.22, .22):
        rod(coats[k], (x + sd * -s, y + sd * c, 0), (x + sd * -s, y + sd * c, 1.3), .24)
    slab(coats[k], x, y, 1.2, 1.1, .7, 1.5, a, .85); slab(iron, x, y, 1.9, 1.15, .75, .12, a)
    blob(skin, x, y, 3.0, .38); cone(hats[k], x, y, 3.15, .3, .35, 8, .22); cone(hats[k], x, y, 3.4, .62, .08, 8, .62)
    rod(coats[k], (x, y, 2.5), (x + c * 1.2, y + s * 1.2, 2.6), .22)
    rod(wood, (x + c * 1.2, y + s * 1.2, 2.6), (x + c * 2.6, y + s * 2.6, 2.5), .12); rod(iron, (x + c * 1.9, y + s * 1.9, 2.65), (x + c * 3.0, y + s * 3.0, 2.55), .08)
    lit("POINT", (1, .6, .2), 40, (x + c * 3.1, y + s * 3.1, 2.6))
gunman(-7.2, 0, 0, 0); gunman(3.6, 6.2, math.pi * .75, 1); gunman(3.6, -6.2, math.pi * .25, 2)
# the cemetery: rows of crosses, slabs and tombstones, some leaning, a few with skulls
for r in range(5):
    for c in range(7):
        x, y = -11 + c * 3.4 + random.uniform(-.4, .4), -11 + r * 4.4 + random.uniform(-.4, .4)
        if math.hypot(x, y) < 7.2 or math.hypot(x, y) > 12.4: continue
        if (x + 7.2) ** 2 + y ** 2 < 14 or (x - 3.6) ** 2 + (y - 6.2) ** 2 < 14 or (x - 3.6) ** 2 + (y + 6.2) ** 2 < 14: continue
        k = (r + c) % 3
        if k == 0:
            rod(stone, (x, y, 0), (x, y, 2.0), .22); rod(stone, (x - .6, y, 1.5), (x + .6, y, 1.5), .18)
        elif k == 1: slab(stone2, x, y, 0, 1.2, .3, 1.2 + random.uniform(0, .4), random.uniform(-.2, .2), .8)
        else: cone(stone, x, y, 0, .6, 1.0, 4, .45); blob(bone, x, y - .5, .2, .22, .8)
for i in range(5): blob(grass, random.uniform(-10, 10), random.uniform(-10, 10), .05, random.uniform(.8, 1.4), .3)
# hanging lantern on a crossbeam at the circle edge, with flame glow
rod(wood, (-4.6, 0, 0), (-4.6, 0, 4.2), .22); rod(wood, (-4.6, 0, 4.2), (-2.2, 0, 4.0), .14)
rod(iron, (-2.2, 0, 4.0), (-2.2, 0, 3.4), .04); slab(flame, -2.2, 0, 2.9, .45, .45, .6, 0, .8)
lit("POINT", (1, .55, .15), 450, (-2.2, 0, 3.2))
# a lone cactus and a boulder or two
cone(cactus, 10.5, 6.5, 0, .5, 2.4, 6, .4); cone(cactus, 11.4, 6.5, 1.2, .22, 1.0, 5, .18); cone(cactus, 11.4, 6.5, 2.0, .22, .5, 5, .18)
blob(stone2, -10.5, 8.5, .3, 1.2, .8); blob(stone2, 8.5, -9.5, .3, 1.0, .8)
lit("SUN", (1, .6, .25), 5.5, (-26, -14, 8), (0, 0, 1)); lit("SUN", (.4, .5, .9), 2, (24, 20, 12), (0, 0, 1))
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
next(n for n in w.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.03, .02, .025, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
t = Vector((0, 0, 1.5)); co.location = t + Vector((16, -58, 38))
co.rotation_euler = (t - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
