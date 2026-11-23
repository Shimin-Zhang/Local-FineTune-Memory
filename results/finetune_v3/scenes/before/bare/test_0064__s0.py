import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_mat(name, color, metallic=0.0, rough=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    return mat

iron_mat   = make_mat("Iron",   (0.15, 0.15, 0.18), 0.85, 0.35)
timber_mat = make_mat("Timber", (0.35, 0.22, 0.10), 0.0, 0.7)
concrete_mat = make_mat("Concrete", (0.55, 0.55, 0.55), 0.0, 0.9)
glass_mat  = make_mat("Glass",  (0.6, 0.8, 0.9), 0.0, 0.1)
brick_mat  = make_mat("Brick",  (0.5, 0.2, 0.12), 0.0, 0.8)
roof_mat   = make_mat("Roof",   (0.25, 0.18, 0.12), 0.0, 0.8)
lamp_mat   = make_mat("LampGlass", (1.0, 0.9, 0.5), 0.0, 0.2)
lamp_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1.0, 0.9, 0.4, 1)
lamp_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0

# Helper: create a box
def add_box(name, size, loc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    obj.data.materials.append(mat)
    bpy.ops.object.transform_apply(scale=True)
    return obj

# Helper: cylinder
def add_cyl(name, r, depth, loc, mat, rot=(0,0,0), verts=12):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

# ---------- ELEVATED RAILWAY ----------
STATION_LEN = 24.0
STATION_W   = 8.0
RAIL_H      = 6.0   # height of rail above ground

# Iron girders (vertical columns)
col_spacing = 4.0
n_cols = int(STATION_LEN // col_spacing) + 1
for i in range(n_cols):
    x = -STATION_LEN/2 + i * col_spacing
    for side in (-1, 1):
        z = side * (STATION_W/2 - 0.3)
        add_box(f"col_{i}_{side}", (0.4, 0.4, RAIL_H), (x, z, RAIL_H/2), iron_mat)

# Cross beams (horizontal)
for i in range(n_cols):
    x = -STATION_LEN/2 + i * col_spacing
    add_box(f"beam_h_{i}", (0.3, STATION_W, 0.3), (x, 0, RAIL_H - 0.5), iron_mat)

# Main platform deck (timber)
add_box("platform", (STATION_LEN, STATION_W, 0.25), (0, 0, RAIL_H), timber_mat)

# Platform edge railings (iron)
for side in (-1, 1):
    z = side * (STATION_W/2 - 0.1)
    add_box(f"rail_{side}", (STATION_LEN, 0.05, 1.0), (0, z, RAIL_H + 0.5), iron_mat)
    # vertical posts
    for i in range(int(STATION_LEN // 2) + 1):
        x = -STATION_LEN/2 + i * 2.0
        add_box(f"rpost_{side}_{i}", (0.05, 0.05, 1.0), (x, z, RAIL_H + 0.5), iron_mat)

# Roof structure (iron frame + timber planks)
roof_h = RAIL_H + 3.5
# Roof support posts
for i in range(n_cols):
    x = -STATION_LEN/2 + i * col_spacing
    for side in (-1, 1):
        z = side * (STATION_W/2 - 0.3)
        add_box(f"rpost2_{i}_{side}", (0.3, 0.3, 3.5), (x, z, RAIL_H + 1.75), iron_mat)

# Roof ridge beam
add_box("roof_ridge", (STATION_LEN, 0.3, 0.3), (0, 0, roof_h), iron_mat)

# Roof panels (timber, slightly angled)
for side in (-1, 1):
    z = side * (STATION_W/4)
    add_box(f"roof_panel_{side}", (STATION_LEN, STATION_W/2, 0.1),
            (0, z, roof_h - 0.1), timber_mat, rot=(0, side * math.radians(8), 0))

# Track rails (two iron rails)
for z in (-1.2, 1.2):
    add_box(f"track_{z}", (STATION_LEN, 0.15, 0.15), (0, z, RAIL_H + 0.15), iron_mat)

# Sleepers (timber)
for i in range(int(STATION_LEN // 1.5) + 1):
    x = -STATION_LEN/2 + i * 1.5
    add_box(f"sleeper_{i}", (0.2, 3.0, 0.1), (x, 0, RAIL_H + 0.05), timber_mat)

# ---------- STAIRCASE ----------
stair_x = STATION_LEN/2 + 2.0
stair_steps = 12
step_h = RAIL_H / stair_steps
step_d = 0.4
for i in range(stair_steps):
    z = -STATION_W/2 - 0.5
    x = stair_x + i * step_d
    y = -STATION_W/2 - 0.5 - i * step_d * 0.3
    add_box(f"stair_{i}", (0.8, 0.8, step_h), (x, y, i * step_h + step_h/2), concrete_mat)

# Stair railings
for i in range(stair_steps + 1):
    x = stair_x + i * step_d
    y = -STATION_W/2 - 0.5 - i * step_d * 0.3
    add_box(f"stair_rail_{i}", (0.05, 0.05, 1.0), (x, y, i * step_h + 0.5), iron_mat)

# ---------- NEWS KIOSK ----------
kiosk_loc = (-STATION_LEN/2 - 3.0, -STATION_W/2 - 2.0, 0)
# Base
add_box("kiosk_base", (3.0, 3.0, 2.5), kiosk_loc, brick_mat)
# Roof
add_box("kiosk_roof", (3.4, 3.4, 0.15), (kiosk_loc[0], kiosk_loc[1], kiosk_loc[2] + 2.6), roof_mat)
# Windows (glass)
for i in range(3):
    x = kiosk_loc[0] - 1.0 + i * 1.0
    add_box(f"kiosk_win_{i}", (0.8, 0.05, 1.5), (x, kiosk_loc[1] - 1.55, kiosk_loc[2] + 1.2), glass_mat)
# Sign
add_box("kiosk_sign", (2.5, 0.05, 0.5), (kiosk_loc[0], kiosk_loc[1] - 1.55, kiosk_loc[2] + 2.3), timber_mat)

# ---------- GAS LAMPS ----------
def add_gas_lamp(loc):
    # Pole
    add_cyl(f"lamp_pole_{loc[0]:.1f}", 0.08, 3.5, (loc[0], loc[1], 1.75), iron_mat)
    # Cross arm
    add_box(f"lamp_arm_{loc[0]:.1f}", (0.05, 0.8, 0.05), (loc[0], loc[1], 3.3), iron_mat)
    # Lamp housing
    add_cyl(f"lamp_housing_{loc[0]:.1f}", 0.15, 0.3, (loc[0], loc[1] + 0.4, 3.4), iron_mat)
    # Glass
    add_cyl(f"lamp_glass_{loc[0]:.1f}", 0.12, 0.2, (loc[0], loc[1] + 0.4, 3.4), lamp_mat)
    # Point light
    light_data = bpy.data.lights.new(f"lamp_light_{loc[0]:.1f}", type='POINT')
    light_data.energy = 50
    light_data.color = (1.0, 0.85, 0.5)
    light_data.shadow_soft_size = 0.3
    light_obj = bpy.data.objects.new(f"lamp_light_{loc[0]:.1f}", light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (loc[0], loc[1] + 0.4, 3.4)

# Place lamps along the street
for i in range(5):
    x = -12 + i * 6.0
    z = -STATION_W/2 - 4.0
    add_gas_lamp((x, z, 0))

# ---------- ROOFTOPS (background) ----------
random.seed(42)
for i in range(15):
    x = random.uniform(-30, 30)
    z = random.uniform(15, 40)  # behind the station
    w = random.uniform(4, 10)
    d = random.uniform(4, 10)
    h = random.uniform(3, 12)
    # Building
    add_box(f"bldg_{i}", (w, d, h), (x, z, h/2), brick_mat)
    # Roof
    add_box(f"roof_{i}", (w + 0.4, d + 0.4, 0.2), (x, z, h + 0.1), roof_mat)
    # Chimney
    if random.random() > 0.5:
        cx = x + random.uniform(-w/3, w/3)
        cz = z + random.uniform(-d/3, d/3)
        add_box(f"chimney_{i}", (0.5, 0.5, 2.0), (cx, cz, h + 1.0), brick_mat)

# ---------- GROUND / STREET ----------
add_box("ground", (80, 80, 0.2), (0, 0, -0.1), concrete_mat)

# ---------- CAMERA & LIGHTING ----------
# Sun
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.color = (1.0, 0.95, 0.85)
sun_data.angle = math.radians(5)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(0))

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (15, -25, 8)
cam_obj.rotation_euler = (math.radians(70), 0, math.radians(20))
bpy.context.scene.camera = cam_obj

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.4, 0.5, 0.7, 1)
    bg.inputs[1].default_value = 0.5

print("Elevated railway station scene built.")
