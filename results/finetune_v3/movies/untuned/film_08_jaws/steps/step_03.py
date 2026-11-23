import bpy, math, random
from mathutils import Vector

# Delete everything and rebuild with proper positioning
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# World - ocean sky
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wl = world.node_tree.links
bg = wn.get("Background")
bg.inputs[0].default_value = (0.05, 0.12, 0.25, 1.0)
bg.inputs[1].default_value = 1.0

# Camera - positioned to see the boat and shark from a dramatic angle
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
# Camera looking at the scene from above and to the side
cam.location = (10, 8, 6)
# Point camera at the boat/shark area (around x=2, y=0, z=0)
target = Vector((2, 0, 0))
direction = target - cam.location
rot_quat = direction.to_track_quat('Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

# Sun - warm afternoon light
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 5
sun_data.color = (1.0, 0.95, 0.85)
sun_data.angle = math.radians(3)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))

# Fill light - cooler from opposite side
fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 100
fill_data.size = 15
fill_data.color = (0.7, 0.8, 1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-8, 5, 10)
fill.rotation_euler = (math.radians(50), 0, math.radians(30))

def new_mat(name, color, rough=0.5, metal=0.0, alpha=1.0, blend=False, emission=0.0, emit_color=(1,1,1)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    if emission > 0:
        b.inputs["Emission Color"].default_value = (*emit_color, 1.0)
        b.inputs["Emission Strength"].default_value = emission
    return m

# ===================== OCEAN =====================
ocean_verts, ocean_faces = [], []
size, res = 80, 60
for i in range(res+1):
    for j in range(res+1):
        x = -size/2 + i*size/res
        z = -size/2 + j*size/res
        # Multiple wave frequencies for realism
        w = (0.5*math.sin(x*0.2)*math.cos(z*0.15) + 
             0.25*math.sin(x*0.5 + z*0.3) + 
             0.1*math.sin(x*1.0 - z*0.7) +
             0.05*math.sin(x*2.0 + z*1.5))
        ocean_verts.append((x, w, z))
for i in range(res):
    for j in range(res):
        a=i*(res+1)+j; b=a+1; c=a+res+1; d=c+1
        ocean_faces.append((a,b,d,c))
ocean = bpy.data.objects.new("Ocean", bpy.data.meshes.new("Ocean"))
ocean.data.from_pydata(ocean_verts, [], ocean_faces)
bpy.context.collection.objects.link(ocean)
ocean.data.materials.append(new_mat("OceanMat", (0.01,0.08,0.2), 0.1, 0.4))

# ===================== FISHING BOAT (ORCA) =====================
# Hull - small wooden fishing boat
hull_v, hull_f = [], []
L, W, H = 6, 1.8, 1.0
secs = 12
for s in range(secs+1):
    t = s/secs
    x = -L/2 + t*L
    # Taper at both ends
    if t < 0.12:
        taper = t / 0.12
    elif t > 0.88:
        taper = (1 - t) / 0.12
    else:
        taper = 1.0
    w = W/2 * taper
    h = H * (0.3 + 0.7 * taper)
    # 6-point cross section
    hull_v += [
        (x, -h, 0),           # bottom center
        (x, -h*0.6, -w),     # port mid
        (x, 0, -w),          # port top
        (x, 0, w),           # starboard top
        (x, -h*0.6, w),      # starboard mid
    ]
for s in range(secs):
    b1=s*5; b2=(s+1)*5
    for k in range(5):
        hull_f.append((b1+k, b1+(k+1)%5, b2+(k+1)%5, b2+k))
# Close ends
hull_f.append((0,1,2,3,4))
hull_f.append((secs*5, secs*5+1, secs*5+2, secs*5+3, secs*5+4))
hull = bpy.data.objects.new("Hull", bpy.data.meshes.new("Hull"))
hull.data.from_pydata(hull_v, [], hull_f)
bpy.context.collection.objects.link(hull)
hull.location = (0, 0.2, 0)
hull.data.materials.append(new_mat("HullWood", (0.28,0.18,0.08), 0.85))

# Gunwales (top edges)
for side in [-1, 1]:
    gv, gf = [], []
    for s in range(secs+1):
        t = s/secs
        x = -L/2 + t*L
        if t < 0.12: taper = t/0.12
        elif t > 0.88: taper = (1-t)/0.12
        else: taper = 1.0
        w = W/2 * taper
        gv.append((x, 0, w*side))
        gv.append((x, 0.15, w*side))
    for s in range(secs):
        gf.append((s*2, s*2+1, (s+1)*2+1, (s+1)*2))
    gunwale = bpy.data.objects.new(f"Gunwale{side}", bpy.data.meshes.new(f"Gunwale{side}"))
    gunwale.data.from_pydata(gv, [], gf)
    bpy.context.collection.objects.link(gunwale)
    gunwale.location = (0, 0.2, 0)
    gunwale.data.materials.append(new_mat("GunwaleWood", (0.35,0.22,0.1), 0.8))

# Deck planking
deck_v, deck_f = [], []
dl, dw = L*0.85, W*0.85
dres = 8
for i in range(dres+1):
    for j in range(3):
        x = -dl/2 + i*dl/dres
        z = -dw/2 + j*(dw/2)
        deck_v.append((x, 0.25, z))
for i in range(dres):
    for j in range(2):
        a=i*3+j; b=a+1; c=a+3; d=c+1
        deck_f.append((a,b,d,c))
deck = bpy.data.objects.new("Deck", bpy.data.meshes.new("Deck"))
deck.data.from_pydata(deck_v, [], deck_f)
bpy.context.collection.objects.link(deck)
deck.location = (0, 0.2, 0)
deck.data.materials.append(new_mat("DeckWood", (0.38,0.28,0.15), 0.9))

# Cabin
cw, cl, ch = 1.0, 1.8, 0.9
cab_v = [(-cl/2,0,-cw/2),(-cl/2,0,cw/2),(-cl/2,ch,cw/2),(-cl/2,ch,-cw/2),
         (cl/2,0,-cw/2),(cl/2,0,cw/2),(cl/2,ch,cw/2),(cl/2,ch,-cw/2)]
cab_f = [(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,2,6,7),(0,1,5,4)]
cabin = bpy.data.objects.new("Cabin", bpy.data.meshes.new("Cabin"))
cabin.data.from_pydata(cab_v, [], cab_f)
bpy.context.collection.objects.link(cabin)
cabin.location = (-1.2, 0.45, 0)
cabin.data.materials.append(new_mat("CabinWood", (0.42,0.32,0.2), 0.85))

# Cabin roof
rv = [(-cl/2-0.05, ch, -cw/2-0.05),(-cl/2-0.05, ch, cw/2+0.05),
      (-cl/2-0.05, ch+0.12, cw/2+0.05),(-cl/2-0.05, ch+0.12, -cw/2-0.05),
      (cl/2+0.05, ch, -cw/2-0.05),(cl/2+0.05, ch, cw/2+0.05),
      (cl/2+0.05, ch+0.12, cw/2+0.05),(cl/2+0.05, ch+0.12, -cw/2-0.05)]
rf = [(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,2,6,7),(0,1,5,4)]
roof = bpy.data.objects.new("CabinRoof", bpy.data.meshes.new("CabinRoof"))
roof.data.from_pydata(rv, [], rf)
bpy.context.collection.objects.link(roof)
roof.location = (-1.2, 1.35, 0)
roof.data.materials.append(new_mat("RoofMat", (0.3,0.28,0.25), 0.7))

# Cabin windows
for side in [-1, 1]:
    win_v = [(-0.3, 0.2, side*0.51), (0.3, 0.2, side*0.51), (0.3, 0.6, side*0.51), (-0.3, 0.6, side*0.51)]
    win_f = [(0,1,2,3)]
    win = bpy.data.objects.new(f"Window{side}", bpy.data.meshes.new(f"Window{side}"))
    win.data.from_pydata(win_v, [], win_f)
    bpy.context.collection.objects.link(win)
    win.location = (-1.2, 0.45, 0)
    win.data.materials.append(new_mat(f"Window{side}", (0.1,0.15,0.2), 0.1, 0.5, 0.5, True))

# Mast
mast_v = [(-0.04,0,-0.04),(-0.04,0,0.04),(-0.04,3.5,0.04),(-0.04,3.5,-0.04),
          (0.04,0,-0.04),(0.04,0,0.04),(0.04,3.5,0.04),(0.04,3.5,-0.04)]
mast_f = [(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,2,6,7),(0,1,5,4)]
mast = bpy.data.objects.new("Mast", bpy.data.meshes.new("Mast"))
mast.data.from_pydata(mast_v, [], mast_f)
bpy.context.collection.objects.link(mast)
mast.location = (0.8, 0.45, 0)
mast.data.materials.append(new_mat("MastWood", (0.32,0.22,0.1), 0.8))

# Boom (horizontal spar)
boom_v = [(-0.03,0,-1.5),(-0.03,0,1.5),(-0.03,0.08,1.5),(-0.03,0.08,-1.5),
          (0.03,0,-1.5),(0.03,0,1.5),(0.03,0.08,1.5),(0.03,0.08,-1.5)]
boom_f = [(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,2,6,7),(0,1,5,4)]
boom = bpy.data.objects.new("Boom", bpy.data.meshes.new("Boom"))
boom.data.from_pydata(boom_v, [], boom_f)
bpy.context.collection.objects.link(boom)
boom.location = (0.8, 2.8, 0)
boom.data.materials.append(new_mat("BoomWood", (0.32,0.22,0.1), 0.8))

# Rigging - thin lines
def make_rigging(name, p1, p2, radius=0.012):
    mid = Vector((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
    length = Vector(p2).distance(Vector(p1))
    direction = Vector(p2) - Vector(p1)
    rot = direction.to_track_quat('Z', 'Y').to_euler()
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(new_mat(name+"Mat", (0.1,0.1,0.1), 0.9))
    return obj

# Forestay (bow to mast top)
make_rigging("Forestay", (-3, 0.45, 0), (0.8, 3.95, 0))
# Backstay (stern to mast top)
make_rigging("Backstay", (3, 0.45, 0), (0.8, 3.95, 0))
# Shrouds
make_rigging("ShroudL", (-0.8, 0.45, -0.9), (0.8, 3.5, 0))
make_rigging("ShroudR", (-0.8, 0.45, 0.9), (0.8, 3.5, 0))

# Stern rail
rail_v, rail_f = [], []
rl = 1.2
for i in range(8):
    t = i/7
    x = -rl/2 + t*rl
    rail_v += [(x, 0, -W/2+0.08), (x, 0.25, -W/2+0.08), (x, 0.25, W/2-0.08), (x, 0, W/2-0.08)]
for i in range(7):
    b1=i*4; b2=(i+1)*4
    for k in range(4):
        rail_f.append((b1+k, b1+(k+1)%4, b2+(k+1)%4, b2+k))
rail = bpy.data.objects.new("SternRail", bpy.data.meshes.new("SternRail"))
rail.data.from_pydata(rail_v, [], rail_f)
bpy.context.collection.objects.link(rail)
rail.location = (2.8, 0.2, 0)
rail.data.materials.append(new_mat("RailWood", (0.35,0.25,0.12), 0.8))

# ===================== GREAT WHITE SHARK =====================
# Detailed shark body
shark_v, shark_f = [], []
sl, smw, smh = 5.0, 0.65, 0.5
prof = [
    (0.0, 0.0, 0.0), (0.03, 0.2, 0.15), (0.06, 0.45, 0.35),
    (0.1, 0.7, 0.55), (0.15, 0.85, 0.7), (0.2, 0.95, 0.8),
    (0.3, 1.0, 0.85), (0.4, 1.0, 0.8), (0.5, 0.95, 0.75),
    (0.6, 0.85, 0.65), (0.7, 0.7, 0.55), (0.8, 0.5, 0.4),
    (0.85, 0.35, 0.3), (0.9, 0.25, 0.22), (0.95, 0.15, 0.15),
    (1.0, 0.05, 0.05)
]
for t, wf, hf in prof:
    x = -sl/2 + t * sl
    w = smw * wf
    h = smh * hf
    for k in range(10):
        a = k * math.pi * 2 / 10
        # Slightly pointed nose shape
        shape_w = w * (1 - 0.3*math.cos(a)) if t < 0.1 else w * math.cos(a)
        shape_h = h * math.sin(a)
        shark_v.append((x, shape_h, shape_w))
for i in range(len(prof)-1):
    b1 = i*10; b2 = (i+1)*10
    for k in range(10):
        shark_f.append((b1+k, b1+(k+1)%10, b2+(k+1)%10, b2+k))
# Nose cap
shark_v.append((-sl/2, 0, 0))
ni = len(shark_v)-1
for k in range(10):
    shark_f.append((ni, k, (k+1)%10))
# Tail cap
shark_v.append((sl/2, 0, 0))
ti = len(shark_v)-1
for k in range(10):
    k1 = (len(prof)-1)*10 + k
    k2 = (len(prof)-1)*10 + (k+1)%10
    shark_f.append((ti, k2, k1))

shark = bpy.data.objects.new("Shark", bpy.data.meshes.new("Shark"))
shark.data.from_pydata(shark_v, [], shark_f)
bpy.context.collection.objects.link(shark)
# Position: rising from water at stern of boat
shark.location = (3.5, -0.5, 0)
shark.rotation_euler = (math.radians(25), 0, 0)  # Angled upward out of water
shark.data.materials.append(new_mat("SharkSkin", (0.35,0.4,0.42), 0.3, 0.15))

# Dorsal fin - tall and prominent
df_v = [
    (-0.5, 0.25, -0.03), (-0.5, 0.65, -0.03), (-0.15, 0.75, -0.03),
    (0.15, 0.55, -0.03), (0.35, 0.25, -0.03),
    (-0.5, 0.25, 0.03), (-0.5, 0.65, 0.03), (-0.15, 0.75, 0.03),
    (0.15, 0.55, 0.03), (0.35, 0.25, 0.03)
]
df_f = [(0,1,2,3,4,5), (5,4,3,2,1,6)]
df = bpy.data.objects.new("DorsalFin", bpy.data.meshes.new("DorsalFin"))
df.data.from_pydata(df_v, [], df_f)
bpy.context.collection.objects.link(df)
df.location = (3.2, 0.1, 0)
df.data.materials.append(new_mat("DorsalFinMat", (0.35,0.4,0.42), 0.3, 0.15))

# Caudal fin (tail) - asymmetric
cf_v = [
    (0, 0, -0.2), (0.3, 0.25, 0), (0.6, 0.05, 0), (0.35, -0.2, 0), (0, 0, 0.2),
    (0, 0, -0.2), (0.3, 0.25, 0), (0.6, 0.05, 0), (0.35, -0.2, 0), (0, 0, 0.2)
]
cf_f = [(0,1,2,3,4,5), (5,4,3,2,1,6)]
cf = bpy.data.objects.new("CaudalFin", bpy.data.meshes.new("CaudalFin"))
cf.data.from_pydata(cf_v, [], cf_f)
bpy.context.collection.objects.link(cf)
cf.location = (6.0, -0.5, 0)
cf.rotation_euler = (math.radians(25), math.radians(10), 0)
cf.data.materials.append(new_mat("CaudalFinMat", (0.35,0.4,0.42), 0.3, 0.15))

# Pectoral fins
for side, sz in [("L", -1), ("R", 1)]:
    pf_v = [
        (0, 0, 0), (0.35, -0.08, 0.22*sz), (0.6, -0.25, 0.35*sz),
        (0.2, -0.15, 0.12*sz), (0, 0, 0.04*sz),
        (0.35, -0.08, 0.26*sz), (0.6, -0.25, 0.39*sz), (0.2, -0.15, 0.16*sz)
    ]
    pf_f = [(0,1,2,3,4), (4,3,2,1,5)]
    pf = bpy.data.objects.new(f"PecFin{side}", bpy.data.meshes.new(f"PecFin{side}"))
    pf.data.from_pydata(pf_v, [], pf_f)
    bpy.context.collection.objects.link(pf)
    pf.location = (2.5, -0.3, 0.3*sz)
    pf.rotation_euler = (math.radians(20), 0, math.radians(12*sz))
    pf.data.materials.append(new_mat(f"PecFin{side}Mat", (0.35,0.4,0.42), 0.3, 0.15))

# Pelvic fins (smaller, lower)
for side, sz in [("L", -1), ("R", 1)]:
    pv_v = [
        (0, 0, 0), (0.2, -0.05, 0.15*sz), (0.35, -0.15, 0.22*sz),
        (0.12, -0.1, 0.08*sz), (0, 0, 0.03*sz),
        (0.2, -0.05, 0.18*sz), (0.35, -0.15, 0.25*sz), (0.12, -0.1, 0.11*sz)
    ]
    pv_f = [(0,1,2,3,4), (4,3,2,1,5)]
    pv = bpy.data.objects.new(f"PelvicFin{side}", bpy.data.meshes.new(f"PelvicFin{side}"))
    pv.data.from_pydata(pv_v, [], pv_f)
    bpy.context.collection.objects.link(pv)
    pv.location = (3.0, -0.5, 0.2*sz)
    pv.rotation_euler = (math.radians(15), 0, math.radians(10*sz))
    pv.data.materials.append(new_mat(f"PelvicFin{side}Mat", (0.35,0.4,0.42), 0.3, 0.15))

# Open mouth - upper jaw
uj_v = [
    (-0.4, -0.05, -0.12), (-0.4, -0.05, 0.12), (-0.15, -0.25, 0.1),
    (-0.15, -0.25, -0.1), (-0.4, 0.1, -0.12), (-0.4, 0.1, 0.12),
    (-0.15, -0.05, 0.1), (-0.15, -0.05, -0.1)
]
uj_f = [(0,1,2,3,4), (4,3,2,1,5)]
uj = bpy.data.objects.new("UpperJaw", bpy.data.meshes.new("UpperJaw"))
uj.data.from_pydata(uj_v, [], uj_f)
bpy.context.collection.objects.link(uj)
uj.location = (1.2, -0.3, 0)
uj.rotation_euler = (math.radians(25), 0, 0)
uj.data.materials.append(new_mat("JawMat", (0.25,0.28,0.3), 0.4))

# Lower jaw
lj_v = [
    (-0.35, -0.15, -0.1), (-0.35, -0.15, 0.1), (-0.1, -0.35, 0.08),
    (-0.1, -0.35, -0.08), (-0.35, 0.0, -0.1), (-0.35, 0.0, 0.1),
    (-0.1, -0.15, 0.08), (-0.1, -0.15, -0.08)
]
lj_f = [(0,1,2,3,4), (4,3,2,1,5)]
lj = bpy.data.objects.new("LowerJaw", bpy.data.meshes.new("LowerJaw"))
lj.data.from_pydata(lj_v, [], lj_f)
bpy.context.collection.objects.link(lj)
lj.location = (1.2, -0.3, 0)
lj.rotation_euler = (math.radians(35), 0, 0)
lj.data.materials.append(new_mat("LowerJawMat", (0.25,0.28,0.3), 0.4))

# Teeth - rows of triangles
tv, tf2 = [], []
# Upper teeth
for i in range(10):
    t = i/9
    x = -0.35 + t*0.5
    z = -0.1 + t*0.2
    bi = len(tv)
    tv += [(x, -0.18, z-0.015), (x, -0.18, z+0.015), (x, -0.05, z)]
    tf2.append((bi, bi+1, bi+2))
# Lower teeth
for i in range(8):
    t = i/7
    x = -0.3 + t*0.4
    z = -0.08 + t*0.16
    bi = len(tv)
    tv += [(x, 0.02, z-0.015), (x, 0.02, z+0.015), (x, -0.1, z)]
    tf2.append((bi, bi+1, bi+2))
teeth = bpy.data.objects.new("Teeth", bpy.data.meshes.new("Teeth"))
teeth.data.from_pydata(tv, [], tf2)
bpy.context.collection.objects.link(teeth)
teeth.location = (1.2, -0.3, 0)
teeth.rotation_euler = (math.radians(25), 0, 0)
teeth.data.materials.append(new_mat("TeethMat", (0.92,0.92,0.88), 0.2))

# Eyes
for side, sz in [("L", -1), ("R", 1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(1.5, -0.15, 0.22*sz))
    eye = bpy.context.active_object
    eye.name = f"Eye{side}"
    eye.data.materials.append(new_mat(f"Eye{side}Mat", (0.01,0.01,0.01), 0.05, 0.6))

# Gills - 5 slits
for i in range(5):
    z = -0.12 + i*0.06
    gill_v = [(0, -0.08, -0.015), (0, 0.08, -0.015), (0.03, 0.08, 0), (0.03, -0.08, 0)]
    gill_f = [(0,1,2,3)]
    gill = bpy.data.objects.new(f"Gill{i}", bpy.data.meshes.new(f"Gill{i}"))
    gill.data.from_pydata(gill_v, [], gill_f)
    bpy.context.collection.objects.link(gill)
    gill.location = (2.2, -0.2, z)
    gill.rotation_euler = (0, math.radians(90), 0)
    gill.data.materials.append(new_mat(f"Gill{i}Mat", (0.55,0.45,0.45), 0.5))

# ===================== SPLASH & WATER EFFECTS =====================
# Splash columns around shark
sv, sf = [], []
for i in range(50):
    a = random.uniform(0, 2*math.pi)
    d = random.uniform(0.4, 1.5)
    x = 3.5 + d*math.cos(a)
    z = d*math.sin(a)
    h = random.uniform(0.2, 1.0)
    bi = len(sv)
    r = random.uniform(0.05, 0.12)
    sv += [
        (x, 0, z), (x+r, 0, z+r*0.5), (x+r, h, z+r*0.5),
        (x+r, 0, z-r*0.5), (x-r, 0, z+r*0.5), (x-r, h, z+r*0.5),
        (x-r, 0, z-r*0.5), (x, h*1.1, z)
    ]
    sf += [(bi,bi+1,bi+2),(bi,bi+2,bi+3),(bi,bi+3,bi+4),(bi,bi+4,bi+5),
           (bi,bi+5,bi+6),(bi,bi+6,bi+1),(bi+1,bi+2,bi+7),(bi+2,bi+3,bi+7),
           (bi+3,bi+4,bi+7),(bi+4,bi+5,bi+7),(bi+5,bi+6,bi+7),(bi+6,bi+1,bi+7)]
splash = bpy.data.objects.new("Splash", bpy.data.meshes.new("Splash"))
splash.data.from_pydata(sv, [], sf)
bpy.context.collection.objects.link(splash)
splash.data.materials.append(new_mat("SplashMat", (0.6,0.8,1.0), 0.0, 0.0, 0.5, True))

# Wave ring around shark
wave_v, wave_f = [], []
for i in range(24):
    a = i * math.pi * 2 / 24
    r = 1.2
    x = 3.5 + r*math.cos(a)
    z = r*math.sin(a)
    h = 0.4 + 0.2*math.sin(a*4)
    wave_v += [(x, 0, z), (x, h, z)]
for