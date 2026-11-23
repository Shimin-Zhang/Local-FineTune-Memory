import bpy
import math
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Collections
def get_or_create_collection(name):
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col

col_ground = get_or_create_collection("Ground")
col_garage = get_or_create_collection("Garage")
col_buses = get_or_create_collection("Buses")
col_pit = get_or_create_collection("Pit")
col_fuel = get_or_create_collection("Fuel")
col_board = get_or_create_collection("Timetable")

# Materials
mat_ground = bpy.data.materials.new("Concrete")
mat_ground.use_nodes = True
bsdf = mat_ground.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.35, 0.35, 0.35, 1)
bsdf.inputs["Roughness"].default_value = 0.9

mat_brick = bpy.data.materials.new("Brick")
mat_brick.use_nodes = True
bsdf = mat_brick.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.45, 0.15, 0.1, 1)
bsdf.inputs["Roughness"].default_value = 0.85

mat_roof = bpy.data.materials.new("Roof")
mat_roof.use_nodes = True
bsdf = mat_roof.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1)
bsdf.inputs["Roughness"].default_value = 0.7

mat_bus1 = bpy.data.materials.new("Bus1_Green")
mat_bus1.use_nodes = True
bsdf = mat_bus1.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.35, 0.15, 1)
bsdf.inputs["Roughness"].default_value = 0.6

mat_bus2 = bpy.data.materials.new("Bus2_Red")
mat_bus2.use_nodes = True
bsdf = mat_bus2.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.5, 0.1, 0.1, 1)
bsdf.inputs["Roughness"].default_value = 0.6

mat_pit = bpy.data.materials.new("Pit_Dark")
mat_pit.use_nodes = True
bsdf = mat_pit.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.05, 1)
bsdf.inputs["Roughness"].default_value = 0.95

mat_fuel = bpy.data.materials.new("FuelPump")
mat_fuel.use_nodes = True
bsdf = mat_fuel.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.25, 1)
bsdf.inputs["Metallic"].default_value = 0.7
bsdf.inputs["Roughness"].default_value = 0.4

mat_wood = bpy.data.materials.new("Wood")
mat_wood.use_nodes = True
bsdf = mat_wood.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.35, 0.2, 0.1, 1)
bsdf.inputs["Roughness"].default_value = 0.8

mat_white = bpy.data.materials.new("White")
mat_white.use_nodes = True
bsdf = mat_white.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1)
bsdf.inputs["Roughness"].default_value = 0.5

mat_glass = bpy.data.materials.new("Glass")
mat_glass.use_nodes = True
bsdf = mat_glass.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.9, 1.0, 1)
bsdf.inputs["Roughness"].default_value = 0.1
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Alpha"].default_value = 0.3
mat_glass.blend_method = 'BLEND'

