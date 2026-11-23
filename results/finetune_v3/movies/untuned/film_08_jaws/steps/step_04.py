import bpy, math, random
from mathutils import Vector

# Delete all objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# World
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.05,0.12,0.25,1.0)
bg.inputs[1].default_value = 1.0

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 40
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.location = (10, 8, 6)
target = Vector((2, 0, 0))
direction = target - cam.location
rot_quat = direction.to_track_quat('Z','Y')
cam.rotation_euler = rot_quat.to_euler()

# Lights
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 5; sun_data.color = (1.0,0.95,0.85)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(30))

fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 100; fill_data.size = 15; fill_data.color = (0.7,0.8,1.0)
fill = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (-8,5,10)
fill.rotation_euler = (math.radians(50),0,math.radians(30))

def new_mat(name, color, rough=0.5, metal=0.0, alpha=1.0, blend=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color,1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    return m

# Ocean
ocean_verts, ocean_faces = [], []
size, res = 80, 60
for i in range(res+1):
    for j in range(res+1):
        x = -size/2 + i*size/res
        z = -size/2 + j*size/res
        w = (0.5*math.sin(x*0.2)*math.cos(z*0.15) + 0.25*math.sin(x*0.5+z*0.3) + 0.1*math.sin(x*1.0-z*0.7))
        ocean_verts.append((x, w, z))
for i in range(res):
    for j in range(res):
        a=i*(res+1)+j; b=a+1; c=a+res+1; d=c+1
        ocean_faces.append((a,b,d,c))
ocean = bpy.data.objects.new("Ocean", bpy.data.meshes.new("Ocean"))
ocean.data.from_pydata(ocean_verts, [], ocean_faces)
bpy.context.collection.objects.link(ocean)
ocean.data.materials.append(new_mat("OceanMat", (0.01,0.08,0.2), 0.1, 0.4))

# Boat hull
hull_v, hull_f = [], []
L, W, H = 6, 1.8, 1.0
secs = 12
for s in range(secs+1):
    t = s/secs
    x = -L/2 + t*L
    if t < 0.12: taper = t/0.12
    elif t > 0.88: taper = (1-t)/0.12
    else: taper = 1.0
    w = W/2*taper; h = H*(0.3+0.7*taper)
    hull_v += [(x,-h,0),(x,-h*0.6,-w),(x,0,-w),(x,0,w),(x,-h*0.6,w)]
for s in range(secs):
    b1=s*5; b2=(s+1)*5
    for k in range(5):
        hull_f.append((b1+k,b1+(k+1)%5,b2+(k+1)%5,b2+k))
hull_f.append((0,1,2,3,4))
hull_f.append((secs*5,secs*5+1,secs*5+2,secs*5+3,secs*5+4))
hull = bpy.data.objects.new("Hull", bpy.data.meshes.new("Hull"))
hull.data.from_pydata(hull_v, [], hull_f)
bpy.context.collection.objects.link(hull)
hull.location = (0,0.2,0)
hull.data.materials.append(new_mat("HullWood", (0.28,0.18,0.08), 0.85))

# Deck
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
deck.location = (0,0.2,0)
deck.data.materials.append(new_mat("DeckWood", (0.38,0.28,0.15), 0.9))

# Cabin
cw, cl, ch = 1.0, 1.8, 0.9
cab_v = [(-cl/2,0,-cw/2),(-cl/2,0,cw/2),(-cl/2,ch,cw/2),(-cl/2,ch,-cw/2),
         (cl/2,0,-cw/2),(cl/2,0,cw/2),(cl/2,ch,cw/2),(cl/2,ch,-cw/2)]
cab_f = [(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,2,6,7),(0,1,5,4)]
cabin = bpy.data.objects.new("Cabin", bpy.data.meshes.new("Cabin"))
cabin.data.from_pydata(cab_v, [], cab_f)
bpy.context.collection.objects.link(cabin)
cabin.location = (-1.2,0.45,0)
cabin.data.materials.append(new_mat("CabinWood", (0.42,0.32,0.2), 0.85))

# Mast
mast_v = [(-0.04,0,-0.04),(-0.04,0,0.04),(-0.04,3.5,0.04),(-0.04,3.5,-0.04),
          (0.04,0,-0.04),(0.04,0,0.04),(0.04,3.5,0.04),(0.04,3.5,-0.04)]
mast_f = [(0,1,2,3),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,2,6,7),(0,1,5,4)]
mast = bpy.data.objects.new("Mast", bpy.data.meshes.new("Mast"))
mast.data.from_pydata(mast_v, [], mast_f)
bpy.context.collection.objects.link(mast)
mast.location = (0.8,0.45,0)
mast.data.materials.append(new_mat("MastWood", (0.32,0.22,0.1), 0.8))

