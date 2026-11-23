import bpy
import math
import mathutils
import random

# --- Setup ---
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def create_material(name, color, metallic=0.0, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

mat_sand = create_material("Sand", (0.8, 0.7, 0.5), 0.0, 0.9)
mat_water = create_material("Water", (0.1, 0.4, 0.6), 0.0, 0.2)
mat_wood = create_material("Wood", (0.4, 0.25, 0.1), 0.0, 0.7)
mat_dark_wood = create_material("DarkWood", (0.2, 0.1, 0.05), 0.0, 0.8)
mat_stone = create_material("Stone", (0.5, 0.5, 0.5), 0.0, 0.9)
mat_metal = create_material("Metal", (0.3, 0.3, 0.3), 1.0, 0.4)
mat_flag_red = create_material("FlagRed", (0.8, 0.1, 0.1), 0.0, 0.6)
mat_flag_black = create_material("FlagBlack", (0.05, 0.05, 0.05), 0.0, 0.6)
mat_sail = create_material("Sail", (0.9, 0.85, 0.8), 0.0, 0.8)
mat_rope = create_material("Rope", (0.5, 0.4, 0.2), 0.0, 0.9)

# --- Terrain ---
# Sand
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
sand = bpy.context.active_object
sand.name = "Sand"
sand.data.materials.append(mat_sand)
# Flatten and move down slightly
sand.scale = (1, 1, 1)
sand.location.z = -0.5

# Water (Beach side)
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, -60, -0.8))
water = bpy.context.active_object
water.name = "Water"
water.data.materials.append(mat_water)

# --- Helper Functions ---
def add_log(start, end, radius=0.2, name="Log"):
    """Create a log (cylinder) between two points."""
    direction = mathutils.Vector(end) - mathutils.Vector(start)
    length = direction.length
    mid = (mathutils.Vector(start) + mathutils.Vector(end)) / 2
    
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=length, location=mid)
    log = bpy.context.active_object
    log.name = name
    
    # Align cylinder to direction
    direction.normalize()
    rot_quat = direction.to_track_quat('Z', 'Y')
    log.rotation_mode = 'QUATERNION'
    log.rotation_quaternion = rot_quat
    
    log.data.materials.append(mat_wood)
    return log

def add_sharpened_log(x, y, z, angle_deg, length=4, radius=0.25):
    """Create a sharpened log stake."""
    # Base cylinder
    log = add_log((x, y, z), (x, y, z + length), radius=radius, name="Stake")
    
    # Add a cone tip
    tip_z = z + length
    bpy.ops.mesh.primitive_cone_add(radius1=radius, radius2=0, depth=radius*1.5, location=(x, y, tip_z + radius*0.75))
    tip = bpy.context.active_object
    tip.name = "Stake_Tip"
    tip.data.materials.append(mat_wood)
    
    # Rotate around Y axis based on angle
    angle_rad = math.radians(angle_deg)
    log.rotation_euler.y = angle_rad
    tip.rotation_euler.y = angle_rad
    
    # Move to position
    log.location.x = x
    log.location.y = y
    log.location.z = z + length/2
    tip.location.x = x
    tip.location.y = y
    tip.location.z = z + length + radius*0.75
    
    return log

# --- Stockade (Palisade) ---
# Location: Behind the beach, forming a semi-circle or line
stockade_center_x = 0
stockade_center_y = 20
stockade_radius = 30
num_stakes = 20
start_angle = math.radians(180)
end_angle = math.radians(0)

for i in range(num_stakes):
    t = i / (num_stakes - 1)
    angle = start_angle + (end_angle - start_angle) * t
    x = stockade_center_x + stockade_radius * math.cos(angle)
    y = stockade_center_y + stockade_radius * math.sin(angle)
    
    # Slight random tilt
    tilt = random.uniform(-5, 5)
    add_sharpened_log(x, y, -0.5, tilt, length=5, radius=0.3)

# --- Lookout Post ---
lookout_x = 0
lookout_y = 25
lookout_height = 12

