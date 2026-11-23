import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Ground
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Materials
mat_ground = bpy.data.materials.new("Grass")
mat_ground.use_nodes = True
mat_ground.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.2, 0.5, 0.1, 1)
ground.data.materials.append(mat_ground)

mat_red = bpy.data.materials.new("BarnRed")
mat_red.use_nodes = True
mat_red.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.8, 0.1, 0.1, 1)

mat_white = bpy.data.materials.new("White")
mat_white.use_nodes = True
mat_white.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1)

mat_yellow = bpy.data.materials.new("HayYellow")
mat_yellow.use_nodes = True
mat_yellow.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.85, 0.7, 0.2, 1)

mat_green = bpy.data.materials.new("TractorGreen")
mat_green.use_nodes = True
mat_green.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.1, 0.4, 0.1, 1)

mat_black = bpy.data.materials.new("Black")
mat_black.use_nodes = True
mat_black.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)

mat_wood = bpy.data.materials.new("Wood")
mat_wood.use_nodes = True
mat_wood.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.5, 0.3, 0.15, 1)

# ==================== BARN ====================
barn_x, barn_y = -8, -5
barn_w, barn_d, barn_h = 10, 8, 5

# Barn base
bpy.ops.mesh.primitive_cube_add(size=1, location=(barn_x, barn_y, barn_h/2))
barn_base = bpy.context.active_object
barn_base.scale = (barn_w/2, barn_d/2, barn_h/2)
barn_base.name = "BarnBase"
barn_base.data.materials.append(mat_red)

# Barn roof (two slanted planes)
roof_angle = math.atan2(barn_d/2, 2)  # roof rise of 2 units over half-depth
roof_len = math.sqrt((barn_d/2)**2 + 2**2)

# Left roof panel
bpy.ops.mesh.primitive_plane_add(size=1, location=(barn_x, barn_y - barn_d/4, barn_h + 1))
roof_left = bpy.context.active_object
roof_left.scale = (barn_w/2, roof_len/2, 1)
roof_left.rotation_euler = (math.radians(60), 0, 0)
roof_left.name = "RoofLeft"
roof_left.data.materials.append(mat_white)

# Right roof panel
bpy.ops.mesh.primitive_plane_add(size=1, location=(barn_x, barn_y + barn_d/4, barn_h + 1))
roof_right = bpy.context.active_object
roof_right.scale = (barn_w/2, roof_len/2, 1)
roof_right.rotation_euler = (math.radians(-60), 0, 0)
roof_right.name = "RoofRight"
roof_right.data.materials.append(mat_white)

# Barn door
bpy.ops.mesh.primitive_cube_add(size=1, location=(barn_x, barn_y + barn_d/2, 1.5))
barn_door = bpy.context.active_object
barn_door.scale = (1.5, 0.1, 1.5)
barn_door.name = "BarnDoor"
barn_door.data.materials.append(mat_wood)

# ==================== SILO ====================
silo_x, silo_y = -2, -8
silo_r, silo_h = 1.5, 8

bpy.ops.mesh.primitive_cylinder_add(radius=silo_r, depth=silo_h, location=(silo_x, silo_y, silo_h/2))
silo_body = bpy.context.active_object
silo_body.name = "SiloBody"
silo_body.data.materials.append(mat_white)

# Silo top (cone)
bpy.ops.mesh.primitive_cone_add(radius1=silo_r, radius2=0, depth=2, location=(silo_x, silo_y, silo_h + 1))
silo_top = bpy.context.active_object
silo_top.name = "SiloTop"
silo_top.data.materials.append(mat_red)

# ==================== FENCE ====================
# Fence along the front (y = 10) and sides
fence_posts = []
fence_height = 1.2
fence_spacing = 2

# Front fence (y = 10, x from -15 to 15)
for i in range(16):
    x = -15 + i * fence_spacing
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 10, fence_height/2))
    post = bpy.context.active_object
    post.scale = (0.1, 0.1, fence_height/2)
    post.name = f"FencePost_F_{i}"
    post.data.materials.append(mat_wood)
    fence_posts.append(post)

# Side fences (x = -15, y from -10 to 10)
for i in range(11):
    y = -10 + i * fence_spacing
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-15, y, fence_height/2))
    post = bpy.context.active_object
    post.scale = (0.1, 0.1, fence_height/2)
    post.name = f"FencePost_L_{i}"
    post.data.materials.append(mat_wood)
    fence_posts.append(post)

