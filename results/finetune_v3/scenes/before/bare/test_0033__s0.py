import bpy
import math
import random
from mathutils import Vector

# Seed for reproducibility
random.seed(42)

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Materials ---
def create_material(name, color, roughness=0.8, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

bone_mat = create_material("OldBone", (0.85, 0.8, 0.7, 1.0), roughness=0.9)
grass_mat = create_material("Grass", (0.2, 0.45, 0.15, 1.0), roughness=1.0)
stone_mat = create_material("StandingStone", (0.35, 0.33, 0.3, 1.0), roughness=0.95)
water_mat = create_material("StreamWater", (0.2, 0.4, 0.6, 1.0), roughness=0.1, metallic=0.1)
water_mat.node_tree.nodes["Principled BSDF"].inputs['Transmission Weight'].default_value = 0.6
water_mat.node_tree.nodes["Principled BSDF"].inputs['IOR'].default_value = 1.33

# --- Ground (valley shape) ---
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100, y_subdivisions=100, size=60)
ground = bpy.context.active_object
ground.name = "ValleyGround"
ground.data.materials.append(grass_mat)

# Displace ground to form a valley (lower in the middle, higher on sides)
import bmesh
me = ground.data
bm = bmesh.new()
bm.from_mesh(me)
for v in bm.verts:
    x, y = v.co.x, v.co.y
    # Valley: lower near center x, higher on sides
    valley_depth = 3.0 * math.exp(-(x * x) / (2 * 8.0 * 8.0))
    # Gentle slope in y
    slope = 0.05 * y
    v.co.z = -valley_depth + slope + random.uniform(-0.1, 0.1)
bm.to_mesh(me)
bm.free()

# --- Helper: Create a rib (curved tube) ---
def create_rib(name, origin, length, radius, curve_factor, rotation=(0,0,0)):
    """Create a rib as a curved cylinder."""
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=length, location=origin)
    rib = bpy.context.active_object
    rib.name = name
    # Bend it: move vertices along a curve
    me = rib.data
    for v in me.vertices:
        t = (v.co.z + length/2) / length  # 0 to 1 along length
        # Curve outward
        offset = curve_factor * math.sin(t * math.pi)
        v.co.x += offset
    rib.rotation_euler = rotation
    rib.data.materials.append(bone_mat)
    return rib

