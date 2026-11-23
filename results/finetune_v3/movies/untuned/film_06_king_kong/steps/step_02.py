import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- MATERIALS (fixed: 4-component colors) ---
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    return mat

mat_kong = create_material('Kong', (0.25, 0.18, 0.12), 0.8)
mat_building = create_material('Building', (0.12, 0.12, 0.15), 0.6, 0.3)
mat_biplane = create_material('Biplane', (0.7, 0.1, 0.1), 0.4, 0.5)
mat_city = create_material('City', (0.08, 0.08, 0.1), 0.7, 0.2)
mat_ground = create_material('Ground', (0.05, 0.05, 0.06), 0.9)
mat_window_lit = create_material('WindowLit', (1.0, 0.9, 0.5), 0.3)
mat_window_dark = create_material('WindowDark', (0.02, 0.02, 0.03), 0.8)

# --- WORLD / SKY (night with stars) ---
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links
bg = world_nodes.get('Background')
bg.inputs['Color'].default_value = (0.01, 0.02, 0.06, 1.0)
bg.inputs['Strength'].default_value = 0.5

# --- LIGHTING ---
# Moonlight (key light)
moon = bpy.data.lights.new('Moon', type='SUN')
moon.energy = 3.0
moon.color = (0.7, 0.75, 1.0)
moon_obj = bpy.data.objects.new('Moon', moon)
bpy.context.collection.objects.link(moon_obj)
moon_obj.rotation_euler = (math.radians(45), math.radians(15), math.radians(30))

# City glow (warm ambient from below)
city_glow = bpy.data.lights.new('CityGlow', type='AREA')
city_glow.energy = 200
city_glow.size = 300
city_glow.color = (1.0, 0.8, 0.4)
city_glow_obj = bpy.data.objects.new('CityGlow', city_glow)
bpy.context.collection.objects.link(city_glow_obj)
city_glow_obj.location = (0, 0, 5)
city_glow_obj.rotation_euler = (0, 0, 0)

# Rim light for Kong
rim = bpy.data.lights.new('RimLight', type='SPOT')
rim.energy = 500
rim.color = (0.5, 0.6, 1.0)
rim_obj = bpy.data.objects.new('RimLight', rim)
bpy.context.collection.objects.link(rim_obj)
rim_obj.location = (-50, -50, 500)
rim_obj.rotation_euler = (math.radians(45), math.radians(45), 0)

