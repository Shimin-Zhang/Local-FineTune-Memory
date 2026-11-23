import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- MATERIALS ---
def make_mat(name, color, roughness=0.8, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

mat_stone = make_mat("Stone", (0.25, 0.22, 0.20), roughness=0.9)
mat_stone_dark = make_mat("StoneDark", (0.15, 0.13, 0.12), roughness=0.95)
mat_stone_bridge = make_mat("BridgeStone", (0.30, 0.27, 0.24), roughness=0.85)
mat_stone_pillar = make_mat("PillarStone", (0.28, 0.25, 0.22), roughness=0.85)
mat_metal = make_mat("Metal", (0.5, 0.5, 0.55), roughness=0.3, metallic=1.0)
mat_metal_dark = make_mat("MetalDark", (0.3, 0.3, 0.32), roughness=0.4, metallic=1.0)
mat_cloth_grey = make_mat("ClothGrey", (0.35, 0.33, 0.30), roughness=0.95)
mat_cloth_dark = make_mat("ClothDark", (0.20, 0.19, 0.18), roughness=0.95)
mat_wood = make_mat("Wood", (0.35, 0.22, 0.10), roughness=0.8)
mat_wood_dark = make_mat("WoodDark", (0.25, 0.15, 0.07), roughness=0.85)
mat_skin = make_mat("Skin", (0.75, 0.60, 0.48), roughness=0.7)
mat_beard = make_mat("Beard", (0.9, 0.9, 0.88), roughness=0.95)
mat_eye = make_mat("Eye", (0.1, 0.1, 0.1), roughness=0.3)
mat_fire = make_mat("Fire", (1.0, 0.3, 0.05), roughness=0.5, emission=(1.0, 0.3, 0.05), emission_strength=5.0)
mat_fire_inner = make_mat("FireInner", (1.0, 0.6, 0.1), roughness=0.3, emission=(1.0, 0.6, 0.1), emission_strength=8.0)
mat_smoke = make_mat("Smoke", (0.15, 0.15, 0.15), roughness=1.0)
mat_chasm = make_mat("Chasm", (0.05, 0.05, 0.05), roughness=1.0)
mat_glow = make_mat("Glow", (1.0, 0.5, 0.1), roughness=0.2, emission=(1.0, 0.5, 0.1), emission_strength=3.0)
mat_balrog_body = make_mat("BalrogBody", (0.08, 0.08, 0.10), roughness=0.6)
mat_balrog_fire = make_mat("BalrogFire", (1.0, 0.2, 0.0), roughness=0.3, emission=(1.0, 0.2, 0.0), emission_strength=10.0)
mat_balrog_eye = make_mat("BalrogEye", (1.0, 0.8, 0.0), roughness=0.1, emission=(1.0, 0.8, 0.0), emission_strength=15.0)
mat_balrog_wing = make_mat("BalrogWing", (0.05, 0.05, 0.08), roughness=0.7)

# --- BRIDGE ---
# Narrow stone bridge over chasm
bridge_width = 2.0
bridge_length = 12.0
bridge_thickness = 0.4
bridge_y = 0.0

# Bridge deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, bridge_y, 0))
bridge = bpy.context.object
bridge.name = "Bridge_Deck"
bridge.scale = (bridge_length/2, bridge_width/2, bridge_thickness/2)
bridge.data.materials.append(mat_stone_bridge)
bpy.ops.object.transform_apply(scale=True)

# Add stone texture via subdivision
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=10)
bpy.ops.object.mode_set(mode='OBJECT')

# Bridge railing - left
for i in range(12):
    x = -bridge_length/2 + 0.5 + i * (bridge_length/12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -bridge_width/2 + 0.1, bridge_thickness/2 + 0.5))
    rail = bpy.context.object
    rail.name = f"Rail_L_{i}"
    rail.scale = (0.15, 0.1, 0.5)
    rail.data.materials.append(mat_stone_pillar)
    bpy.ops.object.transform_apply(scale=True)

# Bridge railing - right
for i in range(12):
    x = -bridge_length/2 + 0.5 + i * (bridge_length/12)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, bridge_width/2 - 0.1, bridge_thickness/2 + 0.5))
    rail = bpy.context.object
    rail.name = f"Rail_R_{i}"
    rail.scale = (0.15, 0.1, 0.5)
    rail.data.materials.append(mat_stone_pillar)
    bpy.ops.object.transform_apply(scale=True)

# Railing top bars
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -bridge_width/2 + 0.1, bridge_thickness/2 + 1.0))
rail_top_l = bpy.context.object
rail_top_l.name = "Rail_Top_L"
rail_top_l.scale = (bridge_length/2, 0.08, 0.08)
rail_top_l.data.materials.append(mat_stone_pillar)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, bridge_width/2 - 0.1, bridge_thickness/2 + 1.0))
rail_top_r = bpy.context.object
rail_top_r.name = "Rail_Top_R"
rail_top_r.scale = (bridge_length/2, 0.08, 0.08)
rail_top_r.data.materials.append(mat_stone_pillar)
bpy.ops.object.transform_apply(scale=True)

