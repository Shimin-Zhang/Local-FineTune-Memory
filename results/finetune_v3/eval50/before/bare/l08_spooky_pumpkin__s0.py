import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a pumpkin (using a UV sphere, scaled to look like a pumpkin)
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=32, ring_count=16, location=(0, 0, 0.5))
pumpkin = bpy.context.active_object
pumpkin.name = "Pumpkin"

# Scale to make it pumpkin-shaped (wider than tall)
pumpkin.scale = (1.2, 1.2, 0.8)

# Add a pumpkin material (orange)
pumpkin_material = bpy.data.materials.new(name="PumpkinMaterial")
pumpkin_material.use_nodes = True
bsdf = pumpkin_material.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.3, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6
pumpkin.data.materials.append(pumpkin_material)

# Add a stem on top
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.3, location=(0, 0, 1.2))
stem = bpy.context.active_object
stem.name = "Stem"
stem.scale = (1, 1, 1)

# Stem material (dark green/brown)
stem_material = bpy.data.materials.new(name="StemMaterial")
stem_material.use_nodes = True
bsdf_stem = stem_material.node_tree.nodes["Principled BSDF"]
bsdf_stem.inputs["Base Color"].default_value = (0.1, 0.2, 0.05, 1.0)
bsdf_stem.inputs["Roughness"].default_value = 0.8
stem.data.materials.append(stem_material)

# Add a ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Ground material (dark, spooky)
ground_material = bpy.data.materials.new(name="GroundMaterial")
ground_material.use_nodes = True
bsdf_ground = ground_material.node_tree.nodes["Principled BSDF"]
bsdf_ground.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1.0)
bsdf_ground.inputs["Roughness"].default_value = 0.9
ground.data.materials.append(ground_material)

# Add a green point light below the pumpkin
bpy.ops.object.light_add(type='POINT', location=(0, 0, 0.05))
green_light = bpy.context.active_object
green_light.name = "GreenLight"
green_light.data.color = (0.0, 1.0, 0.0)  # Green
green_light.data.energy = 50.0
green_light.data.shadow_soft_size = 0.1

# Set up camera
bpy.ops.object.camera_add(location=(0, -4, 1.5))
camera = bpy.context.active_object
camera.name = "Camera"

# Point camera at the pumpkin
direction = (0, 0, 0.5) - camera.location
rot_quat = direction.to_track_quat('Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# Set camera as active
bpy.context.scene.camera = camera

# Set world to dark (spooky atmosphere)
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes["Background"]
bg_node.inputs["Color"].default_value = (0.0, 0.0, 0.0, 1.0)
bg_node.inputs["Strength"].default_value = 0.0

# Enable some ambient occlusion for extra spookiness
bpy.context.scene.cycles.use_denoising = True
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

print("Spooky pumpkin scene set up!")