# Shark body
shark_v, shark_f = [], []
sl, smw, smh = 5.0, 0.65, 0.5
prof = [(0,0,0),(0.03,0.2,0.15),(0.06,0.45,0.35),(0.1,0.7,0.55),(0.15,0.85,0.7),
        (0.2,0.95,0.8),(0.3,1,0.85),(0.4,1,0.8),(0.5,0.95,0.75),(0.6,0.85,0.65),
        (0.7,0.7,0.55),(0.8,0.5,0.4),(0.85,0.35,0.3),(0.9,0.25,0.22),(0.95,0.15,0.15),(1,0.05,0.05)]
for t,wf,hf in prof:
    x = -sl/2 + t*sl
    w = smw*wf; h = smh*hf
    for k in range(10):
        a = k*math.pi*2/10
        shape_w = w*(1-0.3*math.cos(a)) if t<0.1 else w*math.cos(a)
        shape_h = h*math.sin(a)
        shark_v.append((x, shape_h, shape_w))
for i in range(len(prof)-1):
    b1=i*10; b2=(i+1)*10
    for k in range(10):
        shark_f.append((b1+k,b1+(k+1)%10,b2+(k+1)%10,b2+k))
shark_v.append((-sl/2,0,0)); ni=len(shark_v)-1
for k in range(10): shark_f.append((ni,k,(k+1)%10))
shark_v.append((sl/2,0,0)); ti=len(shark_v)-1
for k in range(10):
    k1=(len(prof)-1)*10+k; k2=(len(prof)-1)*10+(k+1)%10
    shark_f.append((ti,k2,k1))
shark = bpy.data.objects.new("Shark", bpy.data.meshes.new("Shark"))
shark.data.from_pydata(shark_v, [], shark_f)
bpy.context.collection.objects.link(shark)
shark.location = (3.5,-0.5,0)
shark.rotation_euler = (math.radians(25),0,0)
shark.data.materials.append(new_mat("SharkSkin", (0.35,0.4,0.42), 0.3, 0.15))

# Dorsal fin
df_v = [(-0.5,0.25,-0.03),(-0.5,0.65,-0.03),(-0.15,0.75,-0.03),(0.15,0.55,-0.03),(0.35,0.25,-0.03),
        (-0.5,0.25,0.03),(-0.5,0.65,0.03),(-0.15,0.75,0.03),(0.15,0.55,0.03),(0.35,0.25,0.03)]
df_f = [(0,1,2,3,4,5),(5,4,3,2,1,6)]
df = bpy.data.objects.new("DorsalFin", bpy.data.meshes.new("DorsalFin"))
df.data.from_pydata(df_v, [], df_f)
bpy.context.collection.objects.link(df)
df.location = (3.2,0.1,0)
df.data.materials.append(new_mat("DorsalFinMat", (0.35,0.4,0.42), 0.3, 0.15))

# Caudal fin
cf_v = [(0,0,-0.2),(0.3,0.25,0),(0.6,0.05,0),(0.35,-0.2,0),(0,0,0.2),
        (0,0,-0.2),(0.3,0.25,0),(0.6,0.05,0),(0.35,-0.2,0),(0,0,0.2)]
cf_f = [(0,1,2,3,4,5),(5,4,3,2,1,6)]
cf = bpy.data.objects.new("CaudalFin", bpy.data.meshes.new("CaudalFin"))
cf.data.from_pydata(cf_v, [], cf_f)
bpy.context.collection.objects.link(cf)
cf.location = (6.0,-0.5,0)
cf.rotation_euler = (math.radians(25),math.radians(10),0)
cf.data.materials.append(new_mat("CaudalFinMat", (0.35,0.4,0.42), 0.3, 0.15))

