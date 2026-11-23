import bpy
import math
import random
from mathutils import Vector, Euler

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# --- Materials ---
def create_material(name, color, roughness=0.8, metal=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metal
    return mat

mat_wood_dark  = create_material("WoodDark",  (0.25, 0.15, 0.08, 1.0), 0.85)
mat_wood_med   = create_material("WoodMed",   (0.40, 0.28, 0.15, 1.0), 0.80)
mat_wood_light = create_material("WoodLight", (0.55, 0.40, 0.25, 1.0), 0.75)
mat_roof       = create_material("Roof",      (0.30, 0.30, 0.32, 1.0), 0.60)
mat_water      = create_material("Water",     (0.05, 0.15, 0.20, 1.0), 0.10)
mat_moss       = create_material("Moss",      (0.15, 0.30, 0.08, 1.0), 0.90)
mat_bark       = create_material("Bark",      (0.20, 0.12, 0.06, 1.0), 0.90)
mat_leaves     = create_material("Leaves",    (0.10, 0.25, 0.05, 1.0), 0.85)
mat_stone      = create_material("Stone",     (0.45, 0.42, 0.38, 1.0), 0.90)
mat_boat_hull  = create_material("BoatHull",  (0.60, 0.50, 0.35, 1.0), 0.70)
mat_boat_seat  = create_material("BoatSeat",  (0.30, 0.20, 0.10, 1.0), 0.80)
mat_chair      = create_material("Chair",     (0.50, 0.35, 0.20, 1.0), 0.75)
mat_sky        = create_material("Sky",       (0.60, 0.75, 0.90, 1.0), 1.0)

# --- Bayou Water Plane ---
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
water = bpy.context.object
water.name = "BayouWater"
water.data.materials.append(mat_water)

# --- Shotgun House (narrow, on blocks) ---
# Blocks / pilings
block_positions = [
    (-1.5, -2.0), (-1.5, 2.0),
    ( 1.5, -2.0), ( 1.5, 2.0),
    ( 0.0, -2.0), ( 0.0,  2.0),
]
for i, (bx, by) in enumerate(block_positions):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(bx, by, 1.0))
    block = bpy.context.object
    block.name = f"Block_{i}"
    block.scale = (0.4, 0.4, 1.0)
    block.data.materials.append(mat_stone)

# Cross beam
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.0))
beam = bpy.context.object
beam.name = "CrossBeam"
beam.scale = (3.5, 4.5, 0.15)
beam.data.materials.append(mat_wood_dark)

# House body - narrow shotgun (front-to-back long, narrow side-to-side)
# Width (x): 2.0m, Depth (y): 5.0m, Height: 3.0m
house_w, house_d, house_h = 2.0, 5.0, 3.0
house_base_z = 2.1  # top of blocks

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, house_base_z + house_h/2))
house = bpy.context.object
house.name = "ShotgunHouse"
house.scale = (house_w/2, house_d/2, house_h/2)
house.data.materials.append(mat_wood_med)

# Roof - gable, pitched front-to-back
roof_y = house_d/2 + 0.3
roof_h = 1.5
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1, radius2=0, depth=1, location=(0, 0, house_base_z + house_h + roof_h/2))
roof = bpy.context.object
roof.name = "Roof"
roof.scale = (house_w/2 + 0.3, roof_y, roof_h/2)
roof.rotation_euler = (0, 0, math.radians(45))
roof.data.materials.append(mat_roof)

# Porch - deep, on the front (positive y side)
porch_depth = 2.5
porch_w = house_w + 1.0
porch_h = 0.15
porch_z = house_base_z

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_d/2 + porch_depth/2, porch_z + porch_h/2))
porch_floor = bpy.context.object
porch_floor.name = "PorchFloor"
porch_floor.scale = (porch_w/2, porch_depth/2, porch_h/2)
porch_floor.data.materials.append(mat_wood_light)

# Porch posts
post_positions = [
    (-porch_w/2, house_d/2 + porch_depth),
    ( porch_w/2, house_d/2 + porch_depth),
    (-porch_w/2, house_d/2),
    ( porch_w/2, house_d/2),
]
for i, (px, py) in enumerate(post_positions):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=house_h, location=(px, py, porch_z + house_h/2))
    post = bpy.context.object
    post.name = f"PorchPost_{i}"
    post.data.materials.append(mat_wood_dark)

# Porch roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, house_d/2 + porch_depth/2, porch_z + house_h + 0.1))
porch_roof = bpy.context.object
porch_roof.name = "PorchRoof"
porch_roof.scale = (porch_w/2 + 0.1, porch_depth/2 + 0.1, 0.05)
porch_roof.data.materials.append(mat_roof)

# Windows (simple recessed planes)
for wy in [-1.5, 0, 1.5]:
    bpy.ops.mesh.primitive_plane_add(size=1, location=(-house_w/2 - 0.01, wy, porch_z + house_h * 0.55))
    win = bpy.context.object
    win.name = f"Window_L_{wy}"
    win.scale = (0.01, 0.5, 0.7)
    win.rotation_euler = (0, math.radians(-90), 0)
    win.data.materials.append(mat_wood_dark)

    bpy.ops.mesh.primitive_plane_add(size=1, location=(house_w/2 + 0.01, wy, porch_z + house_h * 0.55))
    win = bpy.context.object
    win.name = f"Window_R_{wy}"
    win.scale = (0.01, 0.5, 0.7)
    win.rotation_euler = (0, math.radians(90), 0)
    win.data.materials.append(mat_wood_dark)

