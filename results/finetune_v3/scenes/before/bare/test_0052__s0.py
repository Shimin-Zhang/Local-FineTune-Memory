import bpy
import math
import random
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Helper: Create a jigsaw piece with tabs and blanks ---
def create_jigsaw_piece(name, size, color, location, rotation, has_tab_top=True, has_tab_right=True,
                        has_tab_bottom=True, has_tab_left=True, tab_depth=0.3, tab_width=0.25,
                        thickness=0.4, seed=0):
    """
    Create a 3D jigsaw piece with tabs (protruding) and blanks (indented).
    """
    rng = random.Random(seed)
    
    # Define the base square with tabs/blanks
    # We'll build the profile as a list of 2D points, then extrude.
    
    s = size
    t = tab_depth
    w = tab_width
    
    # Start at bottom-left, go counter-clockwise
    # Bottom edge: from (-s/2, -s/2) to (s/2, -s/2)
    # Right edge: from (s/2, -s/2) to (s/2, s/2)
    # Top edge: from (s/2, s/2) to (-s/2, s/2)
    # Left edge: from (-s/2, s/2) to (-s/2, -s/2)
    
    points = []
    
    # Bottom edge (y = -s/2)
    if has_tab_bottom:
        # Tab protrudes downward
        mid_x = 0
        points.append((-s/2, -s/2))
        points.append((-w/2, -s/2))
        points.append((-w/2, -s/2 - t*0.6))
        points.append((-w/2 - 0.05, -s/2 - t))
        points.append((w/2 + 0.05, -s/2 - t))
        points.append((w/2, -s/2 - t*0.6))
        points.append((w/2, -s/2))
        points.append((s/2, -s/2))
    else:
        # Blank: indented upward
        mid_x = 0
        points.append((-s/2, -s/2))
        points.append((-w/2, -s/2))
        points.append((-w/2, -s/2 + t*0.6))
        points.append((-w/2 + 0.05, -s/2 + t))
        points.append((w/2 - 0.05, -s/2 + t))
        points.append((w/2, -s/2 + t*0.6))
        points.append((w/2, -s/2))
        points.append((s/2, -s/2))
    
    # Right edge (x = s/2)
    if has_tab_right:
        mid_y = 0
        points.append((s/2, -s/2))
        points.append((s/2, -w/2))
        points.append((s/2 + t*0.6, -w/2))
        points.append((s/2 + t, -w/2 - 0.05))
        points.append((s/2 + t, w/2 + 0.05))
        points.append((s/2 + t*0.6, w/2))
        points.append((s/2, w/2))
        points.append((s/2, s/2))
    else:
        mid_y = 0
        points.append((s/2, -s/2))
        points.append((s/2, -w/2))
        points.append((s/2 - t*0.6, -w/2))
        points.append((s/2 - t, -w/2 + 0.05))
        points.append((s/2 - t, w/2 - 0.05))
        points.append((s/2 - t*0.6, w/2))
        points.append((s/2, w/2))
        points.append((s/2, s/2))
    
    # Top edge (y = s/2)
    if has_tab_top:
        mid_x = 0
        points.append((s/2, s/2))
        points.append((w/2, s/2))
        points.append((w/2, s/2 + t*0.6))
        points.append((w/2 + 0.05, s/2 + t))
        points.append((-w/2 - 0.05, s/2 + t))
        points.append((-w/2, s/2 + t*0.6))
        points.append((-w/2, s/2))
        points.append((-s/2, s/2))
    else:
        mid_x = 0
        points.append((s/2, s/2))
        points.append((w/2, s/2))
        points.append((w/2, s/2 - t*0.6))
        points.append((w/2 - 0.05, s/2 - t))
        points.append((-w/2 + 0.05, s/2 - t))
        points.append((-w/2, s/2 - t*0.6))
        points.append((-w/2, s/2))
        points.append((-s/2, s/2))
    
    # Left edge (x = -s/2)
    if has_tab_left:
        mid_y = 0
        points.append((-s/2, s/2))
        points.append((-s/2, w/2))
        points.append((-s/2 - t*0.6, w/2))
        points.append((-s/2 - t, w/2 + 0.05))
        points.append((-s/2 - t, -w/2 - 0.05))
        points.append((-s/2 - t*0.6, -w/2))
        points.append((-s/2, -w/2))
        points.append((-s/2, -s/2))
    else:
        mid_y = 0
        points.append((-s/2, s/2))
        points.append((-s/2, w/2))
        points.append((-s/2 + t*0.6, w/2))
        points.append((-s/2 + t, w/2 - 0.05))
        points.append((-s/2 + t, -w/2 + 0.05))
        points.append((-s/2 + t*0.6, -w/2))
        points.append((-s/2, -w/2))
        points.append((-s/2, -s/2))
    
    # Remove duplicate consecutive points
    clean_points = [points[0]]
    for p in points[1:]:
        if p != clean_points[-1]:
            clean_points.append(p)
    
    # Create mesh from profile
    verts = [(x, y, 0) for x, y in clean_points]
    verts_top = [(x, y, thickness) for x, y in clean_points]
    
    n = len(clean_points)
    faces = []
    # Bottom face
    faces.append(list(range(n)))
    # Top face (reversed)
    faces.append(list(range(n, 2*n))[::-1])
    # Side faces
    for i in range(n):
        j = (i + 1) % n
        faces.append([i, j, n+j, n+i])
    
    mesh = bpy.data.meshes.new(name + "_mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Material
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.6
    mesh.materials.append(mat)
    
    # Transform
    obj.location = location
    obj.rotation_euler = rotation
    
    return obj


def create_box(name, size, color, location, rotation=(0,0,0)):
    """Create a simple box."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0]/2, size[1]/2, size[2]/2)
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(scale=True)
    
    mat = bpy.data.materials.new(name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = 0.5
    obj.data.materials.append(mat)
    return obj


# --- Parameters ---
PIECE_SIZE = 2.0
THICKNESS = 0.5
TAB_DEPTH = 0.35
TAB_WIDTH = 0.3

# --- Ground plane ---
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat = bpy.data.materials.new("GroundMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.3, 0.5, 0.3, 1)
bsdf.inputs["Roughness"].default_value = 0.8
ground.data.materials.append(mat)

# --- Jigsaw pieces forming the town base ---
# A 4x4 grid of pieces, with some tabs/blanks
# Colors for pieces
piece_colors = [
    (0.9, 0.85, 0.7, 1),  # warm beige
    (0.8, 0.75, 0.65, 1), # tan
    (0.85, 0.8, 0.7, 1),  # light brown
    (0.75, 0.7, 0.6, 1),  # darker tan
    (0.9, 0.8, 0.7, 1),   # peach
    (0.85, 0.8, 0.75, 1), # cream
]

# Grid: 4x4
grid_size = 4
spacing = PIECE_SIZE

# Define tab/blank pattern for a coherent jigsaw
# Each piece: (top_tab, right_tab, bottom_tab, left_tab)
# True = tab (protrudes), False = blank (indents)
# For adjacent pieces, if piece A has tab on right, piece B (to the right) should have blank on left
# We'll use a pattern

# Create a pattern where tabs alternate
def get_tab_pattern(i, j):
    """Return (top, right, bottom, left) tab flags for piece at grid position (i, j)"""
    # Top: tab if row above has blank on bottom, or it's the top edge
    # Right: tab if column to right has blank on left, or it's the right edge
    # Bottom: tab if row below has blank on top, or it's the bottom edge
    # Left: tab if column to left has blank on right, or it's the left edge
    
    # Simple alternating pattern
    top = (j % 2 == 0) if j < grid_size - 1 else True  # top edge always tab
    right = (i % 2 == 0) if i < grid_size - 1 else True  # right edge always tab
    bottom = (j % 2 == 1) if j > 0 else True  # bottom edge always tab
    left = (i % 2 == 1) if i > 0 else True  # left edge always tab
    
    return (top, right, bottom, left)

# Create the main town pieces
town_pieces = []
for j in range(grid_size):  # rows (y)
    for i in range(grid_size):  # cols (x)
        x = (i - grid_size/2 + 0.5) * spacing
        y = (j - grid_size/2 + 0.5) * spacing
        z = THICKNESS / 2
        
        top, right, bottom, left = get_tab_pattern(i, j)
        
        color = piece_colors[(i * grid_size + j) % len(piece_colors)]
        seed = i * 100 + j
        
        piece = create_jigsaw_piece(
            name=f"TownPiece_{i}_{j}",
            size=PIECE_SIZE,
            color=color,
            location=(x, y, z),
            rotation=(0, 0, 0),
            has_tab_top=top,
            has_tab_right=right,
            has_tab_bottom=bottom,
            has_tab_left=left,
            tab_depth=TAB_DEPTH,
            tab_width=TAB_WIDTH,
            thickness=THICKNESS,
            seed=seed
        )
        town_pieces.append(piece)

# --- Church ---
# Church body
church_body = create_box("Church_Body", (3, 2, 3), (0.9, 0.9, 0.85, 1), (0, -3, 1.5))

# Church roof (pyramid)
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=2.5, radius2=0, depth=2, location=(0, -3, 4))
roof = bpy.context.active_object
roof.name = "Church_Roof"
roof.rotation_euler = (0, 0, math.radians(45))
mat = bpy.data.materials.new("RoofMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.5, 0.2, 0.15, 1)
bsdf.inputs["Roughness"].default_value = 0.4
roof.data.materials.append(mat)

# Church tower
tower = create_box("Church_Tower", (1.5, 1.5, 4), (0.85, 0.85, 0.8, 1), (1.5, -3, 2))

# Tower roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.2, radius2=0, depth=1.5, location=(1.5, -3, 4.75))
tower_roof = bpy.context.active_object
tower_roof.name = "Tower_Roof"
tower_roof.rotation_euler = (0, 0, math.radians(45))
tower_roof.data.materials.append(mat)

# Cross on tower
cross_v = create_box("Cross_V", (0.1, 0.1, 0.8), (0.8, 0.6, 0.2, 1), (1.5, -3, 5.6))
cross_h = create_box("Cross_H", (0.5, 0.1, 0.1), (0.8, 0.6, 0.2, 1), (1.5, -3, 5.7))

# Church door
door = create_box("Church_Door", (0.8, 0.1, 1.5), (0.3, 0.2, 0.1, 1), (0, -4.05, 0.75))

# Church windows
for wx in [-0.8, 0.8]:
    window = create_box(f"Church_Window_{wx}", (0.4, 0.1, 0.6), (0.6, 0.8, 0.9, 1), (wx, -4.05, 1.8))

# --- Street of coloured houses ---
house_colors = [
    (0.9, 0.4, 0.4, 1),   # red
    (0.4, 0.7, 0.9, 1),   # blue
    (0.9, 0.8, 0.3, 1),   # yellow
    (0.5, 0.8, 0.5, 1),   # green
    (0.8, 0.5, 0.8, 1),   # purple
    (0.9, 0.6, 0.3, 1),   # orange
]

house_positions = [
    (-3, 2), (-1, 2), (1, 2), (3, 2),  # front row
    (-3, 4), (-1, 4), (1, 4), (3, 4),  # back row
]

for idx, (hx, hy) in enumerate(house_positions):
    color = house_colors[idx % len(house_colors)]
    
    # House body
    body = create_box(f"House_{idx}_Body", (1.5, 1.2, 1.8), color, (hx, hy, 0.9))
    
    # House roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.3, radius2=0, depth=1, location=(hx, hy, 2.3))
    hroof = bpy