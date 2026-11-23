import bpy
import math
import random
from mathutils import Vector

# Set up the scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up lighting for dappled sun effect
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
nodes = world.node_tree.nodes
links = world.node_tree.links

# Background color for sky
bg_node = nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.7, 0.8, 1.0, 1.0)
    bg_node.inputs[1].default_value = 1.0

# Create a sun light for dappled effect
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_data.energy = 3.0
sun_data.angle = math.radians(5)
sun_obj = bpy.data.objects.new(name="Sun", object_data=sun_data)
bpy.context.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(0))

# Create ground plane
bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# Material for ground (earthy)
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
ground.data.materials.append(ground_mat)

# Create stepping stone path
def create_stone(x, y, z, size=0.5, name="Stone"):
    bpy.ops.mesh.primitive_cylinder_add(radius=size, depth=0.1, location=(x, y, z))
    stone = bpy.context.active_object
    stone.name = name
    # Slightly randomize scale for natural look
    stone.scale = (random.uniform(0.8, 1.2), random.uniform(0.8, 1.2), 1)
    stone.rotation_euler = (0, 0, random.uniform(0, math.pi))
    
    stone_mat = bpy.data.materials.new(name="StoneMaterial")
    stone_mat.use_nodes = True
    bsdf = stone_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
    stone.data.materials.append(stone_mat)
    return stone

# Create a path of stepping stones
stones = []
for i in range(8):
    x = -3 + i * 0.8
    y = random.uniform(-0.5, 0.5)
    stone = create_stone(x, y, 0.05, size=0.4, name=f"SteppingStone_{i}")
    stones.append(stone)

# Create a stone toad (simplified as a small rounded shape)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(2, 1, 0.15))
toad = bpy.context.active_object
toad.name = "StoneToad"
toad.scale = (1.2, 1.0, 0.6)  # Flatten to look like a toad

toad_mat = bpy.data.materials.new(name="ToadMaterial")
toad_mat.use_nodes = True
bsdf = toad_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.4, 0.4, 0.4, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
toad.data.materials.append(toad_mat)

# Add eyes to toad
for eye_offset in [(-0.15, 0.1), (0.15, 0.1)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(2 + eye_offset[0], 1 + eye_offset[1], 0.35))
    eye = bpy.context.active_object
    eye.name = "ToadEye"
    eye_mat = bpy.data.materials.new(name="EyeMaterial")
    eye_mat.use_nodes = True
    bsdf = eye_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.1, 0.1, 0.1, 1.0)
    eye.data.materials.append(eye_mat)

# Create wide-leaf plants
def create_plant(x, y, z, name="Plant"):
    # Stem
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.5, location=(x, y, z + 0.25))
    stem = bpy.context.active_object
    stem.name = name + "_Stem"
    stem_mat = bpy.data.materials.new(name="StemMaterial")
    stem_mat.use_nodes = True
    bsdf = stem_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.2, 0.4, 0.1, 1.0)
    stem.data.materials.append(stem_mat)
    
    # Wide leaf
    bpy.ops.mesh.primitive_plane_add(size=0.4, location=(x, y, z + 0.5))
    leaf = bpy.context.active_object
    leaf.name = name + "_Leaf"
    leaf.scale = (1.5, 0.8, 1)
    leaf.rotation_euler = (math.radians(random.uniform(-30, 30)), math.radians(random.uniform(-30, 30)), random.uniform(0, math.pi))
    
    leaf_mat = bpy.data.materials.new(name="LeafMaterial")
    leaf_mat.use_nodes = True
    bsdf = leaf_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.1, 0.5, 0.1, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
    leaf.data.materials.append(leaf_mat)

# Create a bed of plants around the path
for i in range(20):
    x = random.uniform(-4, 4)
    y = random.uniform(-2, 2)
    # Avoid placing plants directly on the path
    if abs(y) < 0.8:
        continue
    create_plant(x, y, 0, name=f"Plant_{i}")

# Create old trees
def create_tree(x, y, z, name="Tree"):
    # Trunk
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=3, location=(x, y, z + 1.5))
    trunk = bpy.context.active_object
    trunk.name = name + "_Trunk"
    trunk_mat = bpy.data.materials.new(name="TrunkMaterial")
    trunk_mat.use_nodes = True
    bsdf = trunk_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.3, 0.2, 0.1, 1.0)
    trunk.data.materials.append(trunk_mat)
    
    # Canopy (multiple spheres for a bushy look)
    for j in range(5):
        offset_x = random.uniform(-1, 1)
        offset_y = random.uniform(-1, 1)
        offset_z = random.uniform(2.5, 4)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.8, 1.2), location=(x + offset_x, y + offset_y, z + offset_z))
        canopy = bpy.context.active_object
        canopy.name = name + f"_Canopy_{j}"
        canopy_mat = bpy.data.materials.new(name="CanopyMaterial")
        canopy_mat.use_nodes = True
        bsdf = canopy_mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.1, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.8
        canopy.data.materials.append(canopy_mat)

# Place a few old trees
create_tree(-5, -3, 0, name="Tree_1")
create_tree(5, -3, 0, name="Tree_2")
create_tree(-4, 4, 0, name="Tree_3")
create_tree(4, 4, 0, name="Tree_4")

# Create a hammock between two trees
# Tree 1 is at (-5, -3, 0), Tree 3 is at (-4, 4, 0)
# Place hammock between them
hammock_start = Vector((-4.5, -2, 2))
hammock_end = Vector((-4.5, 3, 2))
hammock_mid = (hammock_start + hammock_end) / 2

# Create hammock as a curved plane
bpy.ops.mesh.primitive_plane_add(size=1, location=hammock_mid)
hammock = bpy.context.active_object
hammock.name = "Hammock"
hammock.scale = (0.5, 2, 1)
hammock.rotation_euler = (math.radians(90), 0, math.radians(90))

# Add some curve to the hammock by editing vertices
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.transform.resize(value=(1, 1, 0.5))
bpy.ops.object.mode_set(mode='OBJECT')

hammock_mat = bpy.data.materials.new(name="HammockMaterial")
hammock_mat.use_nodes = True
bsdf = hammock_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs["Base Color"].default_value = (0.8, 0.6, 0.3, 1.0)
bsdf.inputs["Roughness"].default_value = 0.9
hammock.data.materials.append(hammock_mat)

# Add ropes to connect hammock to trees
for end_point, tree_pos in [(hammock_start, Vector((-5, -3, 0))), (hammock_end, Vector((-4, 4, 0)))]:
    # Create a simple rope as a cylinder
    direction = end_point - tree_pos
    length = direction.length
    midpoint = (end_point + tree_pos) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=length, location=midpoint)
    rope = bpy.context.active_object
    rope.name = "Rope"
    # Align rope to direction
    rope.rotation_euler = direction.to_track_quat('Z', 'Y').to_euler()
    
    rope_mat = bpy.data.materials.new(name="RopeMaterial")
    rope_mat.use_nodes = True
    bsdf = rope_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.5, 0.4, 0.3, 1.0)
    rope.data.materials.append(rope_mat)

# Set up camera
bpy.ops.object.camera_add(location=(0, -8, 3))
camera = bpy.context.active_object
camera.name = "Camera"
bpy.context.scene.camera = camera

# Point camera towards the scene
direction = Vector((0, 0, 0)) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Render settings
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.film_transparent = False

print("Scene created successfully!")
