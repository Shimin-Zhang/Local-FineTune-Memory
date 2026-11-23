import bpy
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create materials
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

# Materials
wood_mat = create_material("Wood", (0.4, 0.25, 0.1, 1.0), roughness=0.6)
fabric_mat = create_material("Fabric", (0.3, 0.35, 0.45, 1.0), roughness=0.8)
metal_mat = create_material("Metal", (0.7, 0.7, 0.7, 1.0), roughness=0.3, metallic=0.8)
glass_mat = create_material("Glass", (0.9, 0.9, 0.9, 0.3), roughness=0.1)
rug_mat = create_material("Rug", (0.6, 0.2, 0.2, 1.0), roughness=0.9)
lamp_shade_mat = create_material("LampShade", (0.9, 0.85, 0.7, 1.0), roughness=0.7)
floor_mat = create_material("Floor", (0.5, 0.4, 0.3, 1.0), roughness=0.7)
wall_mat = create_material("Wall", (0.85, 0.85, 0.8, 1.0), roughness=0.9)
cushion_mat = create_material("Cushion", (0.5, 0.6, 0.5, 1.0), roughness=0.85)

# --- Floor ---
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.object
floor.name = "Floor"
floor.data.materials.append(floor_mat)

# --- Walls (two walls for a corner view) ---
# Back wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, -5, 2.5), rotation=(math.radians(90), 0, 0))
back_wall = bpy.context.object
back_wall.name = "BackWall"
back_wall.data.materials.append(wall_mat)

# Left wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(-5, 0, 2.5), rotation=(0, math.radians(90), 0))
left_wall = bpy.context.object
left_wall.name = "LeftWall"
left_wall.data.materials.append(wall_mat)

# --- Rug ---
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0.5, 0.01))
rug = bpy.context.object
rug.name = "Rug"
rug.data.materials.append(rug_mat)

# --- Sofa ---
def create_box(name, size, location, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    obj.data.materials.append(material)
    return obj

# Sofa base
sofa_base = create_box("SofaBase", (2.4, 0.9, 0.4), (0, -1.5, 0.2), fabric_mat)
# Sofa back
sofa_back = create_box("SofaBack", (2.4, 0.2, 0.7), (0, -1.9, 0.75), fabric_mat)
# Left arm
sofa_arm_l = create_box("SofaArmL", (0.2, 0.9, 0.5), (-1.1, -1.5, 0.45), fabric_mat)
# Right arm
sofa_arm_r = create_box("SofaArmR", (0.2, 0.9, 0.5), (1.1, -1.5, 0.45), fabric_mat)
# Seat cushions
for i, x in enumerate([-0.6, 0.6]):
    cushion = create_box(f"SeatCushion{i}", (1.0, 0.7, 0.15), (x, -1.4, 0.475), cushion_mat)
# Back cushions
for i, x in enumerate([-0.6, 0.6]):
    back_cushion = create_box(f"BackCushion{i}", (1.0, 0.15, 0.5), (x, -1.85, 0.75), cushion_mat)
# Sofa legs
for x in [-1.0, 1.0]:
    for y in [-1.1, -1.9]:
        leg = create_box(f"SofaLeg_{x}_{y}", (0.08, 0.08, 0.1), (x, y, 0.05), wood_mat)

# --- Coffee Table ---
table_top = create_box("CoffeeTableTop", (1.2, 0.6, 0.05), (0, 0.5, 0.45), wood_mat)
for x in [-0.5, 0.5]:
    for y in [0.2, 0.8]:
        leg = create_box(f"TableLeg_{x}_{y}", (0.05, 0.05, 0.43), (x, y, 0.215), wood_mat)

# --- Floor Lamp ---
lamp_base = create_box("LampBase", (0.3, 0.3, 0.05), (-2, -2, 0.025), metal_mat)
lamp_pole = create_box("LampPole", (0.04, 0.04, 1.5), (-2, -2, 0.8), metal_mat)
# Lamp shade (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.2, depth=0.4, location=(-2, -2, 1.7))
lamp_shade = bpy.context.object
lamp_shade.name = "LampShade"
lamp_shade.data.materials.append(lamp_shade_mat)

# Add a point light inside the lamp shade
light_data = bpy.data.lights.new("LampLight", type='POINT')
light_data.energy = 50
light_data.color = (1.0, 0.9, 0.7)
light_obj = bpy.data.objects.new("LampLight", light_data)
light_obj.location = (-2, -2, 1.6)
bpy.context.collection.objects.link(light_obj)

# --- Camera ---
bpy.ops.object.camera_add(location=(3, 3, 2.5), rotation=(math.radians(60), 0, math.radians(-45)))
camera = bpy.context.object
camera.name = "LivingRoomCamera"
bpy.context.scene.camera = camera

# --- World lighting ---
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.8, 0.8, 0.85, 1.0)
    bg.inputs[1].default_value = 0.5
