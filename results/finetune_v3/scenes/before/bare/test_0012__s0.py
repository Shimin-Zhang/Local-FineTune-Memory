import bpy
import math
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clear collections
for col in bpy.data.collections:
    if col.name != "Collection":
        bpy.data.collections.remove(col)

# Create collections
scene = bpy.context.scene
coll_bridge = bpy.data.collections.new("Bridge")
coll_truck = bpy.data.collections.new("Truck")
coll_sandbags = bpy.data.collections.new("Sandbags")
coll_water = bpy.data.collections.new("Water")
scene.collection.children.link(coll_bridge)
scene.collection.children.link(coll_truck)
scene.collection.children.link(coll_sandbags)
scene.collection.children.link(coll_water)

# Materials
def make_mat(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_steel = make_mat("Steel", (0.4, 0.4, 0.45), 0.3, 0.9)
mat_timber = make_mat("Timber", (0.35, 0.2, 0.1), 0.8, 0.0)
mat_army_green = make_mat("ArmyGreen", (0.2, 0.3, 0.15), 0.7, 0.1)
mat_dark_green = make_mat("DarkGreen", (0.1, 0.18, 0.08), 0.8, 0.0)
mat_sandbag = make_mat("Sandbag", (0.6, 0.5, 0.3), 0.9, 0.0)
mat_water = make_mat("FloodWater", (0.3, 0.2, 0.1), 0.2, 0.0)
mat_wheel = make_mat("Wheel", (0.05, 0.05, 0.05), 0.9, 0.0)
mat_window = make_mat("Window", (0.1, 0.15, 0.2), 0.1, 0.3)

def add_cube(name, size, loc, mat, coll, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

def add_cylinder(name, r, depth, loc, mat, coll, rot=(0,0,0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    for c in obj.users_collection:
        c.objects.unlink(obj)
    coll.objects.link(obj)
    return obj

# === BRIDGE ===
# Timber blocks (piers)
bridge_length = 8.0
bridge_width = 4.0
deck_height = 1.5
num_piers = 4
pier_spacing = bridge_length / (num_piers - 1)

for i in range(num_piers):
    x = -bridge_length/2 + i * pier_spacing
    for z_off in [-1.2, 1.2]:
        add_cube(f"Pier_{i}_{z_off}", 1.0, (x, z_off, deck_height/2 - 0.3), mat_timber, coll_bridge)
        # Add some timber texture feel - stack 2 blocks
        add_cube(f"PierTop_{i}_{z_off}", 1.1, (x, z_off, deck_height/2 + 0.1), mat_timber, coll_bridge)

# Steel I-beams (trusses)
beam_depth = 0.3
beam_width = 0.15
num_beams = 6
for i in range(num_beams):
    x = -bridge_length/2 + (bridge_length / (num_beams-1)) * i
    # Top chord
    add_cube(f"BeamTop_{i}", beam_width, (x, 0, deck_height + beam_depth/2), mat_steel, coll_bridge)
    # Bottom chord
    add_cube(f"BeamBot_{i}", beam_width, (x, 0, deck_height - beam_depth/2), mat_steel, coll_bridge)
    # Web
    add_cube(f"BeamWeb_{i}", 0.05, (x, 0, deck_height), mat_steel, coll_bridge)

# Longitudinal beams
for z_off in [-1.5, 0, 1.5]:
    add_cube(f"LongBeam_{z_off}", beam_width, (0, z_off, deck_height), mat_steel, coll_bridge)

# Diagonal truss members
for i in range(num_beams - 1):
    x1 = -bridge_length/2 + (bridge_length / (num_beams-1)) * i
    x2 = -bridge_length/2 + (bridge_length / (num_beams-1)) * (i+1)
    mid_x = (x1 + x2) / 2
    # Diagonal up
    rot_z = math.atan2(deck_depth := beam_depth, (x2-x1))
    add_cube(f"DiagUp_{i}", 0.08, (mid_x, -1.5, deck_height + beam_depth/4), mat_steel, coll_bridge, rot=(0, 0, math.radians(20)))
    add_cube(f"DiagDown_{i}", 0.08, (mid_x, 1.5, deck_height - beam_depth/4), mat_steel, coll_bridge, rot=(0, 0, math.radians(-20)))

# Deck planks
plank_width = 0.4
num_planks = int(bridge_width / plank_width)
for i in range(num_planks):
    z = -bridge_width/2 + plank_width/2 + i * plank_width
    add_cube(f"Plank_{i}", 0.35, (0, z, deck_height + 0.08), mat_timber, coll_bridge)

# Cross beams on deck
for i in range(8):
    x = -bridge_length/2 + 0.5 + i * (bridge_length-1)/7
    add_cube(f"CrossBeam_{i}", 0.1, (x, 0, deck_height + 0.15), mat_steel, coll_bridge)

# Guard rails
for z_off in [-1.8, 1.8]:
    add_cube(f"Rail_{z_off}", 0.06, (0, z_off, deck_height + 0.5), mat_steel, coll_bridge)
    for i in range(10):
        x = -bridge_length/2 + 0.4 + i * (bridge_length-0.8)/9
        add_cube(f"RailPost_{z_off}_{i}", 0.04, (x, z_off, deck_height + 0.25), mat_steel, coll_bridge)

# === TRUCK ===
truck_x = 6.0
truck_z = 0.0
truck_y = 0.0

# Chassis
add_cube("Truck_Chassis", 0.8, (truck_x, truck_z, 0.5), mat_army_green, coll_truck)

# Cab
add_cube("Truck_Cab", 1.0, (truck_x - 1.2, truck_z, 1.0), mat_army_green, coll_truck)
# Cab roof
add_cube("Truck_Roof", 1.05, (truck_x - 1.2, truck_z, 1.55), mat_army_green, coll_truck)
# Windshield
add_cube("Truck_Windshield", 0.02, (truck_x - 1.72, truck_z, 1.2), mat_window, coll_truck)
# Side windows
add_cube("Truck_SideWin_L", 0.02, (truck_x - 1.2, truck_z - 0.52, 1.2), mat_window, coll_truck)
add_cube("Truck_SideWin_R", 0.02, (truck_x - 1.2, truck_z + 0.52, 1.2), mat_window, coll_truck)

# Cargo bed
add_cube("Truck_Bed", 1.2, (truck_x + 0.5, truck_z, 0.9), mat_army_green, coll_truck)
# Bed sides
add_cube("Truck_BedSide_L", 0.05, (truck_x + 0.5, truck_z - 0.62, 1.1), mat_army_green, coll_truck)
add_cube("Truck_BedSide_R", 0.05, (truck_x + 0.5, truck_z + 0.62, 1.1), mat_army_green, coll_truck)
add_cube("Truck_BedBack", 0.05, (truck_x + 1.12, truck_z, 1.1), mat_army_green, coll_truck)

# Wheels
wheel_positions = [
    (truck_x - 1.2, truck_z - 0.7, 0.35),
    (truck_x - 1.2, truck_z + 0.7, 0.35),
    (truck_x + 0.8, truck_z - 0.7, 0.35),
    (truck_x + 0.8, truck_z + 0.7, 0.35),
]
for i, (wx, wz, wy) in enumerate(wheel_positions):
    add_cylinder(f"Truck_Wheel_{i}", 0.35, 0.2, (wx, wz, wy), mat_wheel, coll_truck, rot=(math.radians(90), 0, 0), verts=24)

# Front bumper
add_cube("Truck_Bumper", 0.1, (truck_x - 1.8, truck_z, 0.4), mat_steel, coll_truck)

# Headlights
for hz in [-0.4, 0.4]:
    add_cylinder(f"Truck_HL_{hz}", 0.08, 0.05, (truck_x - 1.75, hz, 0.8), mat_window, coll_truck, rot=(0, math.radians(90), 0), verts=12)

# === SANDBAGS ===
sandbag_positions = [
    # Left side of bridge
    (-4.0, -2.2, 0.2), (-3.8, -2.4, 0.2), (-3.6, -2.1, 0.2),
    (-4.2, -2.0, 0.4), (-3.9, -2.3, 0.4),
    # Right side
    (4.0, 2.2, 0.2), (4.2, 2.4, 0.2), (3.8, 2.1, 0.2),
    (4.1, 2.0, 0.4), (3.9, 2.3, 0.4),
    # Near truck
    (5.5, -1.5, 0.2), (5.7, -1.3, 0.2), (5.3, -1.7, 0.2),
    (5.6, -1.5, 0.4),
    # Scattered
    (-1.0, -2.5, 0.2), (1.0, 2.5, 0.2), (-2.0, 2.3, 0.2),
]

for i, (sx, sz, sy) in enumerate(sandbag_positions):
    # Slightly randomize
    rx = sx + random.uniform(-0.1, 0.1)
    rz = sz + random.uniform(-0.1, 0.1)
    ry = sy + random.uniform(-0.02, 0.02)
    rot_y = random.uniform(0, math.pi)
    add_cube(f"Sandbag_{i}", 0.5, (rx, rz, ry), mat_sandbag, coll_sandbags, rot=(random.uniform(-0.1, 0.1), rot_y, random.uniform(-0.1, 0.1)))

# === FLOOD WATER ===
# Brown flood water close under the deck
water_surface = 0.3  # Close under deck (deck is at 1.5)
water_size = 20.0

bpy.ops.mesh.primitive_plane_add(size=water_size, location=(0, 0, water_surface))
water_obj = bpy.context.active_object
water_obj.name = "FloodWater"
water_obj.data.materials.append(mat_water)
for c in water_obj.users_collection:
    c.objects.unlink(water_obj)
coll_water.objects.link(water_obj)

# Make water slightly wavy by subdividing and moving vertices
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# Add subtle wave displacement
import mathutils
for vert in water_obj.data.vertices:
    wave = 0.03 * math.sin(vert.co.x * 2) * math.cos(vert.co.y * 2)
    vert.co.z += wave

# Set water material to be slightly transparent
mat_water.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = 0.85
mat_water.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.3

# === LIGHTING ===
# Sun
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Ambient
bpy.ops.object.light_add(type='POINT', location=(0, 0, 15))
amb = bpy.context.active_object
amb.name = "Ambient"
amb.data.energy = 50
amb.data.color = (0.8, 0.8, 0.9)

# Camera
bpy.ops.object.camera_add(location=(12, 8, 6), rotation=(math.radians(65), 0, math.radians(-30)))
cam = bpy.context.active_object
cam.name = "Camera"
scene.camera = cam

# Set render settings
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.5, 0.5, 0.6, 1.0)
    bg_node.inputs[1].default_value = 0.5