# Helper: add object to collection
def add_to_collection(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

# Helper: cube
def make_cube(name, size, loc, mat, col):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    add_to_collection(obj, col)
    return obj

# Helper: cylinder
def make_cyl(name, r, depth, loc, mat, col, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    add_to_collection(obj, col)
    return obj

# Helper: scale object
def scale_obj(obj, sx, sy, sz):
    obj.scale = (sx, sy, sz)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(scale=True)

# ===== GROUND =====
ground = make_cube("Ground", 40, (0, 0, -0.05), mat_ground, col_ground)
scale_obj(ground, 1, 1, 0.1)

# ===== BRICK GARAGE =====
# Garage: 12m wide (x), 8m deep (y), 5m tall
gx, gy, gz = 0, 5, 2.5  # center
gw, gd, gh = 12, 8, 5

# Walls (4 sides, with opening at front)
# Back wall
make_cube("Garage_Back", (gw, 0.3, gh), (gx, gy + gd/2 - 0.15, gh/2), mat_brick, col_garage)
# Left wall
make_cube("Garage_Left", (0.3, gd, gh), (gx - gw/2 + 0.15, gy, gh/2), mat_brick, col_garage)
# Right wall
make_cube("Garage_Right", (0.3, gd, gh), (gx + gw/2 - 0.15, gy, gh/2), mat_brick, col_garage)
# Front wall - two segments leaving 8m opening in center
front_seg_w = (gw - 8) / 2  # 2m each side
make_cube("Garage_Front_L", (front_seg_w, 0.3, gh), (gx - gw/2 + front_seg_w/2, gy - gd/2 + 0.15, gh/2), mat_brick, col_garage)
make_cube("Garage_Front_R", (front_seg_w, 0.3, gh), (gx + gw/2 - front_seg_w/2, gy - gd/2 + 0.15, gh/2), mat_brick, col_garage)
# Lintel above opening
make_cube("Garage_Lintel", (8, 0.3, 1.5), (gx, gy - gd/2 + 0.15, gh - 0.75), mat_brick, col_garage)

# Roof
roof = make_cube("Garage_Roof", (gw + 0.6, gd + 0.6, 0.3), (gx, gy, gh + 0.15), mat_roof, col_garage)

# ===== TWO BUSES NOSE TO NOSE =====
# Bus dimensions: 10m long, 2.5m wide, 3m tall
# Bus 1: nose pointing +Y, positioned at x=-3, y=5
# Bus 2: nose pointing -Y, positioned at x=+3, y=5
# Noses meet around y=5

def make_bus(name, loc, rot_z, mat, col):
    objs = []
    # Body
    body = make_cube(name + "_Body", (2.5, 10, 3), (loc[0], loc[1], 1.5), mat, col)
    objs.append(body)
    # Cabin (front) - slightly protruding
    # For bus 1 (nose +Y): cabin at +Y end
    if rot_z == 0:  # nose +Y
        cabin_loc = (loc[0], loc[1] + 5, 1.5)
    else:  # nose -Y
        cabin_loc = (loc[0], loc[1] - 5, 1.5)
    cabin = make_cube(name + "_Cabin", (2.5, 1.5, 3), cabin_loc, mat, col)
    objs.append(cabin)
    # Windshield
    if rot_z == 0:
        wind_loc = (loc[0], loc[1] + 5.75, 2.0)
    else:
        wind_loc = (loc[0], loc[1] - 5.75, 2.0)
    windshield = make_cube(name + "_Windshield", (2.2, 0.1, 1.2), wind_loc, mat_glass, col)
    objs.append(windshield)
    # Wheels (4)
    wheel_positions = [
        (loc[0] - 1.2, loc[1] + 3.5, 0.5),
        (loc[0] + 1.2, loc[1] + 3.5, 0.5),
        (loc[0] - 1.2, loc[1] - 3.5, 0.5),
        (loc[0] + 1.2, loc[1] - 3.5, 0.5),
    ]
    for i, wp in enumerate(wheel_positions):
        wheel = make_cyl(name + f"_Wheel{i}", 0.5, 0.3, wp, mat_pit, col, verts=16)
        wheel.rotation_euler = (0, math.radians(90), 0)
        objs.append(wheel)
    return objs

# Bus 1: green, nose pointing +Y (toward center)
make_bus("Bus1", (-3, 0, 0), 0, mat_bus1, col_buses)
# Bus 2: red, nose pointing -Y (toward center)
make_bus("Bus2", (3, 10, 0), math.radians(180), mat_bus2, col_buses)

# Actually let me reposition so noses are close together
# Bus 1 at x=-3, y=0, body from y=-5 to y=5, nose at y=5
# Bus 2 at x=3, y=10, body from y=5 to y=15, nose at y=5
# Noses meet at y=5, x=-3 and x=3 -- that's 6m apart, not nose-to-nose
# Let me put them closer: x=-2.5 and x=2.5, and align noses

# Delete and redo buses properly
for obj in list(col_buses.objects):
    bpy.data.objects.remove(obj, do_unlink=True)

# Bus 1: centered at (-2.5, 2, 0), body y from -3 to 7, nose at y=7
# Bus 2: centered at (2.5, 2, 0), body y from -3 to 7, nose at y=-3... 
# Let me think differently. 
# Nose-to-nose: Bus 1 nose points +Y, Bus 2 nose points -Y
# Bus 1: body from y=-5 to y=5, nose at y=5 (cabin at y=5)
# Bus 2: body from y=5 to y=15, nose at y=5 (cabin at y=5)
# Place them at x=-2.5 and x=2.5 so they're side by side with noses meeting at y=5

# Bus 1
b1x, b1y = -2.5, 0
body1 = make_cube("Bus1_Body", (2.4, 10, 2.8), (b1x, b1y, 1.4), mat_bus1, col_buses)
cabin1 = make_cube("Bus1_Cabin", (2.4, 1.5, 2.8), (b1x, b1y + 5, 1.4), mat_bus1, col_buses)
wind1 = make_cube("Bus1_Windshield", (2.0, 0.1, 1.1), (b1x, b1y + 5.75, 1.9), mat_glass, col_buses)
for i, dy in enumerate([3.5, -3.5]):
    for dx in [-1.1, 1.1]:
        w = make_cyl(f"Bus1_Wheel{i}_{dx}", 0.45, 0.3, (b1x + dx, b1y + dy, 0.45), mat_pit, col_buses, verts=16)
        w.rotation_euler = (0, math.radians(90), 0)

# Bus 2
b2x, b2y = 2.5, 10
body2 = make_cube("Bus2_Body", (2.4, 10, 2.8), (b2x, b2y, 1.4), mat_bus2, col_buses)
cabin2 = make_cube("Bus2_Cabin", (2.4, 1.5, 2.8), (b2x, b2y - 5, 1.4), mat_bus2, col_buses)
wind2 = make_cube("Bus2_Windshield", (2.0, 0.1, 1.1), (b2x, b2y - 5.75, 1.9), mat_glass, col_buses)
for i, dy in enumerate([3.5, -3.5]):
    for dx in [-1.1, 1.1]:
        w = make_cyl(f"Bus2_Wheel{i}_{dx}", 0.45, 0.3, (b2x + dx, b2y + dy, 0.45), mat_pit, col_buses, verts=16)

# ===== PIT (under bus 1) =====
# A rectangular pit in the ground
pit_w, pit_d, pit_h = 3, 11, 0.8
pit_x, pit_y = -2.5, 0
# Create pit by making a dark box slightly below ground
pit = make_cube("Pit", (pit_w, pit_d, pit_h), (pit_x, pit_y, -pit_h/2 + 0.01), mat_pit, col_pit)
# Pit edges (concrete border)
for dx in [-pit_w/2, pit_w/2]:
    make_cube(f"Pit_Edge_{dx}", (0.2, pit_d, 0.15), (pit_x + dx, pit_y, 0.075), mat_ground, col_pit)
for dy in [-pit_d/2, pit_d/2]:
    make_cube(f"Pit_EdgeY_{dy}", (pit_w, 0.2, 0.15), (pit_x, pit_y + dy, 0.075), mat_ground, col_pit)

# ===== FUEL PUMP =====
fp_x, fp_y = -8, 2
# Base
make_cube("Fuel_Base", (1.5, 1.5, 0.3), (fp_x, fp_y, 0.15), mat_ground, col_fuel)
# Pump body
make_cube("Fuel_Body", (0.8, 0.6, 1.5), (fp_x, fp_y, 1.05), mat_fuel, col_fuel)
# Display
make_cube("Fuel_Display", (0.5, 0.05, 0.3), (fp_x, fp_y - 0.33, 1.3), mat_white, col_fuel)
# Nozzle holder
make_cube("Fuel_Holder", (0.15, 0.15, 0.4), (fp_x + 0.5, fp_y, 1.0), mat_fuel, col_fuel)
# Hose (simple cylinder)
hose = make_cyl("Fuel_Hose", 0.04, 1.0, (fp_x + 0.5, fp_y + 0.5, 0.8), mat_pit, col_fuel, verts=8)
hose.rotation_euler = (math.radians(45), 0, 0)

# ===== WOODEN TIMETABLE BOARD =====
tb_x, tb_y = 8, 2
# Posts
make_cube("Board_Post_L", (0.15, 0.15, 2.5), (tb_x - 1.5, tb_y, 1