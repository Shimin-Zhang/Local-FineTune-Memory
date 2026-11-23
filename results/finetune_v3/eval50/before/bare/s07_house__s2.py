import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up materials
def create_material(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
    return mat

# Create materials
white_wall_mat = create_material("WhiteWall", (1, 1, 1, 1))
red_roof_mat = create_material("RedRoof", (0.8, 0.05, 0.05, 1))
brown_door_mat = create_material("BrownDoor", (0.35, 0.15, 0.05, 1))
window_glass_mat = create_material("WindowGlass", (0.7, 0.85, 1.0, 1))

# Build the house body (walls)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.5))
house_body = bpy.context.active_object
house_body.scale = (2, 2, 1.5)
bpy.ops.object.transform_apply(scale=True)
house_body.data.materials.append(white_wall_mat)

# Build the roof (a triangular prism / pyramid-like shape)
# Using a cone with 4 vertices to make a pyramid roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=3.0, radius2=0, depth=1.2, location=(0, 0, 3.6))
roof = bpy.context.active_object
roof.rotation_euler = (0, 0, math.radians(45))
roof.scale = (1, 1, 1)
bpy.ops.object.transform_apply(rotation=True)
roof.data.materials.append(red_roof_mat)

# Build the door (brown)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -2.01, 0.8))
door = bpy.context.active_object
door.scale = (0.5, 0.05, 0.8)
bpy.ops.object.transform_apply(scale=True)
door.data.materials.append(brown_door_mat)

# Build two windows
# Left window
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.0, -2.01, 1.5))
window_left = bpy.context.active_object
window_left.scale = (0.4, 0.05, 0.4)
bpy.ops.object.transform_apply(scale=True)
window_left.data.materials.append(window_glass_mat)

# Right window
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.0, -2.01, 1.5))
window_right = bpy.context.active_object
window_right.scale = (0.4, 0.05, 0.4)
bpy.ops.object.transform_apply(scale=True)
window_right.data.materials.append(window_glass_mat)

# Add a ground plane for context
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = create_material("Ground", (0.3, 0.5, 0.2, 1))
ground.data.materials.append(ground_mat)

# Add a simple light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(45), 0, math.radians(45))
sun.data.energy = 3.0

# Set up a camera
bpy.ops.object.camera_add(location=(6, -8, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(30))
bpy.context.scene.camera = camera
