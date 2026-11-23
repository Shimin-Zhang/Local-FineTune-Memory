import bpy, bmesh, random, math
from mathutils import Vector
random.seed(1152)
for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)
sc = bpy.context.scene
col = {}
def tint(name, rgb, em=0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = .9; p.inputs["Alpha"].default_value = alpha
    if em: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = em
    col[name] = m
tint("sand", (.3, .27, .22)); tint("wet", (.14, .13, .13)); tint("sea", (.06, .17, .24), 0, .8); tint("paving", (.22, .22, .24))
tint("post", (.35, .22, .14)); tint("refuge", (.5, .12, .08)); tint("roof", (.2, .22, .24)); tint("white", (.7, .7, .65))
tint("beacon", (1, .8, .3), 25); tint("grass", (.1, .22, .1)); tint("weed", (.2, .25, .12)); tint("stone", (.3, .3, .3))
def form(bm, m, at=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new("f"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("f", me); o.location, o.rotation_euler = at, rot
    sc.collection.objects.link(o); o.data.materials.append(col[m]); return o
def blk(at, d, m, rz=0, rx=0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * d[0], v.co.y * d[1], (v.co.z + .5) * d[2]))
    return form(bm, m, at, (rx, 0, rz))
def rod(at, r, h, n, m, r2=None):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=n, radius1=r, radius2=r if r2 is None else r2, depth=h)
    for v in bm.verts: v.co.z += h / 2
    return form(bm, m, at)
def lump(at, r, m, sq=.5):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts: v.co *= random.uniform(.85, 1.15); v.co.z *= sq
    return form(bm, m, at)
def lamp(c, w, at):
    L = bpy.data.lights.new("l", "POINT"); L.color, L.energy = c, w
    o = bpy.data.objects.new("l", L); o.location = at; sc.collection.objects.link(o)
# tidal sand base, rough below
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=6, radius2=15, depth=3)
for v in bm.verts:
    if v.co.z < 0: v.co += Vector((random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1.2, .3)))
    else: v.co.z += random.uniform(-.1, .1)
    v.co.z -= 1.5
form(bm, "sand")
# sea pools creeping over the pavement
blk((0, -6.0, .02), (26, 3.4, .1), "sea"); blk((-6, 2.5, .02), (5, 4, .1), "sea"); blk((12, -2, .02), (5, 3, .1), "sea")
blk((-3, 6.5, .02), (5, 2.5, .1), "sea"); blk((10, 6.5, .02), (6, 3, .1), "sea")
# the paved causeway, a slightly curving strip of slabs
pts = [(-11, -1.0), (-8.2, -.4), (-5.4, .3), (-2.6, .9), (.2, 1.1), (3.0, .8), (5.8, .2), (8.4, -.4), (10.8, -1.0)]
for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
    mid = ((x0 + x1) / 2, (y0 + y1) / 2); ang = math.atan2(y1 - y0, x1 - x0)
    blk(mid, (math.hypot(x1 - x0, y1 - y0) + .15, 2.6, .22), "paving", ang)
    blk((mid[0], mid[1], .22), (math.hypot(x1 - x0, y1 - y0) + .15, .12, .04), "wet", ang)
# refuge posts on stilts with a beacon on each
for x, y in ((-6.5, 1.9), (-2.5, 2.5), (1.5, 2.3), (5.5, 1.6), (9.2, 1.0)):
    for sx in (-.5, .5):
        for sy in (-.4, .4): rod((x + sx, y + sy, 0), .07, 1.0, 5, "post")
    blk((x, y, 1.0), (1.4, 1.2, .12), "post"); blk((x, y, 1.12), (1.2, 1.0, .5), "refuge")
    blk((x, y, 1.62), (1.4, 1.2, .12), "roof"); rod((x, y, 1.74), .18, .35, 6, "beacon")
    lamp((1, .8, .3), 160, (x, y, 2.1))
# marker poles along the road, striped
for i, (x, y) in enumerate(pts):
    for sy in (-1.8, 1.8):
        rod((x, y + sy, 0), .07, 1.5, 5, "post"); blk((x, y + sy, 1.2), (.2, .2, .25), "white"); blk((x, y + sy, .95), (.2, .2, .15), "refuge")
# island: grassy mound with a beacon hut, stones and weeds
lump((13.5, 3.5, 0), 4.2, "grass", .45); lump((13.5, 3.5, 1.2), 2.6, "grass", .4)
blk((13.5, 3.5, 1.4), (2.0, 1.6, 1.3), "white"); blk((13.5, 3.5, 2.7), (2.4, 2.0, .3), "roof", .2)
rod((13.5, 3.5, 3.0), .25, .5, 6, "beacon"); lamp((1, .8, .3), 700, (13.5, 3.5, 4.0))
for i in range(14):
    a = random.uniform(0, 6.28); r = random.uniform(1, 3.6)
    lump((13.5 + r * math.cos(a), 3.5 + r * math.sin(a), 1.0 + (3.6 - r) * .1), random.uniform(.3, .6), "stone", .7)
for i in range(30):
    x, y = random.uniform(-12, 12), random.uniform(-8, 8)
    if abs(y - 0) < 2.4 or math.hypot(x - 13.5, y - 3.5) < 4.5: continue
    rod((x, y, 0), .06, random.uniform(.5, 1.0), 4, "weed", .01)
for i in range(12): lump((random.uniform(-12, 12), random.uniform(-8, 8), .1), random.uniform(.4, .8), "wet", .2)
for c, w, p in (((.55, .7, .85), 4.5, (-24, -16, 10)), ((.7, .45, .3), 2.2, (20, 22, 9))):
    s = bpy.data.lights.new("s", "SUN"); s.color, s.energy = c, w
    o = bpy.data.objects.new("s", s); o.location = p; sc.collection.objects.link(o)
    o.rotation_euler = (Vector((0, 0, 1)) - o.location).to_track_quat('-Z', 'Y').to_euler()
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND").inputs["Color"].default_value = (.02, .035, .05, 1)
cam = bpy.data.cameras.new("c"); cam.lens = 80; cam.clip_end = 500
co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co)
tg = Vector((1, 1, 1)); co.location = tg + Vector((6, -66, 42))
co.rotation_euler = (tg - co.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = co
