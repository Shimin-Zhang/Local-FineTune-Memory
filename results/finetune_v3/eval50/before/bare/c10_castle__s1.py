import bpy
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def create_material(name, color, roughness=0.8, metalness=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metalness
    return mat

stone_mat = create_material("Stone", (0.55, 0.5, 0.45), roughness=0.9)
dark_stone_mat = create_material("DarkStone", (0.35, 0.32, 0.3), roughness=0.95)
water_mat = create_material("Water", (0.1, 0.3, 0.5, 1.0), roughness=0.1)
wood_mat = create_material("Wood", (0.35, 0.2, 0.1), roughness=0.8)
grass_mat = create_material("Grass", (0.2, 0.5, 0.15), roughness=0.9)

# Helper: create a box mesh
def create_box(name, size, location, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(material)
    return obj

# Helper: create a cylinder
def create_cylinder(name, radius, depth, location, material, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# Helper: create a cone (for tower roofs)
def create_cone(name, radius1, radius2, depth, location, material, vertices=32):
    bpy.ops.mesh.primitive_cone_add(radius1=radius1, radius2=radius2, depth=depth, location=location, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# === GROUND ===
bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.01))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(grass_mat)

# === MOAT ===
# Moat is a ring (torus-like) around the castle
moat_inner_radius = 30
moat_outer_radius = 40
moat_depth = 3

# Create moat as a flat ring using a cylinder with a hole (boolean or just a torus-like shape)
# Simpler: create a large flat cylinder for water surface at moat level
moat_center = (0, 0, -1.5)  # water level below ground

# Water surface (flat circle ring)
bpy.ops.mesh.primitive_cylinder_add(radius=moat_outer_radius, depth=0.1, location=(0, 0, -1.5), vertices=64)
water_outer = bpy.context.active_object
water_outer.name = "MoatWater"
water_outer.data.materials.append(water_mat)

# Cut out the inner part to make a ring
bpy.ops.mesh.primitive_cylinder_add(radius=moat_inner_radius, depth=1, location=(0, 0, -1.5), vertices=64)
water_inner = bpy.context.active_object
water_inner.name = "MoatWaterInnerCut"

# Boolean difference
mod = water_outer.modifiers.new("CutInner", 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = water_inner
bpy.context.view_layer.objects.active = water_outer
bpy.ops.object.modifier_apply(modifier="CutInner")
bpy.ops.object.select_all(action='DESELECT')
water_inner.select_set(True)
bpy.context.view_layer.objects.active = water_inner
bpy.ops.object.delete(use_global=False)

# Moat walls (stone banks)
bpy.ops.mesh.primitive_cylinder_add(radius=moat_outer_radius, depth=moat_depth, location=(0, 0, -moat_depth/2 + 0.5), vertices=64)
moat_wall_outer = bpy.context.active_object
moat_wall_outer.name = "MoatWallOuter"
moat_wall_outer.data.materials.append(dark_stone_mat)

bpy.ops.mesh.primitive_cylinder_add(radius=moat_inner_radius, depth=moat_depth + 0.5, location=(0, 0, -moat_depth/2 + 0.5), vertices=64)
moat_wall_inner = bpy.context.active_object
moat_wall_inner.name = "MoatWallInner"

mod = moat_wall_outer.modifiers.new("CutInner", 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = moat_wall_inner
bpy.context.view_layer.objects.active = moat_wall_outer
bpy.ops.object.modifier_apply(modifier="CutInner")
bpy.ops.object.select_all(action='DESELECT')
moat_wall_inner.select_set(True)
bpy.context.view_layer.objects.active = moat_wall_inner
bpy.ops.object.delete(use_global=False)

# === CASTLE WALLS ===
wall_radius = 25
wall_height = 12
wall_thickness = 3

# Create the main wall as a ring (cylinder with hole)
bpy.ops.mesh.primitive_cylinder_add(radius=wall_radius, depth=wall_height, location=(0, 0, wall_height/2), vertices=64)
wall_outer = bpy.context.active_object
wall_outer.name = "CastleWallOuter"
wall_outer.data.materials.append(stone_mat)

bpy.ops.mesh.primitive_cylinder_add(radius=wall_radius - wall_thickness, depth=wall_height + 1, location=(0, 0, wall_height/2), vertices=64)
wall_inner = bpy.context.active_object
wall_inner.name = "CastleWallInnerCut"

mod = wall_outer.modifiers.new("CutInner", 'BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = wall_inner
bpy.context.view_layer.objects.active = wall_outer
bpy.ops.object.modifier_apply(modifier="CutInner")
bpy.ops.object.select_all(action='DESELECT')
wall_inner.select_set(True)
bpy.context.view_layer.objects.active = wall_inner
bpy.ops.object.delete(use_global=False)

# Crenellations on top of wall (small boxes around the top)
num_crenels = 32
for i in range(num_crenels):
    angle = i * (2 * math.pi / num_crenels)
    x = wall_radius - wall_thickness / 2 * 0.5 * math.cos(angle)
    y = wall_radius - wall_thickness / 2 * 0.5 * math.sin(angle)
    # Place crenel at the top of the wall
    cx = (wall_radius - 1.5) * math.cos(angle)
    cy = (wall_radius - 1.5) * math.sin(angle)
    crenel = create_box(
        f"Crenel_{i}",
        (2, 2, 2),
        (cx, cy, wall_height + 1),
        stone_mat
    )

# === FOUR TOWERS ===
tower_positions = [
    (wall_radius, 0),          # East
    (-wall_radius, 0),         # West
    (0, wall_radius),          # North
    (0, -wall_radius),         # South
]

tower_radius = 6
tower_height = 20

for idx, (tx, ty) in enumerate(tower_positions):
    # Tower body
    tower = create_cylinder(
        f"Tower_{idx}",
        tower_radius,
        tower_height,
        (tx, ty, tower_height / 2),
        stone_mat,
        vertices=32
    )
    
    # Tower roof (cone)
    roof = create_cone(
        f"Roof_{idx}",
        tower_radius + 1,
        0,
        8,
        (tx, ty, tower_height + 4),
        dark_stone_mat,
        vertices=32
    )
    
    # Crenellations on tower top
    num_tower_crenels = 12
    for j in range(num_tower_crenels):
        angle = j * (2 * math.pi / num_tower_crenels)
        cx = tx + (tower_radius - 1) * math.cos(angle)
        cy = ty + (tower_radius - 1) * math.sin(angle)
        crenel = create_box(
            f"TCrenel_{idx}_{j}",
            (1.5, 1.5, 1.5),
            (cx, cy, tower_height + 0.75),
            stone_mat
        )

# === GATE ===
# Gate is in the south tower (at (0, -wall_radius))
gate_width = 6
gate_height = 8
gate_depth = 4

# Gate arch (using a box with a hole or just a flat portal)
# Create gate opening in the south wall
gate_x = 0
gate_y = -wall_radius

# Gate frame (two pillars)
left_pillar = create_box("GatePillarL", (2, 4, gate_height + 2), (gate_x - gate_width/2, gate_y, (gate_height + 2)/2), dark_stone_mat)
right_pillar = create_box("GatePillarR", (2, 4, gate_height + 2), (gate_x + gate_width/2, gate_y, (gate_height + 2)/2), dark_stone_mat)

# Gate lintel (top beam)
lintel = create_box("GateLintel", (gate_width + 4, 4, 2), (gate_x, gate_y, gate_height + 1), dark_stone_mat)

# Gate door (wooden)
gate_door = create_box("GateDoor", (gate_width, 0.5, gate_height), (gate_x, gate_y, gate_height/2), wood_mat)

# Gate arch decoration (half cylinder on top of door)
bpy.ops.mesh.primitive_cylinder_add(radius=gate_width/2, depth=0.5, location=(gate_x, gate_y, gate_height), rotation=(0, math.pi/2, 0), vertices=32)
gate_arch = bpy.context.active_object
gate_arch.name = "GateArch"
gate_arch.data.materials.append(dark_stone_mat)

# === DRAWBRIDGE ===
# A simple flat bridge crossing the moat at the gate
bridge_width = 8
bridge_length = moat_outer_radius - moat_inner_radius + 4
bridge_x = 0
bridge_y = -(moat_inner_radius + moat_outer_radius) / 2
bridge = create_box("Drawbridge", (bridge_width, bridge_length, 0.5), (bridge_x, bridge_y, 0.25), wood_mat)

# Bridge supports
support_l = create_box("BridgeSupportL", (1, 1, 2), (bridge_x - bridge_width/2 + 1, bridge_y, 0), dark_stone_mat)
support_r = create_box("BridgeSupportR", (1, 1, 2), (bridge_x + bridge_width/2 - 1, bridge_y, 0), dark_stone_mat)

# === ADDITIONAL DETAILS ===

# Courtyard floor inside the castle
bpy.ops.mesh.primitive_cylinder_add(radius=wall_radius - wall_thickness - 1, depth=0.1, location=(0, 0, 0.05), vertices=64)
courtyard = bpy.context.active_object
courtyard.name = "Courtyard"
courtyard.data.materials.append(stone_mat)

# Central keep (larger structure in the middle)
keep = create_cylinder("Keep", 8, 18, (0, 0, 9), stone_mat, vertices=32)
keep_roof = create_cone("KeepRoof", 9, 0, 10, (0, 0, 23), dark_stone_mat, vertices=32)

# Windows on the keep (small dark boxes)
for i in range(8):
    angle = i * (2 * math.pi / 8)
    wx = 8.1 * math.cos(angle)
    wy = 8.1 * math.sin(angle)
    window = create_box(f"KeepWindow_{i}", (1, 0.5, 2), (wx, wy, 10), dark_stone_mat)

# Lighting
# Sun
bpy.ops.object.light_add(type='SUN', location=(50, 50, 100))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Camera
bpy.ops.object.camera_add(location=(60, -60, 40))
cam = bpy.context.active_object
cam.name = "Camera"
# Point camera at castle center
direction = (0, 0, 10) - cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
cam.rotation_euler = rot_quat.to_euler()

# Set camera as active
bpy.context.scene.camera = cam

print("Medieval castle created successfully!")
