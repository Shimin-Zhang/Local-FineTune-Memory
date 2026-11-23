import bpy
import math
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set seed for reproducibility
random.seed(42)

# Material setup
def create_wood_material(name, base_color, roughness=0.6):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear existing nodes
    for n in nodes:
        nodes.remove(n)

    # Output
    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (400, 0)

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (100, 0)
    bsdf.inputs['Roughness'].default_value = roughness

    # Noise texture for wood grain
    noise = nodes.new('ShaderNodeTexNoise')
    noise.location = (-500, 0)
    noise.inputs['Scale'].default_value = 15.0
    noise.inputs['Detail'].default_value = 8.0
    noise.inputs['Roughness'].default_value = 0.6
    noise.inputs['Distortion'].default_value = 0.3

    # Mapping for stretching (wood grain direction)
    mapping = nodes.new('ShaderNodeMapping')
    mapping.location = (-700, 0)
    mapping.inputs['Scale'].default_value = (1.0, 10.0, 1.0)  # Stretch along Y for grain

    # Texture coordinate
    tex_coord = nodes.new('ShaderNodeTexCoord')
    tex_coord.location = (-900, 0)

    # ColorRamp for wood tones
    color_ramp = nodes.new('ShaderNodeValToRGB')
    color_ramp.location = (-300, 0)
    color_ramp.color_ramp.interpolation = 'LINEAR'

    # Set color stops for wood
    color_ramp.color_ramp.elements[0].position = 0.3
    color_ramp.color_ramp.elements[0].color = [base_color[0] * 0.7, base_color[1] * 0.7, base_color[2] * 0.7, 1.0]
    color_ramp.color_ramp.elements[1].position = 0.7
    color_ramp.color_ramp.elements[1].color = [base_color[0], base_color[1], base_color[2], 1.0]

    # Add another element for darker grain
    elem_mid = color_ramp.color_ramp.elements.new(0.5)
    elem_mid.color = [base_color[0] * 0.85, base_color[1] * 0.85, base_color[2] * 0.85, 1.0]

    # Links
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    return mat

# Create wood materials
wood_light = create_wood_material("Wood_Light", [0.55, 0.35, 0.15], 0.65)
wood_dark = create_wood_material("Wood_Dark", [0.4, 0.25, 0.1], 0.7)

# Crate dimensions
crate_w = 1.0  # width (X)
crate_h = 1.0  # height (Y)
crate_d = 1.0  # depth (Z)
plank_thickness = 0.03
plank_gap = 0.01

def create_plank(width, height, depth, location, material, rotation=(0, 0, 0)):
    """Create a single plank (box) with beveled edges."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (width / 2, height / 2, depth / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Add bevel modifier for slight edge rounding
    bevel = obj.modifiers.new(name="Bevel", type='BEVEL')
    bevel.width = 0.005
    bevel.segments = 2

    obj.data.materials.append(material)
    obj.rotation_euler = rotation
    return obj

# Create crate planks
planks = []

# Bottom planks (along X, stacked in Z)
num_bottom = 4
for i in range(num_bottom):
    z_pos = -crate_d / 2 + plank_thickness / 2 + i * (plank_thickness + plank_gap)
    plank = create_plank(
        crate_w, crate_h, plank_thickness,
        (0, 0, z_pos),
        wood_light
    )
    planks.append(plank)

# Top planks
for i in range(num_bottom):
    z_pos = crate_d / 2 - plank_thickness / 2 - i * (plank_thickness + plank_gap)
    plank = create_plank(
        crate_w, crate_h, plank_thickness,
        (0, 0, z_pos),
        wood_light
    )
    planks.append(plank)

# Front planks (along Y, on +X face)
num_side = 4
for i in range(num_side):
    x_pos = crate_w / 2 - plank_thickness / 2
    y_offset = -crate_h / 2 + plank_thickness / 2 + i * (crate_h / num_side)
    plank_h = crate_h / num_side - plank_gap
    plank = create_plank(
        plank_thickness, plank_h, crate_d,
        (x_pos, y_offset, 0),
        wood_dark
    )
    planks.append(plank)

# Back planks (on -X face)
for i in range(num_side):
    x_pos = -crate_w / 2 + plank_thickness / 2
    y_offset = -crate_h / 2 + plank_thickness / 2 + i * (crate_h / num_side)
    plank_h = crate_h / num_side - plank_gap
    plank = create_plank(
        plank_thickness, plank_h, crate_d,
        (x_pos, y_offset, 0),
        wood_dark
    )
    planks.append(plank)

# Left planks (along X, on +Y face)
for i in range(num_side):
    y_pos = crate_h / 2 - plank_thickness / 2
    x_offset = -crate_w / 2 + plank_thickness / 2 + i * (crate_w / num_side)
    plank_w = crate_w / num_side - plank_gap
    plank = create_plank(
        plank_w, plank_thickness, crate_d,
        (x_offset, y_pos, 0),
        wood_dark
    )
    planks.append(plank)

# Right planks (on -Y face)
for i in range(num_side):
    y_pos = -crate_h / 2 + plank_thickness / 2
    x_offset = -crate_w / 2 + plank_thickness / 2 + i * (crate_w / num_side)
    plank_w = crate_w / num_side - plank_gap
    plank = create_plank(
        plank_w, plank_thickness, crate_d,
        (x_offset, y_pos, 0),
        wood_dark
    )
    planks.append(plank)

# Corner posts (vertical edges)
post_size = 0.06
corner_positions = [
    (crate_w / 2, crate_h / 2, 0),
    (crate_w / 2, -crate_h / 2, 0),
    (-crate_w / 2, crate_h / 2, 0),
    (-crate_w / 2, -crate_h / 2, 0),
]

for pos in corner_positions:
    post = create_plank(
        post_size, post_size, crate_d,
        pos,
        wood_dark
    )
    planks.append(post)

# Horizontal corner braces
brace_size = 0.05
# Top and bottom horizontal braces on each face
for x in [crate_w / 2, -crate_w / 2]:
    for z in [crate_d / 2 - brace_size / 2, -crate_d / 2 + brace_size / 2]:
        brace = create_plank(
            brace_size, crate_h, brace_size,
            (x, 0, z),
            wood_dark
        )
        planks.append(brace)

for y in [crate_h / 2, -crate_h / 2]:
    for z in [crate_d / 2 - brace_size / 2, -crate_d / 2 + brace_size / 2]:
        brace = create_plank(
            crate_w, brace_size, brace_size,
            (0, y, z),
            wood_dark
        )
        planks.append(brace)

# Add slight random rotation to planks for natural look
for plank in planks:
    plank.rotation_euler.x += random.uniform(-0.01, 0.01)
    plank.rotation_euler.y += random.uniform(-0.01, 0.01)

# Add a simple light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Set up camera
bpy.ops.object.camera_add(location=(2.5, -2.5, 2.0))
cam = bpy.context.active_object
bpy.ops.object.select_all(action='DESELECT')
cam.select_set(True)
bpy.context.view_layer.objects.active = cam
bpy.ops.object.camera_set_active()

# Point camera at origin
direction = (0, 0, 0) - cam.location
cam.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1024
bpy.context.scene.render.resolution_y = 1024
