import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove default objects
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)

# --- Create the table top ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
table_top = bpy.context.active_object
table_top.name = "TableTop"
table_top.scale = (1.5, 1.0, 0.05)  # 3m x 2m x 0.1m
bpy.ops.object.transform_apply(scale=True)

# --- Create the four legs ---
leg_positions = [
    (-1.2, -0.8, 0.5),
    (1.2, -0.8, 0.5),
    (-1.2, 0.8, 0.5),
    (1.2, 0.8, 0.5),
]

for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    leg.scale = (0.08, 0.08, 0.5)  # 0.16m x 0.16m x 1.0m
    bpy.ops.object.transform_apply(scale=True)

# --- Create the green vase ---
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.4, location=(0, 0, 1.3))
vase = bpy.context.active_object
vase.name = "Vase"
bpy.ops.object.transform_apply(scale=True)

# Make the vase slightly tapered by editing its vertices
# We'll use a cone instead for a nicer vase shape
bpy.data.objects.remove(vase, do_unlink=True)

bpy.ops.mesh.primitive_cone_add(radius1=0.15, radius2=0.08, depth=0.4, location=(0, 0, 1.3))
vase = bpy.context.active_object
vase.name = "Vase"
bpy.ops.object.transform_apply(scale=True)

# --- Add materials ---

# Wood material for the table
wood_mat = bpy.data.materials.new(name="WoodMaterial")
wood_mat.use_nodes = True
nodes = wood_mat.node_tree.nodes
links = wood_mat.node_tree.links

# Set up wood color
diffuse = nodes.get("Principled BSDF")
if diffuse:
    diffuse.inputs["Base Color"].default_value = (0.35, 0.18, 0.08, 1.0)  # Brown wood
    diffuse.inputs["Roughness"].default_value = 0.6

# Apply wood material to table top and legs
table_top.data.materials.append(wood_mat)
for i in range(4):
    leg = bpy.data.objects.get(f"Leg_{i+1}")
    if leg:
        leg.data.materials.append(wood_mat)

# Green material for the vase
green_mat = bpy.data.materials.new(name="GreenVaseMaterial")
green_mat.use_nodes = True
nodes = green_mat.node_tree.nodes
links = green_mat.node_tree.links

diffuse = nodes.get("Principled BSDF")
if diffuse:
    diffuse.inputs["Base Color"].default_value = (0.1, 0.5, 0.1, 1.0)  # Green
    diffuse.inputs["Roughness"].default_value = 0.3
    diffuse.inputs["Metallic"].default_value = 0.1

vase.data.materials.append(green_mat)

# --- Add a light for better visualization ---
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# --- Add a camera ---
bpy.ops.object.camera_add(location=(4, 4, 3))
camera = bpy.context.active_object
camera.name = "Camera"
# Point camera at the table
direction = (0, 0, 1.0) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Set the camera as active
bpy.context.scene.camera = camera

print("Wooden table with four legs and a green vase created successfully.")
