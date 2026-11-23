import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- MATERIALS ---
def create_mat(name, color, roughness=0.8, metallic=0.0, emission=0.0, emit_color=(0,0,0,1)):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = emit_color
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat

mat_wood_dark   = create_mat("WoodDark",   (0.12, 0.06, 0.03, 1), 0.9)
mat_wood_mid    = create_mat("WoodMid",    (0.25, 0.14, 0.07, 1), 0.85)
mat_wood_light  = create_mat("WoodLight",  (0.45, 0.30, 0.15, 1), 0.8)
mat_dirt        = create_mat("Dirt",       (0.55, 0.42, 0.28, 1), 1.0)
mat_piano       = create_mat("Piano",      (0.05, 0.05, 0.05, 1), 0.3, 0.1)
mat_piano_keys  = create_mat("PianoKeys",  (0.90, 0.88, 0.82, 1), 0.4)
mat_glass       = create_mat("Glass",      (0.8, 0.85, 0.9, 1), 0.1, 0.0)
mat_glass.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 0.9
mat_sign        = create_mat("Sign",       (0.7, 0.6, 0.4, 1), 0.7)
mat_tumbleweed  = create_mat("Tumbleweed", (0.6, 0.5, 0.3, 1), 1.0)
mat_sky         = create_mat("Sky",        (0.85, 0.88, 0.95, 1), 1.0)

# --- GROUND ---
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_dirt)

# --- SALOON STRUCTURE ---
# Main building: 10 wide (x), 12 deep (y), 8 tall (z)
W, D, H = 10, 12, 8

def add_box(name, loc, size, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, size=1)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.rotation_euler = Euler(rot)
    obj.data.materials.append(mat)
    return obj

# Walls
add_box("Wall_Front",  (0,  D/2, H/2), (W, 0.3, H), mat_wood_mid)
add_box("Wall_Back",   (0, -D/2, H/2), (W, 0.3, H), mat_wood_mid)
add_box("Wall_Left",   (-W/2, 0, H/2), (0.3, D, H), mat_wood_mid)
add_box("Wall_Right",  ( W/2, 0, H/2), (0.3, D, H), mat_wood_mid)

# Roof (slight overhang)
add_box("Roof", (0, 0, H + 0.3), (W + 1.5, D + 1.5, 0.6), mat_wood_dark)

# --- DOORWAY (front center) ---
# Cut out door opening: remove front wall section and add frame
# We'll place door panels manually
door_w, door_h = 2.2, 5.0
door_y = D/2  # front face

# Left door panel (hinged at left edge of opening)
door_left = add_box("Door_Left", (-0.55, door_y, door_h/2), (door_w/2, 0.12, door_h), mat_wood_light)
# Pivot left door: rotate around its left edge
door_left.location = (-door_w/2 + 0.06, door_y, door_h/2)
door_left.rotation_euler = Euler((0, math.radians(35), 0))  # swung open 35 deg inward

# Right door panel (hinged at right edge)
door_right = add_box("Door_Right", (0.55, door_y, door_h/2), (door_w/2, 0.12, door_h), mat_wood_light)
door_right.location = (door_w/2 - 0.06, door_y, door_h/2)
door_right.rotation_euler = Euler((0, math.radians(-15), 0))  # slightly ajar

# Door frame
add_box("DoorFrame_L", (-door_w/2 - 0.1, door_y, door_h/2), (0.2, 0.4, door_h), mat_wood_dark)
add_box("DoorFrame_R", ( door_w/2 + 0.1, door_y, door_h/2), (0.2, 0.4, door_h), mat_wood_dark)
add_box("DoorFrame_T", (0, door_y, door_h + 0.1), (door_w + 0.4, 0.4, 0.2), mat_wood_dark)

# --- WINDOWS (front, left and right of door) ---
win_w, win_h = 2.0, 2.5
win_y = D/2
win_z = 3.0

for side, x_off in [("L", -3.0), ("R", 3.0)]:
    # Window frame
    add_box(f"WinFrame_{side}", (x_off, win_y, win_z), (win_w + 0.3, 0.3, win_h + 0.3), mat_wood_dark)
    # Glass pane
    glass = add_box(f"WinGlass_{side}", (x_off, win_y - 0.05, win_z), (win_w, 0.05, win_h), mat_glass)

# --- INTERIOR: BROKEN PIANO (visible through right window) ---
# Place piano inside near right wall
piano_x, piano_y, piano_z = 3.2, 1.0, 0.0
piano_w, piano_d, piano_h = 1.8, 1.0, 2.8

