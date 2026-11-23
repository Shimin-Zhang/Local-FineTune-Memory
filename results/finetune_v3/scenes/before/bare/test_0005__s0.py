import bpy
import math
import random

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Collections
def get_or_create_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

col_water = get_or_create_collection("Water")
col_dock = get_or_create_collection("Dock")
col_boathouse = get_or_create_collection("Boathouse")
col_plane = get_or_create_collection("Plane")
col_ramp = get_or_create_collection("Ramp")
col_gas = get_or_create_collection("GasPump")
col_mountains = get_or_create_collection("Mountains")
col_ground = get_or_create_collection("Ground")

def add_to_collection(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

def set_material(obj, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=f"Mat_{obj.name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    obj.data.materials.append(mat)
    return mat

def add_box(name, size, location, rotation=(0,0,0), color=(0.5,0.5,0.5), roughness=0.5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(scale=True)
    set_material(obj, color, roughness)
    return obj

def add_cylinder(name, radius, depth, location, rotation=(0,0,0), color=(0.5,0.5,0.5), roughness=0.5, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, rotation=rotation, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    set_material(obj, color, roughness)
    return obj

def add_sphere(name, radius, location, color=(0.5,0.5,0.5), roughness=0.5):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=32, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    set_material(obj, color, roughness)
    return obj

# ===================== WATER =====================
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
water = bpy.context.active_object
water.name = "Water"
mat_water = bpy.data.materials.new("WaterMat")
mat_water.use_nodes = True
bsdf = mat_water.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.05, 0.15, 0.3, 1.0)
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Metallic"].default_value = 0.3
bsdf.inputs["Transmission Weight"].default_value = 0.5
water.data.materials.append(mat_water)
add_to_collection(water, col_water)

# ===================== FLOATING DOCK =====================
# Main dock platform
dock_main = add_box("Dock_Main", (12, 4, 0.3), (0, 0, 0.5), color=(0.4, 0.3, 0.2))
add_to_collection(dock_main, col_dock)

# Dock pilings (posts)
piling_positions = [(-5, -1.5), (-5, 1.5), (5, -1.5), (5, 1.5), (0, -1.5), (0, 1.5)]
for i, (px, py) in enumerate(piling_positions):
    piling = add_cylinder(f"Dock_Piling_{i}", 0.15, 2.5, (px, py, -0.75), color=(0.3, 0.2, 0.15))
    add_to_collection(piling, col_dock)

# Side dock extending to the right
dock_side = add_box("Dock_Side", (8, 2.5, 0.3), (10, 0, 0.5), color=(0.4, 0.3, 0.2))
add_to_collection(dock_side, col_dock)

# Side dock pilings
for i, (px, py) in enumerate([(7, -1), (7, 1), (13, -1), (13, 1)]):
    piling = add_cylinder(f"Dock_Side_Piling_{i}", 0.15, 2.5, (px, py, -0.75), color=(0.3, 0.2, 0.15))
    add_to_collection(piling, col_dock)

# ===================== BOATHOUSE =====================
# Boathouse body
boathouse_body = add_box("Boathouse_Body", (5, 4, 3), (-10, 0, 1.5), color=(0.5, 0.4, 0.3))
add_to_collection(boathouse_body, col_boathouse)

# Boathouse roof
bpy.ops.mesh.primitive_cone_add(radius1=3.5, radius2=0, depth=1.5, location=(-10, 0, 3.75), vertices=4, rotation=(0, 0, math.pi/4))
roof = bpy.context.active_object
roof.name = "Boathouse_Roof"
roof.scale = (1.3, 1.0, 1.0)
bpy.ops.object.transform_apply(scale=True)
set_material(roof, (0.2, 0.15, 0.1), 0.6)
add_to_collection(roof, col_boathouse)

# Boathouse door
door = add_box("Boathouse_Door", (1.5, 0.1, 2.5), (-10, 2.05, 1.25), color=(0.25, 0.15, 0.1))
add_to_collection(door, col_boathouse)

# Boathouse windows
for wx in [-11.5, -8.5]:
    window = add_box(f"Boathouse_Window_{wx}", (0.8, 0.1, 0.8), (wx, 2.05, 2.0), color=(0.6, 0.7, 0.8), roughness=0.2)
    add_to_collection(window, col_boathouse)

# Boathouse on stilts over water
for i, (sx, sy) in enumerate([(-12, -1.5), (-12, 1.5), (-8, -1.5), (-8, 1.5)]):
    stilt = add_cylinder(f"Boathouse_Stilt_{i}", 0.12, 2.0, (sx, sy, -0.5), color=(0.3, 0.2, 0.15))
    add_to_collection(stilt, col_boathouse)

# ===================== PLANE ON CRADLE =====================
# Cradle (floating platform)
cradle = add_box("Cradle", (6, 4, 0.5), (18, 0, 0.4), color=(0.3, 0.3, 0.35))
add_to_collection(cradle, col_plane)

# Cradle supports
for i, (cx, cy) in enumerate([(16, -1.5), (16, 1.5), (20, -1.5), (20, 1.5)]):
    support = add_cylinder(f"Cradle_Support_{i}", 0.15, 2.0, (cx, cy, -0.5), color=(0.2, 0.2, 0.2))
    add_to_collection(support, col_plane)

# Plane fuselage
fuselage = add_cylinder("Plane_Fuselage", 0.8, 5, (18, 0, 1.5), rotation=(math.pi/2, 0, 0), color=(0.85, 0.85, 0.9), roughness=0.3)
add_to_collection(fuselage, col_plane)

# Nose cone
bpy.ops.mesh.primitive_cone_add(radius1=0.8, radius2=0.1, depth=1.5, location=(18, -2.75, 1.5), rotation=(math.pi/2, 0, 0))
nose = bpy.context.active_object
nose.name = "Plane_Nose"
set_material(nose, (0.85, 0.85, 0.9), 0.3)
add_to_collection(nose, col_plane)

# Tail
tail = add_box("Plane_Tail", (0.3, 2.5, 1.5), (18, 2.5, 2.2), color=(0.85, 0.85, 0.9), roughness=0.3)
add_to_collection(tail, col_plane)

# Tail horizontal stabilizer
stab = add_box("Plane_Stabilizer", (1.5, 0.3, 0.8), (18, 2.5, 1.8), color=(0.85, 0.85, 0.9), roughness=0.3)
add_to_collection(stab, col_plane)

# Wings
wing_left = add_box("Plane_Wing_Left", (4, 0.2, 0.6), (18, -1.5, 1.5), color=(0.85, 0.85, 0.9), roughness=0.3)
add_to_collection(wing_left, col_plane)
wing_right = add_box("Plane_Wing_Right", (4, 0.2, 0.6), (18, 1.5, 1.5), color=(0.85, 0.85, 0.9), roughness=0.3)
add_to_collection(wing_right, col_plane)

# Propeller
prop = add_cylinder("Plane_Propeller", 0.05, 2.0, (18, -3.5, 1.5), rotation=(0, math.pi/2, 0), color=(0.1, 0.1, 0.1), roughness=0.4)
add_to_collection(prop, col_plane)
prop2 = add_cylinder("Plane_Propeller2", 0.05, 2.0, (18, -3.5, 1.5), rotation=(0, math.pi/2 + math.pi/2, 0), color=(0.1, 0.1, 0.1), roughness=0.4)
add_to_collection(prop2, col_plane)

# Cockpit
cockpit = add_box("Plane_Cockpit", (1.5, 1.2, 0.8), (18, 0, 2.2), color=(0.3, 0.5, 0.7), roughness=0.2)
add_to_collection(cockpit, col_plane)

# ===================== RAMP =====================
# Ramp from shore to dock
ramp = add_box("Ramp", (6, 3, 0.2), (-3, 0, 0.8), rotation=(0, math.radians(8), 0), color=(0.4, 0.35, 0.25))
add_to_collection(ramp, col_ramp)

# Ramp supports
for i, (rx, ry) in enumerate([(-5.5, -1), (-5.5, 1), (-0.5, -1), (-0.5, 1)]):
    support = add_cylinder(f"Ramp_Support_{i}", 0.12, 1.5, (rx, ry, 0.1), color=(0.3, 0.2, 0.15))
    add_to_collection(support, col_ramp)

# ===================== GAS PUMP =====================
# Gas pump base
pump_base = add_box("GasPump_Base", (1.2, 1.0, 0.8), (6, 3, 0.4), color=(0.2, 0.2, 0.25))
add_to_collection(pump_base, col_gas)

# Gas pump body
pump_body = add_box("GasPump_Body", (0.8, 0.6, 1.2), (6, 3, 1.4), color=(0.15, 0.15, 0.2))
add_to_collection(pump_body, col_gas)

# Gas pump display
display = add_box("GasPump_Display", (0.5, 0.1, 0.3), (6, 2.7, 1.7), color=(0.1, 0.3, 0.1), roughness=0.3)
add_to_collection(display, col_gas)

# Gas pump nozzle
nozzle = add_cylinder("GasPump_Nozzle", 0.05, 0.8, (6.4, 3, 1.5), rotation=(math.pi/4, 0, 0), color=(0.1, 0.1, 0.1))
add_to_collection(nozzle, col_gas)

# Gas pump hose
bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.04, location=(6.5, 3, 1.2), rotation=(0, math.pi/2, 0))
hose = bpy.context.active_object
hose.name = "GasPump_Hose"
set_material(hose, (0.1, 0.1, 0.1), 0.6)
add_to_collection(hose, col_gas)

# ===================== COLD BLUE MOUNTAINS =====================
def add_mountain(name, location, scale, color_base):
    bpy.ops.mesh.primitive_cone_add(radius1=scale[0], radius2=0, depth=scale[2], location=location, vertices=6)
    mtn = bpy.context.active_object
    mtn.name = name
    mtn.scale = (1, 1, 1)
    # Make it look more mountain-like by scaling
    mtn.scale = (scale[0], scale[1], scale[2])
    bpy.ops.object.transform_apply(scale=True)
    # Displace for roughness
    mod = mtn.modifiers.new("Displace", 'DISPLACE')
    tex = bpy.data.textures.new(f"Tex_{name}", 'CLOUDS')
    tex.noise_scale = 0.5
    mod.texture = tex
    mod.strength = 0.3 * scale[2]
    set_material(mtn, color_base, 0.7)
    return mtn

# Mountains in the background (negative Y direction)
mountain_data = [
    ("Mountain_1", (-30, -80, 15), (15, 12, 25), (0.15, 0.2, 0.35)),
    ("Mountain_2", (-10, -90, 20), (20, 15, 35), (0.12, 0.18, 0.32)),
    ("Mountain_3", (10, -85, 18), (18, 14, 30), (0.14, 0.2, 0.34)),
    ("Mountain_4", (30, -95, 22), (22, 16, 40), (0.1, 0.15, 0.3)),
    ("Mountain_5", (50, -80, 14), (14, 10, 22), (0.16, 0.22, 0.36)),
    ("Mountain_6", (-50, -90, 16), (16, 12, 26), (0.13, 0.19, 0.33)),
    ("Mountain_7", (70, -85, 12), (12, 10, 20), (0.17, 0.23, 0.37)),
    ("Mountain_8", (-70, -80, 10), (10, 8, 18), (0.18, 0.24, 0.38)),
]

for name, loc, scale, color in mountain_data:
    mtn = add_mountain(name, loc, scale, color)
    add_to_collection(mtn, col_mountains)

# Snow caps on some mountains
for name, loc, scale, color in mountain_data[:5]:
    cap_loc = (loc[0], loc[1], loc[2] + scale[2]