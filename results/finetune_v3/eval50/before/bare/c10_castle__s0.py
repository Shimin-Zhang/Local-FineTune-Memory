import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
def create_material(name, color, roughness=0.8):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return mat

stone_mat = create_material("Stone", (0.5, 0.48, 0.45, 1), 0.9)
dark_stone_mat = create_material("DarkStone", (0.3, 0.28, 0.25, 1), 0.9)
wood_mat = create_material("Wood", (0.35, 0.2, 0.1, 1), 0.7)
water_mat = create_material("Water", (0.1, 0.3, 0.5, 1), 0.1)
water_mat.blend_method = 'BLEND'
grass_mat = create_material("Grass", (0.2, 0.4, 0.1, 1), 0.95)
gate_mat = create_material("GateWood", (0.25, 0.12, 0.05, 1), 0.6)

# --- Helper functions ---
def create_cylinder(name, radius, depth, location, material, segments=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=segments, radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

def create_cube(name, size, location, material, scale=(1,1,1)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def create_cone(name, radius1, radius2, depth, location, material, segments=32):
    bpy.ops.mesh.primitive_cone_add(vertices=segments, radius1=radius1, radius2=radius2, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# --- Ground ---
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(grass_mat)

# --- Moat ---
# Outer ring (moat)
moat_outer = 25
moat_inner = 20
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=moat_outer, depth=0.5, location=(0, 0, -0.25))
moat_outer_obj = bpy.context.active_object
moat_outer_obj.name = "MoatOuter"
moat_outer_obj.data.materials.append(water_mat)

# Inner fill to make it a ring (we'll use a torus-like approach or just a flat ring)
# Simpler: create a large flat cylinder for water and a smaller one for land
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=moat_inner, depth=0.5, location=(0, 0, -0.25))
moat_inner_obj = bpy.context.active_object
moat_inner_obj.name = "MoatInner"
moat_inner_obj.data.materials.append(grass_mat)

# Actually, let's do it differently: 
# 1. Big water cylinder
# 2. Slightly smaller land cylinder on top
# 3. The castle sits on the land

# Remove previous moat objects
bpy.data.objects.remove(moat_outer_obj, do_unlink=True)
bpy.data.objects.remove(moat_inner_obj, do_unlink=True)

# Moat: water surface
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=25, depth=0.1, location=(0, 0, -0.5))
moat_water = bpy.context.active_object
moat_water.name = "MoatWater"
moat_water.data.materials.append(water_mat)

# Land inside moat
bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=20, depth=0.5, location=(0, 0, -0.25))
land = bpy.context.active_object
land.name = "Land"
land.data.materials.append(grass_mat)

# --- Castle Dimensions ---
wall_length = 30
wall_height = 8
wall_thickness = 2
tower_radius = 4
tower_height = 12
tower_cone_height = 6

# Corner positions for towers
corners = [
    (-wall_length/2, -wall_length/2),
    (wall_length/2, -wall_length/2),
    (wall_length/2, wall_length/2),
    (-wall_length/2, wall_length/2)
]

# --- Towers ---
for i, (cx, cy) in enumerate(corners):
    # Tower base
    tower = create_cylinder(f"Tower_{i}", tower_radius, tower_height, (cx, cy, tower_height/2), stone_mat)
    # Tower cone roof
    cone = create_cone(f"TowerRoof_{i}", tower_radius + 0.5, 0, tower_cone_height, (cx, cy, tower_height + tower_cone_height/2), dark_stone_mat)
    # Small battlements on top of tower (simple ring of small cubes)
    battlement_count = 8
    for j in range(battlement_count):
        angle = (j / battlement_count) * 2 * math.pi
        bx = cx + (tower_radius - 0.3) * math.cos(angle)
        by = cy + (tower_radius - 0.3) * math.sin(angle)
        create_cube(f"Battlement_{i}_{j}", 1, (bx, by, tower_height + 0.5), stone_mat, scale=(0.8, 0.8, 0.5))

# --- Walls ---
# Four walls connecting the towers
# Wall 1: from corner 0 to corner 1 (south wall, y = -wall_length/2)
# Wall 2: from corner 1 to corner 2 (east wall, x = wall_length/2)
# Wall 3: from corner 2 to corner 3 (north wall, y = wall_length/2)
# Wall 4: from corner 3 to corner 0 (west wall, x = -wall_length/2)

# South wall (with gate)
# Gate is in the middle of the south wall
gate_width = 4
gate_height = 6