# 4 Posts
post_offset = 2
posts = [
    (lookout_x - post_offset, lookout_y - post_offset),
    (lookout_x + post_offset, lookout_y - post_offset),
    (lookout_x - post_offset, lookout_y + post_offset),
    (lookout_x + post_offset, lookout_y + post_offset)
]

for px, py in posts:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=lookout_height, location=(px, py, lookout_height/2))
    post = bpy.context.active_object
    post.name = "Lookout_Post"
    post.data.materials.append(mat_dark_wood)

# Platform
bpy.ops.mesh.primitive_cube_add(size=1, location=(lookout_x, lookout_y, lookout_height))
platform = bpy.context.active_object
platform.scale = (post_offset*2 + 1, post_offset*2 + 1, 0.2)
platform.name = "Lookout_Platform"
platform.data.materials.append(mat_wood)

# Railing
rail_height = 1
rail_thick = 0.1
# Front
bpy.ops.mesh.primitive_cube_add(size=1, location=(lookout_x, lookout_y - post_offset - 0.5, lookout_height + rail_height/2))
rail_f = bpy.context.active_object
rail_f.scale = (post_offset*2 + 1, rail_thick, rail_height)
rail_f.data.materials.append(mat_wood)
# Back
bpy.ops.mesh.primitive_cube_add(size=1, location=(lookout_x, lookout_y + post_offset + 0.5, lookout_height + rail_height/2))
rail_b = bpy.context.active_object
rail_b.scale = (post_offset*2 + 1, rail_thick, rail_height)
rail_b.data.materials.append(mat_wood)
# Left
bpy.ops.mesh.primitive_cube_add(size=1, location=(lookout_x - post_offset - 0.5, lookout_y, lookout_height + rail_height/2))
rail_l = bpy.context.active_object
rail_l.scale = (rail_thick, post_offset*2 + 1, rail_height)
rail_l.data.materials.append(mat_wood)
# Right
bpy.ops.mesh.primitive_cube_add(size=1, location=(lookout_x + post_offset + 0.5, lookout_y, lookout_height + rail_height/2))
rail_r = bpy.context.active_object
rail_r.scale = (rail_thick, post_offset*2 + 1, rail_height)
rail_r.data.materials.append(mat_wood)

# --- Cannon ---
cannon_x = 15
cannon_y = 10

# Carriage (Wooden base)
bpy.ops.mesh.primitive_cube_add(size=1, location=(cannon_x, cannon_y, 0.5))
carriage = bpy.context.active_object
carriage.scale = (2, 1, 1)
carriage.name = "Cannon_Carriage"
carriage.data.materials.append(mat_dark_wood)

# Wheels
for wx in [cannon_x - 1.5, cannon_x + 1.5]:
    bpy.ops.mesh.primitive_torus_add(major_radius=0.8, minor_radius=0.15, location=(wx, cannon_y, 0.8), rotation=(0, math.radians(90), 0))
    wheel = bpy.context.active_object
    wheel.name = "Cannon_Wheel"
    wheel.data.materials.append(mat_dark_wood)

# Barrel
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=3, location=(cannon_x, cannon_y, 1.2), rotation=(0, math.radians(90), 0))
barrel = bpy.context.active_object
barrel.name = "Cannon_Barrel"
barrel.data.materials.append(mat_metal)

# Muzzle (slightly wider)
bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.3, location=(cannon_x + 1.5, cannon_y, 1.2), rotation=(0, math.radians(90), 0))
muzzle = bpy.context.active_object
muzzle.name = "Cannon_Muzzle"
muzzle.data.materials.append(mat_metal)

# --- Rum Store Hut ---
hut_x = -15
hut_y = 15
hut_width = 6
hut_depth = 5
hut_height = 4

# Floor
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y, 0.2))
floor = bpy.context.active_object
floor.scale = (hut_width, hut_depth, 0.4)
floor.name = "Hut_Floor"
floor.data.materials.append(mat_wood)

