import bpy
import math
import mathutils
from mathutils import Vector

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Create a new collection for the memorial
memorial_col = bpy.data.collections.new("Memorial")
bpy.context.scene.collection.children.link(memorial_col)

# Materials
def create_material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

stone_mat = create_material("Stone", (0.55, 0.53, 0.50, 1.0), roughness=0.85)
dark_stone_mat = create_material("Dark Stone", (0.30, 0.28, 0.26, 1.0), roughness=0.9)
pool_water_mat = create_material("Pool Water", (0.1, 0.35, 0.5, 1.0), roughness=0.05, metallic=0.3)
path_mat = create_material("Path Stone", (0.45, 0.44, 0.42, 1.0), roughness=0.8)
step_mat = create_material("Step Stone", (0.5, 0.48, 0.46, 1.0), roughness=0.85)
grass_mat = create_material("Grass", (0.2, 0.45, 0.15, 1.0), roughness=1.0)

# Helper: assign object to memorial collection
def assign_to_memorial(obj):
    for col in obj.users_collection:
        col.objects.unlink(obj)
    memorial_col.objects.link(obj)

# Ground plane
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.01))
ground = bpy.context.object
ground.name = "Ground"
ground.data.materials.append(grass_mat)
assign_to_memorial(ground)

# --- Central Pool ---
pool_radius = 2.0
pool_depth = 0.5
pool_wall_thickness = 0.3

# Pool basin (cylinder, hollowed)
bpy.ops.mesh.primitive_cylinder_add(radius=pool_radius + pool_wall_thickness, depth=pool_depth, location=(0, 0, -pool_depth/2 + 0.02), vertices=64)
pool_outer = bpy.context.object
pool_outer.name = "Pool Outer Wall"
pool_outer.data.materials.append(dark_stone_mat)
assign_to_memorial(pool_outer)

# Inner basin
bpy.ops.mesh.primitive_cylinder_add(radius=pool_radius, depth=pool_depth, location=(0, 0, -pool_depth/2 + 0.02), vertices=64)
pool_inner = bpy.context.object
pool_inner.name = "Pool Inner"
pool_inner.data.materials.append(dark_stone_mat)
assign_to_memorial(pool_inner)

# Water surface
bpy.ops.mesh.primitive_cylinder_add(radius=pool_radius - 0.05, depth=0.02, location=(0, 0, -0.05), vertices=64)
water = bpy.context.object
water.name = "Pool Water"
water.data.materials.append(pool_water_mat)
assign_to_memorial(water)

# Pool rim (torus-like ring)
bpy.ops.mesh.primitive_torus_add(major_radius=pool_radius + pool_wall_thickness/2, minor_radius=pool_wall_thickness/2, location=(0, 0, 0.02), major_segments=64, minor_segments=16)
pool_rim = bpy.context.object
pool_rim.name = "Pool Rim"
pool_rim.data.materials.append(stone_mat)
assign_to_memorial(pool_rim)

# --- Concentric Stone Rings ---
# Each ring is a torus-like band with varying radius
ring_specs = [
    # (inner_radius, outer_radius, height, name_offset)
    (3.0, 4.5, 0.6, "Ring 1"),
    (5.5, 7.0, 0.55, "Ring 2"),
    (8.0, 9.5, 0.5, "Ring 3"),
    (10.5, 12.0, 0.45, "Ring 4"),
    (13.0, 14.5, 0.4, "Ring 5"),
]