# South wall: two segments with a gap for the gate
south_wall_y = -wall_length/2
# Left segment
left_seg_length = (wall_length - gate_width) / 2
left_seg_center_x = -gate_width/2 - left_seg_length/2
create_cube("Wall_South_Left", 1, (left_seg_center_x, south_wall_y, wall_height/2), stone_mat, scale=(left_seg_length, wall_thickness, wall_height))
# Right segment
right_seg_center_x = gate_width/2 + left_seg_length/2
create_cube("Wall_South_Right", 1, (right_seg_center_x, south_wall_y, wall_height/2), stone_mat, scale=(left_seg_length, wall_thickness, wall_height))
# Gate arch (top part above gate)
gate_top = create_cube("Wall_South_GateTop", 1, (0, south_wall_y, gate_height + (wall_height - gate_height)/2), stone_mat, scale=(gate_width, wall_thickness, wall_height - gate_height))

# East wall
east_wall_x = wall_length/2
create_cube("Wall_East", 1, (east_wall_x, 0, wall_height/2), stone_mat, scale=(wall_thickness, wall_length, wall_height))

# North wall
north_wall_y = wall_length/2
create_cube("Wall_North", 1, (0, north_wall_y, wall_height/2), stone_mat, scale=(wall_length, wall_thickness, wall_height))

# West wall
west_wall_x = -wall_length/2
create_cube("Wall_West", 1, (west_wall_x, 0, wall_height/2), stone_mat, scale=(wall_thickness, wall_length, wall_height))

# --- Battlements on walls ---
def add_battlements_to_wall(name, center_x, center_y, length, orientation, wall_height, wall_thickness):
    """Add battlements along a wall"""
    battlement_size = 1
    spacing = 2
    count = int(length / spacing)
    
    if orientation == 'x':  # wall runs along x-axis
        for i in range(count):
            bx = center_x - length/2 + spacing/2 + i * spacing
            by = center_y
            create_cube(f"{name}_Battlement_{i}", battlement_size, (bx, by, wall_height + 0.5), stone_mat, scale=(battlement_size*0.8, wall_thickness*0.8, 1))
    elif orientation == 'y':  # wall runs along y-axis
        for i in range(count):
            bx = center_x
            by = center_y - length/2 + spacing/2 + i * spacing
            create_cube(f"{name}_Battlement_{i}", battlement_size, (bx, by, wall_height + 0.5), stone_mat, scale=(wall_thickness*0.8, battlement_size*0.8, 1))

# Add battlements to east, north, west walls
add_battlements_to_wall("Battlement_East", wall_length/2, 0, wall_length, 'y', wall_height, wall_thickness)
add_battlements_to_wall("Battlement_North", 0, wall_length/2, wall_length, 'x', wall_height, wall_thickness)
add_battlements_to_wall("Battlement_West", -wall_length/2, 0, wall_length, 'y', wall_height, wall_thickness)

# South wall battlements (skip the gate area)
# Left segment battlements
left_seg_length = (wall_length - gate_width) / 2
add_battlements_to_wall("Battlement_South_Left", -gate_width/2 - left_seg_length/2, -wall_length/2, left_seg_length, 'x', wall_height, wall_thickness)
add_battlements_to_wall("Battlement_South_Right", gate_width/2 + left_seg_length/2, -wall_length/2, left_seg_length, 'x', wall_height, wall_thickness)

# --- Gate ---
# Gate structure (wooden doors)
gate_door = create_cube("GateDoor", 1, (0, -wall_length/2, gate_height/2), gate_mat, scale=(gate_width - 0.5, 0.3, gate_height))
# Gate frame (stone arch)
gate_frame_left = create_cube("GateFrame_Left", 1, (-gate_width/2 - 0.3, -wall_length/2, gate_height/2), stone_mat, scale=(0.6, wall_thickness + 0.5, gate_height))
gate_frame_right = create_cube("GateFrame_Right", 1, (gate_width/2 + 0.3, -wall_length/2, gate_height/2), stone_mat, scale=(0.6, wall_thickness + 0.5, gate_height))
gate_frame_top = create_cube("GateFrame_Top", 1, (0, -wall_length/2, gate_height + 0.3), stone_mat, scale=(gate_width + 1.2, wall_thickness + 0.5, 0.6))

# --- Central keep (optional, adds to medieval feel) ---
keep_size = 10
keep = create_cube("Keep", keep_size, (0, 0, keep_size/2 + 0.5), stone_mat)
# Keep roof
keep_roof = create_cone("KeepRoof", keep_size/2 + 1, 0, 5, (0, 0, keep_size + 2.5), dark_stone_mat)

# --- Lighting ---
bpy.ops.object.light_add(type='SUN', location=(0, 0, 50))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Fill light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 30))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 500

# --- Camera ---
bpy.ops.object.camera_add(location=(40, -40, 25))
camera = bpy.context.active_object
camera.name = "Camera"
# Point camera at center
direction = Vector((0, 0, 5)) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = camera

print("Medieval castle created successfully!")
