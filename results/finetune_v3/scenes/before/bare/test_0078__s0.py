import bpy
import math
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
def create_mat(name, color, metallic=0.0, rough=0.5, emissive=None, em_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    if emissive:
        bsdf.inputs["Emission Color"].default_value = emissive
        bsdf.inputs["Emission Strength"].default_value = em_str
    return mat

m_hangar_wall = create_mat("hangar_wall", (0.3, 0.3, 0.35), 0.5, 0.6)
m_hangar_floor = create_mat("hangar_floor", (0.2, 0.2, 0.22), 0.3, 0.7)
m_hangar_roof = create_mat("hangar_roof", (0.25, 0.25, 0.28), 0.4, 0.6)
m_fighter_body = create_mat("fighter_body", (0.7, 0.75, 0.8), 0.8, 0.3)
m_fighter_accent = create_mat("fighter_accent", (0.1, 0.4, 0.8), 0.6, 0.4)
m_cradle = create_mat("cradle", (0.15, 0.15, 0.18), 0.6, 0.5)
m_hose = create_mat("fuel_hose", (0.05, 0.05, 0.05), 0.2, 0.8)
m_rail = create_mat("launch_rail", (0.4, 0.4, 0.45), 0.9, 0.2)
m_rail_glow = create_mat("rail_glow", (0.0, 0.0, 0.0), 0.0, 0.0, emissive=(0.0, 0.8, 1.0), em_str=3.0)
m_officer_body = create_mat("officer_body", (0.85, 0.8, 0.7), 0.1, 0.6)
m_officer_suit = create_mat("officer_suit", (0.2, 0.2, 0.3), 0.2, 0.6)
m_wand_glow = create_mat("wand_glow", (0.0, 0.0, 0.0), 0.0, 0.0, emissive=(0.2, 1.0, 0.3), em_str=5.0)
m_wand_glow2 = create_mat("wand_glow2", (0.0, 0.0, 0.0), 0.0, 0.0, emissive=(1.0, 0.5, 0.1), em_str=5.0)

# --- Hangar Structure ---
# Floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Hangar_Floor"
floor.data.materials.append(m_hangar_floor)
floor.scale = (1.5, 2, 1)

# Back wall
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -10, 4))
back_wall = bpy.context.object
back_wall.name = "Hangar_BackWall"
back_wall.scale = (15, 1, 4)
back_wall.data.materials.append(m_hangar_wall)

# Left wall
bpy.ops.mesh.primitive_plane_add(size=1, location=(-15, 0, 4))
left_wall = bpy.context.object
left_wall.name = "Hangar_LeftWall"
left_wall.rotation_euler = (0, math.radians(90), 0)
left_wall.scale = (20, 1, 4)
left_wall.data.materials.append(m_hangar_wall)

# Right wall
bpy.ops.mesh.primitive_plane_add(size=1, location=(15, 0, 4))
right_wall = bpy.context.object
right_wall.name = "Hangar_RightWall"
right_wall.rotation_euler = (0, math.radians(90), 0)
right_wall.scale = (20, 1, 4)
right_wall.data.materials.append(m_hangar_wall)

# Roof
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 8))
roof = bpy.context.object
roof.name = "Hangar_Roof"
roof.scale = (15, 20, 1)
roof.data.materials.append(m_hangar_roof)

# --- Fighter 1 (left) ---
def make_fighter(name, loc, rot_z=0):
    parts = []
    # Fuselage
    bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.1, depth=4, location=loc, rotation=(math.radians(90), 0, rot_z))
    fus = bpy.context.object
    fus.name = name + "_Fuselage"
    fus.data.materials.append(m_fighter_body)
    parts.append(fus)
    # Wings
    bpy.ops.mesh.primitive_cube_add(location=loc)
    wing = bpy.context.object
    wing.name = name + "_Wing"
    wing.scale = (0.1, 2.5, 0.5)
    wing.location = (loc[0], loc[1], loc[2] - 0.3)
    wing.rotation_euler = (0, 0, rot_z)
    wing.data.materials.append(m_fighter_accent)
    parts.append(wing)
    # Tail fin
    bpy.ops.mesh.primitive_cube_add(location=(loc[0], loc[1] - 1.5, loc[2] + 0.8))
    fin = bpy.context.object
    fin.name = name + "_Fin"
    fin.scale = (0.1, 0.5, 1.0)
    fin.rotation_euler = (0, 0, rot_z)
    fin.data.materials.append(m_fighter_accent)
    parts.append(fin)
    return parts

f1 = make_fighter("Fighter1", (-5, -2, 1.5), math.radians(10))
f2 = make_fighter("Fighter2", (5, -2, 1.5), math.radians(-10))

# --- Cradles ---
def make_cradle(name, loc):
    parts = []
    # Base
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.3, location=loc)
    base = bpy.context.object
    base.name = name + "_Base"
    base.data.materials.append(m_cradle)
    parts.append(base)
    # Arms
    for i, ang in enumerate([0, 120, 240]):
        a = math.radians(ang)
        arm_loc = (loc[0] + 0.8 * math.cos(a), loc[1] + 0.8 * math.sin(a), loc[2] + 0.8)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=1.2, location=arm_loc, rotation=(0, 0, a))
        arm = bpy.context.object
        arm.name = name + f"_Arm{i}"
        arm.data.materials.append(m_cradle)
        parts.append(arm)
    return parts

c1 = make_cradle("Cradle1", (-5, -2, 0.15))
c2 = make_cradle("Cradle2", (5, -2, 0.15))

