import bpy
import math
import random
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Set up world
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs[0].default_value = (0.1, 0.2, 0.35, 1.0)
bg.inputs[1].default_value = 1.0

# Camera setup
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam)
cam_data.lens = 50
bpy.context.scene.camera = cam
cam.location = (8, -12, 4)
cam.rotation_euler = (math.radians(85), 0, math.radians(10))

# Lighting
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3
sun_data.angle = math.radians(5)
sun = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(60), math.radians(20), math.radians(30))

# Helper: create mesh from vertices
def create_mesh_obj(name, verts, faces, location=(0,0,0)):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return obj

# ===================== OCEAN =====================
# Create a large plane with waves
ocean_verts = []
ocean_faces = []
size = 200
res = 80
for i in range(res+1):
    for j in range(res+1):
        x = -size/2 + i * size/res
        z = -size/2 + j * size/res
        # Wave function
        wave = 0.3 * math.sin(x*0.1) * math.cos(z*0.1) + 0.15 * math.sin(x*0.3 + z*0.2)
        ocean_verts.append((x, wave, z))
for i in range(res):
    for j in range(res):
        v1 = i*(res+1) + j
        v2 = v1 + 1
        v3 = v1 + (res+1)
        v4 = v3 + 1
        ocean_faces.append((v1, v2, v4, v3))

ocean = create_mesh_obj("Ocean", ocean_verts, ocean_faces)
ocean.location = (0, 0, 0)

# Ocean material
ocean_mat = bpy.data.materials.new("OceanMat")
ocean_mat.use_nodes = True
nodes = ocean_mat.node_tree.nodes
links = ocean_mat.node_tree.links
bsdf = nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.02, 0.12, 0.25, 1.0)
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Metallic"].default_value = 0.3
bsdf.inputs["Transmission Weight"].default_value = 0.5
ocean.data.materials.append(ocean_mat)

# ===================== FISHING BOAT (ORCA) =====================
# The Orca is a small wooden fishing boat - let's build it with hull, deck, cabin, mast, etc.

# Hull - elongated shape
hull_verts = []
hull_faces = []
length = 8
width = 2.2
height = 1.5
# Build hull as a series of cross-sections
sections = 12
for s in range(sections+1):
    t = s / sections
    x = -length/2 + t * length
    # Taper at bow and stern
    taper = 1.0
    if t < 0.15:
        taper = t / 0.15
    elif t > 0.85:
        taper = (1 - t) / 0.15
    w = width/2 * taper
    h = height * (0.5 + 0.5 * taper)
    # Cross section: bottom point, two sides, two top
    hull_verts.append((x, -h, 0))        # bottom
    hull_verts.append((x, -h/2, -w))     # port side mid
    hull_verts.append((x, 0, -w))        # port top
    hull_verts.append((x, 0, w))         # starboard top
    hull_verts.append((x, -h/2, w))      # starboard side mid

for s in range(sections):
    base1 = s * 5
    base2 = (s+1) * 5
    for k in range(5):
        k2 = (k+1) % 5
        hull_faces.append((base1+k, base1+k2, base2+k2, base2+k))

hull = create_mesh_obj("Hull", hull_verts, hull_faces, (0, 0, 0))
hull.location = (0, 0.5, 0)

# Hull material - weathered wood
hull_mat = bpy.data.materials.new("HullWood")
hull_mat.use_nodes = True
hn = hull_mat.node_tree.nodes
hb = hn.get("Principled BSDF")
hb.inputs["Base Color"].default_value = (0.35, 0.22, 0.12, 1.0)
hb.inputs["Roughness"].default_value = 0.8
hull.data.materials.append(hull_mat)

# Deck
deck_verts = [
    (-length/2*0.9, 0.3, -width/2*0.9),
    (-length/2*0.9, 0.3, width/2*0.9),
    (length/2*0.9, 0.3, width/2*0.9),
    (length/2*0.9, 0.3, -width/2*0.9),
]
deck_faces = [(0,1,2,3)]
deck = create_mesh_obj("Deck", deck_verts, deck_faces, (0, 0, 0))
deck.location = (0, 0.8, 0)
deck_mat = bpy.data.materials.new("DeckWood")
deck_mat.use_nodes = True
dn = deck_mat.node_tree.nodes
db = dn.get("Principled BSDF")
db.inputs["Base Color"].default_value = (0.45, 0.32, 0.18, 1.0)
db.inputs["Roughness"].default_value = 0.9
deck.data.materials.append(deck_mat)

