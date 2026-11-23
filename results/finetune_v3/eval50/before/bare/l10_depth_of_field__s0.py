import bpy
import math
import random

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a chess king
# Base
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
base.name = "King_Base"

# Stem
bpy.ops.mesh.primitive_cone_add(radius1=0.4, radius2=0.25, depth=0.8, location=(0, 0, 0.5))
stem = bpy.context.active_object
stem.name = "King_Stem"

# Body
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.6, location=(0, 0, 1.1))
body = bpy.context.active_object
body.name = "King_Body"

# Cross
# Vertical bar
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0, 1.65))
vbar = bpy.context.active_object
vbar.name = "King_Cross_Vertical"
vbar.scale = (1, 1, 2.5)

# Horizontal bar
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(0, 0, 1.65))
hbar = bpy.context.active_object
hbar.name = "King_Cross_Horizontal"
hbar.scale = (2.5, 1, 1)

# Top sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(0, 0, 1.85), segments=32, ring_count=16)
top = bpy.context.active_object
top.name = "King_Top"

# Apply materials
# Gold material
gold_mat = bpy.data.materials.new(name="Gold")
gold_mat.use_nodes = True
bsdf = gold_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 0.85, 0.3, 1.0)
bsdf.inputs["Metallic"].default_value = 1.0
bsdf.inputs["Roughness"].default_value = 0.2

# Apply gold to all king parts
for obj in [base, stem, body, vbar, hbar, top]:
    obj.data.materials.append(gold_mat)

# Create background plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
bg_plane = bpy.context.active_object
bg_plane.name = "Background"

# Background material - dark wood
wood_mat = bpy.data.materials.new(name="Wood")
wood_mat.use_nodes = True
bsdf_bg = wood_mat.node_tree.nodes["Principled BSDF"]
bsdf_bg.inputs["Base Color"].default_value = (0.2, 0.1, 0.05, 1.0)
bsdf_bg.inputs["Roughness"].default_value = 0.6
bg_plane.data.materials.append(wood_mat)

# Add some background objects to blur (chess pieces or shapes)
random.seed(42)
for i in range(8):
    x = random.uniform(-3, 3)
    y = random.uniform(2, 6)
    z = 0.3
    size = random.uniform(0.2, 0.4)
    
    # Random shape: cylinder or cube
    if random.random() > 0.5:
        bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=size*2, location=(x, y, z + size))
    else:
        bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, z + size/2))
    
    bg_obj = bpy.context.active_object
    bg_obj.name = f"BG_Object_{i}"
    
    # Random dark material
    mat = bpy.data.materials.new(name=f"BG_Mat_{i}")
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (random.uniform(0.1, 0.3), random.uniform(0.05, 0.2), random.uniform(0.05, 0.15), 1.0)
    b.inputs["Roughness"].default_value = 0.7
    bg_obj.data.materials.append(mat)

# Set up camera
bpy.ops.object.camera_add(location=(0, -2.5, 1.2), rotation=(math.radians(85), 0, 0))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Set camera to close-up
camera.data.lens = 85  # Telephoto for close-up
camera.data.sensor_width = 36

# Enable depth of field
camera.data.dof.use_dof = True
camera.data.dof.focus_object = body  # Focus on the king's body
camera.data.dof.aperture_fstop = 1.8  # Very shallow depth of field

# Set up lighting
# Key light
bpy.ops.object.light_add(type='AREA', location=(2, -2, 3))
key_light = bpy.context.active_object
key_light.name = "Key_Light"
key_light.data.energy = 200
key_light.data.size = 2
key_light.rotation_euler = (math.radians(45), math.radians(30), 0)

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-2, -2, 2))
fill_light = bpy.context.active_object
fill_light.name = "Fill_Light"
fill_light.data.energy = 80
fill_light.data.size = 3
fill_light.rotation_euler = (math.radians(60), math.radians(-30), 0)

# Rim light
bpy.ops.object.light_add(type='AREA', location=(0, 2, 3))
rim_light = bpy.context.active_object
rim_light.name = "Rim_Light"
rim_light.data.energy = 150
rim_light.data.size = 1
rim_light.rotation_euler = (math.radians(-45), 0, 0)

# World settings
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
    bg_node.inputs[1].default_value = 1.0

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100

# Set film transparency off
bpy.context.scene.render.film_transparent = False

print("Chess king close-up scene with shallow depth of field is ready.")
