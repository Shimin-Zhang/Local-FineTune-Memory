import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set world to dark
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.node_tree.nodes["Background"].inputs[0].default_value = (0.0, 0.0, 0.0, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.0

# Create the desk
# Desk top
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.75))
desk_top = bpy.context.active_object
desk_top.name = "DeskTop"
desk_top.scale = (1.2, 0.6, 0.025)

# Desk legs (4 legs)
leg_positions = [
    (-1.0, -0.45, 0.35),
    (1.0, -0.45, 0.35),
    (-1.0, 0.45, 0.35),
    (1.0, 0.45, 0.35),
]
for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.active_object
    leg.name = f"DeskLeg_{i}"
    leg.scale = (0.05, 0.05, 0.35)

# Create the lamp
# Lamp base
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.02, location=(0.6, 0.2, 0.78))
lamp_base = bpy.context.active_object
lamp_base.name = "LampBase"

# Lamp pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.015, depth=0.3, location=(0.6, 0.2, 0.93))
lamp_pole = bpy.context.active_object
lamp_pole.name = "LampPole"

# Lamp shade (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.12, radius2=0.06, depth=0.15, location=(0.6, 0.2, 1.12))
lamp_shade = bpy.context.active_object
lamp_shade.name = "LampShade"

# Create a point light inside the lamp shade
light_data = bpy.data.lights.new("LampLight", type='POINT')
light_data.energy = 50  # Adjust brightness
light_data.color = (1.0, 0.9, 0.7)  # Warm light
light_data.shadow_soft_size = 0.05

light_obj = bpy.data.objects.new("LampLight", light_data)
bpy.context.scene.collection.objects.link(light_obj)
light_obj.location = (0.6, 0.2, 1.1)  # Inside the shade

# Add materials
# Desk material (wood)
wood_mat = bpy.data.materials.new("Wood")
wood_mat.use_nodes = True
bsdf = wood_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.15, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.7

# Apply wood to desk
for obj in [desk_top] + [bpy.data.objects[f"DeskLeg_{i}"] for i in range(4)]:
    obj.data.materials.append(wood_mat)

# Lamp base/pole material (metal)
metal_mat = bpy.data.materials.new("Metal")
metal_mat.use_nodes = True
bsdf = metal_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.3

for obj in [lamp_base, lamp_pole]:
    obj.data.materials.append(metal_mat)

# Lamp shade material (fabric)
shade_mat = bpy.data.materials.new("LampShade")
shade_mat.use_nodes = True
bsdf = shade_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.85, 0.7, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
bsdf.inputs["Transmission Weight"].default_value = 0.3  # Some light passes through

lamp_shade.data.materials.append(shade_mat)

# Add a floor to catch the light
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor_mat = bpy.data.materials.new("FloorMat")
floor_mat.use_nodes = True
bsdf = floor_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.8
floor.data.materials.append(floor_mat)

# Add walls to make a room
# Back wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, -5, 2.5), rotation=(math.radians(90), 0, 0))
back_wall = bpy.context.active_object
back_wall.name = "BackWall"
back_wall.data.materials.append(floor_mat)

# Left wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(-5, 0, 2.5), rotation=(0, math.radians(90), 0))
left_wall = bpy.context.active_object
left_wall.name = "LeftWall"
left_wall.data.materials.append(floor_mat)

# Right wall
bpy.ops.mesh.primitive_plane_add(size=10, location=(5, 0, 2.5), rotation=(0, math.radians(90), 0))
right_wall = bpy.context.active_object
right_wall.name = "RightWall"
right_wall.data.materials.append(floor_mat)

# Set up camera
bpy.ops.object.camera_add(location=(2.5, 2.5, 1.5), rotation=(math.radians(60), 0, math.radians(-45)))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Enable shadows and set render engine
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True

# Make sure only the lamp light is on (no other lights in scene)
for obj in bpy.context.scene.objects:
    if obj.type == 'LIGHT' and obj.name != 'LampLight':
        obj.hide_render = True