# Cabin
cabin_w = 1.5
cabin_l = 2.5
cabin_h = 1.2
cabin_verts = [
    (-cabin_l/2, 0, -cabin_w/2),
    (-cabin_l/2, 0, cabin_w/2),
    (-cabin_l/2, cabin_h, cabin_w/2),
    (-cabin_l/2, cabin_h, -cabin_w/2),
    (cabin_l/2, 0, -cabin_w/2),
    (cabin_l/2, 0, cabin_w/2),
    (cabin_l/2, cabin_h, cabin_w/2),
    (cabin_l/2, cabin_h, -cabin_w/2),
]
cabin_faces = [
    (0,1,2,3),  # back
    (4,5,6,7),  # front
    (0,4,7,3),  # left
    (1,2,6,5),  # right
    (3,2,6,7),  # top
    (0,1,5,4),  # bottom
]
cabin = create_mesh_obj("Cabin", cabin_verts, cabin_faces, (0, 0, 0))
cabin.location = (-1.5, 1.1, 0)
cabin_mat = bpy.data.materials.new("CabinWood")
cabin_mat.use_nodes = True
cn = cabin_mat.node_tree.nodes
cb = cn.get("Principled BSDF")
cb.inputs["Base Color"].default_value = (0.5, 0.4, 0.25, 1.0)
cb.inputs["Roughness"].default_value = 0.85
cabin.data.materials.append(cabin_mat)

# Cabin roof
roof_verts = [
    (-cabin_l/2 - 0.1, cabin_h, -cabin_w/2 - 0.1),
    (-cabin_l/2 - 0.1, cabin_h, cabin_w/2 + 0.1),
    (-cabin_l/2 - 0.1, cabin_h + 0.15, cabin_w/2 + 0.1),
    (-cabin_l/2 - 0.1, cabin_h + 0.15, -cabin_w/2 - 0.1),
    (cabin_l/2 + 0.1, cabin_h, -cabin_w/2 - 0.1),
    (cabin_l/2 + 0.1, cabin_h, cabin_w/2 + 0.1),
    (cabin_l/2 + 0.1, cabin_h + 0.15, cabin_w/2 + 0.1),
    (cabin_l/2 + 0.1, cabin_h + 0.15, -cabin_w/2 - 0.1),
]
roof_faces = [
    (0,1,2,3),
    (4,5,6,7),
    (0,4,7,3),
    (1,2,6,5),
    (3,2,6,7),
    (0,1,5,4),
]
roof = create_mesh_obj("CabinRoof", roof_verts, roof_faces, (0, 0, 0))
roof.location = (-1.5, 2.3, 0)
roof_mat = bpy.data.materials.new("RoofMat")
roof_mat.use_nodes = True
rn = roof_mat.node_tree.nodes
rb = rn.get("Principled BSDF")
rb.inputs["Base Color"].default_value = (0.3, 0.28, 0.25, 1.0)
rb.inputs["Roughness"].default_value = 0.7
roof.data.materials.append(roof_mat)

# Mast
mast_verts = [
    (-0.05, 0, -0.05),
    (-0.05, 0, 0.05),
    (-0.05, 5, 0.05),
    (-0.05, 5, -0.05),
    (0.05, 0, -0.05),
    (0.05, 0, 0.05),
    (0.05, 5, 0.05),
    (0.05, 5, -0.05),
]
mast_faces = [
    (0,1,2,3),
    (4,5,6,7),
    (0,4,7,3),
    (1,2,6,5),
    (3,2,6,7),
    (0,1,5,4),
]
mast = create_mesh_obj("Mast", mast_verts, mast_faces, (0, 0, 0))
mast.location = (1, 1.1, 0)
mast_mat = bpy.data.materials.new("MastWood")
mast_mat.use_nodes = True
mn = mast_mat.node_tree.nodes
mb = mn.get("Principled BSDF")
mb.inputs["Base Color"].default_value = (0.4, 0.3, 0.15, 1.0)
mb.inputs["Roughness"].default_value = 0.8
mast.data.materials.append(mast_mat)

