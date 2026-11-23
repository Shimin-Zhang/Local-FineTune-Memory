import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=3, location=(0, 0, 1.5))
pole = bpy.context.active_object
pole.name = "Pole"
mat_pole = bpy.data.materials.new("PoleMaterial")
mat_pole.use_nodes = True
bsdf = mat_pole.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1)
bsdf.inputs["Metallic"].default_value = 0.8
pole.data.materials.append(mat_pole)

# Create the traffic light housing
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 3.5))
housing = bpy.context.active_object
housing.name = "Housing"
housing.scale = (0.4, 0.4, 0.9)
bpy.ops.object.transform_apply(scale=True)
mat_housing = bpy.data.materials.new("HousingMaterial")
mat_housing.use_nodes = True
bsdf = mat_housing.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
bsdf.inputs["Metallic"].default_value = 0.5
housing.data.materials.append(mat_housing)

# Create the three lights (red, yellow, green)
light_positions = [
    (0, 0, 4.1, "Red", (1, 0, 0, 1)),
    (0, 0, 3.5, "Yellow", (1, 1, 0, 1)),
    (0, 0, 2.9, "Green", (0, 1, 0, 1)),
]

for x, y, z, name, color in light_positions:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.1, location=(x, 0.35, z), rotation=(math.pi/2, 0, 0))
    light_obj = bpy.context.active_object
    light_obj.name = f"Light_{name}"
    
    mat = bpy.data.materials.new(f"{name}LightMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Emission Color"].default_value = color
    bsdf.inputs["Emission Strength"].default_value = 2.0
    light_obj.data.materials.append(mat)

# Add a base plate at the bottom of the pole
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
base.name = "Base"
base.data.materials.append(mat_pole)

print("Traffic light created successfully!")
