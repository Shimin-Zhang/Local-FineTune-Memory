import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a simple chess king using cylinders and spheres
# Base
base = bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.3, location=(0, 0, 0.15))
base_obj = bpy.context.object
base_obj.name = "King_Base"

# Stem
stem = bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.2, location=(0, 0, 0.9))
stem_obj = bpy.context.object
stem_obj.name = "King_Stem"

# Cross bar
crossbar = bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.2, location=(0, 0, 1.5))
crossbar_obj = bpy.context.object
crossbar_obj.name = "King_Crossbar"

# Top sphere (crown tip)
tip = bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0, 0, 1.75))
tip_obj = bpy.context.object
tip_obj.name = "King_Tip"

# Add a crown-like ring
crown = bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.1, location=(0, 0, 1.6))
crown_obj = bpy.context.object
crown_obj.name = "King_Crown"

# Material for the king (white/ivory)
king_mat = bpy.data.materials.new(name="King_Material")
king_mat.use_nodes = True
bsdf = king_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.95, 0.93, 0.88, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Metallic"].default_value = 0.1

# Apply material to all king parts
for obj in [base_obj, stem_obj, crossbar_obj, tip_obj, crown_obj]:
    obj.data.materials.append(king_mat)

# Create a background plane
bg_plane = bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
bg_obj = bpy.context.object
bg_obj.name = "Background"

# Background material (dark wood-like)
bg_mat = bpy.data.materials.new(name="Background_Material")
bg_mat.use_nodes = True
bg_bsdf = bg_mat.node_tree.nodes["Principled BSDF"]
bg_bsdf.inputs["Base Color"].default_value = (0.15, 0.08, 0.04, 1.0)
bg_bsdf.inputs["Roughness"].default_value = 0.8
bg_obj.data.materials.append(bg_mat)

# Add some background objects for bokeh interest (chess pieces silhouettes)
for i in range(5):
    x = (i - 2) * 2.5
    y = -5 - (i % 2) * 1.5
    piece = bpy.ops.mesh.primitive_cone_add(radius1=0.3, radius2=0.1, depth=1.5, location=(x, y, 0.75))
    piece_obj = bpy.context.object
    piece_obj.name = f"Bg_Piece_{i}"
    piece_obj.data.materials.append(bg_mat)

# Set up camera
cam_data = bpy.data.cameras.new(name="Camera")
cam_data.lens = 85  # Portrait lens for close-up
cam_data.dof.use_dof = True
cam_data.dof.aperture_fstop = 1.8  # Shallow depth of field
cam_data.dof.focus_distance = 2.0  # Focus on the king

cam_obj = bpy.data.objects.new(name="Camera", object_data=cam_data)
bpy.context.collection.objects.link(cam_obj)

# Position camera for close-up of the king
cam_obj.location = (0, -2.5, 1.5)
cam_obj.rotation_euler = (math.radians(85), 0, 0)

# Set camera as active
bpy.context.scene.camera = cam_obj

# Lighting
# Key light
key_light_data = bpy.data.lights.new(name="Key_Light", type='AREA')
key_light_data.energy = 100
key_light_data.size = 2
key_light_obj = bpy.data.objects.new(name="Key_Light", object_data=key_light_data)
bpy.context.collection.objects.link(key_light_obj)
key_light_obj.location = (2, -2, 3)
key_light_obj.rotation_euler = (math.radians(45), math.radians(30), 0)

# Fill light
fill_light_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
fill_light_data.energy = 30
fill_light_data.size = 3
fill_light_obj = bpy.data.objects.new(name="Fill_Light", object_data=fill_light_data)
bpy.context.collection.objects.link(fill_light_obj)
fill_light_obj.location = (-2, -1, 2)
fill_light_obj.rotation_euler = (math.radians(60), math.radians(-20), 0)

# Rim light
rim_light_data = bpy.data.lights.new(name="Rim_Light", type='SPOT')
rim_light_data.energy = 50
rim_light_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_light_data)
bpy.context.collection.objects.link(rim_light_obj)
rim_light_obj.location = (0, 2, 3)
rim_light_obj.rotation_euler = (math.radians(90), 0, 0)

# World settings
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world_node = world.node_tree.nodes["Background"]
world_node.inputs[0].default_value = (0.05, 0.03, 0.02, 1.0)
world_node.inputs[1].default_value = 0.5

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True

# Set output path
bpy.context.scene.render.filepath = "/tmp/chess_king_closeup.png"
bpy.context.scene.render.image_settings.file_format = 'PNG'

# Render
bpy.ops.render.render(write_still=True)