# Cross beam (boom)
beam_verts = [
    (-0.05, 0, -2),
    (-0.05, 0, 2),
    (-0.05, 0.1, 2),
    (-0.05, 0.1, -2),
    (0.05, 0, -2),
    (0.05, 0, 2),
    (0.05, 0.1, 2),
    (0.05, 0.1, -2),
]
beam_faces = [
    (0,1,2,3),
    (4,5,6,7),
    (0,4,7,3),
    (1,2,6,5),
    (3,2,6,7),
    (0,1,5,4),
]
beam = create_mesh_obj("Boom", beam_verts, beam_faces, (0, 0, 0))
beam.location = (1, 4, 0)
beam.data.materials.append(mast_mat)

# Rigging lines (simple thin cylinders)
def make_cylinder(name, r, depth, loc, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    return obj

# Forestay
forestay = make_cylinder("Forestay", 0.015, 5.5, (1, 3, 0), (math.radians(90), 0, 0))
# Backstay
backstay = make_cylinder("Backstay", 0.015, 5.5, (1, 3, 0), (math.radians(-90), 0, 0))

# Stern rail
rail_verts = []
rail_faces = []
rail_len = 1.5
for i in range(10):
    t = i / 9
    x = -rail_len/2 + t * rail_len
    rail_verts.append((x, 0, -width/2 + 0.1))
    rail_verts.append((x, 0.3, -width/2 + 0.1))
    rail_verts.append((x, 0.3, width/2 - 0.1))
    rail_verts.append((x, 0, width/2 - 0.1))
for i in range(9):
    b1 = i * 4
    b2 = (i+1) * 4
    for k in range(4):
        k2 = (k+1) % 4
        rail_faces.append((b1+k, b1+k2, b2+k2, b2+k))

rail = create_mesh_obj("SternRail", rail_verts, rail_faces, (0, 0, 0))
rail.location = (3.5, 0.8, 0)
rail.data.materials.append(mast_mat)

# ===================== GREAT WHITE SHARK =====================
# Build a detailed great white shark rising from the water at the stern

# Shark body - main shape using a series of cross-sections
shark_verts = []
shark_faces = []
# Shark parameters
shark_length = 6
shark_max_width = 0.8
shark_max_height = 0.6
num_sections = 20

# Define shark profile: (t, width_factor, height_factor, y_offset)
# t goes from 0 (nose) to 1 (tail)
profile = [
    (0.0, 0.0, 0.0, 0.0),      # nose tip
    (0.05, 0.3, 0.2, 0.0),
    (0.1, 0.6, 0.4, 0.0),
    (0.15, 0.8, 0.6, 0.0),
    (0.2, 0.9, 0.7, 0.0),
    (0.3, 1.0, 0.8, 0.0),
    (0.4, 1.0, 0.75, 0.0),
    (0.5, 0.95, 0.7, 0.0),
    (0.6, 0.85, 0.6, 0.0),
    (0.7, 0.7, 0.5, 0.0),
    (0.8, 0.5, 0.35, 0.0),
    (0.85, 0.35, 0.25, 0.0),
    (0.9, 0.25, 0.2, 0.0),
    (0.95, 0.15, 0.15, 0.0),
    (1.0, 0.05, 0.05, 0.0),   # tail tip
]

# Build cross sections
for i, (t, wf, hf, yoff) in enumerate(profile):
    x = -shark_length/2 + t * shark_length
    w = shark_max_width * wf
    h = shark_max_height * hf
    # 8-point cross section (elliptical)
    for k in range(8):
        angle = k * math.pi / 4
        vx = x
        vy = h * math.sin(angle) + yoff
        vz = w * math.cos(angle)
        shark_verts.append((vx, vy, vz))

# Connect sections
for i in range(len(profile) - 1):
    base1 = i * 8
    base2 = (i+1) * 8
    for k in range(8):
        k2 = (k+1) % 8
        shark_faces.append((base1+k, base1+k2, base2+k2, base2+k))

# Nose cap
nose_center = [0] * 3
shark_verts.append((-shark_length/2, 0, 0))
nose_idx = len(shark_verts) - 1
for k in range(8):
    shark_faces.append((nose_idx, k, (k+1) % 8))

# Tail cap
tail_center = [0] * 3
shark_verts.append((shark_length/2, 0, 0))
tail_idx = len(shark_verts) - 1
for k in range(8):
    k1 = (len(profile)-1)*8 + k
    k2 = (len(profile)-1)*8 + (k+1) % 8
    shark_faces.append((tail_idx, k2, k1))

shark = create_mesh_obj("Shark", shark_verts, shark_faces, (0, 0, 0))
# Position shark at stern, rising from water
shark.location = (4.5, -0.5, 0)
shark.rotation_euler = (math.radians(15), 0, 0)  # angled upward

# Shark material - grey on top, white on bottom
shark_mat = bpy.data.materials.new("SharkSkin")
shark_mat.use_nodes = True
sn = shark_mat.node_tree.nodes
sl = shark_mat.node_tree.links
sb = sn.get("Principled BSDF")
sb.inputs["Base Color"].default_value = (0.45, 0.48, 0.5, 1.0)
sb.inputs["Roughness"].default_value = 0.4
sb.inputs["Metallic"].default_value = 0.1
shark.data.materials.append(shark_mat)

# Dorsal fin
dorsal_verts = [
    (-0.8, 0.3, 0),
    (-0.8, 0.8, 0),
    (-0.3, 0.9, 0),
    (0.2, 0.7, 0),
    (0.5, 0.3, 0),
    (0.5, 0.3, 0.05),
    (0.2, 0.7, 0.05),
    (-0.3, 0.9, 0.05),
    (-0.8, 0.8, 0.05),
    (-0.8, 0.3, 0.05),
]
dorsal_faces = [
    (0,1,2,3,4,5,6,7,8,9),  # front face
    (0,9,8,7,6,5,4,3,2,1),  # back face
]
# Better: build as two triangles for front and back
dorsal_verts = [
    (-0.8, 0.3, -0.02),
    (-0.8, 0.8, -0.02),
    (-0.3, 0.9, -0.02),
    (0.2, 0.7, -0.02),
    (0.5, 0.3, -0.02),
    (-0.8, 0.3, 0.02),
    (-0.8, 0.8, 0.02),
    (-0.3, 0.9, 0.02),
    (0.2, 0.7, 0.02),
    (0.5, 0.3, 0.02),
]
dorsal_faces = [
    (0,1,2,3,4,5),  # front
    (5,4,3,2,1,6),  # back (reversed)
]
dorsal = create_mesh_obj("DorsalFin", dorsal_verts, dorsal_faces, (0, 0, 0))
dorsal.location = (4.2, 0.2, 0)
dorsal.data.materials.append(shark_mat)

# Tail fin (caudal fin)
tail_verts = [
    (0, 0, -0.3),
    (0.5, 0.3, 0),
    (0.8, 0, 0),
    (0.5, -0.3, 0),
    (0, 0, 0.3),
    (0, 0, -0.3),
    (0.5, 0.3, 0),
    (0.8, 0, 0),
    (0.5, -0.3, 0),
    (0, 0, 0.3),
]
tail_faces = [
    (0,1,2,3,4,5),
    (5,4,3,2,1,6),
]
tail_fin = create_mesh_obj("TailFin", tail_verts, tail_faces, (0, 0, 0))
tail_fin.location = (7.5, -0.5, 0)
tail_fin.rotation_euler = (0, math.radians(10), 0)
tail_fin.data.materials.append(shark_mat)

# Pectoral fins
pec_verts_l = [
    (0, 0, 0),
    (0.5, -0.1, 0.3),
    (0.8, -0.3, 0.5),
    (0.3, -0.2, 0.2),
    (0, 0, 0.05),
    (0.5, -0.1, 0.35),
    (0.8, -0.3, 0.55),
    (0.3, -0.2, 0.25),
]
pec_faces_l = [
    (0,1,2,3,4),
    (4,3,2,1,5),
]
pec_l = create_mesh_obj("PecFinL", pec_verts_l, pec_faces_l, (0, 0, 0))
pec_l.location = (3.5, -0.3, -0.4)
pec_l.rotation_euler = (math.radians(30), 0, math.radians(20))
pec_l.data.materials.append(shark_mat)

pec_r = create_mesh_obj("PecFinR", pec_verts_l, pec_faces_l, (0, 0, 0))
pec_r.location = (3.5, -0.3, 0.4)
pec_r.rotation_euler = (math.radians(30), 0, math.radians(-20))
pec_r.scale = (1, 1, -1)
pec_r.data.materials.append(shark_mat)

# Mouth - open jaw
jaw_verts = [
    (-0.5, -0.1, -0.2),
    (-0.5, -0.1, 0.2),
    (-0.3, -0.3, 0.15),
    (-0.3, -0.3, -0.15),
    (-0.5, 0.1, -0.2),
    (-0.5, 0.1, 0.2),
    (-0.3, -0.1, 0.15),
    (-0.3, -0.1, -0.15),
]
jaw_faces = [
    (0,1,2,3,4),
    (4,3,2,1,5),
]
jaw = create_mesh_obj("Jaw", jaw_verts, jaw_faces, (0, 0, 0))
jaw.location = (1.8, -0.5, 0)
jaw.rotation_euler = (math.radians(15), 0, 0)
jaw.data.materials.append(shark_mat)

# Teeth - small cones
teeth_verts = []
teeth_faces = []
num_teeth = 8
for i in range(num_teeth):
    t = i / (num_teeth - 1)
    x = -0.3 + t * 0.6
    z = -0.15 + t * 0.3
    # Upper tooth
    base_idx = len(teeth_verts)
    teeth_verts.append((x, -0.2, z - 0.02))
    teeth_verts.append((x, -0.2, z + 0.02))
    teeth_verts.append((x, -0.05, z))
    teeth_faces.append((base_idx, base_idx+1, base_idx+2))
    # Lower tooth
    base_idx = len(teeth_verts)
    teeth_verts.append((x, 0.0, z - 0.02))
    teeth_verts.append((x, 0.0, z + 0.02))
    teeth_verts.append((x, -0.15, z))
    teeth_faces.append((base_idx, base_idx+1, base_idx+2))

teeth = create_mesh_obj("Teeth", teeth_verts, teeth_faces, (0, 0, 0))
teeth.location = (1.8, -0.5, 0)
teeth.rotation_euler = (math.radians(15), 0, 0)
teeth_mat = bpy.data.materials.new("TeethMat")
teeth_mat.use_nodes = True
tn = teeth_mat.node_tree.nodes
tb = tn.get("Principled BSDF")
tb.inputs["Base Color"].default_value = (0.9, 0.9, 0.85, 1.0)
tb.inputs["Roughness"].default_value = 0.3
teeth.data.materials.append(teeth_mat)

# Eyes
eye_l = make_cylinder("EyeL", 0.04, 0.02, (2.2, -0.4, -0.3), (0, math.radians(90), 0))
eye_r = make_cylinder("EyeR", 0.04, 0.02, (2.2, -0.4, 0.3), (0, math.radians(90), 0))
eye_mat = bpy.data.materials.new("EyeMat")
eye_mat.use_nodes = True
en = eye_mat.node_tree.nodes
eb = en.get("Principled BSDF")
eb.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
eb.inputs["Roughness"].default_value = 0.1
eb.inputs["Metallic"].default_value = 0.5
eye_l.data.materials.append(eye_mat)
eye_r.data.materials.append(eye_mat)

# Gills
for i in range(4):
    z = -0.15 + i * 0.1
    gill_verts = [
        (0, -0.1, -0.02),
        (0, 0.1, -0.02),
        (0.05, 0.1, 0),
        (0.05, -0.1, 0),
    ]
    gill_faces = [(0,1,2,3)]
    gill = create_mesh_obj(f"Gill{i}", gill_verts, gill_faces, (0, 0, 0))
    gill.location = (2.8, -0.4, z)
    gill.rotation_euler = (0, math.radians(90), 0)
    gill_mat = bpy.data.materials.new("GillMat")
    gill_mat.use_nodes = True
    gn = gill_mat.node_tree.nodes
    gb = gn.get("Principled BSDF")
    gb.inputs["Base Color"].default_value = (0.6, 0.5, 0.5, 1.0)
    gb.inputs["Roughness"].default_value = 0.6
    gill.data.materials.append(gill_mat)

# ===================== SPLASH / WATER EFFECTS =====================
# Create splash particles around the shark
splash_verts = []
splash_faces = []
num_splash = 50
for i in range(num_splash):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0.5, 2.0)
    x = 4.5 + dist * math.cos(angle)
    z = dist * math.sin(angle)
    h = random.uniform(0.2, 1.5)
    # Small cone for splash
    base_idx = len(splash_verts)
    splash_verts.append((x, 0, z))
    splash_verts.append((x + 0.1, 0, z + 0.1))
    splash_verts.append((x + 0.1, h, z + 0.1))
    splash_verts.append((x + 0.1, 0, z - 0.1))
    splash_verts.append((x - 0.1, 0, z + 0.1))
    splash_verts.append((x - 0.1, h, z + 0.1))
    splash_verts.append((x - 0.1, 0, z - 0.1))
    splash_verts.append((x, h*1.2, z))
    splash_faces.append((base_idx, base_idx+1, base_idx+2))
    splash_faces.append((base_idx, base_idx+2, base_idx+3))
    splash_faces.append((base_idx, base_idx+3, base_idx+4))
    splash_faces.append((base_idx, base_idx+4, base_idx+5))
    splash_faces.append((base_idx, base_idx+5, base_idx+6))
    splash_faces.append((base_idx, base_idx+6, base_idx+1))
    splash_faces.append((base_idx+1, base_idx+2, base_idx+7))
    splash_faces.append((base_idx+2, base_idx+3, base_idx+7))
    splash_faces.append((base_idx+3, base_idx+4, base_idx+7))
    splash_faces.append((base_idx+4, base_idx+5, base_idx+7))
    splash_faces.append((base_idx+5, base_idx+6, base_idx+7))
    splash_faces.append((base_idx+6, base_idx+1, base_idx+7))

