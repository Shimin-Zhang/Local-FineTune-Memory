import bpy
import math
import random

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# --- Helper functions ---
def create_cylinder(name, radius, depth, x=0, y=0, z=0, segments=32, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=(x, y, z), vertices=segments, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_cube(name, size, x=0, y=0, z=0, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=(x, y, z), rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def create_sphere(name, radius, x=0, y=0, z=0):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(x, y, z))
    obj = bpy.context.active_object
    obj.name = name
    return obj

def set_material(obj, color, roughness=0.5):
    mat = bpy.data.materials.new(name=obj.name + "_mat")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    obj.data.materials.clear()
    obj.data.materials.append(mat)

# --- Water ---
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.5))
water = bpy.context.active_object
water.name = "Water"
set_material(water, (0.1, 0.3, 0.5, 1.0), 0.1)

# --- Ground / Shore ---
bpy.ops.mesh.primitive_plane_add(size=40, location=(15, 0, 0))
ground = bpy.context.active_object
ground.name = "Shore"
set_material(ground, (0.6, 0.5, 0.3, 1.0), 0.8)

# --- Pier ---
pier_y = -5
pier_x_start = 5
pier_x_end = 20
pier_width = 3
pier_height = 0.5

# Pier deck
bpy.ops.mesh.primitive_cube_add(size=1, location=((pier_x_start + pier_x_end)/2, pier_y, pier_height))
pier_deck = bpy.context.active_object
pier_deck.name = "Pier_Deck"
pier_deck.scale = ((pier_x_end - pier_x_start), pier_width, pier_height)
set_material(pier_deck, (0.4, 0.3, 0.2, 1.0), 0.7)

# Pier posts
num_posts = 5
for i in range(num_posts):
    x = pier_x_start + i * (pier_x_end - pier_x_start) / (num_posts - 1)
    post = create_cylinder(f"Pier_Post_{i}", 0.2, 2, x=x, y=pier_y, z=0)
    set_material(post, (0.3, 0.2, 0.1, 1.0), 0.8)

# --- Lighthouse ---
lh_x = 25
lh_y = -3
lh_base_z = 0

# Base
lh_base = create_cylinder("Lighthouse_Base", 2, 1, x=lh_x, y=lh_y, z=lh_base_z + 0.5)
set_material(lh_base, (0.8, 0.8, 0.8, 1.0), 0.3)

# Tower
lh_tower = create_cylinder("Lighthouse_Tower", 1.5, 8, x=lh_x, y=lh_y, z=lh_base_z + 1 + 4)
set_material(lh_tower, (0.9, 0.9, 0.9, 1.0), 0.3)

# Red stripe
stripe = create_cylinder("Lighthouse_Stripe", 1.52, 2, x=lh_x, y=lh_y, z=lh_base_z + 1 + 5)
set_material(stripe, (0.8, 0.1, 0.1, 1.0), 0.3)

# Gallery
lh_gallery = create_cylinder("Lighthouse_Gallery", 2, 0.5, x=lh_x, y=lh_y, z=lh_base_z + 1 + 8 + 0.25)
set_material(lh_gallery, (0.2, 0.2, 0.2, 1.0), 0.4)

# Light room
lh_light_room = create_cylinder("Lighthouse_Light_Room", 1.2, 1.5, x=lh_x, y=lh_y, z=lh_base_z + 1 + 8 + 0.5 + 0.75)
set_material(lh_light_room, (0.9, 0.9, 0.7, 1.0), 0.1)

# Roof
bpy.ops.mesh.primitive_cone_add(radius1=1.3, radius2=0, depth=1.5, location=(lh_x, lh_y, lh_base_z + 1 + 8 + 0.5 + 1.5 + 0.75))
roof = bpy.context.active_object
roof.name = "Lighthouse_Roof"
set_material(roof, (0.1, 0.1, 0.1, 1.0), 0.4)

# --- Boats ---
def create_boat(name, x, y, z, scale=1.0):
    # Hull
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    hull = bpy.context.active_object
    hull.name = name + "_Hull"
    hull.scale = (4 * scale, 1.5 * scale, 0.8 * scale)
    set_material(hull, (0.5, 0.3, 0.1, 1.0), 0.6)
    
    # Deck
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z + 0.4 * scale))
    deck = bpy.context.active_object
    deck.name = name + "_Deck"
    deck.scale = (3.8 * scale, 1.3 * scale, 0.1 * scale)
    set_material(deck, (0.6, 0.4, 0.2, 1.0), 0.5)
    
    # Cabin
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + 1 * scale, y, z + 0.4 * scale + 0.5 * scale))
    cabin = bpy.context.active_object
    cabin.name = name + "_Cabin"
    cabin.scale = (1.5 * scale, 1 * scale, 1 * scale)
    set_material(cabin, (0.8, 0.8, 0.8, 1.0), 0.4)
    
    # Mast
    mast = create_cylinder(name + "_Mast", 0.05, 3 * scale, x=x - 1 * scale, y=y, z=z + 0.4 * scale + 1.5 * scale)
    set_material(mast, (0.3, 0.2, 0.1, 1.0), 0.7)
    
    # Sail
    bpy.ops.mesh.primitive_plane_add(size=1, location=(x - 1 * scale, y + 0.8 * scale, z + 0.4 * scale + 1.5 * scale))
    sail = bpy.context.active_object
    sail.name = name + "_Sail"
    sail.scale = (1.5 * scale, 2 * scale, 1)
    sail.rotation_euler = (math.radians(90), 0, 0)
    set_material(sail, (0.9, 0.9, 0.9, 1.0), 0.3)

# Boat 1
create_boat("Boat1", x=-2, y=-8, z=0.2, scale=1.0)

# Boat 2
create_boat("Boat2", x=2, y=-12, z=0.2, scale=0.8)

# --- Crates ---
crate_positions = [
    (6, -4, 0.75), (7, -4.5, 0.75), (6.5, -3.5, 0.75),
    (8, -4, 0.75), (8.5, -4.5, 0.75),
    (10, -4, 0.75), (10.5, -4.5, 0.75), (11, -4, 0.75)
]

for i, (cx, cy, cz) in enumerate(crate_positions):
    crate = create_cube(f"Crate_{i}", 0.8, x=cx, y=cy, z=cz)
    set_material(crate, (0.6, 0.45, 0.2, 1.0), 0.7)

# --- Add some rocks near shore ---
for i in range(5):
    x = random.uniform(20, 28)
    y = random.uniform(-8, 5)
    rock = create_sphere(f"Rock_{i}", random.uniform(0.3, 0.8), x=x, y=y, z=0.1)
    rock.scale = (1, 1, 0.6)
    set_material(rock, (0.4, 0.4, 0.4, 1.0), 0.9)

# --- Lighting ---
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# World settings
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.5, 0.7, 0.9, 1.0)
    bg_node.inputs[1].default_value = 1.0

print("Harbour scene created successfully!")
