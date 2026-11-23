import bpy
import bmesh
import math
import random
from mathutils import Vector

# Set random seed for reproducibility
random.seed(42)

# Remove default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base icosphere
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0, location=(0, 0, 0))
rock_obj = bpy.context.active_object
rock_obj.name = "LavaRock"

# Displace vertices to make it look like a rock
bm = bmesh.new()
bm.from_mesh(rock_obj.data)

for vert in bm.verts:
    # Add noise-based displacement
    noise = (
        math.sin(vert.co.x * 3.0) * math.cos(vert.co.y * 2.5) * 0.3 +
        math.sin(vert.co.y * 4.0) * math.cos(vert.co.z * 3.5) * 0.25 +
        math.sin(vert.co.z * 2.0) * math.cos(vert.co.x * 4.5) * 0.2 +
        random.uniform(-0.1, 0.1)
    )
    vert.co += vert.co.normalized() * noise

bm.to_mesh(rock_obj.data)
bm.free()

# Recalculate normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Create material for the rock
rock_mat = bpy.data.materials.new(name="LavaRockMaterial")
rock_mat.use_nodes = True
nodes = rock_mat.node_tree.nodes
links = rock_mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (600, 0)

# Noise texture for rock surface
noise_node = nodes.new('ShaderNodeTexNoise')
noise_node.location = (-400, 0)
noise_node.inputs['Scale'].default_value = 8.0
noise_node.inputs['Detail'].default_value = 10.0
noise_node.inputs['Roughness'].default_value = 0.6

# Voronoi for crack pattern
voronoi_node = nodes.new('ShaderNodeTexVoronoi')
voronoi_node.location = (-400, -200)
voronoi_node.feature = 'DISTANCE_TO_EDGE'
voronoi_node.inputs['Scale'].default_value = 5.0

# ColorRamp for rock color (dark basalt)
rock_ramp = nodes.new('ShaderNodeValToRGB')
rock_ramp.location = (-100, 100)
rock_ramp.color_ramp.elements[0].position = 0.0
rock_ramp.color_ramp.elements[0].color = (0.05, 0.04, 0.04, 1.0)
rock_ramp.color_ramp.elements[1].position = 1.0
rock_ramp.color_ramp.elements[1].color = (0.15, 0.12, 0.10, 1.0)

# ColorRamp for crack glow (orange to yellow)
crack_ramp = nodes.new('ShaderNodeValToRGB')
crack_ramp.location = (-100, -200)
crack_ramp.color_ramp.elements[0].position = 0.0
crack_ramp.color_ramp.elements[0].color = (1.0, 0.3, 0.05, 1.0)  # Orange
crack_ramp.color_ramp.elements[1].position = 0.3
crack_ramp.color_ramp.elements[1].color = (1.0, 0.8, 0.2, 1.0)   # Yellow
# Add a third element for hot core
crack_ramp.color_ramp.elements.new(0.1).color = (1.0, 0.5, 0.1, 1.0)

# Mix shader to combine rock and crack
mix_shader = nodes.new('ShaderNodeMixShader')
mix_shader.location = (300, 0)

# Principled BSDF for rock
rock_bsdf = nodes.new('ShaderNodeBsdfPrincipled')
rock_bsdf.location = (100, 100)
rock_bsdf.inputs['Roughness'].default_value = 0.9
rock_bsdf.inputs['Specular'].default_value = 0.1

# Emission for cracks
crack_emission = nodes.new('ShaderNodeEmission')
crack_emission.location = (100, -200)
crack_emission.inputs['Strength'].default_value = 5.0

# Links
# Noise to rock ramp
links.new(noise_node.outputs['Fac'], rock_ramp.inputs['Fac'])
# Rock ramp to rock BSDF color
links.new(rock_ramp.outputs['Color'], rock_bsdf.inputs['Base Color'])

# Voronoi to crack ramp (invert so cracks are bright)
crack_invert = nodes.new('ShaderNodeInvert')
crack_invert.location = (-250, -200)
links.new(voronoi_node.outputs['Distance'], crack_invert.inputs['Color'])
links.new(crack_invert.outputs['Color'], crack_ramp.inputs['Fac'])

# Crack ramp to emission color
links.new(crack_ramp.outputs['Color'], crack_emission.inputs['Color'])

# Mix shader: use voronoi distance as factor (where distance is small = crack)
crack_mask = nodes.new('ShaderNodeMath')
crack_mask.location = (0, -300)
crack_mask.operation = 'LESS_THAN'
crack_mask.inputs[1].default_value = 0.05  # Threshold for crack
links.new(voronoi_node.outputs['Distance'], crack_mask.inputs[0])
links.new(crack_mask.outputs['Value'], mix_shader.inputs['Fac'])

# Connect shaders to mix
links.new(rock_bsdf.outputs['BSDF'], mix_shader.inputs[1])
links.new(crack_emission.outputs['Emission'], mix_shader.inputs[2])
links.new(mix_shader.outputs['Shader'], output_node.inputs['Surface'])

# Assign material to rock
rock_obj.data.materials.append(rock_mat)

# Add a point light inside the rock for extra glow effect
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
light_obj = bpy.context.active_object
light_obj.name = "InnerGlow"
light_obj.data.energy = 50
light_obj.data.color = (1.0, 0.4, 0.1)
light_obj.data.shadow_soft_size = 0.5

# Add an area light for ambient
bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
area_light = bpy.context.active_object
area_light.name = "AmbientLight"
area_light.data.energy = 100
area_light.data.color = (1.0, 0.8, 0.6)
area_light.data.size = 2.0

# Set up camera
bpy.ops.object.camera_add(location=(3, -3, 2))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Point camera at the rock
direction = Vector((0, 0, 0)) - camera.location
rotation_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rotation_quat.to_euler()

# Set world background to dark
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

# Clear world nodes
for node in world_nodes:
    world_nodes.remove(node)

bg_node = world_nodes.new('ShaderNodeBackground')
bg_node.location = (0, 0)
bg_node.inputs['Color'].default_value = (0.01, 0.01, 0.015, 1.0)
bg_node.inputs['Strength'].default_value = 1.0

world_output = world_nodes.new('ShaderNodeOutputWorld')
world_output.location = (200, 0)
world_links.new(bg_node.outputs['Background'], world_output.inputs['Surface'])

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
