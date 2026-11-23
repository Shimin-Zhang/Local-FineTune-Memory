import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV Sphere for the bubble
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=128, ring_count=64, location=(0, 0, 0))
bubble = bpy.context.active_object
bubble.name = "SoapBubble"

# Smooth shading
bpy.ops.object.shade_smooth()

# Create a new material
mat = bpy.data.materials.new(name="SoapBubbleMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
# Texture Coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-1200, 0)

# Mapping
mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-1000, 0)

# Noise Texture for slight surface variation (optional, subtle)
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-800, -200)
noise.inputs['Scale'].default_value = 2.0
noise.inputs['Detail'].default_value = 2.0

# Bump Map
bump = nodes.new('ShaderNodeBump')
bump.location = (-600, -200)
bump.inputs['Strength'].default_value = 0.02

# Layer Weight for Fresnel effect
layer_weight = nodes.new('ShaderNodeLayerWeight')
layer_weight.location = (-800, 100)
layer_weight.inputs['Blend'].default_value = 0.5

# ColorRamp for rainbow iridescence
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (-600, 300)
color_ramp.color_ramp.interpolation = 'LINEAR'

# Set rainbow colors in the ColorRamp
cr = color_ramp.color_ramp
cr.elements[0].position = 0.0
cr.elements[0].color = (1.0, 0.0, 0.0, 1.0)   # Red
cr.elements[1].position = 1.0
cr.elements[1].color = (0.0, 0.0, 1.0, 1.0)   # Blue

# Add more color stops for full rainbow
cr.elements.new(0.17).color = (1.0, 0.5, 0.0, 1.0)   # Orange
cr.elements.new(0.33).color = (1.0, 1.0, 0.0, 1.0)   # Yellow
cr.elements.new(0.5).color = (0.0, 1.0, 0.0, 1.0)    # Green
cr.elements.new(0.67).color = (0.0, 0.5, 1.0, 1.0)   # Cyan
cr.elements.new(0.83).color = (0.0, 0.0, 1.0, 1.0)   # Blue
cr.elements.new(1.0).color = (0.5, 0.0, 1.0, 1.0)    # Purple

# Separate XYZ to get a varying input for the rainbow
sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
sep_xyz.location = (-800, 400)

# Math node to create a smooth gradient based on normal
math_node = nodes.new('ShaderNodeMath')
math_node.location = (-400, 300)
math_node.operation = 'MULTIPLY'
math_node.inputs[1].default_value = 0.5

# Add node to offset
add_node = nodes.new('ShaderNodeMath')
add_node.location = (-200, 300)
add_node.operation = 'ADD'
add_node.inputs[1].default_value = 0.5

# Mix Shader for combining glass-like and rainbow effects
mix_shader = nodes.new('ShaderNodeMixShader')
mix_shader.location = (200, 0)

# Principled BSDF for base bubble material
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.location = (0, -200)
principled.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
principled.inputs['Roughness'].default_value = 0.0
principled.inputs['Metallic'].default_value = 0.0
principled.inputs['Transmission Weight'].default_value = 1.0
principled.inputs['IOR'].default_value = 1.33  # Water-like IOR
principled.inputs['Alpha'].default_value = 0.1  # Slight transparency

# Rainbow Emission/Sheen
emission = nodes.new('ShaderNodeEmission')
emission.location = (0, 200)
emission.inputs['Strength'].default_value = 0.3

# Layer Weight output to control mix
layer_weight_out = nodes.new('ShaderNodeLayerWeight')
layer_weight_out.location = (-800, 100)
layer_weight_out.inputs['Blend'].default_value = 0.4

# Connect nodes
# TexCoord -> Mapping
links.new(tex_coord.outputs['Normal'], mapping.inputs['Vector'])

# Mapping -> Noise
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

# Noise -> Bump
links.new(noise.outputs['Fac'], bump.inputs['Height'])

# TexCoord Normal -> Separate XYZ
links.new(tex_coord.outputs['Normal'], sep_xyz.inputs['Vector'])

# Separate XYZ Z -> Math
links.new(sep_xyz.outputs['Z'], math_node.inputs[0])

# Math -> Add
links.new(math_node.outputs['Value'], add_node.inputs[0])

# Add -> ColorRamp
links.new(add_node.outputs['Value'], color_ramp.inputs['Fac'])

# ColorRamp -> Emission Color
links.new(color_ramp.outputs['Color'], emission.inputs['Color'])

# Layer Weight -> Mix Shader Fac
links.new(layer_weight_out.outputs['Fresnel'], mix_shader.inputs['Fac'])

# Emission -> Mix Shader 1
links.new(emission.outputs['Emission'], mix_shader.inputs[1])

# Principled -> Mix Shader 2
links.new(principled.outputs['BSDF'], mix_shader.inputs[2])

# Bump -> Principled Normal
links.new(bump.outputs['Normal'], principled.inputs['Normal'])

# Mix Shader -> Material Output
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (400, 0)
links.new(mix_shader.outputs['Shader'], output.inputs['Surface'])

# Assign material to bubble
bubble.data.materials.append(mat)

# Add a world with a simple environment for reflections
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

for node in world_nodes:
    world_nodes.remove(node)

# Background
bg = world_nodes.new('ShaderNodeBackground')
bg.location = (0, 0)
bg.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)
bg.inputs['Strength'].default_value = 1.0

# Output
world_output = world_nodes.new('ShaderNodeOutputWorld')
world_output.location = (200, 0)
world_links.new(bg.outputs['Background'], world_output.inputs['Surface'])

# Add a light for better visualization
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Set up camera
bpy.ops.object.camera_add(location=(0, -4, 1))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Point camera at bubble
direction = Vector((0, 0, 0)) - camera.location
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
bpy.context.scene.cycles.samples = 256
bpy.context.scene.cycles.use_denoising = True
