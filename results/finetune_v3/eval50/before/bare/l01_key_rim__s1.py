import bpy
import math
import mathutils

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set world to dark background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links
nodes.clear()
bg = nodes.new('NodeBackground')
bg.inputs[0].default_value = (0.02, 0.02, 0.03, 1.0)
bg.inputs[1].default_value = 1.0
out = nodes.new('NodeOutputWorld')
links.new(bg.outputs[0], out.inputs[0])

# Create floor
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
floor = bpy.context.active_object
floor.name = "Floor"
floor_mat = bpy.data.materials.new("FloorMat")
floor_mat.use_nodes = True
bsdf = floor_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.15, 0.15, 0.15, 1.0)
bsdf.inputs["Roughness"].default_value = 0.6
floor.data.materials.append(floor_mat)

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(-2, 0, 1))
sphere = bpy.context.active_object
sphere.name = "Sphere"
bpy.ops.object.shade_smooth()
sphere_mat = bpy.data.materials.new("SphereMat")
sphere_mat.use_nodes = True
bsdf = sphere_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.8, 0.8, 0.8, 1.0)
bsdf.inputs["Roughness"].default_value = 0.3
sphere.data.materials.append(sphere_mat)

# Create cube
bpy.ops.mesh.primitive_cube_add(size=1.5, location=(0, 0, 0.75))
cube = bpy.context.active_object
cube.name = "Cube"
cube_mat = bpy.data.materials.new("CubeMat")
cube_mat.use_nodes = True
bsdf = cube_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.7, 0.7, 0.7, 1.0)
bsdf.inputs["Roughness"].default_value = 0.4
cube.data.materials.append(cube_mat)

# Create cone
bpy.ops.mesh.primitive_cone_add(radius1=1, radius2=0, depth=2, location=(2, 0, 1))
cone = bpy.context.active_object
cone.name = "Cone"
cone_mat = bpy.data.materials.new("ConeMat")
cone_mat.use_nodes = True
bsdf = cone_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.75, 1.0)
bsdf.inputs["Roughness"].default_value = 0.35
cone.data.materials.append(cone_mat)

# Warm key light from the left (area light)
key_data = bpy.data.lights.new("KeyLight", type='AREA')
key_data.energy = 300
key_data.color = (1.0, 0.85, 0.6)  # warm
key_data.size = 3
key_light = bpy.data.objects.new("KeyLight", key_data)
bpy.context.collection.objects.link(key_light)
key_light.location = (-5, -2, 4)
# Point it toward the objects
direction = mathutils.Vector((0, 0, 1)) - key_light.location
key_light.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Cool blue rim light from behind (area light)
rim_data = bpy.data.lights.new("RimLight", type='AREA')
rim_data.energy = 200
rim_data.color = (0.4, 0.6, 1.0)  # cool blue
rim_data.size = 4
rim_light = bpy.data.objects.new("RimLight", rim_data)
bpy.context.collection.objects.link(rim_light)
rim_light.location = (0, 6, 3)
# Point it toward the objects from behind
direction = mathutils.Vector((0, 0, 1)) - rim_light.location
rim_light.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Set render engine to Cycles for better lighting
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.cycles.device = 'CPU'

# Camera setup
bpy.ops.object.camera_add(location=(0, -8, 3))
camera = bpy.context.active_object
camera.name = "Camera"
direction = mathutils.Vector((0, 0, 1)) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = camera
