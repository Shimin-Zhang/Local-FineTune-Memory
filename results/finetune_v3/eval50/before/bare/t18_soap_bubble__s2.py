import bpy
import math

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=64, location=(0, 0, 0))
bubble = bpy.context.active_object
bpy.ops.object.shade_smooth()

# Create a new material
mat = bpy.data.materials.new(name="BubbleMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
# Output
output_node = nodes.new('ShaderNodeOutputMaterial')
output_node.location = (600, 0)

# Principled BSDF
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (300, 0)
bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)
bsdf.inputs['Metallic'].default_value = 0.0
bsdf.inputs['Roughness'].default_value = 0.0
bsdf.inputs['IOR'].default_value = 1.33  # Water-like IOR
bsdf.inputs['Transmission Weight'].default_value = 1.0
bsdf.inputs['Coat Weight'].default_value = 1.0
bsdf.inputs['Coat Roughness'].default_value = 0.0
bsdf.inputs['Coat IOR'].default_value = 1.5

# Texture Coordinate
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-600, 0)

# Mapping
mapping = nodes.new('ShaderNodeMapping')
mapping.location = (-400, 0)

# ColorRamp for rainbow
color_ramp = nodes.new('ShaderNodeValToRGB')
color_ramp.location = (-200, 0)

# Set up rainbow gradient
color_ramp.color_ramp.interpolation = 'LINEAR'
# Add color stops for rainbow
cr = color_ramp.color_ramp
# Clear existing elements
while len(cr.elements) > 0:
    cr.elements.remove(cr.elements[0])

# Add rainbow colors (ROYGBIV)
rainbow_colors = [
    (0.0, (1.0, 0.0, 0.0, 1.0)),   # Red
    (0.17, (1.0, 0.5, 0.0, 1.0)),  # Orange
    (0.33, (1.0, 1.0, 0.0, 1.0)),  # Yellow
    (0.5, (0.0, 1.0, 0.0, 1.0)),   # Green
    (0.67, (0.0, 0.5, 1.0, 1.0)),  # Cyan
    (0.83, (0.0, 0.0, 1.0, 1.0)),  # Blue
    (1.0, (0.5, 0.0, 1.0, 1.0)),   # Violet
]

for pos, color in rainbow_colors:
    elem = cr.elements.new(pos)
    elem.color = color

# Separate XYZ to get angle
sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
sep_xyz.location = (-400, -200)

# Math node to compute angle from normal
# Use the Y and X components of the normal to create an angle
math_acos = nodes.new('ShaderNodeMath')
math_acos.operation = 'ARCTAN2'
math_acos.location = (-200, -200)

# Math node to map to 0-1 range
math_map = nodes.new('ShaderNodeMath')
math_map.operation = 'MULTIPLY_ADD'
math_map.location = (0, -200)
math_map.inputs[1].default_value = 1.0 / (2 * math.pi)
math_map.inputs[2].default_value = 0.5

# Link nodes
# TexCoord -> Mapping
links.new(tex_coord.outputs['Normal'], mapping.inputs['Vector'])

# Mapping -> Separate XYZ
links.new(mapping.outputs['Vector'], sep_xyz.inputs['Vector'])

# Separate XYZ Y and X -> Arctan2
links.new(sep_xyz.outputs['Y'], math_acos.inputs[0])
links.new(sep_xyz.outputs['X'], math_acos.inputs[1])

# Arctan2 -> Map Range
links.new(math_acos.outputs['Value'], math_map.inputs[0])

# Map Range -> ColorRamp
links.new(math_map.outputs['Value'], color_ramp.inputs['Fac'])

# ColorRamp -> Base Color
links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])

# BSDF -> Output
links.new(bsdf.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to bubble
bubble.data.materials.append(mat)

# Add a world with some lighting
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

# Clear world nodes
for node in world_nodes:
    world_nodes.remove(node)

# Background
bg_node = world_nodes.new('ShaderNodeBackground')
bg_node.location = (0, 0)
bg_node.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)
bg_node.inputs['Strength'].default_value = 1.0

# World Output
world_output = world_nodes.new('ShaderNodeOutputWorld')
world_output.location = (200, 0)

world_links.new(bg_node.outputs['Background'], world_output.inputs['Surface'])

# Add a sun light for better reflections
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Add a point light for extra sparkle
bpy.ops.object.light_add(type='POINT', location=(-3, -3, 5))
point_light = bpy.context.active_object
point_light.data.energy = 100.0

# Set up camera
bpy.ops.object.camera_add(location=(0, -4, 1))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
