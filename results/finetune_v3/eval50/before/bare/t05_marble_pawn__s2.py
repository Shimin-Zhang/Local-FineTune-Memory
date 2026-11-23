import bpy
import math
import random
from mathutils import Vector

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Create the chess pawn geometry ---
# A chess pawn typically has: base, stem, collar, and head (sphere)
# We'll build it using a lathe/spin operation or by joining primitives

# Method: Create the pawn using a profile curve and spin it, or use cylinders and spheres

# Simpler approach: join basic shapes
# Base: flat cylinder
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.5, depth=0.15, location=(0, 0, 0.075))
base = bpy.context.object
base.name = "Pawn_Base"

# Stem: tapered cylinder
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=0.2, depth=0.8, location=(0, 0, 0.55))
stem = bpy.context.object
stem.name = "Pawn_Stem"
# Taper the top
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
# We'll just use a cone for the stem to give it a tapered look
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['Pawn_Stem'].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects['Pawn_Stem']
bpy.ops.object.delete()

bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=0.25, radius2=0.15, depth=0.8, location=(0, 0, 0.55))
stem = bpy.context.object
stem.name = "Pawn_Stem"

# Collar: small torus or cylinder
bpy.ops.mesh.primitive_torus_add(major_radius=0.18, minor_radius=0.06, major_segments=64, minor_segments=32, location=(0, 0, 0.95))
collar = bpy.context.object
collar.name = "Pawn_Collar"

# Head: sphere
bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, radius=0.22, location=(0, 0, 1.25))
head = bpy.context.object
head.name = "Pawn_Head"
# Smooth shade the head
bpy.ops.object.shade_smooth()

# Join all parts into one object
bpy.ops.object.select_all(action='DESELECT')
for obj in [base, stem, collar, head]:
    obj.select_set(True)
bpy.context.view_layer.objects.active = base
bpy.ops.object.join()
pawn = bpy.context.object
pawn.name = "Chess_Pawn"

# Apply smooth shading to the whole pawn
bpy.ops.object.shade_smooth()

# --- Create the white marble material with grey veins ---
mat = bpy.data.materials.new(name="White_Marble")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create nodes
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (800, 0)

principled_node = nodes.new('ShaderNodeBsdfPrincipled')
principled_node.location = (500, 0)
principled_node.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)
principled_node.inputs['Roughness'].default_value = 0.15
principled_node.inputs['Metallic'].default_value = 0.0
# Slight subsurface for marble feel
if 'Subsurface Weight' in principled_node.inputs:
    principled_node.inputs['Subsurface Weight'].default_value = 0.1
    if 'Subsurface Radius' in principled_node.inputs:
        principled_node.inputs['Subsurface Radius'].default_value = (0.5, 0.5, 0.5)

# Texture Coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-800, 0)

# Mapping node to control scale
mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-600, 0)
mapping.inputs['Scale'].default_value = (3.0, 3.0, 3.0)

# Noise texture for veins
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 0)
noise.inputs['Scale'].default_value = 5.0
noise.inputs['Detail'].default_value = 8.0
noise.inputs['Roughness'].default_value = 0.6
noise.inputs['Distortion'].default_value = 1.5

# ColorRamp to create vein pattern (threshold the noise)
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (-200, 0)
color_ramp.color_ramp.interpolation = 'LINEAR'
# Set stops: mostly white, with grey veins
# Position 0: white
color_ramp.color_ramp.elements[0].position = 0.3
color_ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.85, 1.0)  # white marble
# Position 1: grey
color_ramp.color_ramp.elements[1].position = 0.55
color_ramp.color_ramp.elements[1].color = (0.45, 0.45, 0.45, 1.0)  # grey veins

# Add a second noise for more organic vein patterns
noise2 = nodes.new('ShaderNodeTexNoise')
noise2.location = (-400, -200)
noise2.inputs['Scale'].default_value = 8.0
noise2.inputs['Detail'].default_value = 10.0
noise2.inputs['Roughness'].default_value = 0.7
noise2.inputs['Distortion'].default_value = 2.0

# Mix the two noises
mix_noise = nodes.new('ShaderNodeMix')
mix_noise.location = (-200, -100)
mix_noise.data_type = 'FLOAT'
mix_noise.inputs['Factor'].default_value = 0.5

# ColorRamp for second vein layer
color_ramp2 = nodes.new('ShaderNodeValToRGB')
color_ramp2.location = (0, -200)
color_ramp2.color_ramp.interpolation = 'LINEAR'
color_ramp2.color_ramp.elements[0].position = 0.35
color_ramp2.color_ramp.elements[0].color = (0.85, 0.85, 0.85, 1.0)
color_ramp2.color_ramp.elements[1].position = 0.6
color_ramp2.color_ramp.elements[1].color = (0.5, 0.5, 0.5, 1.0)

# Mix the two color ramps
mix_color = nodes.new('ShaderNodeMix')
mix_color.location = (200, -100)
mix_color.data_type = 'RGBA'
mix_color.inputs['Factor'].default_value = 0.5

# Connect nodes
links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])

links.new(noise.outputs['Fac'], mix_noise.inputs['A'])
links.new(noise2.outputs['Fac'], mix_noise.inputs['B'])

links.new(mix_noise.outputs['Result'], color_ramp.inputs['Fac'])
links.new(noise2.outputs['Fac'], color_ramp2.inputs['Fac'])

links.new(color_ramp.outputs['Color'], mix_color.inputs['A'])
links.new(color_ramp2.outputs['Color'], mix_color.inputs['B'])

links.new(mix_color.outputs['Result'], principled_node.inputs['Base Color'])
links.new(principled_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to the pawn
pawn.data.materials.clear()
pawn.data.materials.append(mat)

# --- Set up a simple scene for context ---
# Add a light
bpy.ops.object.light_add(type='AREA', location=(2, 2, 3))
light = bpy.context.object
light.data.energy = 500
light.data.size = 2

# Add a world background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.1, 0.1, 0.1, 1.0)
    bg_node.inputs['Strength'].default_value = 0.5

# Set camera
bpy.ops.object.camera_add(location=(2, -2, 1.5), rotation=(math.radians(60), 0, math.radians(45)))
cam = bpy.context.object
bpy.context.scene.camera = cam

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024

print("Chess pawn with white marble and grey veins created successfully.")
