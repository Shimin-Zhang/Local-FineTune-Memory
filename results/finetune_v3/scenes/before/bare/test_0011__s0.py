import bpy
import math
import random
from mathutils import Vector, Matrix

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.object.select_all(action='DESELECT')

# Set up materials
def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

mat_stone = create_material("Stone", (0.4, 0.4, 0.38, 1.0), roughness=0.9)
mat_mud = create_material("Mud", (0.35, 0.25, 0.15, 1.0), roughness=0.95)
mat_water = create_material("Water", (0.1, 0.2, 0.3, 1.0), roughness=0.1, metallic=0.3)
mat_grass = create_material("Grass", (0.2, 0.4, 0.1, 1.0), roughness=0.9)
mat_wood = create_material("Wood", (0.4, 0.3, 0.15, 1.0), roughness=0.8)
mat_bird = create_material("Bird", (0.1, 0.1, 0.1, 1.0), roughness=0.7)
mat_fisherman = create_material("Fisherman", (0.2, 0.2, 0.25, 1.0), roughness=0.8)
mat_hat = create_material("Hat", (0.3, 0.25, 0.1, 1.0), roughness=0.8)

# --- Stone Bridge Arch ---
# Create the bridge arch using a curve or mesh
# Build a series of stones forming an arch
arch_center = Vector((0, 0, 3))
arch_radius = 5
num_stones = 20
for i in range(num_stones):
    angle = math.pi * i / (num_stones - 1)  # from 0 to pi
    x = arch_center.x + arch_radius * math.cos(angle)
    z = arch_center.z + arch_radius * math.sin(angle)
    # Create a box stone
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, 0, z))
    stone = bpy.context.active_object
    stone.scale = (1.2, 3.0, 0.8)
    stone.rotation_euler = (0, angle - math.pi/2, 0)
    stone.data.materials.append(mat_stone)
    stone.name = f"BridgeStone_{i}"

# Bridge deck (flat top)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 8))
deck = bpy.context.active_object
deck.scale = (12, 6, 0.5)
deck.data.materials.append(mat_stone)
deck.name = "BridgeDeck"

# Side walls of bridge
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=(side * 10, 0, 4))
    wall = bpy.context.active_object
    wall.scale = (2, 6, 8)
    wall.data.materials.append(mat_stone)
    wall.name = f"BridgeWall_{side}"

# --- Mud Nests under the arch ---
# Place a row of mud nests along the bank under the arch
random.seed(42)
for i in range(8):
    x = -6 + i * 1.5 + random.uniform(-0.3, 0.3)
    y = 2.5 + random.uniform(-0.2, 0.2)
    z = 0.3 + random.uniform(-0.1, 0.1)
    
    # Main nest body (flattened sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4, location=(x, y, z), segments=16, ring_count=12)
    nest = bpy.context.active_object
    nest.scale = (1.0, 0.8, 0.6)
    nest.data.materials.append(mat_mud)
    nest.name = f"MudNest_{i}"
    
    # Add a smaller bump on top
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(x + 0.1, y + 0.1, z + 0.3), segments=12, ring_count=8)
    bump = bpy.context.active_object
    bump.scale = (1.0, 0.8, 0.7)
    bump.data.materials.append(mat_mud)
    bump.name = f"MudNestBump_{i}"

# --- Stream (slow water) ---
# Create a flat plane for the stream
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -2, 0.05))
stream = bpy.context.active_object
stream.scale = (20, 4, 1)
stream.data.materials.append(mat_water)
stream.name = "Stream"

# Add some gentle wave-like displacement with a few small bumps
for i in range(15):
    x = random.uniform(-10, 10)
    y = random.uniform(-4, 0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, y, 0.08), segments=8, ring_count=6)
    ripple = bpy.context.active_object
    ripple.scale = (1.5, 1.0, 0.3)
    ripple.data.materials.append(mat_water)
    ripple.name = f"Ripple_{i}"