# --- Fuel Hoses ---
def make_hose(name, start, end, radius=0.08):
    mid = (Vector(start) + Vector(end)) / 2
    length = (Vector(end) - Vector(start)).length
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid)
    hose = bpy.context.object
    hose.name = name
    # Orient along the vector
    direction = Vector(end) - Vector(start)
    rot = direction.to_track_quat('Z', 'Y').to_euler()
    hose.rotation_euler = rot
    hose.data.materials.append(m_hose)
    return hose

h1 = make_hose("FuelHose1", (-12, -6, 2), (-6, -2, 1.5))
h2 = make_hose("FuelHose2", (12, -6, 2), (6, -2, 1.5))
h3 = make_hose("FuelHose3", (-12, -6, 3), (-6, -2, 2.0))
h4 = make_hose("FuelHose4", (12, -6, 3), (6, -2, 2.0))

# --- Launch Rail ---
# Main rail beam
bpy.ops.mesh.primitive_cube_add(location=(0, 5, 0.3))
rail = bpy.context.object
rail.name = "LaunchRail"
rail.scale = (12, 0.5, 0.3)
rail.data.materials.append(m_rail)

# Glow strip on top
bpy.ops.mesh.primitive_cube_add(location=(0, 5, 0.65))
rail_glow = bpy.context.object
rail_glow.name = "LaunchRail_Glow"
rail_glow.scale = (12, 0.2, 0.05)
rail_glow.data.materials.append(m_rail_glow)

# Support struts
for x in [-8, -4, 0, 4, 8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.6, location=(x, 5, 0.3))
    strut = bpy.context.object
    strut.name = f"RailStrut_{x}"
    strut.data.materials.append(m_rail)

# --- Deck Officer ---
def make_officer(name, loc):
    parts = []
    # Body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.2, location=loc)
    body = bpy.context.object
    body.name = name + "_Body"
    body.data.materials.append(m_officer_suit)
    parts.append(body)
    # Head
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(loc[0], loc[1], loc[2] + 0.85))
    head = bpy.context.object
    head.name = name + "_Head"
    head.data.materials.append(m_officer_body)
    parts.append(head)
    # Arms
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=(loc[0] + side * 0.4, loc[1], loc[2] + 0.3), rotation=(0, math.radians(30 * side), 0))
        arm = bpy.context.object
        arm.name = name + f"_Arm{side}"
        arm.data.materials.append(m_officer_suit)
        parts.append(arm)
    # Legs
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, location=(loc[0] + side * 0.15, loc[1], loc[2] - 1.0))
        leg = bpy.context.object
        leg.name = name + f"_Leg{side}"
        leg.data.materials.append(m_officer_suit)
        parts.append(leg)
    # Glowing wand 1 (left hand)
    wand1_loc = (loc[0] - 0.7, loc[1], loc[2] + 0.6)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.6, location=wand1_loc, rotation=(math.radians(45), 0, 0))
    wand1 = bpy.context.object
    wand1.name = name + "_Wand1"
    wand1.data.materials.append(m_wand_glow)
    parts.append(wand1)
    # Glowing wand 2 (right hand)
    wand2_loc = (loc[0] + 0.7, loc[1], loc[2] + 0.6)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.6, location=wand2_loc, rotation=(math.radians(-45), 0, 0))
    wand2 = bpy.context.object
    wand2.name = name + "_Wand2"
    wand2.data.materials.append(m_wand_glow2)
    parts.append(wand2)
    return parts

off1 = make_officer("Officer1", (-3, 3, 1.0))
off2 = make_officer("Officer2", (3, 3, 1.0))

# --- Lighting ---
# Key light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 7))
key_light = bpy.context.object
key_light.name = "KeyLight"
key_light.data.energy = 500
key_light.data.color = (1.0, 0.95, 0.9)

# Fill lights
bpy.ops.object.light_add(type='POINT', location=(-10, -5, 5))
fill1 = bpy.context.object
fill1.name = "FillLight1"
fill1.data.energy = 200
fill1.data.color = (0.8, 0.85, 1.0)

bpy.ops.object.light_add(type='POINT', location=(10, -5, 5))
fill2 = bpy.context.object
fill2.name = "FillLight2"
fill2.data.energy = 200
fill2.data.color = (0.8, 0.85, 1.0)

# Rail glow light
bpy.ops.object.light_add(type='POINT', location=(0, 5, 1.5))
rail_light = bpy.context.object
rail_light.name = "RailGlowLight"
rail_light.data.energy = 300
rail_light.data.color = (0.0, 0.8, 1.0)

# Wand glow lights
bpy.ops.object.light_add(type='POINT', location=(-3.7, 3, 1.8))
wand_l1 = bpy.context.object
wand_l1.name = "WandLight1"
wand_l1.data.energy = 50
wand_l1.data.color = (0.2, 1.0, 0.3)

bpy.ops.object.light_add(type='POINT', location=(3.7, 3, 1.8))
wand_l2 = bpy.context.object
wand_l2.name = "WandLight2"
wand_l2.data.energy = 50
wand_l2.data.color = (1.0, 0.5, 0.1)

# --- Camera ---
bpy.ops.object.camera_add(location=(0, 18, 4), rotation=(math.radians(75), 0, 0))
cam = bpy.context.object
cam.name = "HangarCam"
bpy.context.scene.camera = cam

# --- World background ---
world = bpy.context.scene.world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
bg_node.inputs[1].default_value = 1.0

print("Hangar scene created successfully!")
