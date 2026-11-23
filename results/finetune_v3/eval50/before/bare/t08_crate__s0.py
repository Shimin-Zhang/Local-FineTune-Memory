import bpy
import math
import random
from mathutils import Vector, Matrix

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up scene
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.cycles.use_denoising = True

# Camera setup
cam_data = bpy.data.cameras.new("Camera")
cam = bpy.data.objects.new("Camera", cam_data)
scene.collection.objects.link(cam)
cam.location = (3.5, -3.5, 2.5)
cam.rotation_euler = (math.radians(65), 0, math.radians(45))
scene.camera = cam

# Lighting
light_data = bpy.data.lights.new("KeyLight", type='SUN')
light_data.energy = 3.0
light_data.angle = math.radians(5)
light = bpy.data.objects.new("KeyLight", light_data)
scene.collection.objects.link(light)
light.rotation_euler = (math.radians(50), math.radians(20), math.radians(30))

light_data2 = bpy.data.lights.new("FillLight", type='SUN')
light_data2.energy = 1.0
light2 = bpy.data.objects.new("FillLight", light_data2)
scene.collection.objects.link(light2)
light2.rotation_euler = (math.radians(70), math.radians(-30), math.radians(-20))

# Create wood grain texture using procedural nodes
def create_wood_material(name, base_color, dark_color, grain_scale=10.0, roughness=0.6):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # Clear default nodes
    for node in nodes:
        nodes.remove(node)
    
    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (800, 0)
    
    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (500, 0)
    bsdf.inputs['Roughness'].default_value = roughness
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-800, 0)
    
    # Mapping
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-600, 0)
    mapping.inputs['Scale'].default_value = (1.0, grain_scale, 1.0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    
    # Noise for grain
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = 8.0
    noise.inputs['Detail'].default_value = 10.0
    noise.inputs['Roughness'].default_value = 0.7
    noise.inputs['Distortion'].default_value = 0.3
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    
    # Wave texture for grain lines
    wave = nodes.new('ShaderNodeTexWave')
    wave.location = (-400, -100)
    wave.inputs['Scale'].default_value = 3.0
    wave.inputs['Distortion'].default_value = 4.0
    wave.inputs['Detail'].default_value = 2.0
    wave.bands_direction = 'Y'
    links.new(mapping.outputs['Vector'], wave.inputs['Vector'])
    
    # Combine noise and wave
    mix_grain = nodes.new('ShaderNodeMixRGB')
    mix_grain.location = (-200, 0)
    mix_grain.blend_type = 'MULTIPLY'
    mix_grain.inputs['Fac'].default_value = 0.5
    links.new(noise.outputs['Fac'], mix_grain.inputs['Color1'])
    links.new(wave.outputs['Fac'], mix_grain.inputs['Color2'])
    
    # Color ramp for wood colors
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.location = (0, 0)
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = dark_color
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = base_color
    links.new(mix_grain.outputs['Color'], ramp.inputs['Fac'])
    
    # Add subtle variation
    noise2 = nodes.new('ShaderNodeTexNoise')
    noise2.location = (-400, 300)
    noise2.inputs['Scale'].default_value = 2.0
    noise2.inputs['Detail'].default_value = 4.0
    links.new(tex_coord.outputs['Object'], noise2.inputs['Vector'])
    
    mix_color = nodes.new('ShaderNodeMixRGB')
    mix_color.location = (200, 0)
    mix_color.blend_type = 'MULTIPLY'
    mix_color.inputs['Fac'].default_value = 0.15
    links.new(ramp.outputs['Color'], mix_color.inputs['Color1'])
    links.new(noise2.outputs['Fac'], mix_color.inputs['Color2'])
    
    links.new(mix_color.outputs['Color'], bsdf.inputs['Base Color'])
    
    # Bump for wood grain
    bump = nodes.new('ShaderNodeBump')
    bump.location = (300, -200)
    bump.inputs['Strength'].default_value = 0.15
    links.new(mix_grain.outputs['Color'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    
    return mat

# Create wood materials
wood_mat = create_wood_material("Wood", (0.45, 0.28, 0.12, 1.0), (0.25, 0.12, 0.05, 1.0), grain_scale=15.0, roughness=0.55)
dark_wood_mat = create_wood_material("DarkWood", (0.35, 0.20, 0.08, 1.0), (0.18, 0.08, 0.03, 1.0), grain_scale=12.0, roughness=0.6)

# Crate dimensions
crate_size = 2.0
wall_thickness = 0.08
plank_width = 0.25
plank_gap = 0.02

# Helper to create a plank
def create_plank(length, width, thickness, location, rotation, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (length / 2, width / 2, thickness / 2)
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    return obj

# Create crate planks
planks = []

# Bottom planks
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + plank_gap)
    plank = create_plank(crate_size, plank_width, wall_thickness, 
                        (x, 0, -crate_size/2 + wall_thickness/2),
                        (0, 0, 0), wood_mat)
    planks.append(plank)

# Top planks
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + plank_gap)
    plank = create_plank(crate_size, plank_width, wall_thickness,
                        (x, 0, crate_size/2 - wall_thickness/2),
                        (0, 0, 0), wood_mat)
    planks.append(plank)

# Front and back walls
for i in range(5):
    y = -crate_size/2 + plank_width/2 + i * (plank_width + plank_gap)
    # Front wall
    plank = create_plank(plank_width, crate_size, wall_thickness,
                        (0, y, 0),
                        (math.radians(90), 0, 0), wood_mat)
    planks.append(plank)
    # Back wall
    plank = create_plank(plank_width, crate_size, wall_thickness,
                        (0, -y, 0),
                        (math.radians(90), 0, 0), wood_mat)
    planks.append(plank)

# Left and right walls
for i in range(5):
    x = -crate_size/2 + plank_width/2 + i * (plank_width + plank_gap)
    # Left wall
    plank = create_plank(crate_size, plank_width, wall_thickness,
                        (x, 0, 0),
                        (0, math.radians(90), 0), wood_mat)
    planks.append(plank)
    # Right wall
    plank = create_plank(crate_size, plank_width, wall_thickness,
                        (-x, 0, 0),
                        (0, math.radians(90), 0), wood_mat)
    planks.append(plank)

# Corner posts (darker wood for contrast)
post_size = 0.12
corners = [
    (-crate_size/2 + post_size/2, -crate_size/2 + post_size/2),
    (crate_size/2 - post_size/2, -crate_size/2 + post_size/2),
    (-crate_size/2 + post_size/2, crate_size/2 - post_size/2),
    (crate_size/2 - post_size/2, crate_size/2 - post_size/2),
]

for cx, cy in corners:
    post = create_plank(post_size, post_size, crate_size,
                       (cx, cy, 0),
                       (0, 0, 0), dark_wood_mat)
    planks.append(post)

# Add diagonal braces on sides
def create_brace(p1, p2, thickness, material):
    """Create a brace between two points"""
    length = (Vector(p2) - Vector(p1)).length
    mid = (Vector(p1) + Vector(p2)) / 2
    
    # Calculate rotation
    direction = Vector(p2) - Vector(p1)
    rot_z = math.atan2(direction.y, direction.x)
    rot_y = math.atan2(direction.z, math.sqrt(direction.x**2 + direction.y**2))
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
    obj = bpy.context.active_object
    obj.scale = (length / 2, thickness / 2, thickness / 2)
    obj.rotation_euler = (0, rot_y, rot_z)
    obj.data.materials.append(material)
    return obj

# Diagonal braces on front and back
brace_thick = 0.06
# Front braces
create_brace((-crate_size/2 + 0.1, -crate_size/2, -crate_size/2 + 0.1),
             (crate_size/2 - 0.1, -crate_size/2, crate_size/2 - 0.1),
             brace_thick, dark_wood_mat)
create_brace((crate_size/2 - 0.1, -crate_size/2, -crate_size/2 + 0.1),
             (-crate_size/2 + 0.1, -crate_size/2, crate_size/2 - 0.1),
             brace_thick, dark_wood_mat)

# Back braces
create_brace((-crate_size/2 + 0.1, crate_size/2, -crate_size/2 + 0.1),
             (crate_size/2 - 0.1, crate_size/2, crate_size/2 - 0.1),
             brace_thick, dark_wood_mat)
create_brace((crate_size/2 - 0.1, crate_size/2, -crate_size/2 + 0.1),
             (-crate_size/2 + 0.1, crate_size/2, crate_size/2 - 0.1),
             brace_thick, dark_wood_mat)

# Add some bevel to all planks for realism
for plank in planks:
    modifier = plank.modifiers.new("Bevel", 'BEVEL')
    modifier.width = 0.005
    modifier.segments = 2

# Add a ground plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -crate_size/2 - 0.01))
ground = bpy.context.active_object
ground_mat = bpy.data.materials.new("Ground")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.3, 0.25, 0.2, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8
ground.data.materials.append(ground_mat)

# Set render resolution
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

print("Wooden crate created successfully!")
