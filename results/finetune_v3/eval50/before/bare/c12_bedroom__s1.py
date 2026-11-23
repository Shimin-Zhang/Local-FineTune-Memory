import bpy
import math
import random

# Clear existing mesh objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
def create_material(name, color, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

mat_wall = create_material("Wall", (0.85, 0.82, 0.78, 1.0), 0.8)
mat_floor = create_material("Floor", (0.6, 0.45, 0.3, 1.0), 0.7)
mat_wood = create_material("Wood", (0.45, 0.3, 0.18, 1.0), 0.6)
mat_wood_light = create_material("WoodLight", (0.7, 0.55, 0.35, 1.0), 0.5)
mat_mattress = create_material("Mattress", (0.9, 0.9, 0.85, 1.0), 0.9)
mat_pillow = create_material("Pillow", (0.95, 0.95, 0.95, 1.0), 0.9)
mat_blanket = create_material("Blanket", (0.3, 0.5, 0.7, 1.0), 0.9)
mat_rug = create_material("Rug", (0.7, 0.3, 0.3, 1.0), 0.95)
mat_glass = create_material("Glass", (0.7, 0.85, 0.95, 1.0), 0.1)
mat_frame = create_material("Frame", (0.9, 0.9, 0.9, 1.0), 0.4)
mat_metal = create_material("Metal", (0.6, 0.6, 0.6, 1.0), 0.3)
mat_shade = create_material("LampShade", (0.95, 0.9, 0.8, 1.0), 0.8)
mat_sky = create_material("Sky", (0.5, 0.7, 1.0, 1.0), 1.0)

# --- Helper Functions ---
def add_box(name, size, location, material, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return obj

def add_cylinder(name, radius, depth, location, material, rotation=(0,0,0), vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return obj

# --- Room Dimensions ---
room_w = 6.0
room_d = 5.0
room_h = 3.0
wall_t = 0.2

# --- Floor ---
floor = add_box("Floor", (room_w, room_d, wall_t), (0, 0, -wall_t/2), mat_floor)

# --- Walls ---
# Back wall (with window cutout)
# Left wall
wall_left = add_box("WallLeft", (wall_t, room_d, room_h), (-room_w/2 - wall_t/2, 0, room_h/2), mat_wall)
# Right wall
wall_right = add_box("WallRight", (wall_t, room_d, room_h), (room_w/2 + wall_t/2, 0, room_h/2), mat_wall)
# Front wall (opposite back)
wall_front = add_box("WallFront", (room_w, wall_t, room_h), (0, room_d/2 + wall_t/2, room_h/2), mat_wall)

# Back wall - split into sections around window
win_w = 2.0
win_h = 1.5
win_center_y = -room_d/2
win_center_z = 1.5
win_left_x = -win_w/2
win_right_x = win_w/2
win_bottom_z = win_center_z - win_h/2
win_top_z = win_center_z + win_h/2

# Back wall left of window
bw_left_w = (win_left_x + room_w/2)
bw_left = add_box("WallBackLeft", (bw_left_w, wall_t, room_h), 
                  (-room_w/2 + bw_left_w/2, win_center_y - wall_t/2, room_h/2), mat_wall)

# Back wall right of window
bw_right_w = (room_w/2 - win_right_x)
bw_right = add_box("WallBackRight", (bw_right_w, wall_t, room_h), 
                   (room_w/2 - bw_right_w/2, win_center_y - wall_t/2, room_h/2), mat_wall)

# Back wall below window
bw_below_h = win_bottom_z
bw_below = add_box("WallBackBelow", (win_w, wall_t, bw_below_h), 
                   (0, win_center_y - wall_t/2, bw_below_h/2), mat_wall)

# Back wall above window
bw_above_h = room_h - win_top_z
bw_above = add_box("WallBackAbove", (win_w, wall_t, bw_above_h), 
                   (0, win_center_y - wall_t/2, win_top_z + bw_above_h/2), mat_wall)

# --- Window ---
# Glass
glass = add_box("WindowGlass", (win_w, 0.02, win_h), (0, win_center_y, win_center_z), mat_glass)
# Window frame
frame_t = 0.08
# Top frame
add_box("WinFrameTop", (win_w + frame_t*2, frame_t, frame_t), (0, win_center_y, win_top_z + frame_t/2), mat_frame)
# Bottom frame
add_box("WinFrameBottom", (win_w + frame_t*2, frame_t, frame_t), (0, win_center_y, win_bottom_z - frame_t/2), mat_frame)
# Left frame
add_box("WinFrameLeft", (frame_t, frame_t, win_h + frame_t*2), (win_left_x - frame_t/2, win_center_y, win_center_z), mat_frame)
# Right frame
add_box("WinFrameRight", (frame_t, frame_t, win_h + frame_t*2), (win_right_x + frame_t/2, win_center_y, win_center_z), mat_frame)
# Middle vertical bar
add_box("WinFrameMidV", (frame_t/2, frame_t/2, win_h), (0, win_center_y, win_center_z), mat_frame)
# Middle horizontal bar
add_box("WinFrameMidH", (win_w, frame_t/2, frame_t/2), (0, win_center_y, win_center_z), mat_frame)

# Sky plane behind window
sky = add_box("Sky", (win_w*2, 0.01, win_h*2), (0, win_center_y - 0.5, win_center_z), mat_sky)

# --- Bed ---
bed_x = -1.5
bed_y = -1.0
bed_w = 1.8
bed_d = 2.2
bed_h = 0.5
bed_frame_h = 0.3

# Bed frame
bed_frame = add_box("BedFrame", (bed_w, bed_d, bed_frame_h), (bed_x, bed_y, bed_frame_h/2), mat_wood)

# Mattress
mattress_h = 0.2
mattress = add_box("Mattress", (bed_w - 0.1, bed_d - 0.1, mattress_h), 
                   (bed_x, bed_y, bed_frame_h + mattress_h/2), mat_mattress)

# Headboard
headboard_h = 1.0
headboard = add_box("Headboard", (bed_w, 0.1, headboard_h), 
                    (bed_x, bed_y - bed_d/2 - 0.05, bed_frame_h + headboard_h/2), mat_wood)

# Pillows
pillow_w = 0.5
pillow_d = 0.3
pillow_h = 0.15
pillow_z = bed_frame_h + mattress_h + pillow_h/2
pillow_y = bed_y - bed_d/2 + 0.4

# Left pillow
p1 = add_box("PillowLeft", (pillow_w, pillow_d, pillow_h), (bed_x - bed_w/4, pillow_y, pillow_z), mat_pillow)
p1.rotation_euler = (0, 0, math.radians(5))

# Right pillow
p2 = add_box("PillowRight", (pillow_w, pillow_d, pillow_h), (bed_x + bed_w/4, pillow_y, pillow_z), mat_pillow)
p2.rotation_euler = (0, 0, math.radians(-5))

# Blanket
blanket_h = 0.05
blanket = add_box("Blanket", (bed_w - 0.15, bed_d * 0.6, blanket_h), 
                  (bed_x, bed_y + bed_d * 0.15, bed_frame_h + mattress_h + blanket_h/2), mat_blanket)

# --- Nightstand ---
ns_x = bed_x + bed_w/2 + 0.5
ns_y = bed_y - bed_d/2 + 0.3
ns_w = 0.5
ns_d = 0.5
ns_h = 0.6

# Nightstand body
nightstand = add_box("Nightstand", (ns_w, ns_d, ns_h), (ns_x, ns_y, ns_h/2), mat_wood_light)

# Nightstand top
ns_top_t = 0.05
ns_top = add_box("NightstandTop", (ns_w + 0.05, ns_d + 0.05, ns_top_t), 
                 (ns_x, ns_y, ns_h + ns_top_t/2), mat_wood_light)

# Drawer
drawer_h = ns_h * 0.35
drawer = add_box("Drawer", (ns_w - 0.05, 0.02, drawer_h), 
                 (ns_x, ns_y + ns_d/2 + 0.01, ns_h * 0.5), mat_wood)
# Drawer handle
handle = add_box("DrawerHandle", (0.15, 0.03, 0.03), 
                 (ns_x, ns_y + ns_d/2 + 0.04, ns_h * 0.5), mat_metal)

# --- Lamp ---
lamp_x = ns_x
lamp_y = ns_y
lamp_base_z = ns_h + ns_top_t

# Lamp base
lamp_base_r = 0.08
lamp_base_h = 0.03
lamp_base = add_cylinder("LampBase", lamp_base_r, lamp_base_h, (lamp_x, lamp_y, lamp_base_z + lamp_base_h/2), mat_metal)

# Lamp stem
stem_r = 0.02
stem_h = 0.35
stem = add_cylinder("LampStem", stem_r, stem_h, (lamp_x, lamp_y, lamp_base_z + lamp_base_h + stem_h/2), mat_metal)

# Lamp shade
shade_r = 0.15
shade_h = 0.2
shade_z = lamp_base_z + lamp_base_h + stem_h + shade_h/2
shade = add_cylinder("LampShade", shade_r, shade_h, (lamp_x, lamp_y, shade_z), mat_shade, vertices=24)

# Light inside lamp
bpy.ops.object.light_add(type='POINT', location=(lamp_x, lamp_y, shade_z))
light = bpy.context.active_object
light.name = "LampLight"
light.data.energy = 50
light.data.color = (1.0, 0.9, 0.7)

# --- Wardrobe ---
ward_x = room_w/2 - 0.8
ward_y = 1.0
ward_w = 1.2
ward_d = 0.6
ward_h = 2.0

# Wardrobe body
wardrobe = add_box("Wardrobe", (ward_w, ward_d, ward_h), (ward_x, ward_y, ward_h/2), mat_wood)

# Wardrobe doors
door_gap = 0.02
door_w = (ward_w - door_gap) / 2
door_h = ward_h - 0.1
door_d = 0.03

# Left door
door_left = add_box("WardrobeDoorLeft", (door_w, door_d, door_h), 
                    (ward_x - door_w/2 - door_gap/2, ward_y + ward_d/2 + door_d/2, door_h/2 + 0.05), mat_wood_light)
# Right door
door_right = add_box("WardrobeDoorRight", (door_w, door_d, door_h), 
                     (ward_x + door_w/2 + door_gap/2, ward_y + ward_d/2 + door_d/2, door_h/2 + 0.05), mat_wood_light)

# Door handles
handle_h = 0.1
handle_r = 0.015
# Left door handle
h1 = add_cylinder("WardrobeHandleLeft", handle_r, handle_h, 
                  (ward_x - door_gap/2 - 0.1, ward_y + ward_d/2 + door_d + 0.02, door_h/2 + 0.05), mat_metal)
h1.rotation_euler = (0, math.radians(90), 0)
# Right door handle
h2 = add_cylinder("WardrobeHandleRight", handle_r, handle_h, 
                  (ward_x + door_gap/2 + 0.1, ward_y + ward_d/2 + door_d + 0.02, door_h/2 + 0.05), mat_metal)
h2.rotation_euler = (0, math.radians(90), 0)

# --- Rug ---
rug_x = -0.5
rug_y = 0.5
rug_w = 2.5
rug_d = 1.8
rug_h = 0.02

rug = add_box("Rug", (rug_w, rug_d, rug_h), (rug_x, rug_y, rug_h/2), mat_rug)

# --- Sunlight through window ---
bpy.ops.object.light_add(type='SUN', location=(0, -3, 4))
sun = bpy.context.active_object
sun.name = "Sunlight"
sun.data.energy = 3
sun.rotation_euler = (math.radians(60), 0, 0)

# --- Ambient light ---
bpy.ops.object.light_add(type='AREA', location=(0, 0, room_h - 0.1))
area = bpy.context.active_object
area.name = "Ambient"
area.data.energy = 20
area.data.size = 3
area.rotation_euler = (math.radians(180), 0, 0)

# --- Set up camera ---
bpy.ops.object.camera_add(location=(3, 3, 2.5))
cam = bpy.context.active_object
cam.name = "BedroomCamera"
# Point camera at center of room
direction = (0, 0, 1) - cam.location
rot_quat = direction.to_track_quat('Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = cam

# --- Render settings ---
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.film_transparent = False

print("Bedroom scene built successfully!")
