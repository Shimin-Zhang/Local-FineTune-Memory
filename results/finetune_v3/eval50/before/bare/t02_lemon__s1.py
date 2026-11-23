import bpy
import math

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a UV sphere for the lemon base
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32, location=(0, 0, 0))
lemon = bpy.context.active_object
lemon.name = "Lemon"

# Scale to lemon shape (elongated)
lemon.scale = (1.0, 1.0, 1.4)
bpy.ops.object.transform_apply(scale=True)

# Add a slight pointy tip at top and bottom by moving vertices
for vertex in lemon.data.vertices:
    # Stretch the top and bottom slightly to create pointed ends
    if vertex.co.z > 0.9:
        vertex.co.x *= 0.7
        vertex.co.y *= 0.7
        vertex.co.z *= 1.15
    elif vertex.co.z < -0.9:
        vertex.co.x *= 0.7
        vertex.co.y *= 0.7
        vertex.co.z *= 1.15

# Recalculate normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Add Subdivision Surface modifier for smoothness before bump
subsurf = lemon.modifiers.new(name="Subdivision", type='SUBSURF')
subsurf.levels = 3
subsurf.render_levels = 4

# Create a new material for the lemon
material = bpy.data.materials.new(name="LemonMaterial")
material.use_nodes = True

nodes = material.node_tree.nodes
links = material.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Create nodes
output_node = nodes.new(type='ShaderNodeOutputMaterial')
output_node.location = (600, 0)

diffuse_node = nodes.new(type='ShaderNodeBsdfPrincipled')
diffuse_node.location = (300, 0)

# Set lemon color (bright yellow)
diffuse_node.inputs['Base Color'].default_value = (0.9, 0.85, 0.1, 1.0)
diffuse_node.inputs['Roughness'].default_value = 0.5

# Create noise texture for bumpy skin
noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.location = (-200, 0)
noise_node.inputs['Scale'].default_value = 80.0
noise_node.inputs['Detail'].default_value = 10.0
noise_node.inputs['Roughness'].default_value = 0.7
noise_node.inputs['Distortion'].default_value = 0.3

# Create a second noise for larger bumps
noise_large_node = nodes.new(type='ShaderNodeTexNoise')
noise_large_node.location = (-200, -200)
noise_large_node.inputs['Scale'].default_value = 15.0
noise_large_node.inputs['Detail'].default_value = 6.0
noise_large_node.inputs['Roughness'].default_value = 0.5
noise_large_node.inputs['Distortion'].default_value = 0.2

# Mix the two noise textures
mix_node = nodes.new(type='ShaderNodeMix')
mix_node.location = (0, -100)
mix_node.data_type = 'FLOAT'
mix_node.inputs['Factor'].default_value = 0.5

# Link noise textures to mix
links.new(noise_node.outputs['Fac'], mix_node.inputs['A'])
links.new(noise_large_node.outputs['Fac'], mix_node.inputs['B'])

# Create bump node
bump_node = nodes.new(type='ShaderNodeBump')
bump_node.location = (100, -200)
bump_node.inputs['Strength'].default_value = 0.4
bump_node.inputs['Distance'].default_value = 0.05

# Link mix to bump
links.new(mix_node.outputs['Result'], bump_node.inputs['Height'])

# Link bump to material output
links.new(bump_node.outputs['Normal'], diffuse_node.inputs['Normal'])
links.new(diffuse_node.outputs['BSDF'], output_node.inputs['Surface'])

# Assign material to lemon
lemon.data.materials.append(material)

# Add slight random displacement for more organic feel using a displace modifier
# First, we need a texture for displacement
displace_texture = bpy.data.textures.new(name="LemonBump", type='CLOUDS')
displace_texture.noise_scale = 0.3
displace_texture.noise_depth = 3

displace = lemon.modifiers.new(name="Displace", type='DISPLACE')
displace.texture = displace_texture
displace.strength = 0.08
displace.mid_level = 0.5
displace.direction = 'NORMAL'

# Set up lighting for better visualization
# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a point light for fill
bpy.ops.object.light_add(type='POINT', location=(-3, -3, 5))
point_light = bpy.context.active_object
point_light.data.energy = 100.0

# Set up camera
bpy.ops.object.camera_add(location=(0, -4, 1.5))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.camera = camera

# Set viewport shading to material preview
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].shading.type = 'MATERIAL'

print("Lemon with bumpy texture created successfully!")
