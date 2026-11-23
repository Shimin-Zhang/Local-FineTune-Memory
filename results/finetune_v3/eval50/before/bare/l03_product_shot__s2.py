import bpy
import math

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create white background (large plane)
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
bg_plane = bpy.context.active_object
bg_plane.name = "Background"

# White material for background
mat_bg = bpy.data.materials.new(name="WhiteBG")
mat_bg.use_nodes = True
nodes = mat_bg.node_tree.nodes
links = mat_bg.node_tree.links
nodes.clear()
bsdf = nodes.new('ShaderNodeBsdfDiffuse')
bsdf.inputs[0].default_value = (1, 1, 1, 1)
output = nodes.new('ShaderNodeOutputMaterial')
links.new(bsdf.outputs[0], output.inputs[0])
bg_plane.data.materials.append(mat_bg)

# Create perfume bottle (cylinder body)
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=2.0, location=(0, 0, 1.0), vertices=64)
bottle = bpy.context.active_object
bottle.name = "PerfumeBottle"

# Glass material for bottle
mat_glass = bpy.data.materials.new(name="Glass")
mat_glass.use_nodes = True
nodes = mat_glass.node_tree.nodes
links = mat_glass.node_tree.links
nodes.clear()
transmission = nodes.new('ShaderNodeBsdfGlass')
transmission.inputs[0].default_value = (1, 1, 1, 1)
transmission.inputs[1].default_value = 1.5
transmission.inputs[2].default_value = 0.001
output = nodes.new('ShaderNodeOutputMaterial')
links.new(transmission.outputs[0], output.inputs[0])
bottle.data.materials.append(mat_glass)

# Add liquid inside (slightly smaller cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=1.4, location=(0, 0, 0.7), vertices=64)
liquid = bpy.context.active_object
liquid.name = "Liquid"

mat_liquid = bpy.data.materials.new(name="PerfumeLiquid")
mat_liquid.use_nodes = True
nodes = mat_liquid.node_tree.nodes
links = mat_liquid.node_tree.links
nodes.clear()
transmission = nodes.new('ShaderNodeBsdfGlass')
transmission.inputs[0].default_value = (0.9, 0.8, 0.5, 1)
transmission.inputs[1].default_value = 1.33
transmission.inputs[2].default_value = 0.01
output = nodes.new('ShaderNodeOutputMaterial')
links.new(transmission.outputs[0], output.inputs[0])
liquid.data.materials.append(mat_liquid)

# Add cap (smaller cylinder on top)
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=0.5, location=(0, 0, 2.25), vertices=32)
cap = bpy.context.active_object
cap.name = "Cap"

mat_cap = bpy.data.materials.new(name="CapMetal")
mat_cap.use_nodes = True
nodes = mat_cap.node_tree.nodes
links = mat_cap.node_tree.links
nodes.clear()
metal = nodes.new('ShaderNodeBsdfPrincipled')
metal.inputs[0].default_value = (0.8, 0.8, 0.8, 1)
metal.inputs[1].default_value = 0.0
metal.inputs[2].default_value = 0.9
output = nodes.new('ShaderNodeOutputMaterial')
links.new(metal.outputs[0], output.inputs[0])
cap.data.materials.append(mat_cap)

# Soft light from above (area light)
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
light = bpy.context.active_object
light.name = "SoftTopLight"
light.data.energy = 200
light.data.size = 3.0
light.data.shape = 'SQUARE'

# Add a subtle fill light from the side
bpy.ops.object.light_add(type='AREA', location=(3, 2, 2))
fill_light = bpy.context.active_object
fill_light.name = "FillLight"
fill_light.data.energy = 50
fill_light.data.size = 2.0
fill_light.data.shape = 'SQUARE'
fill_light.rotation_euler = (math.radians(45), 0, math.radians(-30))

# Camera looking slightly down at the bottle
bpy.ops.object.camera_add(location=(0, 4, 2.5))
camera = bpy.context.active_object
camera.name = "ProductCamera"

# Aim camera at the bottle (slightly down)
target = bpy.data.objects.get("PerfumeBottle")
direction = target.location - camera.location
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set camera as active
bpy.context.scene.camera = camera

# Set up render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Set world to white
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world_node = world.node_tree.nodes
world_node.clear()
bg = world_node.new('ShaderNodeBackground')
bg.inputs[0].default_value = (1, 1, 1, 1)
bg.inputs[1].default_value = 1.0
output = world_node.new('ShaderNodeOutputWorld')
world_node.links.new(bg.outputs[0], output.inputs[0])