# --- Bank / Ground ---
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 5, 0))
bank = bpy.context.active_object
bank.scale = (25, 10, 1)
bank.data.materials.append(mat_grass)
bank.name = "Bank"

# --- Fisherman on the bank ---
# Simple low-poly fisherman figure
fisherman_base = Vector((5, 4, 0))

# Body (torso)
bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.0, location=(fisherman_base.x, fisherman_base.y, 1.0))
torso = bpy.context.active_object
torso.data.materials.append(mat_fisherman)
torso.name = "FishermanTorso"

# Head
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(fisherman_base.x, fisherman_base.y, 1.7), segments=16, ring_count=12)
head = bpy.context.active_object
head.data.materials.append(mat_fisherman)
head.name = "FishermanHead"

# Hat (cone)
bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.1, depth=0.3, location=(fisherman_base.x, fisherman_base.y, 1.95))
hat = bpy.context.active_object
hat.data.materials.append(mat_hat)
hat.name = "FishermanHat"

# Legs
for leg_offset in [-0.15, 0.15]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.8, location=(fisherman_base.x + leg_offset, fisherman_base.y, 0.4))
    leg = bpy.context.active_object
    leg.data.materials.append(mat_fisherman)
    leg.name = f"FishermanLeg_{leg_offset}"

# Arms
for arm_offset in [-0.35, 0.35]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.7, location=(fisherman_base.x + arm_offset, fisherman_base.y, 1.2))
    arm = bpy.context.active_object
    arm.rotation_euler = (0, math.pi/4 if arm_offset > 0 else -math.pi/4, 0)
    arm.data.materials.append(mat_fisherman)
    arm.name = f"FishermanArm_{arm_offset}"

# Fishing rod (thin cylinder extending toward the stream)
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=2.5, location=(fisherman_base.x + 1.2, fisherman_base.y - 1.0, 1.5))
rod = bpy.context.active_object
rod.rotation_euler = (math.pi/6, 0, math.pi/4)
rod.data.materials.append(mat_wood)
rod.name = "FishingRod"

# Fishing line (thin cylinder from rod tip down to water)
rod_tip = Vector((fisherman_base.x + 2.2, fisherman_base.y - 1.8, 0.8))
bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.8, location=(rod_tip.x, rod_tip.y, 0.4))
line = bpy.context.active_object
line.data.materials.append(mat_fisherman)
line.name = "FishingLine"

# --- Birds darting over the stream ---
# Simple bird shapes (small elongated spheres with wing-like extensions)
for i in range(6):
    x = random.uniform(-8, 8)
    y = random.uniform(-3, 1)
    z = random.uniform(2, 5)
    
    # Body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, location=(x, y, z), segments=12, ring_count=8)
    bird_body = bpy.context.active_object
    bird_body.scale = (1.5, 0.8, 0.8)
    bird_body.data.materials.append(mat_bird)
    bird_body.name = f"BirdBody_{i}"
    
    # Wings (two small flattened spheres on sides)
    for wing_side in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(x, y + wing_side * 0.2, z + 0.1), segments=8, ring_count=6)
        wing = bpy.context.active_object
        wing.scale = (1.2, 0.5, 0.3)
        wing.rotation_euler = (0, wing_side * math.pi/6, 0)
        wing.data.materials.append(mat_bird)
        wing.name = f"BirdWing_{i}_{wing_side}"

# --- Add a simple sun light ---
bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
sun = bpy.context.active_object
sun.rotation_euler = (math.pi/4, 0, math.pi/4)
sun.data.energy = 3.0
sun.name = "Sun"

# --- Camera ---
bpy.ops.object.camera_add(location=(0, 15, 5))
cam = bpy.context.active_object
cam.rotation_euler = (math.pi/2.5, 0, 0)
cam.name = "Camera"
bpy.context.scene.camera = cam

# Set up world background
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("World")
    bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.5, 0.7, 0.9, 1.0)  # Light blue sky
bg.inputs[1].default_value = 1.0

print("Scene created: mud nests under stone bridge arch, stream, fisherman, and birds.")
