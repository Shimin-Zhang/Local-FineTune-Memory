import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up materials
# Blue material for the car body
blue_mat = bpy.data.materials.new(name="CarBlue")
blue_mat.use_nodes = True
bsdf = blue_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.0, 0.2, 0.8, 1.0)
bsdf.inputs["Metallic"].default_value = 0.3
bsdf.inputs["Roughness"].default_value = 0.3

# Black material for wheels
black_mat = bpy.data.materials.new(name="WheelBlack")
black_mat.use_nodes = True
bsdf_black = black_mat.node_tree.nodes["Principled BSDF"]
bsdf_black.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf_black.inputs["Metallic"].default_value = 0.1
bsdf_black.inputs["Roughness"].default_value = 0.6

# --- Create Car Body ---
# Main body: a cube scaled to look like a car
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
body = bpy.context.active_object
body.name = "CarBody"
body.scale = (2.0, 1.0, 0.5)
bpy.ops.object.transform_apply(scale=True)
body.data.materials.append(blue_mat)

# Cabin: a smaller cube on top, slightly towards the back
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.2, 0, 1.0))
cabin = bpy.context.active_object
cabin.name = "CarCabin"
cabin.scale = (1.2, 0.8, 0.4)
bpy.ops.object.transform_apply(scale=True)
cabin.data.materials.append(blue_mat)

# --- Create Wheels ---
wheel_positions = [
    (-1.2, 0.7, 0.3),   # Front Left
    (-1.2, -0.7, 0.3),  # Front Right
    (1.2, 0.7, 0.3),    # Rear Left
    (1.2, -0.7, 0.3),   # Rear Right
]

for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=pos, rotation=(0, math.pi/2, 0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel_{i+1}"
    wheel.data.materials.append(black_mat)

# Add a simple light for visibility
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
sun.data.energy = 3

# Add a camera
bpy.ops.object.camera_add(location=(5, -5, 3))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(70), 0, math.radians(45))
bpy.context.scene.camera = cam
