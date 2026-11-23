import bpy
import math
import random
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new collection for the crate
crate_collection = bpy.data.collections.new("WoodenCrate")
bpy.context.scene.collection.children.link(crate_collection)

# Set up materials
def create_wood_material(name, base_color, roughness=0.7):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Create nodes
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    
    # Add noise texture for wood grain
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-200, 0)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    noise.inputs['Lacunarity'].default_value = 2.0
    
    # Add wave texture for grain lines
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-200, -200)
    wave.inputs['Scale'].default_value = 5.0
    wave.inputs['Distortion'].default_value = 10.0
    wave.inputs['Detail'].default_value = 3.0
    wave.inputs['Detail Scale'].default_value = 1.0
    
    # Mix noise and wave
    mix = nodes.new('ShaderNodeMix')
    mix.location = (0, -100)
    mix.data_type = 'RGBA'
    mix.inputs['Factor'].default_value = 0.3
    
    # Color ramp for wood tones
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 200)
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = [base_color[0]*0.6, base_color[1]*0.6, base_color[2]*0.6, 1.0]
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = [base_color[0]*1.2, base_color[1]*1.2, base_color[2]*1.2, 1.0]
    
    # Bump map
    bump = nodes.new('ShaderNodeBump')
    bump.location = (0, -300)
    bump.inputs['Strength'].default_value = 0.3
    
    # Links
    links.new(noise.outputs['Fac'], wave.inputs['Distortion'])
    links.new(wave.outputs['Color'], mix.inputs[6])
    links.new(noise.outputs['Fac'], mix.inputs[7])
    links.new(mix.outputs[2], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

# Create wood materials
wood_mat_dark = create_wood_material("WoodDark", [0.25, 0.15, 0.08, 1.0], 0.75)
wood_mat_medium = create_wood_material("WoodMedium", [0.35, 0.22, 0.12, 1.0], 0.7)
wood_mat_light = create_wood_material("WoodLight", [0.45, 0.30, 0.18, 1.0], 0.65)

# Crate dimensions
crate_size = 2.0
plank_thickness = 0.08
plank_width = crate_size / 5.0
gap = 0.02

# Helper function to create a plank
def create_plank(width, height, depth, location, rotation=(0,0,0), material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (width/2, height/2, depth/2)
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(scale=True)
    
    # Add bevel for rounded edges
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.005
    bevel.segments = 2
    
    if material:
        obj.data.materials.append(material)
    
    return obj

# Create crate structure
crate_center = (0, 0, crate_size/2)

# Bottom planks (5 planks)
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + gap)
    mat = [wood_mat_dark, wood_mat_medium, wood_mat_light, wood_mat_medium, wood_mat_dark][i]
    create_plank(plank_width, crate_size, plank_thickness, 
                 (x, 0, crate_size/2), (0, 0, 0), mat)

# Top planks (5 planks)
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + gap)
    mat = [wood_mat_light, wood_mat_medium, wood_mat_dark, wood_mat_medium, wood_mat_light][i]
    create_plank(plank_width, crate_size, plank_thickness, 
                 (x, 0, crate_size - crate_size/2), (0, 0, 0), mat)

# Front planks (5 vertical planks)
for i in range(5):
    y = -crate_size/2 + plank_width/2 + i * (plank_width + gap)
    mat = [wood_mat_medium, wood_mat_dark, wood_mat_light, wood_mat_dark, wood_mat_medium][i]
    create_plank(crate_size, plank_width, plank_thickness, 
                 (0, y, crate_size/2), (0, 0, 0), mat)

# Back planks (5 vertical planks)
for i in range(5):
    y = -crate_size/2 + plank_width/2 + i * (plank_width + gap)
    mat = [wood_mat_dark, wood_mat_light, wood_mat_medium, wood_mat_light, wood_mat_dark][i]
    create_plank(crate_size, plank_width, plank_thickness, 
                 (0, -y, crate_size/2), (0, 0, 0), mat)

# Left side planks (5 vertical planks)
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + gap)
    mat = [wood_mat_light, wood_mat_medium, wood_mat_dark, wood_mat_medium, wood_mat_light][i]
    create_plank(plank_width, crate_size, plank_thickness, 
                 (-crate_size/2, 0, crate_size/2), (0, 0, 0), mat)

# Right side planks (5 vertical planks)
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + gap)
    mat = [wood_mat_medium, wood_mat_light, wood_mat_medium, wood_mat_light, wood_mat_medium][i]
    create_plank(plank_width, crate_size, plank_thickness, 
                 (crate_size/2, 0, crate_size/2), (0, 0, 0), mat)

# Add corner reinforcements (diagonal braces)
def create_brace(start, end, thickness=0.06, material=None):
    # Calculate length and orientation
    vec = Vector(end) - Vector(start)
    length = vec.length
    mid = (Vector(start) + Vector(end)) / 2
    
    # Create a thin cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    obj = bpy.context.active_object
    obj.scale = (thickness/2, thickness/2, length/2)
    
    # Rotate to align with vector
    rot = vec.to_track_quat('Z', 'Y').to_euler()
    obj.rotation_euler = rot
    bpy.ops.object.transform_apply(scale=True)
    
    if material:
        obj.data.materials.append(material)
    
    return obj

# Add diagonal braces on each face
brace_mat = wood_mat_dark

# Front face braces
create_brace((-crate_size/2+0.1, crate_size/2-0.1, 0.1), (crate_size/2-0.1, crate_size/2-0.1, crate_size-0.1), brace_mat)
create_brace((crate_size/2-0.1, crate_size/2-0.1, 0.1), (-crate_size/2+0.1, crate_size/2-0.1, crate_size-0.1), brace_mat)

# Back face braces
create_brace((-crate_size/2+0.1, -crate_size/2+0.1, 0.1), (crate_size/2-0.1, -crate_size/2+0.1, crate_size-0.1), brace_mat)
create_brace((crate_size/2-0.1, -crate_size/2+0.1, 0.1), (-crate_size/2+0.1, -crate_size/2+0.1, crate_size-0.1), brace_mat)

# Left face braces
create_brace((-crate_size/2+0.1, -crate_size/2+0.1, 0.1), (-crate_size/2+0.1, crate_size/2-0.1, crate_size-0.1), brace_mat)
create_brace((-crate_size/2+0.1, crate_size/2-0.1, 0.1), (-crate_size/2+0.1, -crate_size/2+0.1, crate_size-0.1), brace_mat)

# Right face braces
create_brace((crate_size/2-0.1, -crate_size/2+0.1, 0.1), (crate_size/2-0.1, crate_size/2-0.1, crate_size-0.1), brace_mat)
create_brace((crate_size/2-0.1, crate_size/2-0.1, 0.1), (crate_size/2-0.1, -crate_size/2+0.1, crate_size-0.1), brace_mat)

# Move all objects to the crate collection
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for collection in obj.users_collection:
            collection.objects.unlink(obj)
        crate_collection.objects.link(obj)

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add camera
bpy.ops.object.camera_add(location=(4, -4, 3))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(50), 0, math.radians(45))
bpy.context.scene.camera = cam

# Set up world
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = [0.1, 0.1, 0.1, 1.0]
    bg.inputs[1].default_value = 1.0

print("Wooden crate created with visible planks and wood grain!")
