import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Materials
def make_mat(name, color, rough=0.7, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    return mat

mat_tent = make_mat("TentCanvas", (0.85, 0.78, 0.62), 0.85)
mat_tent_dark = make_mat("TentCanvasDark", (0.55, 0.45, 0.32), 0.85)
mat_wood = make_mat("Wood", (0.35, 0.22, 0.12), 0.7)
mat_wood_dark = make_mat("WoodDark", (0.22, 0.14, 0.08), 0.7)
mat_metal = make_mat("Metal", (0.4, 0.4, 0.42), 0.3, 0.9)
mat_brass = make_mat("Brass", (0.85, 0.65, 0.25), 0.25, 0.95)
mat_stone = make_mat("Stone", (0.5, 0.48, 0.45), 0.9)
mat_water = make_mat("Water", (0.2, 0.5, 0.7), 0.1, 0.1)
mat_flame = make_mat("Flame", (1.0, 0.6, 0.1), 0.5)
mat_flame.emission_color = (1.0, 0.5, 0.05)
mat_flame.emission_strength = 5.0
mat_glass = make_mat("Glass", (0.8, 0.85, 0.9), 0.1, 0.0)
mat_glass.blend_method = 'BLEND'
mat_paper = make_mat("Paper", (0.9, 0.88, 0.8), 0.9)
mat_rug = make_mat("Rug", (0.6, 0.15, 0.1), 0.95)
mat_rug2 = make_mat("Rug2", (0.15, 0.3, 0.5), 0.95)
mat_cloth = make_mat("Cloth", (0.7, 0.65, 0.55), 0.9)
mat_leather = make_mat("Leather", (0.4, 0.25, 0.12), 0.8)
mat_ground = make_mat("Ground", (0.55, 0.45, 0.3), 0.95)

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(mat_ground)

# Helper: add a mesh object
def add_obj(name, mesh_data, mat, loc=(0,0,0), rot=(0,0,0), scale=(1,1,1)):
    obj = bpy.data.objects.new(name, mesh_data)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    obj.scale = scale
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_box(name, sx, sy, sz, mat, loc=(0,0,0), rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    obj = bpy.context.object
    obj.name = name
    obj.scale = (sx/2, sy/2, sz/2)
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_cyl(name, r, depth, mat, loc=(0,0,0), rot=(0,0,0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    obj = bpy.context.object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_sphere(name, r, mat, loc=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
    obj = bpy.context.object
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    return obj

# ============================================================
# DINING TENT - long rectangular tent
# ============================================================
tent_len = 16
tent_width = 8
tent_height = 4.5
tent_base_y = 0
tent_x = -5  # center x of tent

# Tent floor (wooden platform)
add_box("TentFloor", tent_len + 1, tent_width + 1, 0.15, mat_wood_dark, (tent_x, 0, 0.075))

# Tent walls (4 sides)
wall_thick = 0.08
# Left wall
add_box("TentWallL", wall_thick, tent_width, tent_height, mat_tent, (tent_x - tent_len/2, 0, tent_height/2))
# Right wall
add_box("TentWallR", wall_thick, tent_width, tent_height, mat_tent, (tent_x + tent_len/2, 0, tent_height/2))
# Back wall
add_box("TentWallB", tent_len, wall_thick, tent_height, mat_tent, (tent_x, -tent_width/2, tent_height/2))
# Front wall (with opening - two segments + top)
front_open_w = 3
front_seg_w = (tent_len - front_open_w) / 2
add_box("TentWallF_L", front_seg_w, wall_thick, tent_height, mat_tent,
        (tent_x - front_open_w/2 - front_seg_w/2, tent_width/2, tent_height/2))
add_box("TentWallF_R", front_seg_w, wall_thick, tent_height, mat_tent,
        (tent_x + front_open_w/2 + front_seg_w/2, tent_width/2, tent_height/2))
# Top of opening
add_box("TentWallF_Top", front_open_w, wall_thick, tent_height - 3, mat_tent,
        (tent_x, tent_width/2, 3 + (tent_height-3)/2))

# Tent roof (prism shape)
roof_peak = 1.5
roof_y = tent_width / 2
# Create roof as a triangular prism
roof_mesh = bpy.data.meshes.new("RoofMesh")
roof_verts = [
    (-tent_len/2, -roof_y, tent_height),
    (tent_len/2, -roof_y, tent_height),
    (tent_len/2, roof_y, tent_height),
    (-tent_len/2, roof_y, tent_height),
    (-tent_len/2, 0, tent_height + roof_peak),
    (tent_len/2, 0, tent_height + roof_peak),
]
roof_faces = [
    (0, 1, 5, 4),   # front slope
    (2, 3, 4, 5),   # back slope
    (0, 3, 4),      # left triangle
    (1, 2, 5),      # right triangle
    (0, 1, 2, 3),   # bottom (not visible)
]
roof_mesh.from_pydata(roof_verts, [], roof_faces)
roof_mesh.update()
roof_obj = bpy.data.objects.new("TentRoof", roof_mesh)
bpy.context.collection.objects.link(roof_obj)
roof_obj.location = (tent_x, 0, 0)
roof_obj.data.materials.append(mat_tent)

# Tent poles (corners + ridge)
pole_r = 0.06
pole_h = tent_height + roof_peak
pole_positions = [
    (tent_x - tent_len/2, -tent_width/2),
    (tent_x + tent_len/2, -tent_width/2),
    (tent_x - tent_len/2, tent_width/2),
    (tent_x + tent_len/2, tent_width/2),
]
for i, (px, py) in enumerate(pole_positions):
    add_cyl(f"TentPole{i}", pole_r, pole_h, mat_wood_dark, (px, py, pole_h/2))

# Ridge pole
add_cyl("RidgePole", pole_r, tent_len, mat_wood_dark, (tent_x, 0, tent_height + roof_peak), rot=(0, math.radians(90), 0))

# Tent guy ropes (visual lines - thin cylinders)
guy_len = 3
guy_angle = math.radians(45)
for i, (px, py) in enumerate(pole_positions):
    # Rope going outward and down
    dx = 1 if px > tent_x else -1
    dy = 1 if abs(py) > tent_width/2 - 0.1 else -1
    end_x = px + dx * guy_len * math.cos(guy_angle)
    end_y = py + dy * guy_len * math.cos(guy_angle)
    end_z = 0
    mid = ((px + end_x)/2, (py + end_y)/2, (tent_height*0.8 + end_z)/2)
    vec = Vector((end_x - px, end_y - py, end_z - tent_height*0.8))
    length = vec.length
    rot = vec.to_track_quat('Z', 'Y').to_euler()
    add_cyl(f"GuyRope{i}", 0.015, length, mat_wood, mid, rot=rot)

# ============================================================
# DINING TABLE (long)
# ============================================================
table_len = 10
table_width = 2
table_h = 1.1
table_x = tent_x
table_y = 0
table_top_y = table_h

# Table top
add_box("DiningTableTop", table_len, table_width, 0.1, mat_wood, (table_x, table_y, table_top_y))

# Table legs
leg_positions = [
    (table_x - table_len/2 + 0.3, table_y - table_width/2 + 0.3),
    (table_x - table_len/2 + 0.3, table_y + table_width/2 - 0.3),
    (table_x + table_len/2 - 0.3, table_y - table_width/2 + 0.3),
    (table_x + table_len/2 - 0.3, table_y + table_width/2 - 0.3),
    (table_x, table_y - table_width/2 + 0.3),
    (table_x, table_y + table_width/2 - 0.3),
]
for i, (lx, ly) in enumerate(leg_positions):
    add_cyl(f"TableLeg{i}", 0.06, table_h, mat_wood_dark, (lx, ly, table_h/2))

# Table cross bars
add_box("TableCross1", table_len - 0.6, 0.08, 0.08, mat_wood_dark, (table_x, table_y - table_width/2 + 0.3, table_h * 0.5))
add_box("TableCross2", table_len - 0.6, 0.08, 0.08, mat_wood_dark, (table_x, table_y + table_width/2 - 0.3, table_h * 0.5))

# Tablecloth (slightly larger plane on top)
bpy.ops.mesh.primitive_plane_add(size=1, location=(table_x, table_y, table_top_y + 0.055))
cloth = bpy.context.object
cloth.name = "Tablecloth"
cloth.scale = (table_len/2 + 0.2, table_width/2 + 0.3, 1)
cloth.data.materials.append(mat_cloth)

# Plates (small cylinders on table)
plate_positions = []
for side in [-1, 1]:
    for i in range(5):
        px = table_x - table_len/2 + 1.2 + i * 1.8
        py = table_y + side * (table_width/2 - 0.4)
        plate_positions.append((px, py))

for i, (px, py) in enumerate(plate_positions):
    add_cyl(f"Plate{i}", 0.18, 0.02, mat_paper, (px, py, table_top_y + 0.07))
    # Glass on plate
    add_cyl(f"Glass{i}", 0.04, 0.12, mat_glass, (px + 0.15, py, table_top_y + 0.13))

# Centerpiece: candle holder
add_cyl("CandleBase", 0.08, 0.15, mat_brass, (table_x, table_y, table_top_y + 0.12))
add_cyl("Candle", 0.03, 0.25, mat_paper, (table_x, table_y, table_top_y + 0.3))
add_sphere("CandleFlame", 0.03, mat_flame, (table_x, table_y, table_top_y + 0.45))

# ============================================================
# FOLDING CHAIRS (around table)
# ============================================================
def make_folding_chair(name, loc, rot_z):
    """Create a simple folding chair"""
    chair_parts = []
    # Seat
    seat = add_box(name+"_Seat", 0.5, 0.5, 0.05, mat_wood, (0, 0, 0.45))
    chair_parts.append(seat)
    # Back
    back = add_box(name+"_Back", 0.5, 0.05, 0.5, mat_wood, (0, -0.25, 0.7))
    chair_parts.append(back)
    # Legs (4)
    leg_h = 0.45
    for i, (lx, ly) in enumerate([(-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)]):
        leg = add_cyl(f"{name}_Leg{i}", 0.025, leg_h, mat_wood_dark, (lx, ly, leg_h/2))
        chair_parts.append(leg)
    # Cross brace
    brace = add_box(name+"_Brace", 0.4, 0.03, 0.03, mat_wood_dark, (0, 0, 0.2))
    chair_parts.append(brace)
    
    # Group and position
    for part in chair_parts:
        part.location = (part.location.x, part.location.y, part.location.z)
    
    # Rotate and move
    pivot = Vector(loc)
    for part in chair_parts:
        part.location = Vector((part.location.x, part.location.y, part.location.z))
        # Apply rotation around chair center
        part.rotation_euler = (part.rotation_euler.x, part.rotation_euler.y, rot_z)
        # Move to final position
        offset = Vector((part.location.x, part.location.y, part.location.z))
        part.location = pivot + Vector((
            offset.x * math.cos(rot_z) - offset.y * math.sin(rot_z),
            offset.x * math.sin(rot_z) + offset.y * math.cos(rot_z),
            offset.z
        ))
    
    return chair_parts

# Chairs on left side of table
for i in range(4):
    cx = table_x - table_len/2 + 1.5 + i * 2.0
    cy = table_y - table_width/2 - 0.8
    make_folding_chair(f"ChairL{i}", (cx, cy, 0), math.radians(90))

# Chairs on right side of table
for i in range(4):
    cx = table_x - table_len/2 + 1.5 + i * 2.0
    cy = table_y + table_width/2 + 0.8
    make_folding_chair(f"ChairR{i}", (cx, cy, 0), math.radians(-90))

# Chairs at head and foot of table
make_folding_chair("ChairHead", (table_x - table_len/2 - 0.8, table_y, 0), math.radians(0))
make_folding_chair("ChairFoot", (table_x + table_len/2 + 0.8, table_y, 0), math.radians(180))

# ============================================================
# BATHTUB (outdoor, stone/wood tub)
# ============================================================
bath_x = 12
bath_y = -3
bath_w = 1.8
bath_l = 3.2
bath_h = 0.9
bath_wall = 0.12

# Tub base
add_box("BathBase", bath_w, bath_l, 0.1, mat_stone, (bath_x, bath_y, 0.05))

# Tub walls
# Long sides
add_box("BathWallL", bath_wall, bath_l, bath_h, mat_stone, (bath_x - bath_w/2 + bath_wall/2, bath_y, bath_h/2 + 0.1))
add_box("BathWallR", bath_wall, bath_l, bath_h, mat_stone, (bath_x + bath_w/2 - bath_wall/2, bath_y, bath_h/2 + 0.1))
# Short sides
add_box("BathWallF", bath_w, bath_wall, bath_h, mat_stone, (bath_x, bath_y + bath_l/2 - bath_wall/2, bath_h/2 + 0.1))
add_box("BathWallB", bath_w, bath_wall, bath_h, mat_stone, (bath_x, bath_y - bath_l/2 + bath_wall/2, bath_h/2 + 0.1))

# Water surface
bpy.ops.mesh.primitive_plane_add(size=1, location=(bath_x, bath_y, bath_h * 0.7 + 0.1))
water = bpy.context.object
water.name = "BathWater"
water.scale = ((bath_w - 2*bath_wall)/2, (bath_l - 2*bath_wall)/2, 1)
water.data.materials.append(mat_water)

# Wooden legs for tub
for i, (lx, ly) in enumerate([
    (bath_x - bath_w/2 + 0.15, bath_y - bath_l/2 + 0.15),
    (bath_x + bath_w/2 - 0.15, bath_y - bath_l/2 + 0.15),
    (bath_x - bath_w/2 + 0.15, bath_y + bath_l/2 - 0.15),
    (bath_x + bath_w/2 - 0.15, bath_y + bath_l/2 - 0.15),
]):
    add_cyl(f"BathLeg{i}", 0.05, 0.1, mat_wood_dark, (lx, ly, 0.05))

# Towel draped over edge
add_box("Towel", 0.5, 0.02, 0.6, mat_paper, (bath_x + bath_w/2, bath_y + bath_l/4, bath_h + 0.15), rot=(math.radians(90), 0, 0))

# ============================================================
# GRAMOPHONE (on a small table near the tent)
# ============================================================
gram_x = tent_x + tent_len/2 + 1.5
gram_y = tent_width/2 + 1.5

# Small side table
add_cyl("GramTableTop", 0.4, 0.05, mat_wood, (gram_x, gram_y, 0.75))
add_cyl("GramTableLeg", 0.04, 0.75, mat_wood_dark, (gram_x, gram_y, 0.375))
# Table base
add_cyl("GramTableBase", 0.2, 0.03, mat_wood_dark, (gram_x, gram_y, 0.015))

# Gramophone body (box)
add_box("GramBody", 0.35, 0.3, 0.2, mat_wood_dark, (gram_x, gram_y, 0.87))

# Gramophone horn (cone shape)
horn_base = 0.08
horn_top = 0.25
horn_h = 0.35
bpy.ops.mesh.primitive_cone_add(radius1=horn_base, radius2=horn_top, depth=horn_h, location=(gram_x, gram_y - 0.25, 1.15), rotation=(math.radians(-60), 0, 0), vertices=32)
horn = bpy.context.object
horn.name = "GramHorn"
horn.data.materials.append(mat_brass)

# Turntable
add_cyl("Turntable", 0.15, 0.02, mat_wood, (gram_x, gram_y + 0.05, 0.98))

# Record
add_cyl("Record", 0.14, 0.005, mat_wood_dark, (gram_x, gram_y + 0.05, 0.99))

# Tone arm
add_cyl("ToneArm", 0.01, 0.2, mat_metal, (gram_x + 0.1, gram_y + 0.05, 1.0), rot=(0, math.radians(45), 0))

# ============================================================
# LANTERNS (hanging and on ground)
# ============================================================
def make_lantern(name, loc, scale=1.0):
    """Create a decorative lantern"""
    parts = []
    # Base
    base = add_cyl(name+"_Base", 0.08*scale, 0.05*scale, mat_metal, (0, 0, 0.025*scale))
    parts.append(base)
    # Body (glass)
    body = add_cyl(name+"_Body", 0.1*scale, 0.2*scale, mat_glass, (0, 0, 0.15*scale))
    parts.append(body)
    # Flame
    flame = add_sphere(name+"_Flame", 0.04*scale, mat_flame, (0, 0, 0.15*scale))
    parts.append(flame)
    # Top cap
    top = add_cyl(name+"_Top", 0.11*scale, 0.03*scale, mat_metal, (0, 0, 0.28*scale))
    parts.append(top)
    # Hook
    hook = add_cyl(name+"_Hook", 0.015*scale, 0.06*scale, mat_metal, (0, 0, 0.33*scale))
    parts.append(hook)
    
    for part in parts:
        part.location = Vector(loc) + Vector(part.location)
    
    return parts

# Hanging lanterns from tent ridge
for i in range(5):
    lx = tent_x - tent_len/2 + 2 + i * 2.5
    ly = 0
    lz = tent_height + roof_peak - 0.5
    make_lantern(f"HangLantern{i}", (lx, ly, lz), scale=0.8)
    # Rope from lantern to ridge
    rope_len = 0.5
    add_cyl(f"LanternRope{i}", 0.01, rope_len, mat_wood, (lx, ly, lz + 0.5 - rope_len/2))

# Ground lanterns near bath
make_lantern("GroundLantern1", (bath_x - 1.5, bath_y - 1, 0), scale=1.0)
make_lantern("GroundLantern2", (bath_x + 1.5, bath_y + 1, 0), scale=1.0)

# Lantern near gramophone
make_lantern("GramLantern", (gram_x + 0.5, gram_y + 0.5, 0), scale=0.9)

# Lantern at tent entrance
make_lantern("EntranceLantern", (tent_x, tent_width/2 + 0.5, 0), scale=1.1)

# ============================================================
# RUGS
# ============================================================
# Rug under dining table
bpy.ops.mesh.primitive_plane_add(size=1, location=(table_x, table_y, 0.16))
rug1 = bpy.context.object
rug1.name = "DiningRug"
rug1.scale = (table_len/2 + 1, table_width/2 + 1, 1)
rug1.data.materials.append(mat_rug)

# Rug near bath
bpy.ops.mesh.primitive_plane_add(size=1, location=(bath_x, bath_y + 2.5, 0.01))
rug2 = bpy.context.object
rug2.name = "BathRug"
rug2.scale = (1.5, 1, 1)
rug2.data.materials.append(mat_rug2)

# ============================================================
# DECORATIVE ELEMENTS
# ============================================================

# Campfire (outside, near bath)
fire_x = 14
fire_y = 0
# Stones in circle
for i in range(8):
    angle = i * math.radians(45)
    sx = fire_x + 0.5 * math.cos(angle)
    sy = fire_y + 0.5 * math.sin(angle)
    add_sphere(f"FireStone{i}", 0.12, mat_stone, (sx, sy, 0.06))

# Fire wood
for i in range(5):
    angle = i * math.radians(72)
    wx = fire_x + 0.2 * math.cos(angle)
    wy = fire_y + 0.2 * math.sin(angle)
    add_cyl(f"FireWood{i}", 0.04, 0.4, mat_wood_dark, (wx, wy, 0.1), rot=(math.radians(90), 0, angle))

# Fire flames
add_sphere("FireFlame1", 0.15, mat_flame, (fire_x, fire_y, 0.15))
add_sphere("FireFlame2", 0.1, mat_flame, (fire_x + 0.05, fire_y - 0.05, 0.25))
add_sphere("FireFlame3", 0.08, mat_flame, (fire_x - 0.05, fire_y + 0.03, 0.3))

# Log seats near fire
add_cyl("LogSeat1", 0.15, 1.2, mat_wood, (fire_x - 1, fire_y, 0.15), rot=(0, math.radians(90), 0))
add_cyl("LogSeat2", 0.15, 1.2, mat_wood, (fire_x + 1, fire_y, 0.15), rot=(0, math.radians(90), 0))

# Crate / storage box near tent
add_box("Crate", 0.6, 0.6, 0.6, mat_wood, (tent_x - tent_len/2 - 1, -tent_width/2 - 1, 0.3))
# Crate lid
add_box("CrateLid", 0.62, 0.62, 0.05, mat_wood_dark, (tent_x - tent_len/2 - 1, -tent_width/2 - 1, 0.62))

# Another crate
add_box("Crate2", 0.5, 0.5, 0.5, mat_wood, (tent_x - tent_len/2 - 1.8, -tent_width/2 - 0.5, 0.25))

# Water bucket near bath
add_cyl("Bucket", 0.15, 0.3, mat_metal, (bath_x - 1.2, bath_y + 1.5, 0.15))

# ============================================================
# LIGHTING
# ============================================================

# Main sun light
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3
sun_data.color = (1.0, 0.95, 0.85)
sun_obj = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), 0)

# Warm ambient fill
amb_data = bpy.data.lights.new("Ambient", type='AREA')
amb_data.energy = 50
amb_data.color = (1.0, 0.9, 0.7)
amb_data.size = 20
amb_obj = bpy.data.objects.new("Ambient", amb_data)
bpy.context.collection.objects.link(amb_obj)
amb_obj.location = (0, 0, 10)
amb_obj.rotation_euler = (0, 0, 0)

# Point lights for lanterns (simulating glow)
lantern_light_positions = [
    (tent_x - tent_len/2 + 2, 0, tent_height + roof_peak - 0.5),
    (tent_x - tent_len/2 + 4.5, 0, tent_height + roof_peak - 0.5),
    (tent_x, 0, tent_height + roof_peak - 0.5),
    (tent_x + tent_len/2 - 4.5, 0, tent_height + roof_peak - 0.5),
    (tent_x + tent_len/2 - 2, 0, tent_height + roof_peak - 0.5),
    (bath_x - 1.5, bath_y - 1, 0.15),
    (bath_x + 1.5, bath_y + 1, 0.15),
    (gram_x + 0.5, gram_y + 0.5, 0.15),
    (tent_x, tent_width/2 + 0.5, 0.15),
    (fire_x, fire_y, 0.2),
]

for i, (lx, ly, lz) in enumerate(lantern_light_positions):
    light_data = bpy.data.lights.new(f"LanternLight{i}", type='POINT')
    light_data.energy = 15
    light_data.color = (1.0, 0.6, 0.2)
    light_data.shadow_soft_size = 0.1
    light_obj = bpy.data.objects.new(f"LanternLight{i}", light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = (lx, ly, lz + 0.1)

# Camera
cam_data = bpy.data.cameras.new("Camera")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Camera", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (20, 15, 8)
# Look at center of scene
target = Vector((tent_x, 0, 2))
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Set camera as active
bpy.context.scene.camera = cam_obj

# World background
world = bpy.data.worlds.get("World")
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.4, 0.5, 0.7, 1)  # Sky blue
    bg.inputs[1].default_value = 1.0

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Colonial-era safari camp built successfully!")
