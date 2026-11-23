import bpy
import math
import random

# Clean up
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create the watermelon sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32)
watermelon = bpy.context.active_object
watermelon.name = "Watermelon"

# Scale to make it slightly oblate (flattened)
watermelon.scale = (1.0, 1.0, 0.95)
bpy.ops.object.transform_apply(scale=True)

# Create a material with procedural stripes
mat = bpy.data.materials.new(name="WatermelonSkin")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (800, 0)

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (500, 0)
bsdf.inputs['Roughness'].default_value = 0.3

# Texture coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-600, 0)

# Mapping to control stripe direction
mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-400, 0)
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

# Separate XYZ to get the Z component for stripes (vertical stripes)
sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
sep_xyz.location = (-200, 0)
links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])

# Math node to create stripe pattern using sine wave
math_sin = nodes.new('ShaderNodeMath')
math_sin.operation = 'SINE'
math_sin.location = (0, 0)
links.new(sep_xyz.outputs['X'], math_sin.inputs[0])

# Scale the sine to make narrower stripes
math_scale = nodes.new('ShaderNodeMath')
math_scale.operation = 'MULTIPLY'
math_scale.location = (150, 0)
math_scale.inputs[1].default_value = 15.0
links.new(math_sin.outputs[0], math_scale.inputs[0])

# Convert to a threshold for sharp stripes
math_threshold = nodes.new('ShaderNodeMath')
math_threshold.operation = 'GREATER_THAN'
math_threshold.location = (300, 0)
math_threshold.inputs[1].default_value = 0.0
links.new(math_scale.outputs[0], math_threshold.inputs[0])

# Mix colors: dark green and light green
mix_rgb = nodes.new('ShaderNodeMixRGB')
mix_rgb.location = (400, 0)
mix_rgb.inputs['Color1'].default_value = (0.05, 0.25, 0.05, 1.0)  # Dark green
mix_rgb.inputs['Color2'].default_value = (0.15, 0.55, 0.15, 1.0)  # Light green
links.new(math_threshold.outputs[0], mix_rgb.inputs['Fac'])

# Connect to BSDF
links.new(mix_rgb.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material
watermelon.data.materials.append(mat)

# Add a small stem
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.3, location=(0, 0, 0.95))
stem = bpy.context.active_object
stem.name = "Stem"
stem.rotation_euler = (0, 0.1, 0)

# Stem material
stem_mat = bpy.data.materials.new(name="StemMaterial")
stem_mat.use_nodes = True
stem_bsdf = stem_mat.node_tree.nodes['Principled BSDF']
stem_bsdf.inputs['Base Color'].default_value = (0.1, 0.3, 0.05, 1.0)
stem_bsdf.inputs['Roughness'].default_value = 0.5
stem.data.materials.append(stem_mat)

# Set viewport to show the watermelon
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].shading.type = 'MATERIAL'
        # Frame all objects
        with bpy.context.temp_override(area=area, region=area.regions[-1]):
            bpy.ops.view3d.view_all()
