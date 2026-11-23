import bpy
import math

# Remove default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV Sphere for the bubble
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32, location=(0, 0, 0))
bubble = bpy.context.active_object
bubble.name = "SoapBubble"

# Subdivide for smoother appearance
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=2)
bpy.ops.object.mode_set(mode='OBJECT')

# Smooth shading
bpy.ops.object.shade_smooth()

# Create a new material for the soap bubble
mat = bpy.data.materials.new(name="SoapBubbleMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Add nodes
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (600, 0)

# Principled BSDF for the bubble
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (300, 0)

# Set basic properties
bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.0
bsdf.inputs['IOR'].default_value = 1.33  # Water-like IOR
bsdf.inputs['Transmission Weight'].default_value = 1.0
bsdf.inputs['Alpha'].default_value = 0.15  # Slight transparency

# Create rainbow sheen using a ColorRamp driven by the normal vector
# Use the Normal to create an iridescent effect
normal_node = nodes.new('ShaderNodeNewGeometry')
normal_node.location = (-400, 200)

# Separate XYZ to get the Z component of the normal (or use a combination)
sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
sep_xyz.location = (-200, 200)

links.new(normal_node.outputs['Normal'], sep_xyz.inputs['Vector'])

# Combine X and Y normals for a more interesting pattern
math_add = nodes.new('ShaderNodeMath')
math_add.operation = 'ADD'
math_add.location = (0, 300)
links.new(sep_xyz.outputs['X'], math_add.inputs[0])
links.new(sep_xyz.outputs['Y'], math_add.inputs[1])

# Scale the combined value
math_mul = nodes.new('ShaderNodeMath')
math_mul.operation = 'MULTIPLY'
math_mul.location = (150, 300)
math_mul.inputs[1].default_value = 3.0
links.new(math_add.outputs['Value'], math_mul.inputs[0])

# Add Z component for more variation
math_add2 = nodes.new('ShaderNodeMath')
math_add2.operation = 'ADD'
math_add2.location = (300, 300)
links.new(math_mul.outputs['Value'], math_add2.inputs[0])
links.new(sep_xyz.outputs['Z'], math_add2.inputs[1])

# Map to 0-1 range for the color ramp
map_range = nodes.new('ShaderNodeMapRange')
map_range.location = (450, 300)
map_range.inputs['From Min'].default_value = -1.0
map_range.inputs['From Max'].default_value = 1.0
map_range.inputs['To Min'].default_value = 0.0
map_range.inputs['To Max'].default_value = 1.0
links.new(math_add2.outputs['Value'], map_range.inputs['Value'])

# ColorRamp for rainbow effect
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (600, 300)

# Set rainbow colors
ramp = color_ramp.color_ramp
ramp.interpolation = 'LINEAR'

# Remove default elements and add rainbow stops
while len(ramp.elements) > 0:
    ramp.elements.remove(ramp.elements[0])

# Add rainbow color stops
rainbow_colors = [
    (0.0, (0.5, 0.0, 0.0, 1.0)),   # Red
    (0.17, (1.0, 0.0, 0.0, 1.0)),   # Red
    (0.33, (1.0, 0.5, 0.0, 1.0)),   # Orange
    (0.5, (1.0, 1.0, 0.0, 1.0)),    # Yellow
    (0.67, (0.0, 1.0, 0.0, 1.0)),   # Green
    (0.83, (0.0, 0.0, 1.0, 1.0)),   # Blue
    (1.0, (0.5, 0.0, 1.0, 1.0)),    # Violet
]

for pos, color in rainbow_colors:
    elem = ramp.elements.new(pos)
    elem.color = color

links.new(map_range.outputs['Result'], color_ramp.inputs['Fac'])

# Mix the rainbow with the base color using a MixRGB
mix_rgb = nodes.new('ShaderNodeMixRGB')
mix_rgb.blend_type = 'MIX'
mix_rgb.location = (800, 100)
mix_rgb.inputs['Fac'].default_value = 0.4  # Blend amount
links.new(color_ramp.outputs['Color'], mix_rgb.inputs['Color2'])
mix_rgb.inputs['Color1'].default_value = (0.9, 0.95, 1.0, 1.0)  # Slight blue-white base

links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])

# Add a slight emission for the sheen
emission_node = nodes.new('ShaderNodeEmission')
emission_node.location = (800, -200)
links.new(color_ramp.outputs['Color'], emission_node.inputs['Color'])
emission_node.inputs['Strength'].default_value = 0.3

# Mix BSDF with emission
mix_shader = nodes.new('ShaderNodeMixShader')
mix_shader.location = (1000, 0)
mix_shader.inputs['Fac'].default_value = 0.2
links.new(bsdf.outputs['BSDF'], mix_shader.inputs[1])
links.new(emission_node.outputs['Emission'], mix_shader.inputs[2])
links.new(mix_shader.outputs['Shader'], output_node.inputs['Surface'])

# Assign material to the bubble
bubble.data.materials.append(mat)

# Add a light for better visualization
bpy.ops.object.light_add(type='SUN', location=(5, 5, 5))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a world background
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links
bg_node = world_nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)
    bg_node.inputs['Strength'].default_value = 0.5

# Set up camera
bpy.ops.object.camera_add(location=(0, -4, 0))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
