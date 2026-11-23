import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create materials
def create_material(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.8
    return mat

mat_red = create_material("RedRoof", (0.8, 0.1, 0.1, 1.0))
mat_brown = create_material("BrownDoor", (0.35, 0.2, 0.1, 1.0))
mat_wall = create_material("Wall", (0.9, 0.85, 0.75, 1.0))
mat_window = create_material("Window", (0.7, 0.85, 0.95, 1.0))

# House body (cube)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1))
house = bpy.context.active_object
house.name = "HouseBody"
bpy.ops.object.transform_apply(scale=True)
house.scale = (3, 2, 2)
bpy.ops.object.transform_apply(scale=True)
house.data.materials.append(mat_wall)

# Roof (pyramid using a cone with 4 vertices)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=2.6, radius2=0, depth=1.5, location=(0, 0, 3.25))
roof = bpy.context.active_object
roof.name = "Roof"
roof.rotation_euler = (0, 0, math.radians(45))
bpy.ops.object.transform_apply(rotation=True)
roof.data.materials.append(mat_red)

# Door
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -1.01, 0.6))
door = bpy.context.active_object
door.name = "Door"
door.scale = (0.4, 0.05, 0.6)
bpy.ops.object.transform_apply(scale=True)
door.data.materials.append(mat_brown)

# Window 1 (left side of front face)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-1.0, -1.01, 1.3))
win1 = bpy.context.active_object
win1.name = "Window1"
win1.scale = (0.4, 0.05, 0.4)
bpy.ops.object.transform_apply(scale=True)
win1.data.materials.append(mat_window)

# Window 2 (right side of front face)
bpy.ops.mesh.primitive_cube_add(size=1, location=(1.0, -1.01, 1.3))
win2 = bpy.context.active_object
win2.name = "Window2"
win2.scale = (0.4, 0.05, 0.4)
bpy.ops.object.transform_apply(scale=True)
win2.data.materials.append(mat_window)

# Add a simple light and camera for context
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

bpy.ops.object.camera_add(location=(0, -8, 3))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.camera = cam

# Set viewport to show the house
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'MATERIAL'
