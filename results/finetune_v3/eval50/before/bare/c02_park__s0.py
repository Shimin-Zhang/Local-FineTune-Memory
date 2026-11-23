import bpy
import math
import random

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Set up basic scene properties
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.eevee.taa_render_samples = 64

# Add a ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Create a green material for the ground
mat_ground = bpy.data.materials.new(name="Grass")
mat_ground.use_nodes = True
nodes = mat_ground.node_tree.nodes
links = mat_ground.node_tree.links
bsdf = nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.8
ground.data.materials.append(mat_ground)

# Create a trunk material
mat_trunk = bpy.data.materials.new(name="Trunk")
mat_trunk.use_nodes = True
bsdf_trunk = mat_trunk.node_tree.nodes["Principled BSDF"]
bsdf_trunk.inputs["Base Color"].default_value = (0.3, 0.15, 0.05, 1.0)
bsdf_trunk.inputs["Roughness"].default_value = 0.9

# Create a leaf material
mat_leaf = bpy.data.materials.new(name="Leaves")
mat_leaf.use_nodes = True
bsdf_leaf = mat_leaf.node_tree.nodes["Principled BSDF"]
bsdf_leaf.inputs["Base Color"].default_value = (0.05, 0.35, 0.05, 1.0)
bsdf_leaf.inputs["Roughness"].default_value = 0.7

# Create a bench material
mat_bench = bpy.data.materials.new(name="BenchWood")
mat_bench.use_nodes = True
bsdf_bench = mat_bench.node_tree.nodes["Principled BSDF"]
bsdf_bench.inputs["Base Color"].default_value = (0.4, 0.25, 0.1, 1.0)
bsdf_bench.inputs["Roughness"].default_value = 0.8

# Create a path material
mat_path = bpy.data.materials.new(name="Path")
mat_path.use_nodes = True
bsdf_path = mat_path.node_tree.nodes["Principled BSDF"]
bsdf_path.inputs["Base Color"].default_value = (0.6, 0.55, 0.45, 1.0)
bsdf_path.inputs["Roughness"].default_value = 0.9

# Create a water material for the pond
mat_water = bpy.data.materials.new(name="Water")
mat_water.use_nodes = True
bsdf_water = mat_water.node_tree.nodes["Principled BSDF"]
bsdf_water.inputs["Base Color"].default_value = (0.1, 0.3, 0.5, 1.0)
bsdf_water.inputs["Roughness"].default_value = 0.1
bsdf_water.inputs["Metallic"].default_value = 0.1
bsdf_water.inputs["Transmission Weight"].default_value = 0.7

# Function to create a tree
def create_tree(location, scale=1.0):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2 * scale, depth=2.0 * scale, location=(location[0], location[1], 1.0 * scale))
    trunk = bpy.context.active_object
    trunk.name = f"Trunk_{location[0]:.1f}_{location[1]:.1f}"
    trunk.data.materials.append(mat_trunk)

    # Foliage - use icosphere for organic look
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1.2 * scale, location=(location[0], location[1], 2.5 * scale))
    foliage = bpy.context.active_object
    foliage.name = f"Foliage_{location[0]:.1f}_{location[1]:.1f}"
    foliage.data.materials.append(mat_leaf)
    # Add some randomness to foliage shape
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.transform.randomize(scale=(0.8, 1.2), rotation=(0.1, 0.1, 0.1))
    bpy.ops.object.mode_set(mode='OBJECT')

    return trunk, foliage

# Create three trees
tree_positions = [(-8, -5, 1.2), (6, -8, 1.0), (-3, 8, 1.4)]
for pos in tree_positions:
    create_tree(pos[:2], scale=pos[2])

# Create a bench
def create_bench(location):
    # Seat
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1], 0.5))
    seat = bpy.context.active_object
    seat.scale = (1.5, 0.4, 0.1)
    seat.name = "Bench_Seat"
    seat.data.materials.append(mat_bench)

    # Backrest
    bpy.ops.mesh.primitive_cube_add(size=1, location=(location[0], location[1] - 0.35, 0.9))
    back = bpy.context.active_object
    back.scale = (1.5, 0.08, 0.5)
    back.rotation_euler = (math.radians(-10), 0, 0)
    back.name = "Bench_Back"
    back.data.materials.append(mat_bench)

    # Legs (4 legs)
    leg_positions = [
        (location[0] - 0.6, location[1] - 0.15, 0.25),
        (location[0] + 0.6, location[1] - 0.15, 0.25),
        (location[0] - 0.6, location[1] + 0.15, 0.25),
        (location[0] + 0.6, location[1] + 0.15, 0.25),
    ]
    for lp in leg_positions:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.5, location=lp)
        leg = bpy.context.active_object
        leg.name = "Bench_Leg"
        leg.data.materials.append(mat_bench)

create_bench((2, 2))

# Create a path (a flat rectangular strip)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.01))
path = bpy.context.active_object
path.scale = (12, 1.5, 1)
path.name = "Path"
path.data.materials.append(mat_path)

# Create a pond (a flat circular mesh slightly above ground)
bpy.ops.mesh.primitive_cylinder_add(radius=3, depth=0.05, location=(8, 5, 0.025))
pond = bpy.context.active_object
pond.name = "Pond"
pond.data.materials.append(mat_water)

# Add a sun light
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a world background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.5, 0.7, 1.0, 1.0)
    bg_node.inputs[1].default_value = 0.5
