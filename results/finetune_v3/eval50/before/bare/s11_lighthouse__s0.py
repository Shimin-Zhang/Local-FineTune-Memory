import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create the lighthouse base (cylinder)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=2, depth=10, location=(0, 0, 5))
lighthouse = bpy.context.active_object
lighthouse.name = "Lighthouse"

# Create red and white bands using a material with procedural texture
# First, let's create a material for the banded lighthouse
mat = bpy.data.materials.new(name="LighthouseBands")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output = nodes.new('ShaderNodeOutputMaterial')
output.location = (600, 0)

# Use a wave texture to create bands
tex_coord = nodes.new('ShaderNodeTexCoord')
tex_coord.location = (-400, 0)

# Separate XYZ to get Z coordinate
sep_xyz = nodes.new('ShaderNodeSeparateXYZ')
sep_xyz.location = (-200, 0)

# Math node to create bands (sine wave)
math1 = nodes.new('ShaderNodeMath')
math1.operation = 'MULTIPLY'
math1.inputs[1].default_value = 0.5  # Frequency of bands
math1.location = (0, 0)

# Math node to create step function (0 or 1)
math2 = nodes.new('ShaderNodeMath')
math2.operation = 'GREATER_THAN'
math2.inputs[1].default_value = 0.0
math2.location = (200, 0)

# Mix color between red and white
mix = nodes.new('ShaderNodeMixRGB')
mix.location = (400, 0)
mix.inputs[1].default_value = (1.0, 0.0, 0.0, 1.0)  # Red
mix.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)  # White

# Principled BSDF
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.location = (400, -200)

# Link nodes
links.new(tex_coord.outputs['Object'], sep_xyz.inputs['Vector'])
links.new(sep_xyz.outputs['Z'], math1.inputs[0])
links.new(math1.outputs['Value'], math2.inputs[0])
links.new(math2.outputs['Value'], mix.inputs['Fac'])
links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Assign material to lighthouse
lighthouse.data.materials.append(mat)

# Create the top of the lighthouse (lamp room)
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.5, depth=2, location=(0, 0, 11))
lamp_room = bpy.context.active_object
lamp_room.name = "LampRoom"

# Create a glass material for the lamp room
glass_mat = bpy.data.materials.new(name="Glass")
glass_mat.use_nodes = True
glass_nodes = glass_mat.node_tree.nodes
glass_links = glass_mat.node_tree.links

# Clear default nodes
for node in glass_nodes:
    glass_nodes.remove(node)

# Create nodes for glass
glass_output = glass_nodes.new('ShaderNodeOutputMaterial')
glass_output.location = (300, 0)

glass_bsdf = glass_nodes.new('ShaderNodeBsdfGlass')
glass_bsdf.location = (100, 0)
glass_bsdf.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
glass_bsdf.inputs['Roughness'].default_value = 0.0
glass_bsdf.inputs['IOR'].default_value = 1.45

glass_links.new(glass_bsdf.outputs['BSDF'], glass_output.inputs['Surface'])

lamp_room.data.materials.append(glass_mat)

# Create the roof (cone)
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=1.8, radius2=0, depth=2, location=(0, 0, 13))
roof = bpy.context.active_object
roof.name = "Roof"

# Create a dark material for the roof
roof_mat = bpy.data.materials.new(name="RoofDark")
roof_mat.use_nodes = True
roof_nodes = roof_mat.node_tree.nodes
roof_links = roof_mat.node_tree.links

for node in roof_nodes:
    roof_nodes.remove(node)

roof_output = roof_nodes.new('ShaderNodeOutputMaterial')
roof_output.location = (300, 0)

roof_bsdf = roof_nodes.new('ShaderNodeBsdfPrincipled')
roof_bsdf.location = (100, 0)
roof_bsdf.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1.0)
roof_bsdf.inputs['Roughness'].default_value = 0.5

roof_links.new(roof_bsdf.outputs['BSDF'], roof_output.inputs['Surface'])

roof.data.materials.append(roof_mat)

# Add a light source inside the lamp room
bpy.ops.object.light_add(type='POINT', location=(0, 0, 11))
light = bpy.context.active_object
light.name = "LighthouseLight"
light.data.energy = 100
light.data.color = (1.0, 1.0, 0.8)

# Add a camera
bpy.ops.object.camera_add(location=(15, 15, 8), rotation=(math.radians(60), 0, math.radians(45)))
camera = bpy.context.active_object
camera.name = "Camera"

# Set the camera as the active camera
bpy.context.scene.camera = camera

# Add a ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Create a simple ground material
ground_mat = bpy.data.materials.new(name="Ground")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_links = ground_mat.node_tree.links

for node in ground_nodes:
    ground_nodes.remove(node)

ground_output = ground_nodes.new('ShaderNodeOutputMaterial')
ground_output.location = (300, 0)

ground_bsdf = ground_nodes.new('ShaderNodeBsdfPrincipled')
ground_bsdf.location = (100, 0)
ground_bsdf.inputs['Base Color'].default_value = (0.3, 0.3, 0.3, 1.0)
ground_bsdf.inputs['Roughness'].default_value = 0.8

ground_links.new(ground_bsdf.outputs['BSDF'], ground_output.inputs['Surface'])

ground.data.materials.append(ground_mat)

print("Lighthouse with red and white bands created successfully!")
