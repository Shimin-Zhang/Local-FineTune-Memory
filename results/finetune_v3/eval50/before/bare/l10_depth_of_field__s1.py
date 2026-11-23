import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a simple chess king using primitives
# Base
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.15, location=(0, 0, 0.075))
base = bpy.context.active_object
base.name = "King_Base"

# Stem
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.8, location=(0, 0, 0.55))
stem = bpy.context.active_object
stem.name = "King_Stem"

# Cross / top ornament
bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.08, location=(0, 0, 1.0))
cross_base = bpy.context.active_object
cross_base.name = "King_Cross_Base"

# Vertical cross bar
bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0, 0, 1.15))
v_bar = bpy.context.active_object
v_bar.name = "King_Vertical_Bar"
v_bar.scale = (1, 1, 2)

# Horizontal cross bar
bpy.ops.mesh.primitive_cube_add(size=0.08, location=(0, 0, 1.15))
h_bar = bpy.context.active_object
h_bar.name = "King_Horizontal_Bar"
h_bar.scale = (3, 1, 1)

# Crown / top sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0, 1.35))
crown = bpy.context.active_object
crown.name = "King_Crown"

# Apply smooth shading to all king parts
for obj in [base, stem, cross_base, v_bar, h_bar, crown]:
    bpy.ops.object.shade_smooth()

# Create a floor/background plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"

# Create a simple material for the king (ivory/white)
king_mat = bpy.data.materials.new(name="King_Ivory")
king_mat.use_nodes = True
bsdf = king_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.95, 0.92, 0.85, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
bsdf.inputs["Metallic"].default_value = 0.0

# Apply material to all king parts
for obj in [base, stem, cross_base, v_bar, h_bar, crown]:
    obj.data.materials.clear()
    obj.data.materials.append(king_mat)

# Floor material
floor_mat = bpy.data.materials.new(name="Floor_Material")
floor_mat.use_nodes = True
bsdf_floor = floor_mat.node_tree.nodes["Principled BSDF"]
bsdf_floor.inputs["Base Color"].default_value = (0.2, 0.15, 0.1, 1.0)
bsdf_floor.inputs["Roughness"].default_value = 0.5
floor.data.materials.clear()
floor.data.materials.append(floor_mat)

# Add some background objects to create depth (blurred in background)
# A few random shapes in the background
import random
random.seed(42)
for i in range(10):
    x = random.uniform(-5, 5)
    y = random.uniform(-8, -3)  # Behind the king
    z = random.uniform(0.5, 3)
    size = random.uniform(0.2, 0.8)
    bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, z))
    bg_obj = bpy.context.active_object
    bg_obj.name = f"BG_Object_{i}"
    # Random rotation
    bg_obj.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    # Random color
    mat = bpy.data.materials.new(name=f"BG_Mat_{i}")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (random.uniform(0.1, 0.6), random.uniform(0.1, 0.6), random.uniform(0.1, 0.6), 1.0)
    b.inputs["Roughness"].default_value = 0.7
    bg_obj.data.materials.clear()
    bg_obj.data.materials.append(mat)

# Set up camera
bpy.ops.object.camera_add(location=(0.8, -1.5, 1.2))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Point camera at the king
import mathutils
target = mathutils.Vector((0, 0, 0.8))
direction = target - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set up DOF (Depth of Field)
camera.data.dof.use_dof = True
camera.data.dof.focus_distance = camera.location.distance_to(target)
camera.data.dof.aperture_fstop = 1.8  # Shallow depth of field

# Camera settings for close-up
camera.data.lens = 85  # Telephoto lens for close-up with nice background compression
camera.data.sensor_width = 36
camera.data.sensor_height = 24

# Set up lighting
# Key light
bpy.ops.object.light_add(type='AREA', location=(2, -2, 3))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 200
key_light.data.size = 2
key_light.rotation_euler = (math.radians(45), 0, math.radians(45))

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-2, -1, 2))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 80
fill_light.data.size = 3
fill_light.rotation_euler = (math.radians(50), 0, math.radians(-45))

# Rim light
bpy.ops.object.light_add(type='AREA', location=(0, 2, 2.5))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 150
rim_light.data.size = 1
rim_light.rotation_euler = (math.radians(-30), 0, 0)

# World settings
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (0.05, 0.05, 0.08, 1.0)
bg_node.inputs[1].default_value = 1.0

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100

# Set output
scene.render.filepath = "//chess_king_closeup.png"
scene.render.image_settings.file_format = 'PNG'

print("Scene set up with chess king, shallow DOF, and blurred background.")
