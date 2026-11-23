import bpy, math, random
from mathutils import Vector

# Delete all
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

def nm(name, color, rough=0.5, metal=0.0, alpha=1.0, blend=False):
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
ov, of = [], []
size, res = 80, 60
for i in range(res+1):
    for j in range(res+1):
        x = -size/2 + i*size/res
        z = -size/2 + j*size/res
        w = 0.5*math.sin(x*0.2)*math.cos(z*0.15) + 0.25*math.sin(x*0.5+z*0.3)
        ov.append((x, w, z))
for i in range(res):
    for j in range(res):
        a=i*(res+1)+j; b=a+1; c=a+res+1; d=c+1
        of.append((a,b,d,c))
ocean = bpy.data.objects.new("Ocean", bpy.data.meshes.new("Ocean"))
ocean.data.from_pydata(ov, [], of)
bpy.context.collection.objects.link(ocean)
ocean.data.materials.append(nm("OceanMat", (0.01,0.08,0.2), 0.1, 0.4))

# Boat hull
hv, hf = [], []
L, W, H = 6, 1.8, 1.0
secs = 12
for s in range(secs+1):
    t = s/secs
    x = -L/2 + t*L
    if t < 0.12: taper = t/0.12
    elif t > 0.88: taper = (1-t)/0.12
    else: taper = 1.0
    w = W/2*taper; h = H*(0.3+0.7*taper)
    hv += [(x,-h,0),(x,-h*0.6,-w),(x,0,-w),(x,0,w),(x,-h*0.6,w)]
for s in range(secs):
    b1=s*5; b2=(s+1)*5
    for k in range(5):
        hf.append((b1+k,b1+(k+1)%5,b2+(k+1)%5,b2+k))
hf.append((0,1,2,3,4))
hf.append((secs*5,secs*5+1,secs*5+2,secs*5+3,secs*5+4))
hull = bpy.data.objects.new("Hull", bpy.data.meshes.new("Hull"))
hull.data.from_pydata(hv, [], hf)
bpy.context.collection.objects.link(hull)
hull.location = (0,0.2,0)
hull.data.materials.append(nm("HullWood", (0.28,0.18,0.08), 0.85))

# Deck
dv, df2 = [], []
dl, dw = L*0.85, W*0.85
dres = 8
for i in range(dres+1):
    for j in range(3):
        x = -dl/2 + i*dl/dres
        z = -dw/2 + j*(dw/2)
        dv.append((x, 0.25, z))
for i in range(dres):
    for j in range(2):
        a=i*3+j; b=a+1; c=a+3; d=c+1
        df2.append((a,b,d,c))
deck = bpy.data.objects.new("Deck", bpy.data.meshes.new("Deck"))
deck.data.from_pydata(dv, [], df2)
bpy.context.collection.objects.link(deck)
deck.location = (0,0.2,0)
deck.data.materials.append(nm("DeckWood", (0.38,0.28,0.15), 0.9))

# Cabin
cw, cl, ch = 1.0, 1.8, 0.9
cv = [(-cl/2,0,-cw/2),(-cl/2,0,cw/2),(-cl/2,ch,cw/2),(-cl/2,ch,-cw/2),
      (cl/2,0,-cw/2),(cl/2,0,cw/2),(cl/2,ch,c