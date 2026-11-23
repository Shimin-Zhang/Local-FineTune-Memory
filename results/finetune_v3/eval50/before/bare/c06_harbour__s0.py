import bpy
import math
import random

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Clear collections
for col in bpy.data.collections:
    bpy.data.collections.remove(col)

# Create collections
def get_or_create_collection(name):
    col = bpy.data.collections.get(name)
    if not col:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col

harbour_col = get_or_create_collection("Harbour")
water_col = get_or_create_collection("Water")
pier_col = get_or_create_collection("Pier")
boats_col = get_or_create_collection("Boats")
lighthouse_col = get_or_create_collection("Lighthouse")
crates_col = get_or_create_collection("Crates")

def link_to_collection(obj, col):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col.objects.link(obj)

def add_cube(name, size, location, col, color=(1,1,1,1)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    link_to_collection(obj, col)
    return obj

def add_cylinder(name, r1, r2, depth, location, col, color=(1,1,1,1), vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(radius1=r1, radius2=r2, depth=depth, location=location, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    link_to_collection(obj, col)
    return obj

def add_plane(name, size, location, col, color=(1,1,1,1)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    link_to_collection(obj, col)
    return obj

def add_uv_sphere(name, radius, location, col, color=(1,1,1,1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location)
    obj = bpy.context.active_object
    obj.name = name
    mat = bpy.data.materials.new(name=name+"_mat")
    mat.diffuse_color = color
    obj.data.materials.append(mat)
    link_to_collection(obj, col)
    return obj

# --- Water ---
water = add_plane("Water", 40, (0, 0, -0.5), water_col, color=(0.1, 0.3, 0.5, 1))
water.scale = (1, 1, 1)

# --- Harbour Basin (shallow area) ---
basin = add_cube("Harbour_Basin", 1, (0, 0, 0), harbour_col, color=(0.4, 0.35, 0.3, 1))
basin.scale = (12, 10, 0.3)
basin.location = (0, 0, -0.2)

# --- Pier ---
# Main pier platform
pier_platform = add_cube("Pier_Platform", 1, (0, 0, 0.5), pier_col, color=(0.5, 0.35, 0.2, 1))
pier_platform.scale = (8, 2, 0.2)
pier_platform.location = (0, 0, 0.5)

# Pier support posts
for i in range(-3, 4):
    post = add_cube(f"Pier_Post_{i}", 0.3, (i*2, 0, 0), pier_col, color=(0.4, 0.25, 0.15, 1))
    post.scale = (0.5, 0.5, 1.5)
    post.location = (i*2, 0, -0.25)

# Pier railing posts
for i in range(-3, 4):
    rail_post = add_cube(f"Pier_Rail_{i}", 0.1, (i*2, 1, 0.8), pier_col, color=(0.4, 0.25, 0.15, 1))
    rail_post.scale = (0.3, 0.3, 1.0)
    rail_post.location = (i*2, 1, 0.8)

    rail_post2 = add_cube(f"Pier_Rail2_{i}", 0.1, (i*2, -1, 0.8), pier_col, color=(0.4, 0.25, 0.15, 1))
    rail_post2.scale = (0.3, 0.3, 1.0)
    rail_post2.location = (i*2, -1, 0.8)

# Railing bars
rail_bar_top = add_cube("Rail_Bar_Top", 0.1, (0, 1, 1.2), pier_col, color=(0.4, 0.25, 0.15, 1))
rail_bar_top.scale = (16, 0.3, 0.3)
rail_bar_top.location = (0, 1, 1.2)

rail_bar_bottom = add_cube("Rail_Bar_Bottom", 0.1, (0, 1, 0.9), pier_col, color=(0.4, 0.25, 0.15, 1))
rail_bar_bottom.scale = (16, 0.3, 0.3)
rail_bar_bottom.location = (0, 1, 0.9)

rail_bar_top2 = add_cube("Rail_Bar_Top2", 0.1, (0, -1, 1.2), pier_col, color=(0.4, 0.25, 0.15, 1))
rail_bar_top2.scale = (16, 0.3, 0.3)
rail_bar_top2.location = (0, -1, 1.2)

rail_bar_bottom2 = add_cube("Rail_Bar_Bottom2", 0.1, (0, -1, 0.9), pier_col, color=(0.4, 0.25, 0.15, 1))
rail_bar_bottom2.scale = (16, 0.3, 0.3)
rail_bar_bottom2.location = (0, -1, 0.9)

# --- Boats ---
def create_boat(name, location, rotation, scale, hull_color, col):
    # Hull
    hull = add_cube(name + "_Hull", 1, location, col, color=hull_color)
    hull.scale = (2*scale, 0.8*scale, 0.5*scale)
    hull.location = (location[0], location[1], 0.2)
    # Taper the bow
    # Add deck
    deck = add_cube(name + "_Deck", 1, (location[0], location[1], 0.5), col, color=(0.6, 0.45, 0.3, 1))
    deck.scale = (1.8*scale, 0.7*scale, 0.1*scale)
    deck.location = (location[0], location[1], 0.5)
    # Cabin
    cabin = add_cube(name + "_Cabin", 1, (location[0] - 0.5*scale, location[1], 0.8), col, color=(0.9, 0.85, 0.8, 1))
    cabin.scale = (0.8*scale, 0.5*scale, 0.4*scale)
    cabin.location = (location[0] - 0.5*scale, location[1], 0.8)
    # Mast
    mast = add_cylinder(name + "_Mast", 0.05, 0.05, 2*scale, (location[0], location[1], 1.2), col, color=(0.5, 0.35, 0.2, 1))
    mast.location = (location[0], location[1], 1.2)
    # Sail (simple plane)
    sail = add_plane(name + "_Sail", 1, (location[0] + 0.3*scale, location[1], 1.5), col, color=(0.95, 0.95, 0.9, 1))
    sail.scale = (0.8*scale, 0.05, 1.0*scale)
    sail.location = (location[0] + 0.3*scale, location[1], 1.5)
    sail.rotation_euler = (math.radians(90), 0, 0)

    return hull

# Boat 1
create_boat("Boat1", (-3, 3, 0), 0, 1.0, (0.7, 0.2, 0.1, 1), boats_col)

# Boat 2
create_boat("Boat2", (3, -3, 0), math.radians(45), 0.8, (0.1, 0.3, 0.6, 1), boats_col)

# --- Lighthouse ---
# Base
lh_base = add_cylinder("Lighthouse_Base", 1.5, 2.0, 1, (8, 8, 0), lighthouse_col, color=(0.9, 0.9, 0.85, 1), vertices=24)
lh_base.location = (8, 8, 0.5)

# Tower
lh_tower = add_cylinder("Lighthouse_Tower", 1.0, 1.5, 6, (8, 8, 3.5), lighthouse_col, color=(0.95, 0.9, 0.85, 1), vertices=24)
lh_tower.location = (8, 8, 3.5)

# Red stripe
lh_stripe = add_cylinder("Lighthouse_Stripe", 1.25, 1.25, 1.5, (8, 8, 3.5), lighthouse_col, color=(0.8, 0.1, 0.1, 1), vertices=24)
lh_stripe.location = (8, 8, 3.5)

# Gallery
lh_gallery = add_cylinder("Lighthouse_Gallery", 1.8, 1.8, 0.3, (8, 8, 6.8), lighthouse_col, color=(0.2, 0.2, 0.2, 1), vertices=24)
lh_gallery.location = (8, 8, 6.8)

# Light room
lh_light_room = add_cylinder("Lighthouse_Light_Room", 1.2, 1.2, 1.5, (8, 8, 7.8), lighthouse_col, color=(0.3, 0.3, 0.3, 1), vertices=24)
lh_light_room.location = (8, 8, 7.8)

# Glass panels (simplified as a slightly smaller cylinder with different color)
lh_glass = add_cylinder("Lighthouse_Glass", 1.1, 1.1, 1.3, (8, 8, 7.8), lighthouse_col, color=(0.7, 0.85, 0.9, 1), vertices=24)
lh_glass.location = (8, 8, 7.8)

# Roof
lh_roof = add_cylinder("Lighthouse_Roof", 0.1, 1.4, 1.0, (8, 8, 8.8), lighthouse_col, color=(0.2, 0.2, 0.2, 1), vertices=24)
lh_roof.location = (8, 8, 8.8)

# Light beam (emissive sphere)
lh_light = add_uv_sphere("Lighthouse_Light", 0.5, (8, 8, 7.8), lighthouse_col, color=(1, 0.9, 0.5, 1))
lh_light.location = (8, 8, 7.8)
# Make it emissive
mat = lh_light.data.materials[0]
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
output = nodes.new('ShaderNodeOutputMaterial')
emission = nodes.new('ShaderNodeEmission')
emission.inputs[0].default_value = (1, 0.9, 0.5, 1)
emission.inputs[1].default_value = 5
links.new(emission.outputs[0], output.inputs[0])

# --- Crates ---
crate_colors = [
    (0.7, 0.5, 0.3, 1),
    (0.6, 0.4, 0.2, 1),
    (0.8, 0.6, 0.4, 1),
    (0.5, 0.35, 0.2, 1),
    (0.65, 0.45, 0.25, 1),
    (0.75, 0.55, 0.35, 1),
    (0.55, 0.4, 0.25, 1),
    (0.6, 0.45, 0.3, 1),
]

crate_positions = [
    (-5, 2, 0.5), (-4, 2.5, 0.5), (-5.5, 1.5, 0.5),
    (-4.5, 3, 0.5), (-5, 3.5, 0.5),
    (5, 2, 0.5), (5.5, 2.5, 0.5), (4.5, 1.5, 0.5),
    (5, 3, 0.5), (4, 2, 0.5),
    (-2, 5, 0.5), (-1, 5.5, 0.5), (0, 5, 0.5),
    (2, 5, 0.5), (3, 5.5, 0.5),
    (-6, -2, 0.5), (-5, -2.5, 0.5), (-6.5, -1.5, 0.5),
]

for i, pos in enumerate(crate_positions):
    size = random.uniform(0.4, 0.8)
    color = crate_colors[i % len(crate_colors)]
    crate = add_cube(f"Crate_{i}", size, pos, crates_col, color=color)
    crate.scale = (size, size, size)
    crate.location = pos
    # Slight random rotation
    crate.rotation_euler = (0, 0, random.uniform(0, math.radians(30)))

# Add some stacked crates
for i in range(5):
    x = -5 + random.uniform(-1, 1)
    y = 2 + random.uniform(-1, 1)
    z = 1.0 + i * 0.5
    size = random.uniform(0.3, 0.5)
    color = crate_colors[i % len(crate_colors)]
    crate = add_cube(f"Stacked_Crate_{i}", size, (x, y, z), crates_col, color=color)
    crate.scale = (size, size, size)
    crate.location = (x, y, z)
    crate.rotation_euler = (0, 0, random.uniform(0, math.radians(15)))

# Add a few crates near the lighthouse
for i in range(3):
    x = 8 + random.uniform(-2, 2)
    y = 8 + random.uniform(-2, 2)
    z = 0.5
    size = random.uniform(0.4, 0.6)
    color = crate_colors[i % len(crate_colors)]
    crate = add_cube(f"Lighthouse_Crate_{i}", size, (x, y, z), crates_col, color=color)
    crate.scale = (size, size, size)
    crate.location = (x, y, z)
    crate.rotation_euler = (0, 0, random.uniform(0, math.radians(20)))

# Add bollards on the pier
for i in range(-2, 3):
    bollard = add_cylinder(f"Bollard_{i}", 0.15, 0.15, 0.5, (i*2, 0.8, 0.75), pier_col, color=(0.15, 0.15, 0.15, 1), vertices=12)
    bollard.location = (i*2, 0.8, 0.75)

    bollard2 = add_cylinder(f"Bollard2_{i}", 0.15, 0.15, 0.5, (i*2, -0.8, 0.75), pier_col, color=(0.15, 0.15, 0.15, 1),