# Walls
# Front (Beach side)
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y - hut_depth/2, hut_height/2 + 0.2))
wall_f = bpy.context.active_object
wall_f.scale = (hut_width, 0.2, hut_height)
wall_f.name = "Hut_Wall_F"
wall_f.data.materials.append(mat_wood)

# Back
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x, hut_y + hut_depth/2, hut_height/2 + 0.2))
wall_b = bpy.context.active_object
wall_b.scale = (hut_width, 0.2, hut_height)
wall_b.name = "Hut_Wall_B"
wall_b.data.materials.append(mat_wood)

# Left
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x - hut_width/2, hut_y, hut_height/2 + 0.2))
wall_l = bpy.context.active_object
wall_l.scale = (0.2, hut_depth, hut_height)
wall_l.name = "Hut_Wall_L"
wall_l.data.materials.append(mat_wood)

# Right
bpy.ops.mesh.primitive_cube_add(size=1, location=(hut_x + hut_width/2, hut_y, hut_height/2 + 0.2))
wall_r = bpy.context.active_object
wall_r.scale = (0.2, hut_depth, hut_height)
wall_r.name = "Hut_Wall_R"
wall_r.data.materials.append(mat_wood)

# Roof (Simple Prism)
# Create a mesh for the roof
verts = [
    (hut_x - hut_width/2 - 0.5, hut_y - hut_depth/2 - 0.5, hut_height + 0.2),
    (hut_x + hut_width/2 + 0.5, hut_y - hut_depth/2 - 0.5, hut_height + 0.2),
    (hut_x + hut_width/2 + 0.5, hut_y + hut_depth/2 + 0.5, hut_height + 0.2),
    (hut_x - hut_width/2 - 0.5, hut_y + hut_depth/2 + 0.5, hut_height + 0.2),
    (hut_x, hut_y, hut_height + 2.5) # Ridge
]
faces = [
    (0, 1, 4), # Front
    (1, 2, 4), # Right
    (2, 3, 4), # Back
    (3, 0, 4)  # Left
]
mesh = bpy.data.meshes.new("Hut_Roof")
mesh.from_pydata(verts, [], faces)
roof = bpy.data.objects.new("Hut_Roof", mesh)
bpy.context.collection.objects.link(roof)
roof.data.materials.append(mat_dark_wood)

# Door (Cutout simulation - just a dark plane)
bpy.ops.mesh.primitive_plane_add(size=1, location=(hut_x, hut_y - hut_depth/2 - 0.11, 1.5))
door = bpy.context.active_object
door.scale = (1.5, 2.5, 1)
door.rotation_euler = (0, 0, 0)
door.name = "Hut_Door"
door.data.materials.append(mat_dark_wood)

# --- Jolly Roger Flag ---
flagpole_x = 5
flagpole_y = 20
flagpole_height = 15

bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=flagpole_height, location=(flagpole_x, flagpole_y, flagpole_height/2))
pole = bpy.context.active_object
pole.name = "Flag_Pole"
pole.data.materials.append(mat_wood)

# Flag (Plane)
flag_width = 3
flag_height = 2
flag_x = flagpole_x
flag_y = flagpole_y
flag_z = flagpole_height - flag_height/2

bpy.ops.mesh.primitive_plane_add(size=1, location=(flag_x + flag_width/2, flag_y, flag_z))
flag = bpy.context.active_object
flag.scale = (flag_width, flag_height, 1)
flag.rotation_euler = (0, math.radians(90), 0) # Face outwards
flag.name = "Jolly_Roger"
flag.data.materials.append(mat_flag_black)

# Add a simple skull shape? Too complex for basic primitives, sticking to black flag with red cross maybe?
# Let's add a red cross on the flag
# Cross vertical
bpy.ops.mesh.primitive_cube_add(size=1, location=(flag_x + flag_width/2, flag_y, flag_z))
cross_v = bpy.context.active_object
cross_v.scale = (0.2, flag_height*0.8, 0.05)
cross_v.rotation_euler = (0, math.radians(90), 0)
cross_v.name = "Flag_Cross_V"
cross_v.data.materials.append(mat_flag_red)

