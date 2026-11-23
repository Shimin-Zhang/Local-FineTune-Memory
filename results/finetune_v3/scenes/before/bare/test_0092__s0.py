import bpy
import math
import mathutils
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up world
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.05, 0.08, 0.15, 1.0)
    bg_node.inputs[1].default_value = 1.0

# Lighting
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 2.0
sun_data.color = (1.0, 0.9, 0.8)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(60), math.radians(20), math.radians(45))

# Ambient fill
fill_data = bpy.data.lights.new("Fill", type='AREA')
fill_data.energy = 100
fill_data.size = 50
fill_obj = bpy.data.objects.new("Fill", fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (0, 0, 30)

# Materials
def create_mat(name, color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            bsdf.inputs["Emission Color"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

mat_stone = create_mat("Stone", (0.75, 0.72, 0.68), roughness=0.8)
mat_dark_stone = create_mat("DarkStone", (0.3, 0.28, 0.26), roughness=0.85)
mat_copper = create_mat("Copper", (0.7, 0.35, 0.15), roughness=0.3, metallic=0.9)
mat_glass = create_mat("Glass", (0.8, 0.9, 1.0), roughness=0.1, metallic=0.0)
mat_gold = create_mat("Gold", (1.0, 0.85, 0.4), roughness=0.2, metallic=0.8)
mat_red = create_mat("Red", (0.8, 0.1, 0.1), roughness=0.6)
mat_green = create_mat("Green", (0.1, 0.5, 0.15), roughness=0.7)
mat_white = create_mat("White", (0.95, 0.95, 0.95), roughness=0.5)
mat_black = create_mat("Black", (0.05, 0.05, 0.05), roughness=0.7)
mat_snow = create_mat("Snow", (0.95, 0.97, 1.0), roughness=0.9)
mat_warm_light = create_mat("WarmLight", (1.0, 0.8, 0.5), emission=(1.0, 0.8, 0.5), emission_strength=2.0)
mat_chrome = create_mat("Chrome", (0.9, 0.9, 0.95), roughness=0.1, metallic=1.0)

# Helper functions
def add_box(name, loc, size, material, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def add_cylinder(name, loc, radius, depth, material, rotation=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rotation, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

def add_sphere(name, loc, radius, material, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=segments, rings=rings)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    bpy.ops.object.shade_smooth()
    return obj

# Main building - L-shaped corner
# Building A (long side along X)
add_box("BuildingA", (15, 0, 12), (30, 12, 24), mat_stone)
# Building B (perpendicular along Y)
add_box("BuildingB", (0, 15, 12), (12, 30, 24), mat_stone)

# Cornice
add_box("CorniceA", (15, 0, 24.5), (31, 13, 1), mat_dark_stone)
add_box("CorniceB", (0, 15, 24.5), (13, 31, 1), mat_dark_stone)

# Base/ground floor darker
add_box("BaseA", (15, 0, 3), (30, 12.5, 6), mat_dark_stone)
add_box("BaseB", (0, 15, 3), (12.5, 30, 6), mat_dark_stone)

# Display windows - Building A front (Y = -6)
for i in range(6):
    x = 3 + i * 5
    # Window frame
    add_box(f"WinFrameA_{i}", (x, -6.1, 3), (4, 0.3, 5), mat_dark_stone)
    # Glass
    add_box(f"WinGlassA_{i}", (x, -6.05, 3), (3.6, 0.1, 4.5), mat_glass)
    # Warm interior glow
    add_box(f"WinGlowA_{i}", (x, -5.8, 3), (3.4, 0.05, 4.3), mat_warm_light)

# Display windows - Building B front (X = -6)
for i in range(6):
    y = 3 + i * 5
    add_box(f"WinFrameB_{i}", (-6.1, y, 3), (0.3, 4, 5), mat_dark_stone)
    add_box(f"WinGlassB_{i}", (-6.05, y, 3), (0.1, 3.6, 4.5), mat_glass)
    add_box(f"WinGlowB_{i}", (-5.8, y, 3), (0.05, 3.4, 4.3), mat_warm_light)

# Corner dome
dome_center = (-6, -6)
# Drum
add_cylinder("DomeDrum", (dome_center[0], dome_center[1], 24), 5, 6, mat_stone, vertices=48)
# Dome
bpy.ops.mesh.primitive_uv_sphere_add(radius=5, location=(dome_center[0], dome_center[1], 27), segments=48, rings=24)
dome = bpy.context.active_object
dome.name = "Dome"
dome.scale = (1, 1, 0.7)
dome.data.materials.append(mat_copper)
bpy.ops.object.shade_smooth()
# Dome finial
add_cylinder("DomeFinial", (dome_center[0], dome_center[1], 32.5), 0.3, 3, mat_gold)
add_sphere("DomeOrb", (dome_center[0], dome_center[1], 34), 0.5, mat_gold)

# Entrance under dome - arched doorway
# Arch frame
bpy.ops.mesh.primitive_torus_add(location=(dome_center[0], dome_center[1], 3), major_radius=3, minor_radius=0.4, major_segments=32, minor_segments=16)
arch = bpy.context.active_object
arch.name = "EntranceArch"
arch.rotation_euler = (0, math.radians(90), 0)
arch.data.materials.append(mat_dark_stone)

# Door recess
add_box("DoorRecess", (dome_center[0], dome_center[1], 3), (5, 0.5, 6), mat_black)

# Double doors
add_box("DoorL", (dome_center[0] - 1.2, dome_center[1] - 0.2, 2.5), (2.2, 0.3, 5), mat_dark_stone)
add_box("DoorR", (dome_center[0] + 1.2, dome_center[1] - 0.2, 2.5), (2.2, 0.3, 5), mat_dark_stone)

# Steps
for i in range(3):
    add_box(f"Step_{i}", (dome_center[0], dome_center[1] - 2 - i*0.4, 0.3 + i*0.3), (7 + i*0.5, 1 + i*0.3, 0.3), mat_stone)

# Doorman
dm_loc = (dome_center[0] + 3.5, dome_center[1] - 2, 0)
# Body
add_cylinder("DoormanBody", (dm_loc[0], dm_loc[1], 1.2), 0.4, 1.8, mat_black)
# Head
add_sphere("DoormanHead", (dm_loc[0], dm_loc[1], 2.4), 0.3, mat_white)
# Hat
add_cylinder("DoormanHat", (dm_loc[0], dm_loc[1], 2.8), 0.35, 0.3, mat_black)
# Arms
add_cylinder("DoormanArmL", (dm_loc[0] - 0.5, dm_loc[1], 1.5), 0.12, 1.0, mat_black, rotation=(0, math.radians(20), 0))
add_cylinder("DoormanArmR", (dm_loc[0] + 0.5, dm_loc[1], 1.5), 0.12, 1.0, mat_black, rotation=(0, math.radians(-20), 0))

# Clock on building face
clock_loc = (15, -6.2, 18)
add_cylinder("ClockFace", clock_loc, 2, 0.3, mat_white, rotation=(math.radians(90), 0, 0), vertices=48)
add_cylinder("ClockRim", clock_loc, 2.2, 0.2, mat_gold, rotation=(math.radians(90), 0, 0), vertices=48)
# Clock hands
add_box("ClockHourHand", (clock_loc[0], clock_loc[1] - 0.1, clock_loc[2] + 0.5), (0.15, 0.1, 1.0), mat_black)
add_box("ClockMinuteHand", (clock_loc[0] + 0.5, clock_loc[1] - 0.1, clock_loc[2]), (0.1, 0.1, 1.5), mat_black)
add_sphere("ClockCenter", clock_loc, 0.15, mat_black)

# Delivery carts
def add_cart(loc, rot_z=0):
    # Platform
    add_box(f"CartPlat_{loc[0]:.1f}", (loc[0], loc[1], 0.8), (2.5, 1.5, 0.2), mat_dark_stone, rotation=(0,0,rot_z))
    # Wheels
    for wx in [-1, 1]:
        for wy in [-0.6, 0.6]:
            add_cylinder(f"CartWheel_{loc[0]:.1f}_{wx}_{wy}", (loc[0] + wx*1.0, loc[1] + wy*0.6, 0.3), 0.3, 0.15, mat_black, rotation=(math.radians(90), 0, 0), vertices=16)
    # Handle
    add_cylinder(f"CartHandle_{loc[0]:.1f}", (loc[0] - 1.5, loc[1], 1.2), 0.08, 1.5, mat_chrome, rotation=(0, math.radians(45), 0))
    # Crates
    add_box(f"CartCrate1_{loc[0]:.1f}", (loc[0] - 0.3, loc[1] - 0.3, 1.2), (0.8, 0.8, 0.8), mat_red)
    add_box(f"CartCrate2_{loc[0]:.1f}", (loc[0] + 0.5, loc[1] + 0.2, 1.1), (0.7, 0.7, 0.7), mat_green)

add_cart((8, -8), math.radians(10))
add_cart((12, -9), math.radians(-15))
add_cart((20, -7), math.radians(5))

# Snow ground
add_box("SnowGround", (10, 10, -0.2), (60, 60, 0.4), mat_snow)

# Holiday decorations - wreaths on windows
for i in range(6):
    x = 3 + i * 5
    # Wreath ring
    bpy.ops.mesh.primitive_torus_add(location=(x, -6.3, 3.5), major_radius=0.8, minor_radius=0.25, major_segments=24, minor_segments=12)
    wreath = bpy.context.active_object
    wreath.name = f"WreathA_{i}"
    wreath.rotation_euler = (math.radians(90), 0, 0)
    wreath.data.materials.append(mat_green)
    # Bow
    add_box(f"WBowA_{i}", (x, -6.4, 4.3), (0.4, 0.1, 0.3), mat_red)

for i in range(6):
    y = 3 + i * 5
    bpy.ops.mesh.primitive_torus_add(location=(-6.3, y, 3.5), major_radius=0.8, minor_radius=0.25, major_segments=24, minor_segments=12)
    wreath = bpy.context.active_object
    wreath.name = f"WreathB_{i}"
    wreath.rotation_euler = (0, math.radians(90), 0)
    wreath.data.materials.append(mat_green)
    add_box(f"WBowB_{i}", (-6.4, y, 4.3), (0.1, 0.4, 0.3), mat_red)

# Bunting/garland along cornice
for i in range(12):
    x = 2 + i * 2.5
    add_sphere(f"BuntingA_{i}", (x, -6.2, 24), 0.25, mat_red if i % 2 == 0 else mat_green)
    add_box(f"BuntingStrandA_{i}", (x + 1.25, -6.2, 24), (2.5, 0.05, 0.05), mat_red if i % 2 == 0 else mat_green)

for i in range(12):
    y = 2 + i * 2.5
    add_sphere(f"BuntingB_{i}", (-6.2, y, 24), 0.25, mat_red if i % 2 == 0 else mat_green)
    add_box(f"BuntingStrandB_{i}", (-6.2, y + 1.25, 24), (0.05, 2.5, 0.05), mat_red if i % 2 == 0 else mat_green)

# String lights along building edges
for i in range(15):
    x = 1 + i * 2
    add_sphere(f"LightA_{i}", (x, -6.15, 23.5), 0.12, mat_warm_light)

for i in range(15):
    y = 1 + i * 2
    add_sphere(f"LightB_{i}", (-6.15, y, 23.5), 0.12, mat_warm_light)

# Christmas tree near entrance
tree_loc = (-10