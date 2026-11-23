import bpy
import math
import random
from mathutils import Vector

# Clear default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the main boulder
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0, location=(0, 0, 0))
boulder = bpy.context.active_object
boulder.name = "MossBoulder"

# Displace the boulder to make it look natural
# Add a Displace modifier with a noise texture
noise_tex = bpy.data.textures.new(name="BoulderNoise", type='CLOUDS')
noise_tex.noise_scale = 0.4
noise_tex.noise_depth = 3

displace_mod = boulder.modifiers.new(name="Displace", type='DISPLACE')
displace_mod.texture = noise_tex
displace_mod.strength = 0.3
displace_mid_level = 0.5

# Apply the modifier
bpy.context.view_layer.objects.active = boulder
bpy.ops.object.modifier_apply(modifier="Displace")

# Add more displacement for larger features
noise_tex2 = bpy.data.textures.new(name="BoulderNoise2", type='CLOUDS')
noise_tex2.noise_scale = 1.2
noise_tex2.noise_depth = 2

displace_mod2 = boulder.modifiers.new(name="Displace2", type='DISPLACE')
displace_mod2.texture = noise_tex2
displace_mod2.strength = 0.2

bpy.ops.object.modifier_apply(modifier="Displace2")

# Flatten the bottom slightly
# Scale and move down
boulder.scale.z = 0.8
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# Add Subdivision Surface for smoother look
subsurf_mod = boulder.modifiers.new(name="Subsurf", type='SUBSURF')
subsurf_mod.levels = 2
subsurf_mod.render_levels = 3

# Apply subdivision
bpy.ops.object.modifier_apply(modifier="Subsurf")

# Smooth shading
bpy.ops.object.shade_smooth()

# Create moss patches using a shader node setup
mat = bpy.data.materials.new(name="MossBoulderMat")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (800, 0)

# Mix shader for combining rock and moss
mix_shader = nodes.new(type='ShaderNodeMixShader')
mix_shader.location = (600, 0)

# Rock material
rock_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
rock_bsdf.location = (200, 200)
rock_bsdf.inputs['Base Color'].default_value = (0.25, 0.22, 0.20, 1.0)
rock_bsdf.inputs['Roughness'].default_value = 0.9
rock_bsdf.inputs['Specular IOR Level'].default_value = 0.3

# Moss material
moss_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
moss_bsdf.location = (200, -200)
moss_bsdf.inputs['Base Color'].default_value = (0.15, 0.45, 0.12, 1.0)
moss_bsdf.inputs['Roughness'].default_value = 1.0
moss_bsdf.inputs['Specular IOR Level'].default_value = 0.1

# Noise texture for moss distribution
noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.location = (-200, 0)
noise_node.inputs['Scale'].default_value = 3.0
noise_node.inputs['Detail'].default_value = 8.0
noise_node.inputs['Roughness'].default_value = 0.6

# Color ramp to create distinct moss areas
color_ramp = nodes.new(type='ShaderNodeValToRGB')
color_ramp.location = (0, 0)
color_ramp.color_ramp.elements[0].position = 0.45
color_ramp.color_ramp.elements[1].position = 0.65

# Geometry node for normal-based masking (moss on top-facing surfaces)
geo_node = nodes.new(type='ShaderNodeNewGeometry')
geo_node.location = (-400, -300)

# Separate XYZ to get Z component
sep_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
sep_xyz.location = (-200, -300)

# Math node to threshold Z (only top-facing)
math_z = nodes.new(type='ShaderNodeMath')
math_z.location = (0, -300)
math_z.operation = 'GREATER_THAN'
math_z.inputs[1].default_value = 0.3

# Multiply noise with Z mask
math_mult = nodes.new(type='ShaderNodeMath')
math_mult.location = (200, -100)
math_mult.operation = 'MULTIPLY'

# Add some variation with a second noise
noise_node2 = nodes.new(type='ShaderNodeTexNoise')
noise_node2.location = (-200, 300)
noise_node2.inputs['Scale'].default_value = 8.0
noise_node2.inputs['Detail'].default_value = 6.0

# Mix the two noise values
math_mix_noise = nodes.new(type='ShaderNodeMath')
math_mix_noise.location = (0, 200)
math_mix_noise.operation = 'MULTIPLY_ADD'

# Final color ramp for moss mask
final_ramp = nodes.new(type='ShaderNodeValToRGB')
final_ramp.location = (300, 100)
final_ramp.color_ramp.elements[0].position = 0.4
final_ramp.color_ramp.elements[1].position = 0.7