# --- Helper: Create a skull (simplified) ---
def create_skull(name, location, scale=1.0, rotation=(0,0,0)):
    """Create a simplified dragon skull."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, radius=1.0, location=location)
    skull = bpy.context.active_object
    skull.name = name
    skull.scale = (1.2 * scale, 1.5 * scale, 1.0 * scale)
    # Add jaw
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(location[0], location[1] - 1.2 * scale, location[2] - 0.3 * scale))
    jaw = bpy.context.active_object
    jaw.scale = (0.8 * scale, 1.0 * scale, 0.4 * scale)
    # Join
    bpy.ops.object.select_all(action='DESELECT')
    skull.select_set(True)
    jaw.select_set(True)
    bpy.context.view_layer.objects.active = skull
    bpy.ops.object.join()
    skull.rotation_euler = rotation
    skull.data.materials.append(bone_mat)
    return skull

# --- Helper: Create a spine/vertebra ---
def create_vertebra(name, location, scale=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.3 * scale, depth=0.5 * scale, location=location)
    vert = bpy.context.active_object
    vert.name = name
    vert.data.materials.append(bone_mat)
    return vert

# --- Place dragon bones in the valley ---
# Main dragon skeleton along the valley center
bones = []

# Skull at one end
skull1 = create_skull("DragonSkull1", (-15, 0, -1.5), scale=1.5, rotation=(0, math.radians(10), math.radians(15)))
bones.append(skull1)

# Spine vertebrae
for i in range(10):
    x = -12 + i * 2.5
    z = -1.5 + 0.3 * math.sin(i * 0.5)
    vert = create_vertebra(f"Vertebra{i}", (x, 0, z), scale=1.2)
    bones.append(vert)

# Ribs - pairs along the spine
for i in range(8):
    x = -10 + i * 2.8
    # Left rib
    rib_l = create_rib(f"RibL{i}", (x, 0.5, -1.2), length=3.0, radius=0.15, curve_factor=1.5, rotation=(math.radians(90), 0, math.radians(-20)))
    bones.append(rib_l)
    # Right rib
    rib_r = create_rib(f"RibR{i}", (x, -0.5, -1.2), length=3.0, radius=0.15, curve_factor=1.5, rotation=(math.radians(90), 0, math.radians(20)))
    bones.append(rib_r)

# Second smaller dragon skeleton, offset
skull2 = create_skull("DragonSkull2", (10, 5, -1.0), scale=1.0, rotation=(math.radians(20), 0, math.radians(-30)))
bones.append(skull2)

for i in range(6):
    x = 7 + i * 2.0
    y = 5 + 0.3 * math.sin(i)
    z = -1.0 + 0.2 * math.sin(i * 0.7)
    vert = create_vertebra(f"Vertebra2_{i}", (x, y, z), scale=0.9)
    bones.append(vert)

for i in range(5):
    x = 8 + i * 2.2
    y = 5
    # Left rib
    rib_l = create_rib(f"Rib2L{i}", (x, y + 0.4, -0.8), length=2.2, radius=0.12, curve_factor=1.0, rotation=(math.radians(90), 0, math.radians(-25)))
    bones.append(rib_l)
    # Right rib
    rib_r = create_rib(f"Rib2R{i}", (x, y - 0.4, -0.8), length=2.2, radius=0.12, curve_factor=1.0, rotation=(math.radians(90), 0, math.radians(25)))
    bones.append(rib_r)

# Scattered bones
for i in range(15):
    x = random.uniform(-20, 20)
    y = random.uniform(-8, 8)
    z = -1.5 + random.uniform(0, 0.5)
    # Check if in valley (not too high)
    valley_z = -3.0 * math.exp(-(x * x) / (2 * 64)) + 0.05 * y
    if z < valley_z + 0.5:
        continue
    bone_type = random.choice(["long_bone", "small_bone"])
    if bone_type == "long_bone":
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.1, depth=random.uniform(1.0, 2.5), location=(x, y, z))
    else:
        bpy.ops.mesh.primitive_cube_add(size=0.3, location=(x, y, z))
    b = bpy.context.active_object
    b.name = f"ScatteredBone{i}"
    b.rotation_euler = (random.uniform(0, math.pi), random.uniform(0, math.pi), random.uniform(0, math.pi))
    b.data.materials.append(bone_mat)
    bones.append(b)

# --- Stream running through the valley ---
# Create a stream as a flat plane along the valley center
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -1.8))
stream = bpy.context.active_object
stream.name = "Stream"
stream.scale = (30, 1.5, 1)
stream.data.materials.append(water_mat)

# Make stream follow valley by adjusting z of vertices
me = stream.data
for v in me.vertices:
    x = v.co.x * stream.scale.x
    valley_z = -3.0 * math.exp(-(x * x) / (2 * 64)) + 0.05 * v.co.y * stream.scale.y
    v.co.z = valley_z + 0.05  # Slightly above ground

# --- Standing Stone ---
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5, -3, 0))
stone = bpy.context.active_object
stone.name = "StandingStone"
stone.scale = (0.8, 0.8, 3.5)
# Bevel for stone look
mod = stone.modifiers.new("Bevel", 'BEVEL')
mod.width = 0.1
mod.segments = 3
stone.data.materials.append(stone_mat)

# Slight tilt
stone.rotation_euler = (math.radians(3), math.radians(-2), math.radians(5))

# --- Grass tufts (simple cones) ---
for i in range(200):
    x = random.uniform(-25, 25)
    y = random.uniform(-10, 10)
    valley_z = -3.0 * math.exp(-(x * x) / (2 * 64)) + 0.05 * y
    if valley_z > -0.5:  # Only on higher ground or near edges
        bpy.ops.mesh.primitive_cone_add(vertices=5, radius1=0.15, radius2=0.02, depth=0.4, location=(x, y, valley_z + 0.2))
        grass_tuft = bpy.context.active_object
        grass_tuft.name = f"GrassTuft{i}"
        grass_tuft.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), random.uniform(0, math.pi))
        grass_tuft.data.materials.append(grass_mat)

# --- Lighting ---
# Sun
bpy.ops.object.light_add(type='SUN', location=(10, 10, 20))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3.0
sun.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))

# World background
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.4, 0.5, 0.7, 1.0)
    bg.inputs['Strength'].default_value = 0.5

# Camera
bpy.ops.object.camera_add(location=(0, 20, 8))
cam = bpy.context.active_object
cam.name = "Camera"
# Point camera at center
direction = Vector((0, 0, -1)) - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
bpy.context.scene.camera = cam

print("Valley of dragon bones created successfully.")
