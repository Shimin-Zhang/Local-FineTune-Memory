import bpy
import math
import mathutils
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Materials
def make_mat(name, base_color, metallic=0.0, roughness=0.5, transmission=0.0, ior=1.45):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = base_color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if transmission > 0:
        bsdf.inputs["Transmission Weight"].default_value = transmission
        bsdf.inputs["IOR"].default_value = ior
    return mat

glass_mat = make_mat("Glass", (0.9, 0.95, 1.0, 1.0), 0.0, 0.05, 0.95, 1.5)
iron_mat = make_mat("WroughtIron", (0.1, 0.1, 0.1, 1.0), 1.0, 0.4)
cast_iron_mat = make_mat("CastIron", (0.15, 0.15, 0.18, 1.0), 0.8, 0.5)
wicker_mat = make_mat("Wicker", (0.55, 0.38, 0.18, 1.0), 0.0, 0.8)
stone_mat = make_mat("Stone", (0.7, 0.68, 0.62, 1.0), 0.0, 0.7)
water_mat = make_mat("Water", (0.2, 0.4, 0.6, 1.0), 0.0, 0.1, 0.8, 1.33)
fern_mat = make_mat("FernGreen", (0.05, 0.3, 0.05, 1.0), 0.0, 0.7)
pot_mat = make_mat("Terracotta", (0.6, 0.3, 0.15, 1.0), 0.0, 0.6)
floor_mat = make_mat("FloorTile", (0.5, 0.48, 0.42, 1.0), 0.0, 0.6)
brick_mat = make_mat("Brick", (0.55, 0.25, 0.15, 1.0), 0.0, 0.8)

# Helper functions
def add_box(name, loc, size, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    obj.data.materials.append(mat)
    return obj

def add_cyl(name, loc, radius, depth, mat, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

def add_sphere(name, loc, radius, mat, segs=16, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=segs, ring_count=rings)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj

# Floor
add_box("Floor", (0, 0, 0), (12, 10, 0.2), floor_mat)

# Brick base walls (cutaway - only back and left walls)
# Back wall (z = 5)
add_box("BackWall", (0, 5, 1.5), (12, 0.3, 3), brick_mat)
# Left wall (x = -6)
add_box("LeftWall", (-6, 0, 1.5), (0.3, 10, 3), brick_mat)

# Glass walls - right side (x=6) and front (z=-5) - partial for cutaway
# Right glass wall
add_box("RightGlass", (6, 0, 1.5), (0.05, 10, 3), glass_mat)
# Front glass wall (partial - cutaway, only back half)
add_box("FrontGlass", (0, -5, 1.5), (12, 0.05, 3), glass_mat)

# Glass roof - angled
# Create a sloped roof using a plane
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 3.0))
roof = bpy.context.active_object
roof.name = "RoofGlass"
roof.scale = (6, 5, 1)
roof.rotation_euler = (0, math.radians(15), 0)
bpy.ops.object.transform_apply(scale=True, rotation=True)
roof.data.materials.append(glass_mat)

# Iron roof frame - ribs
for i in range(7):
    x = -5 + i * 1.67
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=6, location=(x, 0, 3.2), vertices=8)
    rib = bpy.context.active_object
    rib.name = f"RoofRib_{i}"
    rib.rotation_euler = (0, math.radians(15), 0)
    rib.data.materials.append(iron_mat)

# Horizontal iron bars on glass walls
for z in range(-4, 5, 2):
    add_box(f"FrontBar_{z}", (0, -5, 0.5 + z*0.5), (12, 0.03, 0.03), iron_mat)
for x in range(-5, 6, 2):
    add_box(f"RightBar_{x}", (6, 0, 0.5 + x*0.5), (0.03, 10, 0.03), iron_mat)

# Wrought Iron Table
table_x, table_y = -2, -1
# Table top
bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=0.05, location=(table_x, table_y, 0.75), vertices=32)
table_top = bpy.context.active_object
table_top.name = "TableTop"
table_top.data.materials.append(iron_mat)
# Table leg
add_cyl("TableLeg", (table_x, table_y, 0.375), 0.04, 0.75, iron_mat)
# Table base
add_cyl("TableBase", (table_x, table_y, 0.05), 0.3, 0.1, iron_mat)
# Ornamental scrollwork (simplified as torus)
bpy.ops.mesh.primitive_torus_add(radius=0.25, major_segments=16, minor_segments=8, location=(table_x, table_y, 0.72))
scroll = bpy.context.active_object
scroll.name = "TableScroll"
scroll.data.materials.append(iron_mat)

# Wicker Chairs (4 around table)
def make_wicker_chair(name, loc, rot_z):
    # Seat
    seat = add_box(name+"_Seat", (loc[0], loc[1], 0.45), (0.5, 0.5, 0.08), wicker_mat)
    seat.rotation_euler = (0, 0, rot_z)
    # Back
    back = add_box(name+"_Back", (loc[0], loc[1], 0.7), (0.5, 0.06, 0.5), wicker_mat)
    back.rotation_euler = (0, 0, rot_z)
    # Legs
    for dx, dy in [(-0.2, -0.2), (0.2, -0.2), (-0.2, 0.2), (0.2, 0.2)]:
        leg_loc = (loc[0] + dx*math.cos(rot_z) - dy*math.sin(rot_z),
                   loc[1] + dx*math.sin(rot_z) + dy*math.cos(rot_z), 0.22)
        add_cyl(name+f"_Leg_{dx}_{dy}", leg_loc, 0.02, 0.44, wicker_mat, verts=8)

