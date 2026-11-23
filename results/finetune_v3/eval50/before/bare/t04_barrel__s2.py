import bpy
import math
import random

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Create Barrel Geometry ---
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.5,
    depth=1.2,
    vertices=32,
    location=(0, 0, 0.6)
)
barrel = bpy.context.active_object
barrel.name = "RustyBarrel"

# Apply slight taper and curvature to make it look like a barrel
# We'll use a simple approach: scale the middle vertices slightly
mesh = barrel.data
for vertex in mesh.vertices:
    # vertex.z is from -0.6 to 0.6
    # We want to bulge the middle
    t = abs(vertex.z) / 0.6  # 0 at middle, 1 at top/bottom
    # Use a curve: 1 - t^2 gives 1 at middle, 0 at ends
    # Scale factor: 1 + 0.15 * (1 - t^2)
    scale_factor = 1 + 0.15 * (1 - t * t)
    vertex.x *= scale_factor
    vertex.y *= scale_factor

# Recalculate normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# --- Create Rusty Metal Material ---
mat = bpy.data.materials.new(name="RustyMetal")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
nodes.clear()

# Create nodes
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (600, 0)

bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (300, 0)

# Texture coordinates
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-600, 0)

# Noise texture for rust pattern
noise = nodes.new('ShaderNodeTexNoise')
noise.location = (-400, 100)
noise.inputs['Scale'].default_value = 8.0
noise.inputs['Detail'].default_value = 8.0
noise.inputs['Roughness'].default_value = 0.6

# Color ramp to create rust patches
ramp = nodes.new('ShaderNodeValToRGB')
ramp.location = (-200, 100)
ramp.color_ramp.elements[0].position = 0.35
ramp.color_ramp.elements[0].color = (0.15, 0.05, 0.02, 1.0)  # Dark rust
ramp.color_ramp.elements[1].position = 0.65
ramp.color_ramp.elements[1].color = (0.4, 0.2, 0.1, 1.0)  # Lighter rust

# Metal base color (dark metal)
mix_color = nodes.new('ShaderNodeMixRGB')
mix_color.location = (0, 0)
mix_color.blend_type = 'MIX'
mix_color.inputs['Color1'].default_value = (0.05, 0.05, 0.05, 1.0)  # Dark metal
mix_color.inputs['Color2'].default_value = (0.4, 0.2, 0.1, 1.0)  # Rust color

# Connect nodes
links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
links.new(ramp.outputs['Color'], mix_color.inputs['Color2'])
links.new(mix_color.outputs['Color'], bsdf.inputs['Base Color'])

# Roughness: rust is rougher than metal
noise_rough = nodes.new('ShaderNodeTexNoise')
noise_rough.location = (-400, -200)
noise_rough.inputs['Scale'].default_value = 10.0
noise_rough.inputs['Detail'].default_value = 6.0

ramp_rough = nodes.new('ShaderNodeValToRGB')
ramp_rough.location = (-200, -200)
ramp_rough.color_ramp.elements[0].position = 0.3
ramp_rough.color_ramp.elements[0].color = (0.9, 0.9, 0.9, 1.0)  # Rough (rust)
ramp_rough.color_ramp.elements[1].position = 0.7
ramp_rough.color_ramp.elements[1].color = (0.3, 0.3, 0.3, 1.0)  # Smoother (metal)

links.new(tex_coord.outputs['Object'], noise_rough.inputs['Vector'])
links.new(noise_rough.outputs['Fac'], ramp_rough.inputs['Fac'])
links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])

# Metallic: rust is less metallic
ramp_metal = nodes.new('ShaderNodeValToRGB')
ramp_metal.location = (-200, -400)
ramp_metal.color_ramp.elements[0].position = 0.4
ramp_metal.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)  # Non-metallic (rust)
ramp_metal.color_ramp.elements[1].position = 0.7
ramp_metal.color_ramp.elements[1].color = (0.8, 0.8, 0.8, 1.0)  # Metallic

links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
links.new(noise.outputs['Fac'], ramp_metal.inputs['Fac'])
links.new(ramp_metal.outputs['Color'], bsdf.inputs['Metallic'])

# Bump for surface detail
bump = nodes.new('ShaderNodeBump')
bump.location = (0, -500)
bump.inputs['Strength'].default_value = 0.3

noise_bump = nodes.new('ShaderNodeTexNoise')
noise_bump.location = (-400, -600)
noise_bump.inputs['Scale'].default_value = 20.0
noise_bump.inputs['Detail'].default_value = 10.0

links.new(tex_coord.outputs['Object'], noise_bump.inputs['Vector'])
links.new(noise_bump.outputs['Fac'], bump.inputs['Height'])
links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

# Connect BSDF to output
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material
barrel.data.materials.append(mat)

# --- Add some horizontal bands (rusty metal rings) ---
for i, z_pos in enumerate([-0.4, 0.0, 0.4]):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.52,
        minor_radius=0.02,
        major_segments=32,
        minor_segments=8,
        location=(0, 0, z_pos)
    )
    band = bpy.context.active_object
    band.name = f"BarrelBand_{i}"
    band.data.materials.append(mat)

# --- Add a lid ---
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.52,
    depth=0.03,
    vertices=32,
    location=(0, 0, 1.215)
)
lid = bpy.context.active_object
lid.name = "BarrelLid"
lid.data.materials.append(mat)

# --- Add a base ---
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.52,
    depth=0.03,
    vertices=32,
    location=(0, 0, -0.015)
)
base = bpy.context.active_object
base.name = "BarrelBase"
base.data.materials.append(mat)

# --- Set up lighting ---
# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a fill light
bpy.ops.object.light_add(type='POINT', location=(-3, -3, 3))
fill = bpy.context.active_object
fill.data.energy = 100
fill.data.color = (1.0, 0.9, 0.8)

# Set up camera
bpy.ops.object.camera_add(location=(2.5, -2.5, 1.5))
camera = bpy.context.active_object
camera.name = "BarrelCamera"

# Point camera at barrel
direction = (0, 0, 0.6) - camera.location
camera.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()

# Set camera as active
bpy.context.scene.camera = camera

# Set render resolution
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720

# Set background color
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.1, 0.1, 0.12, 1.0)
    bg_node.inputs[1].default_value = 1.0

print("Rusty metal barrel created successfully!")
