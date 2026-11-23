import bpy
import math

# Clean up default objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Parameters ---
wall_width = 6.0
wall_height = 3.0
wall_depth = 0.3
brick_length = 0.4
brick_height = 0.2
brick_gap = 0.02

# Window opening
win_width = 1.5
win_height = 1.2
win_bottom = 1.0  # from floor
win_center_x = 0.0  # centered on wall

# --- Create the main wall with a hole ---
# We'll build the wall from individual bricks, skipping those that overlap the window.

def brick_overlaps_window(bx, by, bl, bh, wx, wy, ww, wh):
    """Check if a brick at (bx, by) with size (bl, bh) overlaps window at (wx, wy) size (ww, wh)."""
    # bx, by is bottom-left corner of brick
    brick_right = bx + bl
    brick_top = by + bh
    win_left = wx - ww / 2
    win_right = wx + ww / 2
    win_bottom = wy
    win_top = wy + wh
    
    if brick_right <= win_left or bx >= win_right:
        return False
    if brick_top <= win_bottom or by >= win_top:
        return False
    return True

# Create a collection for bricks
bricks_collection = bpy.data.collections.new("Bricks")
bpy.context.scene.collection.children.link(bricks_collection)

# Material for bricks
brick_mat = bpy.data.materials.new("BrickMaterial")
brick_mat.use_nodes = True
nodes = brick_mat.node_tree.nodes
links = brick_mat.node_tree.links

# Simple brick color with slight variation
diffuse = nodes["Principled BSDF"]
diffuse.inputs["Base Color"].default_value = (0.6, 0.25, 0.15, 1.0)
diffuse.inputs["Roughness"].default_value = 0.8

# Build bricks
row = 0
y = 0.0
while y < wall_height:
    # Offset every other row for running bond pattern
    offset = 0.0 if row % 2 == 0 else (brick_length + brick_gap) / 2
    
    x = -wall_width / 2 + offset
    while x < wall_width / 2:
        # Check if this brick overlaps the window
        if not brick_overlaps_window(x, y, brick_length, brick_height, win_center_x, win_bottom, win_width, win_height):
            # Create brick
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x + brick_length / 2, y + brick_height / 2, wall_depth / 2))
            brick = bpy.context.active_object
            brick.scale = (brick_length / 2, brick_height / 2, wall_depth / 2)
            brick.data.materials.append(brick_mat)
            # Move to bricks collection
            for col in brick.users_collection:
                col.objects.unlink(brick)
            bricks_collection.objects.link(brick)
        
        x += brick_length + brick_gap
    
    y += brick_height + brick_gap
    row += 1

# --- Create window frame ---
frame_thickness = 0.08
frame_depth = wall_depth + 0.04

# Create frame pieces using cubes
def create_frame_piece(location, scale, name):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.scale = scale
    obj.name = name
    frame_mat = bpy.data.materials.new("FrameMaterial")
    frame_mat.use_nodes = True
    fd = frame_mat.node_tree.nodes["Principled BSDF"]
    fd.inputs["Base Color"].default_value = (0.9, 0.9, 0.9, 1.0)
    fd.inputs["Roughness"].default_value = 0.3
    obj.data.materials.append(frame_mat)
    return obj

win_left = win_center_x - win_width / 2
win_right = win_center_x + win_width / 2
win_bottom_y = win_bottom
win_top_y = win_bottom + win_height

# Bottom frame
create_frame_piece((win_center_x, win_bottom_y - frame_thickness / 2, 0), 
                   (win_width / 2 + frame_thickness, frame_thickness / 2, frame_depth / 2), "Frame_Bottom")

# Top frame
create_frame_piece((win_center_x, win_top_y + frame_thickness / 2, 0), 
                   (win_width / 2 + frame_thickness, frame_thickness / 2, frame_depth / 2), "Frame_Top")

# Left frame
create_frame_piece((win_left - frame_thickness / 2, (win_bottom_y + win_top_y) / 2, 0), 
                   (frame_thickness / 2, win_height / 2 + frame_thickness, frame_depth / 2), "Frame_Left")

# Right frame
create_frame_piece((win_right + frame_thickness / 2, (win_bottom_y + win_top_y) / 2, 0), 
                   (frame_thickness / 2, win_height / 2 + frame_thickness, frame_depth / 2), "Frame_Right")

# Window glass
glass_mat = bpy.data.materials.new("GlassMaterial")
glass_mat.use_nodes = True
glass_mat.node_tree.nodes["Principled BSDF"].inputs["Transmission Weight"].default_value = 1.0
glass_mat.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.0
glass_mat.node_tree.nodes["Principled BSDF"].inputs["IOR"].default_value = 1.5

bpy.ops.mesh.primitive_plane_add(size=1, location=(win_center_x, (win_bottom_y + win_top_y) / 2, 0))
glass = bpy.context.active_object
glass.scale = (win_width / 2, win_height / 2, 1)
glass.rotation_euler = (math.radians(90), 0, 0)
glass.name = "Window_Glass"
glass.data.materials.append(glass_mat)

# --- Add a simple ground plane ---
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, -wall_height / 2, -wall_depth / 2))
ground = bpy.context.active_object
ground.name = "Ground"
ground_mat = bpy.data.materials.new("GroundMaterial")
ground_mat.use_nodes = True
gd = ground_mat.node_tree.nodes["Principled BSDF"]
gd.inputs["Base Color"].default_value = (0.3, 0.3, 0.3, 1.0)
ground.data.materials.append(ground_mat)

# --- Add lighting ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Fill light
bpy.ops.object.light_add(type='POINT', location=(-3, 2, 4))
fill = bpy.context.active_object
fill.data.energy = 100.0

# Camera
bpy.ops.object.camera_add(location=(0, -4, 1.5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = cam

print("Brick wall with window opening created successfully.")