# Bridge supports - large stone pillars going down into chasm
for x in [-bridge_length/2 + 1, 0, bridge_length/2 - 1]:
    for y in [-bridge_width/2 + 0.3, bridge_width/2 - 0.3]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=8, location=(x, y, -4))
        pillar = bpy.context.object
        pillar.name = f"Pillar_{x}_{y}"
        pillar.data.materials.append(mat_stone_dark)

# Chasm walls - left
bpy.ops.mesh.primitive_cube_add(size=1, location=(-bridge_width/2 - 3, 0, -5))
chasm_l = bpy.context.object
chasm_l.name = "Chasm_Wall_L"
chasm_l.scale = (3, bridge_length/2 + 2, 5)
chasm_l.data.materials.append(mat_stone_dark)
bpy.ops.object.transform_apply(scale=True)

# Chasm walls - right
bpy.ops.mesh.primitive_cube_add(size=1, location=(bridge_width/2 + 3, 0, -5))
chasm_r = bpy.context.object
chasm_r.name = "Chasm_Wall_R"
chasm_r.scale = (3, bridge_length/2 + 2, 5)
chasm_r.data.materials.append(mat_stone_dark)
bpy.ops.object.transform_apply(scale=True)

# Chasm floor (deep dark)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -10))
chasm_floor = bpy.context.object
chasm_floor.name = "Chasm_Floor"
chasm_floor.scale = (bridge_width + 6, bridge_length + 4, 0.5)
chasm_floor.data.materials.append(mat_chasm)
bpy.ops.object.transform_apply(scale=True)

# --- GANDALF ---
# Position: near center of bridge, facing toward the Balrog (let's say toward +X direction)
gandalf_x = -1.5
gandalf_y = 0
gandalf_z = bridge_thickness/2  # standing on bridge

# Gandalf's body - robe (cylinder tapered)
bpy.ops.mesh.primitive_cone_add(radius1=0.45, radius2=0.25, depth=1.6, location=(gandalf_x, gandalf_y, gandalf_z + 0.8))
robe = bpy.context.object
robe.name = "Gandalf_Robe"
robe.data.materials.append(mat_cloth_grey)

# Gandalf's torso/upper robe
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.6, location=(gandalf_x, gandalf_y, gandalf_z + 1.7))
torso = bpy.context.object
torso.name = "Gandalf_Torso"
torso.data.materials.append(mat_cloth_dark)

# Gandalf's head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(gandalf_x, gandalf_y, gandalf_z + 2.15))
head = bpy.context.object
head.name = "Gandalf_Head"
head.scale = (1, 1, 1.1)
head.data.materials.append(mat_skin)
bpy.ops.object.transform_apply(scale=True)

# Gandalf's beard
bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.02, depth=0.4, location=(gandalf_x + 0.05, gandalf_y, gandalf_z + 1.95))
beard = bpy.context.object
beard.name = "Gandalf_Beard"
beard.rotation_euler = (math.radians(10), 0, 0)
beard.data.materials.append(mat_beard)

# Gandalf's hat (pointed wizard hat)
bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.02, depth=0.5, location=(gandalf_x, gandalf_y, gandalf_z + 2.5))
hat = bpy.context.object
hat.name = "Gandalf_Hat"
hat.data.materials.append(mat_cloth_dark)

# Hat brim
bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.05, location=(gandalf_x, gandalf_y, gandalf_z + 2.28))
hat_brim = bpy.context.object
hat_brim.name = "Gandalf_HatBrim"
hat_brim.data.materials.append(mat_cloth_dark)

# Gandalf's left arm (holding staff) - extended forward
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.5, location=(gandalf_x + 0.25, gandalf_y - 0.15, gandalf_z + 1.5))
arm_l = bpy.context.object
arm_l.name = "Gandalf_Arm_L"
arm_l.rotation_euler = (0, math.radians(-30), 0)
arm_l.data.materials.append(mat_cloth_grey)

# Gandalf's right arm (holding sword) - extended forward
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.5, location=(gandalf_x + 0.25, gandalf_y + 0.15, gandalf_z + 1.5))
arm_r = bpy.context.object
arm_r.name = "Gandalf_Arm_R"
arm_r.rotation_euler = (0, math.radians(30), 0)
arm_r.data.materials.append(mat_cloth_grey)

# Gandalf's staff (long wooden staff)
staff_x = gandalf_x + 0.45
staff_y = gandalf_y - 0.15
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=2.2, location=(staff_x, staff_y, gandalf_z + 1.1))
staff = bpy.context.object
staff.name = "Gandalf_Staff"
staff.rotation_euler = (0, math.radians(10), 0)
staff.data.materials.append(mat_wood_dark)

