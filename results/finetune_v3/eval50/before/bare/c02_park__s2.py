import bpy
import math
import random
from mathutils import Vector

# Clean scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for block in bpy.data.meshes:
    if block.users == 0:
        bpy.data.meshes.remove(block)
for block in bpy.data.materials:
    if block.users == 0:
        bpy.data.materials.remove(block)

# Helper functions
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat

def add_cylinder(name, radius, depth, location, material, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location, vertices=vertices)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

def add_sphere(name, radius, location, material, segments=16, rings=8):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=segments, rings=rings)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

def add_plane(name, size, location, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(material)
    return obj

# Materials
grass_mat = create_material("Grass", (0.2, 0.5, 0.15, 1.0), roughness=0.8)
trunk_mat = create_material("Trunk", (0.35, 0.2, 0.1, 1.0), roughness=0.9)
leaf_mat = create_material("Leaves", (0.1, 0.4, 0.1, 1.0), roughness=0.7)
bench_mat = create_material("BenchWood", (0.4, 0.25, 0.1, 1.0), roughness=0.8)
path_mat = create_material("Path", (0.6, 0.55, 0.5, 1.0), roughness=0.9)
pond_mat = create_material("Water", (0.1, 0.3, 0.5, 1.0), roughness=0.1, metallic=0.3)
rock_mat = create_material("Rock", (0.4, 0.4, 0.4, 1.0), roughness=0.9)

# Ground
ground = add_plane("Ground", 30, (0, 0, 0), grass_mat)

# Path (a long thin plane)
path = add_plane("Path", 1, (0, 0, 0.01), path_mat)
path.scale = (1, 8, 1)
path.rotation_euler = (0, 0, math.radians(0))

# Pond (a flat cylinder)
pond = add_cylinder("Pond", 3, 0.1, (6, 4, 0.05), pond_mat, vertices=32)
pond.scale = (1, 0.8, 1)

# Trees
tree_positions = [(-5, -3, 0), (-3, 5, 0), (4, -5, 0)]
for i, pos in enumerate(tree_positions):
    # Trunk
    trunk = add_cylinder(f"Trunk_{i}", 0.3, 2.5, (pos[0], pos[1], 1.25), trunk_mat, vertices=12)
    # Canopy - multiple spheres for a fuller look
    canopy_positions = [
        (0, 0, 2.8),
        (0.5, 0.3, 3.2),
        (-0.5, 0.3, 3.2),
        (0.3, -0.5, 3.1),
        (-0.3, -0.5, 3.1),
        (0, 0, 3.6),
    ]
    for j, cp in enumerate(canopy_positions):
        sphere = add_sphere(f"Canopy_{i}_{j}", 1.0, (pos[0] + cp[0], pos[1] + cp[1], cp[2]), leaf_mat, segments=12, rings=6)

# Bench
bench_location = (1, 2, 0)
# Bench legs
leg_positions = [
    (-0.8, -0.3, 0.2),
    (-0.8, 0.3, 0.2),
    (0.8, -0.3, 0.2),
    (0.8, 0.3, 0.2),
]
for i, lp in enumerate(leg_positions):
    leg = add_cylinder(f"BenchLeg_{i}", 0.05, 0.4, (bench_location[0] + lp[0], bench_location[1] + lp[1], lp[2]), bench_mat, vertices=8)

# Bench seat
seat = add_cylinder(f"BenchSeat", 0.05, 0.05, (bench_location[0], bench_location[1], 0.45), bench_mat, vertices=8)
seat.scale = (1.0, 0.5, 1.0)
seat.rotation_euler = (0, 0, math.radians(90))

# Bench back
back = add_cylinder(f"BenchBack", 0.05, 0.05, (bench_location[0], bench_location[1] + 0.4, 0.7), bench_mat, vertices=8)
back.scale = (1.0, 0.5, 1.0)
back.rotation_euler = (math.radians(15), 0, math.radians(90))

# Some rocks around the pond
rock_positions = [
    (8, 3, 0.1),
    (4, 6, 0.1),
    (9, 5, 0.1),
    (5, 2, 0.1),
]
for i, rp in enumerate(rock_positions):
    rock = add_sphere(f"Rock_{i}", 0.3, rp, rock_mat, segments=8, rings=4)
    rock.scale = (1, 0.8, 0.6)

# Add a sun lamp
bpy.ops.object.light_add(type='SUN', location=(10, 10, 15))
sun = bpy.context.active_object
sun.name = "Sun"
sun.data.energy = 3
sun.rotation_euler = (math.radians(45), math.radians(30), 0)

# Add a camera
bpy.ops.object.camera_add(location=(12, -12, 8))
camera = bpy.context.active_object
camera.name = "Camera"
# Point camera at center
direction = Vector((0, 0, 0)) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()
bpy.context.scene.camera = camera

# Set render settings
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.film_transparent = False

print("Park scene created successfully!")
