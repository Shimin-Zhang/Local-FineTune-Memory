import bpy
import math
import mathutils
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Create the stand ---
# Base cylinder
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.1, location=(0, 0, 0.05))
base = bpy.context.active_object
base.name = "Stand_Base"

# Stand stem
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.3, location=(0, 0, 0.25))
stem = bpy.context.active_object
stem.name = "Stand_Stem"

# Stand top (small platform for crystal ball)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.05, location=(0, 0, 0.425))
top = bpy.context.active_object
top.name = "Stand_Top"

# Bevel the edges of the stand parts
for obj in [base, stem, top]:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.bevel(offset=0.02, segments=3)
    bpy.ops.object.mode_set(mode='OBJECT')

# --- Create the crystal ball ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, segments=64, ring_count=32, location=(0, 0, 0.825))
ball = bpy.context.active_object
ball.name = "Crystal_Ball"
bpy.ops.object.shade_smooth()

# --- Create materials ---

# 1. Crystal ball material (glass)
crystal_mat = bpy.data.materials.new(name="Crystal_Glass")
crystal_mat.use_nodes = True
nodes = crystal_mat.node_tree.nodes
links = crystal_mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Output
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (400, 0)

# Glass BSDF
glass_node = nodes.new('ShaderNodeBsdfGlass')
glass_node.location = (0, 0)
glass_node.inputs['IOR'].default_value = 1.5
glass_node.inputs['Roughness'].default_value = 0.0
glass_node.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)

# Mix with a slight emission for inner glow
emission_node = nodes.new('ShaderNodeEmission')
emission_node.location = (0, -200)
emission_node.inputs['Color'].default_value = (0.3, 0.5, 1.0, 1.0)
emission_node.inputs['Strength'].default_value = 0.1

mix_node = nodes.new('ShaderNodeMixShader')
mix_node.location = (200, 0)
mix_node.inputs['Fac'].default_value = 0.05

links.new(glass_node.outputs['BSDF'], mix_node.inputs[1])
links.new(emission_node.outputs['Emission'], mix_node.inputs[2])
links.new(mix_node.outputs['Shader'], output_node.inputs['Surface'])

ball.data.materials.append(crystal_mat)

# 2. Stand material (dark wood/metal)
stand_mat = bpy.data.materials.new(name="Stand_Material")
stand_mat.use_nodes = True
nodes = stand_mat.node_tree.nodes
links = stand_mat.node_tree.links

for node in nodes:
    nodes.remove(node)

output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (400, 0)

principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.location = (0, 0)
principled.inputs['Base Color'].default_value = (0.15, 0.1, 0.08, 1.0)
principled.inputs['Metallic'].default_value = 0.8
principled.inputs['Roughness'].default_value = 0.3

links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

for obj in [base, stem, top]:
    obj.data.materials.append(stand_mat)

# 3. Swirling mist inside the ball
# Create a particle system or use a mesh with animated texture
# We'll create a small sphere inside with a noise-based emission

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, segments=32, ring_count=16, location=(0, 0, 0.825))
mist_ball = bpy.context.active_object
mist_ball.name = "Mist_Inside"
bpy.ops.object.shade_smooth()

# Mist material with noise
mist_mat = bpy.data.materials.new(name="Swirling_Mist")
mist_mat.use_nodes = True
nodes = mist_mat.node_tree.nodes
links = mist_mat.node_tree.links

for node in nodes:
    nodes.remove(node)

output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (600, 0)

# Emission
emission = nodes.new('ShaderNodeEmission')
emission.location = (400, 0)
emission.inputs['Strength'].default_value = 2.0

# Color ramp for mist colors
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (200, 0)
color_ramp.color_ramp.elements[0].color = (0.2, 0.3, 0.8, 1.0)
color_ramp.color_ramp.elements[1].color = (0.6, 0.4, 1.0, 1.0)

# Noise texture
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (0, 0)
noise.inputs['Scale'].default_value = 3.0
noise.inputs['Detail'].default_value = 8.0
noise.inputs['Roughness'].default_value = 0.5

# Mapping for animation
mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-200, 0)
mapping.inputs['Location'].default_value = (0, 0, 0)

# Texture coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-400, 0)

links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(color_ramp.outputs['Color'], emission.inputs['Color'])
links.new(emission.outputs['Emission'], output_node.inputs['Surface'])

mist_ball.data.materials.append(mist_mat)

# Make mist ball slightly transparent
mist_mat.blend_method = 'BLEND'
mist_mat.show_transparent_back = False

# --- Animate the mist swirling ---
# Animate the mapping location to create swirl effect
mist_ball.animation_data_create()
frame = 1
for i in range(250):
    angle = i * 0.05
    x = math.sin(angle) * 0.5
    y = math.cos(angle) * 0.5
    z = math.sin(angle * 0.7) * 0.3
    mist_ball.keyframe_insert(data_path="location", frame=frame)
    frame += 1

# Animate the noise scale for dynamic effect
noise.inputs['Scale'].default_value = 3.0
mist_ball.animation_data_clear()

# Better: animate the mapping node
mist_ball.animation_data_create()
frame = 1
for i in range(250):
    angle = i * 0.05
    x = math.sin(angle) * 0.5
    y = math.cos(angle) * 0.5
    z = math.sin(angle * 0.7) * 0.3
    mist_ball.keyframe_insert(data_path="location", frame=frame)
    frame += 1

# Set frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 250

# --- Add lighting ---
# Key light
bpy.ops.object.light_add(type='POINT', location=(1.5, 1.5, 2))
key_light = bpy.context.active_object
key_light.data.energy = 100
key_light.data.color = (1.0, 0.95, 0.9)

# Fill light
bpy.ops.object.light_add(type='POINT', location=(-1.5, -1.5, 1.5))
fill_light = bpy.context.active_object
fill_light.data.energy = 50
fill_light.data.color = (0.8, 0.85, 1.0)

# Rim light
bpy.ops.object.light_add(type='POINT', location=(0, -2, 1))
rim_light = bpy.context.active_object
rim_light.data.energy = 80
rim_light.data.color = (0.5, 0.7, 1.0)

# --- Camera ---
bpy.ops.object.camera_add(location=(0, -2.5, 1.2))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at crystal ball
direction = Vector((0, 0, 0.825)) - camera.location
rotation_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rotation_quat.to_euler()

bpy.context.scene.camera = camera

# --- World settings ---
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.05, 1.0)
    bg_node.inputs['Strength'].default_value = 1.0

print("Crystal ball with swirling mist on a stand created successfully!")