splash = create_mesh_obj("Splash", splash_verts, splash_faces, (0, 0, 0))
splash_mat = bpy.data.materials.new("SplashMat")
splash_mat.use_nodes = True
spn = splash_mat.node_tree.nodes
spb = spn.get("Principled BSDF")
spb.inputs["Base Color"].default_value = (0.7, 0.85, 1.0, 1.0)
spb.inputs["Roughness"].default_value = 0.0
spb.inputs["Transmission Weight"].default_value = 0.8
spb.inputs["Alpha"].default_value = 0.7
splash_mat.blend_method = 'BLEND'
splash.data.materials.append(splash_mat)

# ===================== ADDITIONAL DETAILS =====================

# Life preserver on the boat
bpy.ops.mesh.primitive_torus_add(major_radius=0.4, minor_radius=0.1, location=(2.5, 1.5, 0.5))
life_preserver = bpy.context.active_object
life_preserver.name = "LifePreserver"
lp_mat = bpy.data.materials.new("LifePreserverMat")
lp_mat.use_nodes = True
lpn = lp_mat.node_tree.nodes
lpb = lpn.get("Principled BSDF")
lpb.inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1.0)
lpb.inputs["Roughness"].default_value = 0.6
life_preserver.data.materials.append(lp_mat)

# Net on deck
net_verts = []
net_faces = []
net_size = 1.5
net_res = 8
for i in range(net_res+1):
    for j in range(net_res+1):
        x = -net_size/2 + i * net_size/net_res
        z = -net_size/2 + j * net_size/net_res
        net_verts.append((x, 0, z))
for i in range(net_res):
    for j in range(net_res):
        v1 = i*(net_res+1) + j
        v2 = v1 + 1
        v3 = v1 + (net_res+1)
        v4 = v3 + 1
        net_faces.append((v1, v2, v4, v3))

net = create_mesh_obj("Net", net_verts, net_faces, (0, 0, 0))
net.location = (0.5, 1.0, 0)
net_mat = bpy.data.materials.new("NetMat")
net_mat.use_nodes = True
nn = net_mat.node_tree.nodes
nb = nn.get("Principled BSDF")
nb.inputs["Base Color"].default