make_wicker_chair("Chair1", (table_x - 1.2, table_y, 0), math.radians(90))
make_wicker_chair("Chair2", (table_x + 1.2, table_y, 0), math.radians(-90))
make_wicker_chair("Chair3", (table_x, table_y - 1.2, 0), 0)
make_wicker_chair("Chair4", (table_x, table_y + 1.2, 0), math.radians(180))

# Fountain
fountain_x, fountain_y = 3, 2
# Base pool
add_cyl("FountainPool", (fountain_x, fountain_y, 0.2), 1.2, 0.4, stone_mat, verts=32)
# Water surface
add_cyl("FountainWater", (fountain_x, fountain_y, 0.38), 1.1, 0.02, water_mat, verts=32)
# Central pillar
add_cyl("FountainPillar", (fountain_x, fountain_y, 0.8), 0.15, 1.2, stone_mat)
# Upper bowl
add_cyl("FountainBowl", (fountain_x, fountain_y, 1.4), 0.6, 0.15, stone_mat, verts=32)
# Water in bowl
add_cyl("FountainBowlWater", (fountain_x, fountain_y, 1.48), 0.55, 0.02, water_mat, verts=32)
# Top ornament
add_sphere("FountainTop", (fountain_x, fountain_y, 1.7), 0.12, stone_mat)
# Water jets (simplified as small cylinders)
for angle in range(0, 360, 45):
    rad = math.radians(angle)
    jet_x = fountain_x + 0.5*math.cos(rad)
    jet_y = fountain_y + 0.5*math.sin(rad)
    add_cyl(f"FountainJet_{angle}", (jet_x, jet_y, 1.0), 0.02, 0.6, water_mat, verts=8)

# Cast Iron Stair
stair_x, stair_y = -4, 3
steps = 8
step_width = 1.0
step_depth = 0.3
step_height = 0.2
for i in range(steps):
    z = 0.1 + i * step_height
    y = stair_y - i * step_depth
    add_box(f"StairStep_{i}", (stair_x, y, z), (step_width, step_depth, step_height), cast_iron_mat)
# Stair stringers
for side in [-0.5, 0.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=3.0, location=(stair_x + side, stair_y - 1.2, 0.9), vertices=8)
    stringer = bpy.context.active_object
    stringer.name = f"StairStringer_{side}"
    stringer.rotation_euler = (math.radians(30), 0, 0)
    stringer.data.materials.append(cast_iron_mat)
# Handrail
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=2.5, location=(stair_x - 0.5, stair_y - 1.0, 1.2), vertices=8)
handrail = bpy.context.active_object
handrail.name = "StairHandrail"
handrail.rotation_euler = (math.radians(30), 0, 0)
handrail.data.materials.append(cast_iron_mat)
# Balusters
for i in range(5):
    t = i / 4
    bx = stair_x - 0.5
    by = stair_y - 0.2 - t * 2.0
    bz = 0.4 + t * 1.2
    add_cyl(f"Baluster_{i}", (bx, by, bz), 0.015, 0.4, cast_iron_mat, verts=8)

# Ferns
def make_fern(name, loc, scale=1.0):
    # Pot
    add_cyl(name+"_Pot", (loc[0], loc[1], 0.15*scale), 0.2*scale, 0.3*scale, pot_mat, verts=16)
    # Fronds - simplified as elongated spheres
    for i in range(6):
        angle = math.radians(i * 60)
        fx = loc[0] + 0.15*scale*math.cos(angle)
        fy = loc[1] + 0.15*scale*math.sin(angle)
        fz = 0.35*scale + 0.15*scale
        frond = add_sphere(name+f"_Frond_{i}", (fx, fy, fz), 0.12*scale, fern_mat, segs=8, rings=6)
        frond.scale = (1, 1, 2.5)
        frond.rotation_euler = (math.radians(30), 0, angle)

make_fern("Fern1", (-5, -4, 0), 1.2)
make_fern("Fern2", (5, -4, 0), 1.0)
make_fern("Fern3", (-5, 4, 0), 1.1)
make_fern("Fern4", (5, 4, 0), 0.9)
make_fern("Fern5", (0, -4.5, 0), 1.3)
make_fern("Fern6", (1, 3, 0), 0.8)
make_fern("Fern7", (-1, -3, 0), 1.0)

# Lighting
# Sun
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))

# Fill light
bpy.ops.object.light_add(type='POINT', location=(0, 0, 4))
fill = bpy.context.active_object
fill.name = "FillLight"
fill.data.energy = 100
fill.data.color = (1.0, 0.95, 0.9)

# Camera
bpy.ops.object.camera_add(location=(8, -8, 5))
cam = bpy.context.active_object
cam.name = "Camera"
cam.rotation_euler = (math.radians(60), 0, math.radians(45))
bpy.context.scene.camera = cam

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# World background
world = bpy.data.worlds.get("World")
if not world:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.7, 0.8, 0.9, 1.0)
bg.inputs[1].default_value = 1.0

print("Victorian conservatory scene created.")
