import bpy
import math
import bmesh
from mathutils import Vector, Matrix

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create materials
def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

concrete_mat = create_material("Concrete", (0.75, 0.73, 0.70, 1.0), roughness=0.9)
water_mat = create_material("Water", (0.1, 0.4, 0.6, 1.0), roughness=0.1)
rock_mat = create_material("Rock", (0.35, 0.30, 0.25, 1.0), roughness=0.95)
grass_mat = create_material("Grass", (0.2, 0.45, 0.15, 1.0), roughness=0.9)
metal_mat = create_material("Metal", (0.5, 0.5, 0.55, 1.0), roughness=0.3, metallic=0.8)
wood_mat = create_material("Wood", (0.4, 0.25, 0.1, 1.0), roughness=0.8)
white_mat = create_material("White", (0.9, 0.9, 0.9, 1.0), roughness=0.5)
dark_mat = create_material("Dark", (0.15, 0.15, 0.15, 1.0), roughness=0.6)

# --- Terrain: Narrow Valley ---
# Create a grid and displace it to form a valley
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=200, size=1, location=(0, 0, 0))
terrain = bpy.context.active_object
terrain.name = "Valley"
terrain.scale = (80, 150, 1)

# Modify vertices to create valley shape
bm = bmesh.new()
bm.from_mesh(terrain.data)
for vert in bm.verts:
    x = vert.co.x
    y = vert.co.y
    # Valley profile: U-shaped cross section
    valley_depth = 30
    valley_width = 30
    # Distance from center
    d = abs(x)
    if d < valley_width:
        # Inside valley - lower
        t = d / valley_width
        z = -valley_depth * (1 - t**2)  # Parabolic valley floor
    else:
        # Outside valley - rises
        excess = d - valley_width
        z = 5 + excess * 0.3
    # Add some noise for natural look
    import random
    random.seed(int(x * 100) + int(y * 100))
    z += random.uniform(-1, 1)
    vert.co.z = z

bm.to_mesh(terrain.data)
bm.free()
terrain.data.materials.append(rock_mat)
# Add grass on top parts
terrain.data.materials.append(grass_mat)

# --- Concrete Arch Dam ---
# Create the arch dam shape
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=1, location=(0, 0, 0))
dam = bpy.context.active_object
dam.name = "ArchDam"

# Replace with custom arch shape
bm = bmesh.new()
# Arch dam: curved wall
num_segments = 50
arch_radius = 25
wall_thickness = 3
wall_height = 35
base_width = 12
top_width = 5

# Create the arch profile (side view)
# The dam curves along x-axis, extends in y (river direction)
vertices = []
for i in range(num_segments + 1):
    t = i / num_segments
    angle = math.pi * (t - 0.5)  # -pi/2 to pi/2
    x = arch_radius * math.sin(angle)
    # y position along river
    y_base = -5  # upstream face
    y_top = 5    # downstream face
    
    # Base vertices
    base_y = y_base
    top_y = y_top
    
    # Width varies with height (trapezoidal cross-section)
    # At each x position, create a vertical column
    pass

# Simpler approach: create a curved wall using a curve or mesh
bm.clear()

# Define arch in plan view (top-down)
# Arch spans from x=-25 to x=25, curving toward upstream (negative y)
arch_points = []
for i in range(num_segments + 1):
    t = i / num_segments
    angle = math.pi * (t - 0.5)
    x = arch_radius * math.sin(angle)
    y = -arch_radius * (1 - math.cos(angle)) * 0.3  # Slight curvature
    arch_points.append((x, y))

# Create the dam as a series of quads
# Each segment has 4 vertices: base-left, base-right, top-left, top-right
dam_verts = []
dam_faces = []

for i in range(num_segments):
    x1, y1 = arch_points[i]
    x2, y2 = arch_points[i + 1]
    
    # Base corners
    v0 = (x1, y1 - base_width/2, 0)
    v1 = (x2, y2 - base_width/2, 0)
    v2 = (x2, y2 + base_width/2, 0)
    v3 = (x1, y1 + base_width/2, 0)
    
    # Top corners (narrower)
    v4 = (x1, y1 - top_width/2, wall_height)
    v5 = (x2, y2 - top_width/2, wall_height)
    v6 = (x2, y2 + top_width/2, wall_height)
    v7 = (x1, y1 + top_width/2, wall_height)
    
    # Add vertices
    for v in [v0, v1, v2, v3, v4, v5, v6, v7]:
        dam_verts.append(v)
    
    base_idx = i * 8
    # Bottom face
    dam_faces.append((base_idx, base_idx+1, base_idx+2, base_idx+3))
    # Top face
    dam_faces.append((base_idx+4, base_idx+5, base_idx+6, base_idx+7))
    # Front face (upstream)
    dam_faces.append((base_idx, base_idx+1, base_idx+5, base_idx+4))
    # Back face (downstream)
    dam_faces.append((base_idx+3, base_idx+2, base_idx+6, base_idx+7))
    # Left side
    dam_faces.append((base_idx, base_idx+4, base_idx+7, base_idx+3))
    # Right side
    dam_faces.append((base_idx+1, base_idx+2, base_idx+6, base_idx+5))

