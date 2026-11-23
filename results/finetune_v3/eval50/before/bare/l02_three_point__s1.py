import bpy
import math
import mathutils

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create Pedestal ---
bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.5, location=(0, 0, 0.25))
pedestal = bpy.context.active_object
pedestal.name = "Pedestal"

# --- Create Statue (Simple Shapes) ---
# Base of statue (small cylinder on top of pedestal)
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.2, location=(0, 0, 0.6))
statue_base = bpy.context.active_object
statue_base.name = "Statue_Base"

# Body (cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=1.0, location=(0, 0, 1.2))
body = bpy.context.active_object
body.name = "Statue_Body"

# Head (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, 1.95))
head = bpy.context.active_object
head.name = "Statue_Head"

# Arms (cylinders)
# Left arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=(-0.35, 0, 1.3))
left_arm = bpy.context.active_object
left_arm.name = "Statue_Left_Arm"
left_arm.rotation_euler = (0, math.radians(30), 0)

# Right arm
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.8, location=(0.35, 0, 1.3))
right_arm = bpy.context.active_object
right_arm.name = "Statue_Right_Arm"
right_arm.rotation_euler = (0, math.radians(-30), 0)

# --- Apply White Material to Statue ---
white_mat = bpy.data.materials.new(name="White_Statue")
white_mat.use_nodes = True
bsdf = white_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Metallic"].default_value = 0.0

# Apply white material to all statue parts
for obj in [statue_base, body, head, left_arm, right_arm]:
    obj.data.materials.clear()
    obj.data.materials.append(white_mat)

# --- Create Ground ---
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

ground_mat = bpy.data.materials.new(name="Ground_Mat")
ground_mat.use_nodes = True
bsdf_g = ground_mat.node_tree.nodes.get("Principled BSDF")
bsdf_g.inputs["Base Color"].default_value = (0.2, 0.2, 0.2, 1.0)
bsdf_g.inputs["Roughness"].default_value = 0.8
ground.data.materials.append(ground_mat)

# --- Three-Point Lighting ---

# Key Light (main light, bright, from front-left)
bpy.ops.object.light_add(type='AREA', location=(-3, -3, 4))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 500
key_light.data.size = 2.0
key_light.rotation_euler = (math.radians(45), 0, math.radians(-45))

# Fill Light (softer, from front-right)
bpy.ops.object.light_add(type='AREA', location=(3, -3, 3))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 150
fill_light.data.size = 3.0
fill_light.rotation_euler = (math.radians(45), 0, math.radians(45))

# Back/Rim Light (from behind, creates dramatic edge)
bpy.ops.object.light_add(type='AREA', location=(0, 4, 3))
back_light = bpy.context.active_object
back_light.name = "Back_Light"
back_light.data.energy = 300
back_light.data.size = 1.5
back_light.rotation_euler = (math.radians(-30), 0, math.radians(180))

# --- Set up Camera ---
bpy.ops.object.camera_add(location=(0, -5, 2))
camera = bpy.context.active_object
camera.name = "Camera"
# Point camera at statue
direction = mathutils.Vector((0, 0, 1.2)) - camera.location
camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
bpy.context.scene.camera = camera

# --- Set Render Settings for Dramatic Look ---
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Set world to dark for drama
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world_node_tree = world.node_tree
bg_node = world_node_tree.nodes.get("Background")
bg_node.inputs[0].default_value = (0.02, 0.02, 0.02, 1.0)  # Very dark background
bg_node.inputs[1].default_value = 1.0

# Enable shadows and set render engine
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