# Cross horizontal
bpy.ops.mesh.primitive_cube_add(size=1, location=(flag_x + flag_width/2, flag_y, flag_z))
cross_h = bpy.context.active_object
cross_h.scale = (flag_width*0.8, 0.2, 0.05)
cross_h.rotation_euler = (0, math.radians(90), 0)
cross_h.name = "Flag_Cross_H"
cross_h.data.materials.append(mat_flag_red)

# --- Sloop at the Beach ---
sloop_x = 10
sloop_y = -10
sloop_length = 10
sloop_width = 3

# Hull
# Create a simple hull shape
hull_verts = [
    (sloop_x - sloop_length/2, sloop_y, 0),      # Stern bottom
    (sloop_x + sloop_length/2, sloop_y, 0),      # Bow bottom
    (sloop_x + sloop_length/2, sloop_y - sloop_width/2, 0), # Bow side
    (sloop_x + sloop_length/2, sloop_y + sloop_width/2, 0), # Bow side
    (sloop_x - sloop_length/2, sloop_y - sloop_width/2, 0), # Stern side
    (sloop_x - sloop_length/2, sloop_y + sloop_width/2, 0), # Stern side
    (sloop_x - sloop_length/2, sloop_y, 1),      # Stern top
    (sloop_x + sloop_length/2, sloop_y, 1.5),    # Bow top (raised)
    (sloop_x + sloop_length/2, sloop_y - sloop_width/2, 1), # Bow side top
    (sloop_x + sloop_length/2, sloop_y + sloop_width/2, 1), # Bow side top
    (sloop_x - sloop_length/2, sloop_y - sloop_width/2, 1), # Stern side top
    (sloop_x - sloop_length/2, sloop_y + sloop_width/2, 1), # Stern side top
]
hull_faces = [
    (0, 1, 8, 7), # Bottom front? No, let's make it simpler.
    # Just use a scaled cube for simplicity and reliability
]
# Let's use a scaled cube for the hull to ensure it works
bpy.ops.mesh.primitive_cube_add(size=1, location=(sloop_x, sloop_y, 0.5))
hull = bpy.context.active_object
hull.scale = (sloop_length, sloop_width, 1)
hull.name = "Sloop_Hull"
hull.data.materials.append(mat_wood)

# Deck
bpy.ops.mesh.primitive_cube_add(size=1, location=(sloop_x, sloop_y, 1.05))
deck = bpy.context.active_object
deck.scale = (sloop_length*0.9, sloop_width*0.8, 0.1)
deck.name = "Sloop_Deck"
deck.data.materials.append(mat_wood)

# Mast
mast_height = 8
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=mast_height, location=(sloop_x, sloop_y, 1 + mast_height/2))
mast = bpy.context.active_object
mast.name = "Sloop_Mast"
mast.data.materials.append(mat_wood)

# Sail
sail_width = 2.5
sail_height = 6
bpy.ops.mesh.primitive_plane_add(size=1, location=(sloop_x + 0.5, sloop_y, 1 + 3))
sail = bpy.context.active_object
sail.scale = (sail_width, sail_height, 1)
sail.rotation_euler = (0, math.radians(90), 0)
sail.name = "Sloop_Sail"
sail.data.materials.append(mat_sail)

# --- Camera & Lighting ---
# Camera
bpy.ops.object.camera_add(location=(0, -30, 15))
cam = bpy.context.active_object
cam.name = "Camera"
cam.rotation_euler = (math.radians(70), 0, 0)
bpy.context.scene.camera = cam

# Sun
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
sun = bpy.context.active_object
sun.name = "Sun"
sun.rotation_euler = (math.radians(45), math.radians(20), 0)
sun.data.energy = 3.0

# World Background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
bg_node.inputs[0].default_value = (0.8, 0.9, 1.0, 1.0) # Sky blue
bg_node.inputs[1].default_value = 1.0
