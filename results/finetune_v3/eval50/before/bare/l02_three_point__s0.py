import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new collection for organization
collection = bpy.data.collections.new("Statue Scene")
bpy.context.scene.collection.children.link(collection)

def link_to_collection(obj):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    collection.objects.link(obj)

# --- Materials ---
# White marble-like material
marble_mat = bpy.data.materials.new("White Marble")
marble_mat.use_nodes = True
nodes = marble_mat.node_tree.nodes
links = marble_mat.node_tree.links
nodes.clear()

bsdf = nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Base Color"].default_value = (0.95, 0.95, 0.95, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Specular IOR Level"].default_value = 0.5
output = nodes.new("ShaderNodeOutputMaterial")
links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

# Dark pedestal material
pedestal_mat = bpy.data.materials.new("Dark Stone")
pedestal_mat.use_nodes = True
nodes_p = pedestal_mat.node_tree.nodes
links_p = pedestal_mat.node_tree.links
nodes_p.clear()
bsdf_p = nodes_p.new("ShaderNodeBsdfPrincipled")
bsdf_p.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
bsdf_p.inputs["Roughness"].default_value = 0.7
output_p = nodes_p.new("ShaderNodeOutputMaterial")
links_p.new(bsdf_p.outputs["BSDF"], output_p.inputs["Surface"])

# --- Pedestal ---
# Base box
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.25))
base = bpy.context.active_object
base.scale = (1.5, 1.5, 0.5)
base.data.materials.append(pedestal_mat)
link_to_collection(base)

# Pedestal column
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.0))
column = bpy.context.active_object
column.scale = (1.0, 1.0, 1.5)
column.data.materials.append(pedestal_mat)
link_to_collection(column)

# Top plate
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.75))
top_plate = bpy.context.active_object
top_plate.scale = (1.3, 1.3, 0.1)
top_plate.data.materials.append(pedestal_mat)
link_to_collection(top_plate)

# --- Statue (simple shapes) ---
statue_base_y = 1.8  # start of statue

# Torso (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.0, location=(0, 0, statue_base_y + 0.5))
torso = bpy.context.active_object
torso.data.materials.append(marble_mat)
link_to_collection(torso)

# Head (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0, 0, statue_base_y + 1.3))
head = bpy.context.active_object
head.data.materials.append(marble_mat)
link_to_collection(head)

# Left arm (cylinder, angled)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.8, location=(-0.45, 0, statue_base_y + 0.7))
left_arm = bpy.context.active_object
left_arm.rotation_euler = (0, math.radians(20), 0)
left_arm.data.materials.append(marble_mat)
link_to_collection(left_arm)

# Right arm (cylinder, angled)
bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.8, location=(0.45, 0, statue_base_y + 0.7))
right_arm = bpy.context.active_object
right_arm.rotation_euler = (0, math.radians(-20), 0)
right_arm.data.materials.append(marble_mat)
link_to_collection(right_arm)

# Left leg (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.9, location=(-0.2, 0, statue_base_y - 0.15))
left_leg = bpy.context.active_object
left_leg.data.materials.append(marble_mat)
link_to_collection(left_leg)

# Right leg (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.9, location=(0.2, 0, statue_base_y - 0.15))
right_leg = bpy.context.active_object
right_leg.data.materials.append(marble_mat)
link_to_collection(right_leg)

# --- Three-Point Lighting ---
# Key light (main light, bright, from front-left)
key_data = bpy.data.lights.new("Key Light", type='AREA')
key_data.energy = 500
key_data.size = 2.0
key_data.color = (1.0, 1.0, 0.95)  # slightly warm
key_obj = bpy.data.objects.new("Key Light", key_data)
key_obj.location = (-3, -3, 3)
key_obj.rotation_euler = (math.radians(60), 0, math.radians(-45))
bpy.context.scene.collection.objects.link(key_obj)

# Fill light (softer, from front-right)
fill_data = bpy.data.lights.new("Fill Light", type='AREA')
fill_data.energy = 200
fill_data.size = 3.0
fill_data.color = (0.9, 0.95, 1.0)  # slightly cool
fill_obj = bpy.data.objects.new("Fill Light", fill_data)
fill_obj.location = (3, -3, 2.5)
fill_obj.rotation_euler = (math.radians(60), 0, math.radians(45))
bpy.context.scene.collection.objects.link(fill_obj)

# Rim/Back light (from behind, creates edge highlight)
rim_data = bpy.data.lights.new("Rim Light", type='SPOT')
rim_data.energy = 800
rim_data.spot_size = math.radians(60)
rim_data.spot_blend = 0.5
rim_data.color = (1.0, 0.95, 0.9)  # warm rim
rim_obj = bpy.data.objects.new("Rim Light", rim_data)
rim_obj.location = (0, 4, 3.5)
rim_obj.rotation_euler = (math.radians(-60), 0, 0)
bpy.context.scene.collection.objects.link(rim_obj)

# --- Ground plane ---
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new("Ground")
ground_mat.use_nodes = True
nodes_g = ground_mat.node_tree.nodes
links_g = ground_mat.node_tree.links
nodes_g.clear()
bsdf_g = nodes_g.new("ShaderNodeBsdfPrincipled")
bsdf_g.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1.0)
bsdf_g.inputs["Roughness"].default_value = 0.9
output_g = nodes_g.new("ShaderNodeOutputMaterial")
links_g.new(bsdf_g.outputs["BSDF"], output_g.inputs["Surface"])
ground.data.materials.append(ground_mat)
link_to_collection(ground)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_obj = bpy.data.objects.new("Camera", cam_data)
cam_obj.location = (0, -5, 2.5)
cam_obj.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Set world to dark for drama
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.01, 0.01, 0.01, 1.0)
    bg.inputs["Strength"].default_value = 0.5
