import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Clear collections
for block in bpy.data.collections:
    bpy.data.collections.remove(block)

# --- World (night sky) ---
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
bg_node.inputs[0].default_value = (0.005, 0.008, 0.015, 1.0)  # very dark blue night
bg_node.inputs[1].default_value = 1.0

# --- Materials ---
# Fire material (emissive orange)
fire_mat = bpy.data.materials.new("FireMat")
fire_mat.use_nodes = True
nodes = fire_mat.node_tree.nodes
links = fire_mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
emit_node = nodes.new("ShaderNodeEmission")
emit_node.inputs[0].default_value = (1.0, 0.35, 0.05, 1.0)
emit_node.inputs[1].default_value = 8.0
links.new(emit_node.outputs[0], out_node.inputs[0])
fire_mat.node_tree.nodes.active = emit_node

# Wood material
wood_mat = bpy.data.materials.new("WoodMat")
wood_mat.use_nodes = True
bsdf = wood_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.15, 0.08, 0.03, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9

# Ground material
ground_mat = bpy.data.materials.new("GroundMat")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.08, 0.06, 0.04, 1.0)
bsdf.inputs["Roughness"].default_value = 1.0

# Rock material
rock_mat = bpy.data.materials.new("RockMat")
rock_mat.use_nodes = True
bsdf = rock_mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.25, 0.22, 0.2, 1.0)
bsdf.inputs["Roughness"].default_value = 0.85

# Ember material (slightly glowing)
ember_mat = bpy.data.materials.new("EmberMat")
ember_mat.use_nodes = True
nodes = ember_mat.node_tree.nodes
links = ember_mat.node_tree.links
nodes.clear()
out_node = nodes.new("ShaderNodeOutputMaterial")
emit_node = nodes.new("ShaderNodeEmission")
emit_node.inputs[0].default_value = (1.0, 0.2, 0.03, 1.0)
emit_node.inputs[1].default_value = 3.0
links.new(emit_node.outputs[0], out_node.inputs[0])

# --- Ground plane ---
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(ground_mat)

# --- Logs (cylinder logs arranged in a teepee/stack) ---
log_positions = [
    (0.3, 0.0, 0.15, 0.0, 0.0, 0.3),   # x, y, z, rot_x, rot_y, rot_z
    (-0.3, 0.0, 0.15, 0.0, 0.0, -0.3),
    (0.0, 0.3, 0.15, 0.3, 0.0, 0.0),
    (0.0, -0.3, 0.15, -0.3, 0.0, 0.0),
    (0.2, 0.2, 0.15, 0.15, 0.15, 0.2),
    (-0.2, -0.2, 0.15, -0.15, -0.15, -0.2),
    (0.2, -0.2, 0.15, 0.15, -0.15, 0.2),
    (-0.2, 0.2, 0.15, -0.15, 0.15, -0.2),
]

for i, (x, y, z, rx, ry, rz) in enumerate(log_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.8, location=(x, y, z), rotation=(rx, ry, rz))
    log = bpy.context.active_object
    log.name = f"Log_{i}"
    log.data.materials.append(wood_mat)

# --- Fire (emissive icosphere) ---
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.25, location=(0, 0, 0.25))
fire = bpy.context.active_object
fire.name = "Fire"
fire.data.materials.append(fire_mat)
# Slightly scale vertically for flame shape
fire.scale = (1.0, 1.0, 1.3)

# --- Embers (small glowing spheres at base) ---
random.seed(42)
for i in range(12):
    angle = random.uniform(0, 2 * math.pi)
    dist = random.uniform(0.05, 0.2)
    ex = dist * math.cos(angle)
    ey = dist * math.sin(angle)
    ez = random.uniform(0.05, 0.15)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.015, 0.035), location=(ex, ey, ez))
    ember = bpy.context.active_object
    ember.name = f"Ember_{i}"
    ember.data.materials.append(ember_mat)

# --- Rocks around the fire ---
for i in range(10):
    angle = (i / 10) * 2 * math.pi
    dist = random.uniform(0.45, 0.6)
    rx = dist * math.cos(angle)
    ry = dist * math.sin(angle)
    rz = random.uniform(0.03, 0.08)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.06, 0.12), location=(rx, ry, rz))
    rock = bpy.context.active_object
    rock.name = f"Rock_{i}"
    rock.scale = (random.uniform(0.8, 1.3), random.uniform(0.8, 1.3), random.uniform(0.5, 0.8))
    rock.rotation_euler = (random.uniform(0, 0.3), random.uniform(0, 0.3), random.uniform(0, 2 * math.pi))
    rock.data.materials.append(rock_mat)

# --- Point light to simulate fire glow ---
light_data = bpy.data.lights.new("FireLight", type='POINT')
light_data.energy = 50
light_data.color = (1.0, 0.45, 0.1)
light_data.shadow_soft_size = 0.3
light_obj = bpy.data.objects.new("FireLight", light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (0, 0, 0.35)

# Add a secondary dimmer light for ambient fill from fire
light_data2 = bpy.data.lights.new("FireGlow", type='POINT')
light_data2.energy = 15
light_data2.color = (1.0, 0.3, 0.05)
light_data2.shadow_soft_size = 0.8
light_obj2 = bpy.data.objects.new("FireGlow", light_data2)
bpy.context.collection.objects.link(light_obj2)
light_obj2.location = (0, 0, 0.15)

# --- Camera ---
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 50
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (2.5, 2.5, 1.2)
# Look at fire
direction = Vector((0, 0, 0.25)) - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam_obj

# --- Render settings ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.view_settings.view_transform = 'Filmic'
scene.view_settings.look = 'Medium High Contrast'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
