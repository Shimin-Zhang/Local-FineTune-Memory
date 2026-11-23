import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1325)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
sc = bpy.context.scene
def tone(r, g, b, e=0):
    m = bpy.data.materials.new("t"); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (r, g, b, 1); p.inputs["Roughness"].default_value = .8
    if e: p.inputs["Emission Color"].default_value = (r, g, b, 1); p.inputs["Emission Strength"].default_value = e
    return m
tile, tile2, plaster, wood, wood2, steel, steel2, white, black, red, glass, pot, fruit, bulb = (tone(*c) for c in (
    (.2, .22, .26), (.14, .16, .2), (.3, .27, .26), (.3, .18, .1), (.2, .12, .07), (.35, .37, .4), (.2, .22, .25), (.55, .56, .58), (.03, .03, .04), (.5, .06, .06), (.1, .2, .25), (.4, .25, .1), (.6, .4, .05), (1, .65, .25, 16)))
def mk(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("k"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("k", me); o.location = at; o.rotation_euler = rot
    sc.collection.objects.link(o); me.materials.append(m); return o
def bx(at, s, m, rot=(0, 0, 0), top=1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        k = top if v.co.z > 0 else 1
        v.co = Vector((v.co.x * s[0] * k, v.co.y * s[1] * k, (v.co.z + .5) * s[2]))
    return mk(bm, m, at, rot)
def cn(at, r, h, n, m, r2=None, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return mk(bm, m, at, rot)
def glim(at, c, w):
    L = bpy.data.lights.new("l", "POINT"); L.color = c; L.energy = w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# kitchen floor slab, chequered tiles, tapered underneath
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
for v in bm.verts:
    v.co = Vector((v.co.x * 15, v.co.y * 13, v.co.z * 2.4 - 1.2))
    if v.co.z < 0: v.co = Vector((v.co.x * .6 + random.uniform(-.6, .6), v.co.y * .6 + random.uniform(-.6, .6), v.co.z - random.uniform(0, 1.2)))
mk(bm, tile2)
for i in range(15):
    for j in range(13):
        if (i + j) % 2 == 0: bx((-6.6 + i, -5.6 + j, 0), (.98, .98, .08), tile)
# two walls only: back and left, with a window in the back wall
bx((0, 6.5, 0), (15, .6, 7), plaster); bx((-7.2, 0, 0), (.6, 13, 7), plaster)
bx((3.5, 6.2, 2.6), (3.6, .2, 2.8), glass); bx((3.5, 6.1, 2.5), (3.8, .3, .2), white); bx((3.5, 6.1, 5.4), (3.8, .3, .2), white); bx((3.5, 6.1, 3.9), (.15, .3, 3), white)
# counter along the back wall: cabinets, worktop, sink with tap, a pot
bx((-1.5, 5.2, 0), (9.4, 2, 1.7), wood2); bx((-1.5, 4.2, 1.7), (9.6, .3, .2), wood)
for i in range(4): bx((-5 + i * 2.4, 4.18, .3), (2.1, .1, 1.1), wood); bx((-4.4 + i * 2.4, 4.1, .9), (.2, .1, .2), steel)
bx((-1.5, 4.2, 1.9), (9.6, 1.7, .2), steel)
bx((-3.2, 4.2, 2.1), (2.2, 1.3, .15), black); bx((-3.2, 4.2, 2.1), (1.9, 1.0, .1), steel2)
cn((-2.2, 4.8, 2.1), .12, 1.1, 6, steel); bx((-2.2, 4.5, 3.1), (.12, .7, .12), steel)
cn((.8, 4.2, 2.1), .55, .5, 8, steel); cn((.8, 4.2, 2.6), .5, .08, 8, black)
# stove: range with four burners, one glowing, oven door and knobs
bx((4.2, 4.6, 0), (3.6, 2.4, 1.7), white); bx((4.2, 4.6, 1.7), (3.7, 2.5, .2), black)
for i in range(4):
    x, y = 3.2 + (i % 2) * 1.9, 4.2 + (i // 2) * .8
    cn((x, y, 1.9), .4, .06, 8, steel2)
cn((3.2, 4.2, 1.9), .3, .06, 8, red); glim((3.2, 4.2, 2.4), (1, .3, .08), 220)
bx((4.2, 3.35, .2), (3.2, .1, 1.2), black); bx((4.2, 3.3, .9), (2.6, .1, .12), steel)
# fridge: tall box with two doors, handles and a magnet note
bx((-5.5, 5.2, 0), (2.6, 2.2, 4.8), white); bx((-5.5, 4.05, 0), (2.4, .1, 2.6), steel); bx((-5.5, 4.05, 2.6), (2.4, .1, 2.1), steel)
bx((-4.5, 3.9, 1.0), (.15, .15, 1.6), black); bx((-4.5, 3.9, 3.2), (.15, .15, 1.2), black)
bx((-5.8, 3.95, 3.5), (.5, .06, .5), red); bx((-5.2, 3.95, 3.2), (.4, .06, .4), fruit)
# two stools at a small bar table
bx((1.5, 1.5, 1.5), (3.2, 1.3, .2), wood); bx((1.5, 1.5, 0), (.2, .2, 1.5), wood2)
for sx in (-.9, .9):
    bx((1.5 + sx, 1.5, 0), (.2, 1.1, .1), wood2); bx((1.5 + sx, 1.5, 1.1), (.9, .9, .15), red, top=.9)
cn((1.5 + .9, 1.5, 1.25), .45, .12, 8, red)
cn((1.5 - .9, 1.5, 1.25), .45, .12, 8, red)
# pendant lamps over the table, a fruit bowl, shelf with jars
for sx in (-.8, .8):
    bx((1.5 + sx, 1.5, 4.4), (.04, .04, 1.6), black); cn((1.5 + sx, 1.5, 4.0), .5, .4, 8, steel2, .2); cn((1.5 + sx, 1.5, 4.0), .18, .12, 6, bulb)
glim((1.5, 1.5, 3.8), (1, .65, .25), 450)
cn((-6.6, 2, 0), .5, 1.1, 8, wood); cn((-6.6, 2, 1.1), .7, .3, 8, white, .45)
for i in range(4): cn((-6.6 + (i - 1.5) * .25, 2 + (i % 2) * .2, 1.3), .22, .3, 6, fruit, .1)
bx((-6.6, 5.6, 3.6), (2.2, .8, .15), wood2)
for i in range(5): cn((-7.2 + i * .5, 5.6, 3.75), .17, .5, 6, red if i % 2 else steel, .15)
# warm evening light: low amber key from the window side, cool rim from the open corner
for c, w, at in (((1, .62, .3), 5, (22, -12, 8)), ((.4, .55, 1), 2.4, (-14, -20, 12))):
    L = bpy.data.lights.new("s", "SUN"); L.color = c; L.energy = w
    o = bpy.data.objects.new("s", L); o.location = at; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
wd = bpy.data.worlds.new("e"); sc.world = wd; wd.use_nodes = True
next(n for n in wd.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .015, .03, 1)
cm = bpy.data.cameras.new("c"); cm.lens = 80
co = bpy.data.objects.new("c", cm); sc.collection.objects.link(co)
tg = Vector((0, 1, 2)); co.location = tg + Vector((14, -46, 30))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