# Pectoral fins
for side,sz in [("L",-1),("R",1)]:
    pf_v = [(0,0,0),(0.35,-0.08,0.22*sz),(0.6,-0.25,0.35*sz),(0.2,-0.15,0.12*sz),
            (0,0,0.04*sz),(0.35,-0.08,0.26*sz),(0.6,-0.25,0.39*sz),(0.2,-0.15,0.16*sz)]
    pf_f = [(0,1,2,3,4),(4,3,2,1,5)]
    pf = bpy.data.objects.new(f"PecFin{side}", bpy.data.meshes.new(f"PecFin{side}"))
    pf.data.from_pydata(pf_v, [], pf_f)
    bpy.context.collection.objects.link(pf)
    pf.location = (2.5,-0.3,0.3*sz)
    pf.rotation_euler = (math.radians(20),0,math.radians(12*sz))
    pf.data.materials.append(new_mat(f"PecFin{side}Mat", (0.35,0.4,0.42), 0.3, 0.15))

# Mouth
uj_v = [(-0.4,-0.05,-0.12),(-0.4,-0.05,0.12),(-0.15,-0.25,0.1),(-0.15,-0.25,-0.1),
        (-0.4,0.1,-0.12),(-0.4,0.1,0.12),(-0.15,-0.05,0.1),(-0.15,-0.05,-0.1)]
uj_f = [(0,1,2,3,4),(4,3,2,1,5)]
uj = bpy.data.objects.new("UpperJaw", bpy.data.meshes.new("UpperJaw"))
uj.data.from_pydata(uj_v, [], uj_f)
bpy.context.collection.objects.link(uj)
uj.location = (1.2,-0.3,0)
uj.rotation_euler = (math.radians(25),0,0)
uj.data.materials.append(new_mat("JawMat", (0.25,0.28,0.3), 0.4))

# Teeth
tv, tf2 = [], []
for i in range(10):
    t = i/9
    x = -0.35 + t*0.5
    z = -0.1 + t*0.2
    bi = len(tv)
    tv += [(x,-0.18,z-0.015),(x,-0.18,z+0.015),(x,-0.05,z)]
    tf2.append((bi,bi+1,bi+2))
for i in range(8):
    t = i/7
    x = -0.3 + t*0.4
    z = -0.08 + t*0.16
    bi = len(tv)
    tv += [(x,0.02,z-0.015),(x,0.02,z+0.015),(x,-0.1,z)]
    tf2.append((bi,bi+1,bi+2))
teeth = bpy.data.objects.new("Teeth", bpy.data.meshes.new("Teeth"))
teeth.data.from_pydata(tv, [], tf2)
bpy.context.collection.objects.link(teeth)
teeth.location = (1.2,-0.3,0)
teeth.rotation_euler = (math.radians(25),0,0)
teeth.data.materials.append(new_mat("TeethMat", (0.92,0.92,0.88), 0.2))

# Eyes
for side,sz in [("L",-1),("R",1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(1.5,-0.15,0.22*sz))
    eye = bpy.context.active_object
    eye.name = f"Eye{side}"
    eye.data.materials.append(new_mat(f"Eye{side}Mat", (0.01,0.01,0.01), 0.05, 0.6))

# Gills
for i in range(5):
    z = -0.12 + i*0.06
    gill_v = [(0,-0.08,-0.015),(0,0.08,-0.015),(0.03,0.08,0),(0.03,-0.08,0)]
    gill_f = [(0,1,2,3)]
    gill = bpy.data.objects.new(f"Gill{i}", bpy.data.meshes.new(f"Gill{i}"))
    gill.data.from_pydata(gill_v, [], gill_f)
    bpy.context.collection.objects.link(gill)
    gill.location = (2.2,-0.2,z)
    gill.rotation_euler = (0,math.radians(90),0)
    gill.data.materials.append(new_mat(f"Gill{i}Mat", (0.55,0.45,0.45), 0.5))

# Splash
sv, sf =