for v in dam_verts:
    bm.verts.new(v)
for f in dam_faces:
    try:
        bm.faces.new([bm.verts[i] for i in f])
    except:
        pass

bm.to_mesh(dam.data)
bm.free()
dam.location = (0, 0, -28)  # Position at valley floor
dam.data.materials.append(concrete_mat)

# --- Water in Reservoir (Upstream) ---
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -15, 2))
water = bpy.context.active_object
water.name = "ReservoirWater"
water.scale = (25, 15, 1)
water.data.materials.append(water_mat)

# --- Spillway ---
# Create a spillway chute on one side of the dam
bpy.ops.mesh.primitive_cube_add(size=1, location=(15, 8, 10))
spillway = bpy.context.active_object
spillway.name = "Spillway"
spillway.scale = (3, 15, 2)
spillway.data.materials.append(concrete_mat)

# Spillway water flow
bpy.ops.mesh.primitive_cylinder_add(radius=1.5, depth=20, location=(15, 15, 5), rotation=(math.radians(75), 0, 0))
spillwater = bpy.context.active_object
spillwater.name = "SpillwayWater"
spillwater.data.materials.append(water_mat)

# --- Power House at Base ---
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 12, -20))
powerhouse = bpy.context.active_object
powerhouse.name = "PowerHouse"
powerhouse.scale = (15, 8, 10)
powerhouse.data.materials.append(white_mat)

# Add details to powerhouse
# Windows
for i in range(5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-6 + i*3, 16.1, -18))
    window = bpy.context.active_object
    window.scale = (1.5, 0.1, 2)
    window.data.materials.append(dark_mat)

# Roof
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 12, -10))
roof = bpy.context.active_object
roof.scale = (16, 9, 1)
roof.data.materials.append(dark_mat)

# --- Pylons Marching Away ---
num_pylons = 8
for i in range(num_pylons):
    x_pos = 20 + i * 15
    y_pos = 20 + i * 5
    
    # Pylon body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.8, depth=20, location=(x_pos, y_pos, -10))
    pylon = bpy.context.active_object
    pylon.name = f"Pylon_{i}"
    pylon.data.materials.append(concrete_mat)
    
    # Cross arm
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, y_pos, 0))
    arm = bpy.context.active_object
    arm.scale = (4, 0.5, 0.5)
    arm.data.materials.append(metal_mat)
    
    # Insulators
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1, location=(x_pos + side*2, y_pos, 0.5))
        ins = bpy.context.active_object
        ins.data.materials.append(dark_mat)

# --- Power Lines (simple curves) ---
for i in range(num_pylons - 1):
    x1 = 20 + i * 15
    x2 = 20 + (i+1) * 15
    y1 = 20 + i * 5
    y2 = 20 + (i+1) * 5
    
    # Sag in the middle
    mid_x = (x1 + x2) / 2
    mid_y = (y1 + y2) / 2
    
    for side in [-1, 1]:
        curve_data = bpy.data.curves.new(f"Line_{i}_{side}", 'CURVE')
        curve_data.dimensions = '3D'
        spline = curve_data.splines.new('BEZIER')
        spline.bezier_points.add(2)
        
        p0 = spline.bezier_points[0]
        p1 = spline.bezier_points[1]
        p2 = spline.bezier_points[2]
        
        p0.co = (x1 + side*2, y1, 0)
        p1.co = (mid_x, mid_y, -2)  # Sag
        p2.co = (x2 + side*2, y2, 0)
        
        p0.handle_left_type = 'AUTO'
        p0.handle_right_type = 'AUTO'
        p1.handle_left_type = 'AUTO'
        p1.handle_right_type = 'AUTO'
        p2.handle_left_type = 'AUTO'
        p2.handle_right_type = 'AUTO'
        
        curve_data.bevel_depth = 0.05
        
        line_obj = bpy.data.objects.new(f"PowerLine_{i}_{side}", curve_data)
        bpy.context.collection.objects.link(line_obj)
        line_obj.data.materials.append(dark_mat)

# --- Lighting ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(50, 50, 50))
sun = bpy.context.active_object
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.5, 0.7, 0.9, 1.0)
    bg_node.inputs[1].default_value = 1.0

# Camera
bpy.ops.object.camera_add(location=(60, 60, 30))
cam = bpy.context.active_object
cam.name = "MainCamera"
# Point camera at the dam
direction = Vector((0, 0, 0)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

# Set render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False
