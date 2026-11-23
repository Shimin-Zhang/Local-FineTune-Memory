import bpy
import math
import random
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Helper: Create a jigsaw piece with tabs and blanks ---
def create_jigsaw_piece(name, size=(2, 2, 0.3), tab_size=0.35, tab_depth=0.4, color=(0.8, 0.8, 0.8, 1.0), location=(0, 0, 0), rotation=(0, 0, 0)):
    """
    Create a flat jigsaw piece with tabs (outies) and blanks (innies).
    size: (width, depth, thickness)
    tab_size: size of the tab
    tab_depth: how far the tab extends
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)

    # Add material
    mat = bpy.data.materials.new(name=name + "_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)

    # We'll build the jigsaw shape using boolean operations with cylinders
    # For simplicity, we'll create a more stylized jigsaw piece using a custom mesh

    # Actually, let's create a proper jigsaw piece by building vertices
    bpy.ops.object.delete()

    # Build jigsaw piece mesh manually
    s = size[0] / 2  # half width
    d = size[1] / 2  # half depth
    t = size[2] / 2  # half thickness
    ts = tab_size
    td = tab_depth

    # Define the 2D outline of the jigsaw piece (top view)
    # Starting from bottom-left, going clockwise
    # The piece has:
    # - Bottom edge: blank (inward)
    # - Right edge: tab (outward)
    # - Top edge: tab (outward)
    # - Left edge: blank (inward)

    # Let's define the outline as a list of 2D points
    # We'll use a simplified jigsaw shape

    # Helper to add a tab (outie) on an edge
    def add_tab_points(edge_start, edge_end, direction, tab_center, tab_size, tab_depth):
        """
        edge_start, edge_end: start and end of the edge
        direction: normal direction (outward for tab, inward for blank)
        tab_center: center of the tab on the edge
        """
        pass

    # Let's just create a box with some boolean cuts for tabs/blanks
    # Simpler approach: create a box and use boolean modifiers

    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)

    mat = bpy.data.materials.new(name=name + "_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)

    # Create tab/blank cutters
    cutters = []

    # Top edge: tab (outie) - add a small cylinder that protrudes
    # For a tab on top, we add material
    # For a blank on top, we remove material

    # Let's use a different approach: create the jigsaw shape with a custom mesh
    # This is getting complex. Let's use a simpler visual approach.

    # Delete and start over with a cleaner method
    bpy.ops.object.delete()

    # Create base cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size[0] / 2, size[1] / 2, size[2] / 2)
    bpy.ops.object.transform_apply(scale=True)

    mat = bpy.data.materials.new(name=name + "_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)

    # We'll add tabs and blanks using boolean operations
    # Top edge: tab (protrudes upward)
    # Right edge: blank (indentation)
    # Bottom edge: blank (indentation)
    # Left edge: tab (protrudes leftward)

    # Create tab on top
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(0, d + td / 2, 0))
    tab_top = bpy.context.active_object
    tab_top.scale = (1.5, 1, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Create blank on right (indentation)
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(s + td / 2, 0, 0))
    blank_right = bpy.context.active_object
    blank_right.scale = (1, 1.5, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Create blank on bottom (indentation)
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(0, -d - td / 2, 0))
    blank_bottom = bpy.context.active_object
    blank_bottom.scale = (1.5, 1, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Create tab on left (protrudes leftward)
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(-s - td / 2, 0, 0))
    tab_left = bpy.context.active_object
    tab_left.scale = (1, 1.5, 1)
    bpy.ops.object.transform_apply(scale=True)

    # Apply boolean modifiers
    # Add tabs (union)
    mod = obj.modifiers.new("Union_Top", 'BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tab_top
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Union_Top")

    mod = obj.modifiers.new("Union_Left", 'BOOLEAN')
    mod.operation = 'UNION'
    mod.object = tab_left
    bpy.ops.object.modifier_apply(modifier="Union_Left")

    # Subtract blanks (difference)
    mod = obj.modifiers.new("Diff_Right", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = blank_right
    bpy.ops.object.modifier_apply(modifier="Diff_Right")

    mod = obj.modifiers.new("Diff_Bottom", 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.object = blank_bottom
    bpy.ops.object.modifier_apply(modifier="Diff_Bottom")

    # Delete cutters
    for cutter in [tab_top, blank_right, blank_bottom, tab_left]:
        bpy.ops.object.select_all(action='DESELECT')
        cutter.select_set(True)
        bpy.context.view_layer.objects.active = cutter
        bpy.ops.object.delete()

    # Rotate if needed
    obj.rotation_euler = rotation
    bpy.ops.object.transform_apply(rotation=True)

    return obj


def create_jigsaw_piece_v2(name, width=2, depth=2, thickness=0.3, tab_size=0.3, tab_depth=0.35, color=(0.8, 0.8, 0.8, 1.0), location=(0, 0, 0), rotation_z=0):
    """
    Create a jigsaw piece with:
    - Top: tab (outie)
    - Right: blank (innie)
    - Bottom: blank (innie)
    - Left: tab (outie)
    """
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width / 2, depth / 2, thickness / 2)
    bpy.ops.object.transform_apply(scale=True)

    mat = bpy.data.materials.new(name=name + "_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)

    hw = width / 2
    hd = depth / 2
    ts = tab_size
    td = tab_depth

    cutters = []

    # Top tab (outie) - cylinder protruding upward
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(0, hd + td / 2, 0))
    tab_top = bpy.context.active_object
    tab_top.scale = (1.4, 1, 1)
    bpy.ops.object.transform_apply(scale=True)
    cutters.append(('UNION', tab_top))

    # Left tab (outie) - cylinder protruding leftward
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(-hw - td / 2, 0, 0))
    tab_left = bpy.context.active_object
    tab_left.scale = (1, 1.4, 1)
    bpy.ops.object.transform_apply(scale=True)
    cutters.append(('UNION', tab_left))

    # Right blank (innie) - cylinder cutting into the right edge
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(hw + td / 2, 0, 0))
    blank_right = bpy.context.active_object
    blank_right.scale = (1, 1.4, 1)
    bpy.ops.object.transform_apply(scale=True)
    cutters.append(('DIFFERENCE', blank_right))

    # Bottom blank (innie) - cylinder cutting into the bottom edge
    bpy.ops.mesh.primitive_cylinder_add(radius=ts, depth=td * 2, location=(0, -hd - td / 2, 0))
    blank_bottom = bpy.context.active_object
    blank_bottom.scale = (1.4, 1, 1)
    bpy.ops.object.transform_apply(scale=True)
    cutters.append(('DIFFERENCE', blank_bottom))

    # Apply booleans
    bpy.context.view_layer.objects.active = obj
    for op, cutter in cutters:
        mod = obj.modifiers.new("Bool", 'BOOLEAN')
        mod.operation = op
        mod.object = cutter
        bpy.ops.object.modifier_apply(modifier="Bool")
        bpy.ops.object.select_all(action='DESELECT')
        cutter.select_set(True)
        bpy.context.view_layer.objects.active = cutter
        bpy.ops.object.delete()

    # Apply rotation
    obj.rotation_euler = (0, 0, rotation_z)
    bpy.ops.object.transform_apply(rotation=True)

    return obj


# --- Create the town ---

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"
mat_ground = bpy.data.materials.new("Ground_Mat")
mat_ground.diffuse_color = (0.3, 0.5, 0.2, 1.0)  # Green
ground.data.materials.append(mat_ground)

# --- Jigsaw piece town layout ---
# We'll place jigsaw pieces in a grid pattern to form the town base
# Then add buildings on top

piece_size = 2.5
piece_thickness = 0.4
tab_size = 0.35
tab_depth = 0.3

# Colors for jigsaw pieces
jigsaw_colors = [
    (0.9, 0.85, 0.7, 1.0),  # Beige
    (0.7, 0.8, 0.9, 1.0),   # Light blue
    (0.8, 0.7, 0.8, 1.0),   # Light purple
    (0.9, 0.7, 0.7, 1.0),   # Light red
    (0.7, 0.9, 0.7, 1.0),   # Light green
    (0.9, 0.9, 0.7, 1.0),   # Light yellow
]

# Place jigsaw pieces in a 4x3 grid
grid_x = 4
grid_y = 3
start_x = -piece_size * grid_x / 2 + piece_size / 2
start_y = -piece_size * grid_y / 2 + piece_size / 2

piece_count = 0
for i in range(grid_x):
    for j in range(grid_y):
        x = start_x + i * piece_size
        y = start_y + j * piece_size
        color = jigsaw_colors[piece_count % len(jigsaw_colors)]
        piece = create_jigsaw_piece_v2(
            name=f"Jigsaw_Piece_{i}_{j}",
            width=piece_size,
            depth=piece_size,
            thickness=piece_thickness,
            tab_size=tab_size,
            tab_depth=tab_depth,
            color=color,
            location=(x, y, piece_thickness / 2),
            rotation_z=0
        )
        piece_count += 1

# --- Church ---
# Place church on a specific piece
church_x = start_x + 1 * piece_size
church_y = start_y + 1 * piece_size

# Church body
bpy.ops.mesh.primitive_cube_add(size=1, location=(church_x, church_y, piece_thickness + 0.8))
church_body = bpy.context.active_object
church_body.name = "Church_Body"
church_body.scale = (0.8, 1.2, 0.8)
bpy.ops.object.transform_apply(scale=True)
mat_church = bpy.data.materials.new("Church_Mat")
mat_church.diffuse_color = (0.95, 0.95, 0.9, 1.0)  # White
church_body.data.materials.append(mat_church)

# Church roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=1.2, depth=0.8, location=(church_x, church_y, piece_thickness + 1.6 + 0.4))
church_roof = bpy.context.active_object
church_roof.name = "Church_Roof"
church_roof.scale = (1, 1.5, 1)
church_roof.rotation_euler = (0, 0, math.pi / 4)
bpy.ops.object.transform_apply(scale=True, rotation=True)
mat_roof = bpy.data.materials.new("Church_Roof_Mat")
mat_roof.diffuse_color = (0.6, 0.3, 0.2, 1.0)  # Brown
church_roof.data.materials.append(mat_roof)

# Church steeple
bpy.ops.mesh.primitive_cube_add(size=1, location=(church_x, church_y + 1.2, piece_thickness + 2.0))
steeple = bpy.context.active_object
steeple.name = "Church_Steeple"
steeple.scale = (0.3, 0.3, 1.0)
bpy.ops.object.transform_apply(scale=True)
steeple.data.materials.append(mat_church)

# Steeple roof
bpy.ops.mesh.primitive_cone_add(vertices=4, radius=0.4, depth=0.6, location=(church_x, church_y + 1.2, piece_thickness + 3.0 + 0.3))
steeple_roof = bpy.context.active_object
steeple_roof.name = "Steeple_Roof"
steeple_roof.scale = (1, 1, 1)
steeple_roof.rotation_euler = (0, 0, math.pi / 4)
bpy.ops.object.transform_apply(rotation=True)
steeple_roof.data.materials.append(mat_roof)

# Church door
bpy.ops.mesh.primitive_cube_add(size=1, location=(church_x, church_y - 1.2, piece_thickness + 0.4))
door = bpy.context.active_object
door.name = "Church_Door"
door.scale = (0.3, 0.05, 0.4)
bpy.ops.object.transform_apply(scale=True)
mat_door = bpy.data.materials.new("Door_Mat")
mat_door.diffuse_color = (0.4, 0.2, 0.1, 1.0)  # Dark brown
door.data.materials.append(mat_door)

# Church windows
for wx in [-0.4, 0.4]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(church_x + wx, church_y - 1.2, piece_thickness + 0.8))
    window = bpy.context.active_object
    window.name = f"Church_Window_{wx}"
    window.scale = (0.15, 0.05, 0.25)
    bpy.ops.object.transform_apply(scale=True)
    mat_window = bpy.data.materials.new("Window_Mat")
    mat_window.diffuse_color = (0.6, 0.8, 0.9, 1.0)  # Light blue
    window.data.materials.append(mat_window)

# --- Street of coloured houses ---
# Place houses along a street (row of jigsaw pieces)
house_colors = [
    (0.9, 0.4, 0.4, 1.0),  # Red
    (0.4, 0.7, 0.9, 1.0),  # Blue
    (0.9, 0.8, 0.3, 1.0),  # Yellow
    (0.5, 0.8, 0.5, 1.0),  # Green
    (0.8, 0.5, 0.8, 1.0),  # Purple
    (0.9, 0.6, 0.4, 1.0),  # Orange
]

# Street runs along the bottom row (j=0)
street_y = start_y + 0 * piece_size
num_houses = 4
house_spacing = piece_size * 0.8

for h in range(num_houses):
    hx = start_x + 0.5 * piece_size + h * house_spacing
    hy = street_y
    color = house_colors[h % len(house_colors)]

    # House body
    bpy.ops.mesh.primitive_cube_add(size=1, location=(hx, hy, piece_thickness + 0.5))
    house = bpy.context.active_object
    house.name = f"House_{h}"
    house.scale = (0.5, 0.6, 0.5)
    bpy.ops.object.transform_apply(scale=True)
    mat_house = bpy.data.materials.new(f"House_Mat_{h}")
    mat_house.diffuse_color = color
    house.data.materials.append(mat_house)

    # House roof
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius=0.7, depth=0.5, location=(hx, hy, piece_thickness + 1.0 + 0.25))
    house_roof = bpy.context.active_object
    house_roof.name = f"House_Roof_{h}"
    house_roof.scale = (1, 1.2, 1)
    house_roof.rotation_euler = (0, 0, math.pi / 4)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    mat_house_roof = bpy.data.materials.new(f"House_Roof_Mat_{h}")
    mat_house_roof.diffuse_color = (0.5, 0.3, 0.2, 1.0)  # Brown
    house_roof.data.materials.append(mat_house_roof)

    # House door
    bpy.ops.mesh.primitive_cube_add(size=1, location=(hx, hy - 0.6, piece_thickness + 0.3))
    h_door = bpy.context.active_object
    h_door.name = f"House_Door_{h}"
    h_door.scale = (0.15, 0.05, 0.3)
    bpy.ops.object.transform_apply(scale=True)
    h_door.data.materials.append(mat_door)

    # House windows
    for wdx in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(hx + wdx, hy - 0.6, piece_thickness + 0.5))
        h_window = bpy.context.active_object
        h_window.name = f"House_Window_{h}_{wdx}"
        h_window.scale = (0.1, 0.05, 0.15)
        bpy.ops.object.transform_apply(scale=True)
        h_window.data.materials.append(mat_window)

# --- Two pieces out of place ---
# Place two jigsaw pieces slightly off the grid, tilted

# Out of place piece 1
oop1_x = start_x + 3.5 * piece_size
oop1_y = start_y + 2.5 * piece_size
piece1 = create_jigsaw_piece_v2(
    name="Jigsaw_OutOfPlace_1",
    width=piece_size,
    depth=piece_size,
    thickness=piece_thickness,
    tab_size=tab_size,
    tab_depth=tab_depth,
    color=(0.9, 0.5, 0.5, 1.0),  # Pink
    location=(oop1_x, oop1_y, piece_thickness / 2 + 0.1),
    rotation_z=math.pi / 6
)

# Out of place piece 2
oop2_x = start_x + 0.5 * piece_size
oop2_y = start_y + 2.5 * piece_size
piece2 = create_jigsaw_piece_v2(
    name="Jigsaw_OutOfPlace_2",
    width=piece_size,
    depth=piece_size,
    thickness=piece_thickness,
    tab_size=tab_size,
    tab_depth=tab_depth,
    color=(0.5, 0.7, 0.9, 1.0),  # Light blue
    location=(oop2_x, oop2_y, piece_thickness / 2 + 0.05),
    rotation_z=-math.pi / 8
)

# --- Add some trees for extra detail ---
for tx, ty in [(start_x - 1, start_y + 2.5 * piece_size), (start_x + 3 * piece_size, start_y + 2.5 * piece_size)]:
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.5, location=(tx, ty, piece_thickness + 0.25))
    trunk = bpy.context.active_object
    trunk.name = f"Tree_Trunk_{tx}_{ty}"
    mat_trunk = bpy.data.materials.new(f"Trunk_Mat_{tx}_{ty}")
    mat_trunk.diffuse_color = (0.4, 0.25, 0.15, 1.0)
    trunk.data.materials.append(mat_trunk)

    # Foliage
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.4, location=(tx, ty, piece_thickness + 0.7))
    foliage = bpy.context.active_object
    foliage.name = f"Tree_Foliage_{tx}_{ty}"
    mat_foliage = bpy.data.materials.new(f"Foliage_Mat_{tx}_{ty}")
    mat_foliage.diffuse_color = (0.2, 0.5, 0.2, 1.0)
    foliage.data.materials.append(mat_foliage)

# --- Set up lighting ---
# Sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3
sun.rotation_euler = (math.pi / 4, 0, math.pi / 4)

# World background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.node_tree.nodes["Background"].inputs[0].default_value = (0.7, 0.8, 0.9, 1.0)  # Sky blue

print("Town built from giant jigsaw pieces created successfully!")
