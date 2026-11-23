import bpy
import math
import random
from mathutils import Vector

# --- Clean up scene ---
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Materials ---
def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_rock = create_material("Basalt", (0.15, 0.15, 0.18, 1.0), roughness=0.9)
mat_sea = create_material("Sea", (0.05, 0.15, 0.25, 1.0), roughness=0.1)
mat_hut_wall = create_material("HutWall", (0.3, 0.2, 0.1, 1.0), roughness=0.9)
mat_hut_roof = create_material("HutRoof", (0.2, 0.15, 0.1, 1.0), roughness=0.9)
mat_giant = create_material("GiantSkin", (0.4, 0.35, 0.3, 1.0), roughness=0.8)
mat_boot = create_material("Boot", (0.2, 0.15, 0.1, 1.0), roughness=0.7)

# --- Hexagonal Basalt Columns (Stepping Stones) ---
def create_hex_column(location, height, radius, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=radius, depth=height, location=location)
    obj = bpy.context.active_object
    obj.data.materials.append(mat)
    # Slight random rotation for natural look
    obj.rotation_euler[2] = random.uniform(0, math.pi)
    return obj

# Create a series of hex columns leading into the sea
positions = []
x = 0
z = 0
for i in range(15):
    # Curve slightly into the sea (positive z)
    x += random.uniform(0.8, 1.2)
    z += random.uniform(0.5, 1.0)
    height = random.uniform(1.5, 3.0)
    radius = random.uniform(0.8, 1.2)
    create_hex_column((x, -height/2, z), height, radius, mat_rock)
    positions.append((x, z))

# --- Sea ---
bpy.ops.mesh.primitive_plane_add(size=100, location=(20, -1, 20))
sea = bpy.context.active_object
sea.name = "Sea"
sea.data.materials.append(mat_sea)
# Subdivide for wave potential
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.subdivide(number_cuts=20)
bpy.ops.object.mode_set(mode='OBJECT')

# --- Rough Waves (Simple geometry displacement) ---
# Add some wave-like bumps near the shore
for i in range(10):
    x = random.uniform(0, 15)
    z = random.uniform(0, 5)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.5, 1.5), location=(x, -0.5, z))
    wave = bpy.context.active_object
    wave.scale = (1.5, 0.3, 0.8)
    wave.data.materials.append(mat_sea)
    wave.name = f"Wave_{i}"

# --- Sleeping Giant's Boot ---
# Create a large boot shape using a metaball or simple mesh
# Using a scaled cube + cylinder for simplicity
bpy.ops.mesh.primitive_cube_add(size=1, location=(5, 0, -5))
boot_base = bpy.context.active_object
boot_base.name = "GiantBoot_Base"
boot_base.scale = (4, 2, 3)
boot_base.data.materials.append(mat_boot)

# Toe of the boot
bpy.ops.mesh.primitive_uv_sphere_add(radius=2, location=(9, 0, -5))
boot_toe = bpy.context.active_object
boot_toe.name = "GiantBoot_Toe"
boot_toe.scale = (1.5, 1, 1)
boot_toe.data.materials.append(mat_boot)

# Heel
bpy.ops.mesh.primitive_cube_add(size=1, location=(2, 0, -5))
boot_heel = bpy.context.active_object
boot_heel.name = "GiantBoot_Heel"
boot_heel.scale = (1.5, 1.5, 1.5)
boot_heel.data.materials.append(mat_boot)

# Ankle/leg part
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=5, location=(4, 0, -2))
boot_leg = bpy.context.active_object
boot_leg.name = "GiantBoot_Leg"
boot_leg.data.materials.append(mat_giant)

# --- Fisherman's Hut ---
# Base
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, 10))
hut_base = bpy.context.active_object
hut_base.name = "Hut_Base"
hut_base.scale = (3, 2.5, 2)
hut_base.data.materials.append(mat_hut_wall)

# Roof (Pyramid)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=4, depth=2, location=(15, 2, 10))
hut_roof = bpy.context.active_object
hut_roof.name = "Hut_Roof"
hut_roof.rotation_euler[2] = math.pi/4
hut_roof.data.materials.append(mat_hut_roof)

# Door
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 0, 12.5))
door = bpy.context.active_object
door.name = "Hut_Door"
door.scale = (0.8, 0.1, 1)
door.data.materials.append(mat_hut_roof)

# --- Lighting ---
bpy.ops.object.light_add(type='SUN', location=(10, 20, 10))
sun = bpy.context.active_object
sun.rotation_euler = (math.radians(45), math.radians(30), 0)
sun.data.energy = 3.0

bpy.ops.object.light_add(type='AREA', location=(0, 5, 0))
area = bpy.context.active_object
area.data.energy = 100
area.scale = (10, 10, 1)

# --- Camera ---
bpy.ops.object.camera_add(location=(25, 15, 10))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(70), 0, math.radians(-45))
bpy.context.scene.camera = cam

# --- World Background ---
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.7, 0.8, 0.9, 1.0)
bg.inputs[1].default_value = 1.0

print("Scene created: Hexagonal basalt columns, sleeping giant's boot, fisherman's hut, and rough waves.")
