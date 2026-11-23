import bpy
import math
import random

# Clean up default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create UV Sphere (lemon base)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=64, ring_count=32, location=(0, 0, 0))
lemon = bpy.context.active_object
lemon.name = "Lemon"

# Scale to lemon shape (elongated with pointed ends)
lemon.scale = (1.0, 1.0, 0.75)
bpy.ops.object.transform_apply(scale=True)

# Add Displace modifier for bumpy texture
# First create a noise texture
noise_tex = bpy.data.textures.new(name="LemonNoise", type='CLOUDS')
noise_tex.noise_scale = 0.15
noise_tex.noise_depth = 4

# Add Displace modifier
displace_mod = lemon.modifiers.new(name="BumpDisplace", type='DISPLACE')
displace_mod.texture = noise_tex
displace_mod.strength = 0.08
displace_mid_level = 0.5
displace_mod.mid_level = displace_mid_level
displace_mod.direction = 'NORMAL'
displace_mod.texture_coords = 'LOCAL'

# Add another finer noise for micro-bumps
noise_tex2 = bpy.data.textures.new(name="LemonFineNoise", type='CLOUDS')
noise_tex2.noise_scale = 0.05
noise_tex2.noise_depth = 3

displace_mod2 = lemon.modifiers.new(name="FineBump", type='DISPLACE')
displace_mod2.texture = noise_tex2
displace_mod2.strength = 0.03
displace_mod2.mid_level = 0.5
displace_mod2.direction = 'NORMAL'
displace_mod2.texture_coords = 'LOCAL'

# Apply modifiers
bpy.context.view_layer.objects.active = lemon
bpy.ops.object.modifier_apply(modifier="BumpDisplace")
bpy.ops.object.modifier_apply(modifier="FineBump")

# Add slight random vertex displacement for organic feel
random.seed(42)
for vertex in lemon.data.vertices:
    offset = random.uniform(-0.005, 0.005)
    vertex.co.x += offset
    vertex.co.y += offset
    vertex.co.z += offset

# Recalculate normals
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Smooth shading
bpy.ops.object.shade_smooth()

# Add material - lemon yellow with subsurface for realistic look
mat = bpy.data.materials.new(name="LemonMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Principled BSDF
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (200, 0)
bsdf.inputs['Base Color'].default_value = (0.95, 0.85, 0.15, 1.0)  # Lemon yellow
bsdf.inputs['Roughness'].default_value = 0.3
bsdf.inputs['Subsurface Weight'].default_value = 0.1
bsdf.inputs['Subsurface Radius'].default_value = (0.1, 0.08, 0.02)
bsdf.inputs['Subsurface Scale'].default_value = 0.05

# Output
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (500, 0)

# Link
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

# Add bump map for surface detail
bump_node = nodes.new(type='ShaderNodeBump')
bump_node.location = (-100, -200)
bump_node.inputs['Strength'].default_value = 0.3
bump_node.inputs['Distance'].default_value = 0.02

# Noise texture for bump
noise_node = nodes.new(type='ShaderNodeTexNoise')
noise_node.location = (-300, -200)
noise_node.inputs['Scale'].default_value = 50.0
noise_node.inputs['Detail'].default_value = 8.0
noise_node.inputs['Roughness'].default_value = 0.5

# Link noise to bump
links.new(noise_node.outputs['Fac'], bump_node.inputs['Height'])
links.new(bump_node.outputs['Normal'], bsdf.inputs['Normal'])

# Assign material to lemon
lemon.data.materials.append(mat)

# Add a light for better visualization
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Set up camera
bpy.ops.object.camera_add(location=(0, -4, 1.5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.camera = cam

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
