import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
# Wood material
wood_mat = bpy.data.materials.new("Wood")
wood_mat.use_nodes = True
nodes = wood_mat.node_tree.nodes
links = wood_mat.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.35, 0.2, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6

# Green material for the vase
green_mat = bpy.data.materials.new("Green")
green_mat.use_nodes = True
nodes_g = green_mat.node_tree.nodes
bsdf_g = nodes_g["Principled BSDF"]
bsdf_g.inputs["Base Color"].default_value = (0.0, 0.5, 0.0, 1.0)
bsdf_g.inputs["Roughness"].default_value = 0.3
bsdf_g.inputs["Metallic"].default_value = 0.0

# --- Table Top ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
table_top = bpy.context.active_object
table_top.name = "TableTop"
table_top.scale = (1.5, 1.0, 0.05)  # 3m x 2m x 0.1m
table_top.data.materials.append(wood_mat)

# --- Four Legs ---
leg_positions = [
    (-1.35, -0.85, 0.5),
    (1.35, -0.85, 0.5),
    (-1.35, 0.85, 0.5),
    (1.35, 0.85, 0.5),
]

for i, pos in enumerate(leg_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    leg = bpy.context.active_object
    leg.name = f"Leg_{i+1}"
    leg.scale = (0.08, 0.08, 0.5)  # 0.16m x 0.16m x 1.0m
    leg.data.materials.append(wood_mat)

# --- Green Vase ---
# Create a vase using a cylinder and scaling
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.15, depth=0.4, location=(0, 0, 1.25))
vase = bpy.context.active_object
vase.name = "Vase"
vase.data.materials.append(green_mat)

# Make it look more like a vase: scale top wider
# We can edit the mesh to taper the top
import bmesh
bm = bmesh.new()
bm.from_mesh(vase.data)

# Find top vertices (z > 0) and scale them outward
for vert in bm.verts:
    if vert.co.z > 0:
        vert.co.x *= 1.5
        vert.co.y *= 1.5

bm.to_mesh(vase.data)
bm.free()

# Add a slight bevel for aesthetics
bpy.ops.object.select_all(action='DESELECT')
vase.select_set(True)
bpy.context.view_layer.objects.active = vase
bpy.ops.object.shade_smooth()

# --- Lighting ---
# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.8, 0.8, 0.8, 1.0)
    bg_node.inputs[1].default_value = 1.0

# Camera setup
bpy.ops.object.camera_add(location=(4, 4, 3))
camera = bpy.context.active_object
camera.name = "Camera"
# Point camera at the table
direction = (0, 0, 1) - camera.location
camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

bpy.context.scene.camera = camera

print("Wooden table with four legs and a green vase has been created.")
