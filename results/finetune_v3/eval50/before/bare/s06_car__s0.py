import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the car body (blue)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.5))
car_body = bpy.context.active_object
car_body.name = "CarBody"
car_body.scale = (1.5, 0.8, 0.4)
bpy.ops.object.transform_apply(scale=True)

# Create car cabin (blue)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.9))
car_cabin = bpy.context.active_object
car_cabin.name = "CarCabin"
car_cabin.scale = (1.0, 0.7, 0.3)
bpy.ops.object.transform_apply(scale=True)

# Material for car body (blue)
blue_material = bpy.data.materials.new(name="BlueCar")
blue_material.use_nodes = True
bsdf = blue_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.0, 0.2, 0.8, 1.0)
bsdf.inputs["Metallic"].default_value = 0.5
bsdf.inputs["Roughness"].default_value = 0.3

car_body.data.materials.append(blue_material)
car_cabin.data.materials.append(blue_material)

# Create four black wheels
wheel_positions = [
    (-0.9, 0.6, 0.25),   # Front left
    (-0.9, -0.6, 0.25),  # Front right
    (0.9, 0.6, 0.25),    # Rear left
    (0.9, -0.6, 0.25)    # Rear right
]

black_material = bpy.data.materials.new(name="BlackWheel")
black_material.use_nodes = True
bsdf_black = black_material.node_tree.nodes["Principled BSDF"]
bsdf_black.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
bsdf_black.inputs["Roughness"].default_value = 0.8

for i, pos in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.2, location=pos, rotation=(0, math.radians(90), 0))
    wheel = bpy.context.active_object
    wheel.name = f"Wheel{i+1}"
    wheel.data.materials.append(black_material)
