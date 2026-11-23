import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def get_mat(name, color, rough=0.8, metal=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
    return mat

mat_bog   = get_mat("Bog",    (0.15, 0.22, 0.10, 1), 0.95)
mat_water = get_mat("Water",  (0.05, 0.12, 0.18, 1), 0.3, 0.1)
mat_quay  = get_mat("Quay",   (0.25, 0.18, 0.10, 1), 0.9)
mat_boat  = get_mat("Boat",   (0.12, 0.08, 0.05, 1), 0.85)
mat_turf  = get_mat("Turf",   (0.35, 0.22, 0.10, 1), 0.9)
mat_peat  = get_mat("Peat",   (0.28, 0.16, 0.08, 1), 0.95)
mat_bridge= get_mat("Bridge", (0.20, 0.14, 0.08, 1), 0.9)
mat_cottage_wall = get_mat("CottageWall", (0.75, 0.70, 0.60, 1), 0.85)
mat_roof  = get_mat("Roof",   (0.15, 0.10, 0.08, 1), 0.9)
mat_chimney= get_mat("Chimney",(0.40, 0.35, 0.30, 1), 0.9)
mat_smoke = get_mat("Smoke",  (0.8, 0.8, 0.8, 1), 1.0)
mat_grass = get_mat("Grass",  (0.10, 0.30, 0.08, 1), 0.95)
mat_tree  = get_mat("Tree",   (0.08, 0.25, 0.06, 1), 0.9)

# --- HELPERS ---
def add_box(name, loc, size, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.rotation_euler = Euler(rot)
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def add_cylinder(name, loc, r, depth, mat, rot=(0,0,0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = Euler(rot)
    obj.data.materials.append(mat)
    return obj

def add_sphere(name, loc, r, mat, segs=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=segs, ring_count=segs//2)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return obj

# --- BOG GROUND (large flat plane) ---
bpy.ops.mesh.primitive_plane_add(size=120, location=(0, 0, 0))
bog = bpy.context.active_object
bog.name = "Bog_Ground"
bog.data.materials.append(mat_bog)

# --- RIVER (long flat strip of water, slightly below bog) ---
# River runs along X axis, centered at y=0, width ~8
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.15))
river = bpy.context.active_object
river.name = "River"
river.scale = (80, 5, 1)
river.data.materials.append(mat_water)
bpy.ops.object.transform_apply(scale=True)

# --- PEAT QUAY (raised bank along one side of river, y = 6..12) ---
quay = add_box("Quay", (0, 9, 0.6), (80, 6, 1.2), mat_quay)

# --- FLAT BOAT on river ---
# Hull
boat = add_box("Boat_Hull", (10, 0, -0.05), (10, 3, 0.8), mat_boat)
# Cabin (small)
add_box("Boat_Cabin", (7, 0, 0.5), (3, 2.5, 1.2), mat_boat)

# Turf blocks on boat (grid of small boxes)
random.seed(42)
for i in range(4):
    for j in range(2):
        x = 11 + i * 1.8
        y = -0.8 + j * 1.6
        z = 0.45 + random.uniform(0, 0.1)
        add_box(f"Turf_{i}_{j}", (x, y, z), (1.5, 1.3, 0.7), mat_turf)

# --- TALL STACK OF PEAT on quay ---
# Base platform
add_box("Peat_Platform", (25, 9, 0.7), (8, 5, 0.2), mat_quay)
# Stack: several layers of peat blocks
for layer in range(6):
    z = 1.0 + layer * 0.8
    # 3 blocks per layer
    for b in range(3):
        x = 22.5 + b * 2.5
        y = 9 + random.uniform(-1, 1)
        add_box(f"Peat_{layer}_{b}", (x, y, z), (2.2, 3.5, 0.75), mat_peat)

# --- BRIDGE over river ---
# Two piers
for px in [35, 45]:
    add_box(f"Bridge_Pier_{px}", (px, 0, 0.3), (1.5, 10, 1.0), mat_bridge)
# Deck
add_box("Bridge_Deck", (40, 0, 1.0), (12, 8, 0.3), mat_bridge)
# Railings
for ry in [-3.5, 3.5]:
    add_box(f"Bridge_Rail_{ry}", (40, ry, 1.5), (12, 0.2, 0.8), mat_bridge)
# Posts
for px in [35, 40, 45]:
    for ry in [-3.5, 3.5]:
        add_cylinder(f"Bridge_Post_{px}_{ry}", (px, ry, 1.4), 0.1, 1.2, mat_bridge)

# --- COTTAGE on quay (y ~ 9, x ~ -15) ---
cx, cy = -15, 9
# Walls
add_box("Cottage_Walls", (cx, cy, 1.5), (6, 5, 3.0), mat_cottage_wall)
# Roof (two angled planes approximated by a box rotated, or use a prism)
# Simple: a box for roof
roof = add_box("Cottage_Roof", (cx, cy, 3.3), (6.5, 5.5, 0.3), mat_roof)
roof.rotation_euler = Euler((0, 0, 0))
# Make roof look pitched: add two slanted planes
bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy - 1.5, 3.6))
roof1 = bpy.context.active_object
roof1.scale = (3.5, 3.0, 1)
roof1.rotation_euler = Euler((math.radians(-30), 0, 0))
roof1.data.materials.append(mat_roof)
bpy.ops.object.transform_apply(scale=True)

bpy.ops.mesh.primitive_plane_add(size=1, location=(cx, cy + 1.5, 3.6))
roof2 = bpy.context.active_object
roof2.scale = (3.5, 3.0, 1)
roof2.rotation_euler = Euler((math.radians(30), 0, 0))
roof2.data.materials.append(mat_roof)
bpy.ops.object.transform_apply(scale=True)

# Chimney
chim = add_box("Chimney", (cx + 2, cy + 1.5, 4.2), (0.8, 0.8, 2.5), mat_chimney)

# Smoke: series of small spheres rising
random.seed(99)
for i in range(8):
    z = 5.5 + i * 0.8
    x_off = random.uniform(-0.3, 0.3)
    y_off = random.uniform(-0.3, 0.3)
    r = 0.25 + i * 0.05
    add_sphere(f"Smoke_{i}", (cx + 2 + x_off, cy + 1.5 + y_off, z), r, mat_smoke)

# --- SCATTERED TREES / BUSHES on bog for atmosphere ---
random.seed(7)
for i in range(20):
    tx = random.uniform(-40, 40)
    ty = random.uniform(-20, -8) if random.random() > 0.5 else random.uniform(14, 30)
    # Trunk
    add_cylinder(f"Tree_Trunk_{i}", (tx, ty, 1.0), 0.2, 2.0, mat_tree)
    # Canopy
    add_sphere(f"Tree_Canopy_{i}", (tx, ty, 2.5), 1.2 + random.uniform(0, 0.5), mat_tree)

# --- CAMERA ---
bpy.ops.object.camera_add(location=(0, -35, 12))
cam = bpy.context.active_object
cam.name = "Camera"
# Point camera toward scene center
direction = Vector((0, 5, 0)) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# --- LIGHTING ---
bpy.ops.object.light_add(type='SUN', location=(20, -20, 30))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = Euler((math.radians(45), math.radians(20), 0))

bpy.ops.object.light_add(type='AREA', location=(0, -10, 15))
area = bpy.context.active_object
area.name = "Fill"
area.data.energy = 50
area.data.size = 10
area.rotation_euler = Euler((math.radians(60), 0, 0))

# World background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.5, 0.6, 0.7, 1)
    bg.inputs["Strength"].default_value = 0.5