# Front door
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, house_d/2 + 0.01, porch_z + house_h * 0.45))
door = bpy.context.object
door.name = "FrontDoor"
door.scale = (0.45, 0.01, 0.9)
door.rotation_euler = (0, math.radians(90), 0)
door.data.materials.append(mat_wood_dark)

# --- Rocking Chair on Porch ---
chair_x, chair_y = 0.5, house_d/2 + 1.2
chair_z = porch_z + porch_h

# Seat
bpy.ops.mesh.primitive_cube_add(size=1, location=(chair_x, chair_y, chair_z + 0.4))
seat = bpy.context.object
seat.name = "ChairSeat"
seat.scale = (0.25, 0.3, 0.03)
seat.data.materials.append(mat_chair)

# Back
bpy.ops.mesh.primitive_cube_add(size=1, location=(chair_x, chair_y + 0.28, chair_z + 0.7))
back = bpy.context.object
back.name = "ChairBack"
back.scale = (0.25, 0.03, 0.35)
back.rotation_euler = (math.radians(-10), 0, 0)
back.data.materials.append(mat_chair)

# Rockers (curved - approximate with cylinders)
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.7, location=(chair_x + side*0.22, chair_y, chair_z + 0.05))
    rocker = bpy.context.object
    rocker.name = f"ChairRocker_{side}"
    rocker.rotation_euler = (math.radians(90), 0, 0)
    rocker.data.materials.append(mat_chair)

# --- Oak Trees with Spanish Moss ---
def create_oak_tree(x, y, z, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3*scale, depth=4*scale, location=(x, y, z + 2*scale))
    trunk = bpy.context.object
    trunk.name = "OakTrunk"
    trunk.data.materials.append(mat_bark)
    
    # Branches
    for angle in [0, 72, 144, 216, 288]:
        rad = math.radians(angle)
        bx = x + math.cos(rad) * 1.2 * scale
        by = y + math.sin(rad) * 1.2 * scale
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08*scale, depth=1.5*scale, location=(bx, by, z + 3.5*scale))
        branch = bpy.context.object
        branch.name = "OakBranch"
        branch.rotation_euler = (math.radians(30), 0, rad)
        branch.data.materials.append(mat_bark)
    
    # Foliage clusters
    for i in range(6):
        fx = x + random.uniform(-1.5, 1.5) * scale
        fy = y + random.uniform(-1.5, 1.5) * scale
        fz = z + (3.5 + random.uniform(0, 1.5)) * scale
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.8*scale, location=(fx, fy, fz))
        foliage = bpy.context.object
        foliage.name = "OakFoliage"
        foliage.scale = (random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), random.uniform(0.6, 0.9))
        foliage.data.materials.append(mat_leaves)
    
    # Spanish Moss - hanging strands
    for i in range(8):
        mx = x + random.uniform(-1.2, 1.2) * scale
        my = y + random.uniform(-1.2, 1.2) * scale
        mz = z + (3.0 + random.uniform(0, 1.0)) * scale
        bpy.ops.mesh.primitive_curve_add(type='BEZIER', location=(mx, my, mz))
        curve = bpy.context.object
        curve.name = "SpanishMoss"
        spline = curve.data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        for j, bp in enumerate(spline.bezier_points):
            bp.co = Vector((random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), -j * 0.4 * scale))
            bp.handle_left_type = bp.handle_right_type = 'AUTO'
        curve.data.bevel_depth = 0.03 * scale
        curve.data.materials.append(mat_moss)

# Place oaks around the bayou
create_oak_tree(-6, -4, 0, 1.2)
create_oak_tree( 7,  3, 0, 1.0)
create_oak_tree(-5,  6, 0, 0.9)
create_oak_tree( 6, -6, 0, 1.1)

# --- Boat in the Water ---
boat_x, boat_y, boat_z = 4.0, -3.0, 0.1
bpy.ops.mesh.primitive_cube_add(size=1, location=(boat_x, boat_y, boat_z))
hull = bpy.context.object
hull.name = "BoatHull"
hull.scale = (0.6, 1.8, 0.3)
hull.data.materials.append(mat_boat_hull)

# Point the bow
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.6, radius2=0, depth=1.0, location=(boat_x, boat_y - 2.0, boat_z))
bow = bpy.context.object
bow.name = "BoatBow"
bow.scale = (0.6, 0.5, 0.3)
bow.rotation_euler = (0, math.radians(-90), 0)
bow.data.materials.append(mat_boat_hull)

# Seats
for sy in [-0.8, 0, 0.8]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(boat_x, boat_y + sy, boat_z + 0.25))
    bseat = bpy.context.object
    bseat.name = "BoatSeat"
    bseat.scale = (0.5, 0.15, 0.05)
    bseat.data.materials.append(mat_boat_seat)

# --- Lighting ---
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(20), 0)

bpy.ops.object.light_add(type='AREA', location=(0, 0, 15))
fill = bpy.context.object
fill.name = "FillLight"
fill.data.energy = 100.0
fill.data.size = 10

# --- Camera ---
bpy.ops.object.camera_add(location=(8, 12, 5))
cam = bpy.context.object
cam.name = "Camera"
cam.rotation_euler = (math.radians(65), 0, math.radians(-30))
bpy.context.scene.camera = cam

# Set viewport to camera
for area in bpy.context.screen.areas:
    if area.type == 'VIEW_3D':
        area.spaces[0].region_3d.view_perspective = 'CAMERA'

print("Bayou shotgun house scene created.")
