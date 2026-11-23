import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a plain white background plane
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
bg = bpy.context.active_object
bg.name = "Background"

# White material for background
mat_bg = bpy.data.materials.new("WhiteBG")
mat_bg.use_nodes = True
nodes = mat_bg.node_tree.nodes
links = mat_bg.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
bsdf.inputs["Roughness"].default_value = 0.8
bg.data.materials.append(mat_bg)

# Create the perfume bottle (simplified: cylinder + sphere cap)
# Bottle body
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.2, location=(0, 0, 0.6))
bottle = bpy.context.active_object
bottle.name = "Bottle"

# Glass material
mat_glass = bpy.data.materials.new("Glass")
mat_glass.use_nodes = True
nodes_g = mat_glass.node_tree.nodes
links_g = mat_glass.node_tree.links
bsdf_g = nodes_g["Principled BSDF"]
bsdf_g.inputs["Base Color"].default_value = (1.0, 1.0, 1.0, 1.0)
bsdf_g.inputs["Roughness"].default_value = 0.0
bsdf_g.inputs["Transmission Weight"].default_value = 1.0
bsdf_g.inputs["IOR"].default_value = 1.5
bottle.data.materials.append(mat_glass)

# Cap (sphere)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 1.35))
cap = bpy.context.active_object
cap.name = "Cap"

# Gold material for cap
mat_gold = bpy.data.materials.new("Gold")
mat_gold.use_nodes = True
nodes_gold = mat_gold.node_tree.nodes
bsdf_gold = nodes_gold["Principled BSDF"]
bsdf_gold.inputs["Base Color"].default_value = (1.0, 0.84, 0.0, 1.0)
bsdf_gold.inputs["Metallic"].default_value = 1.0
bsdf_gold.inputs["Roughness"].default_value = 0.2
cap.data.materials.append(mat_gold)

# Neck
bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=0.3, location=(0, 0, 1.2))
neck = bpy.context.active_object
neck.name = "Neck"
neck.data.materials.append(mat_glass)

# Soft area light from above
bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
light = bpy.context.active_object
light.name = "SoftLight"
light.data.energy = 200
light.data.size = 3.0
light.data.shape = 'DISK'
# Point it down
light.rotation_euler = (0, 0, 0)

# Add a subtle fill light
bpy.ops.object.light_add(type='AREA', location=(2, 2, 3))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 50
fill.data.size = 2.0
fill.data.shape = 'DISK'
fill.rotation_euler = (math.radians(45), 0, math.radians(-45))

# Camera looking slightly down at the bottle
bpy.ops.object.camera_add(location=(0, -3, 2))
cam = bpy.context.active_object
cam.name = "Camera"
# Point camera at the bottle center
direction = (0, 0, 0.6) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# Set up world for soft ambient
world = bpy.context.scene.world
world.use_nodes = True
world_node_tree = world.node_tree
bg_node = world_node_tree.nodes["Background"]
bg_node.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)
bg_node.inputs[1].default_value = 0.3

# Render settings
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.filepath = "/tmp/perfume_shot.png"