# Link nodes
links.new(noise_node.outputs['Fac'], color_ramp.inputs['Fac'])
links.new(geo_node.outputs['Normal'], sep_xyz.inputs['Vector'])
links.new(sep_xyz.outputs['Z'], math_z.inputs[0])
links.new(color_ramp.outputs['Color'], math_mult.inputs[0])
links.new(math_z.outputs['Value'], math_mult.inputs[1])
links.new(noise_node.outputs['Fac'], math_mix_noise.inputs[0])
links.new(noise_node2.outputs['Fac'], math_mix_noise.inputs[1])
links.new(math_mix_noise.outputs['Value'], math_mix_noise.inputs[2])
links.new(math_mix_noise.outputs['Value'], final_ramp.inputs['Fac'])
links.new(final_ramp.outputs['Color'], mix_shader.inputs['Fac'])
links.new(rock_bsdf.outputs['BSDF'], mix_shader.inputs[1])
links.new(moss_bsdf.outputs['BSDF'], mix_shader.inputs[2])
links.new(mix_shader.outputs['Shader'], output_node.inputs['Surface'])

# Assign material to boulder
boulder.data.materials.append(mat)

# Add some displacement for moss bumps
# Create a new noise texture for moss bumps
moss_noise = bpy.data.textures.new(name="MossBumps", type='CLOUDS')
moss_noise.noise_scale = 0.1
moss_noise.noise_depth = 4

# We'll use a second material approach with displacement via geometry nodes or just rely on shader bump
# Add bump to the moss shader
bump_node = nodes.new(type='ShaderNodeBump')
bump_node.location = (0, -400)
bump_node.inputs['Strength'].default_value = 0.3
bump_node.inputs['Distance'].default_value = 0.05

links.new(noise_node2.outputs['Fac'], bump_node.inputs['Height'])
links.new(bump_node.outputs['Normal'], moss_bsdf.inputs['Normal'])

# Add a second bump for rock
rock_bump = nodes.new(type='ShaderNodeBump')
rock_bump.location = (0, 400)
rock_bump.inputs['Strength'].default_value = 0.2
rock_bump.inputs['Distance'].default_value = 0.03

rock_noise = nodes.new(type='ShaderNodeTexNoise')
rock_noise.location = (-200, 500)
rock_noise.inputs['Scale'].default_value = 15.0
rock_noise.inputs['Detail'].default_value = 10.0

links.new(rock_noise.outputs['Fac'], rock_bump.inputs['Height'])
links.new(rock_bump.outputs['Normal'], rock_bsdf.inputs['Normal'])

# Add some small moss clumps as separate objects for detail
random.seed(42)
moss_clump_count = 20
for i in range(moss_clump_count):
    # Random position on top of boulder
    theta = random.uniform(0, 2 * math.pi)
    phi = random.uniform(0, math.pi / 3)  # Upper hemisphere
    r = 0.95 + random.uniform(0, 0.1)
    
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi) * 0.8  # Match flattened Z
    
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=random.uniform(0.05, 0.12), location=(x, y, z))
    clump = bpy.context.active_object
    clump.name = f"MossClump_{i}"
    
    # Random scale
    clump.scale = (random.uniform(0.8, 1.5), random.uniform(0.8, 1.5), random.uniform(0.5, 0.8))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Slight random rotation
    clump.rotation_euler = (random.uniform(0, 0.3), random.uniform(0, 0.3), random.uniform(0, 2 * math.pi))
    
    # Assign moss material
    clump.data.materials.append(mat)
    
    # Smooth shading
    bpy.ops.object.shade_smooth()

# Add a ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.85))
ground = bpy.context.active_object
ground.name = "Ground"

# Ground material
ground_mat = bpy.data.materials.new(name="GroundMat")
ground_mat.use_nodes = True
g_nodes = ground_mat.node_tree.nodes
g_links = ground_mat.node_tree.links

for node in g_nodes:
    g_nodes.remove(node)

g_output = g_nodes.new(type='ShaderNodeOutputMaterial')
g_output.location = (400, 0)

g_bsdf = g_nodes.new(type='ShaderNodeBsdfPrincipled')
g_bsdf.location = (100, 0)
g_bsdf.inputs['Base Color'].default_value = (0.2, 0.18, 0.15, 1.0)
g_bsdf.inputs['Roughness'].default_value = 0.95

g_links.new(g_bsdf.outputs['BSDF'], g_output.inputs['Surface'])
ground.data.materials.append(ground_mat)

# Add a simple sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Set viewport shading
bpy.context.view_layer.shading.type = 'MATERIAL'

print("Moss-covered boulder created successfully!")