# Staff top (carved)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(staff_x + 0.1, staff_y, gandalf_z + 2.2))
staff_top = bpy.context.object
staff_top.name = "Gandalf_StaffTop"
staff_top.data.materials.append(mat_wood)

# Gandalf's sword (Glamdring)
sword_x = gandalf_x + 0.45
sword_y = gandalf_y + 0.15
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.9, location=(sword_x, sword_y, gandalf_z + 1.5))
sword_blade = bpy.context.object
sword_blade.name = "Gandalf_Sword_Blade"
sword_blade.rotation_euler = (0, math.radians(20), 0)
sword_blade.data.materials.append(mat_metal)

# Sword hilt
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.15, location=(sword_x - 0.15, sword_y, gandalf_z + 1.05))
sword_hilt = bpy.context.object
sword_hilt.name = "Gandalf_Sword_Hilt"
sword_hilt.rotation_euler = (0, math.radians(20), 0)
sword_hilt.data.materials.append(mat_metal_dark)

# Sword guard
bpy.ops.mesh.primitive_cube_add(size=1, location=(sword_x - 0.08, sword_y, gandalf_z + 1.15))
sword_guard = bpy.context.object
sword_guard.name = "Gandalf_Sword_Guard"
sword_guard.scale = (0.05, 0.12, 0.03)
sword_guard.rotation_euler = (0, math.radians(20), 0)
sword_guard.data.materials.append(mat_metal_dark)
bpy.ops.object.transform_apply(scale=True)

# Gandalf's cloak (flowing)
bpy.ops.mesh.primitive_plane_add(size=1, location=(gandalf_x - 0.2, gandalf_y, gandalf_z + 1.0))
cloak = bpy.context.object
cloak.name = "Gandalf_Cloak"
cloak.scale = (0.6, 0.8, 1)
cloak.rotation_euler = (math.radians(15), math.radians(-10), 0)
cloak.data.materials.append(mat_cloth_grey)

# --- BALROG ---
# Position: far end of bridge, facing Gandalf (toward -X direction)
balrog_x = 4.5
balrog_y = 0
balrog_z = bridge_thickness/2

# Balrog body - large dark mass
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(balrog_x, balrog_y, balrog_z + 1.5))
balrog_body = bpy.context.object
balrog_body.name = "Balrog_Body"
balrog_body.scale = (1.5, 1.2, 2.0)
balrog_body.data.materials.append(mat_balrog_body)
bpy.ops.object.transform_apply(scale=True)

# Balrog head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(balrog_x - 1.2, balrog_y, balrog_z + 3.2))
balrog_head = bpy.context.object
balrog_head.name = "Balrog_Head"
balrog_head.scale = (1.2, 1.0, 1.3)
balrog_head.data.materials.append(mat_balrog_body)
bpy.ops.object.transform_apply(scale=True)

# Balrog eyes (glowing)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(balrog_x - 1.7, balrog_y - 0.2, balrog_z + 3.4))
eye_l = bpy.context.object
eye_l.name = "Balrog_Eye_L"
eye_l.data.materials.append(mat_balrog_eye)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(balrog_x - 1.7, balrog_y + 0.2, balrog_z + 3.4))
eye_r = bpy.context.object
eye_r.name = "Balrog_Eye_R"
eye_r.data.materials.append(mat_balrog_eye)

# Balrog mouth (fire)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(balrog_x - 1.8, balrog_y, balrog_z + 2.9))
balrog_mouth = bpy.context.object
balrog_mouth.name = "Balrog_Mouth"
balrog_mouth.scale = (1.5, 1.2, 0.8)
balrog_mouth.data.materials.append(mat_balrog_fire)
bpy.ops.object.transform_apply(scale=True)

# Balrog arms - large clawed
# Left arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.5, location=(balrog_x - 0.5, balrog_y - 1.0, balrog_z + 1.5))
balrog_arm_l = bpy.context.object
balrog_arm_l.name = "Balrog_Arm_L"
balrog_arm_l.rotation_euler = (0, math.radians(45), 0)
balrog_arm_l.data.materials.append(mat_balrog_body)

# Right arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.5, location=(balrog_x - 0.5, balrog_y + 1.0, balrog_z + 1.5))
balrog_arm_r = bpy.context.object
balrog_arm_r.name = "Balrog_Arm_R"
balrog_arm_r.rotation_euler = (0, math.radians(-45), 0)
balrog_arm_r.data.materials.append(mat_balrog_body)

# Balrog claws
for i in range(3):
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.01, depth=0.3, 
        location=(balrog_x - 1.2, balrog_y - 1.2 + i*0.2, balrog_z + 0.8))
    claw = bpy.context.object
    claw.name = f"Balrog_Claw_L_{i}"
    claw.rotation_euler = (math.radians(-45), 0, 0)
    claw.data.materials.append(mat_balrog_body)

