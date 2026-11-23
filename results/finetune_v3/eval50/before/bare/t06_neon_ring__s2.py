import bpy
import math

# Clean the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove default camera if exists, then set up camera
for obj in list(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Create dark floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "DarkFloor"

# Create floor material (dark)
floor_mat = bpy.data.materials.new(name="DarkFloorMat")
floor_mat.use_nodes = True
nodes = floor_mat.node_tree.nodes
links = floor_mat.node_tree.links
nodes.clear()

out_node = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf.inputs['Roughness'].default_value = 0.8
bsdf.inputs['Metallic'].default_value = 0.0
links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
floor.data.materials.append(floor_mat)

# Create neon ring (torus)
bpy.ops.mesh.primitive_torus_add(
    major_radius=2.0,
    minor_radius=0.1,
    major_segments=64,
    minor_segments=16,
    location=(0, 0, 3.0)
)
ring = bpy.context.active_object
ring.name = "NeonRing"

# Create neon material with emission
neon_mat = bpy.data.materials.new(name="NeonMat")
neon_mat.use_nodes = True
nodes = neon_mat.node_tree.nodes
links = neon_mat.node_tree.links
nodes.clear()

out_node = nodes.new('ShaderNodeOutputMaterial')
emission = nodes.new('ShaderNodeEmission')
emission.inputs['Color'].default_value = (0.0, 0.8, 1.0, 1.0)  # Cyan neon
emission.inputs['Strength'].default_value = 15.0
links.new(emission.outputs['Emission'], out_node.inputs['Surface'])
ring.data.materials.append(neon_mat)

# Add a point light inside the ring to enhance glow effect
bpy.ops.object.light_add(type='POINT', location=(0, 0, 3.0))
light = bpy.context.active_object
light.name = "NeonLight"
light.data.energy = 50
light.data.color = (0.0, 0.8, 1.0)
light.data.shadow_soft_size = 0.5

# Add world with very dark background
world = bpy.data.worlds.new("DarkWorld")
bpy.context.scene.world = world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links
world_nodes.clear()

out_world = world_nodes.new('ShaderNodeOutputWorld')
bg = world_nodes.new('ShaderNodeBackground')
bg.inputs['Color'].default_value = (0.005, 0.005, 0.005, 1.0)
bg.inputs['Strength'].default_value = 1.0
world_links.new(bg.outputs['Background'], out_world.inputs['Surface'])

# Set up camera
bpy.ops.object.camera_add(location=(0, -8, 4), rotation=(math.radians(80), 0, 0))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Enable bloom for glow effect (using compositor)
scene = bpy.context.scene
scene.use_nodes = True
comp_nodes = scene.node_tree.nodes
comp_links = scene.node_tree.links
comp_nodes.clear()

render_out = comp_nodes.new('CompositorNodeComposite')
glare = comp_nodes.new('CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.quality = 'HIGH'
glare.threshold = 0.5
glare.size = 8
comp_links.new(scene.node_tree.nodes['Render Layers'].outputs['Image'], glare.inputs['Image'])
comp_links.new(glare.outputs['Image'], render_out.inputs['Image'])

# Set render engine to Cycles for better glow
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
