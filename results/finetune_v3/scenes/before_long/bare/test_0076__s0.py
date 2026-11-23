import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Set up
scene = bpy.context.scene
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.film_transparent = False

# Materials
def create_mat(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat

mud_mat = create_mat("Mud", (0.55, 0.42, 0.30), roughness=0.9)
thatch_mat = create_mat("Thatch", (0.65, 0.55, 0.30), roughness=0.95)
stone_mat = create_mat("Stone", (0.45, 0.43, 0.40), roughness=0.85)
dark_stone = create_mat("DarkStone", (0.25, 0.23, 0.22), roughness=0.9)
wood_mat = create_mat("Wood", (0.40, 0.28, 0.15), roughness=0.8)
mask_mat = create_mat("Mask", (0.85, 0.80, 0.70), roughness=0.6)
mask_dark = create_mat("MaskDark", (0.15, 0.12, 0.10), roughness=0.5)
red_accent = create_mat("RedAccent", (0.70, 0.15, 0.10), roughness=0.6)
cliff_mat = create_mat("Cliff", (0.50, 0.45, 0.38), roughness=0.95)
terrace_mat = create_mat("Terrace", (0.52, 0.48, 0.42), roughness=0.9)

# Helper: add mesh
def add_box(name, loc, scale, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

def add_cyl(name, loc, r, depth, mat, rot=(0,0,0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

# --- Cliff base ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -2))
cliff = bpy.context.active_object
cliff.name = "Cliff"
cliff.scale = (18, 14, 4)
cliff.data.materials.append(cliff_mat)
# Taper top
import bmesh
me = cliff.data
bm = bmesh.new()
bm.from_mesh(me)
for v in bm.verts:
    if v.co.z > 0:
        v.co.x *= 0.85
        v.co.y *= 0.85
bm.to_mesh(me)
bm.free()

# --- Mud house (flat-roofed base) ---
house_base = add_box("HouseBase", (0, 0, 0.5), (4, 3, 1.5), mud_mat)

# Flat roof slab
roof_slab = add_box("RoofSlab", (0, 0, 1.3), (4.3, 3.3, 0.15), stone_mat)

# --- Tall thatched roof (pyramid-ish, tall) ---
# Use a cone for thatched tall roof
bpy.ops.mesh.primitive_cone_add(radius1=4.5, radius2=0.5, depth=5, location=(0, 0, 3.8), vertices=4)
thatch_roof = bpy.context.active_object
thatch_roof.name = "ThatchedRoof"
thatch_roof.rotation_euler = (0, 0, math.radians(45))
thatch_roof.scale = (1, 0.75, 1)
thatch_roof.data.materials.append(thatch_mat)

# Roof ridge cap
add_cyl("RoofCap", (0, 0, 6.5), 0.3, 0.4, thatch_mat)

# House door
door = add_box("Door", (0, 1.5, 0.4), (0.6, 0.05, 0.8), wood_mat)

# Windows
add_box("WinL", (-1.5, 1.5, 0.6), (0.4, 0.05, 0.35), dark_stone)
add_box("WinR", (1.5, 1.5, 0.6), (0.4, 0.05, 0.35), dark_stone)

# --- Cave-mouth shrine above the house ---
# Carve a cave shape on the cliff face above
cave_center = (0, -2.5, 4.5)
# Cave mouth (dark opening)
bpy.ops.mesh.primitive_cube_add(size=1, location=cave_center)
cave_open = bpy.context.active_object
cave_open.name = "CaveOpening"
cave_open.scale = (2.5, 1.5, 2)
cave_open.data.materials.append(dark_stone)

# Cave arch (frame)
bpy.ops.mesh.primitive_torus_add(major_radius=2.2, minor_radius=0.3,
                                  location=cave_center,
                                  major_segments=24, minor_segments=8)
cave_arch = bpy.context.active_object
cave_arch.name = "CaveArch"
cave_arch.rotation_euler = (math.radians(90), 0, 0)
cave_arch.scale = (1, 0.8, 1)
cave_arch.data.materials.append(stone_mat)

# Shrine platform inside cave
add_box("CavePlatform", (0, -2.5, 3.8), (1.8, 0.8, 0.15), stone_mat)

# Shrine altar
add_box("Altar", (0, -2.5, 4.1), (0.8, 0.5, 0.5), stone_mat)

# Offering on altar
add_cyl("Offering", (0, -2.5, 4.45), 0.15, 0.2, red_accent)

# --- Terrace with masks ---
# Terrace platform extending from house
terrace = add_box("Terrace", (0, 3.5, 1.4), (5, 2.5, 0.2), terrace_mat)

# Terrace railing posts
for i in range(6):
    x = -2.5 + i * 1.0
    add_cyl(f"RailPost{i}", (x, 4.7, 1.8), 0.05, 0.6, wood_mat)

# Railing bar
add_box("RailBar", (0, 4.7, 2.1), (5, 0.08, 0.08), wood_mat)

# Masks lined up on terrace
mask_positions = [(-2, 3.5, 1.6), (-1, 3.5, 1.6), (0, 3.5, 1.6), (1, 3.5, 1.6), (2, 3.5, 1.6)]
for i, pos in enumerate(mask_positions):
    # Mask body (flattened sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=pos, segments=16, ring_count=12)
    mask = bpy.context.active_object
    mask.name = f"Mask{i}"
    mask.scale = (1, 0.4, 1.2)
    mask.rotation_euler = (math.radians(-10), 0, 0)
    mask.data.materials.append(mask_mat)

    # Eyes
    for side in [-1, 1]:
        eye_pos = (pos[0] + side * 0.1, pos[1] + 0.1, pos[2] + 0.08)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04, location=eye_pos, segments=8, ring_count=6)
        eye = bpy.context.active_object
        eye.name = f"Eye{i}_{side}"
        eye.data.materials.append(mask_dark)

    # Mouth
    mouth = add_box(f"Mouth{i}", (pos[0], pos[1] + 0.1, pos[2] - 0.12), (0.12, 0.02, 0.04), mask_dark)

    # Red accent stripe
    stripe = add_box(f"Stripe{i}", (pos[0], pos[1] + 0.1, pos[2] + 0.2), (0.03, 0.02, 0.15), red_accent)

# --- Steps to terrace ---
for i in range(3):
    step = add_box(f"Step{i}", (0, 2.0 + i * 0.4, 1.0 + i * 0.15), (1.2, 0.35, 0.1), stone_mat)

# --- Cliff texture details (rocks) ---
random.seed(42)
for i in range(15):
    x = random.uniform(-12, 12)
    y = random.uniform(-8, 8)
    z = random.uniform(-3, 1)
    r = random.uniform(0.3, 1.0)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=r, location=(x, y, z), subdivisions=1)
    rock = bpy.context.active_object
    rock.name = f"Rock{i}"
    rock.scale = (random.uniform(0.8, 1.5), random.uniform(0.8, 1.5), random.uniform(0.5, 1.0))
    rock.data.materials.append(stone_mat)

# --- Lighting ---
# Sun
bpy.ops.object.light_add(type='SUN', location=(10, -10, 15))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

# Fill light
bpy.ops.object.light_add(type='AREA', location=(-8, 8, 8))
fill = bpy.context.active_object
fill.name = "Fill"
fill.data.energy = 200
fill.data.size = 5
fill.rotation_euler = (math.radians(30), math.radians(-15), 0)

# Warm accent from cave
bpy.ops.object.light_add(type='POINT', location=(0, -2.5, 4.5))
cave_light = bpy.context.active_object
cave_light.name = "CaveLight"
cave_light.data.energy = 50
cave_light.data.color = (1.0, 0.6, 0.2)
cave_light.data.shadow_soft_size = 0.5

# --- Camera ---
bpy.ops.object.camera_add(location=(12, 12, 6))
cam = bpy.context.active_object
cam.name = "Camera"
cam.rotation_euler = (math.radians(65), 0, math.radians(-45))
scene.camera = cam

# Camera settings
cam.data.lens = 35
cam.data.sensor_width = 36

# World
world = scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.6, 0.7, 0.85, 1.0)
    bg.inputs[1].default_value = 0.8

# Render settings
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.cycles.use_denoising = True
scene.render.film_transparent = False

print("Cliff village shrine scene created.")
