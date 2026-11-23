import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the traffic light pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=3.0, location=(0, 0, 1.5))
pole = bpy.context.active_object
pole.name = "Pole"

# Create the traffic light housing (box)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3.2))
housing = bpy.context.active_object
housing.name = "Housing"
bpy.ops.transform.resize(value=(0.4, 0.4, 1.0))

# Create red light (top)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.21, 3.6), segments=32, ring_count=16)
red_light = bpy.context.active_object
red_light.name = "RedLight"

# Create yellow light (middle)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.21, 3.2), segments=32, ring_count=16)
yellow_light = bpy.context.active_object
yellow_light.name = "YellowLight"

# Create green light (bottom)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.21, 2.8), segments=32, ring_count=16)
green_light = bpy.context.active_object
green_light.name = "GreenLight"

# Materials
# Pole material
mat_pole = bpy.data.materials.new(name="PoleMaterial")
mat_pole.use_nodes = True
bsdf_pole = mat_pole.node_tree.nodes["Principled BSDF"]
bsdf_pole.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
bsdf_pole.inputs["Metallic"].default_value = 0.8
pole.data.materials.append(mat_pole)

# Housing material
mat_housing = bpy.data.materials.new(name="HousingMaterial")
mat_housing.use_nodes = True
bsdf_housing = mat_housing.node_tree.nodes["Principled BSDF"]
bsdf_housing.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
housing.data.materials.append(mat_housing)

# Red light material
mat_red = bpy.data.materials.new(name="RedMaterial")
mat_red.use_nodes = True
bsdf_red = mat_red.node_tree.nodes["Principled BSDF"]
bsdf_red.inputs["Base Color"].default_value = (1.0, 0.0, 0.0, 1.0)
bsdf_red.inputs["Emission Color"].default_value = (1.0, 0.0, 0.0, 1.0)
bsdf_red.inputs["Emission Strength"].default_value = 5.0
red_light.data.materials.append(mat_red)

# Yellow light material
mat_yellow = bpy.data.materials.new(name="YellowMaterial")
mat_yellow.use_nodes = True
bsdf_yellow = mat_yellow.node_tree.nodes["Principled BSDF"]
bsdf_yellow.inputs["Base Color"].default_value = (1.0, 0.8, 0.0, 1.0)
bsdf_yellow.inputs["Emission Color"].default_value = (1.0, 0.8, 0.0, 1.0)
bsdf_yellow.inputs["Emission Strength"].default_value = 5.0
yellow_light.data.materials.append(mat_yellow)

# Green light material
mat_green = bpy.data.materials.new(name="GreenMaterial")
mat_green.use_nodes = True
bsdf_green = mat_green.node_tree.nodes["Principled BSDF"]
bsdf_green.inputs["Base Color"].default_value = (0.0, 1.0, 0.0, 1.0)
bsdf_green.inputs["Emission Color"].default_value = (0.0, 1.0, 0.0, 1.0)
bsdf_green.inputs["Emission Strength"].default_value = 5.0
green_light.data.materials.append(mat_green)

# Add a light source for better visualization
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Set viewport to look at the traffic light
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.region_3d.view_location = (0, 0, 3.2)
                space.region_3d.view_distance = 5.0