# Side fences (x = 15, y from -10 to 10)
for i in range(11):
    y = -10 + i * fence_spacing
    bpy.ops.mesh.primitive_cube_add(size=1, location=(15, y, fence_height/2))
    post = bpy.context.active_object
    post.scale = (0.1, 0.1, fence_height/2)
    post.name = f"FencePost_R_{i}"
    post.data.materials.append(mat_wood)
    fence_posts.append(post)

# Back fence (y = -10, x from -15 to 15)
for i in range(16):
    x = -15 + i * fence_spacing
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -10, fence_height/2))
    post = bpy.context.active_object
    post.scale = (0.1, 0.1, fence_height/2)
    post.name = f"FencePost_B_{i}"
    post.data.materials.append(mat_wood)
    fence_posts.append(post)

# Horizontal rails
# Front rails
for h in [0.4, 0.8, 1.2]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 10, h))
    rail = bpy.context.active_object
    rail.scale = (15, 0.05, 0.05)
    rail.name = f"FenceRail_F_{h}"
    rail.data.materials.append(mat_wood)

# Back rails
for h in [0.4, 0.8, 1.2]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -10, h))
    rail = bpy.context.active_object
    rail.scale = (15, 0.05, 0.05)
    rail.name = f"FenceRail_B_{h}"
    rail.data.materials.append(mat_wood)

# Left rails
for h in [0.4, 0.8, 1.2]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-15, 0, h))
    rail = bpy.context.active_object
    rail.scale = (0.05, 10, 0.05)
    rail.name = f"FenceRail_L_{h}"
    rail.data.materials.append(mat_wood)

# Right rails
for h in [0.4, 0.8, 1.2]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, h))
    rail = bpy.context.active_object
    rail.scale = (0.05, 10, 0.05)
    rail.name = f"FenceRail_R_{h}"
    rail.data.materials.append(mat_wood)

# ==================== TRACTOR ====================
tractor_x, tractor_y = 5, 0

# Tractor body
bpy.ops.mesh.primitive_cube_add(size=1, location=(tractor_x, tractor_y, 1))
tractor_body = bpy.context.active_object
tractor_body.scale = (1.5, 1, 0.8)
tractor_body.name = "TractorBody"
tractor_body.data.materials.append(mat_green)

# Tractor cabin
bpy.ops.mesh.primitive_cube_add(size=1, location=(tractor_x - 0.5, tractor_y, 1.8))
tractor_cabin = bpy.context.active_object
tractor_cabin.scale = (0.8, 0.8, 0.6)
tractor_cabin.name = "TractorCabin"
tractor_cabin.data.materials.append(mat_white)

# Tractor wheels (4 wheels)
wheel_positions = [
    (tractor_x - 1.2, tractor_y - 0.9, 0.5),  # Front left
    (tractor_x - 1.2, tractor_y + 0.9, 0.5),  # Front right
    (tractor_x + 1.2, tractor_y - 1.1, 0.6),  # Rear left
    (tractor_x + 1.2, tractor_y + 1.1, 0.6),  # Rear right
]

for i, (wx, wy, wz) in enumerate(wheel_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5 if i < 2 else 0.6, depth=0.3, location=(wx, wy, wz))
    wheel = bpy.context.active_object
    wheel.rotation_euler = (0, math.radians(90), 0)
    wheel.name = f"TractorWheel_{i}"
    wheel.data.materials.append(mat_black)

# ==================== HAY BALES (3) ====================
hay_positions = [
    (3, 5, 0.5),
    (6, 5, 0.5),
    (4.5, 7, 0.5),
]

for i, (hx, hy, hz) in enumerate(hay_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=1.2, location=(hx, hy, hz))
    bale = bpy.context.active_object
    bale.rotation_euler = (0, math.radians(90), 0)
    bale.name = f"HayBale_{i+1}"
    bale.data.materials.append(mat_yellow)

# Add a camera
bpy.ops.object.camera_add(location=(0, 25, 8), rotation=(math.radians(70), 0, 0))
cam = bpy.context.active_object
cam.name = "FarmCamera"
bpy.context.scene.camera = cam

# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(0, 0, 20))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(20), 0)