# --- HELPER FUNCTIONS ---
def add_box(name, size, loc, mat, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

def add_sphere(name, radius, loc, mat, scale=(1,1,1), segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=segments, ring_count=rings)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj

def add_cylinder(name, radius, depth, loc, mat, rot=(0,0,0), verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    return obj

# --- EMPIRE STATE BUILDING (detailed) ---
# Main shaft (30 floors visible)
b1 = add_box('ESB_Main', (24, 24, 280), (0, 0, 140), mat_building)

# Tapered upper section
b2 = add_box('ESB_Upper', (18, 18, 70), (0, 0, 325), mat_building)

# Setback level
b3 = add_box('ESB_Setback', (14, 14, 40), (0, 0, 380), mat_building)

# Crown
b4 = add_box('ESB_Crown', (10, 10, 30), (0, 0, 415), mat_building)

# Spire base
b5 = add_box('ESB_SpireBase', (4, 4, 15), (0, 0, 440), mat_building)

# Spire
b6 = add_box('ESB_Spire', (1.5, 1.5, 25), (0, 0, 460), mat_building)

# Spire tip
b7 = add_box('ESB_SpireTip', (0.5, 0.5, 5), (0, 0, 475), mat_building)

# Add window grid - main shaft
for i in range(-10, 11):
    for j in range(-10, 11):
        for k in range(0, 28):
            x = i * 2.2
            y = j * 2.2
            z = 15 + k * 10
            if abs(i) <= 10 and abs(j) <= 10:
                # Random lit/dark windows
                if random.random() > 0.3:
                    win = add_box(f'WinM_{i}_{j}_{k}', (0.8, 0.8, 0.8), (x, y, z), mat_window_lit)
                else:
                    win = add_box(f'WinM_{i}_{j}_{k}', (0.8, 0.8, 0.8), (x, y, z), mat_window_dark)

# Upper section windows
for i in range(-7, 8):
    for j in range(-7, 8):
        for k in range(0, 7):
            x = i * 2.2
            y = j * 2.2
            z = 295 + k * 10
            if random.random() > 0.4:
                win = add_box(f'WinU_{i}_{j}_{k}', (0.7, 0.7, 0.7), (x, y, z), mat_window_lit)
            else:
                win = add_box(f'WinU_{i}_{j}_{k}', (0.7, 0.7, 0.7), (x, y, z), mat_window_dark)

# Setback windows
for i in range(-5, 6):
    for j in range(-5, 6):
        for k in range(0, 4):
            x = i * 2.2
            y = j * 2.2
            z = 365 + k * 10
            if random.random() > 0.5:
                win = add_box(f'WinS_{i}_{j}_{k}', (0.6, 0.6, 0.6), (x, y, z), mat_window_lit)
            else:
                win = add_box(f'WinS_{i}_{j}_{k}', (0.6, 0.6, 0.6), (x, y, z), mat_window_dark)

# Crown windows
for i in range(-3, 4):
    for j in range(-3, 4):
        for k in range(0, 3):
            x = i * 2.2
            y = j * 2.2
            z = 405 + k * 10
            if random.random() > 0.5:
                win = add_box(f'WinC_{i}_{j}_{k}', (0.5, 0.5, 0.5), (x, y, z), mat_window_lit)
            else:
                win = add_box(f'WinC_{i}_{j}_{k}', (0.5, 0.5, 0.5), (x, y, z), mat_window_dark)

# --- KONG (detailed, roaring) ---
# Torso
kong_torso = add_sphere('Kong_Torso', 18, (0, 0, 490), mat_kong, (1.2, 0.9, 1.4))

# Head
kong_head = add_sphere('Kong_Head', 10, (0, 0, 520), mat_kong, (1, 1, 1.1))

# Jaw (open mouth)
kong_jaw = add_sphere('Kong_Jaw', 6, (0, 3, 515), mat_kong, (1.2, 0.8, 0.6))

# Eyes
kong_eye_l = add_sphere('Kong_EyeL', 2, (-4, 7, 522), mat_window_lit, (1, 1, 0.8))
kong_eye_r = add_sphere('Kong_EyeR', 2, (4, 7, 522), mat_window_lit, (1, 1, 0.8))

# Left arm (raised, gripping)
kong_arm_l_upper = add_sphere('Kong_ArmLU', (7, 0, 505), mat_kong, (0.5, 0.5, 1.2))
kong_arm_l_lower = add_sphere('Kong_ArmLL', (-10, 5, 520), mat_kong, (0.4, 0.4, 1.0))
kong_hand_l = add_sphere('Kong_HandL', (-12, 8, 530), mat_kong, (0.6, 0.6, 0.5))

# Right arm (extended)
kong_arm_r_upper = add_sphere('Kong_ArmRU', (7, 0, 505), mat_kong, (0.5, 0.5, 1.2))
kong_arm_r_lower = add_sphere('Kong_ArmRL', (10, 5, 515), mat_kong, (0.4, 0.4, 1.0))
kong_hand_r = add_sphere('Kong_HandR', (12, 8, 525), mat_kong, (0.6, 0.6, 0.5))

# Legs (crouched)
kong_leg_l_upper = add_sphere('Kong_LegLU', (-10, 0, 475), mat_kong, (0.7, 0.7, 1.3))
kong_leg_l_lower = add_sphere('Kong_LegLL', (-12, 0, 455), mat_kong, (0.5, 0.5, 1.0))
kong_foot_l = add_sphere('Kong_FootL', (-14, 0, 445), mat_kong, (0.8, 1.2, 0.5))

kong_leg_r_upper = add_sphere('Kong_LegRU', (10, 0, 475), mat_kong, (0.7, 0.7, 1.3))
kong_leg_r_lower = add_sphere('Kong_LegRL', (12, 0, 455), mat_kong, (0.5, 0.5, 1.0))
kong_foot_r = add_sphere('Kong_FootR', (14, 0, 445), mat_kong, (0.8, 1.2, 0.5))

# --- BIPLANES (detailed) ---
def make_biplane(name, loc, rot_z):
    # Fuselage
    fus = add_cylinder(name+'_Fus', 1, 10, loc, mat_biplane, rot=(0, math.radians(90), rot_z))
    
    # Upper wing
    wing_up = add_box(name+'_WingUp', (14, 1, 0.3), (loc[0], loc[1], loc[2]+2), mat_biplane, rot=(0, 0, rot_z))
    
    # Lower wing
    wing_lo = add_box(name+'_WingLo', (14, 1, 0.3), (loc[0], loc[1], loc[2]-1), mat_biplane, rot=(0, 0, rot_z))
    
    # Struts
    strut_l = add_box(name+'_StrutL', (0.3, 0.3, 3), (loc[0]-4, loc[1], loc[2]+0.5), mat_biplane, rot=(0, 0, rot_z))
    strut_r = add_box(name+'_StrutR', (0.3, 0.3, 3), (loc[0]+4, loc[1], loc[2]+0.5), mat_biplane, rot=(0, 0, rot_z))
    
    # Tail
    tail_h = add_box(name+'_TailH', (0.3, 5, 1), (loc[0], loc[1], loc[2]-5), mat_biplane, rot=(0, 0, rot_z))
    tail_v = add_box(name+'_TailV', (0.3, 0.3, 3), (loc[0], loc[1], loc[2]-3), mat_biplane, rot=(0, 0, rot_z))
    
    # Propeller
    prop = add_box(name+'_Prop', (0.2, 4, 0.2), (loc[0], loc[1], loc[2]+5.5), mat_biplane, rot=(0, 0, rot_z))
    
    # Pilot
    pilot = add_sphere(name+'_Pilot', 1, (loc[0], loc[1], loc[2]+1), mat_kong)

# Circle of biplanes
num_planes = 10
radius_circle = 120
height_circle = 520
for i in range(num_planes):
    angle = (i / num_planes) * 2 * math.pi
    x = radius_circle * math.cos(angle)
    y = radius_circle * math.sin(angle)
    z = height_circle + 15 * math.sin(angle * 3)
    make_biplane(f'Biplane_{i}', (x, y, z), angle + math.pi/2)

# --- CITY BELOW (detailed) ---
random.seed(123)
for i in range(80):
    x = random.uniform(-250, 250)
    y = random.uniform(-250, 250)
    # Skip center where ESB is
    if abs(x) < 40 and abs(y) < 40:
        continue
    h = random.uniform(15, 100)
    w = random.uniform(4, 18)
    d = random.uniform(4, 18)
    city_bldg = add_box(f'City_{i}', (w, d, h), (x, y, h/2), mat_city)
    
    # Windows on city buildings
    num_floors = int(h / 6)
    for k in range(num_floors):
        for m in range(3):
            wx = x + random.uniform(-w/2+1, w/2-1)
            wy = y + random.uniform(-d/2+1, d/2-1)
            wz = 3 + k * 6
            if random.random() > 0.4:
                win = add_box(f'CityWin_{i}_{k}_{m}', (0.5, 0.5, 0.5), (wx, wy, wz), mat_window_lit)
            else:
                win = add_box(f'CityWin_{i}_{k}_{m}', (0.5, 0.5, 0.5), (wx, wy, wz), mat_window_dark)

# --- GROUND PLANE ---
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = 'Ground'
ground.data.materials.append(mat_ground)

# --- STARS ---
for i in range(200):
    x = random.uniform(-500, 500)
    y = random.uniform(-500, 500)
    z = random.uniform(300, 800)
    star = add_sphere(f'Star_{i}', 0.5, (x, y, z), mat_window_lit, (1, 1, 1), segments=8, rings=4)

# --- CAMERA ---
cam_data = bpy.data.cameras.new('Camera')
cam_data.lens = 40
cam_data.dof.use_dof = True
cam_data.dof.focus_distance = 150
cam_obj = bpy.data.objects.new('Camera', cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (100, 100, 580)
cam_obj.rotation_euler = (math.radians(75), 0, math.radians(45))
bpy.context.scene.camera = cam_obj

# --- RENDER SETTINGS ---
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Scene complete: Kong on Empire State Building, biplanes circling, city below, night sky with stars")
