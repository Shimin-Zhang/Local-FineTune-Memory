import bpy
import math
from mathutils import Vector

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up scene
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

# Create a ground plane
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
ground.data.materials.append(bpy.data.materials.get("GroundMat") or bpy.data.materials.new("GroundMat"))
ground.data.materials[0].diffuse_color = (0.2, 0.5, 0.1, 1.0)

# Helper function to create a cylinder
def create_cylinder(radius, depth, location, name="Cylinder"):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj

# Helper function to create a box
def create_box(size, location, name="Box"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = (size[0], size[1], size[2])
    obj.name = name
    bpy.ops.object.transform_apply(scale=True)
    return obj

# Helper function to create a sphere
def create_sphere(radius, location, name="Sphere"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    return obj

# =====================
# SLIDE
# =====================
# Slide base platform
slide_platform = create_box((2, 2, 0.2), (0, -5, 1.5), "Slide_Platform")
slide_platform.data.materials.append(bpy.data.materials.get("SlideMat") or bpy.data.materials.new("SlideMat"))
slide_platform.data.materials[0].diffuse_color = (0.8, 0.4, 0.1, 1.0)

# Slide legs
for x in [-0.8, 0.8]:
    for y in [-0.8, 0.8]:
        leg = create_cylinder(0.08, 1.5, (x, -5 + y, 0.75), f"Slide_Leg_{x}_{y}")
        leg.data.materials.append(bpy.data.materials.get("MetalMat") or bpy.data.materials.new("MetalMat"))
        leg.data.materials[0].diffuse_color = (0.3, 0.3, 0.3, 1.0)

# Slide surface (angled plane)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -3.5, 1.0))
slide_surface = bpy.context.active_object
slide_surface.name = "Slide_Surface"
slide_surface.scale = (1.5, 2.5, 1)
slide_surface.rotation_euler = (math.radians(-30), 0, 0)
bpy.ops.object.transform_apply(scale=True, rotation=True)
slide_surface.data.materials.append(bpy.data.materials.get("SlideMat"))

# Slide ladder
for i in range(5):
    rung = create_cylinder(0.04, 0.6, (0.8, -5 + i * 0.3, 0.3 + i * 0.3), f"Slide_Ladder_Rung_{i}")
    rung.rotation_euler = (0, math.radians(90), 0)
    rung.data.materials.append(bpy.data.materials.get("MetalMat"))

# Ladder side rails
for side in [-0.3, 0.3]:
    rail = create_cylinder(0.04, 1.5, (0.8 + side, -4.5, 0.75), f"Slide_Ladder_Rail_{side}")
    rail.data.materials.append(bpy.data.materials.get("MetalMat"))

# =====================
# SWING SET
# =====================
# Swing frame A-frame
for x in [-2, 2]:
    # Left leg
    leg1 = create_cylinder(0.08, 3, (x, -10, 1.5), f"Swing_Leg1_{x}")
    leg1.rotation_euler = (0, math.radians(15 if x < 0 else -15), 0)
    leg1.data.materials.append(bpy.data.materials.get("MetalMat"))
    
    # Right leg
    leg2 = create_cylinder(0.08, 3, (x, -12, 1.5), f"Swing_Leg2_{x}")
    leg2.rotation_euler = (0, math.radians(-15 if x < 0 else 15), 0)
    leg2.data.materials.append(bpy.data.materials.get("MetalMat"))

# Crossbar
crossbar = create_cylinder(0.06, 4, (0, -11, 3), "Swing_Crossbar")
crossbar.rotation_euler = (0, 0, math.radians(90))
crossbar.data.materials.append(bpy.data.materials.get("MetalMat"))

# Swings (two swings)
for i, x in enumerate([-1, 1]):
    # Chains (simplified as thin cylinders)
    for side in [-0.2, 0.2]:
        chain = create_cylinder(0.02, 2.5, (x + side, -11, 1.75), f"Swing_Chain_{i}_{side}")
        chain.data.materials.append(bpy.data.materials.get("MetalMat"))
    
    # Seat
    seat = create_box((0.6, 0.3, 0.05), (x, -11, 0.5), f"Swing_Seat_{i}")
    seat.data.materials.append(bpy.data.materials.get("SlideMat"))

# =====================
# SANDBOX
# =====================
# Sandbox walls
sandbox_size = (3, 3, 0.5)
sandbox_location = (5, 5, 0.25)

# Bottom
sandbox_bottom = create_box((3, 3, 0.1), (5, 5, 0.05), "Sandbox_Bottom")
sandbox_bottom.data.materials.append(bpy.data.materials.get("WoodMat") or bpy.data.materials.new("WoodMat"))
sandbox_bottom.data.materials[0].diffuse_color = (0.5, 0.3, 0.1, 1.0)

# Walls
for wall in ['front', 'back', 'left', 'right']:
    if wall == 'front':
        wall_obj = create_box((3, 0.1, 0.5), (5, 3.5, 0.25), "Sandbox_Front")
    elif wall == 'back':
        wall_obj = create_box((3, 0.1, 0.5), (5, 6.5, 0.25), "Sandbox_Back")
    elif wall == 'left':
        wall_obj = create_box((0.1, 3, 0.5), (3.5, 5, 0.25), "Sandbox_Left")
    else:
        wall_obj = create_box((0.1, 3, 0.5), (6.5, 5, 0.25), "Sandbox_Right")
    wall_obj.data.materials.append(bpy.data.materials.get("WoodMat"))

# Sand (slightly recessed)
sand = create_box((2.8, 2.8, 0.3), (5, 5, 0.2), "Sand")
sand.data.materials.append(bpy.data.materials.get("SandMat") or bpy.data.materials.new("SandMat"))
sand.data.materials[0].diffuse_color = (0.9, 0.8, 0.5, 1.0)

# =====================
# SEESAW
# =====================
# Seesaw fulcrum (pivot point)
fulcrum = create_cylinder(0.1, 0.5, (-5, 0, 0.25), "Seesaw_Fulcrum")
fulcrum.data.materials.append(bpy.data.materials.get("MetalMat"))

# Seesaw base
base = create_box((1, 1, 0.1), (-5, 0, 0.05), "Seesaw_Base")
base.data.materials.append(bpy.data.materials.get("MetalMat"))

# Seesaw board (tilted)
board = create_box((0.5, 4, 0.1), (-5, 0, 0.5), "Seesaw_Board")
board.rotation_euler = (math.radians(10), 0, 0)
board.data.materials.append(bpy.data.materials.get("WoodMat"))

# Handles
for side in [-1.5, 1.5]:
    handle = create_cylinder(0.04, 0.5, (-5, side, 0.8), f"Seesaw_Handle_{side}")
    handle.rotation_euler = (0, math.radians(90), 0)
    handle.data.materials.append(bpy.data.materials.get("MetalMat"))

# =====================
# ADD SOME DECORATION
# =====================
# Trees
for tx, ty in [(-8, -8), (8, -8), (-8, 8), (8, 8)]:
    trunk = create_cylinder(0.2, 2, (tx, ty, 1), f"Tree_Trunk_{tx}_{ty}")
    trunk.data.materials.append(bpy.data.materials.get("WoodMat"))
    
    leaves = create_sphere(1, (tx, ty, 2.5), f"Tree_Leaves_{tx}_{ty}")
    leaves.data.materials.append(bpy.data.materials.get("LeafMat") or bpy.data.materials.new("LeafMat"))
    leaves.data.materials[0].diffuse_color = (0.1, 0.4, 0.1, 1.0)

# Path from entrance to playground
path = create_box((1, 15, 0.05), (0, 0, 0.02), "Path")
path.data.materials.append(bpy.data.materials.get("PathMat") or bpy.data.materials.new("PathMat"))
path.data.materials[0].diffuse_color = (0.7, 0.7, 0.7, 1.0)

print("Playground built successfully!")