for idx, (r_in, r_out, h, label) in enumerate(ring_specs):
    mid_r = (r_in + r_out) / 2
    width = r_out - r_in
    # Create ring as a cylinder with hole (use torus scaled or use a custom mesh)
    # Use a cylinder and boolean, or simpler: create a flat torus
    bpy.ops.mesh.primitive_torus_add(
        major_radius=mid_r,
        minor_radius=width/2,
        location=(0, 0, h/2),
        major_segments=96,
        minor_segments=4
    )
    ring = bpy.context.object
    ring.name = f"{label} Stone Ring"
    # Flatten the torus vertically
    ring.scale.z = h / (width)
    ring.data.materials.append(stone_mat if idx % 2 == 0 else dark_stone_mat)
    assign_to_memorial(ring)

    # Add "carved names" as small text objects on top of each ring
    # Place a few text objects around the ring
    num_names = 8 + idx * 2
    for i in range(num_names):
        angle = (i / num_names) * 2 * math.pi
        x = mid_r * math.cos(angle)
        y = mid_r * math.sin(angle)
        # Create a small text object
        curve = bpy.data.curves.new(f"Name_{label}_{i}", 'FONT')
        curve.body = f"Name {i+1}"
        curve.size = 0.15
        curve.extrude = 0.02
        obj = bpy.data.objects.new(f"Name_{label}_{i}", curve)
        obj.location = (x, y, h + 0.01)
        obj.rotation_euler = (0, 0, -angle + math.pi/2)
        obj.data.materials.append(dark_stone_mat)
        bpy.context.scene.collection.objects.link(obj)
        assign_to_memorial(obj)

# --- Wide Steps ---
# Steps leading to the central pool area, on the north side
step_width = 6.0
step_depth = 0.4
step_height = 0.15
num_steps = 5
start_y = pool_radius + pool_wall_thickness + 0.5

for i in range(num_steps):
    y_pos = start_y + i * step_depth
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, y_pos, step_height * (i + 1) - step_height/2)
    )
    step = bpy.context.object
    step.name = f"Step {i+1}"
    step.scale = (step_width/2, step_depth/2, step_height/2)
    step.data.materials.append(step_mat)
    assign_to_memorial(step)

# --- Quiet Paths Between Rings ---
# Paths radiating outward at 4 cardinal directions
path_width = 1.2
path_length = 16.0

for angle_deg in [0, 90, 180, 270]:
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    # Path from pool edge to outer edge
    start_dist = pool_radius + pool_wall_thickness + 0.3
    end_dist = 15.0
    path_len = end_dist - start_dist
    mid_dist = (start_dist + end_dist) / 2

    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(mid_dist * dx, mid_dist * dy, 0.01)
    )
    path = bpy.context.object
    path.name = f"Path {angle_deg}°"
    path.scale = (path_width/2, path_len/2, 0.02)
    # Rotate to align with radial direction
    path.rotation_euler = (0, 0, -angle_rad)
    path.data.materials.append(path_mat)
    assign_to_memorial(path)

# --- Decorative low walls along paths ---
for angle_deg in [45, 135, 225, 315]:
    angle_rad = math.radians(angle_deg)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)
    # Small wall segments between rings
    for r_in, r_out, h, label in ring_specs[:3]:
        mid_r = (r_in + r_out) / 2
        wall_len = 1.5
        bpy.ops.mesh.primitive_cube_add(
            size=1,
            location=(mid_r * dx, mid_r * dy, h/2)
        )
        wall = bpy.context.object
        wall.name = f"Wall {label} {angle_deg}°"
        wall.scale = (wall_len/2, 0.15, h/2)
        wall.rotation_euler = (0, 0, -angle_rad)
        wall.data.materials.append(dark_stone_mat)
        assign_to_memorial(wall)

# --- Lighting ---
# Sun light
sun_data = bpy.data.lights.new("Sun", type='SUN')
sun_data.energy = 3.0
sun_data.angle = math.radians(5)
sun_obj = bpy.data.objects.new("Sun", sun_data)
sun_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(30))
bpy.context.scene.collection.objects.link(sun_obj)

# Ambient/world
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.6, 0.7, 0.85, 1.0)
    bg_node.inputs[1].default_value = 0.5

# Camera
bpy.ops.object.camera_add(location=(18, 18, 12))
camera = bpy.context.object
camera.name = "Memorial Camera"
# Point camera at center
direction = Vector((0, 0, 0)) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = camera

# Set render resolution
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

print("Memorial built successfully.")
