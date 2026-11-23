import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# --- MATERIALS ---
mat_orange = bpy.data.materials.new("OrangeLandscape")
mat_orange.use_nodes = True
nodes = mat_orange.node_tree.nodes
links = mat_orange.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.85, 0.35, 0.05, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9

mat_rust = bpy.data.materials.new("RustMetal")
mat_rust.use_nodes = True
nodes = mat_rust.node_tree.nodes
links = mat_rust.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.45, 0.18, 0.08, 1.0)
bsdf.inputs["Metallic"].default_value = 0.6
bsdf.inputs["Roughness"].default_value = 0.7

mat_dark_ore = bpy.data.materials.new("DarkOre")
mat_dark_ore.use_nodes = True
nodes = mat_dark_ore.node_tree.nodes
links = mat_dark_ore.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.15, 0.12, 0.08, 1.0)
bsdf.inputs["Roughness"].default_value = 0.95

mat_tin = bpy.data.materials.new("TinSign")
mat_tin.use_nodes = True
nodes = mat_tin.node_tree.nodes
links = mat_tin.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.55, 0.55, 0.58, 1.0)
bsdf.inputs["Metallic"].default_value = 0.8
bsdf.inputs["Roughness"].default_value = 0.3

# --- GROUND (Flat orange landscape) ---
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(mat_orange)

# --- HILLSIDE (for dugout doors) ---
# Create a raised hill on one side
bpy.ops.mesh.primitive_cylinder_add(radius=25, depth=8, location=(30, 0, 4))
hill = bpy.context.active_object
hill.name = "Hillside"
hill.scale = (1.5, 1.0, 1.0)
hill.data.materials.append(mat_orange)
# Make it look more like a mound/hill by scaling
bpy.ops.object.transform_apply(scale=True)

# Flatten top slightly by moving top vertices down
me = hill.data
for v in me.vertices:
    if v.co.z > 3.5:
        v.co.z = 3.5

# --- VENTILATION PIPES ---
pipe_positions = [
    (-15, -10), (-10, 5), (5, -15), (10, 10), (20, -5),
    (-20, 15), (0, 20), (-5, -20), (15, 15), (-25, -5)
]

for i, (px, py) in enumerate(pipe_positions):
    height = random.uniform(3, 7)
    radius = random.uniform(0.3, 0.5)
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=height, location=(px, py, height/2))
    pipe = bpy.context.active_object
    pipe.name = f"VentPipe_{i}"
    pipe.data.materials.append(mat_rust)
    
    # Add a cap on top
    cap_h = 0.3
    bpy.ops.mesh.primitive_cylinder_add(radius=radius*1.2, depth=cap_h, location=(px, py, height + cap_h/2))
    cap = bpy.context.active_object
    cap.name = f"VentPipeCap_{i}"
    cap.data.materials.append(mat_rust)

# --- MOUNDS OF SPOIL ---
mound_positions = [
    (-30, -20, 8, 5), (-25, 25, 6, 4), (35, 20, 10, 6),
    (40, -15, 7, 5), (-40, 5, 9, 6), (15, 30, 5, 3)
]

for i, (mx, my, radius, height) in enumerate(mound_positions):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=24, ring_count=16, location=(mx, my, 0))
    mound = bpy.context.active_object
    mound.name = f"SpoilMound_{i}"
    mound.scale = (1.0, 1.0, height/radius)
    bpy.ops.object.transform_apply(scale=True)
    # Flatten bottom by clipping
    me = mound.data
    for v in me.vertices:
        if v.co.z < 0:
            v.co.z = 0
    mound.data.materials.append(mat_dark_ore)

# --- TIN SIGN ---
# Post
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=4, location=(-5, 0, 2))
sign_post = bpy.context.active_object
sign_post.name = "SignPost"
sign_post.data.materials.append(mat_rust)

# Sign board
bpy.ops.mesh.primitive_cube_add(size=1, location=(-5, 0, 4.5))
sign_board = bpy.context.active_object
sign_board.name = "TinSign"
sign_board.scale = (2.0, 0.1, 1.2)
bpy.ops.object.transform_apply(scale=True)
sign_board.data.materials.append(mat_tin)

# --- DUGOUT DOORS IN HILLSIDE ---
# Create rectangular door frames embedded in the hillside
door_positions = [
    (30, -5, 0), (30, 5, 0), (35, 0, 0), (25, 10, 0), (35, 10, 0)
]

for i, (dx, dy, dz) in enumerate(door_positions):
    # Door frame (slightly protruding from hill)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(dx, dy, 2))
    door = bpy.context.active_object
    door.name = f"DugoutDoor_{i}"
    door.scale = (1.5, 0.3, 2.0)
    bpy.ops.object.transform_apply(scale=True)
    door.data.materials.append(mat_rust)
    
    # Dark opening behind the door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(dx - 0.3, dy, 2))
    opening = bpy.context.active_object
    opening.name = f"DugoutOpening_{i}"
    opening.scale = (1.2, 0.2, 1.7)
    bpy.ops.object.transform_apply(scale=True)
    opening.data.materials.append(mat_dark_ore)

# --- LIGHTING ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.data.color = (1.0, 0.85, 0.6)
sun.rotation_euler = Euler((math.radians(45), math.radians(20), 0))

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.1, 0.08, 0.05, 1.0)
    bg_node.inputs[1].default_value = 0.5

# Camera
bpy.ops.object.camera_add(location=(0, -40, 15))
cam = bpy.context.active_object
cam.name = "Camera"
cam.rotation_euler = Euler((math.radians(75), 0, 0))
bpy.context.scene.camera = cam

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