for i in range(3):
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, radius2=0.01, depth=0.3, 
        location=(balrog_x - 1.2, balrog_y + 1.2 - i*0.2, balrog_z + 0.8))
    claw = bpy.context.object
    claw.name = f"Balrog_Claw_R_{i}"
    claw.rotation_euler = (math.radians(-45), 0, 0)
    claw.data.materials.append(mat_balrog_body)

# Balrog wings (tattered)
bpy.ops.mesh.primitive_plane_add(size=1, location=(balrog_x + 0.5, balrog_y - 1.5, balrog_z + 2.5))
wing_l = bpy.context.object
wing_l.name = "Balrog_Wing_L"
wing_l.scale = (1.5, 2.0, 1)
wing_l.rotation_euler = (math.radians(30), math.radians(20), 0)
wing_l.data.materials.append(mat_balrog_wing)

bpy.ops.mesh.primitive_plane_add(size=1, location=(balrog_x + 0.5, balrog_y + 1.5, balrog_z + 2.5))
wing_r = bpy.context.object
wing_r.name = "Balrog_Wing_R"
wing_r.scale = (1.5, 2.0, 1)
wing_r.rotation_euler = (math.radians(30), math.radians(-20), 0)
wing_r.data.materials.append(mat_balrog_wing)

# Balrog legs
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(balrog_x + 0.3, balrog_y - 0.5, balrog_z + 0.75))
balrog_leg_l = bpy.context.object
balrog_leg_l.name = "Balrog_Leg_L"
balrog_leg_l.data.materials.append(mat_balrog_body)

bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=1.5, location=(balrog_x + 0.3, balrog_y + 0.5, balrog_z + 0.75))
balrog_leg_r = bpy.context.object
balrog_leg_r.name = "Balrog_Leg_R"
balrog_leg_r.data.materials.append(mat_balrog_body)

# --- FIRE AND SMOKE ---
# Fire from Balrog's mouth
for i in range(5):
    x = balrog_x - 2.0 - i * 0.3
    y = (i % 2 - 0.5) * 0.3
    z = balrog_z + 2.9 + i * 0.1
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2 - i*0.03, location=(x, y, z))
    fire = bpy.context.object
    fire.name = f"Fire_{i}"
    fire.data.materials.append(mat_fire if i > 2 else mat_fire_inner)

# Smoke rising
for i in range(8):
    x = balrog_x - 1.0 + random.uniform(-0.5, 0.5)
    y = random.uniform(-0.5, 0.5)
    z = balrog_z + 3.5 + i * 0.5
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3 + i*0.05, location=(x, y, z))
    smoke = bpy.context.object
    smoke.name = f"Smoke_{i}"
    smoke.data.materials.append(mat_smoke)

# Fire on the ground near Balrog
for i in range(4):
    x = balrog_x - 0.5 + random.uniform(-0.5, 0.5)
    y = random.uniform(-0.8, 0.8)
    z = balrog_z + 0.1
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x, y, z))
    fire_ground = bpy.context.object
    fire_ground.name = f"FireGround_{i}"
    fire_ground.data.materials.append(mat_fire)

# --- LIGHTING ---
# Main fire light from Balrog
bpy.ops.object.light_add(type='POINT', location=(balrog_x - 1.5, balrog_y, balrog_z + 3.0))
fire_light = bpy.context.object
fire_light.name = "Fire_Light"
fire_light.data.energy = 500
fire_light.data.color = (1.0, 0.4, 0.1)
fire_light.data.shadow_soft_size = 0.5

# Ambient light (dim, from above)
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.object
sun.name = "Ambient_Sun"
sun.data.energy = 0.5
sun.data.color = (0.3, 0.3, 0.4)

# Rim light from behind Balrog
bpy.ops.object.light_add(type='POINT', location=(balrog_x + 2, balrog_y, balrog_z + 2))
rim_light = bpy.context.object
rim_light.name = "Rim_Light"
rim_light.data.energy = 100
rim_light.data.color = (1.0, 0.3, 0.0)

# --- CAMERA ---
# Camera positioned to capture the dramatic scene
bpy.ops.object.camera_add(location=(-5, 3, 2.5))
camera = bpy.context.object
camera.name = "Main_Camera"

# Point camera at the middle of the bridge (between Gandalf and Balrog)
target = Vector((1.5, 0, 1.5))
direction = target - camera.location
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set as active camera
bpy.context.scene.camera = camera

# --- WORLD BACKGROUND ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
    bg_node.inputs[1].default_value = 1.0

# --- RENDER SETTINGS ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.view_settings.look = 'AgX - Punchy'

print("Scene built: Bridge of Khazad-dum with Gandalf and the Balrog")
