import bpy
import bmesh
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a base icosphere and subdivide
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0, location=(0, 0, 0))
rock = bpy.context.active_object
rock.name = "LavaRock"

# Displace vertices for rocky look
bm = bmesh.new()
bm.from_mesh(rock.data)

random.seed(42)
for vert in bm.verts:
    # Noise-like displacement using pseudo-random based on position
    noise_val = (
        math.sin(vert.co.x * 3.7) * math.cos(vert.co.y * 4.1) * math.sin(vert.co.z * 2.9) +
        math.sin(vert.co.x * 7.3 + vert.co.y * 5.1) * 0.5 +
        math.cos(vert.co.z * 6.7 + vert.co.x * 3.3) * 0.3
    )
    vert.co += vert.co.normalized() * noise_val * 0.15

bm.to_mesh(rock.data)
bm.free()

# Add subdivision surface for smoother base
mod = rock.modifiers.new("Subsurf", 'SUBSURF')
mod.levels = 2
mod.render_levels = 2

# Create crack texture using a procedural approach with a second mesh
# We'll create glowing cracks using a separate material with emission

# Create material for the rock
mat_rock = bpy.data.materials.new("LavaRockMat")
mat_rock.use_nodes = True
nodes = mat_rock.node_tree.nodes
links = mat_rock.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Output
out_node = nodes.new("ShaderNodeOutputMaterial")
out_node.location = (600, 0)

# Mix shader for rock and cracks
mix_node = nodes.new("ShaderNodeMixShader")
mix_node.location = (400, 0)

# Rock diffuse (dark, rough)
rock_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
rock_bsdf.location = (200, 100)
rock_bsdf.inputs["Base Color"].default_value = (0.05, 0.03, 0.02, 1.0)
rock_bsdf.inputs["Roughness"].default_value = 0.9
rock_bsdf.inputs["Metallic"].default_value = 0.0

# Crack emission (orange-red glow)
crack_emission = nodes.new("ShaderNodeEmission")
crack_emission.location = (200, -100)
crack_emission.inputs["Color"].default_value = (1.0, 0.2, 0.05, 1.0)
crack_emission.inputs["Strength"].default_value = 5.0

# Noise texture for cracks
noise_node = nodes.new("ShaderNodeTexNoise")
noise_node.location = (-200, 0)
noise_node.inputs["Scale"].default_value = 4.0
noise_node.inputs["Detail"].default_value = 8.0
noise_node.inputs["Roughness"].default_value = 0.6
noise_node.inputs["Lacunarity"].default_value = 2.0

# ColorRamp to threshold the noise into cracks
ramp_node = nodes.new("ShaderNodeValToRGB")
ramp_node.location = (0, 0)
ramp_node.color_ramp.elements[0].position = 0.45
ramp_node.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp_node.color_ramp.elements[1].position = 0.55
ramp_node.color_ramp.elements[1].color = (1, 1, 1, 1)

# Connect noise to ramp
links.new(noise_node.outputs["Fac"], ramp_node.inputs["Fac"])

# Connect ramp to mix shader factor
links.new(ramp_node.outputs["Color"], mix_node.inputs["Fac"])

# Connect rock and crack shaders to mix
links.new(rock_bsdf.outputs["BSDF"], mix_node.inputs[1])
links.new(crack_emission.outputs["Emission"], mix_node.inputs[2])

# Connect mix to output
links.new(mix_node.outputs["Shader"], out_node.inputs["Surface"])

# Assign material to rock
rock.data.materials.append(mat_rock)

# Add a point light inside the rock for extra glow effect
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
light = bpy.context.active_object
light.name = "LavaGlow"
light.data.color = (1.0, 0.3, 0.1)
light.data.energy = 50
light.data.shadow_soft_size = 0.5

# Add a subtle ambient light
bpy.ops.object.light_add(type='AREA', location=(0, 0, 3))
area_light = bpy.context.active_object
area_light.name = "Ambient"
area_light.data.energy = 20
area_light.data.color = (0.5, 0.4, 0.3)
area_light.data.size = 5

# Set up camera
bpy.ops.object.camera_add(location=(3, -3, 2), rotation=(math.radians(60), 0, math.radians(45)))
camera = bpy.context.active_object
bpy.context.scene.camera = camera

# Set world background to dark
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.01, 0.01, 0.01, 1.0)
    bg_node.inputs["Strength"].default_value = 1.0

print("Lava rock with glowing cracks created successfully!")