# Piano body
add_box("Piano_Body", (piano_x, piano_y, piano_h/2), (piano_w, piano_d, piano_h), mat_piano)
# Piano lid (open, broken)
lid = add_box("Piano_Lid", (piano_x, piano_y + piano_d/2 + 0.3, piano_h + 0.2), (piano_w, 0.08, 0.8), mat_piano)
lid.rotation_euler = Euler((math.radians(-50), 0, 0))
# Keys
add_box("Piano_Keys", (piano_x, piano_y + piano_d/2 - 0.1, 0.15), (piano_w * 0.9, 0.3, 0.08), mat_piano_keys)
# Broken leg (one leg missing, piano tilted slightly)
add_box("Piano_Leg_FL", (piano_x - piano_w/2 + 0.1, piano_y + piano_d/2 - 0.1, 0.3), (0.1, 0.1, 0.6), mat_piano)
add_box("Piano_Leg_FR", (piano_x + piano_w/2 - 0.1, piano_y + piano_d/2 - 0.1, 0.3), (0.1, 0.1, 0.6), mat_piano)
# Tilt piano slightly
for obj_name in ["Piano_Body", "Piano_Lid", "Piano_Keys", "Piano_Leg_FL", "Piano_Leg_FR"]:
    obj = bpy.data.objects[obj_name]
    obj.rotation_euler = Euler((0, math.radians(3), 0))

# --- PORCH ---
porch_w, porch_d, porch_h = W + 2, 4, 0.2
porch = add_box("Porch", (0, D/2 + porch_d/2, porch_h/2), (porch_w, porch_d, porch_h), mat_wood_mid)

# Porch posts
for px in [-W/2 + 0.3, W/2 - 0.3]:
    add_box(f"Post_{px}", (px, D/2 + porch_d/2 - 0.2, H/2 + porch_h), (0.25, 0.25, H), mat_wood_dark)

# Porch roof
add_box("PorchRoof", (0, D/2 + porch_d/2, H + porch_h + 0.3), (porch_w, porch_d + 0.5, 0.4), mat_wood_dark)

# --- TUMBLEWEED on porch ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(1.5, D/2 + porch_d/2 - 0.5, porch_h + 0.4), segments=16, ring_count=12)
tumbleweed = bpy.context.object
tumbleweed.name = "Tumbleweed"
tumbleweed.data.materials.append(mat_tumbleweed)
# Make it look spiky: scale randomly
tumbleweed.scale = (1.1, 0.9, 1.0)
tumbleweed.rotation_euler = Euler((math.radians(20), math.radians(15), 0))

# --- SALOON SIGN above door ---
add_box("Sign", (0, D/2 + 0.2, H - 0.5), (3.0, 0.15, 1.0), mat_sign)
# Text "SALOON"
bpy.ops.object.text_add(location=(0, D/2 + 0.35, H - 0.5))
text_obj = bpy.context.object
text_obj.data.body = "SALOON"
text_obj.data.size = 0.6
text_obj.data.align_x = 'CENTER'
text_obj.data.align_y = 'CENTER'
text_obj.data.extrude = 0.02
text_obj.data.materials.append(mat_wood_dark)

# --- DUSTY GROUND DETAILS: scattered boards, barrels ---
# Barrel near door
bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=0.9, location=(-2.5, D/2 + 1.0, porch_h + 0.45), vertices=12)
barrel = bpy.context.object
barrel.name = "Barrel"
barrel.data.materials.append(mat_wood_mid)

# Scattered planks on ground
for i in range(5):
    x = random.uniform(-4, 4)
    y = random.uniform(D/2 + 2, D/2 + 6)
    z = 0.05
    plank = add_box(f"Plank_{i}", (x, y, z), (1.5 + random.random(), 0.15, 0.08), mat_wood_light)
    plank.rotation_euler = Euler((0, 0, random.uniform(0, math.pi)))

# --- LIGHTING: NOON HEAT ---
# Sun (harsh, high angle)
bpy.ops.object.light_add(type='SUN', location=(5, -5, 20))
sun = bpy.context.object
sun.name = "NoonSun"
sun.data.energy = 5.0
sun.data.angle = math.radians(5)
sun.rotation_euler = Euler((math.radians(10), 0, math.radians(30)))

# Fill light (warm, low intensity for heat haze feel)
bpy.ops.object.light_add(type='AREA', location=(0, D/2 + 8, 5))
fill = bpy.context.object
fill.name = "HeatFill"
fill.data.energy = 15.0
fill.data.size = 10
fill.data.color = (1.0, 0.95, 0.85)

# World: bright noon sky
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.85, 0.88, 0.95, 1.0)
    bg.inputs[1].default_value = 1.5

# --- CAMERA: looking at saloon from front-left, slightly low ---
bpy.ops.object.camera_add(location=(-6, D/2 + 12, 2.5))
cam = bpy.context.object
cam.name = "MainCam"
# Point at saloon center
target = Vector((0, D/2, 3))
direction = target - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# --- RENDER SETTINGS ---
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.view_settings.look = 'Medium High Contrast'
scene.view_settings.exposure = 0.3
